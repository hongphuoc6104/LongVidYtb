"""Google First-Party Applets Source Code Codecs and Live Engines (vp-flow-video).

Reverse-engineered and faithfully implemented from Google Flow First-Party Applets:
1. `Style Writer` (UUID: `0c1b03b1-d77e-42ff-97fe-5efb35ac9aa7`):
   Google's official moodboard-to-style-prompt extractor using multimodal LLM synthesis
   across 6 visual pillars (Visual Style, Composition, Attitude, Colors, Lighting, Camera).
2. `Shot Explorer` (UUID: `83a78fea-bb55-4ddd-b5d3-43855fba4c6f`):
   Google's official camera angle & shot variation engine using reference media IDs
   and the canonical angle transformation prompt wrapper.
3. `Story Sketch` (UUID: `12350ecf-485f-4bc6-aef1-2518692508fb`):
   Google's official storyboard sequence generator chaining sequential prompts:
   `"Generate an image showing what happens next based on this input: {prompt}"`.
4. `Transition Machine` (UUID: `a867151e-7806-490c-b181-655c35af5bdb`):
   Google's official video boundary-frame extractor (end frame of clip A + first frame of clip B)
   and Veo start-end frame interpolation engine.
5. `Title Overlays` (UUID: `4c8ba875-f7db-4092-9e39-80ce2a4c4bd1`):
   Google's official kinetic & transition typography system with 15 Google Fonts
   and 9 standard placement anchors.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

# ===========================================================================
# 1. STYLE WRITER ENGINE (0c1b03b1-d77e-42ff-97fe-5efb35ac9aa7)
# ===========================================================================

@dataclass
class StyleSection:
    """A single pillar in the Google Style Writer 6-pillar summary."""
    name: str
    body: str
    keywords: list[str] = field(default_factory=list)


@dataclass
class StyleDNA:
    """The 6-pillar Style DNA synthesized from visual references."""
    visual_style: StyleSection
    composition: StyleSection
    attitude: StyleSection
    colors: StyleSection
    lighting: StyleSection
    camera: StyleSection
    raw_markdown: str = ""

    def all_keywords(self) -> list[str]:
        """Aggregate all extracted keywords across the 6 pillars."""
        kws: list[str] = []
        for sec in [
            self.visual_style,
            self.composition,
            self.attitude,
            self.colors,
            self.lighting,
            self.camera,
        ]:
            kws.extend(sec.keywords)
        return kws

    def to_image_prompt_suffix(self) -> str:
        """Distill the 6 pillars into a compact, high-signal prompt suffix.

        Designed specifically for Nano Banana Pro / Nano Banana 2 image models.
        """
        parts: list[str] = []
        if self.visual_style.body:
            parts.append(self.visual_style.body)
        if self.colors.body:
            parts.append(f"Palette: {self.colors.body}")
        if self.lighting.body:
            parts.append(f"Lighting: {self.lighting.body}")
        if self.camera.body:
            parts.append(f"Cinematography: {self.camera.body}")
        return " | ".join(parts)

    def to_dict(self) -> dict[str, Any]:
        return {
            "visual_style": asdict(self.visual_style),
            "composition": asdict(self.composition),
            "attitude": asdict(self.attitude),
            "colors": asdict(self.colors),
            "lighting": asdict(self.lighting),
            "camera": asdict(self.camera),
            "all_keywords": self.all_keywords(),
            "prompt_suffix": self.to_image_prompt_suffix(),
            "raw_markdown": self.raw_markdown,
        }


class StyleWriterEngine:
    """Google's exact Style Writer multimodal prompt generator & parser."""

    PILLARS = [
        "Visual Style",
        "Composition",
        "Attitude",
        "Colors",
        "Lighting",
        "Camera",
    ]

    @staticmethod
    def build_audit_prompt(manifest_items: list[tuple[str, Optional[str]]]) -> str:
        """Build Google's exact Style Writer user prompt.

        Args:
            manifest_items: List of (label/id, optional_note) tuples.
        """
        manifest_lines: list[str] = []
        for idx, (_, note) in enumerate(manifest_items, start=1):
            lbl = f"Image {idx}"
            if note and note.strip():
                manifest_lines.append(f'{lbl}: [annotated] "{note.strip()}"')
            else:
                manifest_lines.append(f"{lbl}: [no annotation]")

        manifest_str = "\n".join(manifest_lines)
        return (
            f"Analyze the following {len(manifest_items)} images and produce a Style Summary.\n\n"
            f"IMAGE MANIFEST:\n{manifest_str}\n\n"
            "OUTPUT FORMAT — Return ONLY this markdown structure, nothing else:\n\n"
            "## Visual Style\n"
            "[1-2 sentences describing the overall aesthetic, genre, and visual identity. Bold 3 keywords.]\n\n"
            "## Composition\n"
            "[1-2 sentences on framing, layout, subject placement, and spatial relationships. Bold 3 keywords.]\n\n"
            "## Attitude\n"
            "[1-2 sentences on mood, emotion, tone, and energy conveyed. Bold 3 keywords.]\n\n"
            "## Colors\n"
            "[1-2 sentences on dominant palette, color harmony, saturation, and contrast. Bold 3 keywords.]\n\n"
            "## Lighting\n"
            "[1-2 sentences on light quality, direction, shadow behavior, and temperature. Bold 3 keywords.]\n\n"
            "## Camera\n"
            "[1-2 sentences on lens perspective, depth of field, distance, and angle. Bold 3 keywords.]\n\n"
            "FORMATTING RULES:\n"
            "- Bold exactly 3 single-word keywords per section using **keyword** syntax.\n"
            "- Keywords must be the most visually defining descriptors (colors, moods, techniques).\n"
            "- Never bold phrases — only individual words.\n"
            "- Most of each sentence must remain unbolded."
        )

    @staticmethod
    def build_system_instruction(image_count: int) -> str:
        """Build Google's exact Style Writer system instruction."""
        return (
            "You are a visual design analyst. Your job is to synthesize a cohesive Style Summary from a set of images.\n\n"
            "INPUTS:\n"
            f"- {image_count} images, numbered Image 1 through Image {image_count}.\n"
            "- Each image may have a user annotation (marked [annotated]) or none (marked [no annotation]).\n\n"
            "BEHAVIOR:\n"
            "- Be extremely literal and specific about what you observe — avoid generic or vague language.\n"
            "- Synthesize patterns across ALL images into a unified creative direction, not per-image descriptions.\n"
            "- When annotations exist, treat them as high-signal creative intent and weight them heavily in the relevant section.\n"
            "- Write in a confident, editorial tone appropriate for a creative brief."
        )

    @classmethod
    def parse_style_summary(cls, markdown_text: str) -> StyleDNA:
        """Parse the generated markdown into a structured StyleDNA object."""
        sections: dict[str, StyleSection] = {}

        for pillar in cls.PILLARS:
            pattern = rf"##\s+{re.escape(pillar)}\s*\n(.*?)(?=\n##|\Z)"
            match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
            if match:
                raw_body = match.group(1).strip()
                # Extract bolded keywords (**keyword**)
                keywords = re.findall(r"\*\*([^*]+)\*\*", raw_body)
                # Clean up body text for prompt use
                clean_body = re.sub(r"\*\*([^*]+)\*\*", r"\1", raw_body).strip()
                sections[pillar] = StyleSection(
                    name=pillar,
                    body=clean_body,
                    keywords=[k.strip() for k in keywords if k.strip()],
                )
            else:
                sections[pillar] = StyleSection(name=pillar, body="", keywords=[])

        return StyleDNA(
            visual_style=sections["Visual Style"],
            composition=sections["Composition"],
            attitude=sections["Attitude"],
            colors=sections["Colors"],
            lighting=sections["Lighting"],
            camera=sections["Camera"],
            raw_markdown=markdown_text,
        )

    @classmethod
    def get_channel_style_dna(cls, channel_id: str = "nao_luoi") -> StyleDNA:
        """Dynamically synthesize 6-pillar StyleDNA for any of the 20 Vietnamese channels in registry."""
        try:
            from sys.channels.registry import get_channel

            ch = get_channel(channel_id.strip().replace("ch_", "").replace("-", "_"))
            vis = ch.visual
            palette_str = ", ".join(getattr(vis, "palette", ["#F8F0DC", "#3B82C4"]))
            md = (
                "## Visual Style\n"
                f"A **distinctive** **{vis.profile_id}** illustration style: {vis.style_description} with **clean** 2D linework.\n\n"
                "## Composition\n"
                f"Focused **editorial** framing featuring **{vis.cast_appearance[:24].split()[0]}** subjects and **clear** negative space.\n\n"
                "## Attitude\n"
                f"An **engaging**, **insightful**, and **constructive** tone tailored for channel {ch.display_name}.\n\n"
                "## Colors\n"
                f"Harmonious **channel-locked** **palette** ({palette_str}) with **balanced** contrast.\n\n"
                "## Lighting\n"
                "Clean **2D** **flat** or atmospheric **editorial** illumination with zero unintended 3D clutter.\n\n"
                "## Camera\n"
                "Smooth **2D** **planar** composition with **purposeful** focal transitions between keyframes."
            )
            return cls.parse_style_summary(md)
        except Exception:
            return cls.get_doodle_explainer_reference_dna()

    @classmethod
    def get_doodle_explainer_reference_dna(cls) -> StyleDNA:
        """Pre-extracted Google Style Writer DNA for Video Pilot 2D Doodle Explainer (1.7.0)."""
        md = (
            "## Visual Style\n"
            "A **hand-drawn** 2D **doodle** explainer illustration using wobbly black marker lines and **flat** vector fills.\n\n"
            "## Composition\n"
            "Minimalist **Feynman** framing with one **bald** stickman and one focal **metaphor** surrounded by 60% negative space.\n\n"
            "## Attitude\n"
            "An **inquisitive**, **clear**, and **relatable** educational tone that simplifies complex concepts.\n\n"
            "## Colors\n"
            "Warm **cream** paper canvas (#F8F0DC) paired with **cobalt** blue shirt (#3B82C4) and muted **sage** accents (#93A88C).\n\n"
            "## Lighting\n"
            "Uniform **shadowless** 2D **matte** illumination with **zero** gradients, 3D shading, or vignettes.\n\n"
            "## Camera\n"
            "Strict **orthographic** **2D** front-on whiteboard **planarity** without perspective distortion or isometric walls."
        )
        return cls.parse_style_summary(md)

    @classmethod
    def get_kieuhungdatviet_reference_dna(cls) -> StyleDNA:
        """Pre-extracted Google Style Writer DNA for the Kiêu Hùng Đất Việt reference suite.

        Synthesized from shots 1 to 4 (Lý Thường Kiệt horseback, Tông Đản battleline,
        horseback combat clash, and zenith circular snow tracks).
        """
        md = (
            "## Visual Style\n"
            "A cinematic historical **wuxia** epic combining photorealistic CGI character rendering with "
            "traditional East Asian period **armor** craftsmanship and grand **mythic** military scale.\n\n"
            "## Composition\n"
            "Low-angle heroic framing anchors dynamic equestrian portraits, transitioning to high-tension "
            "crossing **diagonals** in combat and a striking **zenith** top-down **circular** geometry on snow.\n\n"
            "## Attitude\n"
            "A fiercely **determined**, **solemn**, and **epic** aura radiating martial valor and national historical gravity.\n\n"
            "## Colors\n"
            "A muted winter palette dominated by frosty **cyan** overcast skies and pale snow, punctuated by regal "
            "**crimson** capes and weathered **gold** metallic highlights.\n\n"
            "## Lighting\n"
            "Soft **diffused** overcast daylight casting gentle cold ambient illumination with subtle **specular** "
            "glints off steel blades and warm rim **highlights** on armor plates.\n\n"
            "## Camera\n"
            "Expansive **anamorphic** **widescreen** cinematography featuring shallow depth of field for character "
            "close-ups and dramatic **perpendicular** angles for battlefield choreography."
        )
        return cls.parse_style_summary(md)


