"""Exact inverse-alpha unblending for Google Flow BELUGA & Omni Flash corner stars.

Google Flow stamps a deterministic semi-transparent white 4-pointed star (`alpha_max ~= 0.33`)
near the bottom-right corner on both `BELUGA` keyframes and `omni_flash` MP4 video clips:
- `BELUGA` `1024x1024` (`1:1`): slice `[h-136:h-68, w-136:w-68]` (`68x68`)
- `BELUGA` `768x1376` (`9:16`) / `1376x768` (`16:9`): slice `[h-132:h-64, w-132:w-64]` (`68x68`)
- `omni_flash` MP4 `720x1280` (`9:16`) / `1280x720` (`16:9`): slice `[h-148:h-92, w-148:w-92]` (`56x56`)

Because the stamp is a pure linear blend `I_obs = (1 - alpha) * I_true + 255 * alpha`,
exact inverse unblending `I_true = clip((I_obs - 255 * alpha) / (1 - alpha), 0, 255)`
recovers the underlying texture and video motion pixel-for-pixel with zero blur or smudge.
"""

from __future__ import annotations

import base64
import functools
import json
import subprocess
import zlib
from pathlib import Path

import numpy as np
from PIL import Image

_ALPHA_1X1_B64 = (
    "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"
)

_ALPHA_9X16_16X9_B64 = (
    "eNrtWX1MXFUWf29mgGH46sAwFIjFfqwdSoei6zALioUCZebde+59MytGHdnuMLasnTK7paZCUsNqaroxqYZsEBFN"
    "RZcm2NoWqN1KUdCqyVrQNrubrhtN/Nj9o5tN3KRJm7Bbu+e9xxumklVsYabJck/ey+POe/f+7rm/+7vnXARhqSyV"
    "/4cyJApCuuHmwDIuJq7vk+LN4IEUw0pTDKabYF4sRkHIN94MvrnTlMje10R90F89tjnRvjhvHM95naTJa7IVvixP"
    "IE+eWWejafLZ9cqzFXEU4tUct7V0ItrTodpeeoH9dnNJQlnyxbJ2PkI72O/h3vzZ2l/EXVvqyobYi/Qzctlb5Y5V"
    "l/ghGMMx/zOt3/sP6qWCJEgjtDhdqY/3XjMhPmwaKb3sux9s1EJ2st084FydnJkARfvcsp1ehNPwMf0UJuQe8veG"
    "r6z5i8xWk0G7YstUrQAOqYMdhgKaS11sj3zqJ8MGZe1uwzkbnuHqu+LCqsrp6Ejb1HZ/WZJDBSiQRulePkgvERfL"
    "IM20dZUgBMXdhp+LOv41xoVmpeaPbOObiOjZZSl8Dw/CABmhLt7CJqCREDYNm+hbWfo3yYvCleOirpi1yb+yNFVu"
    "lB3g527Ujgbm56tYM7SDm9rhmfpuk7JqtoqLpyP2mZk+XfmIL897RUrhOcgLLxzgDmhhD9JttEPulpoqrUmCYFbn"
    "MX+BV3HYMDu6bWXFbIpV0XGYpB8QP72T94GJTUtn5EJaSA9DBlldOvvlwscmVsNY0lvi/jIXy6Sd5FH+EnPSBuzZ"
    "jDyNQBiOsRE6gNh6qZNMlixPEQRtz8lYcCQrUo+4lzMjEyDTF4SDxMSCuGYG2Qni5JfIO8iOIAyxPN6EaPornVkK"
    "t1sWnCMP5169q9F/gh8kx9h9oJkXrQIthBaEyqjlccKWbTyfoXwXFN8WFZ5nz4MrK4yxEe+1YxgWj+Lf537U5bHI"
    "mej1XayBfh+OElYJn0vb/Q1rBWHrNa0dFe2G+a0GnQ36U3rySzlvlGd6+mU3qZIOsQM8EsVQg1aBV0i1GsQSVOty"
    "aQE9iLpmYmfqe9K3GOa2/z84aNTePDZnNo9kfFImeV28l/pICm/lHmnUG0EEOg7tCqsWmvFLEEK0yfcz6uQBeoVM"
    "0oAzmPqocVScO8bvK08ah8Vhsc72tnsXe45XkAZsrxJGODKDOMmEFFJ7DUf7/TaOIughB/hVxP88DdC/ckH6T9lK"
    "m9Ly/OK2FvFW1TPZOV87nq5/jltIDznLOlibXINq2UsV1XDxj6AVLRzTu/6k1/XBfrqOdZIjkMU6pTS5g32Da/qV"
    "+qrSx7OLk+bniw2mJ6qvkFp+Gh4iJuogB0kY1fJdOkJ38PMsDPvYB74wzJruj0hMXSv7GC6Q3J+uYm56Ru6lYbgI"
    "tag1xyUX/7rquxQlNo76c91O9jzGFpx3wHHJj0pViPtICxukJ4kIRro2xhcajohqszh2MTNvxzdfARciWYv3Zhog"
    "p3w9JNd3qHb+WnG/7Q/rfrPJDi5yTnJAOSp3C87OJywIHuIhe2XdC63QBi/jPRI1DccE9CIvpqUw3E57SDHrQY7v"
    "lZvrHlnfnf3kD9BXi/quw2a/fZPnADexEJXZSsThgABtxF1Wmw8FRztyoR06Z0xHU8z65Re4mf8bMTdzLgfl1PI/"
    "5Vqva9fT1vD5jMdLp6VJ+pD0AL8bApi7iThWnRMKDoWz38bh4p2Q7muj++lr9Hfe1NJS841nwVbjlLlgUxrGG6k0"
    "RAfpPkaYhiOieqM1Oi+z/GhGE3EHukDGqo7btHYKDAXXGQVkGx4U9TOXP67ex0wsC/UjiH17Ve2KRJWjZsaU+ia0"
    "PphGjPd4Nxbd+L4WG02dQ778K626HqSVrAjVskbVcI2tupbH4vBLW+S6+g+tWkal+cFquJ78au6505D4vvlMdRbG"
    "ol3+mmjPGg69f926yGflx5Jjz/K0YjPsvqEITVeeO0wn13dLjTwWR3gGhzZDGo5Mpz1J0aQiYywKXbNvdKZuUcfS"
    "VVLCXKxAfopfIRHMXd5jFTBKW1C5JvHuIW7c1xYrj9Ki9QfEU7j6Iub6H++Ru8hhMOO+Nw6HvS52gbTCDjmHdqIG"
    "997z4aLluFvUOHnHTPvDqY9VDeCqDBAf85HtNIsNoK746Qp4jz1bU2BZ7Iy2JKrIf7Hd2+DCWGBCmsLY3Y76VoxZ"
    "lJNc9doy45Fba8o8jPdbV1/mXBpElbfzAXhVGiAfyUXguE35vWgRs/5kY6FBR2LBK8/wWlUPGcfcgeBOHCCvw5DU"
    "VxePU5gdhtA1K+5vuSFPOTFjrIR7KwnQPjibPqa+YYnLWYwew/7atGdDI8atRZhtm9AnmzcshDZcz38YVqSeQMWY"
    "lo5grLOVeMyJOCnMU33fVlnLL8JZ9EbFHTsTcso+quL4JqeDrZNkVLGpnPllKItVnpacPNP3ZbVy+pSfQBzuDZI0"
    "LfmLZ2u2xpWr+ti7MsKwil2yzt2b41OOijOxtGltTXdt0BibJ8f7LFeL2LKjGOxJwlJZKktlqcS5/BeFAaGN"
)

