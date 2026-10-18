"""Patch partitioner for Flow CDP image generation.

Groups shots into moderate patches (2-4 shots each), keeping dependency
chains (based_on) within the same patch to preserve context and intermediate
forge IDs, while allowing independent patches to run concurrently across profiles.
Tracks per-item completion so failed patches only retry remaining failed items.
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Patch:
    patch_id: str
    items: list[dict[str, Any]]
    status: str = "pending"  # "pending", "running", "completed", "failed"
    completed_items: dict[str, dict[str, Any]] = field(default_factory=dict)
    failed_items: dict[str, str] = field(default_factory=dict)
    error: str | None = None
    assigned_profile: str | None = None
    retry_count: int = 0
    dependency_group_id: str | None = None
    pinned_profile: str | None = None
    depends_on_patch_id: str | None = None

    @property
    def total_items(self) -> int:
        return len(self.items)

    @property
    def pending_count(self) -> int:
        return len(self.items) - len(self.completed_items)

    @property
    def is_completed(self) -> bool:
        return len(self.completed_items) == len(self.items)

    def get_pending_items(self) -> list[dict[str, Any]]:
        """Return only items in the patch that have not succeeded yet."""
        return [
            item for item in self.items
            if self._item_id(item) not in self.completed_items
        ]

    def mark_item_success(self, item_id: str, result: dict[str, Any]) -> None:
        self.completed_items[item_id] = result
        if item_id in self.failed_items:
            del self.failed_items[item_id]
        if self.is_completed:
            self.status = "completed"
            self.error = None

    def mark_item_failure(self, item_id: str, error_msg: str) -> None:
        if item_id in self.completed_items:
            return
        self.failed_items[item_id] = error_msg
        self.error = error_msg
        self.status = "failed"

    @staticmethod
    def _item_id(item: dict[str, Any]) -> str:
        return str(item.get("testCase") or item.get("id") or item.get("job_id") or item.get("request_id") or "")


class PatchPartitioner:
    """Partitions a list of shots/items into moderate-sized patches (2-4 items)."""

    def __init__(self, target_size: int = 3, min_size: int = 2, max_size: int = 4):
        self.target_size = max(1, min(max_size, target_size))
        self.min_size = max(1, min_size)
        self.max_size = max(self.target_size, max_size)

    @staticmethod
    def _get_id(item: dict[str, Any]) -> str:
        return str(item.get("testCase") or item.get("id") or item.get("job_id") or "")

    @staticmethod
    def _get_parent_id(item: dict[str, Any]) -> str | None:
        parent = item.get("based_on") or item.get("base_shot") or item.get("parent_id")
        return str(parent) if parent else None

    @staticmethod
    def _resolve_item_profile(item: dict[str, Any]) -> str | None:
        p_id = item.get("profile_id") or item.get("profile")
        if p_id:
            return str(p_id)
        base_img = item.get("base_image")
        if isinstance(base_img, dict):
            if base_img.get("profile_id"):
                return str(base_img["profile_id"])
            if base_img.get("path"):
                try:
                    sc = Path(str(base_img["path"])).with_suffix(".json")
                    if sc.is_file():
                        data = json.loads(sc.read_text(encoding="utf-8"))
                        cand = data.get("profile_id") or data.get("profile")
                        if cand:
                            return str(cand)
                except Exception:
                    pass
        base_ref = (
            item.get("baseRefPath")
            or item.get("base_ref_path")
            or (base_img if isinstance(base_img, (str, Path)) else None)
        )
        if base_ref:
            try:
                sidecar = Path(str(base_ref)).with_suffix(".json")
                if sidecar.is_file():
                    data = json.loads(sidecar.read_text(encoding="utf-8"))
                    cand = data.get("profile_id") or data.get("profile")
                    if cand:
                        return str(cand)
            except Exception:
                pass
        based_on = item.get("based_on")
        if based_on and isinstance(based_on, (str, Path)):
            try:
                sc = Path(str(based_on)).with_suffix(".json")
                if sc.is_file():
                    data = json.loads(sc.read_text(encoding="utf-8"))
                    cand = data.get("profile_id") or data.get("profile")
                    if cand:
                        return str(cand)
            except Exception:
                pass
        return None

    def build_dependency_groups(self, items: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        """Group items by dependency chains so parents and children stay together."""
        id_to_item = {self._get_id(item): item for item in items}
        parent_map: dict[str, str] = {}
        children_map: dict[str, list[str]] = {}

        for item in items:
            item_id = self._get_id(item)
            p_id = self._get_parent_id(item)
            if p_id and p_id in id_to_item:
                parent_map[item_id] = p_id
                children_map.setdefault(p_id, []).append(item_id)

        visited: set[str] = set()
        chains: list[list[dict[str, Any]]] = []

        def get_root(node_id: str) -> str:
            curr = node_id
            seen_ancestors = set()
            while curr in parent_map and curr not in seen_ancestors:
                seen_ancestors.add(curr)
                curr = parent_map[curr]
            return curr

        # Find connected components (roots first)
        for item in items:
            item_id = self._get_id(item)
            if item_id in visited:
                continue

            root = get_root(item_id)
            # Traverse topologically from root
            chain: list[dict[str, Any]] = []
            queue = [root]
            seen_in_chain = {root}

            while queue:
                curr_id = queue.pop(0)
                if curr_id in id_to_item:
                    chain.append(id_to_item[curr_id])
                visited.add(curr_id)
                for child_id in children_map.get(curr_id, []):
                    if child_id not in seen_in_chain:
                        seen_in_chain.add(child_id)
                        queue.append(child_id)

            if chain:
                chains.append(chain)

        return chains

    def partition(self, items: list[dict[str, Any]]) -> list[Patch]:
        """Partition items into patches of size target_size (min 2, max 4), preserving dependencies."""
        if not items:
            return []

        chains = self.build_dependency_groups(items)
        patches: list[Patch] = []
        current_patch_items: list[dict[str, Any]] = []

        for chain in chains:
            # Check if any item in the chain has a known/pinned profile
            chain_profile = next(
                (self._resolve_item_profile(it) for it in chain if self._resolve_item_profile(it)),
                None
            )

            # If the chain itself is larger than max_size, it must be split sequentially
            # into chunks, but linked via dependency_group_id and depends_on_patch_id
            # so they are sequentially pinned to the same worker profile.
            if len(chain) > self.max_size:
                # Flush existing buffer first
                if current_patch_items:
                    buf_prof = next(
                        (self._resolve_item_profile(it) for it in current_patch_items if self._resolve_item_profile(it)),
                        None
                    )
                    patches.append(Patch(
                        patch_id=f"patch-{len(patches)+1}-{uuid.uuid4().hex[:6]}",
                        items=current_patch_items,
                        pinned_profile=buf_prof,
                    ))
                    current_patch_items = []

                # Split the large chain into chunks of target_size, bound to same dependency group
                group_id = f"depgroup-{uuid.uuid4().hex[:8]}"
                prev_patch_id = None
                for i in range(0, len(chain), self.target_size):
                    chunk = chain[i : i + self.target_size]
                    p_id = f"patch-{len(patches)+1}-{uuid.uuid4().hex[:6]}"
                    p = Patch(
                        patch_id=p_id,
                        items=chunk,
                        dependency_group_id=group_id,
                        pinned_profile=chain_profile,
                        depends_on_patch_id=prev_patch_id,
                    )
                    patches.append(p)
                    prev_patch_id = p_id
                continue

            # If current buffer has items and either size would exceed max_size,
            # or current buffer's profile conflicts with this chain's profile, flush first
            buf_prof = next(
                (self._resolve_item_profile(it) for it in current_patch_items if self._resolve_item_profile(it)),
                None
            )
            profile_conflict = (
                buf_prof is not None
                and chain_profile is not None
                and buf_prof != chain_profile
            )
            if len(current_patch_items) + len(chain) > self.max_size or profile_conflict:
                if current_patch_items:
                    patches.append(Patch(
                        patch_id=f"patch-{len(patches)+1}-{uuid.uuid4().hex[:6]}",
                        items=current_patch_items,
                        pinned_profile=buf_prof,
                    ))
                    current_patch_items = []

            current_patch_items.extend(chain)

            # If current buffer reaches or exceeds target_size, flush
            if len(current_patch_items) >= self.target_size:
                buf_prof = next(
                    (self._resolve_item_profile(it) for it in current_patch_items if self._resolve_item_profile(it)),
                    None
                )
                patches.append(Patch(
                    patch_id=f"patch-{len(patches)+1}-{uuid.uuid4().hex[:6]}",
                    items=current_patch_items,
                    pinned_profile=buf_prof,
                ))
                current_patch_items = []

        if current_patch_items:
            buf_prof = next(
                (self._resolve_item_profile(it) for it in current_patch_items if self._resolve_item_profile(it)),
                None
            )
            # If leftover is 1 item and we have a previous patch with room (<= max_size - 1), merge
            # but only if previous patch is not in a separate dependency group and profile matches
            can_merge = (
                len(current_patch_items) == 1
                and patches
                and len(patches[-1].items) < self.max_size
                and patches[-1].dependency_group_id is None
                and (patches[-1].pinned_profile is None or patches[-1].pinned_profile == buf_prof)
            )
            if can_merge:
                patches[-1].items.extend(current_patch_items)
                if buf_prof and not patches[-1].pinned_profile:
                    patches[-1].pinned_profile = buf_prof
            else:
                patches.append(Patch(
                    patch_id=f"patch-{len(patches)+1}-{uuid.uuid4().hex[:6]}",
                    items=current_patch_items,
                    pinned_profile=buf_prof,
                ))

        return patches
