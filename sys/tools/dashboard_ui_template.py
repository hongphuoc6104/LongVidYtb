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
          Video Pilot V3
          <span class="v-badge">FLEET & CATALOG</span>
        </div>
        <div class="brand-subtitle">Scalable YouTube Multi-Channel Management • Batch Automation Architecture</div>
      </div>
    </div>

    <div class="header-status-group">
      <div class="live-pill" id="header-live-badge">
        <span class="live-dot"></span>
        <span id="header-fleet-status">8/8 Kênh Active</span>
      </div>
      <div style="color: var(--text-muted); font-size: 11.5px;" id="header-updated-at">
        Cập nhật: --:--
      </div>
    </div>

    <div class="header-actions">
      <button class="btn btn-primary" id="btn-refresh" onclick="refreshMetrics()">
        <span>↻</span> Làm mới chỉ số (Live Scrape)
      </button>
      <button class="btn btn-secondary" id="btn-sync" onclick="syncChannelMap()">
        <span>🔄</span> Đồng bộ Video Mới
      </button>
      <button class="btn btn-emerald" id="btn-export-csv" onclick="exportCatalogCSV()">
        <span>📥</span> Xuất CSV Kho Video
      </button>
      <button class="btn btn-secondary" onclick="copyServerCommand()">
        <span>📋</span> Lệnh Server (:8765)
      </button>
    </div>
  </div>
</header>

