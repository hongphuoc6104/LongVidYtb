"""Audio module coverage. Real TTS is never invoked; Colab OmniVoice client is faked."""
import json,math,shutil,struct,subprocess,sys,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,Blocked,read,write,ROOT
import adapters
from colab_bridge.client import Client,ColabError

SR=48000

def tone(path,seconds,level=8000):
 """Mono PCM_16 48 kHz speech stand-in: a tone body plus a trailing silence."""
 body=int(SR*seconds*.8);tail=int(SR*seconds)-body
 frames=b''.join(struct.pack('<h',int(level*math.sin(2*math.pi*180*i/SR))) for i in range(body))+b'\x00\x00'*tail
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(SR);w.writeframes(frames)

def fake_colab_synth(emit,voice=None):
 """Fake Client.synthesize: honours the request's scene/text structure."""
 def synth(client_self,req,out,cache_dir,before_submit=None):
  segs=[]
  for seg in req['segments']:
   emit(out,len(segs),seg,seg['text'])
   segs.append({'scene_id':seg['scene_id'],'text':voice(seg['text']) if voice else seg['text'],'path':f'segment-{len(segs):03}.wav'})
  write(out/'tts-result.json',{'voice':'VietNarrator','engine':{'backend':'colab-omnivoice','model':'kjanh/KhanhTTS-OmniVoice'},'segments':segs})
 return synth

class PureHelperTests(unittest.TestCase):
 def test_chunks_preserve_narration(self):
  """pilot.checks rejoins segment texts and compares to narration verbatim."""
  for s in read(ROOT/'examples/content.json')['scenes']:
   self.assertEqual(' '.join(' '.join(adapters.chunks(s['narration'])).split()),' '.join(s['narration'].split()))

 def test_chunks_never_empty(self):
  for text in ['No terminal punctuation','Một câu. Hai câu!','A'*400+'. B'*5]:
   parts=adapters.chunks(text)
   self.assertTrue(parts and all(c.strip() for c in parts),text[:20])

 def test_gap_after_follows_punctuation(self):
  g=adapters.DEFAULT_PAUSE
  for text,want in [('Xin chào bạn.','sentence'),('Thật sao?','sentence'),('Tuyệt vời!','sentence'),
                    ('Dấu ba chấm…','sentence'),('Một, hai,','minor'),('Vế trước;','minor'),('Không dấu','minor')]:
   self.assertEqual(adapters.gap_after(text,g),g[want],text)

 def test_gap_after_honours_config_override(self):
  self.assertEqual(adapters.gap_after('Câu.',{'sentence':.9}),.9)
  self.assertEqual(adapters.gap_after('Câu,',{}),adapters.DEFAULT_PAUSE['minor'])

 def test_chunks_splits_quoted_sentences(self):
  text='Thứ nhất: "We wake up early every day." Chúng tôi thức giấc sớm mỗi ngày.'
  parts=adapters.chunks(text)
  self.assertEqual(parts,['Thứ nhất: "We wake up early every day."','Chúng tôi thức giấc sớm mỗi ngày.'])

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'ffmpeg required')
class MasterTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()

 def test_master_preserves_frame_count(self):
  """pilot.checks matches the combined wav against segments[-1]['end'] within
  30 ms, so mastering must not pad, trim or resample."""
  src=self.d/'n.wav';tone(src,3.0);before=adapters.frames_of(src)
  adapters.master(src,self.d/'eq.wav',{'audio_lufs':-14.,'audio_peak_db':-1.5})
  self.assertEqual(adapters.frames_of(src),before)
  with wave.open(str(src)) as w:self.assertEqual(w.getframerate(),48000)

 def test_master_hits_loudness_target_without_clipping(self):
  src=self.d/'n.wav';tone(src,3.0,level=2000)
  adapters.master(src,self.d/'eq.wav',{'audio_lufs':-14.,'audio_peak_db':-1.5})
  r=subprocess.run(['ffmpeg','-v','info','-i',str(src),'-af','loudnorm=print_format=json','-f','null','-'],capture_output=True,text=True)
  m=json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}')+1])
  self.assertLess(abs(float(m['input_i'])+14.),1.5,m)
  self.assertLessEqual(float(m['input_tp']),-1.0,m)

 def test_master_leaves_no_temp_files(self):
  src=self.d/'n.wav';tone(src,1.0)
  adapters.master(src,self.d/'eq.wav',{})
  self.assertEqual(sorted(p.name for p in self.d.iterdir()),['eq.log','n.wav'])

 def test_master_raises_blocked_when_ffmpeg_fails(self):
  """A corrupt/undecodable source must never silently pass through unmastered."""
  src=self.d/'n.wav';src.write_bytes(b'not a real wav file')
  with self.assertRaises(Blocked):adapters.master(src,self.d/'eq.wav',{})
  self.assertFalse((self.d/'narration_lv.wav').exists())
  self.assertTrue((self.d/'eq.log').exists())

 def test_master_raises_blocked_when_ffmpeg_missing(self):
  src=self.d/'n.wav';tone(src,1.0);before=src.read_bytes()
  def missing(cmd,**kw):
   if cmd[0]=='ffmpeg':raise FileNotFoundError('ffmpeg')
   return subprocess.run(cmd,**kw)
  with patch.object(adapters.subprocess,'run',side_effect=missing):
   with self.assertRaisesRegex(Blocked,'ffmpeg'):adapters.master(src,self.d/'eq.wav',{})
  self.assertEqual(src.read_bytes(),before,'src must be left untouched, not silently passed through')