_ALPHA_OMNI_VID_56_B64 = (
    "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"
)


@functools.lru_cache(maxsize=4)
def _decode_alpha_square(b64_payload: str, side: int) -> np.ndarray:
    raw = zlib.decompress(base64.b64decode(b64_payload))
    q16 = np.frombuffer(raw, dtype="<u2").reshape(side, side)
    return (q16.astype(np.float64) / 65535.0)[..., None]


def _decode_alpha_68(b64_payload: str) -> np.ndarray:
    return _decode_alpha_square(b64_payload, 68)


def _decode_alpha_vid_56() -> np.ndarray:
    return _decode_alpha_square(_ALPHA_OMNI_VID_56_B64, 56)


def clean_beluga_sparkle_pil(img: Image.Image) -> Image.Image:
    """Remove Google Flow BELUGA's bottom-right star via exact inverse-alpha unblending."""
    w, h = img.size
    if (w, h) == (1024, 1024):
        alpha = _decode_alpha_68(_ALPHA_1X1_B64)
        y0, y1, x0, x1 = h - 136, h - 68, w - 136, w - 68
    elif (w, h) in ((768, 1376), (1376, 768)):
        alpha = _decode_alpha_68(_ALPHA_9X16_16X9_B64)
        y0, y1, x0, x1 = h - 132, h - 64, w - 132, w - 64
    else:
        return img

    orig_mode = img.mode
    arr = np.array(img.convert("RGBA" if orig_mode == "RGBA" else "RGB"), dtype=np.float64)
    rgb_patch = arr[y0:y1, x0:x1, :3]
    unblended = np.clip((rgb_patch - 255.0 * alpha) / np.maximum(0.25, 1.0 - alpha), 0.0, 255.0)
    arr[y0:y1, x0:x1, :3] = np.round(unblended)
    out = Image.fromarray(arr.astype(np.uint8), mode="RGBA" if orig_mode == "RGBA" else "RGB")
    return out if out.mode == orig_mode else out.convert(orig_mode)


