"""Google Flow batchexecute RPC codec for Video Pilot Flow CDP (vp-flow-cdp).

Builds request envelopes and parses responses for Google Flow's batchexecute
transport on flow.google.com, executed directly inside signed-in Chrome tabs
via Chrome DevTools Protocol (CDP).
"""
from __future__ import annotations

import json
import random
import re
import uuid
from dataclasses import dataclass
from typing import Any, Optional

BATCH_PATH = "/_/AiSandboxAngularFrontend/data/batchexecute"
MEDIA_HOST = "flow-content.google"

RPC_GEN_IMAGE = "ogiZ0b"
RPC_OPERATION = "jwpduf"
RPC_CREATE_PROJECT = "jHPbke"
RPC_PROJECT_MEDIA = "Zzl0ze"
RPC_MEDIA = "as29s"
RPC_UPLOAD_IMAGE = "maseQ"
RPC_UPSCALE_IMAGE = "SPrCad"
RPC_GEN_VIDEO_START_FRAME = "eb1hJf"
RPC_GEN_VIDEO_START_END_FRAMES = "nprQif"
RPC_GEN_VIDEO_TEXT = "YhhmEf"
RPC_CREDITS = "nzlxg"
RPC_MODEL_CATALOG = "HTrJv"

CAPTCHA_IMAGE = "IMAGE_GENERATION"
CAPTCHA_VIDEO = "VIDEO_GENERATION"
CAPTCHA_UPLOAD_IMAGE = "UPLOAD_IMAGE"
CAPTCHA_SLOT = "__CAPTCHA__"

IMAGE_MODELS = {
    "GEM_PIX_2",
    "NARWHAL",
    "HARBOR_SEAL",
    "BELUGA",
    "GEM_PIX_2_UPSAMPLE_2K",
    "GEM_PIX_2_UPSAMPLE_4K",
}
IMAGE_MODEL = "BELUGA"

IMAGE_MODEL_BY_NICKNAME = {
    "NANO_BANANA_PRO": "GEM_PIX_2",
    "GEM_PIX_2": "GEM_PIX_2",
    "NANO_BANANA_2_1": "BELUGA",
    "NANO_BANANA_2.1": "BELUGA",
    "BELUGA": "BELUGA",
    "BELUGA_DISPLAY": "BELUGA",
    "NANO_BANANA_2": "NARWHAL",
    "NARWHAL": "NARWHAL",
    "NANO_BANANA_2_LITE": "HARBOR_SEAL",
    "NANO_BANANA_LITE": "HARBOR_SEAL",
    "HARBOR_SEAL": "HARBOR_SEAL",
    "UPSAMPLE_2K": "GEM_PIX_2_UPSAMPLE_2K",
    "UPSAMPLE_4K": "GEM_PIX_2_UPSAMPLE_4K",
}
IMAGE_MODEL_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,95}$")

VIDEO_MODEL = "veo_3_1_i2v_s_fast_fl"
VIDEO_MODEL_BY_NICKNAME = {
    # Veo 3.1 Fast (8s default)
    "VEO_3_1_FAST": "veo_3_1_i2v_s_fast_fl",
    "VEO_3.1_FAST": "veo_3_1_i2v_s_fast_fl",
    "VEO_3_FAST": "veo_3_1_i2v_s_fast_fl",
    "VEO_FAST": "veo_3_1_i2v_s_fast_fl",
    "VEO_3_1_FAST_ULTRA": "veo_3_1_i2v_s_fast_ultra_fl",
    # Veo 3.1 Fast durations (4s, 6s)
    "VEO_3_1_FAST_4S": "veo_3_1_i2v_s_fast_4s_fl",
    "VEO_3.1_FAST_4S": "veo_3_1_i2v_s_fast_4s_fl",
    "VEO_3_1_FAST_6S": "veo_3_1_i2v_s_fast_6s_fl",
    "VEO_3.1_FAST_6S": "veo_3_1_i2v_s_fast_6s_fl",
    # Veo 3.1 Quality (8s default)
    "VEO_3_1_QUALITY": "veo_3_1_i2v_s_fl",
    "VEO_3.1_QUALITY": "veo_3_1_i2v_s_fl",
    "VEO_3_QUALITY": "veo_3_1_i2v_s_fl",
    "VEO_QUALITY": "veo_3_1_i2v_s_fl",
    # Veo 3.1 Quality durations (4s, 6s)
    "VEO_3_1_QUALITY_4S": "veo_3_1_i2v_s_quality_4s_fl",
    "VEO_3.1_QUALITY_4S": "veo_3_1_i2v_s_quality_4s_fl",
    "VEO_3_1_QUALITY_6S": "veo_3_1_i2v_s_quality_6s_fl",
    "VEO_3.1_QUALITY_6S": "veo_3_1_i2v_s_quality_6s_fl",
    # Veo 3.1 Lite (8s default)
    "VEO_3_1_LITE": "veo_3_1_interpolation_lite",
    "VEO_3.1_LITE": "veo_3_1_interpolation_lite",
    "VEO_LITE": "veo_3_1_interpolation_lite",
    # Veo 3.1 Lite durations (4s, 6s)
    "VEO_3_1_LITE_4S": "veo_3_1_i2v_s_lite_4s_fl",
    "VEO_3.1_LITE_4S": "veo_3_1_i2v_s_lite_4s_fl",
    "VEO_3_1_LITE_6S": "veo_3_1_i2v_s_lite_6s_fl",
    "VEO_3.1_LITE_6S": "veo_3_1_i2v_s_lite_6s_fl",
    # Omni 1.1 Flash (abra)
    "OMNI_FLASH": "omni_flash_i2v_8s_first_last",
    "OMNI_1_1_FLASH": "omni_flash_i2v_8s_first_last",
    "OMNI": "omni_flash_i2v_8s_first_last",
    "ABRA": "omni_flash_i2v_8s_first_last",
    "OMNI_FLASH_4S": "omni_flash_i2v_4s_first_last",
    "OMNI_FLASH_6S": "omni_flash_i2v_6s_first_last",
    "OMNI_FLASH_8S": "omni_flash_i2v_8s_first_last",
    "OMNI_FLASH_10S": "abra_i2v_10s",
    "ABRA_4S": "omni_flash_i2v_4s_first_last",
    "ABRA_6S": "omni_flash_i2v_6s_first_last",
    "ABRA_8S": "omni_flash_i2v_8s_first_last",
    "ABRA_10S": "abra_i2v_10s",
    "OMNI_1_1_FLASH_4S": "omni_flash_i2v_4s_first_last",
    "OMNI_1_1_FLASH_6S": "omni_flash_i2v_6s_first_last",
    "OMNI_1_1_FLASH_8S": "omni_flash_i2v_8s_first_last",
    "OMNI_1_1_FLASH_10S": "abra_i2v_10s",
    # Upsamplers
    "VEO_3_1_UPSAMPLER_1080P": "veo_3_1_upsampler_1080p",
    "OMNI_UPSAMPLER_360P": "omni_upsampler_360p",
    "VEO_3_1_UPSAMPLER_4K": "veo_3_1_upsampler_4k",
}
VIDEO_MODEL_ID_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_.-]{1,95}$")

