"""Sử Kể Lại (su_ke_lai) channel module.

Visual Profile: ch_dong_ho_folk (Dong Ho folk woodblock print on do paper)
Voice: VietNarrator (1.0x)
Niche: Lịch sử Việt Nam và thế giới kể như phim
"""

from channels.su_ke_lai.builder import (
    DEFAULT_TOPIC_LONG,
    DEFAULT_TOPIC_SHORT,
    build_su_ke_lai_long,
    build_su_ke_lai_package,
    build_su_ke_lai_short,
)

__all__ = [
    "DEFAULT_TOPIC_LONG",
    "DEFAULT_TOPIC_SHORT",
    "build_su_ke_lai_long",
    "build_su_ke_lai_package",
    "build_su_ke_lai_short",
]
