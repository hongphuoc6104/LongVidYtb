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

CAPTCHA_IMAGE = "IMAGE_GENERATION"
CAPTCHA_SLOT = "__CAPTCHA__"

IMAGE_MODELS = {"GEM_PIX_2", "NARWHAL", "HARBOR_SEAL", "BELUGA"}
IMAGE_MODEL = "BELUGA"

IMAGE_MODEL_BY_NICKNAME = {
    "NANO_BANANA_PRO": "GEM_PIX_2",
    "NANO_BANANA_2_1": "BELUGA",
    "NANO_BANANA_2.1": "BELUGA",
    "BELUGA": "BELUGA",
    "NANO_BANANA_2": "NARWHAL",
    "NANO_BANANA_2_LITE": "HARBOR_SEAL",
    "NANO_BANANA_LITE": "HARBOR_SEAL",
}
IMAGE_MODEL_ID_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,95}$")

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

STATUS_DONE = "CAE"
OUTCOME_OK = 3
OUTCOME_COMPLAINT = 4
SURFACE_ID = 22
REF_TYPE_IMAGE = 1
BASE_TYPE_IMAGE = 2


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


def _context(project_id: str, asset_id: Optional[str] = None) -> list:
    return [
        None, SURFACE_ID, None, None, asset_id, project_id, None, None, None, None,
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
    base_media_id: Optional[str] = None,
    asset_id: Optional[str] = None,
) -> str:
    if not isinstance(count, int) or isinstance(count, bool) or not 1 <= count <= 4:
        raise ValueError("image count must be an integer from 1 to 4")
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
            for mid in (ref_media_ids or [])
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
