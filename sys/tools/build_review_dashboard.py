#!/usr/bin/env python3
"""Video Review Dashboard Builder for Video Pilot (sys/tools/build_review_dashboard.py).

Generates and updates the enterprise Fleet & Video Review Dashboard:
- /home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/youtube_fleet_dashboard.html
- /home/hongphuoc6104/Desktop/vp-agent-core/video/video_review_dashboard.html

Preserves existing Fleet Overview and Channel Audit metrics while embedding the top-level
interactive Review & Approval Gate (20 Vietnamese Channels x 2 Videos = 40 Assets).
"""
from __future__ import annotations

import argparse
import html
import json
import logging
from pathlib import Path
from typing import Any, Optional, Union

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]
SYS_DIR = REPO_ROOT / "sys"
DEFAULT_QUEUE_PATH = SYS_DIR / "channels" / "video_review_queue.json"
DEFAULT_MAP_PATH = SYS_DIR / "channels" / "youtube_channel_map.json"

DEFAULT_BRAIN_DASHBOARD_PATH = Path(
    "/home/hongphuoc6104/.gemini/antigravity/brain/715cbad2-6a65-4677-b14e-8d30e126287f/youtube_fleet_dashboard.html"
)
DEFAULT_VIDEO_DIR_DASHBOARD_PATH = REPO_ROOT / "video" / "video_review_dashboard.html"