# ===========================================================================
# 2. SHOT EXPLORER ENGINE (83a78fea-bb55-4ddd-b5d3-43855fba4c6f)
# ===========================================================================

@dataclass
class CameraPreset:
    id: str
    label: str
    emoji: str
    category: str
    default_prompt: str


class ShotExplorerEngine:
    """Google's exact Shot Explorer camera angle variation system."""

    # Google's exact PRESET_ANGLES from shot_explorer_app.js:
    PRESETS: list[CameraPreset] = [
        # Perspective
        CameraPreset(
            id="birds-eye",
            label="overhead",
            emoji="🦅",
            category="perspective",
            default_prompt="give me an overhead aerial view. zoom out so you can see the entire scene, looking straight down on it, far away.",
        ),
        CameraPreset(
            id="side-view",
            label="side",
            emoji="📐",
            category="perspective",
            default_prompt="Side profile view of the subject",
        ),
        CameraPreset(
            id="back-view",
            label="back",
            emoji="👤",
            category="perspective",
            default_prompt="rotate the camera to show me the back of the main subject entity in this image. I want an entirely new perspective on the scene.",
        ),
        # Pan
        CameraPreset(
            id="pan-left",
            label="left",
            emoji="⬅️",
            category="pan",
            default_prompt="pan to the left to reveal new details of the scene",
        ),
        CameraPreset(
            id="pan-right",
            label="right",
            emoji="➡️",
            category="pan",
            default_prompt="pan to the right to reveal new details of the scene",
        ),
        CameraPreset(
            id="pan-up",
            label="up",
            emoji="⬆️",
            category="pan",
            default_prompt="pan up to reveal new details of the scene",
        ),
        CameraPreset(
            id="pan-down",
            label="down",
            emoji="⬇️",
            category="pan",
            default_prompt="pan down to reveal new details of the scene",
        ),
        # Zoom
        CameraPreset(
            id="zoom-in",
            label="zoom in",
            emoji="🔍",
            category="zoom",
            default_prompt="Zoom in closer to the main subject/area of this image, macrophotography detail.",
        ),
        CameraPreset(
            id="zoom-out",
            label="zoom out",
            emoji="🔭",
            category="zoom",
            default_prompt="zoom out to a very wide shot so I can see much more of surrounding environment.",
        ),
        CameraPreset(
            id="extreme-detail",
            label="extreme detail",
            emoji="👁️",
            category="zoom",
            default_prompt="give me an ultra close-up shot. zoom in extremely close to a specific detail of the main subject of this image, revealing incredible detail and texture, macrophotography.",
        ),
        CameraPreset(
            id="surprise-me",
            label="surprise me",
            emoji="🎲",
            category="zoom",
            default_prompt="Pick any specific detail of this image and zoom in extremely close up to it, revealing its textures and details, macrophotography. Don't just pick the main subject/area, surprise me by choosing some other detail I may not notice.",
        ),
        # Extended Cinematic Angles (for Video Pilot Historical Direction)
        CameraPreset(
            id="low-angle",
            label="low angle heroic",
            emoji="⚔️",
            category="perspective",
            default_prompt="low-angle shot looking up at the subject from ground level, dramatic towering heroic perspective, epic military grandeur.",
        ),
        CameraPreset(
            id="over-the-shoulder",
            label="over the shoulder",
            emoji="🛡️",
            category="perspective",
            default_prompt="over-the-shoulder shot looking past the subject foreground silhouette towards the opposing adversary and battlefield ahead.",
        ),
        CameraPreset(
            id="zenith-top-down",
            label="zenith perpendicular",
            emoji="⭕",
            category="perspective",
            default_prompt="perpendicular 90-degree zenith top-down shot looking straight down onto the ground, revealing geometric circular motion patterns and tracks.",
        ),
    ]

    PRESET_MAP: dict[str, CameraPreset] = {p.id: p for p in PRESETS}

    @classmethod
    def get_preset(cls, preset_id: str) -> Optional[CameraPreset]:
        return cls.PRESET_MAP.get(preset_id)

    @classmethod
    def build_camera_angle_prompt(cls, prompt_or_preset_id: str) -> str:
        """Wrap prompt in Google's exact Shot Explorer transformation template.

        Template: `f"A cinematic new camera angle of this scene: {prompt}"`
        """
        preset = cls.PRESET_MAP.get(prompt_or_preset_id)
        inner_prompt = preset.default_prompt if preset else prompt_or_preset_id
        return f"A cinematic new camera angle of this scene: {inner_prompt}"

    @classmethod
    def build_flow_image_payload(
        cls,
        reference_media_id: str,
        prompt_or_preset_id: str,
        model_display_name: str = "Nano Banana Pro",
        aspect_ratio: str = "16:9",
    ) -> dict[str, Any]:
        """Build the exact payload passed to `Flow.generate.image` by Shot Explorer."""
        final_prompt = cls.build_camera_angle_prompt(prompt_or_preset_id)
        return {
            "prompt": final_prompt,
            "referenceImageMediaIds": [reference_media_id],
            "aspectRatio": aspect_ratio,
            "modelDisplayName": model_display_name,
        }

    @classmethod
    def plan_multi_angle_coverage(
        cls, anchor_media_id: str, scene_title: str = "Scene"
    ) -> list[dict[str, Any]]:
        """Plan a complete 6-angle cinematic coverage suite from a single anchor image.

        Generates:
        1. Wide establishing (zoom-out)
        2. Heroic low-angle
        3. Medium side profile
        4. Over-the-shoulder combat focus
        5. Extreme detail / close-up
        6. Zenith top-down overview
        """
        angle_ids = [
            "zoom-out",
            "low-angle",
            "side-view",
            "over-the-shoulder",
            "extreme-detail",
            "zenith-top-down",
        ]
        plan: list[dict[str, Any]] = []
        for aid in angle_ids:
            preset = cls.PRESET_MAP[aid]
            plan.append({
                "scene": scene_title,
                "angle_id": preset.id,
                "label": f"{preset.emoji} {preset.label}",
                "category": preset.category,
                "payload": cls.build_flow_image_payload(anchor_media_id, aid),
            })
        return plan