ASPECT_SQUARE = 1           # 1024x1024 (1:1)
ASPECT_PORTRAIT = 2         # 768x1376  (9:16)
ASPECT_LANDSCAPE = 3        # 1376x768  (16:9)
ASPECT_PORTRAIT_4_3 = 4     # 896x1200  (3:4)
ASPECT_LANDSCAPE_4_3 = 5    # 1200x896  (4:3)

ASPECT_BY_NAME = {
    "IMAGE_ASPECT_RATIO_SQUARE": ASPECT_SQUARE,
    "IMAGE_ASPECT_RATIO_PORTRAIT": ASPECT_PORTRAIT,
    "IMAGE_ASPECT_RATIO_LANDSCAPE": ASPECT_LANDSCAPE,
    "IMAGE_ASPECT_RATIO_PORTRAIT_THREE_FOUR": ASPECT_PORTRAIT_4_3,
    "IMAGE_ASPECT_RATIO_PORTRAIT_FOUR_THREE": ASPECT_PORTRAIT_4_3,
    "IMAGE_ASPECT_RATIO_LANDSCAPE_FOUR_THREE": ASPECT_LANDSCAPE_4_3,
    "1:1": ASPECT_SQUARE,
    "9:16": ASPECT_PORTRAIT,
    "16:9": ASPECT_LANDSCAPE,
    "3:4": ASPECT_PORTRAIT_4_3,
    "4:3": ASPECT_LANDSCAPE_4_3,
}

# Video aspect ratio enum in Closure L2a(): 0=1:1, 1=9:16, 2=16:9
VIDEO_ASPECT_SQUARE = 0
VIDEO_ASPECT_PORTRAIT = 1
VIDEO_ASPECT_LANDSCAPE = 2

VIDEO_ASPECT_BY_NAME = {
    "VIDEO_ASPECT_RATIO_SQUARE": VIDEO_ASPECT_SQUARE,
    "VIDEO_ASPECT_RATIO_PORTRAIT": VIDEO_ASPECT_PORTRAIT,
    "VIDEO_ASPECT_RATIO_LANDSCAPE": VIDEO_ASPECT_LANDSCAPE,
    "IMAGE_ASPECT_RATIO_SQUARE": VIDEO_ASPECT_SQUARE,
    "IMAGE_ASPECT_RATIO_PORTRAIT": VIDEO_ASPECT_PORTRAIT,
    "IMAGE_ASPECT_RATIO_LANDSCAPE": VIDEO_ASPECT_LANDSCAPE,
    "1:1": VIDEO_ASPECT_SQUARE,
    "9:16": VIDEO_ASPECT_PORTRAIT,
    "16:9": VIDEO_ASPECT_LANDSCAPE,
    "3:4": VIDEO_ASPECT_PORTRAIT,
    "4:3": VIDEO_ASPECT_LANDSCAPE,
}

STATUS_DONE = "CAE"
OUTCOME_OK = 3
OUTCOME_COMPLAINT = 4
SURFACE_ID = 22
REF_TYPE_IMAGE = 1
BASE_TYPE_IMAGE = 2

_UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