DEFAULT_OUTPUT_PATHS = [
    DEFAULT_BRAIN_DASHBOARD_PATH,
    DEFAULT_VIDEO_DIR_DASHBOARD_PATH,
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("build_review_dashboard")


REVIEW_GATE_CSS = """
/* --- Video Review & Approval Gate Styles --- */
.review-gate-section {
  margin-bottom: 32px;
}
.review-header-card {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.08), rgba(139, 92, 246, 0.08));
  border: 1px solid rgba(6, 182, 212, 0.25);
  border-radius: 14px;
  padding: 22px 26px;
  margin-bottom: 24px;
}
.review-header-title {
  font-size: 20px;
  font-weight: 800;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}
.review-header-desc {
  font-size: 13.5px;
  color: #94a3b8;
  line-height: 1.6;
}
.review-summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.rev-stat-card {
  background: rgba(18, 26, 44, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: transform 0.15s ease, border-color 0.15s ease;
}
.rev-stat-card:hover {
  transform: translateY(-2px);
}
.rev-stat-card.stat-total { border-left: 4px solid #06b6d4; }
.rev-stat-card.stat-pending { border-left: 4px solid #f59e0b; }
.rev-stat-card.stat-approved { border-left: 4px solid #10b981; }
.rev-stat-card.stat-rejected { border-left: 4px solid #f43f5e; }

.rev-stat-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #94a3b8;
  font-weight: 600;
}
.rev-stat-value {
  font-size: 28px;
  font-weight: 800;
  color: #f8fafc;
}
.rev-stat-sub {
  font-size: 11.5px;
  color: #64748b;
}

/* Review Toolbar */
.review-toolbar {
  background: rgba(18, 26, 44, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 14px 18px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 26px;
}
.review-filters-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  flex: 1;
}
.review-search-box {
  position: relative;
  min-width: 260px;
  flex: 1;
}
.review-search-input {
  width: 100%;
  background: rgba(12, 18, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 8px 12px 8px 32px;
  color: #fff;
  font-size: 13px;
  outline: none;
}
.review-search-input:focus {
  border-color: #06b6d4;
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
}
.review-search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
}
.review-select-filter {
  background: rgba(12, 18, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 8px 12px;
  color: #cbd5e1;
  font-size: 13px;
  outline: none;
  cursor: pointer;
}
.review-actions-group {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

/* Channel Block */
.channel-review-block {
  background: rgba(18, 26, 44, 0.65);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 20px;
  margin-bottom: 28px;
  transition: border-color 0.15s ease;
}
.channel-review-block:hover {
  border-color: rgba(6, 182, 212, 0.35);
}
.channel-block-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
  gap: 12px;
}
.channel-info-left {
  display: flex;
  align-items: center;
  gap: 12px;
}
.channel-avatar-circle {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #06b6d4, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  color: #ffffff;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.15);
}
.channel-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.channel-title-line {
  font-size: 17px;
  font-weight: 700;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 8px;
}
.badge-cdp-port {
  font-size: 11px;
  padding: 2px 7px;
  background: rgba(6, 182, 212, 0.12);
  border: 1px solid rgba(6, 182, 212, 0.3);
  color: #22d3ee;
  border-radius: 6px;
  font-family: monospace;
}
.channel-subtitle-line {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}
.cards-pair-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(460px, 1fr));
  gap: 20px;
}

/* Video Review Card */
.video-review-card {
  background: rgba(12, 18, 32, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  transition: all 0.2s ease;
  position: relative;
}
.video-review-card:hover {
  border-color: rgba(6, 182, 212, 0.3);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}
.video-review-card.card-approved {
  border-color: rgba(16, 185, 129, 0.35);
  background: rgba(16, 185, 129, 0.03);
}
.video-review-card.card-rejected {
  border-color: rgba(244, 63, 94, 0.35);
  background: rgba(244, 63, 94, 0.03);
}
.card-top-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.card-badges-left {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.badge-format {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  letter-spacing: 0.3px;
}
.badge-format.format-16x9 {
  background: rgba(6, 182, 212, 0.15);
  color: #22d3ee;
  border: 1px solid rgba(6, 182, 212, 0.3);
}
.badge-format.format-9x16 {
  background: rgba(139, 92, 246, 0.15);
  color: #c084fc;
  border: 1px solid rgba(139, 92, 246, 0.3);
}
.badge-engine {
  font-size: 11px;
  padding: 3px 7px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1;
  border-radius: 6px;
}
.status-pill {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 12px;
  letter-spacing: 0.4px;
}
.status-pill.status-PENDING_REVIEW {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
}
.status-pill.status-APPROVED {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}
.status-pill.status-REJECTED {
  background: rgba(244, 63, 94, 0.15);
  color: #fb7185;
  border: 1px solid rgba(244, 63, 94, 0.3);
}
.status-pill.status-PUBLISHED {
  background: rgba(6, 182, 212, 0.15);
  color: #22d3ee;
  border: 1px solid rgba(6, 182, 212, 0.3);
}

/* Video & Media Area */
.media-container {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  background: #000;
  position: relative;
}
.media-container.aspect-16x9 {
  aspect-ratio: 16 / 9;
}
.media-container.aspect-9x16 {
  aspect-ratio: 16 / 9;
  max-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #020617;
}
.review-video-player {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: #000;
}
.media-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 20px;
  text-align: center;
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.05), rgba(139, 92, 246, 0.05));
  position: relative;
}
.media-placeholder-thumb {
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  object-fit: cover;
  opacity: 0.35;
}
.media-placeholder-text {
  position: relative;
  z-index: 2;
  font-size: 13px;
  color: #cbd5e1;
  background: rgba(0, 0, 0, 0.65);
  padding: 6px 12px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Card Content */
.card-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.card-title {
  font-size: 14.5px;
  font-weight: 700;
  color: #f8fafc;
  line-height: 1.4;
}
.card-meta-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  color: #94a3b8;
}
.card-meta-code {
  font-family: monospace;
  color: #06b6d4;
  background: rgba(6, 182, 212, 0.08);
  padding: 1px 6px;
  border-radius: 4px;
}

/* Competitor Formula Callout */
.formula-callout {
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 12px;
  line-height: 1.5;
}
.formula-label {
  font-weight: 700;
  color: #fbbf24;
  margin-bottom: 3px;
  display: flex;
  align-items: center;
  gap: 5px;
}
.formula-body {
  color: #e2e8f0;
}

/* Decision Buttons */
.decision-buttons-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-top: 4px;
}
.btn-dec {
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.04);
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  transition: all 0.15s ease;
  outline: none;
}
.btn-dec:hover {
  background: rgba(255, 255, 255, 0.09);
  color: #ffffff;
}
.btn-dec.dec-pending.active {
  background: rgba(245, 158, 11, 0.18);
  border-color: #f59e0b;
  color: #fbbf24;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.2);
}
.btn-dec.dec-approve.active {
  background: rgba(16, 185, 129, 0.2);
  border-color: #10b981;
  color: #34d399;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
}
.btn-dec.dec-reject.active {
  background: rgba(244, 63, 94, 0.2);
  border-color: #f43f5e;
  color: #fb7185;
  box-shadow: 0 0 10px rgba(244, 63, 94, 0.25);
}

/* Notes Textarea & Tag Chips */
.notes-wrapper {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 4px;
}
.notes-label {
  font-size: 11.5px;
  font-weight: 600;
  color: #cbd5e1;
}
.review-notes-textarea {
  width: 100%;
  background: rgba(6, 10, 20, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 8px;
  padding: 8px 10px;
  font-size: 12.5px;
  color: #f8fafc;
  line-height: 1.45;
  resize: vertical;
  min-height: 64px;
  outline: none;
  font-family: inherit;
}
.review-notes-textarea:focus {
  border-color: #06b6d4;
  box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
}
.tag-chips-row {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}
.chip-hint {
  font-size: 11px;
  color: #64748b;
  font-weight: 600;
}
.tag-chip {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  padding: 3px 8px;
  font-size: 11px;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s ease;
  outline: none;
}
.tag-chip:hover {
  background: rgba(6, 182, 212, 0.15);
  border-color: #06b6d4;
  color: #22d3ee;
  transform: translateY(-1px);
}
"""


REVIEW_GATE_JS = """
// =====================================================================
// VIDEO REVIEW & APPROVAL GATE LOGIC (V1)
// =====================================================================
const REVIEW_STORAGE_KEY = 'VP_VIDEO_REVIEW_QUEUE_V1';

let reviewQueueState = {};

function initReviewQueue() {
  const dataScript = document.getElementById('__REVIEW_QUEUE_DATA__');
  if (dataScript) {
    try {
      const parsed = JSON.parse(dataScript.textContent);
      reviewQueueState = parsed.items || {};
    } catch (e) {
      console.warn('Could not parse review queue JSON:', e);
      reviewQueueState = {};
    }
  }

  // Restore local modifications if any
  try {
    const saved = localStorage.getItem(REVIEW_STORAGE_KEY);
    if (saved) {
      const localDecisions = JSON.parse(saved);
      for (const [jobId, dec] of Object.entries(localDecisions)) {
        if (reviewQueueState[jobId]) {
          if (dec.status) reviewQueueState[jobId].status = dec.status;
          if (dec.review_notes !== undefined) reviewQueueState[jobId].review_notes = dec.review_notes;
        }
      }
    }
  } catch (e) {
    console.warn('LocalStorage error:', e);
  }

  // Hydrate DOM cards with current state
  for (const [jobId, item] of Object.entries(reviewQueueState)) {
    updateCardUI(jobId, item.status, item.review_notes || '');
  }

  updateReviewCounters();
}

function updateCardUI(jobId, status, notes) {
  const card = document.getElementById(`card-${jobId}`);
  if (!card) return;

  card.setAttribute('data-status', status);
  card.classList.remove('card-approved', 'card-rejected');
  if (status === 'APPROVED') card.classList.add('card-approved');
  if (status === 'REJECTED') card.classList.add('card-rejected');

  // Pill
  const pill = document.getElementById(`pill-${jobId}`);
  if (pill) {
    pill.className = `status-pill status-${status}`;
    const labels = {
      'PENDING_REVIEW': '⏳ Chờ duyệt',
      'APPROVED': '✅ Đã duyệt',
      'REJECTED': '❌ Cần sửa',
      'PUBLISHED': '🚀 Đã đăng'
    };
    pill.textContent = labels[status] || status;
  }

  // Buttons
  const btnPending = card.querySelector('.dec-pending');
  const btnApprove = card.querySelector('.dec-approve');
  const btnReject = card.querySelector('.dec-reject');
  if (btnPending) btnPending.classList.toggle('active', status === 'PENDING_REVIEW');
  if (btnApprove) btnApprove.classList.toggle('active', status === 'APPROVED');
  if (btnReject) btnReject.classList.toggle('active', status === 'REJECTED');

  // Textarea
  const textarea = document.getElementById(`notes-${jobId}`);
  if (textarea && textarea.value !== notes) {
    textarea.value = notes;
  }
}

function saveLocalReviewState() {
  try {
    const snapshot = {};
    for (const [jobId, item] of Object.entries(reviewQueueState)) {
      snapshot[jobId] = {
        job_id: jobId,
        status: item.status,
        review_notes: item.review_notes || ''
      };
    }
    localStorage.setItem(REVIEW_STORAGE_KEY, JSON.stringify(snapshot));
  } catch (e) {
    console.warn('Failed to save to localStorage:', e);
  }
}

function setJobDecision(jobId, status) {
  if (!reviewQueueState[jobId]) {
    reviewQueueState[jobId] = { job_id: jobId, status: status, review_notes: '' };
  }
  reviewQueueState[jobId].status = status;
  const notes = reviewQueueState[jobId].review_notes || '';

  updateCardUI(jobId, status, notes);
  updateReviewCounters();
  saveLocalReviewState();

  // If rejected, focus textarea
  if (status === 'REJECTED') {
    const textarea = document.getElementById(`notes-${jobId}`);
    if (textarea) textarea.focus();
  }
}

function onNotesInput(jobId, text) {
  if (!reviewQueueState[jobId]) {
    reviewQueueState[jobId] = { job_id: jobId, status: 'PENDING_REVIEW', review_notes: text };
  }
  reviewQueueState[jobId].review_notes = text;
  saveLocalReviewState();
  updateReviewCounters();
}

function addTagToNote(jobId, tag) {
  const textarea = document.getElementById(`notes-${jobId}`);
  if (!textarea) return;

  const current = textarea.value.trim();
  let updated = '';
  if (!current) {
    updated = tag + ' ';
  } else if (!current.includes(tag)) {
    updated = current + ' • ' + tag;
  } else {
    updated = current;
  }

  textarea.value = updated;
  if (!reviewQueueState[jobId]) {
    reviewQueueState[jobId] = { job_id: jobId, status: 'REJECTED', review_notes: updated };
  }
  reviewQueueState[jobId].review_notes = updated;

  // Auto-switch to REJECTED if currently PENDING_REVIEW or APPROVED
  if (reviewQueueState[jobId].status !== 'REJECTED') {
    reviewQueueState[jobId].status = 'REJECTED';
    updateCardUI(jobId, 'REJECTED', updated);
  }

  saveLocalReviewState();
  updateReviewCounters();
  textarea.focus();
}

function updateReviewCounters() {
  let pending = 0;
  let approved = 0;
  let rejected = 0;
  let total = 0;

  for (const item of Object.values(reviewQueueState)) {
    total++;
    const st = item.status;
    if (st === 'APPROVED') approved++;
    else if (st === 'REJECTED') rejected++;
    else pending++;
  }

  const cp = document.getElementById('counter-pending');
  const ca = document.getElementById('counter-approved');
  const cr = document.getElementById('counter-rejected');
  const ct = document.getElementById('counter-total');
  const tabBadge = document.getElementById('count-tab-review');

  if (cp) cp.textContent = pending;
  if (ca) ca.textContent = approved;
  if (cr) cr.textContent = rejected;
  if (ct) ct.textContent = total;
  if (tabBadge) tabBadge.textContent = total;
}

function filterReviewCards() {
  const searchInput = document.getElementById('review-search');
  const query = (searchInput ? searchInput.value : '').toLowerCase().trim();
  const statusFilter = (document.getElementById('review-status-filter') || {}).value || 'all';
  const formatFilter = (document.getElementById('review-format-filter') || {}).value || 'all';

  const cards = document.querySelectorAll('.video-review-card');
  const channelBlocks = document.querySelectorAll('.channel-review-block');

  cards.forEach(card => {
    const cardStatus = card.getAttribute('data-status') || '';
    const cardFormat = card.getAttribute('data-format') || '';
    const textContent = card.textContent.toLowerCase();

    const matchesQuery = !query || textContent.includes(query);
    const matchesStatus = (statusFilter === 'all') || (cardStatus === statusFilter);
    const matchesFormat = (formatFilter === 'all') || (cardFormat === formatFilter);

    if (matchesQuery && matchesStatus && matchesFormat) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });

  // Hide channel blocks that have no visible cards
  channelBlocks.forEach(block => {
    const visibleCards = block.querySelectorAll('.video-review-card[style="display: flex;"]');
    const allCards = block.querySelectorAll('.video-review-card');
    let hasVisible = false;
    allCards.forEach(c => {
      if (c.style.display !== 'none') hasVisible = true;
    });
    block.style.display = hasVisible ? 'block' : 'none';
  });
}

function exportReviewDecisions() {
  const exportPayload = {
    schema_version: '1.0',
    exported_at: new Date().toISOString(),
    decisions: {}
  };

  for (const [jobId, item] of Object.entries(reviewQueueState)) {
    exportPayload.decisions[jobId] = {
      job_id: jobId,
      status: item.status || 'PENDING_REVIEW',
      review_notes: item.review_notes || ''
    };
  }

  const jsonStr = JSON.stringify(exportPayload, null, 2);
  const blob = new Blob([jsonStr], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'review_decisions.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast('✓ Đã xuất tệp review_decisions.json thành công!', 'success');
}

function copyApplyCommand() {
  const cmd = 'python3 sys/tools/review_queue_manager.py --apply-json sys/channels/review_decisions.json';
  navigator.clipboard.writeText(cmd).then(() => {
    showToast('📋 Đã copy lệnh áp dụng vào clipboard: ' + cmd, 'success');
  }).catch(() => {
    prompt('Copy lệnh sau để áp dụng quyết định duyệt:', cmd);
  });
}

function resetReviewQueue() {
  if (confirm('Bạn có chắc muốn đặt lại toàn bộ thay đổi cục bộ về trạng thái gốc từ máy chủ?')) {
    localStorage.removeItem(REVIEW_STORAGE_KEY);
    location.reload();
  }
}
"""


def _format_duration(seconds: float) -> str:
    """Format duration in seconds to mm:ss."""
    if not seconds or seconds <= 0:
        return "Chưa đo"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"


def _build_review_gate_html(queue_items: dict[str, Any], channel_map: dict[str, Any]) -> str:
    """Generate the full HTML markup for the Review Gate tab."""
    # Group items by channel_id
    channels_grouped: dict[str, list[dict[str, Any]]] = {}
    for item in queue_items.values():
        cid = item.get("channel_id") or "other"
        channels_grouped.setdefault(cid, []).append(item)

    # Sort channels nicely
    channel_blocks_html = []
    for cid, items in channels_grouped.items():
        # Get channel metadata
        ch_meta = channel_map.get("channels", {}).get(cid, {})
        c_name = ch_meta.get("channel_name") or (items[0].get("channel_name") if items else cid)
        handle = ch_meta.get("handle") or f"@{cid}"
        cdp_port = ch_meta.get("cdp_port", "923x")

        # Avatar initial or path
        initial = c_name[0].upper() if c_name else "V"
        avatar_html = f"<span>{initial}</span>"

        # Cards inside this channel
        cards_html = []
        # Sort items: long_16x9 first, then short_9x16
        sorted_items = sorted(items, key=lambda x: 0 if "16x9" in x.get("format_profile", "") else 1)

        for item in sorted_items:
            job_id = item["job_id"]
            status = item.get("status", "PENDING_REVIEW")
            format_prof = item.get("format_profile", "long_16x9")
            is_short = "9x16" in format_prof
            format_label = "Short 9:16 Spin-off" if is_short else "Long 16:9 Explainer"
            format_badge_cls = "format-9x16" if is_short else "format-16x9"
            aspect_cls = "aspect-9x16" if is_short else "aspect-16x9"
            dur_str = _format_duration(item.get("duration_sec", 0.0))
            title = item.get("title") or f"{c_name} — Đợt Batch 3"
            formula = item.get("competitor_formula") or "Benchmark tham chiếu chuẩn hoá theo định dạng Feynman 2D."
            notes = item.get("review_notes", "")
            mp4_path = item.get("mp4_path", "")
            thumb_path = item.get("thumbnail_path", "")

            # Media player / preview
            if mp4_path and Path(mp4_path).is_file():
                media_html = f"""
                <div class="media-container {aspect_cls}">
                  <video controls preload="metadata" poster="{html.escape(thumb_path)}" class="review-video-player">
                    <source src="{html.escape(mp4_path)}" type="video/mp4">
                    Trình duyệt không hỗ trợ thẻ video.
                  </video>
                </div>
                """
            elif thumb_path and Path(thumb_path).is_file():
                media_html = f"""
                <div class="media-container {aspect_cls}">
                  <img src="{html.escape(thumb_path)}" class="media-placeholder-thumb" alt="Thumbnail">
                  <div class="media-placeholder-text">⏳ Video MP4 đang render trên Colab T4</div>
                </div>
                """
            else:
                media_html = f"""
                <div class="media-container {aspect_cls}">
                  <div class="media-placeholder">
                    <div class="media-placeholder-text">⏳ Đang tổng hợp asset & render ({format_label})</div>
                  </div>
                </div>
                """

            status_labels = {
                "PENDING_REVIEW": "⏳ Chờ duyệt",
                "APPROVED": "✅ Đã duyệt",
                "REJECTED": "❌ Cần sửa",
                "PUBLISHED": "🚀 Đã đăng",
            }
            status_text = status_labels.get(status, status)
            card_extra_cls = (
                "card-approved"
                if status == "APPROVED"
                else ("card-rejected" if status == "REJECTED" else "")
            )

            card_html = f"""
            <div class="video-review-card {card_extra_cls}" id="card-{html.escape(job_id)}"
                 data-job-id="{html.escape(job_id)}"
                 data-status="{html.escape(status)}"
                 data-format="{html.escape(format_prof)}">
              <div class="card-top-row">
                <div class="card-badges-left">
                  <span class="badge-format {format_badge_cls}">{format_label}</span>
                  <span class="badge-engine">Flow Start➔End Frames</span>
                </div>
                <span class="status-pill status-{html.escape(status)}" id="pill-{html.escape(job_id)}">{status_text}</span>
              </div>

              {media_html}

              <div class="card-content">
                <div class="card-title">{html.escape(title)}</div>
                <div class="card-meta-row">
                  <span class="card-meta-code">{html.escape(job_id)}</span>
                  <span>Thời lượng: <b>{dur_str}</b></span>
                </div>
              </div>

              <div class="formula-callout">
                <div class="formula-label">🎯 Công thức đối thủ & Benchmark:</div>
                <div class="formula-body">{html.escape(formula)}</div>
              </div>

              <div class="decision-buttons-row">
                <button type="button" class="btn-dec dec-pending {'active' if status == 'PENDING_REVIEW' else ''}"
                        onclick="setJobDecision('{html.escape(job_id)}', 'PENDING_REVIEW')">
                  ⏳ Chờ duyệt
                </button>
                <button type="button" class="btn-dec dec-approve {'active' if status == 'APPROVED' else ''}"
                        onclick="setJobDecision('{html.escape(job_id)}', 'APPROVED')">
                  ✅ Duyệt đăng
                </button>
                <button type="button" class="btn-dec dec-reject {'active' if status == 'REJECTED' else ''}"
                        onclick="setJobDecision('{html.escape(job_id)}', 'REJECTED')">
                  ❌ Cần sửa
                </button>
              </div>

              <div class="notes-wrapper">
                <label class="notes-label" for="notes-{html.escape(job_id)}">Ghi chú lỗi / Yêu cầu sửa:</label>
                <textarea id="notes-{html.escape(job_id)}" class="review-notes-textarea"
                          placeholder="Nhập ghi chú lỗi nếu không duyệt (VD: Hook 3s đầu chưa đủ gắt, cảnh 2 chuyển động chưa khớp, cần đọc nhanh hơn...)"
                          oninput="onNotesInput('{html.escape(job_id)}', this.value)">{html.escape(notes)}</textarea>
                <div class="tag-chips-row">
                  <span class="chip-hint">Gợi ý nhanh:</span>
                  <button type="button" class="tag-chip" onclick="addTagToNote('{html.escape(job_id)}', '[+ Sửa Hook 3s đầu]')">+ Sửa Hook 3s đầu</button>
                  <button type="button" class="tag-chip" onclick="addTagToNote('{html.escape(job_id)}', '[+ Đổi ảnh Start-End cảnh bị lỗi]')">+ Đổi ảnh Start-End cảnh bị lỗi</button>
                  <button type="button" class="tag-chip" onclick="addTagToNote('{html.escape(job_id)}', '[+ Chỉnh lại giọng đọc/nhịp]')">+ Chỉnh lại giọng đọc/nhịp</button>
                  <button type="button" class="tag-chip" onclick="addTagToNote('{html.escape(job_id)}', '[+ Sửa tiêu đề/Thumbnail]')">+ Sửa tiêu đề/Thumbnail</button>
                  <button type="button" class="tag-chip" onclick="addTagToNote('{html.escape(job_id)}', '[+ Sửa nội dung kịch bản]')">+ Sửa nội dung kịch bản</button>
                </div>
              </div>
            </div>
            """
            cards_html.append(card_html)

        block_html = f"""
        <div class="channel-review-block" data-channel-id="{html.escape(cid)}">
          <div class="channel-block-header">
            <div class="channel-info-left">
              <div class="channel-avatar-circle">{avatar_html}</div>
              <div>
                <div class="channel-title-line">
                  {html.escape(c_name)}
                  <span class="badge-cdp-port">CDP Port {cdp_port}</span>
                </div>
                <div class="channel-subtitle-line">{html.escape(handle)} • Kênh ID: <code>{html.escape(cid)}</code></div>
              </div>
            </div>
          </div>
          <div class="cards-pair-grid">
            {''.join(cards_html)}
          </div>
        </div>
        """
        channel_blocks_html.append(block_html)

    # Review Tab Outer Pane
    review_pane_html = f"""
  <!-- ===================================================================== -->
  <!-- TAB 0: TRẠM DUYỆT VIDEO & GHI CHÚ SỬA LỖI (MANDATORY REVIEW GATE) -->
  <!-- ===================================================================== -->
  <div class="tab-pane active" id="tab-review">
    <div class="review-gate-section">
      <div class="review-header-card">
        <div class="review-header-title">
          <span>🎬</span> Trạm Duyệt Video & Ghi Chú Sửa Lỗi (Mandatory Review Gate — 20 Kênh × 2 Video)
        </div>
        <div class="review-header-desc">
          Quy trình kiểm duyệt bắt buộc trước khi phát hành lên YouTube Studio CDP. Chỉ những video có trạng thái
          <b>APPROVED (Đã duyệt)</b> mới được cấp phép tải lên tự động. Video <b>REJECTED</b> sẽ lưu chi tiết ghi chú lỗi
          để quy trình sửa tự động thực hiện tái sản xuất.
        </div>
      </div>

      <!-- Summary Counter Bar -->
      <div class="review-summary-grid">
        <div class="rev-stat-card stat-total">
          <div class="rev-stat-label">Tổng số video kiểm duyệt</div>
          <div class="rev-stat-value" id="counter-total">40</div>
          <div class="rev-stat-sub">20 Long 16:9 + 20 Short 9:16</div>
        </div>
        <div class="rev-stat-card stat-pending">
          <div class="rev-stat-label">⏳ Chờ duyệt (Pending)</div>
          <div class="rev-stat-value" id="counter-pending">0</div>
          <div class="rev-stat-sub">Cần người giám sát kiểm tra</div>
        </div>
        <div class="rev-stat-card stat-approved">
          <div class="rev-stat-label">✅ Đã duyệt - Sẵn sàng đăng</div>
          <div class="rev-stat-value" id="counter-approved">0</div>
          <div class="rev-stat-sub">Đã mở khóa xuất bản YouTube</div>
        </div>
        <div class="rev-stat-card stat-rejected">
          <div class="rev-stat-label">❌ Không duyệt - Chờ sửa</div>
          <div class="rev-stat-value" id="counter-rejected">0</div>
          <div class="rev-stat-sub">Có ghi chú yêu cầu tái tạo</div>
        </div>
      </div>

      <!-- Filter & Bulk Action Toolbar -->
      <div class="review-toolbar">
        <div class="review-filters-group">
          <div class="review-search-box">
            <span class="review-search-icon">🔍</span>
            <input type="text" class="review-search-input" id="review-search"
                   placeholder="Tìm nhanh theo kênh, tiêu đề, mã job, ghi chú..."
                   oninput="filterReviewCards()">
          </div>
          <select class="review-select-filter" id="review-status-filter" onchange="filterReviewCards()">
            <option value="all">Tất cả trạng thái duyệt</option>
            <option value="PENDING_REVIEW">⏳ Chờ duyệt (Pending)</option>
            <option value="APPROVED">✅ Đã duyệt (Approved)</option>
            <option value="REJECTED">❌ Không duyệt (Rejected)</option>
          </select>
          <select class="review-select-filter" id="review-format-filter" onchange="filterReviewCards()">
            <option value="all">Tất cả định dạng video</option>
            <option value="long_16x9">Long 16:9 Explainer</option>
            <option value="short_9x16">Short 9:16 Spin-off</option>
          </select>
        </div>
        <div class="review-actions-group">
          <button type="button" class="btn btn-primary" onclick="exportReviewDecisions()">
            💾 Lưu & Xuất Quyết Định Duyệt (review_decisions.json)
          </button>
          <button type="button" class="btn btn-secondary" onclick="copyApplyCommand()">
            📋 Copy Lệnh Áp Dụng & Tự Động Đăng / Sửa
          </button>
          <button type="button" class="btn btn-secondary btn-sm" onclick="resetReviewQueue()">
            ↺ Đặt lại
          </button>
        </div>
      </div>

      <!-- Channel Review Cards -->
      <div id="review-cards-container">
        {''.join(channel_blocks_html)}
      </div>
    </div>
  </div>
    """
    return review_pane_html


def build_review_dashboard(
    queue_path: Optional[Union[str, Path]] = None,
    output_paths: Optional[list[Union[str, Path]]] = None,
) -> list[Path]:
    """Generate and export the interactive Video Review Dashboard.

    Injects the Review Gate tab, styles, and scripts into the fleet dashboard HTML
    and writes to both brain and video directories.
    """
    q_path = Path(queue_path or DEFAULT_QUEUE_PATH).resolve()

    # Load review queue
    try:
        from tools.review_queue_manager import load_review_queue, sync_all_channel_runs
    except ImportError:
        from sys.tools.review_queue_manager import load_review_queue, sync_all_channel_runs

    queue_data = load_review_queue(q_path)
    if not queue_data.get("items") or len(queue_data.get("items", {})) < 40:
        logger.info("Review queue incomplete; synchronizing all 20 Vietnamese channels...")
        sync_all_channel_runs(batch_tag="batch3", queue_path=q_path)
        queue_data = load_review_queue(q_path)

    # Load channel map
    ch_map = {}
    if DEFAULT_MAP_PATH.is_file():
        try:
            ch_map = json.loads(DEFAULT_MAP_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Could not read youtube_channel_map.json: %s", e)

    # Base HTML template source
    try:
        from tools.dashboard_ui_template import get_dashboard_html

        base_html = get_dashboard_html()
    except ImportError:
        from sys.tools.dashboard_ui_template import get_dashboard_html

        base_html = get_dashboard_html()

    # 1. Inject Review CSS before </style>
    if "/* --- Video Review & Approval Gate Styles --- */" not in base_html:
        base_html = base_html.replace("</style>", f"{REVIEW_GATE_CSS}\n</style>")

    # 2. Inject Review Tab Button into tabs-group
    tab_btn_html = """        <button class="tab-btn active" id="btn-tab-review" onclick="switchTab('tab-review')">
          <span>🎬</span> Trạm Duyệt Video & Ghi Chú Sửa Lỗi (20 Kênh × 2 Video)
          <span class="tab-count" id="count-tab-review">40</span>
        </button>"""

    if "id=\"btn-tab-review\"" not in base_html:
        # Insert before btn-tab-fleet
        base_html = base_html.replace(
            '<button class="tab-btn active" id="btn-tab-fleet"',
            f'{tab_btn_html}\n        <button class="tab-btn" id="btn-tab-fleet"',
        )
        # Or if btn-tab-fleet was not active
        base_html = base_html.replace(
            '<button class="tab-btn" id="btn-tab-fleet"',
            f'{tab_btn_html}\n        <button class="tab-btn" id="btn-tab-fleet"',
        )

    # 3. Generate Review Tab Pane markup
    review_pane_markup = _build_review_gate_html(queue_data.get("items", {}), ch_map)

    # Replace existing tab-review or insert before tab-fleet
    if 'id="tab-review"' in base_html:
        import re

        base_html = re.sub(
            r'<div class="tab-pane[^"]*" id="tab-review">.*?</div>\s*</div>(?=\s*<!-- TOAST|\s*<div class="toast-container")',
            f"{review_pane_markup}\n</div>",
            base_html,
            flags=re.DOTALL,
        )
    else:
        # De-activate tab-fleet so tab-review is active default
        base_html = base_html.replace(
            '<div class="tab-pane active" id="tab-fleet">',
            f'{review_pane_markup}\n  <div class="tab-pane" id="tab-fleet">',
        )

    # 4. Patch switchTab in script
    if "'tab-review': 'btn-tab-review'" not in base_html:
        base_html = base_html.replace(
            "const btnMap = {",
            "const btnMap = {\n    'tab-review': 'btn-tab-review',",
        )

    # 5. Inject Queue JSON data script
    safe_queue_json = json.dumps(queue_data, ensure_ascii=False).replace("</", "<\\/")
    queue_script = f"""<script id="__REVIEW_QUEUE_DATA__" type="application/json">
{safe_queue_json}
</script>
<script>
{REVIEW_GATE_JS}
// Hook review queue initialization on DOM load
document.addEventListener('DOMContentLoaded', () => {{
  initReviewQueue();
}});
</script>"""

    if "__REVIEW_QUEUE_DATA__" in base_html:
        import re

        base_html = re.sub(
            r'<script id="__REVIEW_QUEUE_DATA__".*?</script>\s*<script>\s*// Hook review queue.*?document\.addEventListener\(.*?\);\s*\}\);?\s*</script>',
            queue_script,
            base_html,
            flags=re.DOTALL,
        )
    else:
        base_html = base_html.replace("</body>", f"{queue_script}\n</body>")

    # Determine destination paths
    dests = [Path(p).resolve() for p in (output_paths or DEFAULT_OUTPUT_PATHS)]
    written_paths = []

    for dest in dests:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(base_html, encoding="utf-8")
        logger.info("Successfully wrote review dashboard HTML to: %s (%d bytes)", dest, len(base_html))
        written_paths.append(dest)

    return written_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Video Pilot Interactive Video Review Dashboard")
    parser.add_argument("--queue", help="Path to video_review_queue.json override")
    parser.add_argument("--out", nargs="*", help="Optional output HTML destination paths")
    args = parser.parse_args()

    paths = build_review_dashboard(queue_path=args.queue, output_paths=args.out)
    print("\n=== REVIEW DASHBOARD GENERATED ===")
    for p in paths:
        print(f"✓ {p}")


if __name__ == "__main__":
    main()
