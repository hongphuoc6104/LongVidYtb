"""Unit tests for Google Flow Applet Manager & VP Omni Studio V2 (sys/flow_cdp/applet_manager.py)."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from sys.flow_cdp.applet_manager import (
    KIND_COMMUNITY,
    KIND_GOOGLE,
    KIND_USER,
    OMNI_STUDIO_STORAGE_KEY,
    RPC_APPLET_STATE,
    RPC_DELETE_APPLET,
    RPC_FORK_APPLET,
    RPC_LIST_APPLETS,
    RPC_PIN_APPLET,
    build_delete_applet_request,
    build_fork_applet_request,
    build_get_applet_state_request,
    build_list_applets_request,
    build_pin_applet_request,
    build_set_applet_state_request,
    build_vp_omni_studio_v2_state,
    generate_vp_omni_studio_v2_tsx,
    parse_applets_list,
    resolve_omni_flash_duration,
)
from sys.tools.manage_flow_applets import cmd_build_state_json, cmd_export_v2_tsx


class TestFlowAppletRpcAndManager(unittest.TestCase):
    def setUp(self):
        # Sample mock items matching Google Flow's Protobuf schema for tRARke
        self.mock_user_item = [
            "61216e15-0348-49f7-9fbb-29e96b373718",  # [0] applet_id
            11529157989,                            # [1] owner_user_id
            "Remix of VP Stickman Lab",             # [2] name
            "Personal doodle workbench",            # [3] description
            None,                                   # [4]
            "4ef2340a-cd86-4fa3-92b5-c2963cb303f3", # [5] share_id
            None,                                   # [6]
            [1790996311, 764474000],                # [7] created_at
            [1790996311, 764474000],                # [8] updated_at
            None,                                   # [9]
            None,                                   # [10]
            "applets/61216e15-0348-49f7-9fbb-29e96b373718",  # [11] resource_path
            1,                                      # [12] kind (1 = USER)
            None,                                   # [13] pinned_at
            None,                                   # [14]
            "https://gstatic.com/ada-1.png",        # [15] icon_url
            None,                                   # [16]
            None,                                   # [17] author_display
            True,                                   # [18] is_public
            None,                                   # [19]
            0,                                      # [20] run_count
            None,                                   # [21]
            None,                                   # [22] categories
        ]

        self.mock_google_item = [
            "a867151e-7806-490c-b181-655c35af5bdb",
            -1,
            "Transition Machine",
            "Generate seamless transitions between your videos",
            None,
            "ab0cf718-f2ba-47e1-81ba-dc43424a139a",
            None,
            [1778605806, 824245000],
            [1793516727, 8296000],
            None,
            None,
            "applets/a867151e-7806-490c-b181-655c35af5bdb",
            2,  # kind (2 = GOOGLE)
            1793516727,  # pinned
            None,
            "https://gstatic.com/ada-16.png",
            None,
            "Scotch Johnson, Google",
            True,
            None,
            1973,
            None,
            ["Video"],
        ]

        self.mock_community_item = [
            "community-417e7481-f38b-4b4d-a8f6-076fdafbb9c9",
            -1,
            "ThumbnailForge",
            "Create photorealistic thumbnails in seconds",
            None,
            "85140513-488a-419c-b063-83c76a22c9cb",
            None,
            [1778605806, 824245000],
            [1793516727, 8296000],
            None,
            None,
            "applets/community-417e7481-f38b-4b4d-a8f6-076fdafbb9c9",
            3,  # kind (3 = COMMUNITY)
            None,
            None,
            "https://gstatic.com/ada-20.png",
            None,
            "Jay Pirabakaran",
            True,
            None,
            896,
            None,
            ["Spotlight"],
        ]

    def test_list_applets_parsing_kinds_and_fields(self):
        """Verify parse_applets_list correctly maps USER, GOOGLE, COMMUNITY kinds and fields."""
        raw_payload = [[self.mock_user_item, self.mock_google_item, self.mock_community_item]]
        applets = parse_applets_list(raw_payload)

        self.assertEqual(len(applets), 3)

        # 1. USER kind
        user = applets[0]
        self.assertEqual(user["applet_id"], "61216e15-0348-49f7-9fbb-29e96b373718")
        self.assertEqual(user["name"], "Remix of VP Stickman Lab")
        self.assertEqual(user["kind"], KIND_USER)
        self.assertEqual(user["share_id"], "4ef2340a-cd86-4fa3-92b5-c2963cb303f3")
        self.assertFalse(user["is_pinned"])

        # 2. GOOGLE kind
        google = applets[1]
        self.assertEqual(google["applet_id"], "a867151e-7806-490c-b181-655c35af5bdb")
        self.assertEqual(google["name"], "Transition Machine")
        self.assertEqual(google["kind"], KIND_GOOGLE)
        self.assertEqual(google["author"], "Scotch Johnson, Google")
        self.assertEqual(google["run_count"], 1973)
        self.assertEqual(google["categories"], ["Video"])
        self.assertTrue(google["is_pinned"])

        # 3. COMMUNITY kind
        comm = applets[2]
        self.assertEqual(comm["applet_id"], "community-417e7481-f38b-4b4d-a8f6-076fdafbb9c9")
        self.assertEqual(comm["name"], "ThumbnailForge")
        self.assertEqual(comm["kind"], KIND_COMMUNITY)
        self.assertEqual(comm["author"], "Jay Pirabakaran")
        self.assertEqual(comm["run_count"], 896)
        self.assertEqual(comm["categories"], ["Spotlight"])

    def test_list_applets_parsing_batchexecute_text_envelope(self):
        """Verify parse_applets_list unwraps standard Google batchexecute text envelope."""
        inner_json = json.dumps([[self.mock_user_item, self.mock_google_item]])
        chunk = [["wrb.fr", RPC_LIST_APPLETS, inner_json, None, None, None, "generic"]]
        chunk_str = json.dumps(chunk)
        raw_envelope_text = f")]}}'\n\n{len(chunk_str)}\n{chunk_str}\n"

        applets = parse_applets_list(raw_envelope_text)
        self.assertGreaterEqual(len(applets), 2)
        self.assertEqual(applets[0]["kind"], KIND_USER)
        self.assertEqual(applets[1]["kind"], KIND_GOOGLE)

    def test_list_applets_parsing_empty_and_graceful_fallbacks(self):
        """Verify parsing empty, invalid, or partial data gracefully returns empty list."""
        self.assertEqual(parse_applets_list(""), [])
        self.assertEqual(parse_applets_list("[]"), [])
        self.assertEqual(parse_applets_list(None), [])
        self.assertEqual(parse_applets_list([[]]), [])

    def test_rpc_envelope_construction(self):
        """Verify CSvxid, MVz44c, TsaPHc, ZLaYcd RPC envelope construction."""
        # 1. tRARke
        list_req = build_list_applets_request()
        self.assertIn(RPC_LIST_APPLETS, list_req)
        self.assertIn('"[]"', list_req)

        # 2. CSvxid (Fork)
        fork_req = build_fork_applet_request("test-share-123")
        self.assertIn(RPC_FORK_APPLET, fork_req)
        self.assertIn("test-share-123", fork_req)

        fork_with_proj = build_fork_applet_request("test-share-123", project_id="proj-456")
        self.assertIn(RPC_FORK_APPLET, fork_with_proj)
        self.assertIn("proj-456", fork_with_proj)

        # 3. MVz44c (Get State & Set State)
        get_state_req = build_get_applet_state_request("proj-abc", "applet-xyz")
        self.assertIn(RPC_APPLET_STATE, get_state_req)
        self.assertIn("proj-abc", get_state_req)
        self.assertIn("applet-xyz", get_state_req)

        sample_state = {"mode": "hybrid_video", "counter": 42}
        set_state_req = build_set_applet_state_request("proj-abc", "applet-xyz", sample_state)
        self.assertIn(RPC_APPLET_STATE, set_state_req)
        self.assertIn("proj-abc", set_state_req)
        self.assertIn("hybrid_video", set_state_req)

        # 4. TsaPHc (Pin / Unpin)
        pin_req = build_pin_applet_request("applet-123", pinned=True)
        self.assertIn(RPC_PIN_APPLET, pin_req)
        self.assertIn("applet-123", pin_req)
        self.assertIn("1", pin_req)

        unpin_req = build_pin_applet_request("applet-123", pinned=False)
        self.assertIn(RPC_PIN_APPLET, unpin_req)
        self.assertIn("0", unpin_req)

        # 5. ZLaYcd (Delete)
        del_req = build_delete_applet_request("applet-999")
        self.assertIn(RPC_DELETE_APPLET, del_req)
        self.assertIn("applets/applet-999", del_req)

    def test_resolve_omni_flash_duration(self):
        """Verify duration resolution accurately maps to 4s, 6s, 8s, 10s."""
        self.assertEqual(resolve_omni_flash_duration(2.0), 4)
        self.assertEqual(resolve_omni_flash_duration(4.0), 4)
        self.assertEqual(resolve_omni_flash_duration(5.5), 6)
        self.assertEqual(resolve_omni_flash_duration(6.0), 6)
        self.assertEqual(resolve_omni_flash_duration(7.1), 8)
        self.assertEqual(resolve_omni_flash_duration(8.0), 8)
        self.assertEqual(resolve_omni_flash_duration(9.5), 10)
        self.assertEqual(resolve_omni_flash_duration(15.0), 10)

    def test_build_vp_omni_studio_v2_state(self):
        """Verify build_vp_omni_studio_v2_state constructs complete schema."""
        spec = {
            "aspect_ratio": "16:9",
            "character_ref": {"mediaId": "med-char-1"},
            "style_ref": {"mediaId": "med-style-2"},
            "scenes": [
                {
                    "scene_id": "01",
                    "narration": "Đòn bẩy tài chính là vũ khí mạnh nhất.",
                    "visual_prompt": "Stickman holding lever",
                    "duration_seconds": 3.5,
                },
                {
                    "scene_id": "02",
                    "narration": "Hệ thống vận hành không phụ thuộc vào bạn.",
                    "visual_prompt": "Automated gears turning",
                    "duration_seconds": 7.5,
                },
            ],
        }

        state = build_vp_omni_studio_v2_state(spec)

        self.assertEqual(state["engine"], "VP Omni Chain Studio V2")
        self.assertEqual(state["version"], "2.0.0")
        self.assertEqual(state["storage_key"], OMNI_STUDIO_STORAGE_KEY)
        self.assertEqual(state["mode"], "hybrid_video")
        self.assertFalse(state["zero_credit_flipbook"])
        self.assertEqual(state["aspect_ratio"], "16:9")
        self.assertEqual(len(state["scenes"]), 2)

        # Verify auto-durations
        self.assertEqual(state["scenes"][0]["omni_duration"], 4)
        self.assertEqual(state["scenes"][1]["omni_duration"], 8)

        # Verify zero_credit_flipbook fallback mode
        flip_spec = {"zero_credit_flipbook": True}
        flip_state = build_vp_omni_studio_v2_state(flip_spec)
        self.assertTrue(flip_state["zero_credit_flipbook"])
        self.assertEqual(flip_state["mode"], "zero_credit_flipbook")

    def test_generate_vp_omni_studio_v2_tsx(self):
        """Verify generate_vp_omni_studio_v2_tsx outputs valid React 19 + flow-sdk App.tsx."""
        tsx = generate_vp_omni_studio_v2_tsx()

        self.assertIsInstance(tsx, str)
        self.assertGreater(len(tsx), 15000)

        # 1. Flow SDK import
        self.assertIn('import * as Flow from "flow-sdk"', tsx)

        # 2. Flow SDK API Calls
        self.assertIn("Flow.generate.image", tsx)
        self.assertIn("Flow.generate.video", tsx)
        self.assertIn("Flow.generate.text", tsx)
        self.assertIn("Flow.media.select", tsx)
        self.assertIn("Flow.save", tsx)
        self.assertIn("Flow.download", tsx)
        self.assertIn("Flow.storage.getItem", tsx)
        self.assertIn("Flow.storage.setItem", tsx)

        # 3. Core Models & Keys
        self.assertIn("🍌 Nano Banana 2.1", tsx)
        self.assertIn("Omni 1.2 Flash", tsx)
        self.assertIn(OMNI_STUDIO_STORAGE_KEY, tsx)
        self.assertIn("hybrid_video", tsx)
        self.assertIn("zero_credit_flipbook", tsx)

        # 4. React 19 Hooks
        self.assertIn("useState", tsx)
        self.assertIn("useEffect", tsx)
        self.assertIn("useCallback", tsx)
        self.assertIn("useRef", tsx)

    def test_cli_export_and_build_state(self):
        """Verify manage_flow_applets CLI commands export and build state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_tsx = Path(tmpdir) / "App.tsx"
            cmd_export_v2_tsx(str(out_tsx))
            self.assertTrue(out_tsx.exists())
            self.assertGreater(out_tsx.stat().st_size, 10000)

            # Check prompt companion
            prompt_file = Path(tmpdir) / "CREATION_PROMPT.md"
            self.assertTrue(prompt_file.exists())
            self.assertIn("VP Omni Chain Studio V2", prompt_file.read_text(encoding="utf-8"))

            # Check build state JSON
            out_json = Path(tmpdir) / "state.json"
            cmd_build_state_json(output_path=str(out_json))
            self.assertTrue(out_json.exists())
            parsed_json = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(parsed_json["engine"], "VP Omni Chain Studio V2")


if __name__ == "__main__":
    unittest.main()