# ===========================================================================
# 3. STORY SKETCH ENGINE (12350ecf-485f-4bc6-aef1-2518692508fb)
# ===========================================================================

@dataclass
class StoryboardShot:
    id: str
    prompt: str
    parent_media_id: Optional[str] = None
    media_id: Optional[str] = None
    image_url: Optional[str] = None
    base64: Optional[str] = None


class StorySketchEngine:
    """Google's exact Story Sketch storyboard sequence chaining engine."""

    DEFAULT_MODEL = "Nano Banana 2"

    @staticmethod
    def build_shot_prompt(
        prompt: str,
        parent_media_id: Optional[str] = None,
        global_instructions: str = "",
    ) -> str:
        """Build Google's exact Story Sketch chained prompt.

        Algorithm:
        If parent_media_id exists:
            `base = f"Generate an image showing what happens next based on this input: {prompt}"`
        Else:
            `base = prompt`
        `final = f"{base}. {global_instructions}".strip()`
        """
        clean_prompt = prompt.strip()
        if parent_media_id:
            base = f"Generate an image showing what happens next based on this input: {clean_prompt}"
        else:
            base = clean_prompt

        clean_instructions = global_instructions.strip()
        if clean_instructions:
            return f"{base}. {clean_instructions}".strip()
        return base

    @classmethod
    def build_flow_image_payload(
        cls,
        prompt: str,
        parent_media_id: Optional[str] = None,
        global_instructions: str = "",
        model_display_name: str = DEFAULT_MODEL,
        aspect_ratio: str = "16:9",
    ) -> dict[str, Any]:
        """Build exact payload passed to `Flow.generate.image` by Story Sketch."""
        final_prompt = cls.build_shot_prompt(prompt, parent_media_id, global_instructions)
        payload: dict[str, Any] = {
            "prompt": final_prompt,
            "aspectRatio": aspect_ratio,
            "modelDisplayName": model_display_name,
        }
        if parent_media_id:
            payload["referenceImageMediaIds"] = [parent_media_id]
        return payload

    @classmethod
    def plan_sequence(
        cls,
        shot_prompts: list[str],
        global_instructions: str = "",
        model_display_name: str = DEFAULT_MODEL,
    ) -> list[dict[str, Any]]:
        """Plan a sequence of chained shots respecting parent-child continuity."""
        chain: list[dict[str, Any]] = []
        for idx, p in enumerate(shot_prompts):
            is_follow_up = idx > 0
            chain.append({
                "shot_index": idx + 1,
                "is_chained": is_follow_up,
                "prompt_template": cls.build_shot_prompt(
                    p,
                    parent_media_id=f"<PARENT_MEDIA_ID_OF_SHOT_{idx}>" if is_follow_up else None,
                    global_instructions=global_instructions,
                ),
                "model": model_display_name,
            })
        return chain


