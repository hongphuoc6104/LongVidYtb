"""sys/tools/dashboard_ui_template.py

Scalable Enterprise Fleet & Video Catalog Web Interface (V3).
Self-contained HTML5 + CSS3 + Vanilla JS (zero CDN dependencies).
Engineered to manage hundreds or thousands of videos across 8+ channels and N batches.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Video Pilot V3 • Scalable YouTube Fleet & Video Catalog Manager</title>
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2306b6d4'><polygon points='5 3 19 12 5 21 5 3'/></svg>" type="image/svg+xml">
<style>
  :root {
    --bg-main: #070a13;
    --bg-surface: rgba(18, 26, 44, 0.75);
    --bg-surface-hover: rgba(26, 38, 64, 0.9);
    --bg-card-inner: rgba(12, 18, 32, 0.65);
    --border-color: rgba(255, 255, 255, 0.08);
    --border-hover: rgba(6, 182, 212, 0.35);

    --primary: #06b6d4;
    --primary-light: #22d3ee;
    --primary-glow: rgba(6, 182, 212, 0.2);

    --purple: #8b5cf6;
    --purple-light: #c084fc;
    --purple-bg: rgba(139, 92, 246, 0.12);
    --purple-border: rgba(139, 92, 246, 0.28);

    --rose: #f43f5e;
    --rose-light: #fb7185;
    --rose-bg: rgba(244, 63, 94, 0.12);
    --rose-border: rgba(244, 63, 94, 0.28);

    --emerald: #10b981;
    --emerald-light: #34d399;
    --emerald-bg: rgba(16, 185, 129, 0.12);
    --emerald-border: rgba(16, 185, 129, 0.28);

    --amber: #f59e0b;
    --amber-light: #fbbf24;
    --amber-bg: rgba(245, 158, 11, 0.12);
    --amber-border: rgba(245, 158, 11, 0.28);

    --text-white: #f8fafc;
    --text-gray: #cbd5e1;
    --text-muted: #94a3b8;
    --text-dim: #64748b;

    --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background-color: var(--bg-main);
    background-image:
      radial-gradient(circle at 10% 20%, rgba(6, 182, 212, 0.05), transparent 45%),
      radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.06), transparent 50%),
      radial-gradient(circle at 50% 50%, rgba(16, 185, 129, 0.03), transparent 60%);
    background-attachment: fixed;
    color: var(--text-gray);
    font-family: var(--font-stack);
    font-size: 14px;
    line-height: 1.5;
    min-height: 100vh;
    padding-bottom: 60px;
    -webkit-font-smoothing: antialiased;
  }

  a { color: var(--primary-light); text-decoration: none; transition: color 0.15s; }
  a:hover { color: #fff; text-decoration: underline; }

  /* Top command bar */
  .top-header {
    background: rgba(11, 17, 30, 0.85);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 1000;
  }

  .header-inner {
    max-width: 1720px;
    margin: 0 auto;
    padding: 14px 24px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
  }

  .brand-group {
    display: flex;
    align-items: center;
    gap: 14px;
  }

  .brand-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    background: linear-gradient(135deg, #06b6d4, #8b5cf6);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 14px var(--primary-glow);
    flex-shrink: 0;
  }

  .brand-icon svg {
    width: 22px;
    height: 22px;
    fill: #ffffff;
  }

  .brand-title {
    font-size: 18px;
    font-weight: 700;
    color: var(--text-white);
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.3px;
  }

  .v-badge {
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid var(--primary);
    color: var(--primary-light);
    font-size: 11px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 12px;
    letter-spacing: 0.5px;
  }

  .brand-subtitle {
    font-size: 12px;
    color: var(--text-muted);
  }

  .header-status-group {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
  }

  .live-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid var(--emerald-border);
    color: var(--emerald-light);
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: 600;
  }

  .live-dot {
    width: 8px;
    height: 8px;
    background: #10b981;
    border-radius: 50%;
    box-shadow: 0 0 8px #10b981;
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0% { transform: scale(0.95); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; }
    100% { transform: scale(0.95); opacity: 0.8; }
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 7px 14px;
    border-radius: 8px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s ease;
    border: 1px solid transparent;
    outline: none;
    user-select: none;
    white-space: nowrap;
  }

  .btn-primary {
    background: linear-gradient(135deg, #06b6d4, #0891b2);
    color: #ffffff;
    box-shadow: 0 4px 12px rgba(6, 182, 212, 0.25);
  }
  .btn-primary:hover {
    background: linear-gradient(135deg, #22d3ee, #06b6d4);
    box-shadow: 0 6px 16px rgba(6, 182, 212, 0.35);
    transform: translateY(-1px);
  }

  .btn-secondary {
    background: rgba(255, 255, 255, 0.05);
    border-color: var(--border-color);
    color: var(--text-white);
  }
  .btn-secondary:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(255, 255, 255, 0.2);
    color: #ffffff;
  }

  .btn-emerald {
    background: var(--emerald-bg);
    border-color: var(--emerald-border);
    color: var(--emerald-light);
  }
  .btn-emerald:hover {
    background: rgba(16, 185, 129, 0.22);
    border-color: var(--emerald);
  }

  .btn-sm {
    padding: 4px 9px;
    font-size: 11.5px;
    border-radius: 6px;
  }

  .btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none !important;
  }

  /* Main Container */
  .main-wrapper {
    max-width: 1720px;
    margin: 0 auto;
    padding: 24px;
  }

  /* 6 KPI Cards Grid */
  .kpi-grid {
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 16px;
    margin-bottom: 24px;
  }

  @media (max-width: 1400px) {
    .kpi-grid { grid-template-columns: repeat(3, 1fr); }
  }
  @media (max-width: 768px) {
    .kpi-grid { grid-template-columns: repeat(1, 1fr); }
  }

  .kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 16px;
    backdrop-filter: blur(12px);
    transition: transform 0.2s, border-color 0.2s;
    position: relative;
    overflow: hidden;
  }
  .kpi-card:hover {
    transform: translateY(-2px);
    border-color: var(--border-hover);
  }
  .kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, var(--primary), var(--purple));
    opacity: 0.8;
  }

  .kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .kpi-title {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .kpi-icon {
    font-size: 16px;
  }
  .kpi-value {
    font-size: 26px;
    font-weight: 800;
    color: var(--text-white);
    letter-spacing: -0.5px;
    margin-bottom: 4px;
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .kpi-delta {
    font-size: 12px;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 10px;
    background: var(--emerald-bg);
    color: var(--emerald-light);
    border: 1px solid var(--emerald-border);
  }
  .kpi-subtitle {
    font-size: 11.5px;
    color: var(--text-muted);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  /* Sticky Navigation & Global Filter Bar */
  .nav-filter-bar {
    background: rgba(14, 21, 37, 0.88);
    backdrop-filter: blur(16px);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 12px 18px;
    margin-bottom: 24px;
    position: sticky;
    top: 72px;
    z-index: 900;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .tabs-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    padding-bottom: 10px;
  }

  .tabs-group {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .tab-btn {
    background: transparent;
    border: 1px solid transparent;
    color: var(--text-muted);
    font-size: 13px;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.18s ease;
    display: inline-flex;
    align-items: center;
    gap: 8px;
  }
  .tab-btn:hover {
    color: var(--text-white);
    background: rgba(255, 255, 255, 0.05);
  }
  .tab-btn.active {
    color: var(--primary-light);
    background: rgba(6, 182, 212, 0.12);
    border-color: rgba(6, 182, 212, 0.3);
    box-shadow: 0 2px 10px rgba(6, 182, 212, 0.15);
  }
  .tab-count {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-white);
    font-size: 11px;
    font-weight: 700;
    padding: 1px 7px;
    border-radius: 10px;
  }
  .tab-btn.active .tab-count {
    background: var(--primary);
    color: #070a13;
  }

  .filters-row {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 10px;
  }

  .search-box {
    position: relative;
    flex: 1 1 260px;
    min-width: 220px;
  }
  .search-input {
    width: 100%;
    background: rgba(8, 12, 22, 0.7);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 32px 8px 34px;
    color: var(--text-white);
    font-size: 12.5px;
    outline: none;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .search-input:focus {
    border-color: var(--primary);
    box-shadow: 0 0 0 2px rgba(6, 182, 212, 0.2);
  }
  .search-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-dim);
    pointer-events: none;
  }
  .search-clear {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    background: none;
    border: none;
    color: var(--text-dim);
    cursor: pointer;
    font-size: 14px;
    display: none;
  }
  .search-clear:hover { color: #fff; }

  .select-filter {
    background: rgba(8, 12, 22, 0.7);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px 12px;
    color: var(--text-gray);
    font-size: 12.5px;
    outline: none;
    cursor: pointer;
    transition: border-color 0.15s;
  }
  .select-filter:focus {
    border-color: var(--primary);
  }
  .select-filter option {
    background: #0d1526;
    color: #fff;
  }

  /* Workspace Panes */
  .tab-pane {
    display: none;
    animation: fadeIn 0.2s ease-in-out;
  }
  .tab-pane.active {
    display: block;
  }

  @keyframes fadeIn {
    from { opacity: 0; transform: translateY(4px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* TAB 1: FLEET OVERVIEW */
  .fleet-bar-chart-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
  }

  .chart-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 10px;
  }
  .chart-title {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-white);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .batch-summary-pills {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
  }
  .batch-pill {
    background: var(--bg-card-inner);
    border: 1px solid var(--border-color);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: var(--text-gray);
  }
  .batch-pill b {
    color: var(--text-white);
  }

  .horizontal-chart-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px 24px;
  }
  @media (max-width: 900px) {
    .horizontal-chart-grid { grid-template-columns: 1fr; }
  }

  .chart-row {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .chart-row-label {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
  }
  .chart-row-name {
    font-weight: 600;
    color: var(--text-white);
  }
  .chart-row-views {
    color: var(--primary-light);
    font-weight: 700;
  }
  .chart-bar-bg {
    width: 100%;
    height: 10px;
    background: rgba(255, 255, 255, 0.05);
    border-radius: 6px;
    overflow: hidden;
    position: relative;
    display: flex;
  }
  .chart-bar-fill {
    height: 100%;
    transition: width 0.6s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .fill-long { background: linear-gradient(90deg, #8b5cf6, #a855f7); }
  .fill-short { background: linear-gradient(90deg, #f43f5e, #fb7185); }

  /* 8 Channel Cards Grid */
  .channels-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
  }
  @media (max-width: 1500px) {
    .channels-grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 800px) {
    .channels-grid { grid-template-columns: 1fr; }
  }

  .channel-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    backdrop-filter: blur(12px);
    transition: all 0.2s ease;
  }
  .channel-card:hover {
    border-color: var(--border-hover);
    box-shadow: 0 8px 24px rgba(6, 182, 212, 0.1);
  }

  .channel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
  }

  .channel-avatar {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid var(--primary);
    background: #1e293b;
    flex-shrink: 0;
  }
  .channel-avatar-fallback {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    background: linear-gradient(135deg, #06b6d4, #8b5cf6);
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 16px;
    flex-shrink: 0;
    border: 2px solid rgba(255, 255, 255, 0.2);
  }

  .channel-title-block {
    flex: 1;
    min-width: 0;
  }
  .channel-name {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-white);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .channel-handle {
    font-size: 11.5px;
    color: var(--text-muted);
  }
  .channel-handle a, .channel-name a {
    color: inherit;
    text-decoration: none;
    transition: color 0.15s ease;
  }
  .channel-handle a:hover, .channel-name a:hover {
    color: var(--primary-light);
    text-decoration: underline;
  }
  .channel-profile-tag {
    font-size: 10px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid var(--border-color);
    padding: 1px 6px;
    border-radius: 4px;
    color: var(--text-dim);
    margin-top: 2px;
    display: inline-block;
  }

  .channel-avatar-sm {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    object-fit: cover;
    border: 1.5px solid var(--primary);
    background: #1e293b;
    flex-shrink: 0;
  }

  .channel-account-strip {
    background: rgba(12, 18, 32, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 8px 10px;
    margin: 8px 0 12px;
    display: flex;
    flex-direction: column;
    gap: 5px;
    font-size: 11.5px;
  }
  .account-strip-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    flex-wrap: wrap;
  }
  .btn-copy-mini {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: var(--text-gray);
    border-radius: 4px;
    padding: 1px 6px;
    font-size: 10.5px;
    cursor: pointer;
    transition: all 0.15s;
    line-height: 1.4;
  }
  .btn-copy-mini:hover {
    background: var(--primary);
    color: #000;
    border-color: var(--primary);
  }
  .badge-wave {
    font-size: 10px;
    font-weight: 700;
    padding: 2px 7px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    letter-spacing: 0.3px;
  }
  .badge-wave-1 {
    background: rgba(6, 182, 212, 0.15);
    border: 1px solid var(--primary);
    color: var(--primary-light);
  }
  .badge-wave-2 {
    background: rgba(139, 92, 246, 0.15);
    border: 1px solid var(--purple);
    color: var(--purple-light);
  }
  .badge-wave-3 {
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid var(--amber);
    color: var(--amber-light);
  }
  .badge-wave-4 {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.6);
    color: #6ee7b7;
  }
  .badge-lang {
    font-size: 10px;
    font-weight: 700;
    padding: 2px 6px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    gap: 3px;
    letter-spacing: 0.3px;
  }
  .badge-lang-vi {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.5);
    color: #fca5a5;
  }
  .badge-lang-en {
    background: rgba(59, 130, 246, 0.15);
    border: 1px solid rgba(59, 130, 246, 0.5);
    color: #93c5fd;
  }
  .style-badge-swatch-wrap {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 6px;
    padding: 3px 8px;
    margin-top: 4px;
    max-width: 100%;
  }
  .swatch-dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
    flex-shrink: 0;
  }
  .new-channel-badge {
    background: rgba(16, 185, 129, 0.08);
    border: 1px dashed rgba(16, 185, 129, 0.4);
    color: var(--emerald-light);
    border-radius: 8px;
    padding: 14px 10px;
    text-align: center;
    font-size: 11.5px;
    font-weight: 600;
    margin: 8px 0;
  }
  .channel-ref-drawer-wrap {
    margin-top: 10px;
    margin-bottom: 12px;
  }
  .btn-ref-toggle {
    background: rgba(139, 92, 246, 0.12);
    border: 1px solid rgba(139, 92, 246, 0.3);
    color: var(--purple-light);
    border-radius: 7px;
    padding: 7px 11px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    width: 100%;
    text-align: left;
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: background 0.15s;
  }
  .btn-ref-toggle:hover {
    background: rgba(139, 92, 246, 0.22);
  }
  .ref-drawer-content {
    background: rgba(8, 12, 22, 0.95);
    border: 1px solid rgba(139, 92, 246, 0.25);
    border-radius: 7px;
    padding: 10px 12px;
    margin-top: 6px;
    font-size: 11.5px;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  .ref-section-title {
    font-weight: 700;
    color: var(--purple-light);
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }
  .ref-item-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 4px;
    margin-right: 4px;
  }
  .ref-platform-youtube { background: rgba(244, 63, 94, 0.2); color: #fb7185; }
  .ref-platform-tiktok { background: rgba(6, 182, 212, 0.2); color: #22d3ee; }
  .ref-platform-book { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
  .ref-format-badge { background: rgba(255, 255, 255, 0.1); color: #cbd5e1; }

  .channel-stats-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    background: var(--bg-card-inner);
    border-radius: 8px;
    padding: 8px 4px;
    margin-bottom: 12px;
    text-align: center;
    border: 1px solid rgba(255, 255, 255, 0.04);
  }
  .c-stat-col {
    display: flex;
    flex-direction: column;
  }
  .c-stat-label {
    font-size: 10px;
    color: var(--text-dim);
    text-transform: uppercase;
  }
  .c-stat-val {
    font-size: 13px;
    font-weight: 700;
    color: var(--text-white);
  }

  .top-video-banner {
    background: rgba(6, 182, 212, 0.07);
    border: 1px dashed rgba(6, 182, 212, 0.3);
    border-radius: 6px;
    padding: 6px 8px;
    margin-bottom: 12px;
    font-size: 11px;
    color: var(--primary-light);
    display: flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .top-video-banner b { color: #fff; }

  /* Bounded Collapsible Video List inside Channel Card */
  .channel-videos-wrapper {
    margin-bottom: 12px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }

  .mini-video-card {
    background: rgba(10, 15, 28, 0.8);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 8px;
    display: flex;
    gap: 10px;
    align-items: center;
    transition: border-color 0.15s;
  }
  .mini-video-card:hover {
    border-color: rgba(255, 255, 255, 0.2);
  }

  .mini-thumb-wrap {
    position: relative;
    width: 64px;
    height: 40px;
    border-radius: 5px;
    overflow: hidden;
    flex-shrink: 0;
    background: #000;
  }
  .mini-thumb-wrap.short-aspect {
    width: 32px;
    height: 48px;
  }
  .mini-thumb-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .mini-duration-badge {
    position: absolute;
    bottom: 2px;
    right: 2px;
    background: rgba(0, 0, 0, 0.85);
    color: #fff;
    font-size: 9px;
    font-weight: 600;
    padding: 1px 3px;
    border-radius: 3px;
  }

  .mini-meta {
    flex: 1;
    min-width: 0;
  }
  .mini-title {
    font-size: 11.5px;
    font-weight: 600;
    color: var(--text-white);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    margin-bottom: 2px;
  }
  .mini-sub {
    font-size: 10.5px;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
  }

  .badge-format {
    font-size: 9.5px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 4px;
    text-transform: uppercase;
  }
  .badge-format.long {
    background: var(--purple-bg);
    color: var(--purple-light);
    border: 1px solid var(--purple-border);
  }
  .badge-format.short {
    background: var(--rose-bg);
    color: var(--rose-light);
    border: 1px solid var(--rose-border);
  }

  .badge-funnel {
    font-size: 9.5px;
    font-weight: 600;
    padding: 1px 5px;
    border-radius: 4px;
  }
  .badge-funnel.linked {
    background: var(--emerald-bg);
    color: var(--emerald-light);
  }
  .badge-funnel.unlinked {
    background: var(--amber-bg);
    color: var(--amber-light);
  }

  /* Expandable drawer inside channel card */
  .collapsible-drawer {
    display: none;
    max-height: 280px;
    overflow-y: auto;
    padding-right: 4px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-top: 6px;
    border-top: 1px dashed var(--border-color);
    padding-top: 8px;
  }

  .channel-card-expand-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-top: 4px;
  }

  .btn-expand-toggle {
    background: transparent;
    border: 1px dashed rgba(255, 255, 255, 0.15);
    color: var(--primary-light);
    font-size: 11px;
    padding: 5px 8px;
    border-radius: 6px;
    cursor: pointer;
    flex: 1;
    text-align: center;
    transition: all 0.15s;
  }
  .btn-expand-toggle:hover {
    background: rgba(6, 182, 212, 0.1);
    border-color: var(--primary);
  }

  .channel-footer-actions {
    display: flex;
    align-items: center;
    gap: 6px;
    border-top: 1px solid var(--border-color);
    padding-top: 12px;
    margin-top: auto;
    flex-wrap: wrap;
  }
  .channel-footer-actions .btn {
    flex: 1 1 45%;
    justify-content: center;
    padding: 5px 8px;
    font-size: 11px;
  }

  /* TAB 2: MASTER PAGINATED CATALOG */
  .catalog-container {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    backdrop-filter: blur(14px);
    overflow: hidden;
  }

  .catalog-controls-bar {
    padding: 14px 20px;
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    background: rgba(14, 21, 37, 0.6);
  }

  .catalog-stats-info {
    font-size: 12.5px;
    color: var(--text-muted);
  }
  .catalog-stats-info b {
    color: var(--text-white);
  }

  .catalog-page-controls {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .table-responsive {
    width: 100%;
    overflow-x: auto;
  }

  .catalog-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    text-align: left;
  }

  .catalog-table th {
    background: rgba(10, 16, 28, 0.95);
    color: var(--text-muted);
    font-weight: 700;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.5px;
    padding: 12px 14px;
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    white-space: nowrap;
    user-select: none;
  }
  .catalog-table th.sortable {
    cursor: pointer;
  }
  .catalog-table th.sortable:hover {
    color: var(--primary-light);
  }

  .catalog-table td {
    padding: 12px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    color: var(--text-gray);
    vertical-align: middle;
  }
  .catalog-table tbody tr:hover {
    background: rgba(6, 182, 212, 0.04);
  }

  .cat-thumb-box {
    position: relative;
    width: 80px;
    height: 48px;
    border-radius: 6px;
    overflow: hidden;
    background: #000;
    display: inline-block;
    vertical-align: middle;
  }
  .cat-thumb-box.short-mode {
    width: 36px;
    height: 52px;
  }
  .cat-thumb-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  .cat-duration-tag {
    position: absolute;
    bottom: 2px;
    right: 2px;
    background: rgba(0, 0, 0, 0.85);
    color: #fff;
    font-size: 9px;
    font-weight: 600;
    padding: 1px 3px;
    border-radius: 3px;
  }

  .cat-title-cell {
    max-width: 320px;
  }
  .cat-video-title {
    font-weight: 600;
    color: var(--text-white);
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    line-height: 1.4;
    margin-bottom: 3px;
  }
  .cat-video-meta {
    font-size: 11px;
    color: var(--text-dim);
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .cat-video-id {
    font-family: monospace;
    color: var(--primary-light);
    cursor: pointer;
  }

  .views-bar-wrap {
    display: flex;
    flex-direction: column;
    gap: 3px;
    min-width: 90px;
  }
  .views-bar-val {
    font-weight: 700;
    color: var(--text-white);
  }
  .views-bar-track {
    width: 100%;
    height: 4px;
    background: rgba(255, 255, 255, 0.08);
    border-radius: 2px;
    overflow: hidden;
  }
  .views-bar-fill {
    height: 100%;
    background: linear-gradient(90deg, #06b6d4, #8b5cf6);
    border-radius: 2px;
  }

  .status-dot-active {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #10b981;
    margin-right: 5px;
  }
  .status-dot-unlisted {
    display: inline-block;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #f59e0b;
    margin-right: 5px;
  }

  /* Catalog Bottom Pagination */
  .catalog-pagination-bar {
    padding: 12px 20px;
    border-top: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
    background: rgba(14, 21, 37, 0.4);
  }

  .pagination-btns {
    display: flex;
    align-items: center;
    gap: 6px;
  }

  /* TAB 3: FUNNEL & BATCH ANALYTICS */
  .batch-cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }

  .batch-kpi-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    padding: 18px;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
  }
  .batch-kpi-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #f43f5e, #8b5cf6);
  }

  .batch-kpi-name {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-white);
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .batch-kpi-stats {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    font-size: 12px;
  }
  .b-stat {
    display: flex;
    flex-direction: column;
  }
  .b-stat-label {
    color: var(--text-dim);
    font-size: 10.5px;
    text-transform: uppercase;
  }
  .b-stat-val {
    font-weight: 700;
    color: var(--text-white);
    font-size: 14px;
  }

  /* Funnel Matrix Section */
  .funnel-pairs-container {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }

  .funnel-pair-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 16px 20px;
    backdrop-filter: blur(12px);
  }

  .pair-channel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border-color);
    margin-bottom: 14px;
    flex-wrap: wrap;
    gap: 8px;
  }
  .pair-ch-name {
    font-size: 14px;
    font-weight: 700;
    color: var(--text-white);
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .pair-grid {
    display: grid;
    grid-template-columns: 1fr 140px 1fr;
    gap: 16px;
    align-items: center;
  }
  @media (max-width: 900px) {
    .pair-grid { grid-template-columns: 1fr; gap: 12px; }
  }

  .funnel-video-box {
    background: var(--bg-card-inner);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    padding: 12px;
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .funnel-bridge-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    gap: 6px;
  }
  .bridge-arrow-icon {
    font-size: 20px;
    color: var(--emerald-light);
  }
  .bridge-status-pill {
    font-size: 10.5px;
    font-weight: 700;
    padding: 2px 8px;
    border-radius: 10px;
  }
  .bridge-ratio-text {
    font-size: 11px;
    color: var(--text-muted);
  }

  /* TAB 4: OPERATIONS & GROWTH HISTORY */
  .ops-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 24px;
  }
  @media (max-width: 1100px) {
    .ops-grid { grid-template-columns: 1fr; }
  }

  .ops-card {
    background: var(--bg-surface);
    border: 1px solid var(--border-color);
    border-radius: 14px;
    padding: 20px;
    backdrop-filter: blur(12px);
  }
  .ops-card-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--text-white);
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  /* CLI Generator Form */
  .cli-form-group {
    display: flex;
    flex-direction: column;
    gap: 6px;
    margin-bottom: 12px;
  }
  .cli-label {
    font-size: 11.5px;
    color: var(--text-muted);
    font-weight: 600;
  }
  .cli-output-box {
    background: #050810;
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 8px;
    padding: 12px;
    font-family: monospace;
    font-size: 12.5px;
    color: #38bdf8;
    word-break: break-all;
    position: relative;
    margin-top: 10px;
  }

  /* History Table */
  .history-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }
  .history-table th {
    background: rgba(10, 16, 28, 0.8);
    color: var(--text-muted);
    padding: 8px 10px;
    text-align: left;
    font-size: 10.5px;
    border-bottom: 1px solid var(--border-color);
  }
  .history-table td {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  }

  /* CDP Ports Table */
  .cdp-ports-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }
  .cdp-ports-table th {
    background: rgba(10, 16, 28, 0.8);
    color: var(--text-muted);
    padding: 8px 10px;
    text-align: left;
    border-bottom: 1px solid var(--border-color);
  }
  .cdp-ports-table td {
    padding: 8px 10px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.04);
    vertical-align: middle;
  }

  /* Toast Notification */
  .toast-container {
    position: fixed;
    bottom: 24px;
    right: 24px;
    z-index: 99999;
    display: flex;
    flex-direction: column;
    gap: 8px;
    pointer-events: none;
  }

  .toast-msg {
    pointer-events: auto;
    background: rgba(15, 23, 42, 0.95);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 12px 18px;
    color: #fff;
    font-size: 13px;
    font-weight: 500;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6);
    display: flex;
    align-items: center;
    gap: 10px;
    animation: toastIn 0.25s ease-out;
    max-width: 400px;
  }
  .toast-msg.success { border-color: var(--emerald); }
  .toast-msg.error { border-color: var(--rose); }
  .toast-msg.info { border-color: var(--primary); }

  @keyframes toastIn {
    from { transform: translateY(12px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
  }

  /* Spinners */
  .spinner {
    width: 14px;
    height: 14px;
    border: 2px solid rgba(255, 255, 255, 0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    display: inline-block;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  /* Glass Scrollbar */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.2); }
  ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.15); border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(6, 182, 212, 0.4); }

  /* SIMPLE COMMAND CENTER (38 CHANNELS MANAGEMENT & PRODUCTION) */
  .simple-hub-wrapper {
    background: linear-gradient(180deg, rgba(15, 23, 42, 0.92), rgba(10, 15, 28, 0.95));
    border: 1.5px solid rgba(6, 182, 212, 0.35);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 24px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
  }
  .simple-hub-header {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    margin-bottom: 18px;
  }
  .simple-modes-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-bottom: 18px;
  }
  @media (max-width: 1200px) {
    .simple-modes-grid { grid-template-columns: 1fr; }
  }
  .simple-mode-card {
    background: rgba(18, 28, 48, 0.85);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: border-color 0.2s, transform 0.15s;
  }
  .simple-mode-card:hover {
    border-color: var(--primary);
    transform: translateY(-1px);
  }
  .simple-mode-title {
    font-size: 14px;
    font-weight: 800;
    color: var(--text-white);
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
  }
  .simple-mode-desc {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.4;
  }
  .simple-queue-bar {
    background: rgba(6, 182, 212, 0.08);
    border: 1px solid rgba(6, 182, 212, 0.3);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 18px;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .simple-filter-pills {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 14px;
  }
  .simple-pill-btn {
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    color: var(--text-gray);
    border-radius: 20px;
    padding: 6px 13px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s;
  }
  .simple-pill-btn:hover, .simple-pill-btn.active {
    background: var(--primary);
    border-color: var(--primary-light);
    color: #031525;
    font-weight: 700;
  }
  .verdict-badge {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 800;
  }
  .verdict-SCALE { background: rgba(16, 185, 129, 0.18); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.45); }
  .verdict-ITERATE { background: rgba(245, 158, 11, 0.18); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.45); }
  .verdict-REPAIR_FUNNEL { background: rgba(244, 63, 94, 0.18); color: #fb7185; border: 1px solid rgba(244, 63, 94, 0.45); }
  .verdict-COLLECT { background: rgba(6, 182, 212, 0.16); color: #22d3ee; border: 1px solid rgba(6, 182, 212, 0.4); }
</style>
</head>
<body>

<!-- TOP COMMAND BAR -->
<header class="top-header">
  <div class="header-inner">
    <div class="brand-group">
      <div class="brand-icon">
        <svg viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
      </div>
      <div>
        <div class="brand-title">
          Video Pilot — Hệ Thống Điều Hành 38 Kênh
          <span class="v-badge">FLEET COMMAND V4</span>
        </div>
        <div class="brand-subtitle">Điều Phối Sản Xuất Song Song · AI Chẩn Đoán & Cải Thiện Liên Tục 38 Kênh (20 VN + 18 EN)</div>
      </div>
    </div>

    <div class="header-status-group">
      <div class="live-pill" id="header-live-badge">
        <span class="live-dot"></span>
        <span id="header-fleet-status">38/38 Kênh Active</span>
      </div>
      <div style="color: var(--text-muted); font-size: 11.5px;" id="header-updated-at">
        Cập nhật: --:--
      </div>
    </div>

    <div class="header-actions">
      <button class="btn btn-emerald" id="btn-goto-review" onclick="switchTab('tab-review')" style="background: linear-gradient(135deg, #10b981, #059669); color: #fff; font-weight: 800; box-shadow: 0 0 14px rgba(16, 185, 129, 0.35);">
        <span>✅</span> Duyệt Đăng Video Mới (<span id="header-review-count">40</span>)
      </button>
      <button class="btn btn-primary" id="btn-refresh" onclick="refreshMetrics()">
        <span>↻</span> Làm mới chỉ số (Live Scrape)
      </button>
      <button class="btn btn-secondary" id="btn-sync" onclick="syncChannelMap()">
        <span>🔄</span> Đồng bộ Video Mới
      </button>
      <button class="btn btn-emerald" id="btn-export-csv" onclick="exportCatalogCSV()">
        <span>📥</span> Xuất CSV Kho Video
      </button>
    </div>
  </div>
</header>

<div class="main-wrapper">

  <!-- 4 COMPACT HIGH-SIGNAL KPI SUMMARY CARDS -->
  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Hệ Thống Kênh</span>
        <span class="kpi-icon">🏢</span>
      </div>
      <div class="kpi-value" id="kpi-channels">38 / 38</div>
      <div class="kpi-subtitle" id="kpi-channels-subtitle">20 Kênh Việt · 18 Kênh Anh</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Tổng Kho Video</span>
        <span class="kpi-icon">🎬</span>
      </div>
      <div class="kpi-value" id="kpi-videos">0</div>
      <div class="kpi-subtitle" id="kpi-videos-split">0 Long 16:9 · 0 Short 9:16</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Tổng Lượt Xem & Tương Tác</span>
        <span class="kpi-icon">👁️</span>
      </div>
      <div class="kpi-value">
        <span id="kpi-views">0</span>
        <span class="kpi-delta" id="kpi-views-delta" style="display:none;">+0</span>
      </div>
      <div class="kpi-subtitle" id="kpi-views-split">Shorts: 0 · Longs: 0</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Chuẩn Phễu & Duyệt Bài</span>
        <span class="kpi-icon">🔗</span>
      </div>
      <div class="kpi-value" id="kpi-funnel">100%</div>
      <div class="kpi-subtitle" id="kpi-funnel-sub">0/0 Shorts gắn Related Long</div>
    </div>
  </section>

  <!-- STICKY 4-TAB WORKSPACE NAVIGATION BAR -->
  <nav class="nav-filter-bar">
    <div class="tabs-row" style="margin-bottom: 0;">
      <div class="tabs-group">
        <button class="tab-btn active" id="btn-tab-fleet" onclick="switchTab('tab-fleet')">
          <span>⚡</span> 1. Điều Phối & Sản Xuất 38 Kênh
          <span class="tab-count" id="count-tab-fleet">38</span>
        </button>
        <button class="tab-btn" id="btn-tab-review" onclick="switchTab('tab-review')" style="border-color: rgba(16, 185, 129, 0.55); background: rgba(16, 185, 129, 0.12); color: #34d399; font-weight: 700;">
          <span>✅</span> 2. Duyệt Đăng Video Mới
          <span class="tab-count" id="count-tab-review" style="background: #10b981; color: #022c22; font-weight: 800;">40</span>
        </button>
        <button class="tab-btn" id="btn-tab-catalog" onclick="switchTab('tab-catalog')">
          <span>🎬</span> 3. Kho Video Đã Đăng
          <span class="tab-count" id="count-tab-catalog">0</span>
        </button>
        <button class="tab-btn" id="btn-tab-refs" onclick="switchTab('tab-refs')">
          <span>📚</span> 4. Hồ Sơ Kênh Mẫu & Tài Khoản
          <span class="tab-count" id="count-tab-refs">38</span>
        </button>
      </div>
    </div>
  </nav>

  <!-- ===================================================================== -->
  <!-- TAB 1: ĐIỀU PHỐI & SẢN XUẤT 38 KÊNH (PRIMARY COMMAND HUB)              -->
  <!-- ===================================================================== -->
  <div class="tab-pane active" id="tab-fleet">
    <section class="simple-hub-wrapper" id="simple-command-hub">
      <div class="simple-hub-header">
        <div>
          <div style="font-size: 18px; font-weight: 800; color: #f8fafc; display: flex; align-items: center; gap: 10px;">
            <span>⚡</span> Trung Tâm Điều Phối & Sản Xuất 38 Kênh (20 VN + 18 EN)
            <span class="v-badge" id="simple-38-badge">38 Kênh</span>
          </div>
          <div style="font-size: 12.5px; color: var(--text-muted); margin-top: 3px;">
            3 chế độ sản xuất tự động (1 Kênh · Ca 3–4 Kênh Song Song · Cuốn Chiếu 38 Kênh) kết hợp AI Chẩn Đoán & Cải Thiện Liên Tục.
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <button class="btn btn-primary btn-sm" onclick="runFleetDiagnosisNow()">
            🧠 Chẩn Đoán Lại 38 Kênh
          </button>
        </div>
      </div>

      <!-- 3 PRODUCTION MODES BAR -->
      <div class="simple-modes-grid">
        <!-- MODE 1: SINGLE CHANNEL -->
        <div class="simple-mode-card">
          <div class="simple-mode-title">
            <span>1️⃣ Chạy Chuyên Sâu 1 Kênh</span>
            <span class="v-badge">--mode single</span>
          </div>
          <div class="simple-mode-desc">
            Đọc Analytics ➔ Đồng bộ/Sửa Studio ➔ Sản xuất 1 cặp Long + Short chất lượng cao cho kênh được chọn.
          </div>
          <div style="display: flex; gap: 8px; margin-top: auto; flex-wrap: wrap;">
            <select class="select-filter" id="simple-single-channel" style="flex: 1; min-width: 150px;" onchange="updateSimpleCommandPreview('single')">
              <option value="ho_so_ky_la">Hồ Sơ Kỳ Lạ (ho_so_ky_la)</option>
            </select>
            <select class="select-filter" id="simple-single-action" onchange="updateSimpleCommandPreview('single')">
              <option value="bundle">Trọn bộ (1 Long + Short)</option>
              <option value="analytics">Quét Analytics & Chẩn đoán</option>
              <option value="studio_sync">Đồng bộ & Phễu Studio</option>
              <option value="short_only">Chỉ tạo Short 9:16</option>
            </select>
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-primary btn-sm" style="flex: 1; justify-content: center;" onclick="triggerSimpleFleetAction('single')">
              ▶ Thực Thi Kênh Này
            </button>
            <button class="btn btn-secondary btn-sm" onclick="copySimpleModeCmd('single')">
              📋 Copy Lệnh
            </button>
          </div>
        </div>

        <!-- MODE 2: WAVE 3-4 CHANNELS PARALLEL -->
        <div class="simple-mode-card">
          <div class="simple-mode-title">
            <span>2️⃣ Chạy 1 Ca 3–4 Kênh Song Song</span>
            <span class="v-badge" style="border-color: var(--purple); color: var(--purple-light);">--mode wave</span>
          </div>
          <div class="simple-mode-desc">
            Chạy 3–4 kênh cùng lúc (6–8 video/ca): tận dụng song song Colab T4 (TTS/NVENC) và bể Chrome Flow CDP.
          </div>
          <div style="display: flex; gap: 8px; margin-top: auto; flex-wrap: wrap;">
            <select class="select-filter" id="simple-wave-preset" style="flex: 1;" onchange="onWavePresetChange(this.value)">
              <option value="checked">Các kênh đang tick chọn ở bảng dưới (<span id="checked-count-lbl">4</span>)</option>
              <option value="tier_a_top4">Top 4 Kênh Mũi Nhọn (Tier-A)</option>
              <option value="scale_top4">Top 4 Kênh Đang Thắng (SCALE)</option>
              <option value="repair_top4">4 Kênh Cần Gắn Phễu (REPAIR)</option>
            </select>
            <select class="select-filter" id="simple-wave-size" onchange="updateSimpleCommandPreview('wave')">
              <option value="4" selected>4 kênh / ca</option>
              <option value="3">3 kênh / ca</option>
            </select>
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-primary btn-sm" style="flex: 1; justify-content: center; background: linear-gradient(135deg, #8b5cf6, #6d28d9);" onclick="triggerSimpleFleetAction('wave')">
              ⚡ Chạy 1 Ca
            </button>
            <button class="btn btn-secondary btn-sm" onclick="copySimpleModeCmd('wave')">
              📋 Copy Lệnh
            </button>
          </div>
        </div>

        <!-- MODE 3: ROLLING AUTO-QUEUE ALL 38 CHANNELS -->
        <div class="simple-mode-card">
          <div class="simple-mode-title">
            <span>3️⃣ Dây Chuyền Cuốn Chiếu 38 Kênh</span>
            <span class="v-badge" style="border-color: var(--emerald); color: var(--emerald-light);">--mode auto-queue</span>
          </div>
          <div class="simple-mode-desc">
            Ra 1 lệnh duy nhất: Tự động chia 38 kênh thành từng cụm 3–4 kênh, xong cụm 1 tự nạp cụm 2 cho đến hết.
          </div>
          <div style="display: flex; gap: 8px; margin-top: auto; flex-wrap: wrap;">
            <select class="select-filter" id="simple-queue-scope" style="flex: 1;" onchange="updateSimpleCommandPreview('auto_queue')">
              <option value="all">Toàn bộ 38 Kênh (10 Ca × 4 kênh)</option>
              <option value="vi">20 Kênh Tiếng Việt (5 Ca × 4 kênh)</option>
              <option value="en">18 Kênh Tiếng Anh (5 Ca × 4 kênh)</option>
              <option value="tier_a">Nhóm Mũi Nhọn Tier-A</option>
            </select>
          </div>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-emerald btn-sm" style="flex: 1; justify-content: center; background: #10b981; color: #022c22; font-weight: 800;" onclick="triggerSimpleFleetAction('auto_queue')">
              🔄 Bắt Đầu Cuốn Chiếu
            </button>
            <button class="btn btn-secondary btn-sm" onclick="copySimpleModeCmd('auto_queue')">
              📋 Copy Lệnh
            </button>
          </div>
        </div>
      </div>

      <!-- ACTIVE COMMAND & QUEUE STATUS BAR -->
      <div class="simple-queue-bar" id="simple-queue-status-bar">
        <div style="flex: 1; min-width: 260px;">
          <div style="font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--primary-light); font-weight: 800; margin-bottom: 3px;" id="simple-queue-status-title">
            ⚡ LỆNH THỰC THI SẴN SÀNG (CLI / AI COMMAND):
          </div>
          <code style="font-size: 12.5px; color: #f8fafc; word-break: break-all;" id="simple-cmd-preview-box">
            cd /home/hongphuoc6104/Desktop/vp-agent-core && python3 sys/tools/vp_fleet_manager.py --mode auto-queue --channels all --wave-size 4
          </code>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
          <span style="font-size: 12px; color: var(--emerald-light); font-weight: 700;" id="simple-queue-waves-summary">
            Sẵn sàng điều phối 38 kênh
          </span>
          <button class="btn btn-primary btn-sm" onclick="copyText(document.getElementById('simple-cmd-preview-box').innerText, '✓ Đã copy lệnh!')">
            📋 Sao Chép Lệnh
          </button>
        </div>
      </div>

      <!-- LIVE ACTION FEEDBACK & CHANNEL DIAGNOSIS PANEL -->
      <div id="simple-action-result-panel" style="display: none; background: rgba(15, 23, 42, 0.94); border: 1.5px solid rgba(16, 185, 129, 0.45); border-radius: 12px; padding: 14px 16px; margin-bottom: 18px;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; flex-wrap: wrap; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 10px; margin-bottom: 10px;">
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            <span style="font-size: 14px; font-weight: 800; color: #34d399;" id="simple-result-title">🚀 KẾT QUẢ ĐIỀU PHỐI & CHẨN ĐOÁN</span>
            <span class="v-badge" id="simple-result-conn-badge">Sẵn sàng</span>
          </div>
          <div style="display: flex; align-items: center; gap: 8px;">
            <button class="btn btn-secondary btn-sm" onclick="copyServerCommand()">🖥️ Copy Lệnh Mở Server (:8765)</button>
            <button class="btn btn-secondary btn-sm" onclick="document.getElementById('simple-action-result-panel').style.display='none'">✕ Đóng</button>
          </div>
        </div>
        <div id="simple-result-body" style="font-size: 12.5px; color: var(--text-gray); line-height: 1.55;"></div>
      </div>

      <!-- QUICK FILTER PILLS FOR 38 CHANNELS TABLE -->
      <div class="simple-filter-pills">
        <button class="simple-pill-btn active" id="spill-all" onclick="setSimpleFilter('all')">
          🌐 Tất cả (38 Kênh)
        </button>
        <button class="simple-pill-btn" id="spill-vi" onclick="setSimpleFilter('vi')">
          🇻🇳 20 Kênh Việt
        </button>
        <button class="simple-pill-btn" id="spill-en" onclick="setSimpleFilter('en')">
          🇺🇸 18 Kênh Anh
        </button>
        <button class="simple-pill-btn" id="spill-tier_a" onclick="setSimpleFilter('tier_a')">
          🔥 Mũi Nhọn (Tier-A)
        </button>
        <button class="simple-pill-btn" id="spill-SCALE" onclick="setSimpleFilter('SCALE')">
          🟢 SCALE (Đang thắng)
        </button>
        <button class="simple-pill-btn" id="spill-REPAIR_FUNNEL" onclick="setSimpleFilter('REPAIR_FUNNEL')">
          🔧 Cần Gắn Phễu Short→Long
        </button>
        <button class="simple-pill-btn" id="spill-ITERATE" onclick="setSimpleFilter('ITERATE')">
          🟡 ITERATE (Đổi Hook/Thumb)
        </button>

        <div style="margin-left: auto; display: flex; align-items: center; gap: 8px;">
          <input type="text" class="search-input" id="simple-search-input"
                 placeholder="Tìm nhanh trong 38 kênh..."
                 style="width: 210px; padding: 6px 12px; font-size: 12px;"
                 oninput="onSimpleSearch(this.value)">
          <button class="btn btn-secondary btn-sm" onclick="selectTop4FilteredForWave()">
            ☑️ Chọn 4 Kênh Đầu Vào Ca
          </button>
        </div>
      </div>

      <!-- COMPACT 38-CHANNEL MANAGEMENT & PRODUCTION TABLE -->
      <div class="table-responsive" style="max-height: 580px; overflow-y: auto; border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;">
        <table class="catalog-table" id="simple-38-channels-table">
          <thead>
            <tr>
              <th style="width: 42px; text-align: center;">Ca</th>
              <th style="width: 265px;">Kênh, Email & CDP</th>
              <th style="width: 155px;">Chỉ Số Thực Tế</th>
              <th style="width: 145px;">Phễu & Duyệt</th>
              <th>🧠 AI Chẩn Đoán & Đề Tài Cải Thiện Liên Tục</th>
              <th style="text-align: right; width: 220px;">Sản Xuất & Quản Lý 1-Click</th>
            </tr>
          </thead>
          <tbody id="simple-38-table-body">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </div>
    </section>
  </div>

  <!-- ===================================================================== -->
  <!-- TAB 2: DUYỆT ĐĂNG VIDEO MỚI & GHI CHÚ SỬA LỖI (PRE-PUBLISH GATE)      -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-review">
    <div class="catalog-container" style="padding: 18px;">
      <div style="display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 16px; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 14px;">
        <div>
          <div style="font-size: 16px; font-weight: 800; color: var(--text-white); display: flex; align-items: center; gap: 8px;">
            <span>🛡️</span> Cổng Duyệt Đăng Video Mới & Ghi Chú Lỗi Cần Sửa (Pre-Publish Gate)
          </div>
          <div style="font-size: 12px; color: var(--text-muted); margin-top: 4px;">
            Tất cả video mới tạo phải được bấm <b>"✅ Duyệt đăng (APPROVED)"</b> mới được đăng lên YouTube. Video bấm <b>"❌ Không duyệt / Cần sửa (REJECTED)"</b> sẽ bị chặn đăng và đọc ghi chú để sửa lại.
          </div>
        </div>

        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 8px;">
          <select class="select-filter" id="review-status-filter" onchange="onReviewStatusFilterChange(this.value)">
            <option value="all">Tất cả trạng thái duyệt (40)</option>
            <option value="PENDING_REVIEW">⏳ Đang chờ duyệt (PENDING_REVIEW)</option>
            <option value="APPROVED">✅ Đã duyệt đăng (APPROVED)</option>
            <option value="REJECTED">❌ Không duyệt / Cần sửa (REJECTED)</option>
          </select>

          <button class="btn btn-emerald btn-sm" onclick="approveAllFilteredReviewVideos()" style="background: #10b981; color: #022c22; font-weight: 800;">
            ✅ Duyệt Tất Cả Đang Lọc
          </button>
          <button class="btn btn-primary btn-sm" onclick="exportReviewDecisionsJSON()">
            💾 Xuất File Quyết Định (review_decisions.json)
          </button>
        </div>
      </div>

      <!-- Review Summary Counters -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-bottom: 18px;">
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(255,255,255,0.08); border-radius: 10px; padding: 12px 16px;">
          <div style="font-size: 11.5px; color: var(--text-muted);">Tổng Video Trong Hàng Đợi</div>
          <div style="font-size: 22px; font-weight: 800; color: var(--text-white); margin-top: 4px;" id="rev-stat-total">40</div>
        </div>
        <div style="background: rgba(245, 158, 11, 0.08); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 10px; padding: 12px 16px;">
          <div style="font-size: 11.5px; color: #fbbf24;">⏳ Chờ Duyệt (PENDING_REVIEW)</div>
          <div style="font-size: 22px; font-weight: 800; color: #fbbf24; margin-top: 4px;" id="rev-stat-pending">40</div>
        </div>
        <div style="background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 10px; padding: 12px 16px;">
          <div style="font-size: 11.5px; color: #34d399;">✅ Đã Duyệt Đăng (APPROVED)</div>
          <div style="font-size: 22px; font-weight: 800; color: #34d399; margin-top: 4px;" id="rev-stat-approved">0</div>
        </div>
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 10px; padding: 12px 16px;">
          <div style="font-size: 11.5px; color: #f87171;">❌ Không Duyệt / Cần Sửa (REJECTED)</div>
          <div style="font-size: 22px; font-weight: 800; color: #f87171; margin-top: 4px;" id="rev-stat-rejected">0</div>
        </div>
      </div>

      <!-- Review Video Cards Grid -->
      <div id="review-cards-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(430px, 1fr)); gap: 16px;">
        <!-- Rendered via JS -->
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- TAB 3: KHO VIDEO ĐÃ ĐĂNG TOÀN HỆ THỐNG (MASTER PAGINATED CATALOG)     -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-catalog">
    <div class="catalog-container" style="padding: 14px 16px; margin-bottom: 14px;">
      <div class="filters-row">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input type="text" class="search-input" id="filter-search"
                 placeholder="Tìm nhanh theo tên kênh, @handle, email, ngách, video ID, đợt..."
                 oninput="onSearchInput(this.value)">
          <button class="search-clear" id="search-clear-btn" onclick="clearSearch()">✕</button>
        </div>

        <select class="select-filter" id="filter-wave" onchange="onFilterChange()">
          <option value="all">Tất cả Đợt Kênh (Wave 1, 2, 3, 4)</option>
          <option value="1">Wave 1 — 8 Kênh Gốc</option>
          <option value="2">Wave 2 — 8 Kênh Mở Rộng</option>
          <option value="3">Wave 3 — 4 Kênh Tâm Linh & Minh Triết</option>
          <option value="4">Wave 4 — 19 Kênh Tiếng Anh Quốc Tế</option>
        </select>

        <select class="select-filter" id="filter-lang" onchange="onFilterChange()">
          <option value="all">🌐 Tất cả ngôn ngữ</option>
          <option value="vi">🇻🇳 Tiếng Việt (VN)</option>
          <option value="en">🇺🇸 Tiếng Anh Quốc Tế (EN)</option>
        </select>

        <select class="select-filter" id="filter-style" onchange="onFilterChange()">
          <option value="all">🎨 Tất cả 10 Hệ Mỹ Thuật</option>
          <option value="stickman_doodle">1. Indie Doodle Stickman</option>
          <option value="noir_dossier">2. 2D Noir & Red-String Dossier</option>
          <option value="kawaii_sticker">3. Kawaii Mascots & Sticker-Pop</option>
          <option value="pastel_duo">4. Pastel Warm-Line Duo</option>
          <option value="tactical_atlas">5. 2D Tactical Cartography (Maps)</option>
          <option value="cosmos_vector">6. Deep-Space Geometric Vector</option>
          <option value="blueprint_ledger">7. Ledger, Blueprint & Swiss Infographic</option>
          <option value="editorial_risograph">8. Editorial Risograph Print</option>
          <option value="zen_sumie">9. Sumi-e Zen Ink Wash</option>
          <option value="woodcut_gouache">10. Woodblock Print & Night Gouache</option>
        </select>

        <select class="select-filter" id="filter-channel" onchange="onFilterChange()">
          <option value="all">Tất cả Kênh</option>
        </select>

        <select class="select-filter" id="filter-batch" onchange="onFilterChange()">
          <option value="all">Tất cả Đợt Sản Xuất</option>
        </select>

        <select class="select-filter" id="filter-format" onchange="onFilterChange()">
          <option value="all">Tất cả Định dạng</option>
          <option value="long">Long 16:9 Explainer</option>
          <option value="short">Short 9:16 Spin-off</option>
        </select>

        <select class="select-filter" id="filter-sort" onchange="onFilterChange()">
          <option value="views_desc">Lượt xem: Cao → Thấp</option>
          <option value="published_desc">Mới xuất bản nhất</option>
          <option value="views_asc">Lượt xem: Thấp → Cao</option>
          <option value="likes_desc">Lượt thích: Cao → Thấp</option>
          <option value="engagement_desc">Tỷ lệ tương tác (Likes/Views)</option>
          <option value="channel_name_asc">Tên kênh: A → Z</option>
          <option value="wave_asc">Đợt kênh (Wave 1 → 3)</option>
          <option value="cdp_port_asc">Cổng CDP</option>
        </select>

        <button class="btn btn-secondary btn-sm" onclick="resetAllFilters()">
          ↺ Đặt lại lọc
        </button>
      </div>
    </div>

    <div class="catalog-container">
      <div class="catalog-controls-bar">
        <div class="catalog-stats-info" id="catalog-page-summary">
          Hiển thị <b>0</b> trong tổng số <b>0</b> video
        </div>

        <div class="catalog-page-controls">
          <label style="font-size: 11.5px; color: var(--text-muted);">Hiển thị mỗi trang:</label>
          <select class="select-filter" id="catalog-page-size" onchange="onPageSizeChange(this.value)">
            <option value="10">10 video</option>
            <option value="20" selected>20 video</option>
            <option value="50">50 video</option>
            <option value="100">100 video</option>
            <option value="all">Tất cả</option>
          </select>

          <button class="btn btn-secondary btn-sm" id="btn-page-prev" onclick="changePage(-1)">‹ Trước</button>
          <span style="font-size: 12px; font-weight: 600; color: var(--text-white);" id="catalog-page-indicator">Trang 1 / 1</span>
          <button class="btn btn-secondary btn-sm" id="btn-page-next" onclick="changePage(1)">Sau ›</button>
        </div>
      </div>

      <div class="table-responsive">
        <table class="catalog-table">
          <thead>
            <tr>
              <th style="width: 100px;"># & Thumbnail</th>
              <th class="sortable" onclick="setSort('title_asc')">Tiêu Đề Video & Mã ID ↕</th>
              <th class="sortable" onclick="setSort('channel_name_asc')">Kênh & Cổng CDP ↕</th>
              <th>Đợt & Ngày Đăng</th>
              <th>Định Dạng & Phễu</th>
              <th class="sortable" onclick="setSort('views_desc')">Lượt Xem ↕</th>
              <th class="sortable" onclick="setSort('likes_desc')">Lượt Thích & Tương Tác ↕</th>
              <th>Trạng Thái</th>
              <th style="text-align: right;">Thao Tác</th>
            </tr>
          </thead>
          <tbody id="catalog-table-body">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </div>

      <div class="catalog-pagination-bar">
        <div style="font-size: 12px; color: var(--text-muted);" id="catalog-bottom-summary">
          Tổng số 0 video
        </div>
        <div class="pagination-btns">
          <button class="btn btn-secondary btn-sm" onclick="goToPage(1)">« Đầu</button>
          <button class="btn btn-secondary btn-sm" onclick="changePage(-1)">‹ Trước</button>
          <span style="font-size: 12px; font-weight: 600; padding: 0 8px; color: var(--text-white);" id="catalog-bottom-page-indicator">1 / 1</span>
          <button class="btn btn-secondary btn-sm" onclick="changePage(1)">Sau ›</button>
          <button class="btn btn-secondary btn-sm" id="btn-page-last" onclick="goToLastPage()">Cuối »</button>
        </div>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- TAB 4: HỒ SƠ KÊNH MẪU, TÀI KHOẢN GOOGLE & ĐỀ TÀI HẠT GIỐNG            -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-refs">
    <div class="catalog-container">
      <div class="catalog-controls-bar">
        <div class="catalog-stats-info" style="font-size: 14px; font-weight: 700; color: var(--text-white); display: flex; align-items: center; gap: 8px;">
          <span>📚 Hồ Sơ Kênh Mẫu, Tài Khoản Google, Cổng CDP & Đề Tài Hạt Giống (38 Kênh)</span>
          <span class="v-badge" id="references-count-badge">38 Kênh</span>
        </div>
        <div style="font-size: 12px; color: var(--text-muted);">
          Đồng bộ trực tiếp từ SSOT <code>sys/channels/registry.py</code> & <code>youtube_channel_map.json</code>
        </div>
      </div>

      <div class="table-responsive">
        <table class="catalog-table">
          <thead>
            <tr>
              <th style="width: 220px;">Kênh & Đợt (Wave)</th>
              <th style="width: 240px;">Tài Khoản Google & CDP</th>
              <th style="width: 220px;">Định Vị, Persona & Lời Hứa</th>
              <th style="min-width: 280px;">📺 Kênh Mẫu & Nguồn Tham Khảo</th>
              <th style="min-width: 320px;">💡 Đề Tài Mẫu & Công Thức Hook 3s</th>
            </tr>
          </thead>
          <tbody id="references-table-body">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- HIDDEN LEGACY COMPATIBILITY DOM (Obsolete charts/tabs retired from visible UI) -->
  <div id="legacy-compat-dom" style="display:none !important;">
    <span id="kpi-likes">0</span>
    <span id="kpi-likes-delta">+0</span>
    <span id="kpi-likes-avg">TB: 0 views/video</span>
    <span id="kpi-subs">0</span>
    <span id="kpi-subs-delta">+0</span>
    <span>1. Tổng Quan Hệ Thống Kênh</span>
    <span>5. Kho Kênh Mẫu, Email & Đề Tài Gợi Ý</span>
    <button class="tab-btn" id="btn-tab-funnel" onclick="switchTab('tab-funnel')">
      <span>🔗</span> 3. Ma Trận Phễu Long ↔ Short & Đợt Sản Xuất
      <span class="tab-count" id="count-tab-funnel">0</span>
    </button>
    <button class="tab-btn" id="btn-tab-ops" onclick="switchTab('tab-ops')">
      <span>⚡</span> 4. Điều Hành & Lịch Sử Tăng Trưởng
    </button>
    <div id="fleet-section-title"></div>
    <div id="batch-pills-container"></div>
    <div id="fleet-chart-grid"></div>
    <div id="channels-card-grid"></div>
    <div class="tab-pane" id="tab-funnel">
      <div id="batch-performance-grid"></div>
      <div id="funnel-matrix-compliance-badge"></div>
      <div id="funnel-pairs-grid"></div>
    </div>
    <div class="tab-pane" id="tab-ops">
      <select id="cli-channel-select" onchange="generateCLICommand()"><option value="all">all</option></select>
      <select id="cli-batch-select" onchange="generateCLICommand()"><option value="batch2">batch2</option></select>
      <select id="cli-action-select" onchange="generateCLICommand()"><option value="produce_long">produce_long</option></select>
      <div id="cli-output-text"></div>
      <table><tbody id="history-table-body"></tbody></table>
      <table><tbody id="cdp-ports-table-body"></tbody></table>
    </div>
  </div>

</div>

<!-- TOAST NOTIFICATION CONTAINER -->
<div class="toast-container" id="toast-container"></div>

<!-- {{EMBEDDED_DATA_SCRIPT}} -->

<script>
// ==============================================================================
// VIDEO PILOT V3 FRONTEND ENGINE
// Self-contained Vanilla JS • Zero CDN Dependencies
// ==============================================================================

const API_BASE = window.location.protocol.startsWith('http') ? '' : 'http://127.0.0.1:8765';
const REPO_CD_PREFIX = 'cd /home/hongphuoc6104/Desktop/vp-agent-core && ';

const state = {
  raw: null,
  currentTab: 'tab-fleet',
  searchQuery: '',
  channelFilter: 'all',
  batchFilter: 'all',
  formatFilter: 'all',
  waveFilter: 'all',
  langFilter: 'all',
  styleFilter: 'all',
  reviewStatusFilter: 'all',
  sortBy: 'views_desc',
  page: 1,
  pageSize: 20,
  expandedChannels: {},
  expandedReferences: {},
  simpleFilter: 'all',
  simpleSearch: '',
  selectedWaveChannels: ['ban_do_quyen_luc', 'ho_so_ky_la', 'co_the_ke', 'su_ke_lai'],
  hideAdvancedTabs: false,
};

const ALIAS_CHANNEL_IDS = new Set([
  'en_scale_and_bone',
  'en_root_and_canopy',
  'en_spawn_to_apex',
  'en_deep_time_strata'
]);

const TIER_A_SET = new Set([
  'ban_do_quyen_luc', 'ho_so_ky_la', 'co_the_ke', 'su_ke_lai',
  'chanh_niem_ke', 'ai_binh_dan', 'tui_tien', 'nao_luoi',
  'en_plain_sight_ai', 'en_choke_point', 'en_cold_case_ink', 'en_inside_vessel'
]);

function getLangBadgeHtml(lang, channelId) {
  const isEn = lang === 'en' || (channelId && String(channelId).startsWith('en_'));
  return `<span class="badge-lang ${isEn ? 'badge-lang-en' : 'badge-lang-vi'}">${isEn ? '🇺🇸 EN' : '🇻🇳 VN'}</span>`;
}

function getStyleBadgeAndSwatchesHtml(ch) {
  const archLabel = ch.visual_archetype_label || '';
  const archId = ch.visual_archetype_id || '';
  const palette = Array.isArray(ch.visual_palette) ? ch.visual_palette : [];
  const visLabel = ch.visual_label || ch.visual_profile_id || '';

  if (!archLabel && palette.length === 0) return '';

  const swatchesHtml = palette.map(hex =>
    `<span class="swatch-dot" style="background-color:${escHtml(hex)};" title="${escHtml(hex)}"></span>`
  ).join('');

  return `
    <div class="style-badge-swatch-wrap" title="${escHtml(visLabel)}">
      <span style="font-size:11px; font-weight:600; color:var(--text-white); display:inline-flex; align-items:center; gap:4px;">
        <span>🎨</span> ${escHtml(archLabel || archId)}
      </span>
      <div style="display:inline-flex; align-items:center; gap:3px;">
        ${swatchesHtml}
      </div>
    </div>
  `;
}

// --- DATA NORMALIZATION ENGINE (Defensive against schema variations) ---
function normalizeDashboardData(raw) {
  if (!raw) return null;
  const data = JSON.parse(JSON.stringify(raw));
  data.channels = Array.isArray(data.channels) ? data.channels : [];

  // Deduplicate legacy EN alias channels so physical fleet stays canonical (38 channels: 20 VN + 18 EN)
  const rawChannelCount = data.channels.length;
  const physicalChannels = data.channels.filter(c => !ALIAS_CHANNEL_IDS.has(c.channel_id));
  const removedAliases = physicalChannels.length > 0 && physicalChannels.length < rawChannelCount;
  if (removedAliases) {
    data.channels = physicalChannels;
  }

  // Normalize each channel's video catalog
  data.channels.forEach(ch => {
    ch.wave = ch.wave || 1;
    ch.email = ch.email || '';
    ch.niche = ch.niche || '';
    ch.promise = ch.promise || '';
    ch.persona = ch.persona || '';
    ch.visual_profile_id = ch.visual_profile_id || ch.profile_id || '';
    ch.visual_label = ch.visual_label || '';
    ch.visual_archetype_id = ch.visual_archetype_id || '';
    ch.visual_archetype_label = ch.visual_archetype_label || '';
    ch.visual_palette = Array.isArray(ch.visual_palette) ? ch.visual_palette : [];
    ch.references = Array.isArray(ch.references) ? ch.references : [];
    ch.seed_topics = Array.isArray(ch.seed_topics) ? ch.seed_topics : [];
    ch.hook_formulas = Array.isArray(ch.hook_formulas) ? ch.hook_formulas : [];
    ch.youtube_channel_url = ch.youtube_channel_url || (ch.youtube_channel_id ? `https://www.youtube.com/channel/${ch.youtube_channel_id}` : '');
    if (!Array.isArray(ch.videos) || ch.videos.length === 0) {
      ch.videos = [];
      if (ch.long_video && (ch.long_video.video_id || ch.long_video.video_url)) {
        ch.videos.push({
          ...ch.long_video,
          channel_id: ch.channel_id,
          channel_name: ch.channel_name,
          handle: ch.handle,
          email: ch.email,
          profile_id: ch.profile_id,
          wave: ch.wave,
          youtube_channel_url: ch.youtube_channel_url,
          cdp_port: ch.cdp_port,
          format: 'long_16x9',
          is_short: false,
          batch: ch.long_video.batch || 'week1',
          batch_label: ch.long_video.batch_label || 'Đợt 1 (Week 1)'
        });
      }
      if (ch.short_video && (ch.short_video.video_id || ch.short_video.video_url)) {
        ch.videos.push({
          ...ch.short_video,
          channel_id: ch.channel_id,
          channel_name: ch.channel_name,
          handle: ch.handle,
          email: ch.email,
          profile_id: ch.profile_id,
          wave: ch.wave,
          youtube_channel_url: ch.youtube_channel_url,
          cdp_port: ch.cdp_port,
          format: 'short_9x16',
          is_short: true,
          batch: ch.short_video.batch || 'week1',
          batch_label: ch.short_video.batch_label || 'Đợt 1 (Week 1)'
        });
      }
    }

    // Ensure channel-level video properties
    ch.videos.forEach(v => {
      v.channel_id = v.channel_id || ch.channel_id;
      v.channel_name = v.channel_name || ch.channel_name;
      v.handle = v.handle || ch.handle;
      v.email = v.email || ch.email || '';
      v.profile_id = v.profile_id || ch.profile_id || '';
      v.cdp_port = v.cdp_port || ch.cdp_port;
      v.wave = v.wave || ch.wave || 1;
      v.youtube_channel_url = v.youtube_channel_url || ch.youtube_channel_url;
      v.batch = v.batch || 'week1';
      v.batch_label = v.batch_label || (v.batch === 'week1' ? 'Đợt 1 (Week 1)' : (v.batch === 'batch2' ? 'Đợt 2 (Batch 2)' : v.batch));
      v.is_short = v.is_short ?? (v.format === 'short_9x16');
      v.view_count = Number(v.view_count || 0);
      v.like_count = Number(v.like_count || 0);
      v.engagement_rate = v.view_count > 0 ? ((v.like_count / v.view_count) * 100).toFixed(1) + '%' : '0.0%';
    });

    if (ch.channel_views === undefined || ch.channel_views === null) {
      ch.channel_views = ch.videos.reduce((s, v) => s + (v.view_count || 0), 0);
    }
    if (ch.channel_likes === undefined || ch.channel_likes === null) {
      ch.channel_likes = ch.videos.reduce((s, v) => s + (v.like_count || 0), 0);
    }

    // Build funnel_pairs if missing
    if (!Array.isArray(ch.funnel_pairs) || ch.funnel_pairs.length === 0) {
      const byBatch = {};
      ch.videos.forEach(v => {
        const b = v.batch || 'week1';
        if (!byBatch[b]) byBatch[b] = { batch: b, batch_label: v.batch_label || b, longs: [], shorts: [] };
        if (v.is_short) byBatch[b].shorts.push(v);
        else byBatch[b].longs.push(v);
      });
      ch.funnel_pairs = Object.values(byBatch).map(grp => {
        const lv = grp.longs[0] || ch.long_video || null;
        const sv = grp.shorts[0] || ch.short_video || null;
        const isLinked = sv ? Boolean(sv.has_funnel_link || sv.related_video_id || sv.related_video_url) : false;
        let ratio = 'N/A';
        if (lv && lv.view_count > 0 && sv) {
          ratio = ((sv.view_count / lv.view_count) * 100).toFixed(1) + '%';
        }
        return {
          batch: grp.batch,
          batch_label: grp.batch_label,
          long_video: lv,
          short_video: sv,
          is_linked: isLinked,
          funnel_view_ratio: ratio
        };
      });
    }
  });

  // Flatten or filter all_videos (re-derive cleanly if alias channels were deduplicated)
  if (removedAliases) {
    if (Array.isArray(data.all_videos) && data.all_videos.length > 0) {
      data.all_videos = data.all_videos.filter(v => !ALIAS_CHANNEL_IDS.has(v.channel_id));
    } else {
      data.all_videos = data.channels.flatMap(c => c.videos || []);
    }
  } else if (!Array.isArray(data.all_videos) || data.all_videos.length === 0) {
    data.all_videos = data.channels.flatMap(c => c.videos || []);
  }

  // Derive batches array if missing or recompute after alias deduplication
  if (removedAliases || !Array.isArray(data.batches) || data.batches.length === 0) {
    const batchMap = new Map();
    data.all_videos.forEach(v => {
      const bId = v.batch || 'week1';
      const bLabel = v.batch_label || (bId === 'week1' ? 'Đợt 1 (Week 1)' : (bId === 'batch2' ? 'Đợt 2 (Batch 2)' : bId));
      if (!batchMap.has(bId)) {
        batchMap.set(bId, {
          batch_id: bId,
          batch_label: bLabel,
          videos_count: 0,
          long_count: 0,
          short_count: 0,
          views: 0,
          likes: 0,
          avg_views: 0
        });
      }
      const item = batchMap.get(bId);
      item.videos_count++;
      if (v.is_short) item.short_count++;
      else item.long_count++;
      item.views += (v.view_count || 0);
      item.likes += (v.like_count || 0);
    });
    batchMap.forEach(b => {
      b.avg_views = b.videos_count > 0 ? Math.round(b.views / b.videos_count) : 0;
    });
    data.batches = Array.from(batchMap.values());
  }

  // Calculate totals (recompute cleanly from physical channels when aliases were removed)
  const prevTotals = data.totals || {};
  const shorts = data.all_videos.filter(v => v.is_short);
  const linked = shorts.filter(v => Boolean(v.has_funnel_link || v.related_video_id || v.related_video_url)).length;
  const computedLongs = data.all_videos.filter(v => !v.is_short).length;
  const computedShorts = shorts.length;
  const computedTotalViews = data.all_videos.reduce((s, v) => s + (v.view_count || 0), 0);
  const computedLongViews = data.all_videos.filter(v => !v.is_short).reduce((s, v) => s + (v.view_count || 0), 0);
  const computedShortViews = shorts.reduce((s, v) => s + (v.view_count || 0), 0);
  const computedTotalLikes = data.all_videos.reduce((s, v) => s + (v.like_count || 0), 0);
  const computedTotalSubs = data.channels.reduce((s, c) => s + (c.subscriber_count || 0), 0);

  if (removedAliases) {
    data.totals = {
      ...prevTotals,
      total_channels: data.channels.length,
      total_videos: data.all_videos.length,
      total_long_videos: computedLongs,
      total_short_videos: computedShorts,
      total_views: computedTotalViews,
      long_views: computedLongViews,
      short_views: computedShortViews,
      total_likes: computedTotalLikes,
      total_subscribers: computedTotalSubs,
      avg_views_per_video: data.all_videos.length > 0 ? Math.round(computedTotalViews / data.all_videos.length) : 0,
      funnel_total_shorts: computedShorts,
      funnel_linked_shorts: linked,
      funnel_compliance_pct: computedShorts > 0 ? Math.round((linked / computedShorts) * 100) : 100
    };
  } else {
    data.totals = prevTotals;
    data.totals.total_channels = data.totals.total_channels || data.channels.length;
    data.totals.total_videos = data.totals.total_videos || data.all_videos.length;
    data.totals.total_long_videos = data.totals.total_long_videos ?? computedLongs;
    data.totals.total_short_videos = data.totals.total_short_videos ?? computedShorts;
    data.totals.total_views = data.totals.total_views ?? computedTotalViews;
    data.totals.long_views = data.totals.long_views ?? computedLongViews;
    data.totals.short_views = data.totals.short_views ?? computedShortViews;
    data.totals.total_likes = data.totals.total_likes ?? computedTotalLikes;
    data.totals.total_subscribers = data.totals.total_subscribers ?? computedTotalSubs;
    data.totals.avg_views_per_video = data.totals.avg_views_per_video ?? (data.totals.total_videos > 0 ? Math.round(data.totals.total_views / data.totals.total_videos) : 0);
    data.totals.funnel_total_shorts = data.totals.funnel_total_shorts ?? computedShorts;
    data.totals.funnel_linked_shorts = data.totals.funnel_linked_shorts ?? linked;
    data.totals.funnel_compliance_pct = data.totals.funnel_compliance_pct ?? (computedShorts > 0 ? Math.round((linked / computedShorts) * 100) : 100);
  }

  data.history = Array.isArray(data.history) ? data.history : [];

  return data;
}

// --- UTILITIES ---
function escHtml(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function formatNumber(n) {
  return Number(n || 0).toLocaleString('vi-VN');
}

function formatDuration(seconds) {
  if (!seconds || isNaN(seconds) || seconds <= 0) return '00:00';
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
}

function formatDate(isoStr) {
  if (!isoStr) return '--';
  try {
    const d = new Date(isoStr);
    return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
  } catch {
    return isoStr;
  }
}

function showToast(message, type = 'info', duration = 3200) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast-msg ${type}`;
  let icon = 'ℹ️';
  if (type === 'success') icon = '✓';
  if (type === 'error') icon = '⚠️';
  toast.innerHTML = `<span style="font-weight:700;">${icon}</span> <span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(8px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// --- TAB SWITCHING ---
function switchTab(tabId) {
  state.currentTab = tabId;
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));

  const btnMap = {
    'tab-fleet': 'btn-tab-fleet',
    'tab-catalog': 'btn-tab-catalog',
    'tab-funnel': 'btn-tab-funnel',
    'tab-ops': 'btn-tab-ops',
    'tab-refs': 'btn-tab-refs',
    'tab-review': 'btn-tab-review'
  };
  const activeBtn = document.getElementById(btnMap[tabId]);
  if (activeBtn) activeBtn.classList.add('active');

  const activePane = document.getElementById(tabId);
  if (activePane) activePane.classList.add('active');

  if (tabId === 'tab-catalog') {
    renderCatalogTable();
  } else if (tabId === 'tab-refs') {
    renderReferencesTab();
  } else if (tabId === 'tab-review') {
    renderReviewTab();
  }
}

// --- FILTERING & SEARCH ---
function onSearchInput(val) {
  state.searchQuery = val.trim();
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) clearBtn.style.display = state.searchQuery ? 'block' : 'none';
  state.page = 1;
  renderActiveViews();
}

function clearSearch() {
  const input = document.getElementById('filter-search');
  if (input) input.value = '';
  onSearchInput('');
}

function onFilterChange() {
  state.channelFilter = document.getElementById('filter-channel').value;
  state.batchFilter = document.getElementById('filter-batch').value;
  state.formatFilter = document.getElementById('filter-format').value;
  const waveEl = document.getElementById('filter-wave');
  if (waveEl) state.waveFilter = waveEl.value;
  const langEl = document.getElementById('filter-lang');
  if (langEl) state.langFilter = langEl.value;
  const styleEl = document.getElementById('filter-style');
  if (styleEl) state.styleFilter = styleEl.value;
  state.sortBy = document.getElementById('filter-sort').value;
  state.page = 1;
  renderActiveViews();
}

function resetAllFilters() {
  state.searchQuery = '';
  state.channelFilter = 'all';
  state.batchFilter = 'all';
  state.formatFilter = 'all';
  state.waveFilter = 'all';
  state.langFilter = 'all';
  state.styleFilter = 'all';
  state.sortBy = 'views_desc';
  state.page = 1;

  const searchInput = document.getElementById('filter-search');
  if (searchInput) searchInput.value = '';
  const clearBtn = document.getElementById('search-clear-btn');
  if (clearBtn) clearBtn.style.display = 'none';

  document.getElementById('filter-channel').value = 'all';
  document.getElementById('filter-batch').value = 'all';
  document.getElementById('filter-format').value = 'all';
  const waveEl = document.getElementById('filter-wave');
  if (waveEl) waveEl.value = 'all';
  const langEl = document.getElementById('filter-lang');
  if (langEl) langEl.value = 'all';
  const styleEl = document.getElementById('filter-style');
  if (styleEl) styleEl.value = 'all';
  document.getElementById('filter-sort').value = 'views_desc';

  renderActiveViews();
  showToast('Đã đặt lại toàn bộ bộ lọc', 'info', 1800);
}

function setSort(sortKey) {
  state.sortBy = sortKey;
  const sortSelect = document.getElementById('filter-sort');
  if (sortSelect) sortSelect.value = sortKey;
  renderActiveViews();
}

// --- GET FILTERED VIDEOS ---
function getFilteredVideos() {
  if (!state.raw || !state.raw.all_videos) return [];
  let list = [...state.raw.all_videos];

  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    list = list.filter(v =>
      (v.title && v.title.toLowerCase().includes(q)) ||
      (v.video_id && v.video_id.toLowerCase().includes(q)) ||
      (v.channel_name && v.channel_name.toLowerCase().includes(q)) ||
      (v.handle && v.handle.toLowerCase().includes(q)) ||
      (v.email && v.email.toLowerCase().includes(q)) ||
      (v.batch && v.batch.toLowerCase().includes(q)) ||
      (v.batch_label && v.batch_label.toLowerCase().includes(q)) ||
      (v.job_id && v.job_id.toLowerCase().includes(q))
    );
  }

  if (state.channelFilter !== 'all') {
    list = list.filter(v => v.channel_id === state.channelFilter);
  }

  if (state.batchFilter !== 'all') {
    list = list.filter(v => (v.batch || 'week1') === state.batchFilter);
  }

  if (state.formatFilter === 'long') {
    list = list.filter(v => !v.is_short);
  } else if (state.formatFilter === 'short') {
    list = list.filter(v => v.is_short);
  }

  if (state.waveFilter && state.waveFilter !== 'all') {
    const targetWave = parseInt(state.waveFilter, 10);
    list = list.filter(v => (v.wave || 1) === targetWave);
  }

  if (state.langFilter && state.langFilter !== 'all') {
    list = list.filter(v => (v.language || (v.channel_id && v.channel_id.startsWith('en_') ? 'en' : 'vi')) === state.langFilter);
  }

  if (state.styleFilter && state.styleFilter !== 'all') {
    const chStyleMap = {};
    (state.raw.channels || []).forEach(c => { chStyleMap[c.channel_id] = c.visual_archetype_id; });
    list = list.filter(v => chStyleMap[v.channel_id] === state.styleFilter);
  }

  list.sort((a, b) => {
    switch (state.sortBy) {
      case 'views_desc':
        return (b.view_count || 0) - (a.view_count || 0);
      case 'views_asc':
        return (a.view_count || 0) - (b.view_count || 0);
      case 'published_desc': {
        const da = a.published_at ? new Date(a.published_at).getTime() : 0;
        const db = b.published_at ? new Date(b.published_at).getTime() : 0;
        return db - da;
      }
      case 'likes_desc':
        return (b.like_count || 0) - (a.like_count || 0);
      case 'engagement_desc': {
        const ea = a.view_count > 0 ? (a.like_count || 0) / a.view_count : 0;
        const eb = b.view_count > 0 ? (b.like_count || 0) / b.view_count : 0;
        return eb - ea;
      }
      case 'title_asc':
        return (a.title || '').localeCompare(b.title || '', 'vi');
      case 'channel_name_asc':
        return (a.channel_name || '').localeCompare(b.channel_name || '', 'vi');
      case 'wave_asc':
        return (a.wave || 1) - (b.wave || 1);
      case 'cdp_port_asc':
        return (a.cdp_port || 0) - (b.cdp_port || 0);
      default:
        return (b.view_count || 0) - (a.view_count || 0);
    }
  });

  return list;
}

// --- RENDER KPI CARDS & HEADER ---
function renderKPIs() {
  const d = state.raw;
  if (!d) return;

  const setText = (id, txt) => {
    const el = document.getElementById(id);
    if (el) el.innerText = txt;
  };

  const t = d.totals || {};
  const numCh = t.total_channels || d.channels.length || 0;
  const viCount = d.channels.filter(c => (c.language || (String(c.channel_id || '').startsWith('en_') ? 'en' : 'vi')) === 'vi').length;
  const enCount = Math.max(0, d.channels.length - viCount);

  setText('header-fleet-status', `${numCh}/${numCh} Kênh Active • ${t.total_videos || 0} Videos`);

  if (d.generated_at) {
    const genDate = new Date(d.generated_at);
    setText('header-updated-at', `Cập nhật: ${genDate.toLocaleTimeString('vi-VN')} (${d.scrape_duration_seconds || 0}s)`);
  }

  setText('kpi-channels', `${numCh} / ${numCh}`);
  setText('kpi-channels-subtitle', `${viCount} Kênh Việt · ${enCount} Kênh Anh`);
  setText('kpi-videos', formatNumber(t.total_videos || 0));
  setText('kpi-videos-split', `${t.total_long_videos || 0} Long 16:9 · ${t.total_short_videos || 0} Short 9:16`);

  setText('kpi-views', formatNumber(t.total_views || 0));
  if (t.views_delta) {
    const el = document.getElementById('kpi-views-delta');
    if (el) {
      el.innerText = `+${formatNumber(t.views_delta)}`;
      el.style.display = 'inline-block';
    }
  }
  setText(
    'kpi-views-split',
    `Shorts: ${formatNumber(t.short_views || 0)} · Longs: ${formatNumber(t.long_views || 0)} · ${formatNumber(t.total_likes || 0)} 👍 · ${formatNumber(t.total_subscribers || 0)} Subs`
  );

  setText('kpi-likes', formatNumber(t.total_likes || 0));
  if (t.likes_delta) {
    const el = document.getElementById('kpi-likes-delta');
    if (el) {
      el.innerText = `+${formatNumber(t.likes_delta)}`;
      el.style.display = 'inline-block';
    }
  }
  setText('kpi-likes-avg', `TB: ${formatNumber(t.avg_views_per_video || 0)} views/video`);

  setText('kpi-subs', formatNumber(t.total_subscribers || 0));
  if (t.subs_delta) {
    const el = document.getElementById('kpi-subs-delta');
    if (el) {
      el.innerText = `+${formatNumber(t.subs_delta)}`;
      el.style.display = 'inline-block';
    }
  }

  const compliance = t.funnel_compliance_pct ?? 100;
  const pendingRevCount = getReviewQueueItems().filter(x => (x.status || 'PENDING_REVIEW') === 'PENDING_REVIEW').length;
  setText('kpi-funnel', `${compliance}% ✓`);
  setText('kpi-funnel-sub', `${t.funnel_linked_shorts || 0}/${t.funnel_total_shorts || 0} Phễu · ${pendingRevCount} Chờ duyệt`);

  // Counters in Tab Navigation
  setText('count-tab-fleet', numCh);
  setText('count-tab-catalog', t.total_videos || 0);
  setText('count-tab-refs', numCh);

  const totalPairs = d.channels.reduce((sum, ch) => sum + (ch.funnel_pairs ? ch.funnel_pairs.length : 0), 0);
  setText('count-tab-funnel', totalPairs);
}

// --- POPULATE DROPDOWNS ---
function populateDropdowns() {
  const d = state.raw;
  if (!d) return;

  const numCh = d.channels.length;

  // Channel dropdown
  const chSelect = document.getElementById('filter-channel');
  const cliChSelect = document.getElementById('cli-channel-select');
  const curChVal = chSelect ? chSelect.value : 'all';

  let chOptions = `<option value="all">Tất cả ${numCh} Kênh</option>`;
  let cliOptions = `<option value="all">Tất cả ${numCh} Kênh (Fleet-wide)</option>`;
  d.channels.forEach(ch => {
    chOptions += `<option value="${ch.channel_id}">${ch.channel_name} (${ch.handle || ''})</option>`;
    cliOptions += `<option value="${ch.channel_id}">${ch.channel_name} (${ch.channel_id})</option>`;
  });
  if (chSelect) {
    chSelect.innerHTML = chOptions;
    if (curChVal) chSelect.value = curChVal;
  }
  if (cliChSelect) cliChSelect.innerHTML = cliOptions;

  // Batch dropdown
  const bSelect = document.getElementById('filter-batch');
  const cliBatchSelect = document.getElementById('cli-batch-select');
  const curBVal = bSelect ? bSelect.value : 'all';

  let bOptions = '<option value="all">Tất cả Đợt Sản Xuất</option>';
  let cliBOptions = '';
  (d.batches || []).forEach(b => {
    bOptions += `<option value="${b.batch_id}">${b.batch_label} (${b.videos_count} videos)</option>`;
    cliBOptions += `<option value="${b.batch_id}">${b.batch_id} (${b.batch_label})</option>`;
  });
  if (bSelect) {
    bSelect.innerHTML = bOptions;
    if (curBVal) bSelect.value = curBVal;
  }
  if (cliBatchSelect && cliBOptions) cliBatchSelect.innerHTML = cliBOptions;
}

// --- TAB 1: FLEET OVERVIEW RENDER ---
function renderFleetTab() {
  const d = state.raw;
  if (!d) return;
  const legacyWrap = document.getElementById('legacy-compat-dom');
  const compatChartGrid = document.getElementById('fleet-chart-grid');
  const compatCardGrid = document.getElementById('channels-card-grid');
  if (!compatChartGrid || !compatCardGrid || (legacyWrap && legacyWrap.contains(compatCardGrid))) return;

  // 1. Dynamic header updates
  const totalCh = d.totals ? (d.totals.total_channels || d.channels.length) : d.channels.length;
  const countTabFleet = document.getElementById('count-tab-fleet');
  if (countTabFleet) countTabFleet.innerText = totalCh;
  const fleetSectionTitle = document.getElementById('fleet-section-title');
  if (fleetSectionTitle) {
    fleetSectionTitle.innerHTML = `<span>📊</span> So Sánh Lượt Xem Hệ Thống (${totalCh} Kênh)`;
  }

  // 2. Batch summary pills
  const pillsWrap = document.getElementById('batch-pills-container');
  const totalViews = d.totals.total_views || 1;
  pillsWrap.innerHTML = (d.batches || []).map(b => {
    const share = ((b.views / totalViews) * 100).toFixed(1);
    return `<div class="batch-pill">⚡ <b>${b.batch_label}:</b> ${b.videos_count} vids • ${formatNumber(b.views)} views (${share}%)</div>`;
  }).join('');

  // 3. Fleet Views Chart
  const chartGrid = document.getElementById('fleet-chart-grid');
  const maxChViews = Math.max(1, ...d.channels.map(c => c.channel_views || 0));

  chartGrid.innerHTML = d.channels.map(c => {
    const chViews = c.channel_views || 0;
    const pct = Math.min(100, Math.round((chViews / maxChViews) * 100));

    // Split long vs short
    const lvViews = (c.videos || []).filter(v => !v.is_short).reduce((s, v) => s + (v.view_count || 0), 0);
    const svViews = (c.videos || []).filter(v => v.is_short).reduce((s, v) => s + (v.view_count || 0), 0);
    const lvPct = chViews > 0 ? (lvViews / chViews) * pct : 0;
    const svPct = chViews > 0 ? (svViews / chViews) * pct : 0;

    return `
      <div class="chart-row">
        <div class="chart-row-label">
          <span class="chart-row-name"><a href="${escHtml(c.youtube_channel_url)}" target="_blank" rel="noopener noreferrer">${c.channel_name} <span style="color:var(--text-dim); font-size:11px;">(${c.handle})</span></a></span>
          <span class="chart-row-views">${formatNumber(chViews)} views</span>
        </div>
        <div class="chart-bar-bg" title="${c.channel_name}: ${lvViews} Long views | ${svViews} Short views">
          <div class="chart-bar-fill fill-long" style="width: ${lvPct}%;"></div>
          <div class="chart-bar-fill fill-short" style="width: ${svPct}%;"></div>
        </div>
      </div>
    `;
  }).join('');

  // 4. Channel Cards Grid with Wave & Query Filtering
  const cardGrid = document.getElementById('channels-card-grid');

  let chList = d.channels;
  if (state.waveFilter && state.waveFilter !== 'all') {
    const targetWave = parseInt(state.waveFilter, 10);
    chList = chList.filter(c => (c.wave || 1) === targetWave);
  }
  if (state.langFilter && state.langFilter !== 'all') {
    chList = chList.filter(c => (c.language || (c.channel_id && c.channel_id.startsWith('en_') ? 'en' : 'vi')) === state.langFilter);
  }
  if (state.styleFilter && state.styleFilter !== 'all') {
    chList = chList.filter(c => (c.visual_archetype_id || '') === state.styleFilter);
  }
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    chList = chList.filter(c =>
      (c.channel_name && c.channel_name.toLowerCase().includes(q)) ||
      (c.handle && c.handle.toLowerCase().includes(q)) ||
      (c.email && c.email.toLowerCase().includes(q)) ||
      (c.niche && c.niche.toLowerCase().includes(q)) ||
      (c.channel_id && c.channel_id.toLowerCase().includes(q)) ||
      (c.profile_id && c.profile_id.toLowerCase().includes(q)) ||
      (c.visual_archetype_label && c.visual_archetype_label.toLowerCase().includes(q)) ||
      (c.visual_label && c.visual_label.toLowerCase().includes(q)) ||
      (c.videos || []).some(v => (v.title && v.title.toLowerCase().includes(q)) || (v.video_id && v.video_id.toLowerCase().includes(q)))
    );
  }

  if (chList.length === 0) {
    cardGrid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 40px; color: var(--text-dim); font-size: 13px;">Không có kênh nào khớp với bộ lọc đợt (Wave) hoặc từ khóa tìm kiếm hiện tại.</div>';
    return;
  }

  cardGrid.innerHTML = chList.map(ch => {
    // Filter this channel's videos based on current search & batch & format filters
    let vList = ch.videos || [];
    if (state.batchFilter !== 'all') {
      vList = vList.filter(v => (v.batch || 'week1') === state.batchFilter);
    }
    if (state.formatFilter === 'long') {
      vList = vList.filter(v => !v.is_short);
    } else if (state.formatFilter === 'short') {
      vList = vList.filter(v => v.is_short);
    }
    if (state.searchQuery) {
      const q = state.searchQuery.toLowerCase();
      vList = vList.filter(v => (v.title && v.title.toLowerCase().includes(q)) || (v.video_id && v.video_id.toLowerCase().includes(q)));
    }

    // Top video
    const topVid = [...(ch.videos || [])].sort((a, b) => (b.view_count || 0) - (a.view_count || 0))[0];
    const topBannerHtml = topVid && topVid.view_count > 0 ?
      `<div class="top-video-banner">🔥 Top: <b>${topVid.title ? topVid.title.slice(0, 32) + '...' : topVid.video_id}</b> (${formatNumber(topVid.view_count)} views)</div>` : '';

    const firstTwo = vList.slice(0, 2);
    const remaining = vList.slice(2);
    const isExpanded = state.expandedChannels[ch.channel_id] === true;

    function renderMiniCard(v) {
      const isShort = v.is_short;
      const thumbUrl = v.thumbnail_url || (v.video_id ? `https://i.ytimg.com/vi/${v.video_id}/mqdefault.jpg` : '');
      const watchUrl = v.video_url || (v.video_id ? `https://youtu.be/${v.video_id}` : '#');
      const formatBadge = isShort ? `<span class="badge-format short">9:16 Short</span>` : `<span class="badge-format long">16:9 Long</span>`;

      let funnelBadge = '';
      if (isShort) {
        const isLinked = Boolean(v.has_funnel_link || v.related_video_id || v.related_video_url);
        funnelBadge = isLinked ? `<span class="badge-funnel linked">✓ Phễu</span>` : `<span class="badge-funnel unlinked">⚠️ Chưa phễu</span>`;
      }

      return `
        <div class="mini-video-card">
          <div class="mini-thumb-wrap ${isShort ? 'short-aspect' : ''}">
            <img class="mini-thumb-img" src="${thumbUrl}" alt="Thumbnail" loading="lazy" onerror="this.style.display='none'">
            <span class="mini-duration-badge">${v.duration_formatted || formatDuration(v.length_seconds)}</span>
          </div>
          <div class="mini-meta">
            <div class="mini-title" title="${v.title || ''}">
              <a href="${watchUrl}" target="_blank">${v.title || v.video_id || 'Chưa có tiêu đề'}</a>
            </div>
            <div class="mini-sub">
              ${formatBadge}
              <span>👁️ ${formatNumber(v.view_count)}</span>
              <span>👍 ${v.like_count || 0}</span>
              ${funnelBadge}
            </div>
          </div>
        </div>
      `;
    }

    let expandSection = '';
    if (vList.length > 2) {
      const toggleLabel = isExpanded ? `▲ Thu gọn (${remaining.length}) video` : `▼ Xem thêm (${remaining.length}) video khác`;
      expandSection = `
        <div class="channel-card-expand-bar">
          <button class="btn-expand-toggle" onclick="toggleChannelExpand('${ch.channel_id}')">
            ${toggleLabel}
          </button>
          <button class="btn btn-secondary btn-sm" onclick="openChannelInCatalog('${ch.channel_id}')" title="Mở trong Kho Video">
            🔍 Kho Video
          </button>
        </div>
        <div class="collapsible-drawer" style="display: ${isExpanded ? 'flex' : 'none'};">
          ${remaining.map(renderMiniCard).join('')}
        </div>
      `;
    }

    const avatarHtml = ch.avatar_url ?
      `<img class="channel-avatar" src="${ch.avatar_url}" alt="${ch.channel_name}" onerror="this.onerror=null; this.src=''; this.className='channel-avatar-fallback'; this.innerHTML='${ch.channel_name.slice(0, 2).toUpperCase()}';">` :
      `<div class="channel-avatar-fallback">${ch.channel_name.slice(0, 2).toUpperCase()}</div>`;

    // Collapsible Reference & Seed Topics Drawer
    const refs = ch.references || [];
    const topics = ch.seed_topics || [];
    const hooks = ch.hook_formulas || [];
    const isRefExpanded = state.expandedReferences[ch.channel_id] === true;
    const refBtnLabel = isRefExpanded ?
      `▲ Thu gọn (${refs.length} nguồn · ${topics.length} đề tài)` :
      `📚 Kênh Mẫu, Nguồn Tham Khảo & Đề Tài Mẫu (${refs.length} nguồn · ${topics.length} đề tài)`;

    const refDrawerHtml = `
      <div class="channel-ref-drawer-wrap">
        <button class="btn-ref-toggle" onclick="toggleReferencesExpand('${ch.channel_id}')">
          <span>${refBtnLabel}</span>
          <span style="font-size:10px;">${isRefExpanded ? '▲' : '▼'}</span>
        </button>
        <div class="ref-drawer-content" style="display: ${isRefExpanded ? 'flex' : 'none'};">
          <div>
            <div class="ref-section-title">📺 1. Kênh Mẫu & Nguồn Tham Khảo:</div>
            ${refs.length > 0 ? refs.map(r => {
              const platLow = (r.platform || '').toLowerCase();
              let pClass = 'ref-platform-youtube';
              let pIcon = 'YouTube';
              if (platLow.includes('tiktok')) { pClass = 'ref-platform-tiktok'; pIcon = 'TikTok'; }
              else if (platLow.includes('book') || platLow.includes('kinh')) { pClass = 'ref-platform-book'; pIcon = 'Sách/Kinh'; }
              return `
                <div style="margin-bottom:6px; font-size:11px; line-height:1.4;">
                  <span class="ref-item-badge ${pClass}">${pIcon}</span>
                  ${r.format ? `<span class="ref-item-badge ref-format-badge">${escHtml(r.format)}</span>` : ''}
                  <strong style="color:var(--text-white);">${escHtml(r.name)}</strong>
                  ${r.learn ? `<div style="color:var(--text-muted); padding-left:4px; font-style:italic; margin-top:2px;">↳ Điểm học hỏi: ${escHtml(r.learn)}</div>` : ''}
                </div>
              `;
            }).join('') : '<div style="color:var(--text-dim); font-size:11px;">Chưa cấu hình nguồn mẫu</div>'}
          </div>

          <div>
            <div class="ref-section-title">💡 2. Nội Dung Mẫu / Đề Tài Hạt Giống:</div>
            ${topics.length > 0 ? `
              <ol style="margin:0; padding-left:16px; font-size:11px; line-height:1.5; color:var(--text-gray);">
                ${topics.map(t => `<li>${escHtml(t)}</li>`).join('')}
              </ol>
            ` : '<div style="color:var(--text-dim); font-size:11px;">Chưa có đề tài mẫu</div>'}
          </div>

          ${hooks.length > 0 ? `
            <div>
              <div class="ref-section-title">⚡ 3. Công Thức Hook 3 Giây:</div>
              <ul style="margin:0; padding-left:16px; font-size:11px; line-height:1.4; color:var(--purple-light);">
                ${hooks.map(h => `<li>${escHtml(h)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      </div>
    `;

    return `
      <div class="channel-card">
        <div>
          <div class="channel-header">
            ${avatarHtml}
            <div class="channel-title-block">
              <div class="channel-name" title="${ch.channel_name}">
                <a href="${escHtml(ch.youtube_channel_url)}" target="_blank" rel="noopener noreferrer">${ch.channel_name}</a>
              </div>
              <div class="channel-handle">
                <a href="${escHtml(ch.youtube_channel_url)}" target="_blank" rel="noopener noreferrer">${ch.handle || ''}</a>
              </div>
              <span class="channel-profile-tag">${ch.profile_id || 'Profile'} • Port ${ch.cdp_port || 9222}</span>
            </div>
          </div>

          <!-- Prominent Account & Wave Info Strip -->
          <div class="channel-account-strip">
            <div class="account-strip-row">
              <div style="display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
                <span style="font-size:11px; color:var(--text-muted);">📧 Email Google:</span>
                <strong style="color:var(--text-white); font-size:11.5px;">${escHtml(ch.email || 'Chưa cấu hình')}</strong>
                ${ch.email ? `<button class="btn-copy-mini" onclick="copyText('${escHtml(ch.email)}')" title="Sao chép Email">📋 Copy</button>` : ''}
              </div>
              <div style="display:flex; align-items:center; gap:5px;">
                <span class="badge-wave badge-wave-${ch.wave || 1}">🌊 Wave ${ch.wave || 1}</span>
                ${getLangBadgeHtml(ch.language, ch.channel_id)}
              </div>
            </div>
            <div class="account-strip-row" style="margin-top:2px; font-size:11px; color:var(--text-dim);">
              <span>🔌 Profile: <code>${escHtml(ch.profile_id || 'Profile')}</code> (Port <code>${ch.cdp_port || 9222}</code>)</span>
              ${ch.niche ? `<span style="color:var(--primary-light); font-weight:600;">🎯 ${escHtml(ch.niche)}</span>` : ''}
            </div>
            ${getStyleBadgeAndSwatchesHtml(ch)}
          </div>

          <div class="channel-stats-row">
            <div class="c-stat-col">
              <span class="c-stat-label">Videos</span>
              <span class="c-stat-val">${ch.videos ? ch.videos.length : 0}</span>
            </div>
            <div class="c-stat-col">
              <span class="c-stat-label">Views</span>
              <span class="c-stat-val">${formatNumber(ch.channel_views)}</span>
            </div>
            <div class="c-stat-col">
              <span class="c-stat-label">Subs</span>
              <span class="c-stat-val">${formatNumber(ch.subscriber_count)}</span>
            </div>
            <div class="c-stat-col">
              <span class="c-stat-label">Likes</span>
              <span class="c-stat-val">${formatNumber(ch.channel_likes)}</span>
            </div>
          </div>

          ${topBannerHtml}

          <div class="channel-videos-wrapper">
            ${vList.length > 0 ? firstTwo.map(renderMiniCard).join('') : (
              (!ch.videos || ch.videos.length === 0) ?
                '<div class="new-channel-badge">🆕 Kênh Mới Khởi Tạo — Sẵn Sàng Đăng Video Short & Long</div>' :
                '<div style="font-size:11px; color:var(--text-dim); text-align:center; padding:10px;">Không có video khớp bộ lọc</div>'
            )}
            ${expandSection}
          </div>

          ${refDrawerHtml}
        </div>

        <div class="channel-footer-actions">
          <button class="btn btn-primary" onclick="openChromeStudio('${ch.channel_id}')" title="Mở Profile trong Chrome Studio CDP">
            🚀 Mở Studio (CDP)
          </button>
          <a class="btn btn-secondary" href="${escHtml(ch.youtube_channel_url || '#')}" target="_blank" rel="noopener noreferrer">
            Kênh ↗
          </a>
          <a class="btn btn-secondary" href="${ch.studio_url || '#'}" target="_blank">
            Web Studio ↗
          </a>
          <a class="btn btn-secondary" href="${ch.analytics_url || '#'}" target="_blank">
            Analytics ↗
          </a>
        </div>
      </div>
    `;
  }).join('');
}

function toggleChannelExpand(channelId) {
  state.expandedChannels[channelId] = !state.expandedChannels[channelId];
  renderFleetTab();
}

function toggleReferencesExpand(channelId) {
  state.expandedReferences[channelId] = !state.expandedReferences[channelId];
  renderFleetTab();
}

function openChannelInCatalog(channelId) {
  state.channelFilter = channelId;
  const sel = document.getElementById('filter-channel');
  if (sel) sel.value = channelId;
  switchTab('tab-catalog');
  showToast(`Đã lọc kho video theo kênh: ${channelId}`, 'info', 2000);
}

// --- TAB 2: MASTER CATALOG PAGINATION & RENDER ---
function renderCatalogTable() {
  const filtered = getFilteredVideos();
  const total = filtered.length;

  const pageSize = state.pageSize === 'all' ? Math.max(1, total) : parseInt(state.pageSize, 10);
  const totalPages = Math.max(1, Math.ceil(total / pageSize));

  if (state.page > totalPages) state.page = totalPages;
  if (state.page < 1) state.page = 1;

  const startIdx = (state.page - 1) * pageSize;
  const endIdx = Math.min(startIdx + pageSize, total);
  const pageItems = filtered.slice(startIdx, endIdx);

  // Summary texts
  document.getElementById('catalog-page-summary').innerHTML = `Hiển thị <b>${total > 0 ? startIdx + 1 : 0} - ${endIdx}</b> trong tổng số <b>${formatNumber(total)}</b> video ${state.searchQuery || state.channelFilter !== 'all' || state.batchFilter !== 'all' || state.formatFilter !== 'all' ? '(Đã lọc)' : ''}`;
  document.getElementById('catalog-bottom-summary').innerText = `Tổng số ${formatNumber(total)} video • Trang ${state.page} / ${totalPages}`;
  document.getElementById('catalog-page-indicator').innerText = `Trang ${state.page} / ${totalPages}`;
  document.getElementById('catalog-bottom-page-indicator').innerText = `${state.page} / ${totalPages}`;

  // Prev / Next button states
  document.getElementById('btn-page-prev').disabled = state.page <= 1;
  document.getElementById('btn-page-next').disabled = state.page >= totalPages;

  const tbody = document.getElementById('catalog-table-body');
  if (pageItems.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 40px; color: var(--text-dim);">Không tìm thấy video nào khớp với điều kiện lọc hiện tại.</td></tr>`;
    return;
  }

  const maxViewsInFleet = Math.max(1, ...filtered.map(v => v.view_count || 0));

  tbody.innerHTML = pageItems.map((v, idx) => {
    const isShort = v.is_short;
    const thumbUrl = v.thumbnail_url || (v.video_id ? `https://i.ytimg.com/vi/${v.video_id}/mqdefault.jpg` : '');
    const watchUrl = v.video_url || (v.video_id ? `https://youtu.be/${v.video_id}` : '#');
    const studioEditUrl = v.video_id ? `https://studio.youtube.com/video/${v.video_id}/edit` : '#';
    const rowNum = startIdx + idx + 1;

    const pct = Math.min(100, Math.round(((v.view_count || 0) / maxViewsInFleet) * 100));

    let formatBadge = isShort ?
      `<span class="badge-format short">9:16 Short</span>` :
      `<span class="badge-format long">16:9 Long</span>`;

    let funnelBadge = '';
    if (isShort) {
      if (v.has_funnel_link || v.related_video_id || v.related_video_url) {
        const relId = v.related_video_id || (v.related_video_url ? v.related_video_url.split('/').pop() : '');
        funnelBadge = `<div style="margin-top:3px;"><span class="badge-funnel linked">🔗 Phễu → ${relId || 'Long'}</span></div>`;
      } else {
        funnelBadge = `<div style="margin-top:3px;"><span class="badge-funnel unlinked">⚠️ Chưa gắn phễu</span></div>`;
      }
    }

    const statusHtml = v.is_public !== false ?
      `<span class="status-dot-active"></span>Public` :
      `<span class="status-dot-unlisted"></span>Unlisted`;

    return `
      <tr>
        <td>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:11px; color:var(--text-dim); width:18px;">${rowNum}</span>
            <div class="cat-thumb-box ${isShort ? 'short-mode' : ''}">
              <img class="cat-thumb-img" src="${thumbUrl}" alt="Thumbnail" loading="lazy" onerror="this.style.display='none'">
              <span class="cat-duration-tag">${v.duration_formatted || formatDuration(v.length_seconds)}</span>
            </div>
          </div>
        </td>
        <td class="cat-title-cell">
          <div class="cat-video-title" title="${v.title || ''}">
            <a href="${watchUrl}" target="_blank">${v.title || v.video_id || 'Chưa có tiêu đề'}</a>
          </div>
          <div class="cat-video-meta">
            <span class="cat-video-id" onclick="copyText('${v.video_id}')" title="Click để copy ID">${v.video_id || 'ID N/A'}</span>
            ${v.job_id ? `<span style="color:var(--text-dim);">• ${v.job_id}</span>` : ''}
          </div>
        </td>
        <td>
          <div style="font-weight:600; color:var(--text-white); display:flex; align-items:center; gap:6px;">
            <a href="${escHtml(v.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer" style="color:inherit; text-decoration:none;">${v.channel_name || ''}</a>
            <span class="badge-wave badge-wave-${v.wave || 1}" style="font-size:9.5px; padding:1px 5px;">W${v.wave || 1}</span>
            ${getLangBadgeHtml(v.language, v.channel_id)}
          </div>
          <div style="font-size:11px; color:var(--text-dim); margin-top:2px;">
            <a href="${escHtml(v.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer" style="color:inherit; text-decoration:none;">${v.handle || ''}</a> • Port ${v.cdp_port || 9222}
          </div>
          ${v.email ? `
            <div style="font-size:10.5px; color:var(--text-muted); margin-top:3px; display:flex; align-items:center; gap:4px;">
              <span>📧 ${escHtml(v.email)}</span>
              <button class="btn-copy-mini" onclick="copyText('${escHtml(v.email)}')" title="Sao chép Email" style="padding:0 4px; font-size:9px;">📋</button>
            </div>
          ` : ''}
        </td>
        <td>
          <div style="font-weight:600; color:var(--text-gray);">${v.batch_label || v.batch || 'week1'}</div>
          <div style="font-size:11px; color:var(--text-dim);">${formatDate(v.publish_date || v.published_at)}</div>
        </td>
        <td>
          ${formatBadge}
          ${funnelBadge}
        </td>
        <td>
          <div class="views-bar-wrap">
            <span class="views-bar-val">${formatNumber(v.view_count)}</span>
            <div class="views-bar-track" title="${pct}% so với top view">
              <div class="views-bar-fill" style="width: ${pct}%;"></div>
            </div>
          </div>
        </td>
        <td>
          <div style="font-weight:700; color:var(--text-white);">${formatNumber(v.like_count)} likes</div>
          <div style="font-size:11px; color:var(--text-dim);">Tương tác: <b style="color:var(--primary-light);">${v.engagement_rate || '0.0%'}</b></div>
        </td>
        <td>
          ${statusHtml}
        </td>
        <td style="text-align: right; white-space: nowrap;">
          <button class="btn btn-secondary btn-sm" onclick="copyText('${watchUrl}')" title="Sao chép link xem video">
            Link 📋
          </button>
          <a class="btn btn-secondary btn-sm" href="${watchUrl}" target="_blank" title="Mở YouTube">
            Xem ↗
          </a>
          <a class="btn btn-secondary btn-sm" href="${studioEditUrl}" target="_blank" title="Mở Studio Edit">
            Edit ↗
          </a>
        </td>
      </tr>
    `;
  }).join('');
}

function onPageSizeChange(val) {
  state.pageSize = val;
  state.page = 1;
  renderCatalogTable();
}

function changePage(delta) {
  state.page += delta;
  renderCatalogTable();
  const el = document.querySelector('.catalog-container');
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function goToPage(page) {
  state.page = page;
  renderCatalogTable();
}

function goToLastPage() {
  const filtered = getFilteredVideos();
  const pageSize = state.pageSize === 'all' ? 1 : parseInt(state.pageSize, 10);
  state.page = Math.max(1, Math.ceil(filtered.length / pageSize));
  renderCatalogTable();
}

// --- TAB 3: FUNNEL & BATCH ANALYTICS RENDER ---
function renderFunnelTab() {
  const d = state.raw;
  if (!d) return;

  // 1. Batch performance cards
  const batchGrid = document.getElementById('batch-performance-grid');
  const legacyWrap = document.getElementById('legacy-compat-dom');
  if (!batchGrid || (legacyWrap && legacyWrap.contains(batchGrid))) return;
  const totalFleetViews = d.totals.total_views || 1;

  batchGrid.innerHTML = (d.batches || []).map(b => {
    const share = ((b.views / totalFleetViews) * 100).toFixed(1);
    const avgLikes = b.videos_count > 0 ? (b.likes / b.videos_count).toFixed(1) : 0;
    return `
      <div class="batch-kpi-card">
        <div class="batch-kpi-name">
          <span>🚀 ${b.batch_label}</span>
          <span class="v-badge">${b.videos_count} Videos</span>
        </div>
        <div class="batch-kpi-stats">
          <div class="b-stat">
            <span class="b-stat-label">Cơ Cấu Định Dạng</span>
            <span class="b-stat-val">${b.long_count} Long · ${b.short_count} Short</span>
          </div>
          <div class="b-stat">
            <span class="b-stat-label">Tổng Views Đợt</span>
            <span class="b-stat-val" style="color:var(--primary-light);">${formatNumber(b.views)}</span>
          </div>
          <div class="b-stat">
            <span class="b-stat-label">Thị Phần Hệ Thống</span>
            <span class="b-stat-val">${share}% views</span>
          </div>
          <div class="b-stat">
            <span class="b-stat-label">Trung Bình Lượt Xem</span>
            <span class="b-stat-val">${formatNumber(b.avg_views)} views/vid</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // 2. Funnel pairs matrix
  const pairsContainer = document.getElementById('funnel-pairs-grid');
  let pairsList = [];

  d.channels.forEach(ch => {
    (ch.funnel_pairs || []).forEach(p => {
      // apply channel & batch filters
      if (state.channelFilter !== 'all' && ch.channel_id !== state.channelFilter) return;
      if (state.batchFilter !== 'all' && (p.batch || 'week1') !== state.batchFilter) return;
      pairsList.push({
        channel: ch,
        pair: p
      });
    });
  });

  if (pairsList.length === 0) {
    pairsContainer.innerHTML = `<div style="text-align: center; padding: 40px; color: var(--text-dim); background: var(--bg-surface); border-radius: 12px;">Không có cặp phễu nào khớp với bộ lọc hiện tại.</div>`;
    return;
  }

  pairsContainer.innerHTML = pairsList.map(item => {
    const ch = item.channel;
    const p = item.pair;
    const lv = p.long_video || {};
    const sv = p.short_video || {};

    const lvThumb = lv.thumbnail_url || (lv.video_id ? `https://i.ytimg.com/vi/${lv.video_id}/mqdefault.jpg` : '');
    const svThumb = sv.thumbnail_url || (sv.video_id ? `https://i.ytimg.com/vi/${sv.video_id}/mqdefault.jpg` : '');

    const isLinked = p.is_linked;
    const bridgeClass = isLinked ? 'badge-funnel linked' : 'badge-funnel unlinked';
    const bridgeText = isLinked ? '✓ Chuẩn Phễu V2' : '⚠️ Chưa Gắn Phễu';

    return `
      <div class="funnel-pair-card">
        <div class="pair-channel-header">
          <div class="pair-ch-name">
            <span style="color:var(--primary-light);">🏢 <a href="${escHtml(ch.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer" style="color:inherit; text-decoration:none;">${ch.channel_name}</a></span>
            <span style="font-size:12px; color:var(--text-dim);"><a href="${escHtml(ch.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer" style="color:inherit; text-decoration:none;">(${ch.handle})</a></span>
            <span class="v-badge">${p.batch_label || p.batch || 'week1'}</span>
          </div>
          <div style="font-size:12px; color:var(--text-muted);">
            Port ${ch.cdp_port || 9222} • Tỷ lệ chuyển đổi phễu: <b style="color:var(--emerald-light);">${p.funnel_view_ratio || 'N/A'}</b>
          </div>
        </div>

        <div class="pair-grid">
          <!-- Parent Long 16:9 -->
          <div class="funnel-video-box">
            <div class="mini-thumb-wrap">
              <img class="mini-thumb-img" src="${lvThumb}" alt="Long" onerror="this.style.display='none'">
              <span class="mini-duration-badge">${lv.duration_formatted || formatDuration(lv.length_seconds)}</span>
            </div>
            <div style="flex:1; min-width:0;">
              <span class="badge-format long">Parent Long 16:9</span>
              <div class="mini-title" style="margin-top:4px;">
                <a href="${lv.video_url || '#'}" target="_blank">${lv.title || lv.video_id || 'Chưa xuất bản'}</a>
              </div>
              <div class="mini-sub">
                <span>👁️ ${formatNumber(lv.view_count)} views</span>
                <span>👍 ${lv.like_count || 0} likes</span>
              </div>
            </div>
          </div>

          <!-- Bridge Indicator -->
          <div class="funnel-bridge-col">
            <span class="${bridgeClass}">${bridgeText}</span>
            <span class="bridge-arrow-icon">➔</span>
            <span class="bridge-ratio-text">Short / Long Views: <b>${p.funnel_view_ratio}</b></span>
          </div>

          <!-- Spin-off Short 9:16 -->
          <div class="funnel-video-box">
            <div class="mini-thumb-wrap short-aspect">
              <img class="mini-thumb-img" src="${svThumb}" alt="Short" onerror="this.style.display='none'">
              <span class="mini-duration-badge">${sv.duration_formatted || formatDuration(sv.length_seconds)}</span>
            </div>
            <div style="flex:1; min-width:0;">
              <span class="badge-format short">Spin-off Short 9:16</span>
              <div class="mini-title" style="margin-top:4px;">
                <a href="${sv.video_url || '#'}" target="_blank">${sv.title || sv.video_id || 'Chưa xuất bản'}</a>
              </div>
              <div class="mini-sub">
                <span>👁️ ${formatNumber(sv.view_count)} views</span>
                <span>👍 ${sv.like_count || 0} likes</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// --- TAB 4: OPERATIONS & GROWTH HISTORY RENDER ---
function renderOpsTab() {
  const d = state.raw;
  if (!d) return;

  // 1. History Table
  const histBody = document.getElementById('history-table-body');
  const legacyWrap = document.getElementById('legacy-compat-dom');
  if (!histBody || (legacyWrap && legacyWrap.contains(histBody))) return;
  if (d.history && d.history.length > 0) {
    histBody.innerHTML = d.history.map((h, i) => {
      const prev = d.history[i + 1] || null;
      let vDelta = '';
      if (prev && h.total_views !== undefined && prev.total_views !== undefined) {
        const diff = h.total_views - prev.total_views;
        vDelta = diff >= 0 ? `+${diff}` : `${diff}`;
      }
      return `
        <tr>
          <td>${formatDate(h.timestamp)} ${h.timestamp ? new Date(h.timestamp).toLocaleTimeString('vi-VN') : ''}</td>
          <td><b>${h.total_videos || 0}</b></td>
          <td style="color:var(--primary-light);"><b>${formatNumber(h.total_views)}</b></td>
          <td>${formatNumber(h.total_likes)}</td>
          <td>${formatNumber(h.total_subscribers)}</td>
          <td><span class="kpi-delta">${vDelta || '--'}</span></td>
        </tr>
      `;
    }).join('');
  }

  // 2. CDP Ports & Studio Launcher Table
  const cdpBody = document.getElementById('cdp-ports-table-body');
  cdpBody.innerHTML = d.channels.map(ch => {
    const waveBadgeClass = `badge-wave badge-wave-${ch.wave || 1}`;
    return `
      <tr>
        <td><b><a href="${escHtml(ch.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer" style="color:inherit; text-decoration:none;">${ch.channel_name}</a></b></td>
        <td>
          <div style="display:flex; align-items:center; gap:6px;">
            <a href="${escHtml(ch.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer" style="color:var(--text-dim); text-decoration:none;">${ch.handle || ''}</a>
            <span class="${waveBadgeClass}">Wave ${ch.wave || 1}</span>
            ${getLangBadgeHtml(ch.language, ch.channel_id)}
          </div>
        </td>
        <td><code>${ch.directory || ch.profile_id || 'Profile'}</code></td>
        <td><span class="v-badge">Port ${ch.cdp_port || 9222}</span></td>
        <td>
          <div style="display:flex; align-items:center; gap:6px;">
            <strong style="font-size:11.5px; color:var(--text-white);">${escHtml(ch.email || '--')}</strong>
            ${ch.email ? `<button class="btn-copy-mini" onclick="copyText('${escHtml(ch.email)}')" title="Sao chép Email">📋</button>` : ''}
          </div>
        </td>
        <td><span class="status-dot-active"></span>Sẵn sàng CDP</td>
        <td style="text-align: right;">
          <button class="btn btn-primary btn-sm" onclick="openChromeStudio('${ch.channel_id}')">
            🚀 Mở Chrome Studio
          </button>
        </td>
      </tr>
    `;
  }).join('');

  // 3. Generate initial CLI command
  generateCLICommand();
}

// --- HELPER: DEDUPE STALE PUBLISHED TOPICS ---
function normalizeTopicForDedupe(text) {
  return String(text || '')
    .replace(/@\\S+/g, ' ')
    .replace(/#\\S+/g, ' ')
    .replace(/đ/g, 'd')
    .replace(/Đ/g, 'D')
    .normalize('NFD')
    .replace(/[\\u0300-\\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, ' ')
    .trim();
}

function isTopicPublishedInChannel(topicStr, ch) {
  const stop = new Set(['vi', 'sao', 'nhung', 'cua', 'va', 'trong', 'cho', 'khi', 'nao', 'bi', 'mat', 'giai', 'ma', 'tap', 'moi', 'shorts', 'short', 've', 'khong', 'quyet', 'dinh', 'van', 'quan', 'nghe', 'thuat', 'chien', 'luoc', 'cach', 'nguoi', 'nam', 'bai', 'tran', 'nuoc', 'song', 'the', 'and', 'of', 'to', 'in', 'why', 'how']);
  const tokList = normalizeTopicForDedupe(topicStr).split(/\\s+/).filter(w => w.length >= 2 && !stop.has(w));
  if (tokList.length === 0) return false;
  const tokSet = new Set(tokList);
  const candYears = tokList.filter(w => /^\\d{3,}$/.test(w));
  const candRare = tokList.filter(w => !/^\\d+$/.test(w) && w.length >= 7);
  const vids = (ch && ch.videos) || [];
  for (const v of vids) {
    const exList = normalizeTopicForDedupe(v.title || '').split(/\\s+/).filter(w => w.length >= 2 && !stop.has(w));
    if (exList.length === 0) continue;
    const exSet = new Set(exList);
    if (candYears.some(y => exSet.has(y))) return true;
    const shared = tokList.filter(t => exSet.has(t));
    if (shared.some(t => candRare.includes(t))) return true;
    if (shared.length >= 3) return true;
    if (shared.length >= 2 && (shared.length / Math.max(1, Math.min(tokSet.size, exSet.size))) >= 0.5) return true;
  }
  return false;
}

// --- TAB 5: MASTER REFERENCES & SEED TOPICS TABLE RENDER ---
function renderReferencesTab() {
  const d = state.raw;
  if (!d) return;

  const tbody = document.getElementById('references-table-body');
  if (!tbody) return;

  const diagByCh = {};
  if (d.fleet_diagnostics && Array.isArray(d.fleet_diagnostics.channels)) {
    d.fleet_diagnostics.channels.forEach(dc => { diagByCh[dc.channel_id] = dc; });
  }

  let chList = d.channels;
  if (state.waveFilter && state.waveFilter !== 'all') {
    const targetWave = parseInt(state.waveFilter, 10);
    chList = chList.filter(c => (c.wave || 1) === targetWave);
  }
  if (state.langFilter && state.langFilter !== 'all') {
    chList = chList.filter(c => (c.language || (c.channel_id && c.channel_id.startsWith('en_') ? 'en' : 'vi')) === state.langFilter);
  }
  if (state.styleFilter && state.styleFilter !== 'all') {
    chList = chList.filter(c => (c.visual_archetype_id || '') === state.styleFilter);
  }
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    chList = chList.filter(c =>
      (c.channel_name && c.channel_name.toLowerCase().includes(q)) ||
      (c.handle && c.handle.toLowerCase().includes(q)) ||
      (c.email && c.email.toLowerCase().includes(q)) ||
      (c.niche && c.niche.toLowerCase().includes(q)) ||
      (c.promise && c.promise.toLowerCase().includes(q)) ||
      (c.persona && c.persona.toLowerCase().includes(q)) ||
      (c.visual_archetype_label && c.visual_archetype_label.toLowerCase().includes(q)) ||
      (c.visual_label && c.visual_label.toLowerCase().includes(q)) ||
      (c.references || []).some(r => (r.name && r.name.toLowerCase().includes(q)) || (r.learn && r.learn.toLowerCase().includes(q))) ||
      (c.seed_topics || []).some(t => t.toLowerCase().includes(q))
    );
  }

  const countBadge = document.getElementById('references-count-badge');
  if (countBadge) {
    countBadge.innerText = `${chList.length} / ${d.channels.length} Kênh`;
  }

  if (chList.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" style="text-align: center; padding: 40px; color: var(--text-dim);">Không tìm thấy kênh nào khớp với bộ lọc đợt (Wave) hoặc từ khóa tìm kiếm hiện tại.</td></tr>`;
    return;
  }

  tbody.innerHTML = chList.map(ch => {
    const waveBadgeClass = `badge-wave badge-wave-${ch.wave || 1}`;
    const refs = ch.references || [];
    const diag = diagByCh[ch.channel_id] || {};
    const learn = diag.learning || ch.learning_summary || {};
    const audit = learn.change_impact_audit || {};
    const hooks = ch.hook_formulas || [];

    const freshQueue = Array.isArray(diag.fresh_topic_queue) && diag.fresh_topic_queue.length > 0
      ? diag.fresh_topic_queue
      : (Array.isArray(ch.fresh_topic_queue) && ch.fresh_topic_queue.length > 0 ? ch.fresh_topic_queue : []);

    const filteredSeeds = (ch.seed_topics || []).filter(t => !isTopicPublishedInChannel(t, ch));
    const archivedTopics = Array.isArray(learn.completed_topics_archive) && learn.completed_topics_archive.length > 0
      ? learn.completed_topics_archive
      : ((ch.seed_topics || []).filter(t => isTopicPublishedInChannel(t, ch)));

    const refsHtml = refs.length > 0 ? refs.map(r => {
      const platLow = (r.platform || '').toLowerCase();
      let pClass = 'ref-platform-youtube';
      let pIcon = '📺 YouTube';
      if (platLow.includes('tiktok')) {
        pClass = 'ref-platform-tiktok';
        pIcon = '🎵 TikTok';
      } else if (platLow.includes('book') || platLow.includes('kinh')) {
        pClass = 'ref-platform-book';
        pIcon = '📖 Sách/Kinh';
      }
      const fmtBadge = r.format ? `<span class="ref-item-badge ref-format-badge">${escHtml(r.format)}</span>` : '';
      return `
        <div class="ref-item-row" style="margin-bottom: 6px;">
          <span class="ref-item-badge ${pClass}">${pIcon}</span>
          ${fmtBadge}
          <strong style="color:var(--text-white);">${escHtml(r.name || '')}</strong>
          ${r.learn ? `<div style="font-size:11px; color:var(--text-muted); padding-left:4px; margin-top:2px;">↳ <em>${escHtml(r.learn)}</em></div>` : ''}
        </div>
      `;
    }).join('') : '<span style="color:var(--text-dim); font-size:11px;">Chưa cập nhật nguồn mẫu</span>';

    const freshListHtml = freshQueue.length > 0
      ? `<div style="margin-bottom:6px;">
          <span class="ref-section-title" style="color:#34d399;">🔥 Đề Tài Mới Cập Nhật Liên Tục (Chưa Đăng):</span>
          <ol style="margin:4px 0 0; padding-left:18px; font-size:11.5px; line-height:1.55; color:#f8fafc;">
            ${freshQueue.map(q => `<li><b style="color:#38bdf8;">[${escHtml(String(q.episode_tag || '').toUpperCase())}]</b> ${escHtml(q.long_title || '')}<div style="font-size:10.5px; color:var(--text-muted);">↳ Short: ${escHtml(q.short_title || '')}</div></li>`).join('')}
          </ol>
        </div>`
      : (filteredSeeds.length > 0
          ? `<ol style="margin:0; padding-left:18px; font-size:11.5px; line-height:1.6; color:var(--text-gray);">${filteredSeeds.map(t => `<li>${escHtml(t)}</li>`).join('')}</ol>`
          : `<span style="color:#34d399; font-size:11px;">✓ Toàn bộ đề tài cũ đã làm xong — bấm "Chẩn Đoán Lại 38 Kênh" để nạp tập mới.</span>`);

    const learnRuleTxt = learn.learned_rule_vi || '';
    const impactBadgeTxt = audit.impact_badge_vi || (learn.impact_badge_vi || '');
    const impactSumTxt = audit.impact_summary_vi || (learn.impact_summary_vi || '');
    const learningHtml = (learnRuleTxt || impactBadgeTxt)
      ? `<div style="margin-top:6px; padding:6px 8px; border-radius:6px; background:rgba(56,189,248,0.08); border:1px solid rgba(56,189,248,0.25); font-size:11px; line-height:1.45;">
          ${impactBadgeTxt ? `<div style="color:#38bdf8; font-weight:700;">📊 ${escHtml(impactBadgeTxt)}${impactSumTxt ? ` <span style="font-weight:400; color:#cbd5e1;">(${escHtml(impactSumTxt)})</span>` : ''}</div>` : ''}
          ${learnRuleTxt ? `<div style="color:#e2e8f0; margin-top:2px;">🧬 <b>Rút kinh nghiệm:</b> ${escHtml(learnRuleTxt)}</div>` : ''}
        </div>`
      : '';

    const archiveHtml = archivedTopics.length > 0
      ? `<details style="margin-top:6px; font-size:10.5px; color:var(--text-dim);">
          <summary style="cursor:pointer; color:#94a3b8;">✅ Đã đăng / lưu trữ (${archivedTopics.length} bài — không gợi ý lại)</summary>
          <ul style="margin:4px 0 0; padding-left:16px; opacity:0.78;">
            ${archivedTopics.slice(0, 6).map(t => `<li style="text-decoration:line-through;">${escHtml(t)}</li>`).join('')}
          </ul>
        </details>`
      : '';

    const topicsHtml = freshListHtml + learningHtml + archiveHtml;

    const hooksHtml = hooks.length > 0 ? `
      <div style="margin-top: 8px; border-top: 1px dashed rgba(255,255,255,0.08); padding-top: 6px;">
        <span class="ref-section-title">⚡ Công thức Hook 3s:</span>
        <ul style="margin: 4px 0 0; padding-left: 16px; font-size: 11px; color: var(--purple-light);">
          ${hooks.map(h => `<li>${escHtml(h)}</li>`).join('')}
        </ul>
      </div>
    ` : '';

    const avatarHtml = ch.avatar_url ?
      `<img class="channel-avatar-sm" src="${ch.avatar_url}" alt="${ch.channel_name}" onerror="this.style.display='none'">` : '';

    return `
      <tr>
        <td style="vertical-align: top; width: 220px;">
          <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            ${avatarHtml}
            <div>
              <div style="font-weight:700; color:var(--text-white); font-size:13.5px;">
                <a href="${escHtml(ch.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer">${escHtml(ch.channel_name)}</a>
              </div>
              <div style="font-size:11px; color:var(--text-dim);">
                <a href="${escHtml(ch.youtube_channel_url || '')}" target="_blank" rel="noopener noreferrer">${escHtml(ch.handle || '')}</a>
              </div>
            </div>
          </div>
          <div style="margin-top: 6px; display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
            <span class="${waveBadgeClass}">🌊 Wave ${ch.wave || 1}</span>
            ${getLangBadgeHtml(ch.language, ch.channel_id)}
            <span style="font-size:10.5px; color:var(--text-dim); font-family:monospace;" title="YouTube Channel ID">${ch.youtube_channel_id ? ch.youtube_channel_id.slice(0, 12) + '...' : ''}</span>
          </div>
          <div style="margin-top: 4px;">
            ${getStyleBadgeAndSwatchesHtml(ch)}
          </div>
        </td>
        <td style="vertical-align: top; width: 240px;">
          <div style="display:flex; flex-direction:column; gap:6px;">
            <div style="background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06); border-radius:6px; padding:6px 8px;">
              <div style="font-size:10px; text-transform:uppercase; color:var(--text-dim); font-weight:700; margin-bottom:2px;">📧 Email Google Đã Đăng Nhập</div>
              <div style="display:flex; align-items:center; justify-content:space-between; gap:4px;">
                <strong style="color:var(--text-white); font-size:11.5px; word-break:break-all;">${escHtml(ch.email || 'Chưa cấu hình')}</strong>
                ${ch.email ? `<button class="btn-copy-mini" onclick="copyText('${escHtml(ch.email)}')" title="Sao chép Email">📋 Copy</button>` : ''}
              </div>
            </div>
            <div style="font-size:11px; color:var(--text-muted); display:flex; align-items:center; gap:6px;">
              <span>🔌 <code>${escHtml(ch.profile_id || 'Profile')}</code></span>
              <span>•</span>
              <span class="v-badge">Port ${ch.cdp_port || 9222}</span>
            </div>
            <div>
              <button class="btn btn-secondary btn-sm" onclick="openChromeStudio('${ch.channel_id}')" style="font-size:11px; padding:3px 8px;">
                🚀 Mở Studio CDP
              </button>
            </div>
          </div>
        </td>
        <td style="vertical-align: top; width: 220px;">
          <div style="display:flex; flex-direction:column; gap:4px;">
            <div><span class="badge-format long" style="font-size:10.5px;">🎯 ${escHtml(ch.niche || 'Ngách nội dung')}</span></div>
            ${ch.persona ? `<div style="font-size:11.5px; color:var(--text-white); font-weight:600;">👤 Persona: ${escHtml(ch.persona)}</div>` : ''}
            ${ch.promise ? `<div style="font-size:11px; color:var(--text-muted); line-height:1.4; font-style:italic;">"${escHtml(ch.promise)}"</div>` : ''}
          </div>
        </td>
        <td style="vertical-align: top; min-width: 280px;">
          ${refsHtml}
        </td>
        <td style="vertical-align: top; min-width: 320px;">
          ${topicsHtml}
          ${hooksHtml}
        </td>
      </tr>
    `;
  }).join('');
}

function generateCLICommand() {
  const ch = document.getElementById('cli-channel-select').value;
  const batch = document.getElementById('cli-batch-select').value;
  const action = document.getElementById('cli-action-select').value;
  const outBox = document.getElementById('cli-output-text');

  let cmd = '';
  switch (action) {
    case 'produce_long':
      cmd = ch === 'all' ?
        `python3 sys/tools/run_fleet.py --batch ${batch} --format long` :
        `python3 sys/tools/produce_channel_long_e2e.py --channel ${ch} --batch ${batch}`;
      break;
    case 'produce_short':
      cmd = ch === 'all' ?
        `python3 sys/tools/run_fleet.py --batch ${batch} --format short` :
        `python3 sys/tools/produce_channel_short_e2e.py --channel ${ch} --batch ${batch}`;
      break;
    case 'publish_cdp':
      cmd = ch === 'all' ?
        `python3 sys/tools/publish_youtube_cdp.py --all-channels --batch ${batch}` :
        `python3 sys/tools/publish_youtube_cdp.py --channel ${ch} --batch ${batch}`;
      break;
    case 'run_fleet':
      cmd = `python3 sys/tools/run_fleet.py --batch ${batch}`;
      break;
    case 'refresh_metrics':
      cmd = `python3 sys/tools/youtube_dashboard.py --refresh`;
      break;
    case 'serve_dashboard':
      cmd = `python3 sys/tools/youtube_dashboard.py --serve --port 8765`;
      break;
    default:
      cmd = `python3 sys/tools/youtube_dashboard.py --help`;
  }

  outBox.innerText = REPO_CD_PREFIX + cmd;
}

function copyCLICommand() {
  const cmd = document.getElementById('cli-output-text').innerText;
  copyText(cmd, '✓ Đã sao chép lệnh điều hành!');
}

// --- MASTER RENDER ENTRY POINT ---
function renderDashboard(data) {
  if (!data) return;
  state.raw = normalizeDashboardData(data);

  renderKPIs();
  populateDropdowns();
  renderSimpleHub();
  renderActiveViews();
}

function renderActiveViews() {
  renderSimpleHub();
  renderFleetTab();
  renderCatalogTable();
  renderFunnelTab();
  renderOpsTab();
  renderReferencesTab();
  renderReviewTab();
}

// ==============================================================================
// SIMPLE 38-CHANNEL MANAGEMENT, DIAGNOSTICS & 3-MODE PRODUCTION HUB
// ==============================================================================
function getCanonical38ChannelsWithDiagnostics() {
  if (!state.raw || !Array.isArray(state.raw.channels)) return [];
  const diagMap = {};
  if (state.raw.fleet_diagnostics && Array.isArray(state.raw.fleet_diagnostics.channels)) {
    state.raw.fleet_diagnostics.channels.forEach(d => {
      diagMap[d.channel_id] = d;
    });
  }
  const revItems = getReviewQueueItems();
  const revByCh = {};
  revItems.forEach(it => {
    const cid = it.channel_id || '';
    if (!revByCh[cid]) revByCh[cid] = [];
    revByCh[cid].push(it);
  });

  const physicalChannels = state.raw.channels.filter(c => !ALIAS_CHANNEL_IDS.has(c.channel_id));
  const listToUse = physicalChannels.length > 0 ? physicalChannels : state.raw.channels;

  return listToUse.map(ch => {
    const cid = ch.channel_id;
    const preDiag = diagMap[cid];
    if (preDiag) {
      return { ...ch, diag: preDiag };
    }
    const vids = ch.videos || [];
    const longs = vids.filter(v => !v.is_short);
    const shorts = vids.filter(v => v.is_short);
    const views = Number(ch.channel_views || 0);
    const unlinked = shorts.filter(v => !(v.has_funnel_link || v.related_video_id || v.related_video_url));
    const chRevs = revByCh[cid] || [];
    const pendingCnt = chRevs.filter(r => r.status === 'PENDING_REVIEW').length;

    let tier = (TIER_A_SET.has(cid) || views >= 1000) ? 'tier_a' : (vids.length >= 4 || views >= 200 ? 'tier_b' : 'tier_c');
    let tierLabel = tier === 'tier_a' ? '🔥 Tier-A (Mũi nhọn)' : (tier === 'tier_b' ? '📈 Tier-B (Tăng trưởng)' : '🌱 Tier-C (Ươm mầm)');

    let verdict = 'COLLECT';
    let verdictLabel = '🔵 COLLECT (Tạo thêm bài)';
    let summary = `Có ${longs.length} Long + ${shorts.length} Short (${formatNumber(views)} views). Tiếp tục làm cặp 1 Long + 1 Short.`;
    if (unlinked.length > 0 && longs.length > 0) {
      verdict = 'REPAIR_FUNNEL';
      verdictLabel = '🔧 Cần gắn Phễu Short→Long';
      summary = `Có ${unlinked.length}/${shorts.length} Short chưa nối Related Video về bài Long.`;
    } else if (views >= 1500) {
      verdict = 'SCALE';
      verdictLabel = '🟢 SCALE (Nhân rộng)';
      summary = `Tín hiệu thắng (${formatNumber(views)} views). Ưu tiên làm cặp 1 Long (2K) + 2 Short vệ tinh.`;
    } else if (vids.length >= 4 && views < 250) {
      verdict = 'ITERATE';
      verdictLabel = '🟡 ITERATE (Đổi Hook/Thumb)';
      summary = `Đã có ${vids.length} video (${views} views). Cần đổi Hook 3s đầu và làm mới Thumbnail.`;
    }

    const sortedVids = [...vids].sort((a, b) => Number(b.view_count || 0) - Number(a.view_count || 0));
    const topV = sortedVids[0] || null;
    const filteredSeeds = (ch.seed_topics || []).filter(t => !isTopicPublishedInChannel(t, ch));
    const nextTopic = filteredSeeds.length > 0
      ? filteredSeeds[0]
      : `Tập mới chuyên sâu cho ${ch.channel_name} (EP${String(longs.length + 1).padStart(2, '0')})`;
    const fallbackLearn = ch.learning_summary || {
      top_video: topV ? { title: topV.title || '', views: Number(topV.view_count || 0) } : null,
      change_impact_audit: {
        impact_badge_vi: unlinked.length > 0 && longs.length > 0 ? '🔧 Rò rỉ phễu' : (views >= 1500 ? '📈 Phát triển tốt' : '🔵 Đang tích lũy'),
        impact_summary_vi: topV ? `Đỉnh: ${(topV.title || '').slice(0, 42)} (${formatNumber(topV.view_count || 0)} views)` : 'Chưa có dữ liệu so sánh',
      },
      learned_rule_vi: topV
        ? `Ưu tiên nhân bản cấu trúc từ bài thắng nhất '${String(topV.title || '').slice(0, 46)}' (${formatNumber(topV.view_count || 0)} views).`
        : 'Mở đầu bằng [Con số/Quy mô + Vật thể cụ thể] ngay 3s đầu.',
      fresh_topic_queue: (ch.fresh_topic_queue && ch.fresh_topic_queue.length > 0)
        ? ch.fresh_topic_queue
        : filteredSeeds.slice(0, 3).map((t, i) => ({ episode_tag: `ep${String(longs.length + 1 + i).padStart(2, '0')}`, long_title: t, short_title: '' })),
      completed_topics_archive: (ch.completed_topics_archive && ch.completed_topics_archive.length > 0)
        ? ch.completed_topics_archive
        : (ch.seed_topics || []).filter(t => isTopicPublishedInChannel(t, ch)),
    };

    return {
      ...ch,
      diag: {
        channel_id: cid,
        tier,
        tier_label: tierLabel,
        verdict,
        verdict_label: verdictLabel,
        diagnosis_summary: summary,
        next_topic: nextTopic,
        long_count: longs.length,
        short_count: shorts.length,
        funnel_linked_shorts: shorts.length - unlinked.length,
        funnel_total_shorts: shorts.length,
        funnel_ok: unlinked.length === 0,
        pending_review_count: pendingCnt,
        learning: fallbackLearn,
        fresh_topic_queue: fallbackLearn.fresh_topic_queue || [],
        completed_topics_archive: fallbackLearn.completed_topics_archive || [],
      }
    };
  });
}

function getFilteredSimpleChannels() {
  let list = getCanonical38ChannelsWithDiagnostics();
  const f = state.simpleFilter || 'all';
  if (f === 'vi') {
    list = list.filter(c => (c.language || (c.channel_id.startsWith('en_') ? 'en' : 'vi')) === 'vi');
  } else if (f === 'en') {
    list = list.filter(c => (c.language || (c.channel_id.startsWith('en_') ? 'en' : 'vi')) === 'en');
  } else if (f === 'tier_a') {
    list = list.filter(c => c.diag.tier === 'tier_a');
  } else if (f === 'SCALE' || f === 'REPAIR_FUNNEL' || f === 'ITERATE') {
    list = list.filter(c => c.diag.verdict === f);
  }

  if (state.simpleSearch) {
    const q = state.simpleSearch.toLowerCase();
    list = list.filter(c =>
      (c.channel_name && c.channel_name.toLowerCase().includes(q)) ||
      (c.channel_id && c.channel_id.toLowerCase().includes(q)) ||
      (c.handle && c.handle.toLowerCase().includes(q)) ||
      (c.niche && c.niche.toLowerCase().includes(q)) ||
      (c.diag && c.diag.next_topic && c.diag.next_topic.toLowerCase().includes(q))
    );
  }

  const tierRank = { tier_a: 0, tier_b: 1, tier_c: 2 };
  list.sort((a, b) => {
    const ta = tierRank[a.diag.tier] ?? 9;
    const tb = tierRank[b.diag.tier] ?? 9;
    if (ta !== tb) return ta - tb;
    return (b.channel_views || 0) - (a.channel_views || 0);
  });
  return list;
}

function renderSimpleHub() {
  const all38 = getCanonical38ChannelsWithDiagnostics();
  const badge38 = document.getElementById('simple-38-badge');
  if (badge38) {
    const viCnt = all38.filter(c => (c.language || (c.channel_id.startsWith('en_') ? 'en' : 'vi')) === 'vi').length;
    const enCnt = all38.length - viCnt;
    badge38.innerText = `${all38.length} Kênh (${viCnt} VN + ${enCnt} EN)`;
  }

  // Populate single channel selector
  const singleSel = document.getElementById('simple-single-channel');
  if (singleSel && all38.length > 0) {
    const prevVal = singleSel.value;
    singleSel.innerHTML = all38.map(c =>
      `<option value="${escHtml(c.channel_id)}">${escHtml(c.channel_name)} (${escHtml(c.handle || c.channel_id)})</option>`
    ).join('');
    if (prevVal && all38.some(c => c.channel_id === prevVal)) {
      singleSel.value = prevVal;
    }
  }

  const chkLbl = document.getElementById('checked-count-lbl');
  if (chkLbl) chkLbl.innerText = String(state.selectedWaveChannels.length);

  // Queue state bar
  if (state.raw && state.raw.fleet_queue && state.raw.fleet_queue.active_command) {
    const fq = state.raw.fleet_queue;
    const cmdBox = document.getElementById('simple-cmd-preview-box');
    const sumBox = document.getElementById('simple-queue-waves-summary');
    if (cmdBox && fq.active_command) {
      cmdBox.innerText = fq.active_command.startsWith('cd ') ? fq.active_command : (REPO_CD_PREFIX + fq.active_command);
    }
    if (sumBox) {
      sumBox.innerText = `${fq.status || 'READY'}: ${fq.total_channels || 0} kênh • ${fq.total_waves || (fq.waves ? fq.waves.length : 1)} ca chạy`;
    }
    if (Array.isArray(fq.waves) && fq.waves.length > 0) {
      renderSimpleActionResultPanel(fq, { online: window.location.protocol.startsWith('http'), shouldScroll: false });
    }
  }

  // Render table rows
  const tbody = document.getElementById('simple-38-table-body');
  if (!tbody) return;

  const filtered = getFilteredSimpleChannels();
  if (filtered.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; padding:30px; color:var(--text-dim);">Không có kênh nào khớp bộ lọc.</td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(c => {
    const cid = c.channel_id;
    const d = c.diag;
    const isChecked = state.selectedWaveChannels.includes(cid);
    const funnelBadge = d.funnel_ok
      ? `<span class="badge-funnel linked">✓ ${d.funnel_linked_shorts}/${d.funnel_total_shorts} Phễu</span>`
      : `<span class="badge-funnel unlinked">⚠️ ${d.funnel_linked_shorts}/${d.funnel_total_shorts} Phễu</span>`;
    const revBadge = d.pending_review_count > 0
      ? `<span style="background:rgba(245,158,11,0.2); color:#fbbf24; border:1px solid rgba(245,158,11,0.4); border-radius:6px; padding:1px 6px; font-size:10.5px; font-weight:700; cursor:pointer;" onclick="openChannelReview('${escHtml(cid)}')">⏳ ${d.pending_review_count} chờ duyệt</span>`
      : `<span style="font-size:10.5px; color:var(--text-dim);">✓ Sạch hàng đợi</span>`;
    const waveNum = c.wave || 1;
    const waveBadge = `<span class="badge-wave badge-wave-${waveNum}">W${waveNum}</span>`;
    const emailHtml = c.email
      ? `<span style="color:var(--text-gray); font-family:monospace; font-size:10.5px;">✉️ ${escHtml(c.email)}</span><button class="btn-copy-mini" onclick="copyText('${escHtml(c.email)}', '✓ Đã copy email ${escHtml(c.email)}!')" title="Copy Email Google">📋</button>`
      : `<span style="color:var(--text-dim); font-size:10.5px;">Chưa gán Email</span>`;
    const cdpMeta = `${escHtml(c.profile_id || cid)} • Port ${c.cdp_port || 9222}`;

    const learn = d.learning || c.learning_summary || {};
    const audit = learn.change_impact_audit || {};
    const freshQ = Array.isArray(d.fresh_topic_queue) && d.fresh_topic_queue.length > 0
      ? d.fresh_topic_queue
      : (Array.isArray(learn.fresh_topic_queue) ? learn.fresh_topic_queue : []);
    const next2 = freshQ.slice(1, 3).map(x => `[${String(x.episode_tag || '').toUpperCase()}] ${x.long_title || ''}`).filter(Boolean);
    const impactTxt = audit.impact_badge_vi || learn.impact_badge_vi || '';
    const impactSub = audit.impact_summary_vi || learn.impact_summary_vi || '';
    const learnedRule = learn.learned_rule_vi || '';

    return `
      <tr>
        <td style="text-align: center;">
          <input type="checkbox" ${isChecked ? 'checked' : ''}
                  onchange="toggleWaveChannelCheckbox('${escHtml(cid)}', this.checked)"
                 style="width: 16px; height: 16px; cursor: pointer; accent-color: #06b6d4;">
        </td>
        <td>
          <div style="font-weight: 700; color: var(--text-white); display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <a href="${escHtml(c.youtube_channel_url || '#')}" target="_blank" rel="noopener noreferrer">${escHtml(c.channel_name)}</a>
            ${getLangBadgeHtml(c.language, cid)}
            ${waveBadge}
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px; display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <span>${escHtml(c.handle || cid)}</span>
            <span>•</span>
            <span style="color: var(--primary-light); font-weight: 600;">${escHtml(d.tier_label)}</span>
          </div>
          <div style="font-size: 10.5px; color: var(--text-dim); margin-top: 3px;">
            🔌 ${cdpMeta}
          </div>
          <div style="margin-top: 2px; display: flex; align-items: center; gap: 5px; flex-wrap: wrap;">
            ${emailHtml}
          </div>
        </td>
        <td>
          <div style="font-weight: 800; color: var(--text-white); font-size: 13px;">
            👁️ ${formatNumber(c.channel_views)} views
          </div>
          <div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">
            👥 ${formatNumber(c.subscriber_count)} subs • 🎬 ${d.long_count}L + ${d.short_count}S
          </div>
        </td>
        <td>
          <div>${funnelBadge}</div>
          <div style="margin-top: 4px;">${revBadge}</div>
        </td>
        <td>
          <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap; margin-bottom: 4px;">
            <span class="verdict-badge verdict-${escHtml(d.verdict)}">${escHtml(d.verdict_label)}</span>
            <span style="font-size: 11.5px; color: var(--text-gray);">${escHtml(d.diagnosis_summary)}</span>
          </div>
          ${impactTxt ? `<div style="font-size: 11px; color: #38bdf8; margin-bottom: 2px;">📊 <b>Kiểm chứng:</b> ${escHtml(impactTxt)}${impactSub ? ` <span style="color:#94a3b8;">— ${escHtml(impactSub)}</span>` : ''}</div>` : ''}
          ${learnedRule ? `<div style="font-size: 11px; color: #cbd5e1; margin-bottom: 3px;">🧬 <b>Rút kinh nghiệm:</b> ${escHtml(learnedRule)}</div>` : ''}
          <div style="font-size: 11px; color: var(--purple-light);">
            🎯 <b>Đề tài mới khóa sẵn:</b> ${escHtml(d.next_topic)}
          </div>
          ${next2.length > 0 ? `<div style="font-size: 10.5px; color: var(--text-dim); margin-top: 2px;">🔄 Kế tiếp: ${escHtml(next2.join(' • '))}</div>` : ''}
        </td>
        <td style="text-align: right; white-space: nowrap;">
          <button class="btn btn-primary btn-sm" onclick="quickProduceSingleChannel('${escHtml(cid)}')" title="Chạy/Lấy lệnh sản xuất cặp 1 Long + Short cho kênh này">
            🎬 Sản Xuất
          </button>
          <button class="btn btn-secondary btn-sm" onclick="openChromeStudio('${escHtml(cid)}')" title="Mở Chrome YouTube Studio (Port ${c.cdp_port || 9222})">
            🚀 Studio
          </button>
        </td>
      </tr>
    `;
  }).join('');
}

function setSimpleFilter(filterKey) {
  state.simpleFilter = filterKey;
  document.querySelectorAll('.simple-pill-btn').forEach(b => b.classList.remove('active'));
  const activeBtn = document.getElementById(`spill-${filterKey}`);
  if (activeBtn) activeBtn.classList.add('active');
  renderSimpleHub();
}

function onSimpleSearch(val) {
  state.simpleSearch = (val || '').trim();
  renderSimpleHub();
}

function toggleWaveChannelCheckbox(channelId, checked) {
  const idx = state.selectedWaveChannels.indexOf(channelId);
  if (checked && idx === -1) {
    state.selectedWaveChannels.push(channelId);
  } else if (!checked && idx !== -1) {
    state.selectedWaveChannels.splice(idx, 1);
  }
  const presetEl = document.getElementById('simple-wave-preset');
  if (presetEl) presetEl.value = 'checked';
  updateSimpleCommandPreview('wave');
  renderSimpleHub();
}

function selectTop4FilteredForWave() {
  const filtered = getFilteredSimpleChannels().slice(0, 4);
  state.selectedWaveChannels = filtered.map(c => c.channel_id);
  const presetEl = document.getElementById('simple-wave-preset');
  if (presetEl) presetEl.value = 'checked';
  updateSimpleCommandPreview('wave');
  renderSimpleHub();
  showToast(`☑️ Đã chọn ${state.selectedWaveChannels.length} kênh đầu danh sách vào Ca chạy!`, 'success');
}

function onWavePresetChange(preset) {
  const all38 = getCanonical38ChannelsWithDiagnostics();
  if (preset === 'tier_a_top4') {
    state.selectedWaveChannels = all38.filter(c => c.diag.tier === 'tier_a').slice(0, 4).map(c => c.channel_id);
  } else if (preset === 'scale_top4') {
    state.selectedWaveChannels = all38.filter(c => c.diag.verdict === 'SCALE').slice(0, 4).map(c => c.channel_id);
  } else if (preset === 'repair_top4') {
    state.selectedWaveChannels = all38.filter(c => c.diag.verdict === 'REPAIR_FUNNEL').slice(0, 4).map(c => c.channel_id);
  }
  updateSimpleCommandPreview('wave');
  renderSimpleHub();
}

function buildSimpleModeCmd(mode) {
  if (mode === 'single') {
    const ch = (document.getElementById('simple-single-channel') || {}).value || 'ho_so_ky_la';
    const act = (document.getElementById('simple-single-action') || {}).value || 'bundle';
    return `${REPO_CD_PREFIX}python3 sys/tools/vp_fleet_manager.py --mode single --channel ${ch} --action ${act}`;
  }
  if (mode === 'wave') {
    const wSize = (document.getElementById('simple-wave-size') || {}).value || '4';
    const chs = state.selectedWaveChannels.length > 0
      ? state.selectedWaveChannels.slice(0, parseInt(wSize, 10)).join(',')
      : 'ban_do_quyen_luc,ho_so_ky_la,co_the_ke,su_ke_lai';
    return `${REPO_CD_PREFIX}python3 sys/tools/vp_fleet_manager.py --mode wave --channels ${chs} --wave-size ${wSize}`;
  }
  const scope = (document.getElementById('simple-queue-scope') || {}).value || 'all';
  return `${REPO_CD_PREFIX}python3 sys/tools/vp_fleet_manager.py --mode auto-queue --channels ${scope} --wave-size 4`;
}

function updateSimpleCommandPreview(mode) {
  const cmd = buildSimpleModeCmd(mode);
  const box = document.getElementById('simple-cmd-preview-box');
  if (box) box.innerText = cmd;
}

function copySimpleModeCmd(mode) {
  const cmd = buildSimpleModeCmd(mode);
  updateSimpleCommandPreview(mode);
  copyText(cmd, `✓ Đã sao chép lệnh (${mode}): ${cmd}`);
}

function buildOfflineFallbackPlan(mode, payload, cmd) {
  const all38 = getCanonical38ChannelsWithDiagnostics();
  const byId = {};
  all38.forEach(c => { byId[c.channel_id] = c; });

  let targets = [];
  const rawCh = String(payload.channels || 'all').trim();
  if (mode === 'single') {
    if (byId[rawCh]) targets = [byId[rawCh]];
  } else if (rawCh === 'all') {
    targets = all38;
  } else if (rawCh === 'vi') {
    targets = all38.filter(c => (c.language || (c.channel_id.startsWith('en_') ? 'en' : 'vi')) === 'vi');
  } else if (rawCh === 'en') {
    targets = all38.filter(c => (c.language || (c.channel_id.startsWith('en_') ? 'en' : 'vi')) === 'en');
  } else if (rawCh === 'tier_a') {
    targets = all38.filter(c => c.diag && c.diag.tier === 'tier_a');
  } else {
    targets = rawCh.split(',').map(s => byId[s.trim()]).filter(Boolean);
  }
  if (targets.length === 0 && all38.length > 0) targets = [all38[0]];

  const wSize = Math.max(1, parseInt(payload.wave_size || 4, 10));
  const effSize = mode === 'single' ? 1 : wSize;
  const act = payload.action || 'bundle';

  const makeSteps = (c) => {
    const cid = c.channel_id;
    const d = c.diag || {};
    const bp = d.episode_blueprint || {};
    const isEn = cid.startsWith('en_');
    const hyphenSlug = bp.hyphen_slug || cid.replace(/_/g, '-');
    const epTag = bp.episode_tag || d.episode_tag || 'ep01';
    const fxMode = bp.fx_mode || 'auto_niche';
    const longTitle = (bp.long_title || d.next_topic || `Tap moi ${cid}`).replace(/"/g, "'");
    const shortTitle = (bp.short_title || d.short_topic || `Short: ${longTitle}`).replace(/"/g, "'");
    const longJobId = bp.long_job_id || `${isEn ? 'en' : 'vn'}_${cid}_${epTag}_long`;
    const shortJobId = bp.short_job_id || `${isEn ? 'en' : 'vn'}_${cid}_${epTag}_short`;
    const specLongPath = bp.spec_long_path || `sys/channels/vn_rebuilt_style_specs/${hyphenSlug}/${cid}_${epTag}_long_spec.json`;
    const specShortPath = bp.spec_short_path || `sys/channels/vn_rebuilt_style_specs/${hyphenSlug}/${cid}_${epTag}_short_spec.json`;

    if (act === 'analytics') {
      return [
        `${REPO_CD_PREFIX}python3 sys/tools/youtube_dashboard.py --sync-map`,
        `${REPO_CD_PREFIX}python3 sys/tools/vp_fleet_manager.py --mode diagnose --channel ${cid}`
      ];
    }
    if (act === 'studio_sync') {
      return [
        `${REPO_CD_PREFIX}python3 sys/tools/youtube_dashboard.py --open-studio ${cid}`,
        `${REPO_CD_PREFIX}python3 sys/tools/youtube_dashboard.py --sync-map`
      ];
    }
    const longCmdVn = `${REPO_CD_PREFIX}python3 sys/tools/produce_vn_dual_mode.py --channel ${hyphenSlug} --mode long --job-id ${longJobId} --spec ${specLongPath} --fx-mode ${fxMode} --video-topic "${longTitle}"`;
    const shortCmdVn = `${REPO_CD_PREFIX}python3 sys/tools/produce_vn_dual_mode.py --channel ${hyphenSlug} --mode short --job-id ${shortJobId} --spec ${specShortPath} --fx-mode ${fxMode} --video-topic "${shortTitle}"`;
    const gateStep = `${REPO_CD_PREFIX}python3 sys/tools/youtube_dashboard.py --sync-map  # Đưa ${longJobId} & ${shortJobId} vào Cổng Duyệt Tab 2 (chỉ chạy publish_youtube_cdp.py --channel ${cid} sau khi bấm APPROVED)`;

    if (act === 'short_only') {
      return [
        isEn
          ? `${REPO_CD_PREFIX}python3 sys/tools/produce_en_flow_dynamic_demo.py --demo-key ${hyphenSlug}:9x16`
          : shortCmdVn,
        gateStep
      ];
    }
    if (act === 'long_only') {
      return [
        isEn
          ? `${REPO_CD_PREFIX}python3 sys/tools/produce_en_flow_dynamic_demo.py --demo-key ${hyphenSlug}:16x9`
          : longCmdVn,
        gateStep
      ];
    }
    const prod = isEn
      ? [
          `${REPO_CD_PREFIX}python3 sys/tools/produce_en_flow_dynamic_demo.py --demo-key ${hyphenSlug}:16x9`,
          `${REPO_CD_PREFIX}python3 sys/tools/produce_en_flow_dynamic_demo.py --demo-key ${hyphenSlug}:9x16`
        ]
      : [longCmdVn, shortCmdVn];
    return [
      `${REPO_CD_PREFIX}python3 sys/tools/youtube_dashboard.py --sync-map`,
      ...prod,
      gateStep
    ];
  };

  const waves = [];
  for (let i = 0; i < targets.length; i += effSize) {
    const chunk = targets.slice(i, i + effSize);
    waves.push({
      wave_index: Math.floor(i / effSize) + 1,
      channels: chunk.map(c => c.channel_id),
      channels_count: chunk.length,
      status: 'READY',
      items: chunk.map(c => {
        const d = c.diag || {};
        const bp = d.episode_blueprint || {};
        return {
          channel_id: c.channel_id,
          channel_name: c.channel_name || c.channel_id,
          language: c.language || (c.channel_id.startsWith('en_') ? 'en' : 'vi'),
          verdict: d.verdict || 'COLLECT',
          verdict_label: d.verdict_label || '🔵 COLLECT (Tạo thêm bài)',
          diagnosis_summary: d.diagnosis_summary || '',
          episode_tag: bp.episode_tag || d.episode_tag || 'ep01',
          short_topic: bp.short_title || d.short_topic || '',
          thumbnail_text: bp.thumbnail_text || d.thumbnail_text || '',
          episode_blueprint: bp,
          execution_mode: 'AUTO',
          fx_mode: bp.fx_mode || 'auto_niche',
          next_topic: d.next_topic || '',
          hook_3s_formula: d.hook_3s_formula || '',
          learning: d.learning || c.learning_summary || {},
          fresh_topic_queue: d.fresh_topic_queue || [],
          channel_views: c.channel_views || 0,
          steps: makeSteps(c)
        };
      })
    });
  }

  const firstItem = (waves[0] && waves[0].items && waves[0].items[0]) ? waves[0].items[0] : {};
  const firstBp = firstItem.episode_blueprint || {};
  const firstLearn = firstItem.learning || {};
  const firstAudit = firstLearn.change_impact_audit || {};
  const ai_autonomous_contract = {
    zero_question_mode: true,
    execution_mode: 'AUTO',
    fx_mode: 'auto_niche',
    post_render_gate: 'PENDING_REVIEW_TAB_2',
    auto_create_missing_spec: true,
    directive_vi: 'CHẾ ĐỘ THỰC THI: AUTO (Tự động 100% — KHÔNG HỎI LẠI USER về Đề tài, Chế độ Auto/Review, hay FX Mode)',
    locked_episode_summary: `[${String(firstBp.episode_tag || firstItem.episode_tag || 'ep01').toUpperCase()}] Long: ${firstBp.long_title || firstItem.next_topic || ''} | Short: ${firstBp.short_title || firstItem.short_topic || ''} | Thumb: ${firstBp.thumbnail_text || firstItem.thumbnail_text || ''}`,
    learning_feedback_applied: firstLearn.learned_rule_vi || '',
    impact_audit_status: firstAudit.impact_badge_vi || '',
    technical_contract: `--fx-mode auto_niche | Nguồn đề tài từ fresh_topic_queue + channel_learning_ledger.json; tự động khởi tạo spec tại ${firstBp.spec_long_path || ''} và ${firstBp.spec_short_path || ''} nếu chưa có -> chạy produce_vn_dual_mode.py -> dừng ở cổng PENDING_REVIEW trên Dashboard.`
  };

  return {
    status: 'OFFLINE_READY',
    mode,
    action: act,
    total_channels: targets.length,
    total_waves: waves.length,
    active_command: cmd,
    ai_autonomous_contract,
    waves
  };
}

function renderSimpleActionResultPanel(plan, opts = {}) {
  const panel = document.getElementById('simple-action-result-panel');
  const titleEl = document.getElementById('simple-result-title');
  const badgeEl = document.getElementById('simple-result-conn-badge');
  const bodyEl = document.getElementById('simple-result-body');
  if (!panel || !bodyEl || !plan) return;

  const isOnline = Boolean(opts.online);
  panel.style.display = 'block';
  panel.style.borderColor = isOnline ? 'rgba(16, 185, 129, 0.55)' : 'rgba(245, 158, 11, 0.55)';

  if (badgeEl) {
    badgeEl.innerText = isOnline
      ? '✅ Đã kết nối Server (:8765) & lưu hàng đợi'
      : 'ℹ️ Offline HTML — Copy lệnh dán Terminal (hoặc bật Server :8765)';
    badgeEl.style.borderColor = isOnline ? 'rgba(16, 185, 129, 0.6)' : 'rgba(245, 158, 11, 0.6)';
    badgeEl.style.color = isOnline ? '#34d399' : '#fbbf24';
  }

  const modeNames = {
    single: 'Chạy Chuyên Sâu 1 Kênh',
    wave: 'Chạy 1 Ca Song Song',
    auto_queue: 'Dây Chuyền Cuốn Chiếu',
    diagnose: 'Báo Cáo Chẩn Đoán 38 Kênh'
  };
  if (titleEl) {
    const lbl = modeNames[plan.mode] || plan.mode || 'Kết quả điều phối';
    titleEl.innerText = `🚀 ${lbl} (${plan.total_channels || 0} kênh · ${plan.total_waves || (plan.waves ? plan.waves.length : 1)} ca)`;
  }

  const diagMap = {};
  getCanonical38ChannelsWithDiagnostics().forEach(c => { diagMap[c.channel_id] = c; });

  const contract = plan.ai_autonomous_contract || {};
  const contractHtml = (contract.directive_vi || (plan.waves && plan.waves.length > 0))
    ? `
      <div style="background:rgba(16,185,129,0.10); border:1px solid rgba(16,185,129,0.45); border-radius:10px; padding:10px 12px; margin-bottom:10px;">
        <div style="font-size:12.5px; font-weight:800; color:#34d399;">
          🤖 Hợp Đồng Thực Thi Tự Động (Không Hỏi Lại): Chế độ ${escHtml(contract.execution_mode || 'AUTO')} • <code>--fx-mode ${escHtml(contract.fx_mode || 'auto_niche')}</code> • Đã khóa Đề tài &amp; Tập mới
        </div>
        ${contract.locked_episode_summary ? `<div style="margin-top:4px; font-size:12px; color:#f8fafc;">🎯 <b>Đề tài khóa:</b> ${escHtml(contract.locked_episode_summary)}</div>` : ''}
        ${contract.learning_feedback_applied ? `<div style="margin-top:3px; font-size:11.5px; color:#38bdf8;">🧬 <b>Kinh nghiệm áp dụng:</b> ${contract.impact_audit_status ? `[${escHtml(contract.impact_audit_status)}] ` : ''}${escHtml(contract.learning_feedback_applied)}</div>` : ''}
        ${contract.technical_contract ? `<div style="margin-top:2px; font-size:11.5px; color:#cbd5e1;">⚙️ ${escHtml(contract.technical_contract)}</div>` : ''}
      </div>
    `
    : '';

  const waves = Array.isArray(plan.waves) ? plan.waves : [];
  const previewWaves = waves.slice(0, 4);
  const itemsHtml = previewWaves.map(w => {
    const itemCards = (w.items || []).map(it => {
      const chMeta = diagMap[it.channel_id] || {};
      const chDiag = chMeta.diag || {};
      const bp = it.episode_blueprint || chDiag.episode_blueprint || {};
      const chName = it.channel_name || chMeta.channel_name || it.channel_id;
      const verdictLbl = it.verdict_label || chDiag.verdict_label || '🔵 COLLECT';
      const summary = it.diagnosis_summary || chDiag.diagnosis_summary || '';
      const nextTopic = it.next_topic || chDiag.next_topic || '';
      const longTitle = bp.long_title || '';
      const shortTitle = bp.short_title || it.short_topic || '';
      const thumbTxt = bp.thumbnail_text || it.thumbnail_text || '';
      const epTag = String(bp.episode_tag || it.episode_tag || '').toUpperCase();
      const learn = it.learning || chDiag.learning || chMeta.learning_summary || {};
      const audit = learn.change_impact_audit || {};
      const impactBadge = audit.impact_badge_vi || learn.impact_badge_vi || '';
      const impactSum = audit.impact_summary_vi || learn.impact_summary_vi || '';
      const learnedRule = learn.learned_rule_vi || '';
      const views = it.channel_views ?? chMeta.channel_views ?? 0;
      const stepsHtml = (it.steps || []).map((st, idx) => `
        <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; background:rgba(2,6,23,0.75); border:1px solid rgba(255,255,255,0.08); border-radius:6px; padding:5px 8px; margin-top:4px;">
          <code style="font-size:11.5px; color:#38bdf8; word-break:break-all;">${idx + 1}. ${escHtml(st)}</code>
          <button class="btn-copy-mini" onclick="copyText(${JSON.stringify(st)}, '✓ Đã sao chép bước ${idx + 1}!')">📋 Copy</button>
        </div>
      `).join('');

      return `
        <div style="background:rgba(30,41,59,0.55); border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:10px 12px; margin-top:8px;">
          <div style="display:flex; align-items:center; justify-content:space-between; gap:8px; flex-wrap:wrap;">
            <div>
              <strong style="color:#f8fafc; font-size:13px;">${escHtml(chName)}</strong>
              <span style="font-size:11px; color:var(--text-dim);">(${escHtml(it.channel_id)} · ${formatNumber(views)} views)</span>
              ${epTag ? `<span class="v-badge" style="margin-left:6px; border-color:rgba(16,185,129,0.5); color:#34d399;">${escHtml(epTag)} • AUTO • ${escHtml(bp.fx_mode || it.fx_mode || 'auto_niche')}</span>` : ''}
            </div>
            <span class="verdict-badge verdict-${escHtml(it.verdict || chDiag.verdict || 'COLLECT')}">${escHtml(verdictLbl)}</span>
          </div>
          ${summary ? `<div style="margin-top:4px; color:#cbd5e1;">🧠 <b>Chẩn đoán:</b> ${escHtml(summary)}</div>` : ''}
          ${impactBadge ? `<div style="margin-top:3px; font-size:11.5px; color:#38bdf8;">📊 <b>Kiểm chứng thay đổi:</b> ${escHtml(impactBadge)}${impactSum ? ` <span style="color:#94a3b8;">— ${escHtml(impactSum)}</span>` : ''}</div>` : ''}
          ${learnedRule ? `<div style="margin-top:2px; font-size:11.5px; color:#e2e8f0;">🧬 <b>Rút kinh nghiệm:</b> ${escHtml(learnedRule)}</div>` : ''}
          ${longTitle ? `<div style="margin-top:3px; color:#e9d5ff;">🎬 <b>Bài Long:</b> ${escHtml(longTitle)}${shortTitle ? ` <span style="color:#94a3b8;">|</span> <b>Short:</b> ${escHtml(shortTitle)}` : ''}${thumbTxt ? ` <span style="color:#94a3b8;">|</span> <b>Thumb:</b> <code>${escHtml(thumbTxt)}</code>` : ''}</div>` : (nextTopic ? `<div style="margin-top:2px; color:var(--purple-light);">💡 <b>Đề tài gợi ý:</b> ${escHtml(nextTopic)}</div>` : '')}
          <div style="margin-top:6px;">${stepsHtml}</div>
        </div>
      `;
    }).join('');

    return `
      <div style="margin-top:8px;">
        <div style="font-size:11.5px; font-weight:700; color:var(--primary-light);">
          📦 Ca ${w.wave_index} (${w.channels_count || (w.channels || []).length} kênh): ${escHtml((w.channels || []).join(', '))}
        </div>
        ${itemCards}
      </div>
    `;
  }).join('');

  const extraNote = waves.length > 4
    ? `<div style="margin-top:8px; font-size:11.5px; color:var(--text-muted);">... và ${waves.length - 4} ca tiếp theo trong hàng đợi cuốn chiếu.</div>`
    : '';

  bodyEl.innerHTML = contractHtml + itemsHtml + extraNote;
  if (opts.shouldScroll !== false) {
    panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

async function triggerSimpleFleetAction(mode) {
  const cmd = buildSimpleModeCmd(mode);
  updateSimpleCommandPreview(mode);

  let payload = { mode, wave_size: 4, action: 'bundle' };
  if (mode === 'single') {
    payload.channels = (document.getElementById('simple-single-channel') || {}).value || 'ho_so_ky_la';
    payload.action = (document.getElementById('simple-single-action') || {}).value || 'bundle';
  } else if (mode === 'wave') {
    const wSize = parseInt((document.getElementById('simple-wave-size') || {}).value || '4', 10);
    payload.wave_size = wSize;
    payload.channels = state.selectedWaveChannels.length > 0
      ? state.selectedWaveChannels.slice(0, wSize).join(',')
      : 'ban_do_quyen_luc,ho_so_ky_la,co_the_ke,su_ke_lai';
  } else {
    payload.channels = (document.getElementById('simple-queue-scope') || {}).value || 'all';
    payload.wave_size = 4;
  }

  try {
    const res = await fetch(`${API_BASE}/api/fleet-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      const data = await res.json();
      if (data.fleet_queue) {
        state.raw.fleet_queue = data.fleet_queue;
      }
      if (data.fleet_diagnostics) {
        state.raw.fleet_diagnostics = data.fleet_diagnostics;
      }
      renderSimpleHub();
      renderReferencesTab();
      const fq = data.fleet_queue || {};
      renderSimpleActionResultPanel(fq, { online: true, shouldScroll: true });
      showToast(`🚀 Đã lên lịch ${fq.total_channels || 1} kênh (${fq.total_waves || 1} ca chạy)!`, 'success');
      return;
    }
  } catch (err) {
    console.log('Offline fleet action fallback:', err.message);
  }
  const fallbackPlan = buildOfflineFallbackPlan(mode, payload, cmd);
  state.raw.fleet_queue = fallbackPlan;
  renderSimpleHub();
  renderSimpleActionResultPanel(fallbackPlan, { online: false, shouldScroll: true });
  copyText(cmd, `⚡ Đã hiển thị chi tiết & copy lệnh: ${cmd}`);
}

function quickProduceSingleChannel(channelId) {
  const singleSel = document.getElementById('simple-single-channel');
  if (singleSel) singleSel.value = channelId;
  triggerSimpleFleetAction('single');
}

function openChannelReview(channelId) {
  state.channelFilter = channelId;
  const sel = document.getElementById('filter-channel');
  if (sel) sel.value = channelId;
  switchTab('tab-review');
}

async function runFleetDiagnosisNow() {
  showToast('🧠 Đang chạy AI chẩn đoán & cập nhật kế hoạch cải thiện cho 38 kênh...', 'info');
  try {
    const res = await fetch(`${API_BASE}/api/fleet-action`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode: 'diagnose' })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.fleet_diagnostics) state.raw.fleet_diagnostics = data.fleet_diagnostics;
      renderSimpleHub();
      renderReferencesTab();
      const top4 = (data.fleet_diagnostics && Array.isArray(data.fleet_diagnostics.channels))
        ? data.fleet_diagnostics.channels.slice(0, 4).map(c => c.channel_id).join(',')
        : 'ban_do_quyen_luc,su_ke_lai,co_the_ke,ho_so_ky_la';
      const preview = buildOfflineFallbackPlan('wave', { channels: top4, wave_size: 4, action: 'bundle' }, `${REPO_CD_PREFIX}python3 sys/tools/vp_fleet_manager.py --mode diagnose`);
      preview.mode = 'diagnose';
      preview.total_channels = 38;
      renderSimpleActionResultPanel(preview, { online: true, shouldScroll: true });
      showToast('✓ Đã cập nhật chẩn đoán & đề tài tiếp theo cho 38 kênh!', 'success');
      return;
    }
  } catch (err) {
    console.log('Offline diagnose fallback:', err.message);
  }
  renderSimpleHub();
  const top4Off = getCanonical38ChannelsWithDiagnostics().slice(0, 4).map(c => c.channel_id).join(',');
  const previewOff = buildOfflineFallbackPlan('wave', { channels: top4Off, wave_size: 4, action: 'bundle' }, `${REPO_CD_PREFIX}python3 sys/tools/vp_fleet_manager.py --mode diagnose`);
  previewOff.mode = 'diagnose';
  previewOff.total_channels = 38;
  renderSimpleActionResultPanel(previewOff, { online: false, shouldScroll: true });
  showToast('✓ Đã làm mới bảng chẩn đoán 38 kênh!', 'success');
}

function toggleAdvancedDashboardView() {
  state.hideAdvancedTabs = false;
  switchTab('tab-fleet');
}

// ==============================================================================
// TAB 6: VIDEO REVIEW & PRE-PUBLISH APPROVAL GATE ENGINE
// ==============================================================================
function getReviewQueueItems() {
  if (!state.raw || !state.raw.review_queue || !state.raw.review_queue.items) {
    return [];
  }
  return Object.values(state.raw.review_queue.items);
}

function getFilteredReviewItems() {
  const allItems = getReviewQueueItems();
  const q = (state.searchQuery || '').toLowerCase();
  return allItems.filter(item => {
    if (state.reviewStatusFilter !== 'all' && item.status !== state.reviewStatusFilter) {
      return false;
    }
    if (state.channelFilter !== 'all' && item.channel_id !== state.channelFilter) {
      return false;
    }
    if (state.formatFilter === 'long' && item.format_profile !== 'long_16x9') {
      return false;
    }
    if (state.formatFilter === 'short' && item.format_profile !== 'short_9x16') {
      return false;
    }
    if (q) {
      const hay = `${item.job_id || ''} ${item.channel_name || ''} ${item.channel_id || ''} ${item.title || ''} ${item.competitor_formula || ''} ${item.review_notes || ''}`.toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
}

function onReviewStatusFilterChange(val) {
  state.reviewStatusFilter = val || 'all';
  renderReviewTab();
}

function getMediaUrlForJob(item, kind) {
  const jobId = item.job_id || '';
  const isHttp = window.location.protocol.startsWith('http');
  const ver = encodeURIComponent(item.updated_at || '');
  const qs = ver ? `?v=${ver}` : '';
  if (kind === 'mp4') {
    if (isHttp) return `/media/${encodeURIComponent(jobId)}/${encodeURIComponent(jobId)}.mp4${qs}`;
    return item.mp4_path ? `file://${item.mp4_path}` : '';
  }
  if (kind === 'thumb') {
    const thumbFile = item.format_profile === 'short_9x16' ? 'thumbnail_9x16.jpg' : 'thumbnail_16x9.jpg';
    if (isHttp) return `/media/${encodeURIComponent(jobId)}/${thumbFile}${qs}`;
    return item.thumbnail_path ? `file://${item.thumbnail_path}` : '';
  }
  return '';
}

function renderReviewTab() {
  const allItems = getReviewQueueItems();
  const totalCnt = allItems.length;
  const pendingCnt = allItems.filter(i => i.status === 'PENDING_REVIEW').length;
  const approvedCnt = allItems.filter(i => i.status === 'APPROVED' || i.status === 'PUBLISHED').length;
  const rejectedCnt = allItems.filter(i => i.status === 'REJECTED').length;

  const badgeTab = document.getElementById('count-tab-review');
  if (badgeTab) badgeTab.textContent = String(pendingCnt > 0 ? pendingCnt : totalCnt);
  const badgeHeader = document.getElementById('header-review-count');
  if (badgeHeader) badgeHeader.textContent = String(pendingCnt > 0 ? `${pendingCnt} chờ duyệt` : `${totalCnt}`);

  const elTot = document.getElementById('rev-stat-total');
  const elPend = document.getElementById('rev-stat-pending');
  const elApp = document.getElementById('rev-stat-approved');
  const elRej = document.getElementById('rev-stat-rejected');
  if (elTot) elTot.textContent = String(totalCnt);
  if (elPend) elPend.textContent = String(pendingCnt);
  if (elApp) elApp.textContent = String(approvedCnt);
  if (elRej) elRej.textContent = String(rejectedCnt);

  const grid = document.getElementById('review-cards-grid');
  if (!grid) return;

  const filtered = getFilteredReviewItems();
  if (filtered.length === 0) {
    grid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: var(--text-muted); background: rgba(15,23,42,0.5); border-radius: 12px; border: 1px dashed rgba(255,255,255,0.12);">
        Không tìm thấy video nào khớp bộ lọc hiện tại.
      </div>
    `;
    return;
  }

  grid.innerHTML = filtered.map(item => {
    const jid = item.job_id || '';
    const st = item.status || 'PENDING_REVIEW';
    const isShort = item.format_profile === 'short_9x16';
    const fmtBadge = isShort
      ? `<span style="background: rgba(139, 92, 246, 0.2); color: #c4b5fd; border: 1px solid rgba(139,92,246,0.4); padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700;">📱 Short 9:16</span>`
      : `<span style="background: rgba(59, 130, 246, 0.2); color: #93c5fd; border: 1px solid rgba(59,130,246,0.4); padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: 700;">🖥️ Long 16:9</span>`;

    let statusPill = `<span style="background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245,158,11,0.45); padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 800;">⏳ CHỜ DUYỆT (PENDING)</span>`;
    let borderCol = 'rgba(255, 255, 255, 0.1)';
    if (st === 'APPROVED' || st === 'PUBLISHED') {
      statusPill = `<span style="background: rgba(16, 185, 129, 0.22); color: #34d399; border: 1px solid rgba(16,185,129,0.55); padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 800;">✅ ĐÃ DUYỆT ĐĂNG (APPROVED)</span>`;
      borderCol = 'rgba(16, 185, 129, 0.55)';
    } else if (st === 'REJECTED') {
      statusPill = `<span style="background: rgba(239, 68, 68, 0.22); color: #f87171; border: 1px solid rgba(239,68,68,0.55); padding: 3px 10px; border-radius: 999px; font-size: 11.5px; font-weight: 800;">❌ KHÔNG DUYỆT / CẦN SỬA</span>`;
      borderCol = 'rgba(239, 68, 68, 0.55)';
    }

    const mp4Url = getMediaUrlForJob(item, 'mp4');
    const thumbUrl = getMediaUrlForJob(item, 'thumb');
    const approveActiveStyle = st === 'APPROVED'
      ? 'background: #10b981; color: #022c22; font-weight: 800; border: 1px solid #34d399;'
      : 'background: rgba(16, 185, 129, 0.12); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4);';
    const rejectActiveStyle = st === 'REJECTED'
      ? 'background: #ef4444; color: #fff; font-weight: 800; border: 1px solid #f87171;'
      : 'background: rgba(239, 68, 68, 0.12); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4);';

    return `
      <div style="background: rgba(15, 23, 42, 0.82); border: 2px solid ${borderCol}; border-radius: 14px; padding: 14px; display: flex; flex-direction: column; gap: 10px;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; flex-wrap: wrap;">
          <div style="display: flex; align-items: center; gap: 6px; flex-wrap: wrap;">
            <span style="font-size: 14px; font-weight: 800; color: var(--text-white);">${escHtml(item.channel_name || item.channel_id)}</span>
            ${fmtBadge}
            <span style="font-size: 11px; color: var(--text-muted);">⏱️ ${formatDuration(item.duration_sec)} (${Number(item.duration_sec || 0).toFixed(1)}s)</span>
          </div>
          ${statusPill}
        </div>

        <div style="font-size: 13.5px; font-weight: 700; color: #f8fafc; line-height: 1.4;">
          ${escHtml(item.title || jid)}
        </div>

        <div style="background: #020617; border-radius: 10px; overflow: hidden; border: 1px solid rgba(255,255,255,0.08); display: flex; justify-content: center; align-items: center;">
          <video controls preload="metadata" poster="${escHtml(thumbUrl)}" style="width: 100%; max-height: 280px; object-fit: contain; background: #000;">
            <source src="${escHtml(mp4Url)}" type="video/mp4">
          </video>
        </div>

        <div style="font-size: 11.5px; color: var(--text-muted); background: rgba(30, 41, 59, 0.55); padding: 7px 10px; border-radius: 8px;">
          <b>🎯 Công thức kênh mẫu:</b> ${escHtml(item.competitor_formula || 'Standard High-Retention Formula')}
          <div style="margin-top: 3px; font-family: monospace; font-size: 10.5px; color: #94a3b8;">Job ID: ${escHtml(jid)}</div>
        </div>

        <!-- NÚT BẤM DUYỆT ĐĂNG / KHÔNG DUYỆT -->
        <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 2px;">
          <button class="btn btn-sm" style="flex: 1; justify-content: center; padding: 8px 10px; cursor: pointer; border-radius: 8px; ${approveActiveStyle}"
                  onclick="setVideoReviewStatus('${escHtml(jid)}', 'APPROVED')">
            ✅ Duyệt đăng (APPROVED)
          </button>
          <button class="btn btn-sm" style="flex: 1; justify-content: center; padding: 8px 10px; cursor: pointer; border-radius: 8px; ${rejectActiveStyle}"
                  onclick="setVideoReviewStatus('${escHtml(jid)}', 'REJECTED')">
            ❌ Không duyệt / Cần sửa
          </button>
          <button class="btn btn-secondary btn-sm" style="padding: 8px 10px; cursor: pointer; border-radius: 8px;"
                  onclick="setVideoReviewStatus('${escHtml(jid)}', 'PENDING_REVIEW')" title="Đặt lại chờ duyệt">
            ⏳
          </button>
        </div>

        <!-- Ô NHẬP GHI CHÚ LỖI CẦN SỬA -->
        <div style="display: flex; flex-direction: column; gap: 5px;">
          <div style="display: flex; justify-content: space-between; align-items: center;">
            <label style="font-size: 11.5px; font-weight: 700; color: #cbd5e1;">
              📝 Ghi chú lỗi cần sửa (review_notes — dùng để sửa tự động nếu Không duyệt):
            </label>
            <button class="btn btn-secondary btn-sm" style="padding: 2px 8px; font-size: 11px;"
                    onclick="saveVideoReviewNotes('${escHtml(jid)}')">
              💾 Lưu ghi chú
            </button>
          </div>
          <textarea id="review-notes-${escHtml(jid)}" rows="2"
                    placeholder="Nhập lỗi cần sửa (ví dụ: giọng đọc đoạn đầu hơi nhanh, đổi ảnh cảnh 2, sửa tiêu đề)..."
                    onblur="saveVideoReviewNotes('${escHtml(jid)}', true)"
                    style="width: 100%; background: rgba(2, 6, 23, 0.75); border: 1px solid rgba(255,255,255,0.14); border-radius: 8px; color: #f8fafc; padding: 7px 10px; font-size: 12px; resize: vertical;">${escHtml(item.review_notes || '')}</textarea>
        </div>
      </div>
    `;
  }).join('');
}

async function setVideoReviewStatus(jobId, status) {
  if (!state.raw || !state.raw.review_queue || !state.raw.review_queue.items) return;
  const item = state.raw.review_queue.items[jobId];
  if (!item) return;

  const notesEl = document.getElementById(`review-notes-${jobId}`);
  const notesVal = notesEl ? notesEl.value.trim() : (item.review_notes || '');

  item.status = status;
  item.review_notes = notesVal;
  renderReviewTab();

  try {
    const res = await fetch(`${API_BASE}/api/review-decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, status: status, review_notes: notesVal })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.review_queue) state.raw.review_queue = data.review_queue;
      renderReviewTab();
      const label = status === 'APPROVED' ? '✅ ĐÃ DUYỆT ĐĂNG' : (status === 'REJECTED' ? '❌ KHÔNG DUYỆT (CẦN SỬA)' : '⏳ CHỜ DUYỆT');
      showToast(`${label}: ${jobId}`, status === 'APPROVED' ? 'success' : (status === 'REJECTED' ? 'error' : 'info'));
      return;
    }
  } catch (err) {
    console.log('Offline review save fallback:', err.message);
  }
  showToast(`Đã cập nhật trạng thái ${status} cho ${jobId}`, 'info');
}

async function saveVideoReviewNotes(jobId, silentIfUnchanged = false) {
  if (!state.raw || !state.raw.review_queue || !state.raw.review_queue.items) return;
  const item = state.raw.review_queue.items[jobId];
  if (!item) return;

  const notesEl = document.getElementById(`review-notes-${jobId}`);
  const notesVal = notesEl ? notesEl.value.trim() : '';
  if (silentIfUnchanged && notesVal === (item.review_notes || '')) return;

  item.review_notes = notesVal;
  try {
    const res = await fetch(`${API_BASE}/api/review-decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ job_id: jobId, status: item.status || 'PENDING_REVIEW', review_notes: notesVal })
    });
    if (res.ok) {
      showToast(`💾 Đã lưu ghi chú cho ${jobId}`, 'success');
      return;
    }
  } catch (err) {
    console.log('Offline note save:', err.message);
  }
  showToast(`💾 Đã lưu ghi chú tạm cho ${jobId}`, 'info');
}

async function approveAllFilteredReviewVideos() {
  const filtered = getFilteredReviewItems();
  if (filtered.length === 0) return;

  const decisions = {};
  filtered.forEach(item => {
    item.status = 'APPROVED';
    decisions[item.job_id] = { status: 'APPROVED', review_notes: item.review_notes || '' };
  });
  renderReviewTab();

  try {
    const res = await fetch(`${API_BASE}/api/review-decision`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ decisions })
    });
    if (res.ok) {
      const data = await res.json();
      if (data.review_queue) state.raw.review_queue = data.review_queue;
      renderReviewTab();
      showToast(`✅ Đã duyệt đăng ${filtered.length} video đang hiển thị!`, 'success');
      return;
    }
  } catch (err) {
    console.log('Bulk approve fallback:', err.message);
  }
  showToast(`✅ Đã đánh dấu duyệt ${filtered.length} video!`, 'success');
}

function exportReviewDecisionsJSON() {
  const allItems = getReviewQueueItems();
  const payload = {
    exported_at: new Date().toISOString(),
    decisions: {}
  };
  allItems.forEach(item => {
    payload.decisions[item.job_id] = {
      status: item.status || 'PENDING_REVIEW',
      review_notes: item.review_notes || ''
    };
  });
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'review_decisions.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast('💾 Đã xuất tệp review_decisions.json!', 'success');
}

// --- API ACTIONS ---
async function refreshMetrics() {
  const btn = document.getElementById('btn-refresh');
  const oldText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span> Đang cào dữ liệu...`;
  showToast('Đang quét chỉ số live từ YouTube cho toàn bộ kênh...', 'info');

  try {
    const res = await fetch(`${API_BASE}/api/refresh`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    renderDashboard(data);
    showToast('✓ Đã cập nhật chỉ số live thành công!', 'success');
  } catch (err) {
    console.error('Refresh failed:', err);
    showToast(`Không thể kết nối API refresh (${err.message}). Vui lòng chạy lệnh --serve!`, 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = oldText;
  }
}

async function syncChannelMap() {
  const btn = document.getElementById('btn-sync');
  const oldText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span> Đang đồng bộ...`;
  showToast('Đang đồng bộ dữ liệu từ youtube_channel_map.json...', 'info');

  try {
    const res = await fetch(`${API_BASE}/api/sync-map`, { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.metrics || data.snapshot) renderDashboard(data.metrics || data.snapshot);
    showToast('✓ Đã đồng bộ video từ youtube_channel_map.json!', 'success');
  } catch (err) {
    console.error('Sync failed:', err);
    showToast(`API đồng bộ chưa sẵn sàng: ${err.message}`, 'info');
  } finally {
    btn.disabled = false;
    btn.innerHTML = oldText;
  }
}

async function openChromeStudio(channelId) {
  showToast(`Đang mở Chrome Studio cho kênh ${channelId}...`, 'info');
  try {
    const res = await fetch(`${API_BASE}/api/open-studio`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ channel_id: channelId })
    });
    const result = await res.json();
    if (result.status === 'ok') {
      showToast(`✓ ${result.message}`, 'success');
    } else {
      showToast(`⚠️ ${result.message || 'Không thể mở Chrome Studio'}`, 'error');
    }
  } catch (err) {
    showToast(`Lỗi gọi API mở Studio: ${err.message}`, 'error');
  }
}

function copyServerCommand() {
  const cmd = `${REPO_CD_PREFIX}python3 sys/tools/youtube_dashboard.py --serve --port 8765`;
  copyText(cmd, '✓ Đã sao chép lệnh khởi chạy server: ' + cmd);
}

function copyText(str, msg = '✓ Đã sao chép vào bộ nhớ tạm!') {
  if (!str) return;
  navigator.clipboard.writeText(str).then(() => {
    showToast(msg, 'success');
  }).catch(() => {
    // fallback
    const ta = document.createElement('textarea');
    ta.value = str;
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
    showToast(msg, 'success');
  });
}

// --- CSV EXPORT FUNCTION ---
function exportCatalogCSV() {
  const videos = getFilteredVideos();
  if (!videos || videos.length === 0) {
    showToast('Không có video nào trong danh sách lọc để xuất!', 'warning');
    return;
  }

  const headers = [
    'Mã Video',
    'Tiêu Đề',
    'Định Dạng',
    'Đợt (Batch)',
    'Kênh',
    'Handle',
    'Cổng CDP',
    'Lượt Xem',
    'Lượt Thích',
    'Tỷ Lệ Tương Tác (%)',
    'Thời Lượng',
    'Ngày Xuất Bản',
    'Trạng Thái',
    'Link Video',
    'Link Phễu (Related Video)',
    'Job ID'
  ];

  const rows = videos.map(v => [
    v.video_id || '',
    (v.title || '').replace(/"/g, '""'),
    (v.is_short ? 'Short 9:16' : 'Long 16:9'),
    v.batch_label || v.batch || 'week1',
    v.channel_name || '',
    v.handle || '',
    v.cdp_port || '',
    v.view_count || 0,
    v.like_count || 0,
    v.engagement_rate || '0.0%',
    v.duration_formatted || formatDuration(v.length_seconds),
    v.publish_date || v.published_at || '',
    v.is_public !== false ? 'Public' : 'Unlisted',
    v.video_url || (v.video_id ? 'https://youtu.be/' + v.video_id : ''),
    v.related_video_url || '',
    v.job_id || ''
  ]);

  const csvContent = '\\uFEFF' + [
    headers.map(h => `"${h}"`).join(','),
    ...rows.map(row => row.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(','))
  ].join('\\r\\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  const now = new Date().toISOString().slice(0, 19).replace(/[-:]/g, '').replace('T', '_');
  a.href = url;
  a.download = `video_pilot_fleet_catalog_${now}.csv`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
  showToast(`✓ Đã xuất thành công ${videos.length} video ra tệp CSV!`, 'success');
}

// --- BOOTSTRAP INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
  // If embedded data is injected
  if (window.__INITIAL_DASHBOARD_DATA__) {
    renderDashboard(window.__INITIAL_DASHBOARD_DATA__);
  }

  if (window.location.hash === '#review' || window.location.search.includes('tab=review')) {
    switchTab('tab-review');
  }

  // Sync latest live metrics (works both via HTTP server and file:// when local :8765 server is up)
  fetch(`${API_BASE}/api/metrics`)
    .then(res => {
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      return res.json();
    })
    .then(data => renderDashboard(data))
    .catch(err => console.log('Live fetch note:', err.message));
});
</script>
</body>
</html>
"""