<div class="main-wrapper">

  <!-- 6 KPI SUMMARY CARDS -->
  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Kênh Hoạt Động</span>
        <span class="kpi-icon">🏢</span>
      </div>
      <div class="kpi-value" id="kpi-channels">8 / 8</div>
      <div class="kpi-subtitle" id="kpi-channels-subtitle">Hệ Thống Phân Phối Ngách</div>
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
        <span class="kpi-title">Tổng Lượt Xem</span>
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
        <span class="kpi-title">Tổng Lượt Thích</span>
        <span class="kpi-icon">👍</span>
      </div>
      <div class="kpi-value">
        <span id="kpi-likes">0</span>
        <span class="kpi-delta" id="kpi-likes-delta" style="display:none;">+0</span>
      </div>
      <div class="kpi-subtitle" id="kpi-likes-avg">TB: 0 views/video</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Tổng Subscribers</span>
        <span class="kpi-icon">👥</span>
      </div>
      <div class="kpi-value">
        <span id="kpi-subs">0</span>
        <span class="kpi-delta" id="kpi-subs-delta" style="display:none;">+0</span>
      </div>
      <div class="kpi-subtitle">Đồng Bộ Real-Time Từ YouTube</div>
    </div>

    <div class="kpi-card">
      <div class="kpi-header">
        <span class="kpi-title">Chuẩn Phễu V2</span>
        <span class="kpi-icon">🔗</span>
      </div>
      <div class="kpi-value" id="kpi-funnel">100%</div>
      <div class="kpi-subtitle" id="kpi-funnel-sub">0/0 Shorts gắn Related Long</div>
    </div>
  </section>

  <!-- STICKY GLOBAL NAVIGATION & FILTER BAR -->
  <nav class="nav-filter-bar">
    <div class="tabs-row">
      <div class="tabs-group">
        <button class="tab-btn active" id="btn-tab-fleet" onclick="switchTab('tab-fleet')">
          <span>🏢</span> 1. Tổng Quan Hệ Thống Kênh
          <span class="tab-count" id="count-tab-fleet">8</span>
        </button>
        <button class="tab-btn" id="btn-tab-catalog" onclick="switchTab('tab-catalog')">
          <span>🎬</span> 2. Kho Video Toàn Hệ Thống
          <span class="tab-count" id="count-tab-catalog">0</span>
        </button>
        <button class="tab-btn" id="btn-tab-funnel" onclick="switchTab('tab-funnel')">
          <span>🔗</span> 3. Ma Trận Phễu Long ↔ Short & Đợt Sản Xuất
          <span class="tab-count" id="count-tab-funnel">0</span>
        </button>
        <button class="tab-btn" id="btn-tab-ops" onclick="switchTab('tab-ops')">
          <span>⚡</span> 4. Điều Hành & Lịch Sử Tăng Trưởng
        </button>
        <button class="tab-btn" id="btn-tab-refs" onclick="switchTab('tab-refs')">
          <span>📚</span> 5. Kho Kênh Mẫu, Email & Đề Tài Gợi Ý
          <span class="tab-count" id="count-tab-refs">0</span>
        </button>
      </div>
    </div>

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
  </nav>

  <!-- ===================================================================== -->
  <!-- TAB 1: TỔNG QUAN HỆ THỐNG KÊNH -->
  <!-- ===================================================================== -->
  <div class="tab-pane active" id="tab-fleet">
    <!-- Fleet Views Comparison Bar Chart -->
    <div class="fleet-bar-chart-card">
      <div class="chart-title-row">
        <div class="chart-title" id="fleet-section-title">
          <span>📊</span> So Sánh Lượt Xem Hệ Thống Kênh
        </div>
        <div class="batch-summary-pills" id="batch-pills-container">
          <!-- Dynamic batch summary pills -->
        </div>
      </div>
      <div class="horizontal-chart-grid" id="fleet-chart-grid">
        <!-- Rendered via JS -->
      </div>
    </div>

    <!-- 8 Scalable Channel Cards Grid -->
    <div class="channels-grid" id="channels-card-grid">
      <!-- Rendered via JS -->
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- TAB 2: KHO VIDEO TOÀN HỆ THỐNG (MASTER PAGINATED CATALOG) -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-catalog">
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
  <!-- TAB 3: MA TRẬN PHỄU LONG ↔ SHORT & ĐỢT SẢN XUẤT -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-funnel">
    <!-- Batch Performance Comparison Cards -->
    <div class="batch-cards-grid" id="batch-performance-grid">
      <!-- Dynamic batch cards -->
    </div>

    <!-- Long ↔ Short Funnel Pairing Matrix -->
    <div style="margin-bottom: 14px; font-size: 15px; font-weight: 700; color: var(--text-white); display: flex; align-items: center; justify-content: space-between;">
      <span>🔗 Chi Tiết Các Cặp Phễu Long 16:9 ↔ Spin-off Short 9:16</span>
      <span style="font-size: 12px; color: var(--emerald-light); font-weight: 600;" id="funnel-matrix-compliance-badge">
        ✓ Chuẩn V2 Phễu Bắt Buộc
      </span>
    </div>

    <div class="funnel-pairs-container" id="funnel-pairs-grid">
      <!-- Rendered via JS -->
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- TAB 4: ĐIỀU HÀNH & LỊCH SỬ TĂNG TRƯỞNG -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-ops">
    <div class="ops-grid">
      <!-- CLI Command Generator -->
      <div class="ops-card">
        <div class="ops-card-title">
          <span>🛠️</span> Bộ Tạo Lệnh Điều Hành Tự Động (Multi-T4 & CDP)
        </div>

        <div class="cli-form-group">
          <label class="cli-label">Kênh Mục Tiêu:</label>
          <select class="select-filter" id="cli-channel-select" onchange="generateCLICommand()">
            <option value="all">Tất cả 8 Kênh (Fleet-wide)</option>
          </select>
        </div>

        <div class="cli-form-group">
          <label class="cli-label">Đợt Sản Xuất (Batch):</label>
          <select class="select-filter" id="cli-batch-select" onchange="generateCLICommand()">
            <option value="batch2">batch2 (Đợt 2 - Hiện tại)</option>
            <option value="batch3">batch3 (Đợt 3 - Kế tiếp)</option>
            <option value="batch4">batch4 (Đợt 4)</option>
            <option value="week1">week1 (Đợt 1)</option>
          </select>
        </div>

        <div class="cli-form-group">
          <label class="cli-label">Hành Động Cần Thực Hiện:</label>
          <select class="select-filter" id="cli-action-select" onchange="generateCLICommand()">
            <option value="produce_long">1. Sản xuất Long 16:9 E2E (Multi-T4 Colab)</option>
            <option value="produce_short">2. Sản xuất Short 9:16 E2E (Multi-T4 Colab)</option>
            <option value="publish_cdp">3. Xuất bản YouTube CDP (Auto Upload + Phễu V2)</option>
            <option value="run_fleet">4. Chạy Toàn Bộ 8 Kênh Tự Động (run_fleet.py)</option>
            <option value="refresh_metrics">5. Quét / Cập nhật Chỉ số Live Scrape</option>
            <option value="serve_dashboard">6. Khởi chạy Server Web Dashboard (:8765)</option>
          </select>
        </div>

        <div class="cli-output-box" id="cli-output-text">
          python3 sys/tools/produce_channel_long_e2e.py --batch batch2
        </div>

        <button class="btn btn-primary" style="margin-top: 12px; width: 100%; justify-content: center;" onclick="copyCLICommand()">
          <span>📋</span> Sao Chép Lệnh Thực Thi
        </button>
      </div>

      <!-- Growth History Snapshots -->
      <div class="ops-card">
        <div class="ops-card-title">
          <span>📈</span> Lịch Sử Tăng Trưởng & Snapshots Đã Lưu
        </div>
        <div class="table-responsive" style="max-height: 300px; overflow-y: auto;">
          <table class="history-table">
            <thead>
              <tr>
                <th>Thời Điểm</th>
                <th>Tổng Vids</th>
                <th>Tổng Views</th>
                <th>Likes</th>
                <th>Subs</th>
                <th>Tăng Trưởng</th>
              </tr>
            </thead>
            <tbody id="history-table-body">
              <tr>
                <td colspan="6" style="text-align: center; color: var(--text-dim); padding: 20px;">
                  Chưa có dữ liệu lịch sử ghi nhận
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- CDP Ports & Chrome Studio Launcher Table -->
    <div class="ops-card">
      <div class="ops-card-title">
        <span>🚀</span> Quản Lý Cổng Chrome CDP & Khởi Chạy YouTube Studio (Toàn Bộ Kênh Độc Lập)
      </div>
      <div class="table-responsive">
        <table class="cdp-ports-table">
          <thead>
            <tr>
              <th>Kênh</th>
              <th>Handle & Wave</th>
              <th>Profile Chrome</th>
              <th>Cổng CDP</th>
              <th>Email Đăng Nhập</th>
              <th>Trạng Thái</th>
              <th style="text-align: right;">Khởi Chạy</th>
            </tr>
          </thead>
          <tbody id="cdp-ports-table-body">
            <!-- Rendered via JS -->
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- ===================================================================== -->
  <!-- TAB 5: KHO KÊNH MẪU, EMAIL & ĐỀ TÀI GỢI Ý -->
  <!-- ===================================================================== -->
  <div class="tab-pane" id="tab-refs">
    <div class="catalog-container">
      <div class="catalog-controls-bar">
        <div class="catalog-stats-info" style="font-size: 14px; font-weight: 700; color: var(--text-white); display: flex; align-items: center; gap: 8px;">
          <span>📚 Kho Kênh Mẫu, Nguồn Tham Khảo, Email Google & Đề Tài Hạt Giống</span>
          <span class="v-badge" id="references-count-badge">0 Kênh</span>
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