class RpcError(RuntimeError):
    """A batchexecute envelope returned an error slot instead of payload data."""

    def __init__(self, rpcid: str, detail: Any):
        super().__init__(f"{rpcid} failed: {detail!r}")
        self.rpcid = rpcid
        self.detail = detail


class FlowBatchError(RuntimeError):
    """The RPC succeeded but the payload lacked expected fields."""


@dataclass(frozen=True)
class RpcResult:
    rpcid: str
    data: Any
    error: Any = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass(frozen=True)
class GeneratedImage:
    media_id: str
    url: str


@dataclass(frozen=True)
class GeneratedVideo:
    media_id: str
    url: str
    status: str = "completed"


def resolve_image_model(key: Optional[str]) -> str:
    if isinstance(key, str):
        normalized = key.strip().upper().replace("-", "_").replace(" ", "_")
        if normalized in IMAGE_MODEL_BY_NICKNAME:
            return IMAGE_MODEL_BY_NICKNAME[normalized]
        if IMAGE_MODEL_ID_RE.fullmatch(normalized):
            return normalized
    return IMAGE_MODEL


def resolve_aspect(aspect: Any) -> int:
    if isinstance(aspect, int):
        if aspect not in (1, 2, 3, 4, 5):
            raise ValueError(f"image aspect must be 1-5, got {aspect}")
        return aspect
    try:
        return ASPECT_BY_NAME[aspect]
    except KeyError:
        raise ValueError(
            f"unknown aspect {aspect!r} — use one of {sorted(ASPECT_BY_NAME)} or 1-5"
        ) from None


def resolve_video_aspect(aspect: Any) -> int:
    """Resolve video aspect ratio to Flow's L2a enum (0=1:1, 1=9:16, 2=16:9)."""
    if isinstance(aspect, int) and not isinstance(aspect, bool):
        if aspect in (0, 1, 2):
            return aspect
        if aspect == ASPECT_LANDSCAPE:
            return VIDEO_ASPECT_LANDSCAPE
        raise ValueError(f"video aspect must be 0-2, got {aspect}")
    try:
        return VIDEO_ASPECT_BY_NAME[str(aspect).strip()]
    except KeyError:
        raise ValueError(
            f"unknown video aspect {aspect!r} — use one of {sorted(VIDEO_ASPECT_BY_NAME)} or 0-2"
        ) from None


def resolve_video_model(
    key: Optional[str],
    aspect: Any = "16:9",
    has_start_frame: bool = True,
    has_end_frame: bool = False,
    catalog: Optional[list[dict[str, Any]]] = None,
    duration_seconds: Optional[int] = None,
) -> str:
    """Resolve video model key (`c.qf`) from catalog or nickname fallback."""
    v_aspect = resolve_video_aspect(aspect)
    raw = (key or "").strip()
    upper = raw.upper().replace("-", "_").replace(" ", "_")

    if duration_seconds is not None:
        dur_upper = f"{upper}_{int(duration_seconds)}S"
        if dur_upper in VIDEO_MODEL_BY_NICKNAME:
            upper = dur_upper

    want_omni = any(k in upper for k in ["OMNI", "ABRA"])
    want_lite = "LITE" in upper
    want_fast = "QUALITY" not in upper and not want_lite and not want_omni

    if catalog:
        req_caps = {1}
        if has_start_frame:
            req_caps.add(5)
        if has_end_frame:
            req_caps.add(7)

        # 1. Direct match on usage key if provided
        for fam in catalog:
            usages = fam.get("usages") or []
            for u in usages:
                if u.get("key") == raw:
                    return str(u["key"])

        # 2. Match target families
        target_fams: list[dict[str, Any]] = []
        for fam in catalog:
            fam_id = str(fam.get("id") or "").lower()
            disp = str(fam.get("display_name") or "").lower()
            if want_omni:
                if "abra" in fam_id or "omni" in disp:
                    target_fams.append(fam)
            elif want_lite:
                if "lite" in fam_id and "low_priority" not in fam_id:
                    target_fams.append(fam)
            elif want_fast:
                if "fast" in fam_id and "low_priority" not in fam_id:
                    target_fams.append(fam)
            else:
                if "quality" in fam_id:
                    target_fams.append(fam)

        if not target_fams:
            target_fams = catalog

        for fam in target_fams:
            candidate_usages: list[dict[str, Any]] = []
            for u in fam.get("usages") or []:
                u_aspects = u.get("aspects") or []
                if u_aspects and v_aspect not in u_aspects:
                    if not want_omni:
                        continue
                hi_list = u.get("capabilities") or []
                if hi_list and not any(req_caps.issubset(set(cap_set)) for cap_set in hi_list):
                    continue
                candidate_usages.append(u)

            if candidate_usages:
                if duration_seconds is not None:
                    target_dur = int(duration_seconds)
                    match_exact = [u for u in candidate_usages if u.get("duration") == target_dur]
                    if match_exact:
                        return str(match_exact[0]["key"])
                    closest = min(
                        candidate_usages,
                        key=lambda u: abs(int(u.get("duration", 8)) - target_dur),
                    )
                    return str(closest["key"])
                match_8s = [u for u in candidate_usages if u.get("duration") == 8]
                if match_8s:
                    return str(match_8s[0]["key"])
                return str(candidate_usages[0]["key"])

    if want_omni:
        dur = 8
        if duration_seconds is not None:
            dur = int(duration_seconds)
        else:
            m = re.search(r"_(\d+)S?$", upper)
            if m:
                dur = int(m.group(1))

        if has_end_frame:
            # omni_flash start_end_frames supports 4s, 6s, 8s
            if dur <= 4:
                return "omni_flash_i2v_4s_first_last"
            elif dur <= 6:
                return "omni_flash_i2v_6s_first_last"
            else:
                return "omni_flash_i2v_8s_first_last"
        else:
            # abra start_frame supports 4s, 6s, 8s, 10s
            if dur <= 4:
                return "abra_i2v_4s"
            elif dur <= 6:
                return "abra_i2v_6s"
            elif dur <= 8:
                return "abra_i2v_8s"
            else:
                return "abra_i2v_10s"

    if upper in VIDEO_MODEL_BY_NICKNAME:
        base_key = VIDEO_MODEL_BY_NICKNAME[upper]
        if not has_end_frame and base_key.endswith("_fl"):
            base_key = base_key[:-3]
        if v_aspect == VIDEO_ASPECT_PORTRAIT and "_portrait" not in base_key:
            if base_key.endswith("_fl"):
                return base_key[:-3] + "_portrait_fl"
            return base_key + "_portrait"
        return base_key

    if raw and VIDEO_MODEL_ID_RE.fullmatch(raw):
        return raw.lower()
    return VIDEO_MODEL