# ===========================================================================
# 4. TRANSITION MACHINE ENGINE (a867151e-7806-490c-b181-655c35af5bdb)
# ===========================================================================

class TransitionMachineEngine:
    """Google's exact Transition Machine boundary frame extraction & Veo interpolation engine."""

    DEFAULT_VEO_MODEL = "Veo 3.1 - Lite"
    SUPPORTED_DURATIONS = [4, 6, 8]
    DEFAULT_DURATION = 8

    # WebCodecs / MP4 Stitching specification from constants.ts
    STITCH_FPS = 30
    STITCH_BITRATE = 20_000_000  # 20 Mbps
    STITCH_MIME_PREFERENCES = [
        "video/mp4; codecs=avc1.640028",  # H.264 High Profile — Premiere native
        "video/mp4; codecs=avc1.42E01E",  # H.264 Baseline — broad compat
        "video/mp4",
        "video/webm; codecs=vp9",
        "video/webm; codecs=vp8",
    ]

    @staticmethod
    def calculate_boundary_timestamps(
        video_a_duration_sec: float,
    ) -> tuple[float, float]:
        """Calculate the exact boundary frame timestamps required by Google's Transition Machine.

        Algorithm from `virtual:utils/video.ts`:
        - Clip A End Frame: `Math.max(0, duration - 0.05)`
        - Clip B Start Frame: `0.0`
        """
        end_time_a = max(0.0, video_a_duration_sec - 0.05) if video_a_duration_sec > 0 else 0.0
        start_time_b = 0.0
        return end_time_a, start_time_b

    @classmethod
    def build_veo_interpolation_payload(
        cls,
        first_frame_media_id: str,
        last_frame_media_id: str,
        duration_seconds: int = DEFAULT_DURATION,
        prompt: Optional[str] = None,
        model_display_name: str = DEFAULT_VEO_MODEL,
        aspect_ratio: str = "16:9",
    ) -> dict[str, Any]:
        """Build exact payload passed to `Flow.generate.video` for boundary interpolation."""
        if duration_seconds not in cls.SUPPORTED_DURATIONS:
            duration_seconds = cls.DEFAULT_DURATION

        payload: dict[str, Any] = {
            "firstFrameImageMediaId": first_frame_media_id,
            "lastFrameImageMediaId": last_frame_media_id,
            "modelDisplayName": model_display_name,
            "durationSeconds": duration_seconds,
            "aspectRatio": aspect_ratio,
        }
        if prompt and prompt.strip():
            payload["prompt"] = prompt.strip()
        return payload

    @classmethod
    def get_ffmpeg_stitching_command(
        cls,
        clip_a_path: Path | str,
        transition_clip_path: Path | str,
        clip_b_path: Path | str,
        output_path: Path | str,
    ) -> list[str]:
        """Generate ffmpeg command conforming to Google's H.264 High Profile 30fps 20M bitrate."""
        return [
            "ffmpeg",
            "-y",
            "-i",
            str(clip_a_path),
            "-i",
            str(transition_clip_path),
            "-i",
            str(clip_b_path),
            "-filter_complex",
            "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[v][a]",
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-profile:v",
            "high",
            "-r",
            str(cls.STITCH_FPS),
            "-b:v",
            f"{cls.STITCH_BITRATE}",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            str(output_path),
        ]


