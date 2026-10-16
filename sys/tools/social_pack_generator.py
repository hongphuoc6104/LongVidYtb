"""Deterministic social metadata from approved copy and measured scene timing."""
from __future__ import annotations

import re


def timestamp(seconds: float) -> str:
    """Format measured seconds without wrapping after one hour."""
    total = int(seconds)
    return f'{total // 3600:02}:{total // 60 % 60:02}:{total % 60:02}' if total >= 3600 else f'{total // 60:02}:{total % 60:02}'


def social_post_kit(brief: dict, scenes: list[dict], deliveries: list[dict], content: dict | None = None) -> str:
    """Use supplied editorial copy; never fabricate sources or performance claims."""
    packaging = brief.get('packaging', {})
    title = brief.get('youtube_title') or packaging.get('youtube_title') or brief.get('topic', '')
    if len(title) > 55:
        raise ValueError('SOCIAL_TITLE_TOO_LONG: maximum 55 characters')
    lines = ['# SOCIAL POST KIT', '', '## YouTube', title, '',
             brief.get('social_copy', {}).get('youtube_description', brief.get('goal', '')), '', '### Timestamps']
    seen = set()
    for scene in scenes:
        chapter = scene.get('chapter_id', scene['id'])
        if chapter in seen:
            continue
        seen.add(chapter)
        lines.append(f"{timestamp(scene['start'])} {scene.get('chapter_title', scene.get('title', chapter))}")
    lines += ['', '### Sources']
    for source in brief.get('sources', []):
        lines.append(f"- {source.get('title', '')}: {source.get('reference', '')}")
    tags = brief.get('seo_keywords', packaging.get('seo_keywords', []))
    lines += ['', '### Tags', ', '.join(tags), '', '## Deliverables']
    lines += [f"- {item['file']}" for item in deliveries]
    lines += ['', '## TikTok / Facebook Reels']
    for short in brief.get('spinoff_shorts', []):
        lines += ['', f"### {short['id']}", short.get('hook_title', ''), short.get('caption', short.get('opening_hook', ''))]
    post = brief.get('social_copy', {}).get('facebook_post', '')
    if not post and content:
        sentences = re.split(r'(?<=[.!?])\s+', ' '.join(scene['narration'] for scene in content['scenes']))
        selected = []
        for sentence in sentences:
            if len((' '.join(selected) + ' ' + sentence).split()) > 160:
                break
            selected.append(sentence)
            if len(' '.join(selected).split()) >= 125:
                break
        post = ' '.join(selected) + '\n\nBạn đã gặp nghịch lý này trong quá trình nghiên cứu chưa?'
    lines += ['', '#NghienCuu #TuDuyPhanBien #HocThuat #TriThuc #PhuongPhapNghienCuu', '', '## Facebook Page / Group',
              post or brief.get('goal', ''), '']
    return '\n'.join(lines)
