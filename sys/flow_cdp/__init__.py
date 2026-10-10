"""Flow CDP (formerly B-2 Illustrator / CDP) package.

Provides Chrome DevTools Protocol automation for Google Flow image creation,
including multi-profile failover across 3 Chrome profiles and patch-based
parallel processing.
"""
from .patch_partitioner import PatchPartitioner, Patch
from .multi_profile_manager import (
    MultiProfileManager,
    MultiProfileDispatcher,
    ProfileState,
    ChromeProfileWorker,
)
from .bridge import (
    generate_cdp_image,
    generate_cdp_batch,
    generate_b2_image,
    generate_b2_batch,
    ensure_connected,
    query_status,
    send_raw_command,
    require_queue_acceptance,
    is_session_available,
    get_socket_path,
    SOCKET_PATH,
)

__all__ = [
    "PatchPartitioner",
    "Patch",
    "MultiProfileManager",
    "MultiProfileDispatcher",
    "ProfileState",
    "ChromeProfileWorker",
    "generate_cdp_image",
    "generate_cdp_batch",
    "generate_b2_image",
    "generate_b2_batch",
    "ensure_connected",
    "query_status",
    "send_raw_command",
    "require_queue_acceptance",
    "is_session_available",
    "get_socket_path",
    "SOCKET_PATH",
]