</div>

<!-- TOAST NOTIFICATION CONTAINER -->
<div class="toast-container" id="toast-container"></div>

<!-- {{EMBEDDED_DATA_SCRIPT}} -->

<script>
// ==============================================================================
// VIDEO PILOT V3 FRONTEND ENGINE
// Self-contained Vanilla JS • Zero CDN Dependencies
// ==============================================================================

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
  sortBy: 'views_desc',
  page: 1,
  pageSize: 20,
  expandedChannels: {},
  expandedReferences: {},
};

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

  // Flatten all_videos
  if (!Array.isArray(data.all_videos) || data.all_videos.length === 0) {
    data.all_videos = data.channels.flatMap(c => c.videos || []);
  }

  // Derive batches array if missing
  if (!Array.isArray(data.batches) || data.batches.length === 0) {
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

  // Calculate totals
  data.totals = data.totals || {};
  data.totals.total_channels = data.totals.total_channels || data.channels.length;
  data.totals.total_videos = data.totals.total_videos || data.all_videos.length;
  data.totals.total_long_videos = data.totals.total_long_videos ?? data.all_videos.filter(v => !v.is_short).length;
  data.totals.total_short_videos = data.totals.total_short_videos ?? data.all_videos.filter(v => v.is_short).length;
  data.totals.total_views = data.totals.total_views ?? data.all_videos.reduce((s, v) => s + (v.view_count || 0), 0);
  data.totals.long_views = data.totals.long_views ?? data.all_videos.filter(v => !v.is_short).reduce((s, v) => s + (v.view_count || 0), 0);
  data.totals.short_views = data.totals.short_views ?? data.all_videos.filter(v => v.is_short).reduce((s, v) => s + (v.view_count || 0), 0);
  data.totals.total_likes = data.totals.total_likes ?? data.all_videos.reduce((s, v) => s + (v.like_count || 0), 0);
  data.totals.total_subscribers = data.totals.total_subscribers ?? data.channels.reduce((s, c) => s + (c.subscriber_count || 0), 0);
  data.totals.avg_views_per_video = data.totals.avg_views_per_video ?? (data.totals.total_videos > 0 ? Math.round(data.totals.total_views / data.totals.total_videos) : 0);

  const shorts = data.all_videos.filter(v => v.is_short);
  const linked = shorts.filter(v => Boolean(v.has_funnel_link || v.related_video_id || v.related_video_url)).length;
  data.totals.funnel_total_shorts = data.totals.funnel_total_shorts ?? shorts.length;
  data.totals.funnel_linked_shorts = data.totals.funnel_linked_shorts ?? linked;
  data.totals.funnel_compliance_pct = data.totals.funnel_compliance_pct ?? (shorts.length > 0 ? Math.round((linked / shorts.length) * 100) : 100);

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
    'tab-refs': 'btn-tab-refs'
  };
  const activeBtn = document.getElementById(btnMap[tabId]);
  if (activeBtn) activeBtn.classList.add('active');

  const activePane = document.getElementById(tabId);
  if (activePane) activePane.classList.add('active');

  if (tabId === 'tab-catalog') {
    renderCatalogTable();
  } else if (tabId === 'tab-refs') {
    renderReferencesTab();
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

  const t = d.totals || {};
  const numCh = t.total_channels || d.channels.length || 0;
  document.getElementById('header-fleet-status').innerText = `${numCh}/${numCh} Kênh Active • ${t.total_videos || 0} Videos • ${(d.batches || []).length} Đợt`;

  if (d.generated_at) {
    const genDate = new Date(d.generated_at);
    document.getElementById('header-updated-at').innerText = `Cập nhật: ${genDate.toLocaleTimeString('vi-VN')} (${d.scrape_duration_seconds || 0}s)`;
  }

  document.getElementById('kpi-channels').innerText = `${numCh} / ${numCh}`;
  document.getElementById('kpi-videos').innerText = formatNumber(t.total_videos || 0);
  document.getElementById('kpi-videos-split').innerText = `${t.total_long_videos || 0} Long 16:9 · ${t.total_short_videos || 0} Short 9:16 (across ${(d.batches || []).length} Đợt)`;

  document.getElementById('kpi-views').innerText = formatNumber(t.total_views || 0);
  if (t.views_delta) {
    const el = document.getElementById('kpi-views-delta');
    el.innerText = `+${formatNumber(t.views_delta)}`;
    el.style.display = 'inline-block';
  }
  document.getElementById('kpi-views-split').innerText = `Shorts: ${formatNumber(t.short_views || 0)} · Longs: ${formatNumber(t.long_views || 0)}`;

  document.getElementById('kpi-likes').innerText = formatNumber(t.total_likes || 0);
  if (t.likes_delta) {
    const el = document.getElementById('kpi-likes-delta');
    el.innerText = `+${formatNumber(t.likes_delta)}`;
    el.style.display = 'inline-block';
  }
  document.getElementById('kpi-likes-avg').innerText = `TB: ${formatNumber(t.avg_views_per_video || 0)} views/video`;

  document.getElementById('kpi-subs').innerText = formatNumber(t.total_subscribers || 0);
  if (t.subs_delta) {
    const el = document.getElementById('kpi-subs-delta');
    el.innerText = `+${formatNumber(t.subs_delta)}`;
    el.style.display = 'inline-block';
  }

  const compliance = t.funnel_compliance_pct ?? 100;
  document.getElementById('kpi-funnel').innerText = `${compliance}% ✓`;
  document.getElementById('kpi-funnel-sub').innerText = `${t.funnel_linked_shorts || 0}/${t.funnel_total_shorts || 0} Shorts gắn Related Long`;

  // Counters in Tab Navigation
  document.getElementById('count-tab-fleet').innerText = numCh;
  document.getElementById('count-tab-catalog').innerText = t.total_videos || 0;

  const countTabRefs = document.getElementById('count-tab-refs');
  if (countTabRefs) countTabRefs.innerText = numCh;

  const totalPairs = d.channels.reduce((sum, ch) => sum + (ch.funnel_pairs ? ch.funnel_pairs.length : 0), 0);
  document.getElementById('count-tab-funnel').innerText = totalPairs;
}