def build_envelope(rpcid: str, inner: Any) -> str:
    return json.dumps(
        [[[rpcid, json.dumps(inner, separators=(",", ":"), ensure_ascii=False), None, "generic"]]],
        separators=(",", ":"),
        ensure_ascii=False,
    )


def parse_envelope(text: str) -> list[RpcResult]:
    if not text:
        return []
    body = text.split("\n", 1)[1] if text.startswith(")]}'") else text
    decoder = json.JSONDecoder()
    results: list[RpcResult] = []
    index = 0
    while index < len(body):
        start = body.find("[", index)
        if start == -1:
            break
        try:
            chunk, consumed = decoder.raw_decode(body[start:])
        except json.JSONDecodeError:
            index = start + 1
            continue
        index = start + consumed
        for entry in chunk if isinstance(chunk, list) else []:
            if not isinstance(entry, list) or not entry or entry[0] != "wrb.fr":
                continue
            rpcid = entry[1] if len(entry) > 1 else "?"
            payload = entry[2] if len(entry) > 2 else None
            if payload is None:
                results.append(RpcResult(rpcid, None, entry[5] if len(entry) > 5 else True))
                continue
            results.append(
                RpcResult(rpcid, json.loads(payload) if isinstance(payload, str) else payload)
            )
    return results


def first_payload(text: str, rpcid: str) -> Any:
    results = parse_envelope(text)
    for result in results:
        if result.rpcid != rpcid:
            continue
        if not result.ok:
            raise RpcError(rpcid, result.error)
        return result.data
    raise FlowBatchError(f"no {rpcid} envelope in response ({len(results)} others)")


def _client_uuid() -> str:
    return str(uuid.uuid4()).upper()


def _context(
    project_id: str,
    asset_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
) -> list:
    return [
        None, SURFACE_ID, None, None, asset_id, project_id, None, workflow_id, None, None,
        [CAPTCHA_SLOT, 1],
    ]


def _image_input(media_id: str, input_type: int) -> list:
    return [media_id, None, None, None, input_type]


def image_request(
    prompt: str,
    project_id: str,
    count: int = 1,
    aspect: Any = ASPECT_LANDSCAPE,
    seed: Optional[int] = None,
    prompts: Optional[list[str]] = None,
    model: str = IMAGE_MODEL,
    ref_media_ids: Optional[list[str]] = None,
    reference_media_ids: Optional[list[str]] = None,
    base_media_id: Optional[str] = None,
    asset_id: Optional[str] = None,
) -> str:
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 4:
        raise ValueError("image count must be an integer from 1 to 4")
    effective_refs = reference_media_ids if reference_media_ids is not None else ref_media_ids
    ratio = resolve_aspect(aspect)
    resolved_model = resolve_image_model(model)
    base = seed if seed is not None else random.randint(1, 10**9)
    items = []
    target_asset = asset_id or base_media_id
    for index in range(count):
        text = prompts[index] if prompts and index < len(prompts) else prompt
        image_inputs = []
        if base_media_id:
            image_inputs.append(_image_input(base_media_id, BASE_TYPE_IMAGE))
        image_inputs.extend(
            _image_input(mid, REF_TYPE_IMAGE)
            for mid in (effective_refs or [])
            if mid != base_media_id
        )
        items.append([
            None, None, image_inputs or None, base + index * 9973, ratio,
            resolved_model, None, _context(project_id, target_asset), [[[text]]],
            None, None, None, None if base_media_id else _client_uuid(), _client_uuid(),
        ])
    return build_envelope(
        RPC_GEN_IMAGE,
        [None, items, 1, _context(project_id, target_asset), [_client_uuid()]],
    )


image_generation_request = image_request


