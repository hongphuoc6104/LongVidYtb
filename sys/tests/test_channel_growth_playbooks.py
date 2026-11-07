"""Unit test suite for 38-Channel Individualized Growth Playbooks & Phone SIM Verification Matrix."""

import pytest
from channels.channel_growth_playbooks import (
    CANONICAL_CHANNEL_IDS,
    CHANNEL_ALIASES,
    CHANNEL_GROWTH_PLAYBOOKS,
    SIM_SLOT_ALLOCATION_PLAN,
    USER_SIM_INVENTORY,
    ChannelGrowthPlaybook,
    get_channel_playbook,
    get_sim_verification_priority_queue,
    list_all_channel_playbooks,
)

VN_CHANNEL_IDS = [
    "nao_luoi",
    "tui_tien",
    "ua_sao_vay",
    "su_ke_lai",
    "thuong_cho_kheo",
    "ho_so_ky_la",
    "co_the_ke",
    "ai_binh_dan",
    "luat_ngam",
    "ban_do_quyen_luc",
    "dia_com",
    "luat_doi_thuong",
    "banh_rang",
    "vu_tru_ti_hon",
    "nghe_song_sot",
    "la_ban_hoc_thuat",
    "chanh_niem_ke",
    "loi_sang_soi",
    "minh_triet_song",
    "tam_tinh_dem",
]

EN_CANONICAL_CHANNEL_IDS = [
    "en_lazy_brain",
    "en_crowd_strings",
    "en_kindred_sketch",
    "en_first_principles",
    "en_wallet_anatomy",
    "en_macro_gears",
    "en_plain_sight_ai",
    "en_career_leverage",
    "en_fine_print",
    "en_inside_vessel",
    "en_kitchen_molecules",
    "en_wait_how",
    "en_cold_case_ink",
    "en_choke_point",
    "en_pocket_cosmos",
    "en_second_arrow",
    "en_parable_lamp",
    "en_bamboo_marble",
]