// --- POPULATE DROPDOWNS ---
function populateDropdowns() {
  const d = state.raw;
  if (!d) return;

  const numCh = d.channels.length;

  // Channel dropdown
  const chSelect = document.getElementById('filter-channel');
  const cliChSelect = document.getElementById('cli-channel-select');
  const curChVal = chSelect.value;

  let chOptions = `<option value="all">Tất cả ${numCh} Kênh</option>`;
  let cliOptions = `<option value="all">Tất cả ${numCh} Kênh (Fleet-wide)</option>`;
  d.channels.forEach(ch => {
    chOptions += `<option value="${ch.channel_id}">${ch.channel_name} (${ch.handle || ''})</option>`;
    cliOptions += `<option value="${ch.channel_id}">${ch.channel_name} (${ch.channel_id})</option>`;
  });
  chSelect.innerHTML = chOptions;
  if (curChVal) chSelect.value = curChVal;
  if (cliChSelect) cliChSelect.innerHTML = cliOptions;

  // Batch dropdown
  const bSelect = document.getElementById('filter-batch');
  const cliBatchSelect = document.getElementById('cli-batch-select');
  const curBVal = bSelect.value;

  let bOptions = '<option value="all">Tất cả Đợt Sản Xuất</option>';
  let cliBOptions = '';
  (d.batches || []).forEach(b => {
    bOptions += `<option value="${b.batch_id}">${b.batch_label} (${b.videos_count} videos)</option>`;
    cliBOptions += `<option value="${b.batch_id}">${b.batch_id} (${b.batch_label})</option>`;
  });
  bSelect.innerHTML = bOptions;
  if (curBVal) bSelect.value = curBVal;
  if (cliBatchSelect && cliBOptions) cliBatchSelect.innerHTML = cliBOptions;
}

