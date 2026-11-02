"""Tests for Google First-Party Tools Engine."""

import unittest
from sys.flow_video.google_first_party_tools import (
    ShotExplorerEngine,
    StorySketchEngine,
    StyleWriterEngine,
    TitleOverlaysEngine,
    TransitionMachineEngine,
)


class TestGoogleFirstPartyTools(unittest.TestCase):
    def test_style_writer_engine_audit_prompt(self):
        items = [("shot1", "Lý Thường Kiệt on horse"), ("shot2", None)]
        prompt = StyleWriterEngine.build_audit_prompt(items)
        self.assertIn("IMAGE MANIFEST:", prompt)
        self.assertIn('Image 1: [annotated] "Lý Thường Kiệt on horse"', prompt)
        self.assertIn("Image 2: [no annotation]", prompt)
        self.assertIn("## Visual Style", prompt)
        self.assertIn("## Composition", prompt)
        self.assertIn("## Attitude", prompt)
        self.assertIn("## Colors", prompt)
        self.assertIn("## Lighting", prompt)
        self.assertIn("## Camera", prompt)

    def test_style_writer_engine_parsing(self):
        sample_md = """
## Visual Style
A cinematic historical **wuxia** epic combining photorealistic CGI with **armor** craftsmanship and **mythic** military scale.

## Composition
Low-angle heroic framing anchors dynamic equestrian portraits, transitioning to crossing **diagonals** in combat and **zenith** top-down **circular** geometry.

## Attitude
A fiercely **determined**, solemn, and **epic** aura radiating martial valor.

## Colors
A muted winter palette with **cyan** skies, pale snow, and **crimson** capes with **gold** highlights.

## Lighting
Soft **diffused** overcast daylight casting gentle cold ambient illumination with subtle **specular** glints and rim **highlights**.

## Camera
Expansive **anamorphic** widescreen cinematography with shallow depth of field and dramatic **perpendicular** angles.
"""
        dna = StyleWriterEngine.parse_style_summary(sample_md)
        self.assertIn("wuxia", dna.visual_style.keywords)
        self.assertIn("diagonals", dna.composition.keywords)
        self.assertIn("determined", dna.attitude.keywords)
        self.assertIn("cyan", dna.colors.keywords)
        self.assertIn("diffused", dna.lighting.keywords)
        self.assertIn("anamorphic", dna.camera.keywords)
        self.assertTrue(len(dna.all_keywords()) >= 15)
        self.assertTrue(len(dna.to_image_prompt_suffix()) > 50)

    def test_kieuhungdatviet_reference_dna(self):
        dna = StyleWriterEngine.get_kieuhungdatviet_reference_dna()
        self.assertEqual(len(dna.visual_style.keywords), 3)
        self.assertEqual(len(dna.composition.keywords), 3)
        self.assertEqual(len(dna.attitude.keywords), 3)
        self.assertEqual(len(dna.colors.keywords), 3)
        self.assertEqual(len(dna.lighting.keywords), 3)
        self.assertEqual(len(dna.camera.keywords), 3)

    def test_shot_explorer_engine_presets(self):
        self.assertIsNotNone(ShotExplorerEngine.get_preset("birds-eye"))
        self.assertIsNotNone(ShotExplorerEngine.get_preset("low-angle"))
        self.assertIsNotNone(ShotExplorerEngine.get_preset("zenith-top-down"))

        p = ShotExplorerEngine.build_camera_angle_prompt("birds-eye")
        self.assertTrue(p.startswith("A cinematic new camera angle of this scene: "))

        payload = ShotExplorerEngine.build_flow_image_payload("media_123", "zoom-out")
        self.assertEqual(payload["referenceImageMediaIds"], ["media_123"])
        self.assertEqual(payload["aspectRatio"], "16:9")
        self.assertIn("zoom out to a very wide shot", payload["prompt"])

        coverage = ShotExplorerEngine.plan_multi_angle_coverage("media_anchor_1")
        self.assertEqual(len(coverage), 6)

    def test_story_sketch_engine_prompts(self):
        # Anchor shot
        anchor_prompt = StorySketchEngine.build_shot_prompt(
            "Trần Hưng Đạo draws sword on flagship", None, "style: wuxia cinematic"
        )
        self.assertEqual(
            anchor_prompt,
            "Trần Hưng Đạo draws sword on flagship. style: wuxia cinematic",
        )

        # Chained shot
        chained_prompt = StorySketchEngine.build_shot_prompt(
            "Fleet charges into Bach Dang river", "media_anchor", "style: wuxia cinematic"
        )
        self.assertTrue(
            chained_prompt.startswith(
                "Generate an image showing what happens next based on this input: Fleet charges into Bach Dang river."
            )
        )

        chain_plan = StorySketchEngine.plan_sequence(
            ["Shot A", "Shot B", "Shot C"], global_instructions="cinematic epic"
        )
        self.assertEqual(len(chain_plan), 3)
        self.assertFalse(chain_plan[0]["is_chained"])
        self.assertTrue(chain_plan[1]["is_chained"])
        self.assertTrue(chain_plan[2]["is_chained"])

    def test_transition_machine_engine(self):
        end_a, start_b = TransitionMachineEngine.calculate_boundary_timestamps(10.0)
        self.assertAlmostEqual(end_a, 9.95)
        self.assertEqual(start_b, 0.0)

        payload = TransitionMachineEngine.build_veo_interpolation_payload(
            first_frame_media_id="frame_a_end",
            last_frame_media_id="frame_b_start",
            duration_seconds=8,
        )
        self.assertEqual(payload["firstFrameImageMediaId"], "frame_a_end")
        self.assertEqual(payload["lastFrameImageMediaId"], "frame_b_start")
        self.assertEqual(payload["modelDisplayName"], "Veo 3.1 - Lite")
        self.assertEqual(payload["durationSeconds"], 8)

    def test_title_overlays_engine(self):
        self.assertEqual(len(TitleOverlaysEngine.FONTS), 15)
        css = TitleOverlaysEngine.build_remotion_overlay_css(
            font_name="Google Sans", position="bottom_center", effect="typewriter"
        )
        self.assertIn("Google Sans", css["fontFamily"])
        self.assertEqual(css["left"], "50.0%")
        self.assertEqual(css["top"], "90.0%")
        self.assertEqual(css["animation_type"], "typewriter")


if __name__ == "__main__":
    unittest.main()
