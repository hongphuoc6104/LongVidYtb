"""Generate separated per-channel PLAN.md files under ``sys/channels/<id>/PLAN.md``."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from channels.registry import ChannelProfile, channels  # noqa: E402

WEEK1_BUNDLES: Dict[str, Dict[str, object]] = {
    "nao_luoi": {
        "youtube_long": {
            "title": "Tại Sao Càng Tự Trách Bản Thân Bạn Lại Càng Trì Hoãn? (Giải Mã Cơ Chế Phòng Vệ Của Não Bộ)",
            "duration": "10 phút (24 cảnh)",
            "hook": "Bạn đã bao giờ nằm lướt điện thoại cả tiếng đồng hồ, trong lòng cực kỳ sốt ruột vì công việc chưa xong, nhưng tay vẫn không thể dừng lại?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Vì sao càng gần deadline bạn lại càng muốn đi dọn phòng?", "35s"),
            ("Spin-off #2 (0 ảnh mới)", "Bạn không hề lười: não bạn đang bật chế độ đóng băng vì sợ hoàn hảo.", "35s"),
            ("Spin-off #3 (0 ảnh mới)", "Quy tắc 120 giây đánh lừa bộ não đang trì hoãn.", "30s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Vì sao bạn thức tới 2 giờ sáng dù mắt đã díp lại? (Trả thù giờ đi ngủ)", "35s"),
        ],
    },
    "tui_tien": {
        "youtube_long": {
            "title": "Giải Mã Đế Chế Trà Sữa & Cà Phê: Vì Sao Ly Nước 50 Nghìn Lãi Đậm Mà Hàng Loạt Quán Vẫn Sập?",
            "duration": "12 phút (26 cảnh)",
            "hook": "Một ly trà sữa bán 50 nghìn đồng, tiền cốt trà và trân châu thật sự chỉ tốn chưa tới 7 nghìn, vậy 43 nghìn còn lại đi đâu?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Ly trà sữa 35 nghìn: chủ quán thực sự đút túi bao nhiêu tiền?", "45s"),
            ("Spin-off #2 (0 ảnh mới)", "Bẫy tâm lý 'Thêm 5 nghìn lên size L': quán lời gấp đôi thế nào?", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Vì sao quán cà phê để khách ngồi điều hòa cả ngày vẫn sống khỏe?", "45s"),
            ("Fast-Short #4 (5 ảnh Flow + bảng tính Remotion)", "Mua trả góp 0% lãi suất: ai đang âm thầm trả lãi thay bạn?", "50s"),
        ],
    },
    "ua_sao_vay": {
        "youtube_long": {
            "title": "8 Hiện Tượng Quen Thuộc Mỗi Ngày Nhưng 99% Chúng Ta Đều Hiểu Sai Bản Chất Khoa Học",
            "duration": "10 phút (8 chương câu hỏi độc lập)",
            "hook": "Ai cũng nghĩ nước suối đóng chai có hạn sử dụng vì nước bị thiu, nhưng sự thật khoa học lại nằm ở một thứ hoàn toàn khác.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (Cắt thẳng Chương 1)", "Ủa, sao trong phòng có chục người mà muỗi chỉ đốt đúng một người?", "25s"),
            ("Spin-off #2 (Cắt thẳng Chương 2)", "Ủa, sao mình không bao giờ tự cù lét cho mình cười được?", "25s"),
            ("Spin-off #3 (Cắt thẳng Chương 3)", "Ủa, nước ngầm triệu năm không hỏng sao đóng chai lại có hạn sử dụng?", "30s"),
            ("Spin-off #4 (Cắt thẳng Chương 4)", "Ủa, sao ngủ nướng cuối tuần dậy lại đau đầu hơn ngày thường?", "28s"),
            ("Spin-off #5 (Cắt thẳng Chương 5)", "Ủa, sao nghe lại giọng ghi âm của chính mình ai cũng thấy kỳ cục?", "25s"),
        ],
    },
    "su_ke_lai": {
        "youtube_long": {
            "title": "Trận Bạch Đằng Năm 938: Ngô Quyền Đã Tính Toán Thủy Triều & Bẫy Cọc Gỗ Chính Xác Đến Từng Phút Ra Sao?",
            "duration": "15 phút (28 cảnh bản đồ + Đông Hồ)",
            "hook": "Mùa đông năm 938, đoàn chiến thuyền khổng lồ của quân Nam Hán tiến vào cửa sông Bạch Đằng mà không hề biết dưới mặt nước phẳng lặng kia là một tử địa.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Vì sao tướng Nam Hán biết sông Bạch Đằng hiểm trở mà vẫn sa vào bẫy?", "60s"),
            ("Spin-off #2 (0 ảnh mới)", "Bí mật kỹ thuật đóng cọc gỗ đầu bịt sắt giữa dòng nước chảy xiết.", "60s"),
            ("Spin-off #3 (0 ảnh mới)", "Khoảnh khắc con nước rút quyết định 1.000 năm độc lập của dân tộc.", "60s"),
            ("Fast-Short #4 (8 ảnh Flow)", "Vì sao vua Quang Trung hành quân ra Thăng Long nhanh gấp đôi dự tính?", "65s"),
        ],
    },
    "thuong_cho_kheo": {
        "youtube_long": {
            "title": "Vì Sao Hai Người Thương Nhau Thật Lòng Nhưng Cứ Mở Lời Là Làm Nhau Tổn Thương? (5 Bẫy Giao Tiếp Kinh Điển)",
            "duration": "11 phút (24 cảnh đối thoại Tũn & Mây)",
            "hook": "Có bao giờ bạn nói ra một câu chỉ vì lo cho người ấy, nhưng vừa dứt lời thì không khí lập tức đóng băng?",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Khi người yêu nói 'Em không sao', tuyệt đối đừng trả lời theo bản năng.", "40s"),
            ("Spin-off #2 (0 ảnh mới)", "Khác biệt giữa người biết lắng nghe và người chỉ chờ đến lượt mình cãi.", "45s"),
            ("Spin-off #3 (0 ảnh mới)", "3 câu nói ngắn giúp hạ nhiệt mọi cuộc tranh cãi trong 10 giây.", "40s"),
            ("Fast-Short #4 (6 ảnh Flow based_on)", "Cách từ chối lời nhờ vả vô lý mà không làm mất lòng đối phương.", "45s"),
        ],
    },
    "ho_so_ky_la": {
        "youtube_long": {
            "title": "Hồ Sơ Con Tàu Mary Celeste: Vì Sao Toàn Bộ Thủy Thủ Đoàn Biến Mất Khi Bữa Ăn Vẫn Còn Nguyên Trên Bàn?",
            "duration": "15 phút (28 cảnh Noir hồ sơ)",
            "hook": "Ngày 4 tháng 12 năm 1872, người ta tìm thấy con tàu Mary Celeste trôi dạt giữa Đại Tây Dương: hàng hóa nguyên vẹn, quần áo vẫn xếp gọn, nhưng không còn một bóng người.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Manh mối #1: Chi tiết kỳ lạ nhất trên boong tàu Mary Celeste.", "60s"),
            ("Spin-off #2 (0 ảnh mới)", "Manh mối #2: Vì sao giả thuyết cướp biển tấn công bị bác bỏ ngay lập tức?", "55s"),
            ("Spin-off #3 (0 ảnh mới)", "Manh mối #3: Giả thuyết khoa học hợp lý nhất giải thích lệnh bỏ tàu khẩn cấp.", "60s"),
            ("Fast-Short #4 (8 ảnh Flow)", "Tín hiệu 'Wow!' năm 1977: 72 giây sóng vô tuyến bí ẩn từ vũ trụ.", "60s"),
        ],
    },
    "co_the_ke": {
        "youtube_long": {
            "title": "Hành Trình 24 Giờ Bên Trong Cơ Thể Khi Bạn Thức Trắng Đêm: Tim, Gan Và Não Bộ Phải Gồng Gánh Ra Sao?",
            "duration": "10 phút (24 cảnh Kawaii y học)",
            "hook": "Nếu tối nay bạn quyết định thức trắng để cày phim hoặc chạy deadline, đây là cuộc họp khẩn cấp diễn ra ngay bên trong não và tim bạn lúc 2 giờ sáng.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Dạ dày than phiền gì khi bạn ăn mì gói lúc 11 giờ đêm?", "35s"),
            ("Spin-off #2 (0 ảnh mới)", "Điều gì xảy ra trong não khi bạn bấm 'Ngủ nướng thêm 10 phút' liên tục?", "35s"),
            ("Spin-off #3 (0 ảnh mới)", "Một ca làm việc quá tải của lá gan sau ly nước ngọt khổng lồ.", "40s"),
            ("Fast-Short #4 (6 ảnh Flow)", "Vì sao cúi đầu nhìn điện thoại làm đốt sống cổ gánh sức nặng 27 kg?", "35s"),
        ],
    },
    "ai_binh_dan": {
        "youtube_long": {
            "title": "Trọn Bộ 5 Quy Trình Dùng AI Miễn Phí Giúp Dân Văn Phòng Tiết Kiệm 2 Giờ Mỗi Ngày (Kèm Câu Lệnh Mẫu)",
            "duration": "12 phút (kết hợp Doodle + khung câu lệnh Remotion + quay màn hình)",
            "hook": "Đừng mất 2 tiếng ngồi đọc từng trang báo cáo dài nữa: chỉ với một câu lệnh miễn phí này, bạn sẽ có bảng tóm tắt chuẩn xác trong 30 giây.",
        },
        "tiktok_shorts": [
            ("Spin-off #1 (0 ảnh mới)", "Tóm tắt file PDF 50 trang thành bảng việc cần làm trong 30 giây.", "40s"),
            ("Spin-off #2 (0 ảnh mới)", "Một câu lệnh biến ghi chú họp lộn xộn thành biên bản gửi sếp ngay.", "40s"),
            ("Spin-off #3 (0 ảnh mới)", "Cách nhờ AI viết email xin nghỉ phép hoặc từ chối khéo cực lịch sự.", "35s"),
            ("Fast-Short #4 (4 ảnh Flow + khung lệnh Remotion)", "Mẹo dùng AI rà soát lỗi hợp đồng trước khi đặt bút ký.", "40s"),
        ],
    },
}


def render_channel_plan(ch: ChannelProfile) -> str:
    so = ch.speed_optimization
    bundle = WEEK1_BUNDLES[ch.id]
    yt = bundle["youtube_long"]
    shorts: List[tuple] = bundle["tiktok_shorts"]  # type: ignore[assignment]

    refs_short = [r for r in ch.references if r.format == "short"]
    refs_long = [r for r in ch.references if r.format == "long"]

    lines = [
        f"# KẾ HOẠCH CHI TIẾT KÊNH: {ch.name.upper()} (`{ch.id}`)",
        "",
        "## 1. Định Vị Kênh & Phân Tách Nền Tảng",
        f"- **Mã kênh:** `{ch.id}` (Đợt triển khai: Wave {ch.wave})",
        f"- **Nhánh GitHub độc lập:** `{ch.git_branch}` (`origin/{ch.git_branch}`)",
        f"- **Thư mục phát triển trên máy:** `/home/hongphuoc6104/Desktop/vp-channels/{ch.workspace_dirname}`",
        f"- **Ngách nội dung:** {ch.niche}",
        f"- **Lời hứa thương hiệu (Value Proposition):** {ch.promise}",
        f"- **Khán giả mục tiêu:** {ch.audience}",
        f"- **Nhân vật dẫn chuyện (Persona):** {ch.persona}",
        f"- **Giọng văn (Tone):** {ch.tone} | **Giọng TTS:** `{ch.voice}` ({ch.speed}x)",
        "- **Phân tách nền tảng bắt buộc:**",
        f"  - **TikTok (`{ch.platform_routing['tiktok']}` — 9:16):** Video ngắn {ch.short_spec.duration_seconds[0]}–{ch.short_spec.duration_seconds[1]}s, nhịp chuyển cảnh {ch.short_spec.beat_interval_seconds[0]:g}–{ch.short_spec.beat_interval_seconds[1]:g}s. Mục tiêu: Lên xu hướng FYP, kéo follow và gắn Affiliate / dẫn phễu.",
        f"  - **YouTube (`{ch.platform_routing['youtube']}` — 16:9):** Video dài {ch.long_spec.duration_seconds[0] // 60}–{ch.long_spec.duration_seconds[1] // 60} phút, nhịp pattern-interrupt {ch.long_spec.beat_interval_seconds[0]:g}–{ch.long_spec.beat_interval_seconds[1]:g}s. Mục tiêu: Bật kiếm tiền AdSense RPM cao & xây dựng uy tín lâu dài.",
        "",
        "## 2. Kênh Mẫu Tham Chiếu (Bám Theo Cấu Trúc Đã Kiểm Chứng)",
        "### Kênh mẫu TikTok Short (`short_9x16`)",
        *[f"- **{r.name}** ({r.platform}): {r.learn}" for r in refs_short],
        "### Kênh mẫu YouTube Long (`long_16x9`)",
        *[f"- **{r.name}** ({r.platform}): {r.learn}" for r in refs_long],
        "",
        "## 3. Luật Viết Kịch Bản & Công Thức Hook",
        "### Nguyên tắc giọng kể",
        *[f"- {rule}" for rule in ch.tone_rules],
        "### Công thức Hook 3 giây đầu (viết 3 bản A/B/C, chấm điểm bằng `script_hook_scorer.py`)",
        *[f"- `{h}`" for h in ch.hook_formulas],
        "### Cấu trúc giữ chân TikTok Short (`short_9x16`)",
        *[f"1. {s}" for s in ch.short_spec.structure],
        f"- **Câu kết (CTA):** {ch.short_spec.closing}",
        "### Cấu trúc giữ chân YouTube Long (`long_16x9`)",
        *[f"1. {s}" for s in ch.long_spec.structure],
        f"- **Câu kết (CTA):** {ch.long_spec.closing}",
        "### Điều cấm kỵ (Avoid)",
        *[f"- {a}" for a in ch.avoid],
        "",
        "## 4. Phong Cách Hình Ảnh & Thumbnail Flow Native",
        f"- **Visual Profile ID:** `{ch.visual.profile_id}` — {ch.visual.label}",
        f"- **Bảng màu khóa cứng:** {', '.join(f'`{c}`' for c in ch.visual.palette)}",
        f"- **Tạo hình nhân vật (`CAST_APPEARANCE`):** {ch.visual.cast_appearance}",
        f"- **Trang phục (`DEFAULT_OUTFIT`):** {ch.visual.outfit}",
        f"- **Luật Thumbnail (100% Flow Native, `overlay_card: false`):** {ch.visual.thumbnail_rule}",
        f"- **Prompt Style gốc:**\n  > {ch.visual.style_description}",
        "",
        "## 5. Tối Ưu Thời Gian Sản Xuất (Kết Hợp Flow CDP + Remotion / Hyperframes)",
    ]
    if so is not None:
        lines.extend(
            [
                f"- **Chế độ Render chủ đạo:** `{so.render_mode}` (Tỷ lệ đồ họa động Remotion/Hyperframes: **{int(so.remotion_motion_ratio * 100)}%**)",
                f"- **Số ảnh Flow tối đa cho 1 TikTok Fast-Short:** **{so.fast_short_max_images} ảnh** (nhịp 2–4s/chuyển cảnh được tạo bằng Remotion camera beats, zoom/pan, kinetic badges).",
                f"- **Số TikTok Spin-off trích xuất từ 1 YouTube Long:** **{so.spinoff_shorts_per_long} video ngắn** (qua `sys/omni_platform.py`, **0 phút sinh thêm ảnh Flow**).",
                f"- **Thời gian mục tiêu:** **{so.estimated_short_minutes[0]}–{so.estimated_short_minutes[1]} phút** cho 1 TikTok Short độc lập; **{so.estimated_bundle_minutes[0]}–{so.estimated_bundle_minutes[1]} phút** cho trọn bộ (1 YouTube Long + {so.spinoff_shorts_per_long} TikTok Shorts).",
                f"- **Chiến thuật tốc độ riêng của kênh:** {so.notes}",
            ]
        )
    lines.extend(
        [
            "",
            "## 6. Lộ Trình Sản Xuất Tuần 1 (1 YouTube Long + Chuỗi TikTok Shorts)",
            f"### YouTube Long #1 (`long_16x9`)",
            f"- **Tiêu đề:** *{yt['title']}*",
            f"- **Thời lượng:** {yt['duration']}",
            f"- **Câu mở đầu (Cold Open):** \"{yt['hook']}\"",
            "### Danh sách TikTok Shorts Tuần 1 (`short_9x16`)",
            *[f"- **{kind}:** *{title}* ({dur})" for kind, title, dur in shorts],
            "",
            "### Backlog chủ đề hạt giống tiếp theo",
            *[f"- {t}" for t in ch.seed_topics],
            "",
            "## 7. Kiếm Tiền, Hashtag & Ngưỡng Quyết Định (14 Ngày)",
            f"- **Bộ Hashtag chuẩn TikTok:** `{' '.join(ch.hashtags)}`",
            f"- **Nguồn doanh thu:** {', '.join(ch.monetization)}",
            "- **Lệnh làm việc nhanh trên máy:**",
            "  ```bash",
            f"  cd /home/hongphuoc6104/Desktop/vp-channels/{ch.workspace_dirname}",
            f"  python3 sys/tools/script_hook_scorer.py --content sys/runs/<job>/content.json --channel {ch.id}",
            "  python3 sys/analytics/channel_metrics.py sys/channels/metrics.csv",
            "  ```",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_all_plans(base_dir: Path | None = None) -> List[Path]:
    root = base_dir or Path(__file__).resolve().parents[1] / "channels"
    written: List[Path] = []
    for cid, ch in channels().items():
        cdir = root / cid
        cdir.mkdir(parents=True, exist_ok=True)
        plan_path = cdir / "PLAN.md"
        plan_path.write_text(render_channel_plan(ch), encoding="utf-8")
        written.append(plan_path)
    return written


if __name__ == "__main__":
    paths = generate_all_plans()
    for p in paths:
        print(f"[+] Wrote {p}")
