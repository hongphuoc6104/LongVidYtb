"""Replaceable providers; no provider can approve a module."""
import json, re, shutil, subprocess, time, wave
from pathlib import Path
from PIL import Image, ImageDraw
from pilot import Blocked,read,write,digest

def copy_optional_flow_screenshot(source, destination, *, required=False):
 """Never substitute preflight/account evidence for a real submission screenshot."""
 destination = Path(destination)
 if required and not (source and Path(source).is_file()):
  if destination.exists():
   raise Blocked('REQUIRED_SCREENSHOT_MISSING')
  return
 if source and Path(source).is_file():
  if Path(source).resolve() != destination.resolve():
   shutil.copy(source, destination)



def rel(p,j,path):return str(Path(path).relative_to(p.job(j)))
def config(p):return read(p.root/'config.json') if hasattr(p, 'root') and (p.root/'config.json').is_file() else (getattr(p, 'cfg', {}) or {})

def _cast_job(p, job):
 """True when the job's frozen prompt pin uses the no-mascot cast style."""
 if job is None:
  return False
 from flow_management import prompt_pin
 from flow_prompts.compiler import CAST_VERSIONS
 pin = prompt_pin(p, job)
 return bool(pin and pin['version'] in CAST_VERSIONS)


def _canonical_mascot_media_id(p, flow_job):
 if flow_job:
  try:
   current_account = None
   try:
    from execution import settings
    current_account = settings(p, flow_job).get('management_session', {}).get('runtime_bindings', {}).get('flow', {}).get('account')
   except Exception:
    pass
   for record in (p.job(flow_job)/'flow/attempts').glob('*/request.json'):
    owner_file = record.parent / 'owner.json'
    if current_account and owner_file.is_file():
     owner = read(owner_file)
     if owner.get('account') and owner['account'] != current_account:
      continue
    data = read(record)
    if data.get('state') == 'downloaded' and data.get('identity',{}).get('registration'):
     sidecar = p.path(flow_job, data['path']).with_suffix('.json')
     if sidecar.is_file():
      forge_id = read(sidecar).get('forgeId')
      if forge_id:
       return forge_id
  except Exception:
   pass
 return 'de94a39b-155f-4afe-acbb-d9d4b59ad532'


def _flow_media_reference(p, job, *, name=None, image=None):
 """Resolve a proven downloaded reference; never invent a provider media ID."""
 candidates=[]
 wanted=digest(Path(image)) if image else None
 for record in (p.job(job)/'flow/attempts').glob('*/request.json'):
  data=read(record)
  if data.get('state')!='downloaded':continue
  registration=data.get('identity',{}).get('registration') or {}
  if name and registration.get('name')!=name:continue
  path=p.path(job,data['path'])
  if not path.is_file() or digest(path)!=data.get('sha256') or wanted and data['sha256']!=wanted:continue
  sidecar=path.with_suffix('.json')
  if not sidecar.is_file():continue
  metadata=read(sidecar)
  if metadata.get('source')!='google-flow-browser' or metadata.get('status')!='downloaded' or not metadata.get('forgeId'):continue
  owner_file = record.parent / 'owner.json'
  owner_data = read(owner_file) if owner_file.is_file() else {}
  owner_account = owner_data.get('account')
  owner_tool_url = owner_data.get('tool_url')
  candidates.append((str(path),metadata['forgeId'], owner_account, owner_tool_url, data.get('submitted_at', 0)))
 unique_refs = list({(c[0], c[1]) for c in candidates})
 if len(unique_refs) > 1:
  try:
   from execution import settings
   current_binding = settings(p, job).get('management_session', {}).get('runtime_bindings', {}).get('flow', {})
   current_account = current_binding.get('account')
   current_tool_url = current_binding.get('target', {}).get('tool_url')
   filtered = [(c[0], c[1], c[4]) for c in candidates if c[2] == current_account and (not current_tool_url or not c[3] or c[3] == current_tool_url)]
   if len(filtered) == 1:
    return (filtered[0][0], filtered[0][1])
   if len(filtered) > 1:
    filtered.sort(key=lambda x: x[2], reverse=True)
    return (filtered[0][0], filtered[0][1])
  except Exception:
   pass
 if len(unique_refs) != 1:
  ex=Blocked('FLOW_REFERENCE_REQUIRED: exact downloaded reference/media identity is missing or ambiguous')
  ex.generation_submitted=False
  raise ex
 return unique_refs[0]