class AudioStageTests(unittest.TestCase):
 """Drives adapters.audio() with a fake Colab OmniVoice client and asserts every pilot gate."""
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for name in ['schemas','.agents','tests','examples']:shutil.copytree(ROOT/name,self.root/name)
  shutil.copytree(ROOT/'assets/voices/viet_narrator',self.root/'assets/voices/viet_narrator')
  (self.root/'renderer').mkdir();(self.root/'renderer/render.mjs').write_text('// dummy renderer')
  for name in ['config.json','AGENTS.md','GEMINI.md','pilot.py','workflow.py','machine_review.py','image_pipeline.py','prompt_templates.py','adapters.py','package.json','package-lock.json','requirements.txt']:
   if (ROOT/name).exists():shutil.copy(ROOT/name,self.root/name)
  self.p=Pilot(self.root);self.p.new('test')
  self.p.approve('test','control',self.p.rows('test')['control']['revision'],'TEST FIXTURE approval, not user consent')
  self.p.run('test','content');self.p.approve('test','content',self.p.rows('test')['content']['revision'],'TEST FIXTURE approval, not user consent')
  self.p.db.execute("UPDATE modules SET state='approved' WHERE job='test' AND module='images'");self.p.db.commit()
 def tearDown(self):self.p.db.close();self.tmp.cleanup()

 def fake_worker(self,seconds=4.0):
  return fake_colab_synth(lambda out,i,sc,t:tone(out/f'segment-{i:03}.wav',seconds))

 def test_audio_passes_every_gate(self):
  with patch.object(Client,'synthesize',self.fake_worker()):
   self.p.run('test','audio')
  r=self.p.rows('test')['audio']
  self.assertEqual(r['state'],'awaiting_review')
  self.p.validate('test','audio')
  pay=read(self.p.path('test',r['envelope']))['payload']
  self.assertEqual(pay['voice'],'VietNarrator')
  self.assertEqual(len(pay['segments']),sum(len(adapters.chunks(s['narration'])) for s in self.p.payload('test','content')['scenes']))
  last=0
  for s in pay['segments']:
   self.assertAlmostEqual(s['start'],last,places=3);self.assertGreater(s['end'],s['start']);last=s['end']
  self.assertAlmostEqual(pay['duration'],last,places=3)

 def test_request_carries_per_scene_retake(self):
  self.p.db.execute("INSERT INTO audio_edits(job,scene_id,note,at) VALUES('test','SC02','TEST retake',0)")
  self.p.db.commit()
  sent={};base=self.fake_worker()
  def spy(client_self,req,out,cache_dir,before_submit=None):
   sent.update(req)
   return base(client_self,req,out,cache_dir,before_submit)
  with patch.object(Client,'synthesize',spy):
   self.p.run('test','audio')
  retakes_by_scene={}
  for seg in sent['segments']:
   for idx in seg['items']:
    retakes_by_scene[seg['scene_id']]=sent['items'][idx]['retake']
  self.assertEqual(retakes_by_scene['SC02'],1)
  self.assertEqual({v for k,v in retakes_by_scene.items() if k!='SC02'},{0})

 def test_request_carries_pauses_and_viet_narrator_voice(self):
  seen={};inner=self.fake_worker()
  def spy(client_self,req,out,cache_dir,before_submit=None):
   seen.update(req)
   return inner(client_self,req,out,cache_dir,before_submit)
  with patch.object(Client,'synthesize',spy):self.p.run('test','audio')
  cfg=read(self.root/'config.json')
  self.assertEqual(seen['profiles']['vi']['voice'],'VietNarrator')
  self.assertEqual(seen['items'][0]['speed'],1.0)
  self.assertEqual(seen['segments'][-1]['pause'],cfg['tts_pause']['tail'])

 def test_silent_segment_is_blocked(self):
  run=fake_colab_synth(lambda out,i,sc,t:tone(out/f"segment-{i:03}.wav",4.0,level=0))
  with patch.object(Client,'synthesize',run):
   with self.assertRaises(Blocked):self.p.run('test','audio')

 def test_altered_narration_is_blocked(self):
  run=fake_colab_synth(lambda out,i,sc,t:tone(out/f"segment-{i:03}.wav",4.0),voice=lambda t:t+' thêm chữ')
  with patch.object(Client,'synthesize',run):
   with self.assertRaises(Blocked):self.p.run('test','audio')

