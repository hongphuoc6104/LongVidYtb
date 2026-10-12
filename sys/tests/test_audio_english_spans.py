"""English words/sentences inside Vietnamese narration are split into spans and
routed to Colab OmniVoice (Adam 1.22x); retakes change a recorded knob."""
import sqlite3,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import read,write,ROOT
import adapters,jsonschema
import numpy as np
import soundfile as sf
from colab_bridge.client import Client
from colab_bridge.protocol import build_request

SR=48000
SC04='Tới lượt bạn nhé! Hãy nghe và lặp lại thật to nào: "Please don\'t scold me!"'
VOCAB=[{'word':'scold','phonetic':'/skoʊld/','meaning':'mắng'}]

def sine(path,seconds,amp):
 t=np.arange(int(SR*seconds))/SR;sf.write(str(path),(amp*np.sin(2*np.pi*220*t)).astype('float32'),SR,subtype='PCM_16')

class EnglishPartsTests(unittest.TestCase):
 def test_quoted_practice_sentence_goes_to_english_engine(self):
  self.assertEqual(adapters.english_parts('Hãy nghe và lặp lại thật to nào: "Please don\'t scold me!"',['scold']),
   [{'lang':'vi','text':'Hãy nghe và lặp lại thật to nào:'},{'lang':'en','text':"Please don't scold me!"}])
 def test_bare_vocabulary_word_keeps_its_punctuation(self):
  self.assertEqual(adapters.english_parts('Phát âm chuẩn là: scold.',['scold']),
   [{'lang':'vi','text':'Phát âm chuẩn là:'},{'lang':'en','text':'scold.'}])
  self.assertEqual(adapters.english_parts('Scold có nghĩa là trách mắng.',['scold'])[0],{'lang':'en','text':'Scold'})
 def test_mid_sentence_word_and_inflection(self):
  self.assertEqual([x['lang'] for x in adapters.english_parts('Đừng quên một câu với scolding để nhớ nhé!',['scold'])],['vi','en','vi'])
  self.assertEqual(adapters.english_parts('Tôi thấy scoldx ở đây.',['scold']),[{'lang':'vi','text':'Tôi thấy scoldx ở đây.'}])
 def test_quote_wins_over_word_and_curly_quotes(self):
  parts=adapters.english_parts('Mẹ mắng: “My mom scolded me.” Xong!',['scold'])
  self.assertEqual(parts,[{'lang':'vi','text':'Mẹ mắng:'},{'lang':'en','text':'My mom scolded me.'},{'lang':'vi','text':'Xong!'}])
 def test_quoted_vietnamese_stays_vi(self):
  t='Bố can: "Đừng mắng con bé nữa!"'
  self.assertEqual(adapters.english_parts(t,['scold']),[{'lang':'vi','text':t}])

class SpanTakeTests(unittest.TestCase):
 def test_retake_zero_is_configured_delivery(self):
  self.assertEqual(adapters.span_take({'en_seed':42,'en_temperature':.3},0),{'seed':42,'temperature':.3,'rate':1.})
 def test_each_retake_changes_seed_temperature_and_rate_deterministically(self):
  takes=[adapters.span_take({},r) for r in range(4)]
  self.assertEqual(takes,[adapters.span_take({},r) for r in range(4)])
  for a,b in zip(takes,takes[1:]):
   self.assertEqual(b['seed'],a['seed']+1);self.assertLess(b['temperature'],a['temperature']);self.assertLess(b['rate'],a['rate'])
 def test_floors(self):
  t=adapters.span_take({},50);self.assertEqual((t['temperature'],t['rate']),(.1,.8))

