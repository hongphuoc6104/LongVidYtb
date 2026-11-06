"""Chain planning and task generation for Flow Video daisy chain and scene pairs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from sys.flow_video.models import (
    ChainMode,
    FlowVideoChainSpec,
    KeyframeSpec,
    ScenePairSpec,
    VideoChainSpec,
    VideoClipTask,
)
from typing import Any

SILENT_PROMPT_SUFFIX = ", silent visual storytelling, no talking, no lip movement"

_TALKING_KEYWORDS = (
    "no talking",
    "no lip movement",
    "silent visual",
    "no dialogue",
    "without dialogue",
    "no speech",
    "silent storytelling",
)


def select_clip_duration_and_credits(
    target_sec: float,
    video_model: str,
    has_end_frame: bool,
    default_duration_sec: int = 6,
    auto_duration: bool = True,
    mode: str | ChainMode | None = None,
) -> tuple[int, int]:
    """Select clip duration and credit cost based on target duration and video model capabilities."""
    vm = (video_model or "").lower().strip()
    mode_str = str(mode.value if isinstance(mode, ChainMode) else (mode or "")).lower().strip()

    if mode_str == "zero_credit_flipbook" or "flipbook" in vm or "zero_credit" in vm:
        return (max(1, int(round(target_sec))), 0)

    is_omni = any(k in vm for k in ["omni", "abra"])

    if is_omni:
        allowed = [4, 6, 8] if has_end_frame else [4, 6, 8, 10]
        credit_map = {4: 7, 6: 10, 8: 12, 10: 15}

        if auto_duration:
            if target_sec <= 4.8:
                dur = 4
            elif target_sec <= 6.8:
                dur = 6
            elif target_sec <= 8.8 or has_end_frame:
                dur = 8
            else:
                dur = 10
            return (dur, credit_map[dur])
        else:
            closest_dur = min(allowed, key=lambda d: abs(d - default_duration_sec))
            return (closest_dur, credit_map[closest_dur])

    if "lite" in vm:
        return (8, 10)
    if "quality" in vm:
        return (8, 100)
    if "fast" in vm:
        return (8, 20)

    # Fallback to omni_flash defaults
    allowed = [4, 6, 8] if has_end_frame else [4, 6, 8, 10]
    credit_map = {4: 7, 6: 10, 8: 12, 10: 15}
    if auto_duration:
        if target_sec <= 4.8:
            dur = 4
        elif target_sec <= 6.8:
            dur = 6
        elif target_sec <= 8.8 or has_end_frame:
            dur = 8
        else:
            dur = 10
        return (dur, credit_map[dur])
    closest_dur = min(allowed, key=lambda d: abs(d - default_duration_sec))
    return (closest_dur, credit_map[closest_dur])


def apply_prompt_guard(prompt: str, guard_enabled: bool = True) -> str:
    """Ensure characters do not flap mouths while narrator voiceover speaks."""
    cleaned = (prompt or "").strip()
    if not guard_enabled:
        return cleaned

    lower = cleaned.lower()
    if any(kw in lower for kw in _TALKING_KEYWORDS):
        return cleaned

    if not cleaned:
        return SILENT_PROMPT_SUFFIX.lstrip(", ")
    return f"{cleaned}{SILENT_PROMPT_SUFFIX}"


def build_daisy_chain_tasks(
    keyframes: list[KeyframeSpec],
    work_dir: str | Path,
    aspect: str = "16:9",
    video_model: str = "omni_flash",
    duration_seconds: int = 6,
    no_talking_prompt_guard: bool = True,
    seed: int | None = None,
    auto_duration: bool = True,
) -> list[VideoClipTask]:
    """Generate daisy chain clip tasks (F0 -> F1, F1 -> F2, ..., F_{N-1} -> F_N).

    Clip 0 keeps the full clip.
    Every subsequent clip (i >= 1) sets `trim_first_frame = True` so the join boundary
    never duplicates the shared keyframe.
    """
    if len(keyframes) < 2:
        raise ValueError(
            f"Daisy chain requires at least 2 keyframes (received {len(keyframes)})"
        )

    clips_dir = Path(work_dir) / "clips"
    tasks: list[VideoClipTask] = []

    for i in range(len(keyframes) - 1):
        kf_start = keyframes[i]
        kf_end = keyframes[i + 1]

        clip_id = f"clip_{i:03d}_{kf_start.id}_to_{kf_end.id}"
        out_path = clips_dir / f"{clip_id}.mp4"
        raw_prompt = kf_start.motion_prompt or "smooth cinematic transition"
        final_prompt = apply_prompt_guard(raw_prompt, no_talking_prompt_guard)

        target_sec = float(getattr(kf_start, "target_duration", None) or duration_seconds)
        has_end = bool(kf_end.image_path)
        clip_dur, clip_cost = select_clip_duration_and_credits(
            target_sec=target_sec,
            video_model=video_model,
            has_end_frame=has_end,
            default_duration_sec=duration_seconds,
            auto_duration=auto_duration,
        )

        task = VideoClipTask(
            clip_id=clip_id,
            index=i,
            start_frame_path=kf_start.image_path or "",
            end_frame_path=kf_end.image_path,
            motion_prompt=final_prompt,
            output_mp4_path=str(out_path.resolve()),
            aspect=aspect,
            video_model=video_model,
            duration_seconds=clip_dur,
            target_duration=getattr(kf_start, "target_duration", None),
            trim_first_frame=(i > 0),
            seed=seed,
            status="pending",
            credit_cost=clip_cost,
        )
        tasks.append(task)

    return tasks


def build_scene_pair_tasks(
    scene_pairs: list[ScenePairSpec],
    work_dir: str | Path,
    aspect: str = "16:9",
    video_model: str = "omni_flash",
    duration_seconds: int = 6,
    no_talking_prompt_guard: bool = True,
    seed: int | None = None,
    auto_duration: bool = True,
) -> list[VideoClipTask]:
    """Generate tasks for independent scene pairs (A_k -> B_k).

    Preserves target_duration and sets trim_first_frame = False.
    """
    if not scene_pairs:
        raise ValueError("Scene pairs requires at least 1 scene pair specification")

    clips_dir = Path(work_dir) / "clips"
    tasks: list[VideoClipTask] = []

    for k, sp in enumerate(scene_pairs):
        clip_id = f"clip_{k:03d}_{sp.id}"
        out_path = clips_dir / f"{clip_id}.mp4"
        raw_prompt = sp.motion_prompt or "cinematic scene transition"
        final_prompt = apply_prompt_guard(raw_prompt, no_talking_prompt_guard)

        target_sec = float(sp.target_duration) if sp.target_duration is not None else float(duration_seconds)
        has_end = bool(sp.end_image_path or sp.end_image_prompt)
        clip_dur, clip_cost = select_clip_duration_and_credits(
            target_sec=target_sec,
            video_model=video_model,
            has_end_frame=has_end,
            default_duration_sec=duration_seconds,
            auto_duration=auto_duration,
        )

        task = VideoClipTask(
            clip_id=clip_id,
            index=k,
            start_frame_path=sp.start_image_path or "",
            end_frame_path=sp.end_image_path,
            motion_prompt=final_prompt,
            output_mp4_path=str(out_path.resolve()),
            aspect=aspect,
            video_model=video_model,
            duration_seconds=clip_dur,
            target_duration=sp.target_duration,
            trim_first_frame=bool(getattr(sp, "trim_first_frame", False)),
            seed=seed,
            status="pending",
            credit_cost=clip_cost,
        )
        tasks.append(task)

    return tasks


def build_flipbook_tasks(
    spec: VideoChainSpec,
    work_dir: str | Path | None = None,
) -> list[VideoClipTask]:
    """Generate tasks for 0-credit keyframe flipbook transitions or holds.

    Each task represents a 0-credit keyframe transition (KFi -> KFi+1)
    or single keyframe hold if 1 frame, with credit_cost = 0 and exact target_duration_sec.
    """
    wd = Path(work_dir) if work_dir else Path(f"sys/runs/flow_video_{spec.job_id}")
    clips_dir = wd / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    tasks: list[VideoClipTask] = []

    if spec.keyframes:
        if len(spec.keyframes) == 1:
            kf = spec.keyframes[0]
            clip_id = f"clip_000_{kf.id}_hold"
            out_path = clips_dir / f"{clip_id}.mp4"
            target_sec = float(getattr(kf, "target_duration", None) or spec.duration_seconds)
            task = VideoClipTask(
                clip_id=clip_id,
                index=0,
                start_frame_path=kf.image_path or "",
                end_frame_path=None,
                motion_prompt=kf.motion_prompt or "smooth animated keyframe hold",
                output_mp4_path=str(out_path.resolve()),
                aspect=spec.aspect,
                video_model="zero_credit_flipbook",
                duration_seconds=max(1, int(round(target_sec))),
                target_duration=target_sec,
                trim_first_frame=False,
                status="pending",
                credit_cost=0,
            )
            tasks.append(task)
        else:
            for i in range(len(spec.keyframes) - 1):
                kf_start = spec.keyframes[i]
                kf_end = spec.keyframes[i + 1]
                clip_id = f"clip_{i:03d}_{kf_start.id}_to_{kf_end.id}"
                out_path = clips_dir / f"{clip_id}.mp4"
                target_sec = float(getattr(kf_start, "target_duration", None) or spec.duration_seconds)
                task = VideoClipTask(
                    clip_id=clip_id,
                    index=i,
                    start_frame_path=kf_start.image_path or "",
                    end_frame_path=kf_end.image_path,
                    motion_prompt=kf_start.motion_prompt or "smooth animated flipbook crossfade",
                    output_mp4_path=str(out_path.resolve()),
                    aspect=spec.aspect,
                    video_model="zero_credit_flipbook",
                    duration_seconds=max(1, int(round(target_sec))),
                    target_duration=target_sec,
                    trim_first_frame=False,
                    status="pending",
                    credit_cost=0,
                )
                tasks.append(task)
    elif spec.scene_pairs:
        for k, sp in enumerate(spec.scene_pairs):
            clip_id = f"clip_{k:03d}_{sp.id}"
            out_path = clips_dir / f"{clip_id}.mp4"
            target_sec = float(sp.target_duration) if sp.target_duration is not None else float(spec.duration_seconds)
            task = VideoClipTask(
                clip_id=clip_id,
                index=k,
                start_frame_path=sp.start_image_path or "",
                end_frame_path=sp.end_image_path,
                motion_prompt=sp.motion_prompt or "smooth animated flipbook crossfade",
                output_mp4_path=str(out_path.resolve()),
                aspect=spec.aspect,
                video_model="zero_credit_flipbook",
                duration_seconds=max(1, int(round(target_sec))),
                target_duration=target_sec,
                trim_first_frame=False,
                status="pending",
                credit_cost=0,
            )
            tasks.append(task)
    else:
        raise ValueError("Zero-credit flipbook requires at least 1 keyframe or scene pair")

    return tasks


def build_chain_tasks(
    spec: VideoChainSpec,
    work_dir: str | Path | None = None,
) -> list[VideoClipTask]:
    """Dispatch task generation based on chain mode."""
    wd = Path(work_dir) if work_dir else Path(f"sys/runs/flow_video_{spec.job_id}")
    auto_dur = getattr(spec, "auto_duration", True)
    if spec.mode == ChainMode.DAISY_CHAIN:
        return build_daisy_chain_tasks(
            keyframes=spec.keyframes,
            work_dir=wd,
            aspect=spec.aspect,
            video_model=spec.video_model,
            duration_seconds=spec.duration_seconds,
            no_talking_prompt_guard=spec.no_talking_prompt_guard,
            auto_duration=auto_dur,
        )
    elif spec.mode == ChainMode.ZERO_CREDIT_FLIPBOOK:
        return build_flipbook_tasks(spec, work_dir=wd)
    else:
        return build_scene_pair_tasks(
            scene_pairs=spec.scene_pairs,
            work_dir=wd,
            aspect=spec.aspect,
            video_model=spec.video_model,
            duration_seconds=spec.duration_seconds,
            no_talking_prompt_guard=spec.no_talking_prompt_guard,
            auto_duration=auto_dur,
        )


# Aliases
build_daisy_chain_specs = build_daisy_chain_tasks
build_scene_pair_specs = build_scene_pair_tasks


@dataclass
class VideoChainPlan:
    job_id: str
    mode: ChainMode
    aspect: str
    video_model: str
    clips: list[VideoClipTask]
    total_credit_cost: int
    total_duration_sec: float
    auto_duration: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "mode": self.mode.value if isinstance(self.mode, ChainMode) else str(self.mode),
            "aspect": self.aspect,
            "video_model": self.video_model,
            "clips": [c.to_dict() for c in self.clips],
            "total_credit_cost": self.total_credit_cost,
            "total_duration_sec": self.total_duration_sec,
            "auto_duration": self.auto_duration,
            "nb_clips": len(self.clips),
        }

    def __getitem__(self, item: str) -> Any:
        return getattr(self, item)


def build_chain_plan(
    spec: VideoChainSpec | FlowVideoChainSpec | None = None,
    work_dir: str | Path | None = None,
    **kwargs: Any,
) -> VideoChainPlan:
    """Build an execution plan for a video chain and calculate total credits."""
    if spec is None:
        spec = VideoChainSpec.from_dict(kwargs)

    wd = Path(work_dir) if work_dir else Path(f"sys/runs/flow_video_{spec.job_id}")
    auto_dur = getattr(spec, "auto_duration", True)

    clips = build_chain_tasks(spec, work_dir=wd)

    total_credits = sum(getattr(c, "credit_cost", 10) for c in clips)
    total_dur = sum(getattr(c, "duration_sec", c.duration_seconds) for c in clips)

    return VideoChainPlan(
        job_id=spec.job_id,
        mode=spec.mode,
        aspect=spec.aspect,
        video_model=spec.video_model,
        clips=clips,
        total_credit_cost=total_credits,
        total_duration_sec=total_dur,
        auto_duration=auto_dur,
    )


def export_remotion_beats(
    completed_clips: list[VideoClipTask | dict[str, Any]],
    mode: ChainMode = ChainMode.DAISY_CHAIN,
    fps: int = 30,
) -> list[dict[str, Any]]:
    """Export Remotion-compatible scene beat metadata for `sys/renderer/index.tsx`."""
    beats: list[dict[str, Any]] = []

    for item in completed_clips:
        if isinstance(item, VideoClipTask):
            d = item.to_dict()
        else:
            d = dict(item)

        trim_before = 1 if d.get("trim_first_frame") else 0
        dur_sec = float(d.get("duration_seconds", 5))
        target_dur = d.get("target_duration")

        playback_rate = 1.0
        if target_dur is not None and target_dur > 0:
            raw_dur = dur_sec - (trim_before / fps)
            if raw_dur > 0:
                ratio = raw_dur / target_dur
                if 0.65 <= ratio <= 1.45:
                    playback_rate = round(ratio, 3)

        effective_duration = float(target_dur) if target_dur is not None else dur_sec

        beat = {
            "id": d.get("clip_id", f"clip_{d.get('index', 0):03d}"),
            "index": int(d.get("index", 0)),
            "kind": "scene",
            "src": d.get("output_mp4_path", ""),
            "trim_before": trim_before,
            "playback_rate": playback_rate,
            "duration_seconds": effective_duration,
            "duration_frames": max(1, int(round(effective_duration * fps))),
            "target_duration": target_dur,
            "aspect": d.get("aspect", "16:9"),
            "motion_prompt": d.get("motion_prompt", ""),
            "mode": mode.value if isinstance(mode, ChainMode) else str(mode),
        }
        beats.append(beat)

    return beats