class EnglishTrackTests(unittest.TestCase):
 """16:9 jobs carry an English track on its own timeline; 9:16 jobs must not."""
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
  for n in ['schemas','.agents','tests','examples']:shutil.copytree(ROOT/n,self.root/n)
  shutil.copytree(ROOT/'assets/voices/viet_narrator',self.root/'assets/voices/viet_narrator')
  (self.root/'renderer').mkdir();(self.root/'renderer/render.mjs').write_text('// dummy renderer')
  for n in ['pilot.py','workflow.py','machine_review.py','image_pipeline.py','prompt_templates.py','content_contract.py','adapters.py','config.json','AGENTS.md','GEMINI.md','package.json','package-lock.json','requirements.txt']:
   if (ROOT/n).exists():shutil.copy(ROOT/n,self.root/n)
 def tearDown(self):
  if hasattr(self,'p'):self.p.db.close()
  self.tmp.cleanup()

 def start(self,ratio):
  b=read(ROOT/'examples/m1/brief.json');b['aspect_ratio']=ratio
  self.p=Pilot(self.root);self.p.new('m1',b)
  self.p.approve('m1','control',1,'TEST FIXTURE approval, not user consent')
  d=read(ROOT/'examples/m1/content.json');_,rev,h=self.p.brief('m1')
  d.update(brief_revision=rev,brief_hash=h)
  if ratio in ('dual','16:9'):
   for s in d['scenes']:s['narration_en']='English narration for '+s['id']+'. It carries the same idea in natural English.'
  write(self.p.job('m1')/'draft/content.json',d)
  self.p.run('m1','content');self.p.approve('m1','content',1,'TEST FIXTURE approval, not user consent')
  self.p.db.execute("UPDATE modules SET state='approved' WHERE job='m1' AND module='images'");self.p.db.commit()
  return d

 def fake(self,vi=4.0,en=9.0):
  """Fakes Colab OmniVoice synthesis for both VI and EN tracks."""
  def synth(client_self,req,out,cache_dir,before_submit=None):
   segs=[]
   for seg in req['segments']:
    tone(out/f'segment-{len(segs):03}.wav',vi)
    segs.append({'scene_id':seg['scene_id'],'text':seg['text'],'path':f'segment-{len(segs):03}.wav'})
   write(out/'tts-result.json',{'voice':'VietNarrator','engine':{'backend':'colab-omnivoice','model':'kjanh/KhanhTTS-OmniVoice'},'segments':segs})
   if req.get('english'):
    scs=[]
    for sc in req['english']:
     path=f"en-{sc['scene_id']}.wav";tone(out/path,en)
     scs.append({'scene_id':sc['scene_id'],'path':path})
    write(out/'en-result.json',{'engine':'colab-omnivoice','voice':'VietNarrator','scenes':scs})
  return synth

 def test_dual_job_produces_english_track(self):
  content=self.start('dual')
  with patch.object(Client,'synthesize',self.fake()):self.p.run('m1','audio')
  self.p.validate('m1','audio')
  pay=read(self.p.path('m1',self.p.rows('m1')['audio']['envelope']))['payload']
  en=pay['en']
  self.assertEqual(en['engine'],'colab-omnivoice');self.assertEqual(en['voice'],'VietNarrator')
  self.assertEqual([s['scene_id'] for s in en['scenes']],[s['id'] for s in content['scenes']])
  last=0
  for s in en['scenes']:
   self.assertAlmostEqual(s['start'],last,places=3);last=s['end']
  self.assertAlmostEqual(en['duration'],last,places=3)
  self.assertNotAlmostEqual(en['duration'],pay['duration'],places=1)

 def test_english_request_uses_viet_narrator_omnivoice_settings(self):
  self.start('dual');seen={};inner=self.fake()
  def spy(client_self,req,out,cache_dir,before_submit=None):
   seen.update(req)
   return inner(client_self,req,out,cache_dir,before_submit)
  with patch.object(Client,'synthesize',spy):self.p.run('m1','audio')
  self.assertEqual(seen['profiles']['en']['voice'],'VietNarrator')
  en_items=[x for x in seen['items'] if x['language']=='en']
  self.assertEqual(en_items[0]['speed'],1.0)
  self.assertEqual(seen['models']['en']['id'],'kjanh/KhanhTTS-OmniVoice')

 def test_colab_failure_blocks_audio(self):
  self.start('dual')
  def fail(client_self,req,out,cache_dir,before_submit=None):
   raise ColabError('Colab synthesis failed')
  with patch.object(Client,'synthesize',fail):
   with self.assertRaisesRegex(Blocked,'Colab synthesis failed'):self.p.run('m1','audio')

 def test_vertical_job_has_no_english_track(self):
  self.start('9:16')
  with patch.object(Client,'synthesize',self.fake()):self.p.run('m1','audio')
  pay=read(self.p.path('m1',self.p.rows('m1')['audio']['envelope']))['payload']
  self.assertNotIn('en',pay)

 def test_dual_content_without_english_is_rejected(self):
  from content_contract import ContractError
  b=read(ROOT/'examples/m1/brief.json');b['aspect_ratio']='dual'
  self.p=Pilot(self.root);self.p.new('m1',b)
  self.p.approve('m1','control',1,'TEST FIXTURE approval, not user consent')
  d=read(ROOT/'examples/m1/content.json');_,rev,h=self.p.brief('m1')
  d.update(brief_revision=rev,brief_hash=h);write(self.p.job('m1')/'draft/content.json',d)
  with self.assertRaises(ContractError) as c:self.p.run('m1','content')
  self.assertIn('NARRATION_EN',{e['code'] for e in c.exception.errors})

 def test_render_props_carry_english_timeline(self):
  content=self.start('dual')
  with patch.object(Client,'synthesize',self.fake()):self.p.run('m1','audio')
  self.p.approve('m1','audio',1,'TEST FIXTURE approval, not user consent')
  snd=self.p.payload('m1','audio')
  imgs={'items':[{'scene_id':s['id'],'path':'x.png','prompt':'p','source':'fake'} for s in content['scenes']]}
  out=self.p.job('m1')/'revisions/render/1';out.mkdir(parents=True)
  for s in content['scenes']:
   f=self.p.job('m1')/'x.png'
   if not f.exists():f.write_bytes(b'TEST ONLY; renderer never executes')
  captured={}
  def stop(cmd,**kw):
   captured.update(read(out/'props.json'));raise RuntimeError('renderer not executed in tests')
  with patch.object(adapters,'subprocess') as sp:
   sp.run.side_effect=stop
   with patch.object(self.p,'payload',side_effect=lambda j,m:{'content':content,'images':imgs,'audio':snd}[m]):
    with self.assertRaises(RuntimeError):adapters.render(self.p,'m1',out)
  self.assertEqual(captured['en_duration'],snd['en']['duration'])
  self.assertEqual([s['start'] for s in captured['en_scenes']],[s['start'] for s in snd['en']['scenes']])
  self.assertNotEqual([s['end'] for s in captured['en_scenes']],[s['end'] for s in captured['scenes']])

if __name__=='__main__':unittest.main()