def upload_image_request(
    image_b64: str,
    mime_type: str,
    project_id: str,
    file_name: str = "frame.png",
    asset_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    is_hidden: bool = False,
) -> str:
    """Build `maseQ` (`Q9a`/`T9a`) image upload request envelope.

    Closure `Q9a` field numbers (`ocb` in wO1vlb.js):
      field 1  (idx 0):  _context(project_id, asset_id, workflow_id) with CAPTCHA_SLOT
      field 2  (idx 1):  base64-encoded image bytes
      field 3  (idx 2):  mime_type (e.g. 'image/png')
      field 4  (idx 3):  1 (Dg = true)
      field 7  (idx 6):  crop coordinates (None)
      field 8  (idx 7):  1 if is_hidden else 0
      field 9  (idx 8):  file_name
      field 10 (idx 9):  None
      field 11 (idx 10): workflow seed UUID
      field 12 (idx 11): media seed UUID
      field 13 (idx 12): None (_.Z user context)
      field 14 (idx 13): [1] (_.nO())
    """
    inner = [
        _context(project_id, asset_id=asset_id, workflow_id=workflow_id),
        image_b64,
        mime_type,
        1,
        None,
        None,
        None,
        1 if is_hidden else 0,
        file_name,
        None,
        _client_uuid(),
        _client_uuid(),
        None,
        [1],
    ]
    return build_envelope(RPC_UPLOAD_IMAGE, inner)


def _video_prompt_msg(prompt: str) -> list:
    """Closure `$9a(new a$a, c.Nj)` -> field 3 (idx 2) = `[[[prompt]]]`."""
    return [None, None, [[[prompt]]]]


def _video_frame_input(media_id: str, crop: Optional[list] = None) -> list:
    """Closure `SQ(TQ(new UQ, media_id), tQ(crop))` -> field 2 (idx 1) = media_id."""
    if crop is not None:
        return [None, media_id, None, None, None, crop]
    return [None, media_id]


def _video_item_metadata(
    asset_id: Optional[str] = None,
    workflow_id: Optional[str] = None,
    media_uuid: Optional[str] = None,
    workflow_uuid: Optional[str] = None,
) -> list:
    """Closure `dS` metadata (`l(D)` in `qp()`):
      field 1 (idx 0): scene clip id (None)
      field 2 (idx 1): workflow_id when joining existing workflow, else None
      field 3 (idx 2): asset_id (rb)
      field 4 (idx 3): None
      field 5 (idx 4): Eo[y] media seed UUID
      field 6 (idx 5): tr[y] workflow seed UUID
    """
    m_uuid = media_uuid or _client_uuid()
    w_uuid = None if workflow_id else (workflow_uuid or _client_uuid())
    return [None, workflow_id, asset_id, None, m_uuid, w_uuid]


def video_start_frame_request(
    prompt: str,
    project_id: str,
    first_frame_media_id: str,
    aspect: Any = "16:9",
    model: str = VIDEO_MODEL,
    count: int = 1,
    asset_id: Optional[str] = None,
    catalog: Optional[list[dict[str, Any]]] = None,
    duration_seconds: Optional[int] = None,
) -> str:
    """Build `eb1hJf` (`P$a`/`R$a` = `START_FRAME`) video generation request envelope.

    Item `L$a` fields:
      field 1 (idx 0): _video_prompt_msg(prompt)
      field 2 (idx 1): resolved model key (`c.qf`)
      field 3 (idx 2): video aspect ratio (`0`=1:1, `1`=9:16, `2`=16:9)
      field 4 (idx 3): None
      field 5 (idx 4): _video_frame_input(first_frame_media_id)
      field 6 (idx 5): _video_item_metadata() (`dS`)
    Outer `P$a` fields:
      field 1 (idx 0): items (`[L$a, ...]`)
      field 2 (idx 1): _context(project_id, asset_id)
      field 3 (idx 2): [_client_uuid()] (`LR`)
    """
    ratio = resolve_video_aspect(aspect)
    resolved_model = resolve_video_model(
        model,
        aspect=aspect,
        has_start_frame=True,
        has_end_frame=False,
        catalog=catalog,
        duration_seconds=duration_seconds,
    )
    items = []
    for _ in range(max(1, int(count))):
        items.append([
            _video_prompt_msg(prompt),
            resolved_model,
            ratio,
            None,
            _video_frame_input(first_frame_media_id),
            _video_item_metadata(asset_id=asset_id),
        ])
    return build_envelope(
        RPC_GEN_VIDEO_START_FRAME,
        [items, _context(project_id, asset_id=asset_id), [_client_uuid()]],
    )


