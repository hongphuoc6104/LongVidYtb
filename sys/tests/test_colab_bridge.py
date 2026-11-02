#!/usr/bin/env python3
"""Unit tests for colab_bridge protocol and tone speed resolution."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from colab_bridge.protocol import (
    TONE_SPEED_MULTIPLIERS,
    positive,
    resolve_tone_speed,
    safe_id,
)


class TestColabBridgeProtocol(unittest.TestCase):
    def test_tone_speed_multipliers(self):
        self.assertEqual(TONE_SPEED_MULTIPLIERS["narrative_warm"], 1.00)
        self.assertEqual(TONE_SPEED_MULTIPLIERS["analytical_crisp"], 1.02)
        self.assertEqual(TONE_SPEED_MULTIPLIERS["reflective_slow"], 0.98)

    def test_resolve_tone_speed(self):
        self.assertEqual(resolve_tone_speed(1.0, "narrative_warm"), 1.00)
        self.assertEqual(resolve_tone_speed(1.0, "analytical_crisp"), 1.02)
        self.assertEqual(resolve_tone_speed(1.0, "reflective_slow"), 0.98)
        self.assertEqual(resolve_tone_speed(1.0, None), 1.00)
        self.assertEqual(resolve_tone_speed(1.0, "unknown_tone"), 1.00)

        # Scaled speeds
        self.assertEqual(resolve_tone_speed(1.10, "narrative_warm"), 1.10)
        self.assertEqual(resolve_tone_speed(1.05, "analytical_crisp"), 1.071)
        self.assertEqual(resolve_tone_speed(0.95, "reflective_slow"), 0.931)

    def test_safe_id(self):
        self.assertEqual(safe_id("scene_001"), "scene_001")
        with self.assertRaises(ValueError):
            safe_id("invalid/id")

    def test_positive(self):
        self.assertEqual(positive(1.5, "speed"), 1.5)
        with self.assertRaises(ValueError):
            positive(-1.0, "speed")


if __name__ == "__main__":
    unittest.main()
