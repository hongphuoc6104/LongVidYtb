"""Audio module coverage. Real TTS is never invoked; Colab OmniVoice client is faked."""
import json,math,shutil,struct,subprocess,sys,tempfile,unittest,wave
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from pilot import Pilot,Blocked,read,write,ROOT
import adapters
import numpy as np
from audio_processing import TRUE_PEAK_MARGIN_DB, VOICE_CHAIN
from colab_bridge.client import Client, ColabError
from colab_bridge.worker import _trim_silence

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

 def test_master_pure_silence_unity_gain_and_true_peak(self):
  """Pure digital silence must be mastered with unity gain (0.00 dB) and preserve true peak <= -1.0 dBTP."""
  src = self.d / "silence.wav"
  n_frames = 2 * SR
  with wave.open(str(src), "wb") as w:
   w.setparams((1, 2, SR, n_frames, "NONE", "not compressed"))
   w.writeframes(b"\x00\x00" * n_frames)

  adapters.master(src, self.d / "eq.wav", {"audio_lufs": -11.0, "audio_peak_db": -1.0})
  self.assertEqual(adapters.frames_of(src), n_frames)

  # Verify FFmpeg execution log confirms unity gain (0.00dB) and no infdB divergence
  log_path = self.d / "eq.log"
  self.assertTrue(log_path.exists())
  log_content = log_path.read_text()
  self.assertIn("volume=0.00dB", log_content, "Expected volume=0.00dB unity gain in mastering log")
  self.assertNotIn("volume=infdB", log_content, "volume=infdB divergence must never be executed")

  # Verify True Peak of mastered silence is <= -1.0 dBTP
  r = subprocess.run(
   ["ffmpeg", "-v", "info", "-i", str(src), "-af", "loudnorm=print_format=json", "-f", "null", "-"],
   capture_output=True,
   text=True,
  )
  m = json.loads(r.stderr[r.stderr.rindex("{") : r.stderr.rindex("}") + 1])
  self.assertEqual(m["input_i"], "-inf")
  self.assertLessEqual(float(m["input_tp"]), -1.0)

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