def video_start_end_frames_request(
    prompt: str,
    project_id: str,
    first_frame_media_id: str,
    last_frame_media_id: str,
    aspect: Any = "16:9",
    model: str = VIDEO_MODEL,
    count: int = 1,
    asset_id: Optional[str] = None,
    catalog: Optional[list[dict[str, Any]]] = None,
    duration_seconds: Optional[int] = None,
) -> str:
    """Build `nprQif` (`I$a`/`K$a` = `START_END_FRAMES`) video generation request envelope.

    Item `E$a` fields:
      field 1 (idx 0): _video_prompt_msg(prompt)
      field 2 (idx 1): resolved model key (`c.qf`)
      field 3 (idx 2): video aspect ratio (`0`=1:1, `1`=9:16, `2`=16:9)
      field 4 (idx 3): None
      field 5 (idx 4): _video_frame_input(first_frame_media_id)
      field 6 (idx 5): _video_frame_input(last_frame_media_id)
      field 7 (idx 6): _video_item_metadata() (`dS`)
    Outer `I$a` fields:
      field 1 (idx 0): items (`[E$a, ...]`)
      field 2 (idx 1): _context(project_id, asset_id)
      field 3 (idx 2): [_client_uuid()] (`LR`)
    """
    ratio = resolve_video_aspect(aspect)
    resolved_model = resolve_video_model(
        model,
        aspect=aspect,
        has_start_frame=True,
        has_end_frame=True,
        catalog=catalog,
        duration_seconds=duration_seconds,
    )
    items = []
    for _ in range(max(1, int(count))):
        items.append([
            _video_prompt_msg(prompt),
            resolved_model,
            ratio,
            None,
            _video_frame_input(first_frame_media_id),
            _video_frame_input(last_frame_media_id),
            _video_item_metadata(asset_id=asset_id),
        ])
    return build_envelope(
        RPC_GEN_VIDEO_START_END_FRAMES,
        [items, _context(project_id, asset_id=asset_id), [_client_uuid()]],
    )


def video_frames_request(
    prompt: str,
    project_id: str,
    first_frame_media_id: str,
    last_frame_media_id: Optional[str] = None,
    aspect: Any = "16:9",
    model: str = VIDEO_MODEL,
    count: int = 1,
    asset_id: Optional[str] = None,
    catalog: Optional[list[dict[str, Any]]] = None,
    duration_seconds: Optional[int] = None,
) -> tuple[str, str]:
    """Return `(rpcid, envelope)` for either `START_FRAME` or `START_END_FRAMES`."""
    if last_frame_media_id:
        return (
            RPC_GEN_VIDEO_START_END_FRAMES,
            video_start_end_frames_request(
                prompt=prompt,
                project_id=project_id,
                first_frame_media_id=first_frame_media_id,
                last_frame_media_id=last_frame_media_id,
                aspect=aspect,
                model=model,
                count=count,
                asset_id=asset_id,
                catalog=catalog,
                duration_seconds=duration_seconds,
            ),
        )
    return (
        RPC_GEN_VIDEO_START_FRAME,
        video_start_frame_request(
            prompt=prompt,
            project_id=project_id,
            first_frame_media_id=first_frame_media_id,
            aspect=aspect,
            model=model,
            count=count,
            asset_id=asset_id,
            catalog=catalog,
            duration_seconds=duration_seconds,
        ),
    )


def create_project_request(title: str = "Video Pilot") -> str:
    """Build `jHPbke` project creation envelope: `["projects/*", [null, [title]], [null, 22]]`."""
    return build_envelope(
        RPC_CREATE_PROJECT,
        ["projects/*", [None, [title]], [None, SURFACE_ID]],
    )


def operation_request(media_ids: list[str]) -> str:
    """Build `jwpduf` (`gab`/`hab`) batch media operation polling envelope."""
    return build_envelope(
        RPC_OPERATION,
        [None, None, [[mid] for mid in media_ids if mid]],
    )


def media_request(media_id: str) -> str:
    """Build `as29s` (`_.A0a`/`_.B0a`) single media lookup envelope."""
    return build_envelope(RPC_MEDIA, [media_id])


def credits_request() -> str:
    """Build `nzlxg` (`_.tC`) live credit balance query envelope."""
    return build_envelope(RPC_CREDITS, [])


def model_catalog_request() -> str:
    """Build `HTrJv` (`R8a`) model catalog query envelope."""
    return build_envelope(RPC_MODEL_CATALOG, [])


def _walk_strings(node: Any):
    if isinstance(node, str):
        yield node
    elif isinstance(node, list):
        for item in node:
            yield from _walk_strings(item)


def read_images(payload: Any) -> list[GeneratedImage]:
    images: list[GeneratedImage] = []
    seen: set[str] = set()
    for text in _walk_strings(payload):
        if MEDIA_HOST + "/image/" not in text:
            continue
        media_id = text.split("/image/", 1)[1].split("?", 1)[0]
        if media_id in seen:
            continue
        seen.add(media_id)
        images.append(GeneratedImage(media_id=media_id, url=text))
    return images


def read_uploaded_image(payload: Any) -> GeneratedImage:
    """Extract `GeneratedImage(media_id, url)` from `maseQ` response payload."""
    images = read_images(payload)
    if images:
        return images[0]

    media_id = ""
    if (
        isinstance(payload, list)
        and payload
        and isinstance(payload[0], list)
        and payload[0]
        and isinstance(payload[0][0], str)
    ):
        media_id = payload[0][0].strip()

    url = ""
    for text in _walk_strings(payload):
        if text.startswith("https://") and not url:
            url = text
        if not media_id:
            m = _UUID_RE.search(text)
            if m:
                media_id = m.group(0)

    if not media_id:
        raise FlowBatchError(f"Could not extract uploaded media_id from maseQ payload: {payload!r}")
    return GeneratedImage(media_id=media_id, url=url)