class FakeP:
 """Minimal stand-in for Pilot: exactly what adapters.audio() touches."""
 def __init__(self,root,content,cfg):
  self.root=root;self.content=content;(root/'jobs/j').mkdir(parents=True)
  write(root/'config.json',cfg)
  for sub in ['assets/voices/adam']:
   (root/sub).mkdir(parents=True,exist_ok=True)
   for f in (ROOT/sub).iterdir():
    if f.is_file():(root/sub/f.name).write_bytes(f.read_bytes())
  self.db=sqlite3.connect(':memory:');self.db.row_factory=sqlite3.Row
  self.db.execute('CREATE TABLE audio_edits(id INTEGER PRIMARY KEY,job TEXT,scene_id TEXT,note TEXT,at REAL)')
 def payload(self,j,m):return self.content
 def job(self,j):return self.root/'jobs'/j
 def brief(self,j):return None

class AudioAdapterTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  self.content={'scenes':[{'id':'SC03','narration':'Mẹ mắng tôi. Bố nói: "Đừng mắng con!"','vocabulary':VOCAB},
                          {'id':'SC04','narration':SC04,'vocabulary':VOCAB,'audio_direction':{'vi':{'learner_pause_seconds':3.0}}},
                          {'id':'SC05','narration':'Rất tuyệt vời, hẹn gặp lại!'}]}
  self.cfg=dict(read(ROOT/'config.json'))
  self.calls=[]
 def tearDown(self):self.tmp.cleanup()

 def run_audio(self,**cfg):
  selected=dict(self.cfg,**cfg)
  p=FakeP(self.root,self.content,selected);self.p=p
  for sid,n in getattr(self,'retakes',{}).items():
   for _ in range(n):p.db.execute("INSERT INTO audio_edits(job,scene_id,note,at) VALUES('j',?,'TEST',0)",(sid,))
  def fake_synthesize(client_self,req,out,cache_dir,before_submit=None):
   self.calls.append(req)
   segs=[]
   for idx,seg in enumerate(req['segments']):
    wav_name=f'segment-{idx:03}.wav'
    sine(out/wav_name,.8,.2)
    segs.append({'scene_id':seg['scene_id'],'text':seg['text'],'path':wav_name,'content_duration':.6})
   res={'voice':'Adam','engine':{'backend':'colab-omnivoice','model':'kjanh/KhanhTTS-OmniVoice'},'segments':segs}
   write(out/'tts-result.json',res)
  out=p.job('j')/'revisions/audio/1';out.mkdir(parents=True)
  with patch.object(Client,'synthesize',fake_synthesize):return adapters.audio(p,'j',out)

 def test_scold_practice_line_uses_adam_omnivoice_and_valid_timeline(self):
  pay=self.run_audio()
  jsonschema.validate(pay,read(ROOT/'schemas/audio.json'))
  req=self.calls[0]
  self.assertEqual(req['profiles']['vi']['voice'],'Adam')
  self.assertEqual(req['profiles']['en']['voice'],'Adam')
  en_items=[x for x in req['items'] if x['language']=='en']
  self.assertEqual([x['text'] for x in en_items],["Please don't scold me!"])
  for sc in self.content['scenes']:
   self.assertEqual(' '.join(x['text'] for x in pay['segments'] if x['scene_id']==sc['id']),sc['narration'])
  last=0
  for x in pay['segments']:
   self.assertAlmostEqual(x['start'],last,places=6);self.assertLess(x['start'],x['content_end']);self.assertLessEqual(x['content_end'],x['end']);last=x['end']
  self.assertAlmostEqual(pay['duration'],last,places=6)
  self.assertEqual(pay['srt'].split('/')[-1],'subtitles.srt')

 def test_retake_changes_english_take_and_is_recorded(self):
  self.retakes={'SC04':2}
  self.run_audio()
  req=self.calls[0]
  en_items=[x for x in req['items'] if x['language']=='en']
  self.assertEqual(en_items[0]['retake'],2)
  self.assertEqual(en_items[0]['speed'],1.22)

 def test_scenes_without_vocabulary_have_no_english_parts(self):
  for s in self.content['scenes']:s.pop('vocabulary',None)
  self.run_audio()
  req=self.calls[0]
  self.assertEqual({x['language'] for x in req['items']},{'vi'})

if __name__=='__main__':unittest.main()