class TestChannelResolutionAndCoverage:
    """Verifies that all 38 physical channels and 4 aliases resolve cleanly."""

    def test_total_physical_channel_count(self) -> None:
        assert len(CANONICAL_CHANNEL_IDS) == 38
        assert len(VN_CHANNEL_IDS) == 20
        assert len(EN_CANONICAL_CHANNEL_IDS) == 18
        assert set(CANONICAL_CHANNEL_IDS) == set(VN_CHANNEL_IDS + EN_CANONICAL_CHANNEL_IDS)

    @pytest.mark.parametrize("cid", VN_CHANNEL_IDS)
    def test_all_vn_channels_resolve(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        assert isinstance(playbook, ChannelGrowthPlaybook)
        assert playbook.channel_id == cid
        assert playbook.language == "vi"
        assert playbook.display_name.strip() != ""
        assert playbook.handle.startswith("@")

    @pytest.mark.parametrize("cid", EN_CANONICAL_CHANNEL_IDS)
    def test_all_en_canonical_channels_resolve(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        assert isinstance(playbook, ChannelGrowthPlaybook)
        assert playbook.channel_id == cid
        assert playbook.language == "en"
        assert playbook.display_name.strip() != ""
        assert playbook.handle.startswith("@")

    @pytest.mark.parametrize(
        ("alias", "canonical"),
        [
            ("en_scale_and_bone", "en_plain_sight_ai"),
            ("en_root_and_canopy", "en_kitchen_molecules"),
            ("en_spawn_to_apex", "en_wait_how"),
            ("en_deep_time_strata", "en_parable_lamp"),
        ],
    )
    def test_renamed_en_aliases_resolve_to_canonical(self, alias: str, canonical: str) -> None:
        assert alias in CHANNEL_ALIASES
        assert CHANNEL_ALIASES[alias] == canonical

        playbook_via_func = get_channel_playbook(alias)
        playbook_via_dict = CHANNEL_GROWTH_PLAYBOOKS[alias]
        canonical_playbook = CHANNEL_GROWTH_PLAYBOOKS[canonical]

        assert playbook_via_func == canonical_playbook
        assert playbook_via_dict == canonical_playbook
        assert playbook_via_func.channel_id == canonical

    def test_unknown_channel_id_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="Unknown channel_id 'non_existent_channel'"):
            get_channel_playbook("non_existent_channel")


class TestViralBlueprintsAntiFlopStandards:
    """Verifies that all 114 viral blueprints comply with YouTube Anti-Flop length & formatting rules."""

    def test_blueprint_counts_across_all_physical_channels(self) -> None:
        for cid in CANONICAL_CHANNEL_IDS:
            playbook = get_channel_playbook(cid)
            assert len(playbook.next_3_viral_blueprints) == 3, f"{cid} must have exactly 3 viral blueprints"

    @pytest.mark.parametrize("cid", CANONICAL_CHANNEL_IDS)
    def test_blueprint_title_lengths_under_55_chars(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        for idx, bp in enumerate(playbook.next_3_viral_blueprints, start=1):
            short_t = bp["short_title"]
            long_t = bp["long_title"]

            assert len(short_t) <= 55, (
                f"{cid} blueprint #{idx} short_title length {len(short_t)} exceeds 55 chars: '{short_t}'"
            )
            assert len(long_t) <= 55, (
                f"{cid} blueprint #{idx} long_title length {len(long_t)} exceeds 55 chars: '{long_t}'"
            )
            assert len(short_t.strip()) > 0
            assert len(long_t.strip()) > 0

    @pytest.mark.parametrize("cid", CANONICAL_CHANNEL_IDS)
    def test_thumbnail_text_has_2_to_4_uppercase_words(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        for idx, bp in enumerate(playbook.next_3_viral_blueprints, start=1):
            thumb = bp["thumbnail_text"]
            words = thumb.strip().split()
            word_count = len(words)

            assert 2 <= word_count <= 4, (
                f"{cid} blueprint #{idx} thumbnail_text '{thumb}' has {word_count} words; expected 2 to 4 words"
            )
            assert thumb == thumb.upper(), (
                f"{cid} blueprint #{idx} thumbnail_text '{thumb}' is not strictly uppercase"
            )

    @pytest.mark.parametrize("cid", CANONICAL_CHANNEL_IDS)
    def test_hooks_and_bridges_are_populated(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        for idx, bp in enumerate(playbook.next_3_viral_blueprints, start=1):
            hook = bp["hook_opening_sentence"]
            bridge = bp["cliffhanger_bridge"]

            assert len(hook.strip()) > 0, f"{cid} blueprint #{idx} hook_opening_sentence is empty"
            assert len(bridge.strip()) > 0, f"{cid} blueprint #{idx} cliffhanger_bridge is empty"


class TestCohortAndAlgorithmicEngines:
    """Verifies cohort tiers, pacing directives, and algorithmic engine assignments."""

    VALID_COHORTS = {
        "vn_breakthrough",
        "vn_mid_tier",
        "vn_cold_pivot",
        "en_velocity_leader",
        "en_high_conversion",
        "en_breakout_queue",
    }

    VALID_ENGINES = {
        "shorts_somatosensory_shock",
        "search_seo_geopolitics",
        "forensic_open_loop",
        "parable_night_healing",
        "3d_universal_visual",
        "workplace_script_utility",
        "consumer_price_autopsy",
    }

    @pytest.mark.parametrize("cid", CANONICAL_CHANNEL_IDS)
    def test_cohort_tier_validity(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        assert playbook.cohort_tier in self.VALID_COHORTS

        if playbook.language == "vi":
            assert playbook.cohort_tier.startswith("vn_")
        else:
            assert playbook.cohort_tier.startswith("en_")

    @pytest.mark.parametrize("cid", CANONICAL_CHANNEL_IDS)
    def test_algorithmic_engine_validity(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        assert playbook.algorithmic_engine in self.VALID_ENGINES

    @pytest.mark.parametrize("cid", CANONICAL_CHANNEL_IDS)
    def test_retention_and_pacing_rules_populated(self, cid: str) -> None:
        playbook = get_channel_playbook(cid)
        assert len(playbook.hook_3s_formula.strip()) > 0
        assert len(playbook.short_to_long_cliffhanger.strip()) > 0
        assert len(playbook.long_retention_reset_rule.strip()) > 0
        assert len(playbook.visual_pacing_directive.strip()) > 0


class TestSimVerificationAndInventoryMatrix:
    """Verifies the 4 SIM cards inventory and priority allocation plan."""

    EXPECTED_PHONE_NUMBERS = {
        "0794999539",
        "0398658115",
        "0559745970",
        "0559238139",
    }

    def test_user_sim_inventory_integrity(self) -> None:
        assert len(USER_SIM_INVENTORY) == 4
        inventory_numbers = {sim["phone_number"] for sim in USER_SIM_INVENTORY.values()}
        assert inventory_numbers == self.EXPECTED_PHONE_NUMBERS

        # 2 used SIMs and 2 fresh SIMs
        used_sims = [s for s in USER_SIM_INVENTORY.values() if s["status"] == "used_sms"]
        fresh_sims = [s for s in USER_SIM_INVENTORY.values() if s["status"] == "fresh"]
        assert len(used_sims) == 2
        assert len(fresh_sims) == 2

        # Each SIM must account for 2 SMS and 2 Voice slots
        for sim in USER_SIM_INVENTORY.values():
            assert sim["sms_slots_total"] == 2
            assert sim["voice_slots_total"] == 2

    def test_sim_slot_allocation_plan_integrity(self) -> None:
        # Total slots = 4 numbers * 4 slots = 16 slots
        assert len(SIM_SLOT_ALLOCATION_PLAN) == 16

        historical_slots = [s for s in SIM_SLOT_ALLOCATION_PLAN.values() if s.is_historical]
        active_remaining_slots = [s for s in SIM_SLOT_ALLOCATION_PLAN.values() if not s.is_historical]

        assert len(historical_slots) == 4
        assert len(active_remaining_slots) == 12

        # Verify historical slots are on the used SIMs SMS slots (1 and 2)
        for slot in historical_slots:
            assert slot.phone_number in {"0794999539", "0398658115"}
            assert slot.verification_method == "sms"
            assert slot.slot_index in {1, 2}

        # Verify all user-requested high-priority unverified channels are allocated to active slots
        target_allocated_channels = {
            "en_macro_gears",
            "en_inside_vessel",
            "en_cold_case_ink",
            "en_fine_print",
            "en_choke_point",
            "en_first_principles",
            "en_kitchen_molecules",  # Root & Canopy
            "ban_do_quyen_luc",
            "tui_tien",
            "la_ban_hoc_thuat",
            "ai_binh_dan",
            "ho_so_ky_la",
        }
        active_channel_ids = {s.channel_id for s in active_remaining_slots}
        assert target_allocated_channels == active_channel_ids

    def test_sim_verification_priority_queue_length_and_order(self) -> None:
        queue = get_sim_verification_priority_queue()

        # Exactly 12 channels for the 12 active remaining slots
        assert len(queue) == 12

        # Verify strict order of priority ranks from 1 to 12
        ranks = [p.sim_priority_rank for p in queue]
        assert ranks == list(range(1, 13))

        # Check unique channels in queue
        queue_ids = [p.channel_id for p in queue]
        assert len(set(queue_ids)) == 12

        # Check that ranks 1..4 are assigned to SIM 3 (Fresh 0559745970)
        sim3_channels = queue[0:4]
        for p in sim3_channels:
            assert p.sim_slot_id is not None
            assert p.sim_slot_id.startswith("0559745970-")

        # Check that ranks 5..8 are assigned to SIM 4 (Fresh 0559238139)
        sim4_channels = queue[4:8]
        for p in sim4_channels:
            assert p.sim_slot_id is not None
            assert p.sim_slot_id.startswith("0559238139-")

        # Check that ranks 9..10 are assigned to SIM 1 (0794999539 Voice slots)
        sim1_voice_channels = queue[8:10]
        for p in sim1_voice_channels:
            assert p.sim_slot_id is not None
            assert p.sim_slot_id.startswith("0794999539-")

        # Check that ranks 11..12 are assigned to SIM 2 (0398658115 Voice slots)
        sim2_voice_channels = queue[10:12]
        for p in sim2_voice_channels:
            assert p.sim_slot_id is not None
            assert p.sim_slot_id.startswith("0398658115-")

    def test_unverified_cold_channels_have_frame_injection_strategy(self) -> None:
        cold_channels = [
            cid
            for cid in CANONICAL_CHANNEL_IDS
            if get_channel_playbook(cid).cohort_tier in {"vn_cold_pivot", "en_breakout_queue"}
            and get_channel_playbook(cid).sim_priority_rank > 12
        ]
        assert len(cold_channels) > 0
        for cid in cold_channels:
            pb = get_channel_playbook(cid)
            assert "Frame-0/25%/50% In-Video High-Contrast Thumbnail Injection" in pb.phone_sim_allocation
            assert "1,000 Shorts views" in pb.phone_sim_allocation

    def test_list_all_channel_playbooks_helper(self) -> None:
        canonical_only = list_all_channel_playbooks(include_aliases=False)
        assert len(canonical_only) == 38

        with_aliases = list_all_channel_playbooks(include_aliases=True)
        assert len(with_aliases) == 42