def clean_beluga_sparkle_file(img_path: str | Path) -> bool:
    """Clean BELUGA corner sparkle in-place on disk if image matches BELUGA native dimensions."""
    p = Path(img_path)
    if not p.is_file():
        return False
    with Image.open(p) as im:
        if im.size not in ((768, 1376), (1376, 768), (1024, 1024)):
            return False
        cleaned = clean_beluga_sparkle_pil(im.copy())
    cleaned.save(p)
    return True


def clean_omni_video_sparkle_mp4(mp4_path: str | Path) -> bool:
    """Idempotently unblend Google Flow Omni Flash's corner star on 720x1280 or 1280x720 MP4 clips."""
    p = Path(mp4_path)
    if not p.is_file() or p.stat().st_size == 0:
        return False

    sidecar = p.with_suffix(".json")
    sidecar_obj: dict = {}
    if sidecar.is_file():
        try:
            sidecar_obj = json.loads(sidecar.read_text(encoding="utf-8"))
            if sidecar_obj.get("sparkle_unblended") is True:
                return False
        except Exception:
            sidecar_obj = {}

    probe = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate",
            "-of",
            "json",
            str(p),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        return False
    streams = json.loads(probe.stdout or "{}").get("streams", [])
    if not streams:
        return False
    w = int(streams[0].get("width") or 0)
    h = int(streams[0].get("height") or 0)
    fps_str = str(streams[0].get("r_frame_rate") or "24/1")
    if (w, h) not in ((720, 1280), (1280, 720)):
        return False

    raw_bytes = subprocess.check_output(
        ["ffmpeg", "-v", "error", "-i", str(p), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    )
    frame_bytes = w * h * 3
    if not raw_bytes or len(raw_bytes) % frame_bytes != 0:
        return False

    frames = np.frombuffer(raw_bytes, dtype=np.uint8).reshape(-1, h, w, 3).copy()
    alpha = _decode_alpha_vid_56()[None, ...]  # (1, 56, 56, 1)
    y0, y1, x0, x1 = h - 148, h - 92, w - 148, w - 92
    patch = frames[:, y0:y1, x0:x1, :].astype(np.float64)
    unblended = np.clip(np.round((patch - 255.0 * alpha) / np.maximum(0.25, 1.0 - alpha)), 0.0, 255.0)
    frames[:, y0:y1, x0:x1, :] = unblended.astype(np.uint8)

    tmp_mp4 = p.with_name(f".{p.stem}_unblend.mp4")
    enc_cmd = [
        "ffmpeg",
        "-y",
        "-v",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{w}x{h}",
        "-r",
        fps_str,
        "-i",
        "-",
        "-i",
        str(p),
        "-map",
        "0:v:0",
        "-map",
        "1:a?",
        "-c:v",
        "libx264",
        "-crf",
        "14",
        "-preset",
        "fast",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "copy",
        str(tmp_mp4),
    ]
    subprocess.run(enc_cmd, input=frames.tobytes(), check=True)
    tmp_mp4.replace(p)

    if sidecar.is_file() or sidecar_obj:
        sidecar_obj["sparkle_unblended"] = True
        sidecar.write_text(json.dumps(sidecar_obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        sidecar.write_text(json.dumps({"sparkle_unblended": True}, indent=2) + "\n", encoding="utf-8")
    return True