def read_project_id(payload: Any) -> str:
    """Extract UUID project_id from `jHPbke` response payload (`_.jO`)."""
    for text in _walk_strings(payload):
        if text.startswith("projects/"):
            cand = text.split("projects/", 1)[1].split("/", 1)[0].strip()
            if _UUID_RE.fullmatch(cand):
                return cand
        m = _UUID_RE.search(text)
        if m:
            return m.group(0)
    raise FlowBatchError(f"Could not extract project_id from jHPbke payload: {payload!r}")


def read_credits(payload: Any) -> dict[str, Any]:
    """Parse `nzlxg` response: `[remaining, paygate_tier, sku, service_tier, top_up, subscription_credits, [expiry_s, nanos]]`."""
    if not isinstance(payload, list):
        raise FlowBatchError(f"Unexpected nzlxg credits payload: {payload!r}")

    def _int_at(arr: list, idx: int, default: int = 0) -> int:
        if idx < len(arr) and arr[idx] is not None:
            try:
                return int(arr[idx])
            except (ValueError, TypeError):
                return default
        return default

    remaining = _int_at(payload, 0, 0)
    paygate_tier = _int_at(payload, 1, 0)
    sku = payload[2] if len(payload) > 2 else None
    service_tier = _int_at(payload, 3, 0)
    top_up = _int_at(payload, 4, 0)
    subscription_credits = _int_at(payload, 5, 1000)

    expiry_epoch: Optional[int] = None
    if len(payload) > 6 and isinstance(payload[6], list) and payload[6]:
        if payload[6][0] is not None:
            try:
                expiry_epoch = int(payload[6][0])
            except (ValueError, TypeError):
                expiry_epoch = None

    return {
        "remaining": remaining,
        "credits_remaining": remaining,
        "paygate_tier": paygate_tier,
        "sku": sku,
        "service_tier": service_tier,
        "top_up": top_up,
        "subscription_credits": subscription_credits,
        "expiry_epoch": expiry_epoch,
    }


def _parse_tier_costs(kp: Any) -> dict[int, int]:
    costs: dict[int, int] = {}
    if not isinstance(kp, list):
        return costs
    for entry in kp:
        if isinstance(entry, list) and len(entry) > 1 and isinstance(entry[0], int):
            tier = entry[0]
            val = entry[1]
            if isinstance(val, list) and val:
                first = val[0]
                if isinstance(first, list) and len(first) > 1 and isinstance(first[1], int):
                    costs[tier] = first[1]
    return costs


def read_model_catalog(payload: Any) -> list[dict[str, Any]]:
    """Parse `HTrJv` (`R8a`) response into a list of video model families and usage keys."""
    families: list[dict[str, Any]] = []
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], list):
        return families
    root = payload[0]
    video_fams = root[4] if len(root) > 4 and isinstance(root[4], list) else []
    for fam in video_fams:
        if not isinstance(fam, list):
            continue
        disp = fam[0] if len(fam) > 0 and isinstance(fam[0], str) else ""
        fam_key = fam[3] if len(fam) > 3 and isinstance(fam[3], str) else ""
        raw_usages = fam[1] if len(fam) > 1 and isinstance(fam[1], list) else []
        usages: list[dict[str, Any]] = []
        for u in raw_usages:
            if not isinstance(u, list) or not u or not isinstance(u[0], str):
                continue
            u_key = u[0]
            # Field 13 (idx 12): G8a -> [aspect_list] where 1=9:16, 2=16:9
            aspects: list[int] = []
            if len(u) > 12 and isinstance(u[12], list) and u[12] and isinstance(u[12][0], list):
                aspects = [int(x) for x in u[12][0] if isinstance(x, int)]
            # Field 8 (idx 7): I8a -> [[[cap_ints], ...]]
            caps: list[list[int]] = []
            if len(u) > 7 and isinstance(u[7], list) and u[7] and isinstance(u[7][0], list):
                for c_entry in u[7][0]:
                    if isinstance(c_entry, list) and c_entry and isinstance(c_entry[0], list):
                        caps.append([int(x) for x in c_entry[0] if isinstance(x, int)])
            duration = int(u[16]) if len(u) > 16 and isinstance(u[16], int) else 8
            credits = _parse_tier_costs(u[4] if len(u) > 4 else None)
            usages.append({
                "key": u_key,
                "aspects": aspects,
                "capabilities": caps,
                "duration": duration,
                "credits": credits,
            })
        families.append({
            "id": fam_key,
            "display_name": disp,
            "usages": usages,
        })
    return families


def read_image_model_catalog(payload: Any) -> list[dict[str, Any]]:
    """Parse `HTrJv` (`R8a`) response into a list of image models."""
    models: list[dict[str, Any]] = []
    if not isinstance(payload, list) or not payload or not isinstance(payload[0], list):
        return models
    root = payload[0]
    image_fams = root[5] if len(root) > 5 and isinstance(root[5], list) else []
    for fam in image_fams:
        if not isinstance(fam, list):
            continue
        disp = fam[0] if len(fam) > 0 and isinstance(fam[0], str) else ""
        fam_key = fam[3] if len(fam) > 3 and isinstance(fam[3], str) else ""
        raw_usages = fam[1] if len(fam) > 1 and isinstance(fam[1], list) else []
        usages: list[dict[str, Any]] = []
        for u in raw_usages:
            if not isinstance(u, list) or not u or not isinstance(u[0], str):
                continue
            u_key = u[0]
            credits = _parse_tier_costs(u[4] if len(u) > 4 else None)
            usages.append({
                "key": u_key,
                "credits": credits,
            })
        models.append({
            "id": fam_key,
            "display_name": disp,
            "usages": usages,
        })
    return models