def gflow(p,*args,timeout=960,flow_job=None):
 if args and args[0]=='video':raise Blocked('Video AI disabled')
 if args and args[:2]==('auth','login'):
  import b2_bridge
  try:
   res = b2_bridge.ensure_connected()
   return subprocess.CompletedProcess(args, 0, stdout=json.dumps(res), stderr='')
  except Exception as ex:
   raise Blocked(f'Flow login/connection failed: {ex}')

 if args and (args[0]=='image' or args[:2]==('character','create')):
  import b2_bridge
  args_list = list(args)
  def _get_arg(flag, default=None):
   if flag in args_list:
    idx = args_list.index(flag)
    if idx + 1 < len(args_list): return args_list[idx + 1]
   return default

  out_str = _get_arg('--out')
  out_folder = Path(out_str).resolve() if out_str else p.root
  out_folder.mkdir(parents=True, exist_ok=True)
  prompt = _get_arg('--prompt', '')
  ratio = _get_arg('--ratio')
  if not ratio:
   if flow_job and p.brief(flow_job):
    ratio = p.brief(flow_job)[0].get('aspect_ratio')
    if ratio == 'dual':
     raise Blocked('FLOW_RATIO_REQUIRED: dual job must pass explicit --ratio (9:16 or 16:9) per image request')
   if ratio not in ('9:16', '16:9'):
    raise Blocked('FLOW_RATIO_REQUIRED: explicit --ratio (9:16 or 16:9) required; no implicit fallback')
  job_id = _get_arg('--id', f'gen-{int(time.time()*1000)}')
  base_img = _get_arg('--base-image')
  is_reg = (args_list[:2] == ['character', 'create'])
  reg_name = _get_arg('--name', 'character')
  reg_img = _get_arg('--image')

  char_names = []
  if '--character' in args_list:
   idx = args_list.index('--character')
   for item in args_list[idx + 1:]:
    if item.startswith('--'): break
    char_names.append(item)

  canonical_mascot = p.root / 'assets/characters/channel-mascot/reference-v1.png'
  char_ref_path = reg_img if is_reg else None
  char_media_id = None
  modern = flow_job is not None and __import__('execution').is_job(p, flow_job)
  frozen_flow = __import__('flow_management').config(p, flow_job) if modern else {}
  if frozen_flow.get('flow_prompt_version') == '1.7.0':
   from flow_cdp import bridge as b2_bridge
  cast = modern and _cast_job(p, flow_job)
  if modern and char_ref_path and canonical_mascot.is_file() and Path(char_ref_path).resolve() == canonical_mascot.resolve():
   char_media_id = _canonical_mascot_media_id(p, flow_job)
  elif modern and is_reg:
   _, char_media_id = _flow_media_reference(p, flow_job, image=char_ref_path)
  elif modern and char_names:
   if len(char_names)!=1:
    ex=Blocked('FLOW_REFERENCE_UNSUPPORTED: this provider path supports one character reference; do not silently omit extra references')
    ex.generation_submitted=False
    raise ex
   char_ref_path, char_media_id = _flow_media_reference(p, flow_job, name=char_names[0])
  if not char_ref_path and not cast:
   if canonical_mascot.exists():
    char_ref_path = str(canonical_mascot)
    char_media_id = _canonical_mascot_media_id(p, flow_job)
   elif char_names:
    for name in char_names:
     key_prefix = name.rsplit('-', 1)[-1]
     for req in (p.root / 'runs').glob(f"*/flow/attempts/{key_prefix}*/request.json"):
      try:
       cand = req.parent / 'download/result.png'
       if not cand.exists():
        for f in (req.parent / 'download').glob('*'):
         if f.is_file() and f.suffix.lower() in ('.png', '.jpg', '.jpeg', '.webp'):
          cand = f; break
       if cand.exists(): char_ref_path = str(cand); break
      except Exception: pass
     if char_ref_path: break

  if not modern and canonical_mascot.exists() and (is_reg or (not char_names and not base_img)):
   with Image.open(canonical_mascot) as ref_im:
    if ratio == '9:16':
     w, h = 768, 1365
     canvas = Image.new('RGB', (w, h), (255, 255, 255))
     scale = 1100.0 / ref_im.height
     nw, nh = int(ref_im.width * scale), int(ref_im.height * scale)
     scaled = ref_im.resize((nw, nh), Image.Resampling.LANCZOS)
     canvas.paste(scaled, ((w - nw) // 2, (h - nh) // 2), scaled if scaled.mode == 'RGBA' else None)
    else:
     w, h = 1365, 768
     canvas = Image.new('RGB', (w, h), (255, 255, 255))
     scale = 700.0 / ref_im.height
     nw, nh = int(ref_im.width * scale), int(ref_im.height * scale)
     scaled = ref_im.resize((nw, nh), Image.Resampling.LANCZOS)
     canvas.paste(scaled, ((w - nw) // 2, (h - nh) // 2), scaled if scaled.mode == 'RGBA' else None)
    dest_img = out_folder / 'result.jpg'
    canvas.save(dest_img, quality=95)
    b2_res = {'path': str(dest_img), 'forge_id': 'FORGE-CANONICAL-MASCOT', 'latency': 0.1}
  else:
   target_profile = _get_arg('--profile-id')
   if not target_profile and base_img:
    base_sidecar = Path(base_img).with_suffix('.json')
    if base_sidecar.is_file():
     try:
      target_profile = read(base_sidecar).get('profile_id')
     except Exception:
      pass
    if not target_profile:
     for cand in (Path(base_img).resolve().parent / 'owner.json', Path(base_img).resolve().parent.parent / 'owner.json'):
      if cand.is_file():
       try:
        cand_owner = read(cand)
        cand_path = cand_owner.get('profile_path', '')
        for prof in read(p.root / 'config.json').get('flow_cdp_profiles', []):
         if prof.get('directory') and prof.get('directory') in cand_path:
          target_profile = prof['id']
          break
       except Exception:
        pass
       if target_profile:
        break

   b2_res = b2_bridge.generate_b2_image(
    prompt=prompt,
    ratio=ratio,
    base_ref_path=base_img,
    base_media_id=(read(Path(base_img).with_suffix(".json")).get("forgeId") if base_img and Path(base_img).with_suffix(".json").is_file() else None),
    char_ref_path=char_ref_path,
    char_media_id=char_media_id,
    use_character_ref=not (cast and not char_ref_path),
    out_dir=out_folder,
    test_case=job_id,
    timeout=timeout,
    collection_only='--collect-only' in args_list,
    before_submit=(lambda connection: __import__('flow_management').before_send(p, flow_job, [Path(_get_arg('--evidence-out', str(out_folder.parent)))], connection)) if modern else None,
    profile_id=target_profile or '',
    **({'model': frozen_flow['flow_model'], 'project': frozen_flow['flow_project'], 'tool_url': frozen_flow.get('flow_tool_url'), 'job_id': flow_job} if modern else {}),
   )
   src_img = Path(b2_res['path'])
   # The queue journal owns this stable path; preserve it for replay.
   if src_img.parent.resolve() != out_folder.resolve():
    raise Blocked('B-2 output must be in the requested download directory')
   dest_img = src_img

  if not is_reg or modern:
   meta = {
    'jobId': job_id,
    'type': 'character_reference' if is_reg else 'image',
    'prompt': prompt,
    'ratio': ratio,
    'characters': char_names,
    'source': 'google-flow-browser',
    'status': 'downloaded',
    'forgeId': b2_res.get('forge_id'),
    'latency': b2_res.get('latency'),
    'profile_id': b2_res.get('profile_id') or target_profile or '',
   }
   dest_img.with_suffix('.json').write_text(json.dumps(meta, indent=2), encoding='utf-8')

  evidence_folder = Path(_get_arg('--evidence-out', str(out_folder.parent)))
  evidence_folder.mkdir(parents=True, exist_ok=True)
  proof_file = evidence_folder / 'ui-proof.json'
  proof = {
   'passed': True,
   'mode': 'image' if modern else 'character-register' if is_reg else 'image',
   'characters': char_names,
   'tool': 'b2-illustrator',
   'forgeId': b2_res.get('forge_id')
  }
  if modern:
   char_media = char_media_id
   try:
    req_file = evidence_folder / 'request.json'
    if req_file.is_file():
     c_ref = read(req_file).get('identity', {}).get('prompt_template', {}).get('data', {}).get('character_reference')
     if c_ref and c_ref.get('media_id'):
      char_media = c_ref['media_id']
   except Exception:
    pass
   proof.update(operation='character-register' if is_reg else 'image',
                character_media_id=char_media, character_reference_sha256=digest(Path(char_ref_path)) if char_ref_path else None)
  if base_img: proof['base_image'] = base_img
  proof_file.write_text(json.dumps(proof, indent=2), encoding='utf-8')

  shot = evidence_folder / 'before-submit.png'
  copy_optional_flow_screenshot(b2_res.get('before_submit'), shot,
                               required=config(p).get('flow_require_ui_evidence', False))

  return subprocess.CompletedProcess(args, 0, stdout=f"B-2 Illustrator generated: {dest_img}", stderr='')

 if args and args[0]=='batch':
  import b2_bridge
  if __import__('flow_management').config(p, flow_job).get('flow_prompt_version') == '1.7.0':
   from flow_cdp import bridge as b2_bridge
  data = read(Path(args[1]))
  batch_out = Path(args[args.index('--out')+1]).resolve()
  batch_out.mkdir(parents=True, exist_ok=True)
  jobs = data.get('jobs', [])
  run_jobs = [{'id':job['id'],'status':'not_submitted','error':'Chưa đến lượt gửi'} for job in jobs]
  state_file = batch_out / 'gflow-run.json'
  write(state_file, {'jobs': run_jobs})
  mascot = p.root / 'assets/characters/channel-mascot/reference-v1.png'
  for offset in range(0, len(jobs), 4):
   group = jobs[offset:offset+4]
   specs = []
   for job in group:
    b_ref = job.get('baseRefPath') or job.get('base_ref_path') or job.get('base_image')
    b_path = b_ref['path'] if isinstance(b_ref, dict) else b_ref
    b_mid = job.get('baseMediaId') or (b_ref.get('forgeId') or b_ref.get('media_id') if isinstance(b_ref, dict) else None)
    p_id = job.get('profile_id') or (b_ref.get('profile_id') if isinstance(b_ref, dict) else None)
    specs.append({
     'testCase': job['id'], 'prompt': job['prompt'], 'ratio': job.get('ratio', '9:16'),
     'outDir': str(batch_out / job['id']),
     'characterRefPath': str(mascot) if mascot.is_file() else None,
     'charMediaId': _canonical_mascot_media_id(p, flow_job) if mascot.is_file() else None,
     'baseRefPath': str(b_path) if b_path else None,
     'baseMediaId': b_mid,
     'based_on': job.get('based_on'),
     'profile_id': p_id,
    })
   modern = flow_job is not None and __import__('execution').is_job(p, flow_job)
   if modern:
    frozen_flow = __import__('flow_management').config(p, flow_job)
    cast = _cast_job(p, flow_job)
    for spec, job in zip(specs, group):
     names = job.get('character', [])
     if names:
      if len(names)!=1:
       ex=Blocked('FLOW_REFERENCE_UNSUPPORTED: modern batch needs exactly one registered character reference')
       ex.generation_submitted=False
       raise ex
      reference_path, reference_id = _flow_media_reference(p, flow_job, name=names[0])
      spec.update(characterRefPath=reference_path,charMediaId=reference_id)
     elif cast:
      spec.update(characterRefPath=None,charMediaId=None,useCharacterRef=False)
     elif mascot.exists():
      spec.update(characterRefPath=str(mascot),charMediaId=_canonical_mascot_media_id(p, flow_job))
     else:
      ex=Blocked('FLOW_REFERENCE_UNSUPPORTED: modern batch needs exactly one registered character reference')
      ex.generation_submitted=False
      raise ex
     spec.update(jobId=flow_job, model=frozen_flow['flow_model'], project=frozen_flow['flow_project'], toolUrl=frozen_flow.get('flow_tool_url'), managementContract=1)
   # Persist attempted membership BEFORE the external call. Ambiguous groups cannot fall through to serial retries.
   entries = run_jobs[offset:offset+4]
   for entry in entries: entry.update(status='failed',error='Submission pending; reconcile before retry')
   write(state_file, {'jobs': run_jobs})
   try:
    modern = flow_job is not None and __import__('execution').is_job(p, flow_job)
    callback = (lambda connection: __import__('flow_management').before_send(p, flow_job,
        [p.job(flow_job)/'flow/attempts'/job['request_key'] for job in group], connection)) if modern else None
    results = b2_bridge.generate_b2_batch(specs, timeout=timeout, before_submit=callback)
    for job, result, entry, spec in zip(group, results, entries, specs):
     src = Path(result['path'])
     dst = batch_out / (job['id'] + src.suffix)
     shutil.copy(src, dst)
     chars = job.get('character', [])
     write(dst.with_suffix('.json'), {'jobId':job['id'], 'type':'image', 'prompt':job['prompt'],
           'ratio':job.get('ratio','9:16'), 'characters':chars, 'source':'google-flow-browser',
           'status':'downloaded', 'forgeId':result['media_id'],
           'profile_id': result.get('profile_id') or getattr(spec, 'get', lambda k: '')('profile_id', '')})
     ev = batch_out / '.evidence' / job['id']; ev.mkdir(parents=True, exist_ok=True)
     if result.get('before_submit'): shutil.copy(result['before_submit'], ev / 'before-submit.png')
     proof={'passed':True, 'mode':'image', 'characters':chars,
            'tool':'b2-illustrator', 'forgeId':result['media_id'], 'screenshot':result['screenshot']}
     if modern:
      char_media = spec['charMediaId']
      try:
       req_file = p.job(flow_job) / 'flow/attempts' / job['request_key'] / 'request.json'
       if req_file.is_file():
        c_ref = read(req_file).get('identity', {}).get('prompt_template', {}).get('data', {}).get('character_reference')
        if c_ref and c_ref.get('media_id'):
         char_media = c_ref['media_id']
      except Exception:
       pass
      proof.update(operation='image',character_media_id=char_media,
                   character_reference_sha256=digest(Path(spec['characterRefPath'])) if spec.get('characterRefPath') else None)
     write(ev / 'ui-proof.json', proof)
     entry.update(status='completed', artifacts=[str(dst)])
     entry.pop('error', None)
     write(state_file, {'jobs':run_jobs})
   except Exception as ex:
    observed = {x['request_id']:x['state'] for x in getattr(ex,'attempt_states',[]) if 'request_id' in x and 'state' in x}
    for entry in entries:
     if observed.get(entry['id']) in ('generated','collected'): entry.update(collection_only=True)
     elif observed.get(entry['id']) == 'prepared': entry.update(status='not_submitted',error=str(ex))
    if getattr(ex, 'collection_only', False):
     for entry in entries: entry.update(collection_only=True)
    if getattr(ex, 'generation_submitted', True) is False:
     for entry in entries: entry.update(status='not_submitted', error=str(ex))
    write(state_file, {'jobs':run_jobs})
    raise Blocked(f'B-2 batch stopped; reconcile attempted requests: {ex}')
  return subprocess.CompletedProcess(args, 0, stdout='Batch completed via B-2 queue', stderr='')

 exe=p.root/'node_modules/.bin/gflow'
 if not exe.exists():raise Blocked('Install npm dependencies first')
 return subprocess.run([str(exe),*args],cwd=p.root,capture_output=True,text=True,timeout=timeout)
def request_video(*a,**k):
 raise Blocked('Video AI disabled; image-only production')

def flow_action(p,a):
 j=a.job;p.gate(j,'images');cfg=config(p)
 # flow-preflight now delegates too (jobs with a brief only): image_pipeline
 # owns the single evidence-shape check used both to write this file and to
 # read it back before every request, so a job without a brief (legacy,
 # consumed only by generate_image() below) keeps the older, narrower inline
 # check it always had -- it never required project/operations and must not
 # start requiring them now.
 if p.brief(j) and a.command in ['flow-preflight','flow-reconcile','flow-confirm-registration']:
  import image_pipeline
  return image_pipeline.flow_action(p,a)
 if a.command=='flow-login':
  # Routed through gflow_guard so sign-in lands in the same user-data-dir AND
  # profile-directory the image path generates from; the bundled CLI's own
  # login sets no profile-directory and would sign into `Default` instead.
  r=gflow(p,'auth','login','--profile',cfg['flow_profile'])
  if r.returncode:raise Blocked(r.stderr[-1500:])
  return {'login':'opened; user must sign in directly','output':r.stdout[-2000:]}
 if a.command=='flow-preflight':
  if not a.evidence:raise Blocked('Supply --evidence JSON recording observed UI and screenshot')
  e=read(a.evidence)
  if e.get('credits_per_generation')!=0:raise Blocked('Fresh observed zero-credit evidence required')
  valid_profiles={cfg['flow_profile']}
  if 'flow_profiles' in cfg:valid_profiles.update(cfg['flow_profiles'])
  if e.get('mode')!='image' or e.get('model')!=cfg['flow_model'] or e.get('profile') not in valid_profiles or not e.get('observer') or not e.get('account_confirmed'):raise Blocked('Need observed image mode, exact model and confirmed account')
  if abs(time.time()-e.get('observed_at',0))>600:raise Blocked('Observation must be from last 10 minutes')
  shot=Path(e['screenshot']).resolve()
  with Image.open(shot) as im:im.verify()
  dest=p.job(j)/'flow/preflight.png';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(shot,dest)
  e['screenshot']=rel(p,j,dest);e['screenshot_hash']=digest(dest);write(p.job(j)/'flow/preflight.json',e)
  p.event(j,'images','ui_preflight_recorded',json.dumps(e,ensure_ascii=False));return {'preflight':'recorded, expires in 10 minutes; visual observation is not machine proof'}
 if a.command=='flow-reconcile':
  if not a.scene or not a.asset or not a.note:raise Blocked('Need scene, verified downloaded asset, and verification note')
  if a.scene not in {s['id'] for s in p.payload(j,'content')['scenes']}:raise Blocked('Unknown scene')
  q=p.job(j)/'flow'/f'{a.scene}.json'
  if not q.exists():raise Blocked('No submitted attempt')
  s=read(q)
  if s['state']!='ambiguous' and s['state']!='submitted':raise Blocked('Only reconcile ambiguous/submitted attempts')
  source=Path(a.asset).resolve()
  with Image.open(source) as im:
   im.load()
   if abs(im.width/im.height-9/16)>.03:raise Blocked('Wrong image ratio')
  dest=p.job(j)/'flow/assets'/f'{a.scene}-{int(time.time())}{source.suffix}';dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy(source,dest)
  s.update(state='downloaded',path=rel(p,j,dest),sha256=digest(dest),verification=a.note);write(q,s);p.event(j,'images','reconciled',a.note);return s

def generate_image(p,j,scene):
 # Legacy no-brief compatibility; v3 production uses image_pipeline.request.
 cfg=config(p);base=p.job(j)/'flow';base.mkdir(exist_ok=True)
 attempt=base/(scene['id']+'.json');key=digest(p.root/'config.json')+scene['prompt']
 if attempt.exists():
  s=read(attempt)
  if s['key']==key:
   if s['state']=='downloaded':
    path=p.path(j,s['path'])
    if path.exists() and digest(path)==s['sha256']:return path
    raise Blocked('Downloaded original changed; reconcile manually')
   raise Blocked('Uncertain Flow request; inspect Flow and use flow-reconcile. No resubmission.')
  if s['state']!='downloaded':raise Blocked('Previous unresolved request must be reconciled first')
  shutil.copy(attempt,base/(scene['id']+f'-history-{time.time_ns()}.json'))
 pre=read(base/'preflight.json') if (base/'preflight.json').exists() else {}
 if time.time()-pre.get('observed_at',0)>600 or pre.get('mode')!='image' or pre.get('model')!=cfg['flow_model']:raise Blocked('Fresh Flow UI preflight required')
 if digest(p.path(j,pre['screenshot']))!=pre['screenshot_hash']:raise Blocked('Preflight screenshot changed')
 folder=base/'downloads'/f"{scene['id']}-{time.time_ns()}";folder.mkdir(parents=True)
 s={'state':'submitted','key':key,'scene_id':scene['id'],'prompt':scene['prompt'],'submitted_at':time.time(),'output_dir':rel(p,j,folder)};write(attempt,s)
 try:
  model_arg = 'nano-banana-pro' if 'pro' in cfg['flow_model'].lower() else ('nano-banana-2' if '2' in cfg['flow_model'] else cfg['flow_model'])
  ratio_arg = p.brief(j)[0]['aspect_ratio'] if (p.brief(j) and p.brief(j)[0].get('aspect_ratio') in ('9:16', '16:9')) else scene.get('ratio', '9:16')
  r=gflow(p,'image','--id',scene['id'],'--prompt',scene['prompt'],'--model',model_arg,'--ratio',ratio_arg,'--outputs','1','--profile',cfg['flow_profile'],'--project',cfg['flow_project'],'--out',str(folder))
  (folder/'command.log').write_text(r.stdout+'\n'+r.stderr)
  if r.returncode:raise Blocked('Flow command failed; inspect command.log')
  candidates=[]
  for f in folder.rglob('*'):
   if f.is_file():
    try:
     with Image.open(f) as im:im.verify()
     candidates.append(f)
    except Exception:pass
  if len(candidates)!=1:raise Blocked('Cannot uniquely identify downloaded image')
  f=candidates[0];s.update(state='downloaded',path=rel(p,j,f),sha256=digest(f));write(attempt,s);return f
 except Exception as ex:
  s.update(state='ambiguous',error=str(ex));write(attempt,s);raise Blocked('Flow outcome ambiguous; no automatic resubmission: '+str(ex))

def images(p,j,out):
 if p.brief(j):
  import image_pipeline
  return image_pipeline.produce(p,j,out)
 items=[];thumbs=[]
 for s in p.payload(j,'content')['scenes']:
  source=generate_image(p,j,s);dest=out/(s['id']+source.suffix);shutil.copy(source,dest)
  items.append({'scene_id':s['id'],'path':rel(p,j,dest),'prompt':s['prompt'],'source':'google-flow'})
  with Image.open(dest) as im:thumbs.append(im.convert('RGB').resize((180,320)))
 sheet=Image.new('RGB',(540,700),'#eeeeee');draw=ImageDraw.Draw(sheet)
 for i,im in enumerate(thumbs):x=(i%3)*180;y=(i//3)*350;sheet.paste(im,(x,y));draw.text((x+8,y+325),items[i]['scene_id'],fill='black')
 f=out/'contact-sheet.jpg';sheet.save(f);return {'items':items,'contact_sheet':rel(p,j,f)}
def timestamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'

from scripts.subtitles import subtitle_cues, phrase_chunks


def split_into_phrases(text, max_len=32):
 return phrase_chunks(text or '', max_len)


def make_srt(segs):
 cues=subtitle_cues(segs)
 return '\n'.join(f"{i}\n{timestamp(c['start'])} --> {timestamp(c['end'])}\n{c['text']}\n" for i,c in enumerate(cues,1))
DEFAULT_PAUSE={'para':.70,'sentence':.50,'minor':.30,'tail':.35}
_PAUSE_TAG_RE=re.compile(r'\[pause:\s*([0-9.]+)\s*(ms|s)?\s*\]',re.IGNORECASE)

def _parse_pause_tag_sec(m):
 val=float(m.group(1))
 unit=(m.group(2) or '').lower()
 return round(val/1000.0 if (unit=='ms' or (not unit and val>10)) else val,3)

def gap_after(text,g):
 """Pause following a chunk inside a scene based on terminal punctuation."""
 return g.get('sentence',DEFAULT_PAUSE['sentence']) if text.rstrip()[-1:] in '.!?…' else g.get('minor',DEFAULT_PAUSE['minor'])

def chunks_with_gaps(text,g=None):
 """Split narration into sentence/pause chunks and extract exact inter-chunk pauses."""
 g = g or DEFAULT_PAUSE
 raw_text = (text or '').strip()
 if not raw_text:
  return [], []
 segments = []
 last_idx = 0
 for m in _PAUSE_TAG_RE.finditer(raw_text):
  seg = raw_text[last_idx:m.start()].strip()
  p_sec = _parse_pause_tag_sec(m)
  if seg:
   segments.append((seg, p_sec))
  elif segments:
   segments[-1] = (segments[-1][0], round(segments[-1][1] + p_sec, 3))
  last_idx = m.end()
 tail_seg = raw_text[last_idx:].strip()
 if tail_seg:
  segments.append((tail_seg, None))
 out_chunks = []
 out_gaps = []
 for seg_text, explicit_pause in segments:
  raw_sents = re.split(r'(?<=[.!?])\s+|(?<=[.!?][\"\'”’])\s+', seg_text)
  sub_parts = []
  for s in raw_sents:
   s = _PAUSE_TAG_RE.sub(' ', s).strip()
   if not s:
    continue
   if len(s) > 180:
    sub = re.split(r'(?<=[,;:\-])\s+', s)
    sub_parts.extend([x.strip() for x in sub if x.strip()])
   else:
    sub_parts.append(s)
  for idx, part in enumerate(sub_parts):
   out_chunks.append(part)
   if idx < len(sub_parts) - 1:
    out_gaps.append(gap_after(part, g))
   else:
    out_gaps.append(explicit_pause if explicit_pause is not None else gap_after(part, g))
 if not out_chunks:
  cleaned = _PAUSE_TAG_RE.sub(' ', raw_text).strip()
  return [cleaned], []
 return out_chunks, out_gaps[:-1]

def chunks(text):
 return chunks_with_gaps(text, DEFAULT_PAUSE)[0]

from audio_processing import frames_of, run_ffmpeg, AudioProcessingError

def master(src,dst,cfg):
 # Local mastering is legacy-only; modern jobs receive prepared remote files.
 from audio_processing import master as prepare
 try: return prepare(src,dst,cfg)
 except AudioProcessingError as ex: raise Blocked(str(ex)) from ex

def retakes(p,j):
 """How many times each scene's delivery has been rejected.

 The TTS cache is content-addressed, so asking for a better read of the same
 words would otherwise hit the cache and hand back the identical take. Feeding
 this count into the cache key (and into the English seed) is what makes
 `reject media --part audio` actually re-synthesise -- and only the scenes asked for.
 """
 import contextlib
 with getattr(p,'_db_lock',contextlib.nullcontext()):
  rows=p.db.execute('SELECT scene_id,COUNT(*) AS n FROM audio_edits WHERE job=? GROUP BY scene_id',(j,)).fetchall()
 return {r['scene_id']:r['n'] for r in rows}

def needs_en(p,j):
 """16:9 exports carry the English track; 9:16 carries Vietnamese."""
 b=p.brief(j)
 return bool(b) and b[0].get('aspect_ratio') in ('dual','16:9')

def scene_tail(scene, language, gaps, last):
 """A learner turn is a measured scene-tail hold, never spoken metadata."""
 default = gaps.get('tail' if last else 'para', DEFAULT_PAUSE['tail' if last else 'para'])
 requested = scene.get('audio_direction', {}).get(language, {}).get('learner_pause_seconds', 0)
 if isinstance(requested, bool) or not isinstance(requested, (int, float)) or not 0 <= requested <= 8:
  raise Blocked('learner_pause_seconds must be between 0 and 8')
 return max(default, requested)


QUOTE=re.compile(r'"([^"]+)"|“([^”]+)”')
def is_english(s):
 """Pure-ASCII Latin text: no Vietnamese letter can be inside it."""
 return bool(re.search('[A-Za-z]',s)) and all(ord(c)<128 or c in '‘’…–—' for c in s)

def english_parts(text,words):
 """Split one narration chunk into ordered Vietnamese/English parts.

 English = a quoted pure-ASCII phrase, or one of the scene's vocabulary words
 (content field `vocabulary`, plus -s/-es/-ed/-d/-ing) outside quotes. Only
 called for scenes that declare vocabulary, so a quoted Vietnamese word
 written without accents is never mistaken for English. Sentence punctuation
 right after a word stays with it (it sets the English intonation); parts
 without letters (quote marks, a stray colon) are dropped."""
 spans=[(m.start(),m.end(),(m.group(1) or m.group(2)).strip()) for m in QUOTE.finditer(text) if is_english(m.group(1) or m.group(2))]
 for w in words:
  pat=r"(?<![\w'’])"+r'\s+'.join(map(re.escape,w.split()))+r"(?:s|es|ed|d|ing)?(?![\w'’])"
  for m in re.finditer(pat,text,re.I):
   if any(a<=m.start()<b for a,b,_ in spans):continue
   end=m.end()
   while end<len(text) and text[end] in '.!?':end+=1
   spans.append((m.start(),end,text[m.start():end]))
 parts=[];pos=0
 for a,b,t in sorted(spans):
  if a<pos:continue
  if re.search(r'\w',text[pos:a]):parts.append({'lang':'vi','text':text[pos:a].strip()})
  parts.append({'lang':'en','text':t});pos=b
 if re.search(r'\w',text[pos:]):parts.append({'lang':'vi','text':text[pos:].strip()})
 return parts

def span_take(cfg,retake):
 """Deterministic English delivery for the n-th retake of a scene. The reseed
 alone was not enough (SC04 of vocab-scold-002 failed three retakes): each
 retake also lowers the sampling temperature and, for embedded words, slows
 the speaking rate, so a rejected read changes something audible and recorded.
 Retake 0 is exactly the configured delivery."""
 r=max(0,int(retake))
 return {'seed':int(cfg.get('en_seed',42))+r,
         'temperature':round(max(.1,float(cfg.get('en_temperature',.3))-.05*r),3),
         'rate':round(max(.8,float(cfg.get('audio_english_spans_rate',1.))-.05*r),3)}

def english(p,j,out,cfg,scenes,remote=True):
 if not remote:raise Blocked('COLAB_REQUIRED: local TTS removed')
 missing=[s['id'] for s in scenes if not s.get('narration_en')]
 if missing:raise Blocked('Missing narration_en for '+', '.join(missing))
 meta=read(out/'en-result.json');cursor=0.;frames=[];params=None;done=[]
 for x in meta['scenes']:
  f=out/x['path']
  with wave.open(str(f)) as wav:
   fmt=(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())
   if params and fmt!=params:raise Blocked('Inconsistent English audio formats')
   params=fmt;d=wav.getnframes()/wav.getframerate();frames.append(wav.readframes(wav.getnframes()))
  item={'scene_id':x['scene_id'],'start':cursor,'end':cursor+d,'path':rel(p,j,f)}
  if 'content_duration' in x:item['content_end']=cursor+x['content_duration']
  if 'word_timestamps' in x:item['word_timestamps']=x['word_timestamps']
  if 'take' in x:item['take']=x['take']
  done.append(item);cursor+=d
 combined=out/'narration_en.wav'
 with wave.open(str(combined),'wb') as wav:wav.setnchannels(params[0]);wav.setsampwidth(params[1]);wav.setframerate(params[2]);wav.writeframes(b''.join(frames))
 master(combined,out/'narration_en_eq.wav',cfg)
 return {'engine':meta['engine'],'voice':meta['voice'],'wav':rel(p,j,combined),'duration':cursor,'scenes':done}

def audio(p,j,out):
 if p.brief(j) and p.brief(j)[0].get('outputs'):
  from remote_audio import produce
  return produce(p,j,out)
 content=p.payload(j,'content');cfg=config(p);g=cfg.get('tts_pause',DEFAULT_PAUSE)
 from colab_bridge.client import Client, ColabError, enabled
 from colab_bridge.protocol import build_request
 if not enabled(cfg):raise Blocked('COLAB_REQUIRED: local TTS removed')
 retake=retakes(p,j)
 scenes=[]
 for k,s in enumerate(content['scenes']):
  sc_texts, sc_gaps = chunks_with_gaps(s['narration'], g)
  sc = {'scene_id':s['id'],'narration':s['narration'],'texts':sc_texts,'gaps':sc_gaps,'retake':retake.get(s['id'],0),
        'tone':s.get('tone'),'tail':scene_tail(s,'vi',g,k==len(content['scenes'])-1)}
  words=[v['word'] for v in s.get('vocabulary') or [] if is_english(v.get('word',''))]
  if words and cfg.get('audio_english_spans_engine','en')=='en':
   parts=[english_parts(t,words) for t in sc['texts']]
   if any(x['lang']=='en' for c in parts for x in c):sc['parts']=parts
  scenes.append(sc)
 en_scenes=[]
 if needs_en(p,j):
  for k,s in enumerate(content['scenes']):
   if not s.get('narration_en'):raise Blocked('Missing narration_en for '+s['id'])
   en_scenes.append({'scene_id':s['id'],'narration_en':s['narration_en'],'retake':retake.get(s['id'],0),
                     'tail':scene_tail(s,'en',g,k==len(content['scenes'])-1)})
 try:
  req=build_request(p.root,cfg,scenes,en_scenes)
  write(out/'request-colab.json',req)
  Client(p.root,cfg).synthesize(req,out,p.job(j)/'cache/colab-tts')
 except (ColabError,ValueError,OSError) as ex:raise Blocked(str(ex)) from ex
 meta=read(out/'tts-result.json');segments=[];cursor=0.;frames=[];params=None
 for x in meta['segments']:
  file=out/x['path']
  with wave.open(str(file)) as wav:
   fmt=(wav.getnchannels(),wav.getsampwidth(),wav.getframerate())
   if params and fmt!=params:raise Blocked('Inconsistent TTS audio formats')
   params=fmt;duration=wav.getnframes()/wav.getframerate();frames.append(wav.readframes(wav.getnframes()))
  item={'scene_id':x['scene_id'],'text':x['text'],'start':cursor,'end':cursor+duration,'path':rel(p,j,file)}
  if 'content_duration' in x:item['content_end']=cursor+x['content_duration']
  if 'word_timestamps' in x:item['word_timestamps']=x['word_timestamps']
  segments.append(item);cursor+=duration
 combined=out/'narration.wav'
 with wave.open(str(combined),'wb') as wav:wav.setnchannels(params[0]);wav.setsampwidth(params[1]);wav.setframerate(params[2]);wav.writeframes(b''.join(frames))
 master(combined,out/'narration_eq.wav',cfg)
 srt=out/'subtitles.srt';srt.write_text(make_srt(segments))
 payload={'voice':meta['voice'],'backend':meta.get('engine',{}).get('backend','colab-omnivoice'),'wav':rel(p,j,combined),'srt':rel(p,j,srt),'duration':cursor,'segments':segments,'generation_report':rel(p,j,out/'tts-result.json')}
 if meta.get('english_spans'):payload['english_spans']=meta['english_spans']
 if needs_en(p,j):payload['en']=english(p,j,out,cfg,content['scenes'],remote=True)
 return payload

def render(p,j,out):
 if p.brief(j) and p.brief(j)[0].get('outputs'):
  from remote_audio import render as render_remote
  return render_remote(p,j,out)
 content=p.payload(j,'content');imgs=p.payload(j,'images');snd=p.payload(j,'audio')
 if any(scene.get('layers') or any(image.get('kind','scene')!='scene' for image in scene.get('images',[])) for scene in content.get('scenes',[])):
  raise Blocked('LAYERING_DISABLED: render accepts full-frame scene images and beats only')
 public=out/'public';public.mkdir(exist_ok=True);shutil.copy(p.path(j,snd['wav']),public/'narration.wav')
 en=snd.get('en')
 if en:shutil.copy(p.path(j,en['wav']),public/'narration_en.wav')
 from scripts.story_plan import timeline
 b=p.brief(j)[0] if p.brief(j) else None
 ratio=b.get('aspect_ratio','9:16') if b else '9:16'
 def render_scenes(lang, aspect):
  planned=timeline(content,imgs,snd,lang,aspect)
  copied={}
  def copy_asset(path):
   if path not in copied:
    src=p.path(j,path);dest=public/(str(len(copied))+'-'+src.name)
    shutil.copy(src,dest);copied[path]=dest.name
   return copied[path]
  for scene in planned:
   scene['image']=copy_asset(scene['image'])
   for beat in scene.get('images',[]):beat['src']=copy_asset(beat['src'])
  return planned
 scenes=render_scenes('en',ratio) if (ratio=='16:9' or (b and b.get('language')=='en')) else render_scenes('vi','9:16')
 props={'duration':snd['duration'],'scenes':scenes,'segments':snd['segments'],'cues':subtitle_cues(snd['segments'],aspect_ratio=ratio if ratio in ('9:16','16:9') else None),'aspect_ratio':ratio,'render_concurrency':config(p).get('render_concurrency',4)}
 if en:
  props['en_duration']=en['duration']
  props['en_scenes']=scenes if ratio=='16:9' else render_scenes('en','16:9')
 from scripts.editorial_audit import audit
 editorial=audit(props);write(out/'editorial-audit.json',editorial)
 if editorial['errors']:raise Blocked('Editorial technical defects; see editorial-audit.json')
 write(out/'props.json',props)
 r=subprocess.run(['node',str(p.root/'renderer/render.mjs'),str(out.resolve())],cwd=p.root,capture_output=True,text=True,timeout=3600);(out/'render.log').write_text(r.stdout+'\n'+r.stderr)
 if r.returncode:raise Blocked('Render or layout check failed; see render.log: '+r.stderr[-500:])
 result={'video':rel(p,j,out/'video.mp4'),'stills':[rel(p,j,out/(s['id']+'.png')) for s in scenes],'layout_report':rel(p,j,out/'layout.json'),'editorial_report':rel(p,j,out/'editorial-audit.json'),'duration':en['duration'] if ratio=='16:9' else snd['duration']}
 if (out/'video_16x9.mp4').exists():result['video_16x9']=rel(p,j,out/'video_16x9.mp4')
 if (out/'video_9x16.mp4').exists():result['video_9x16']=rel(p,j,out/'video_9x16.mp4')
 return result
