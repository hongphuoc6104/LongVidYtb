"""Flow CDP (formerly B-2 Illustrator / CDP) package.

Provides Chrome DevTools Protocol automation for Google Flow image creation,
including multi-profile failover across 3 Chrome profiles and patch-based
parallel processing.
"""
from .bridge import (
    SOCKET_PATH,
    ensure_connected,
    generate_b2_batch,
    generate_b2_image,
    generate_cdp_batch,
    generate_cdp_image,
    get_socket_path,
    is_session_available,
    query_status,
    require_queue_acceptance,
    send_raw_command,
)
from .multi_profile_manager import (
    ChromeProfileWorker,
    MultiProfileDispatcher,
    MultiProfileManager,
    ProfileState,
)
from .lifecycle import (
    ProfileLifecycleManager,
    calculate_optimal_workers,
    calculate_rampup_timeout,
    calculate_rampup_workers,
    get_current_lifecycle,
    get_workload_tier_info,
    register_spawned_port,
    stop_all_profiles,
)
from .patch_partitioner import Patch, PatchPartitioner

__all__ = [
    "PatchPartitioner",
    "Patch",
    "MultiProfileManager",
    "MultiProfileDispatcher",
    "ProfileState",
    "ChromeProfileWorker",
    "calculate_optimal_workers",
    "calculate_rampup_workers",
    "calculate_rampup_timeout",
    "stop_all_profiles",
    "get_workload_tier_info",
    "ProfileLifecycleManager",
    "register_spawned_port",
    "get_current_lifecycle",
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