# ===========================================================================
# 5. TITLE OVERLAYS ENGINE (4c8ba875-f7db-4092-9e39-80ce2a4c4bd1)
# ===========================================================================

@dataclass
class FontPreset:
    name: str
    family: str
    google_spec: str
    weights: list[int]


@dataclass
class PositionPreset:
    name: str
    x_pct: float
    y_pct: float


class TitleOverlaysEngine:
    """Google's exact Title Overlays typography, animation & positioning engine."""

    # Google's 15 official typography presets from virtual:src/types.ts
    FONTS: list[FontPreset] = [
        FontPreset("Instrument Sans", "'Instrument Sans', sans-serif", "Instrument+Sans:wght@400;500;600;700", [400, 500, 600, 700]),
        FontPreset("Google Sans", "'Google Sans', sans-serif", "Google+Sans:wght@400;500;700", [400, 500, 700]),
        FontPreset("Stack Sans", "'Stack Sans Notch', sans-serif", "Stack+Sans+Notch:wght@200;300;400;500;600;700", [200, 300, 400, 500, 600, 700]),
        FontPreset("Instrument Serif", "'Instrument Serif', serif", "Instrument+Serif:ital@0;1", [400]),
        FontPreset("Baskervville", "'Baskervville', serif", "Baskervville:wght@400;500;600;700", [400, 500, 600, 700]),
        FontPreset("Space Mono", "'Space Mono', monospace", "Space+Mono:ital,wght@0,400;0,700;1,400;1,700", [400, 700]),
        FontPreset("Michroma", "'Michroma', sans-serif", "Michroma", [400]),
        FontPreset("Sofia Sans", "'Sofia Sans', sans-serif", "Sofia+Sans:wght@400;500;600;700", [400, 500, 600, 700]),
        FontPreset("Faculty Glyphic", "'Faculty Glyphic', sans-serif", "Faculty+Glyphic", [400]),
        FontPreset("Tasa Orbiter", "'Tasa Orbiter', sans-serif", "Tasa+Orbiter:wght@400;700", [400, 700]),
        FontPreset("Ballet", "'Ballet', cursive", "Ballet", [400]),
        FontPreset("Danfo", "'Danfo', serif", "Danfo", [400]),
        FontPreset("Pirata One", "'Pirata One', system-ui", "Pirata+One", [400]),
        FontPreset("Astloch", "'Astloch', display", "Astloch:wght@400;700", [400, 700]),
        FontPreset("Bitcount Grid", "'Bitcount Grid Double', monospace", "Bitcount+Grid+Double", [400]),
    ]

    # Google's animation effect categories
    KINETIC_EFFECTS = {"wave", "wiggle", "font-shuffle"}
    TRANSITION_EFFECTS = {"blur-in", "typewriter", "slide-up", "slide-fade"}
    SEQUENTIAL_EFFECTS = {"sequential-stack"}

    # Google's 9 position presets
    POSITIONS: dict[str, PositionPreset] = {
        "top_left": PositionPreset("Top Left", 10.0, 10.0),
        "top_center": PositionPreset("Top Center", 50.0, 10.0),
        "top_right": PositionPreset("Top Right", 90.0, 10.0),
        "center_left": PositionPreset("Center Left", 10.0, 50.0),
        "center": PositionPreset("Center", 50.0, 50.0),
        "center_right": PositionPreset("Center Right", 90.0, 50.0),
        "bottom_left": PositionPreset("Bottom Left", 10.0, 90.0),
        "bottom_center": PositionPreset("Bottom Center", 50.0, 90.0),
        "bottom_right": PositionPreset("Bottom Right", 90.0, 90.0),
    }

    @classmethod
    def get_google_fonts_url(cls) -> str:
        """Construct the official Google Fonts stylesheet URL for all applet fonts."""
        families = "&".join(f"family={f.google_spec}" for f in cls.FONTS)
        return f"https://fonts.googleapis.com/css2?{families}&display=swap"

    @classmethod
    def build_remotion_overlay_css(
        cls,
        font_name: str = "Google Sans",
        position: str = "bottom_center",
        effect: str = "slide-up",
    ) -> dict[str, Any]:
        """Convert Google Type Overlays preset into Remotion / CSS component styles."""
        font_spec = next((f for f in cls.FONTS if f.name == font_name), cls.FONTS[1])
        pos_spec = cls.POSITIONS.get(position, cls.POSITIONS["bottom_center"])

        return {
            "fontFamily": font_spec.family,
            "left": f"{pos_spec.x_pct}%",
            "top": f"{pos_spec.y_pct}%",
            "transform": "translate(-50%, -50%)",
            "position": "absolute",
            "animation_type": effect,
            "google_fonts_url": cls.get_google_fonts_url(),
        }
