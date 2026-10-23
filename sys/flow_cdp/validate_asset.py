"""Read-only verification of downloaded bytes, never trusts a UI extension.

Includes automated bottom blank-gap inspection to catch unintended white subtitle
margins at asset ingestion time rather than relying on post-hoc zoom cropping.
"""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image


def check_bottom_blank_gap(image: Image.Image, bottom_fraction: float = 0.18, white_threshold: int = 242) -> dict:
    """Inspects the bottom band of an image for an unintended solid white/blank margin."""
    rgb = image.convert('RGB')
    width, height = rgb.size
    band_top = max(0, int(height * (1.0 - bottom_fraction)))
    band = rgb.crop((0, band_top, width, height))
    pixels = list(band.getdata())
    if not pixels:
        return {'bottomBlankRatio': 0.0, 'hasBottomBlankGap': False}
    near_white = sum(
        1 for (r, g, b) in pixels
        if min(r, g, b) >= white_threshold and (max(r, g, b) - min(r, g, b)) <= 12
    )
    blank_ratio = round(near_white / len(pixels), 4)
    return {
        'bottomBlankRatio': blank_ratio,
        'hasBottomBlankGap': blank_ratio >= 0.92,
    }


def validate_asset(file, ratio, declared_mime=None, *, require_full_bleed=False):
    if ratio not in ('16:9', '9:16'):
        raise ValueError('Unsupported ratio')
    file = Path(file).resolve(strict=True)
    with Image.open(file) as image:
        fmt = image.format
        image.verify()
    allowed = {'PNG': ('image/png', '.png'), 'JPEG': ('image/jpeg', '.jpg'), 'WEBP': ('image/webp', '.webp')}
    if fmt not in allowed:
        raise ValueError('Unsupported actual image format')
    with Image.open(file) as image:
        image.load()
        width, height = image.size
        if getattr(image, 'n_frames', 1) != 1:
            raise ValueError('Animated image not accepted')
        gap_info = check_bottom_blank_gap(image)
    mime, extension = allowed[fmt]
    if declared_mime and declared_mime != mime:
        raise ValueError('Declared MIME differs from actual bytes')
    numerator, denominator = map(int, ratio.split(':'))
    if abs(width / height - numerator / denominator) > .04:
        raise ValueError('Actual aspect ratio differs from request')
    if require_full_bleed and gap_info['hasBottomBlankGap']:
        raise ValueError(f"Unintended bottom blank margin detected ({gap_info['bottomBlankRatio']*100:.1f}% white)")
    with file.open('rb') as stream:
        if hasattr(hashlib, 'file_digest'):
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        else:
            h = hashlib.sha256()
            while chunk := stream.read(65536):
                h.update(chunk)
            digest = h.hexdigest()
    return {
        'path': str(file),
        'sha256': digest,
        'mimeType': mime,
        'extension': extension,
        'width': width,
        'height': height,
        'ratio': ratio,
        'bottomBlankRatio': gap_info['bottomBlankRatio'],
        'hasBottomBlankGap': gap_info['hasBottomBlankGap'],
        'technicalValidation': 'pass',
        'visualReview': 'pending',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('file')
    parser.add_argument('--ratio', required=True, choices=['16:9', '9:16'])
    parser.add_argument('--declared-mime')
    parser.add_argument('--require-full-bleed', action='store_true')
    args = parser.parse_args()
    print(json.dumps(validate_asset(args.file, args.ratio, args.declared_mime, require_full_bleed=args.require_full_bleed), indent=2))