def get_dashboard_html(embedded_data: Optional[Dict[str, Any]] = None) -> str:
    """Generate the complete self-contained HTML document for Video Pilot Dashboard.

    Parameters
    ----------
    embedded_data : Optional[Dict[str, Any]]
        Pre-collected dashboard snapshot dictionary. If supplied, it will be safely
        serialized and embedded in the HTML document so that the dashboard works
        100% offline without needing a running server.
    """
    if embedded_data is not None:
        enriched = dict(embedded_data)
        if "review_queue" not in enriched:
            try:
                from pathlib import Path
                rq_path = Path(__file__).resolve().parents[1] / "channels" / "video_review_queue.json"
                if rq_path.is_file():
                    enriched["review_queue"] = json.loads(rq_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        safe_json = json.dumps(enriched, ensure_ascii=False).replace(
            "</", "<\\/"
        )
        embedded_script = f"""<script id="__INITIAL_DATA__" type="application/json">
{safe_json}
</script>
<script>
  window.__INITIAL_DASHBOARD_DATA__ = JSON.parse(document.getElementById('__INITIAL_DATA__').textContent);
</script>"""
    else:
        embedded_script = """<script>
  window.__INITIAL_DASHBOARD_DATA__ = null;
</script>"""

    return HTML_TEMPLATE.replace("<!-- {{EMBEDDED_DATA_SCRIPT}} -->", embedded_script)


if __name__ == "__main__":
    from pathlib import Path

    sample_metrics = Path("/home/hongphuoc6104/Desktop/vp-agent-core/sys/channels/dashboard_metrics.json")
    if sample_metrics.exists():
        data = json.loads(sample_metrics.read_text(encoding="utf-8"))
        html = get_dashboard_html(data)
        out_file = Path("/tmp/test_dashboard_v3.html")
        out_file.write_text(html, encoding="utf-8")
        print(f"Generated test dashboard at {out_file} ({len(html)} bytes)")
    else:
        print("Sample metrics not found, generating blank template...")
        html = get_dashboard_html(None)
        print(f"Generated blank HTML ({len(html)} bytes)")