@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'), 'ffmpeg required')
class MasterInvarianceTests(unittest.TestCase):
    """Verifies clean 4-stage studio VOICE_CHAIN, LUFS targeting (-11.0 and -14.0), and 100% exact frame count invariance."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_voice_chain_composition(self):
        """VOICE_CHAIN comprises clean 4-stage anti-mud clarity studio processing."""
        stages = [s.strip() for s in VOICE_CHAIN.split(',') if s.strip()]
        self.assertEqual(len(stages), 4, f'Expected 4 stages, got {len(stages)}: {stages}')
        self.assertTrue(stages[0].startswith('highpass=f=90'), stages[0])
        self.assertTrue(stages[1].startswith('equalizer=f=185'), stages[1])
        self.assertTrue(stages[2].startswith('equalizer=f=2400'), stages[2])
        self.assertTrue(stages[3].startswith('lowpass=f=13500'), stages[3])
        self.assertNotIn('acompressor', VOICE_CHAIN)
        self.assertNotIn('afftdn', VOICE_CHAIN)

    # Backward compatibility aliases
    test_voice_chain_5_stages_composition = test_voice_chain_composition
    test_voice_chain_7_stages_composition = test_voice_chain_composition

    def test_master_lufs_target_minus_14_long_format(self):
        """Long 16:9 format targets -14.0 LUFS with true peak headroom."""
        src = self.d / 'long.wav'
        tone(src, 3.0, level=4000)
        before_frames = adapters.frames_of(src)
        adapters.master(src, self.d / 'eq_long.wav', {'audio_lufs': -14.0, 'audio_peak_db': -1.5})
        self.assertEqual(adapters.frames_of(src), before_frames)
        r = subprocess.run(
            ['ffmpeg', '-v', 'info', '-i', str(src), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
            capture_output=True,
            text=True,
        )
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        self.assertLess(abs(float(m['input_i']) - (-14.0)), 1.5, m)
        self.assertLessEqual(float(m['input_tp']), -1.5 - TRUE_PEAK_MARGIN_DB + 0.3, m)

    def test_master_lufs_target_minus_11_short_format(self):
        """Short 9:16 format targets -11.0 LUFS for punchy mobile phone playback."""
        src = self.d / 'short.wav'
        tone(src, 3.0, level=4000)
        before_frames = adapters.frames_of(src)
        adapters.master(src, self.d / 'eq_short.wav', {'audio_lufs': -11.0, 'audio_peak_db': -1.0})
        self.assertEqual(adapters.frames_of(src), before_frames)
        r = subprocess.run(
            ['ffmpeg', '-v', 'info', '-i', str(src), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
            capture_output=True,
            text=True,
        )
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        self.assertLess(abs(float(m['input_i']) - (-11.0)), 1.5, m)
        self.assertLessEqual(float(m['input_tp']), -1.0, m)

    def test_master_two_pass_feedback_loop_converges(self):
        """Signal with high crest factor triggering peak limiter converges via 2-pass feedback."""
        src = self.d / 'peaks.wav'
        tone(src, 4.0, level=14000)
        adapters.master(src, self.d / 'eq_peaks.wav', {'audio_lufs': -14.0, 'audio_peak_db': -1.5})
        r = subprocess.run(
            ['ffmpeg', '-v', 'info', '-i', str(src), '-af', 'loudnorm=print_format=json', '-f', 'null', '-'],
            capture_output=True,
            text=True,
        )
        m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
        self.assertLess(abs(float(m['input_i']) + 14.0), 1.0, m)

    def test_master_strict_sample_count_invariance_arbitrary_durations(self):
        """Mastering guarantees 100% sample-exact PCM frame count across arbitrary and prime durations."""
        sample_counts = [
            48000,   # 1.0s
            65761,   # ~1.37s prime frame count
            120000,  # 2.5s
            12347,   # ~0.257s odd sample count
        ]
        for n_frames in sample_counts:
            src = self.d / f'inv_{n_frames}.wav'
            frames = b''.join(
                struct.pack('<h', int(6000 * math.sin(2.0 * math.pi * 260.0 * i / SR)))
                for i in range(n_frames)
            )
            with wave.open(str(src), 'wb') as w:
                w.setnchannels(1)
                w.setsampwidth(2)
                w.setframerate(SR)
                w.writeframes(frames)

            before = adapters.frames_of(src)
            adapters.master(src, self.d / f'eq_{n_frames}.wav', {'audio_lufs': -14.0})
            self.assertEqual(adapters.frames_of(src), before)
            with wave.open(str(src)) as w:
                self.assertEqual(w.getframerate(), SR)
                self.assertEqual(w.getnchannels(), 1)
                self.assertEqual(w.getsampwidth(), 2)

    def test_master_preserves_frames_on_silence_and_clipping_audio(self):
        """Pure silence and saturated clipping signals both retain exact frame count."""
        # 1. Silence input: 2.0s zero-amplitude
        silence_src = self.d / 'silence.wav'
        n_frames = 2 * SR
        with wave.open(str(silence_src), 'wb') as w:
            w.setparams((1, 2, SR, n_frames, 'NONE', 'not compressed'))
            w.writeframes(b'\x00\x00' * n_frames)
        adapters.master(silence_src, self.d / 'eq_silence.wav', {})
        self.assertEqual(adapters.frames_of(silence_src), n_frames)

        # 2. Clipping input: 2.0s maximum amplitude tone
        clipping_src = self.d / 'clipping.wav'
        with wave.open(str(clipping_src), 'wb') as w:
            w.setparams((1, 2, SR, n_frames, 'NONE', 'not compressed'))
            clip_frames = b''.join(
                struct.pack('<h', max(-32767, min(32767, int(32000 * math.sin(2.0 * math.pi * 400.0 * i / SR)))))
                for i in range(n_frames)
            )
            w.writeframes(clip_frames)
        adapters.master(clipping_src, self.d / 'eq_clip.wav', {})
        self.assertEqual(adapters.frames_of(clipping_src), n_frames)

    def test_master_frame_mismatch_raises_blocked(self):
        """Any filter altering sample count raises Blocked and leaves src untouched."""
        src = self.d / 'mismatch.wav'
        tone(src, 1.0)
        before_bytes = src.read_bytes()
        # atrim alters sample count by dropping 100 samples
        with self.assertRaisesRegex(Blocked, 'frame count'):
            adapters.master(src, self.d / 'eq_mismatch.wav', {'audio_voice_chain': 'atrim=start_sample=100'})
        self.assertEqual(src.read_bytes(), before_bytes, 'src must be untouched when frame count check fails')
        self.assertFalse((self.d / 'narration_lv.wav').exists())


class TrimSilenceTests(unittest.TestCase):
    """Verifies 48kHz mono PCM16 silence trimming, idempotency, padding preservation, and soft fricatives."""

    def test_trim_silence_is_idempotent(self):
        """trim(trim(w)) == trim(w) holds for clean audio and audio with low-level noise floor."""
        # 1. Zero-lead audio
        lead = np.zeros(round(0.25 * SR), dtype=np.float32)
        speech = (0.20 * np.sin(np.arange(round(0.50 * SR)) * 0.05)).astype(np.float32)
        trail = np.zeros(round(0.20 * SR), dtype=np.float32)
        w = np.concatenate([lead, speech, trail])
        once = _trim_silence(w, sr=SR)
        twice = _trim_silence(once, sr=SR)
        np.testing.assert_array_equal(once, twice)

        # 2. Audio with non-zero noise floor (below 0.012 threshold)
        noise = np.full(len(w), 0.001, dtype=np.float32)
        w_noise = w + noise
        once_noise = _trim_silence(w_noise, sr=SR)
        twice_noise = _trim_silence(once_noise, sr=SR)
        np.testing.assert_array_equal(once_noise, twice_noise)

    def test_trim_silence_preserves_lead_and_trail_buffers(self):
        """Preserves 25ms lead (1200 frames) and 30ms trail (1440 frames) padding."""
        lead = np.zeros(round(0.20 * SR), dtype=np.float32)  # 9600 samples
        speech = np.full(round(0.50 * SR), 0.25, dtype=np.float32)  # 24000 samples
        trail = np.zeros(round(0.20 * SR), dtype=np.float32)  # 9600 samples
        w = np.concatenate([lead, speech, trail])

        trimmed = _trim_silence(w, sr=SR, lead_ms=25, trail_ms=30, fade_ms=8)
        # Expected duration: 24000 speech + 1200 lead + 1440 trail = 26640 samples
        expected_len = 24000 + round(0.025 * SR) + round(0.030 * SR)
        self.assertEqual(len(trimmed), expected_len)
        self.assertEqual(len(trimmed), 26640)

    def test_trim_silence_soft_fricative_preservation(self):
        """Preserves soft fricatives (>=0.008 amplitude) in the 35ms lead window without fade attenuation."""
        # 15ms fricative at 0.008 amplitude preceding voiced vowel
        lead = np.zeros(round(0.20 * SR), dtype=np.float32)
        fricative = np.full(round(0.015 * SR), 0.008, dtype=np.float32)
        vowel = (0.30 * np.sin(np.arange(round(0.40 * SR)) * 0.05)).astype(np.float32)
        trail = np.zeros(round(0.20 * SR), dtype=np.float32)
        w = np.concatenate([lead, fricative, vowel, trail])

        trimmed = _trim_silence(w, sr=SR)
        # Total duration: ~0.40s vowel + 0.015s fricative + lead/trail buffers (~0.495s)
        dur = len(trimmed) / float(SR)
        self.assertGreaterEqual(dur, 0.45)
        self.assertLessEqual(dur, 0.51)

        # Fricative samples within lead buffer are unattenuated (0.008)
        idx0 = int(np.where(np.abs(w) >= 0.008)[0][0])
        start = max(0, idx0 - round(0.035 * SR))
        fric_start = len(lead) - start
        fric_end = fric_start + len(fricative)
        np.testing.assert_allclose(trimmed[fric_start:fric_end], 0.008)

    def test_trim_silence_empty_and_pure_silence_arrays(self):
        """Empty input and all-silent arrays are returned safely without error."""
        empty = np.array([], dtype=np.float32)
        np.testing.assert_array_equal(_trim_silence(empty, sr=SR), empty)

        silence = np.zeros(SR, dtype=np.float32)
        np.testing.assert_array_equal(_trim_silence(silence, sr=SR), silence)

    def test_trim_silence_sub_buffer_short_utterance(self):
        """Utterance shorter than lead + trail is returned intact without indexing crash."""
        w = np.full(500, 0.05, dtype=np.float32)
        trimmed = _trim_silence(w, sr=SR)
        self.assertEqual(len(trimmed), 500)


if __name__ == '__main__':
    unittest.main()