def _extract_xb_items(payload: Any) -> list[list[Any]]:
    """Extract `_.XB` media arrays from `eS` (field 4), `hab` (field 3), or `as29s` (root)."""
    if not isinstance(payload, list):
        return []
    # eS (eb1hJf / nprQif): field 4 (idx 3) is Ag() -> list of _.XB
    if len(payload) > 3 and isinstance(payload[3], list) and payload[3] and isinstance(payload[3][0], list):
        return payload[3]
    # hab (jwpduf): field 3 (idx 2) is Ag() -> list of _.XB
    if len(payload) > 2 and isinstance(payload[2], list) and payload[2] and isinstance(payload[2][0], list):
        return payload[2]
    # as29s: root is _.XB (field 1 = media_id string)
    if payload and isinstance(payload[0], str) and _UUID_RE.fullmatch(payload[0]):
        return [payload]
    return []


def parse_xb_media_status(xb: list[Any]) -> dict[str, Any]:
    """Inspect a single `_.XB` media array for `media_id`, `status`, `url`, and `error`."""
    media_id = xb[0] if xb and isinstance(xb[0], str) else ""
    video_url = ""
    # 1. Primary check: look for video URL in any string in xb
    for text in _walk_strings(xb):
        if "/video/" in text:
            video_url = text
            if not media_id and "/video/" in text:
                media_id = text.split("/video/", 1)[1].split("?", 1)[0]
            break
        if text.startswith("https://") and (
            ".mp4" in text or "storage.googleapis.com" in text or "video" in text
        ) and "/image/" not in text:
            video_url = text
            break

    # 2. Broader fallback: any https URL in xb that is NOT an image URL
    if not video_url:
        for text in _walk_strings(xb):
            if (
                text.startswith("https://")
                and "/image/" not in text
                and not text.lower().endswith((".png", ".jpg", ".jpeg", ".webp", ".gif"))
            ):
                video_url = text
                break

    # Inspect _.DP (field 6 = idx 5 -> _.VB)
    status = "completed" if video_url else "pending"
    error_detail: Optional[str] = None
    if len(xb) > 5 and isinstance(xb[5], list):
        vb = xb[5]
        # Field 9 (idx 8) of _.VB is _.dy status message: [outcome_code, ...]
        if len(vb) > 8 and isinstance(vb[8], list) and vb[8]:
            code = vb[8][0]
            if code == OUTCOME_OK:
                status = "completed"
            elif code in (OUTCOME_COMPLAINT, 5):
                status = "failed"
                error_detail = f"Video generation failed with outcome={code}: {vb[8]!r}"
        for text in _walk_strings(vb):
            if any(
                err_tok in text
                for err_tok in ("PUBLIC_ERROR_", "UNSAFE", "SAFETY", "FILTER", "FAILED", "CANCELED")
            ):
                status = "failed"
                error_detail = text
                break

    return {
        "media_id": media_id,
        "status": status,
        "url": video_url,
        "error": error_detail,
    }


def read_video_submission(payload: Any) -> dict[str, Any]:
    """Parse initial `eb1hJf` or `nprQif` (`eS`) response for submitted `media_id` and status."""
    xb_items = _extract_xb_items(payload)
    if xb_items:
        info = parse_xb_media_status(xb_items[0])
        if info["status"] == "failed":
            raise FlowBatchError(info["error"] or "Video submission immediately failed")
        if info["media_id"]:
            return info

    # Fallback: scan for UUID in payload
    for text in _walk_strings(payload):
        m = _UUID_RE.search(text)
        if m:
            return {"media_id": m.group(0), "status": "pending", "url": "", "error": None}
    raise FlowBatchError(f"No media_id returned in video submission payload: {payload!r}")


def read_video_poll(payload: Any, target_media_id: Optional[str] = None) -> dict[str, Any]:
    """Parse `jwpduf` (`hab`) or `as29s` (`_.XB`) poll response."""
    xb_items = _extract_xb_items(payload)
    for xb in xb_items:
        info = parse_xb_media_status(xb)
        if target_media_id and info["media_id"] and info["media_id"] != target_media_id:
            continue
        return info

    for text in _walk_strings(payload):
        if MEDIA_HOST + "/video/" in text:
            mid = text.split("/video/", 1)[1].split("?", 1)[0]
            return {"media_id": mid, "status": "completed", "url": text, "error": None}

    return {
        "media_id": target_media_id or "",
        "status": "pending",
        "url": "",
        "error": None,
    }


async def query_credits_rpc(session: Any) -> dict[str, Any]:
    """Convenience helper used by `sys.flow_cdp.accounts` to query live credits on a session."""
    if hasattr(session, "query_credits"):
        return await session.query_credits()
    raise RuntimeError("Session does not implement query_credits()")
