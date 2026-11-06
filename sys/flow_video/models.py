"""Data models for Flow Video multi-account generation and stitching."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class ChainMode(str, Enum):
    DAISY_CHAIN = "daisy_chain"
    SCENE_PAIRS = "scene_pairs"
    ZERO_CREDIT_FLIPBOOK = "zero_credit_flipbook"


@dataclass
class KeyframeSpec:
    id: str
    image_path: str | None = None
    image_prompt: str | None = None
    motion_prompt: str = ""
    based_on: str | None = None
    target_duration: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> KeyframeSpec:
        target_dur = data.get("target_duration")
        if target_dur is None:
            target_dur = data.get("target_duration_sec")
        return cls(
            id=str(data["id"]),
            image_path=data.get("image_path"),
            image_prompt=data.get("image_prompt"),
            motion_prompt=str(data.get("motion_prompt", "")),
            based_on=data.get("based_on"),
            target_duration=float(target_dur) if target_dur is not None else None,
        )


@dataclass
class ScenePairSpec:
    id: str
    start_image_path: str | None = None
    end_image_path: str | None = None
    start_image_prompt: str | None = None
    end_image_prompt: str | None = None
    motion_prompt: str = ""
    target_duration: float | None = None
    trim_first_frame: bool = False
    start_based_on: str | None = None
    end_based_on_start: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScenePairSpec:
        target_dur = data.get("target_duration")
        if target_dur is None:
            target_dur = data.get("target_duration_sec")
        return cls(
            id=str(data["id"]),
            start_image_path=data.get("start_image_path"),
            end_image_path=data.get("end_image_path"),
            start_image_prompt=data.get("start_image_prompt"),
            end_image_prompt=data.get("end_image_prompt"),
            motion_prompt=str(data.get("motion_prompt", "")),
            target_duration=float(target_dur) if target_dur is not None else None,
            trim_first_frame=bool(data.get("trim_first_frame", False)),
            start_based_on=data.get("start_based_on"),
            end_based_on_start=bool(data.get("end_based_on_start", False)),
        )


@dataclass
class VideoClipTask:
    clip_id: str
    index: int
    start_frame_path: str
    end_frame_path: str | None = None
    motion_prompt: str = ""
    output_mp4_path: str = ""
    aspect: str = "16:9"
    video_model: str = "omni_flash"
    duration_seconds: int = 6
    target_duration: float | None = None
    trim_first_frame: bool = False
    seed: int | None = None
    status: str = "pending"  # "pending" | "running" | "completed" | "failed"
    profile_used: str | None = None
    error: str | None = None
    generation_seconds: float = 0.0
    credit_cost: int = 10

    @property
    def duration_sec(self) -> float:
        return float(self.duration_seconds)

    @duration_sec.setter
    def duration_sec(self, val: float) -> None:
        self.duration_seconds = int(round(val))

    @property
    def target_duration_sec(self) -> float | None:
        return self.target_duration

    @target_duration_sec.setter
    def target_duration_sec(self, val: float | None) -> None:
        self.target_duration = val

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["duration_sec"] = self.duration_sec
        d["target_duration_sec"] = self.target_duration_sec
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoClipTask:
        target_dur = data.get("target_duration")
        if target_dur is None:
            target_dur = data.get("target_duration_sec")
        seed_val = data.get("seed")
        dur_sec = data.get("duration_seconds")
        if dur_sec is None:
            dur_sec = data.get("duration_sec", 6)
        return cls(
            clip_id=str(data["clip_id"]),
            index=int(data["index"]),
            start_frame_path=str(data["start_frame_path"]),
            end_frame_path=data.get("end_frame_path"),
            motion_prompt=str(data.get("motion_prompt", "")),
            output_mp4_path=str(data.get("output_mp4_path", "")),
            aspect=str(data.get("aspect", "16:9")),
            video_model=str(data.get("video_model", "omni_flash")),
            duration_seconds=int(dur_sec),
            target_duration=float(target_dur) if target_dur is not None else None,
            trim_first_frame=bool(data.get("trim_first_frame", False)),
            seed=int(seed_val) if seed_val is not None else None,
            status=str(data.get("status", "pending")),
            profile_used=data.get("profile_used"),
            error=data.get("error"),
            generation_seconds=float(data.get("generation_seconds", 0.0)),
            credit_cost=int(data.get("credit_cost", 10)),
        )


def _natural_sort_key(path: Path) -> list[int | str]:
    """Human/natural sort key for files with embedded numbering."""
    parts = re.split(r"(\d+)", path.name)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


@dataclass
class VideoChainSpec:
    job_id: str = "flow_video_job"
    mode: ChainMode = ChainMode.DAISY_CHAIN
    aspect: str = "16:9"
    video_model: str = "omni_flash"
    duration_seconds: int = 6
    keyframes: list[KeyframeSpec] = field(default_factory=list)
    scene_pairs: list[ScenePairSpec] = field(default_factory=list)
    audio_path: str | None = None
    no_talking_prompt_guard: bool = True
    keep_veo_audio: bool = False
    veo_audio_mix_weight: float = 0.45
    target_fps: int = 30
    normalize_audio_lufs: bool = True
    auto_duration: bool = True
    auto_fallback_zero_credit: bool = True
    channel_id: str | None = None
    overscan_crop: float = 1.05

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "mode": self.mode.value if isinstance(self.mode, ChainMode) else str(self.mode),
            "aspect": self.aspect,
            "video_model": self.video_model,
            "duration_seconds": self.duration_seconds,
            "keyframes": [kf.to_dict() for kf in self.keyframes],
            "scene_pairs": [sp.to_dict() for sp in self.scene_pairs],
            "audio_path": self.audio_path,
            "no_talking_prompt_guard": self.no_talking_prompt_guard,
            "keep_veo_audio": self.keep_veo_audio,
            "veo_audio_mix_weight": self.veo_audio_mix_weight,
            "target_fps": self.target_fps,
            "normalize_audio_lufs": self.normalize_audio_lufs,
            "auto_duration": self.auto_duration,
            "auto_fallback_zero_credit": self.auto_fallback_zero_credit,
            "channel_id": self.channel_id,
            "overscan_crop": self.overscan_crop,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VideoChainSpec:
        raw_mode = data.get("mode", ChainMode.DAISY_CHAIN.value)
        try:
            mode = ChainMode(raw_mode)
        except ValueError:
            mode = ChainMode.DAISY_CHAIN

        keyframes = [KeyframeSpec.from_dict(k) for k in data.get("keyframes", [])]
        scene_pairs = [ScenePairSpec.from_dict(s) for s in data.get("scene_pairs", [])]

        return cls(
            job_id=str(data.get("job_id", "flow_video_job")),
            mode=mode,
            aspect=str(data.get("aspect", "16:9")),
            video_model=str(data.get("video_model", "omni_flash")),
            duration_seconds=int(data.get("duration_seconds", 6)),
            keyframes=keyframes,
            scene_pairs=scene_pairs,
            audio_path=data.get("audio_path"),
            no_talking_prompt_guard=bool(data.get("no_talking_prompt_guard", True)),
            keep_veo_audio=bool(data.get("keep_veo_audio", False)),
            veo_audio_mix_weight=float(data.get("veo_audio_mix_weight", 0.45)),
            target_fps=int(data.get("target_fps", 30)),
            normalize_audio_lufs=bool(data.get("normalize_audio_lufs", True)),
            auto_duration=bool(data.get("auto_duration", True)),
            auto_fallback_zero_credit=bool(data.get("auto_fallback_zero_credit", True)),
            channel_id=data.get("channel_id"),
            overscan_crop=float(data.get("overscan_crop", 1.05)),
        )

    def to_json_file(self, path: str | Path) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def from_json_file(cls, path: str | Path) -> VideoChainSpec:
        p = Path(path)
        with open(p, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @classmethod
    def from_directory(
        cls,
        dir_path: str | Path,
        motion_prompt: str = "",
        mode: ChainMode = ChainMode.DAISY_CHAIN,
        aspect: str = "16:9",
        video_model: str = "omni_flash",
        duration_seconds: int = 6,
        no_talking_prompt_guard: bool = True,
        audio_path: str | None = None,
        job_id: str | None = None,
        auto_duration: bool = True,
        auto_fallback_zero_credit: bool = True,
        channel_id: str | None = None,
        keep_veo_audio: bool = False,
        veo_audio_mix_weight: float = 0.45,
    ) -> VideoChainSpec:
        """Construct a VideoChainSpec from a directory of naturally sorted image files."""
        dir_p = Path(dir_path)
        if not dir_p.is_dir():
            raise FileNotFoundError(f"Frames directory not found: {dir_path}")

        valid_exts = {".png", ".jpg", ".jpeg", ".webp"}
        files = [
            f for f in dir_p.iterdir()
            if f.is_file() and f.suffix.lower() in valid_exts and not f.name.startswith(".")
        ]
        files.sort(key=_natural_sort_key)

        if len(files) < 2:
            raise ValueError(
                f"Directory {dir_path} must contain at least 2 image frames, found {len(files)}"
            )

        resolved_job_id = job_id or f"chain_{dir_p.name}"

        keyframes: list[KeyframeSpec] = []
        scene_pairs: list[ScenePairSpec] = []

        if mode in (ChainMode.DAISY_CHAIN, ChainMode.ZERO_CREDIT_FLIPBOOK):
            for idx, img_file in enumerate(files):
                stem = img_file.stem
                keyframes.append(
                    KeyframeSpec(
                        id=f"{idx:03d}_{stem}",
                        image_path=str(img_file.resolve()),
                        motion_prompt=motion_prompt,
                    )
                )
        else:
            # Pair consecutive frames (0->1, 1->2...) or (0->1, 2->3...)
            # For scene pairs from folder, consecutive pairs (i -> i+1) ensure all frames link
            for idx in range(len(files) - 1):
                start_f = files[idx]
                end_f = files[idx + 1]
                pair_id = f"pair_{idx:03d}_{start_f.stem}_to_{end_f.stem}"
                scene_pairs.append(
                    ScenePairSpec(
                        id=pair_id,
                        start_image_path=str(start_f.resolve()),
                        end_image_path=str(end_f.resolve()),
                        motion_prompt=motion_prompt,
                        target_duration=float(duration_seconds),
                    )
                )

        return cls(
            job_id=resolved_job_id,
            mode=mode,
            aspect=aspect,
            video_model=video_model,
            duration_seconds=duration_seconds,
            keyframes=keyframes,
            scene_pairs=scene_pairs,
            audio_path=audio_path,
            no_talking_prompt_guard=no_talking_prompt_guard,
            auto_duration=auto_duration,
            auto_fallback_zero_credit=auto_fallback_zero_credit,
            channel_id=channel_id,
            keep_veo_audio=keep_veo_audio,
            veo_audio_mix_weight=veo_audio_mix_weight,
        )


# Aliases
VideoClipSpec = VideoClipTask
FlowVideoChainSpec = VideoChainSpec

__all__ = [
    "ChainMode",
    "FlowVideoChainSpec",
    "KeyframeSpec",
    "ScenePairSpec",
    "VideoChainSpec",
    "VideoClipSpec",
    "VideoClipTask",
]