// --- TAB 1: FLEET OVERVIEW RENDER ---
function renderFleetTab() {
  const d = state.raw;
  if (!d) return;

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

// --- TAB 5: MASTER REFERENCES & SEED TOPICS TABLE RENDER ---
function renderReferencesTab() {
  const d = state.raw;
  if (!d) return;

  const tbody = document.getElementById('references-table-body');
  if (!tbody) return;

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
    const topics = ch.seed_topics || [];
    const hooks = ch.hook_formulas || [];

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

    const topicsHtml = topics.length > 0 ? `
      <ol style="margin: 0; padding-left: 18px; font-size: 11.5px; line-height: 1.6; color: var(--text-gray);">
        ${topics.map(t => `<li>${escHtml(t)}</li>`).join('')}
      </ol>
    ` : '<span style="color:var(--text-dim); font-size:11px;">Chưa có đề tài mẫu</span>';

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

  outBox.innerText = cmd;
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
  renderActiveViews();
}

function renderActiveViews() {
  renderFleetTab();
  renderCatalogTable();
  renderFunnelTab();
  renderOpsTab();
  renderReferencesTab();
}

// --- API ACTIONS ---
async function refreshMetrics() {
  const btn = document.getElementById('btn-refresh');
  const oldText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner"></span> Đang cào dữ liệu...`;
  showToast('Đang quét chỉ số live từ YouTube cho toàn bộ kênh...', 'info');

  try {
    const res = await fetch('/api/refresh', { method: 'POST' });
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
    const res = await fetch('/api/sync-map', { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.snapshot) renderDashboard(data.snapshot);
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
    const res = await fetch('/api/open-studio', {
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
  const cmd = 'python3 sys/tools/youtube_dashboard.py --serve --port 8765';
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

  // If served over HTTP/HTTPS, fetch latest live metrics
  if (window.location.protocol.startsWith('http')) {
    fetch('/api/metrics')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => renderDashboard(data))
      .catch(err => console.log('Live fetch note:', err.message));
  }
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
        safe_json = json.dumps(embedded_data, ensure_ascii=False).replace(
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
