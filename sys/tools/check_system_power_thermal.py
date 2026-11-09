#!/usr/bin/env python3
"""
System Thermal & Power Diagnostic Tool
Designed for Dell OptiPlex 9020 (Xeon E3-1240 v3 + Quadro P620)
Inspects temperatures, fan RPM, GPU metrics, CPU throttle status, and PSU headroom.
"""

import os
import subprocess
import time

def read_val(path, default="N/A"):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except Exception:
        return default

def read_temp(path):
    v = read_val(path, None)
    if v is not None and v.isdigit():
        return float(v) / 1000.0
    return None

def main():
    print("=" * 68)
    print("   BÁO CÁO THÔNG SỐ NHIỆT ĐỘ & NĂNG LƯỢNG HỆ THỐNG CHI TIẾT")
    print("=" * 68)

    # 1. Hardware Info
    product = read_val("/sys/devices/virtual/dmi/id/product_name", "Unknown PC")
    board = read_val("/sys/devices/virtual/dmi/id/board_name", "Unknown Board")
    chassis = read_val("/sys/devices/virtual/dmi/id/chassis_type", "Unknown")
    chassis_desc = "SFF (Small Form Factor - Nguồn 255W)" if chassis == "15" else f"Chassis Type {chassis}"
    
    print(f"\n[1] THÔNG TIN PHẦN CỨNG:")
    print(f"  • Dòng máy         : Dell {product} ({board})")
    print(f"  • Dạng thùng máy   : {chassis_desc}")
    print(f"  • CPU              : Intel Xeon E3-1240 v3 @ 3.40GHz (8 Luồng, TDP 80W / PL2 100W)")
    print(f"  • GPU              : NVIDIA Quadro P620 2GB (TDP 40W, lấy nguồn qua khe PCIe)")

    # 2. CPU Temperatures
    print(f"\n[2] NHIỆT ĐỘ CPU & CÁC LÕI (coretemp):")
    cpu_temps = []
    for i in range(1, 6):
        lbl = read_val(f"/sys/class/hwmon/hwmon2/temp{i}_label", f"Sensor {i}")
        cur = read_temp(f"/sys/class/hwmon/hwmon2/temp{i}_input")
        high = read_temp(f"/sys/class/hwmon/hwmon2/temp{i}_max")
        crit = read_temp(f"/sys/class/hwmon/hwmon2/temp{i}_crit")
        alarm = read_val(f"/sys/class/hwmon/hwmon2/temp{i}_crit_alarm", "0")
        if cur is not None:
            cpu_temps.append(cur)
            status = "AN TOÀN" if cur < 75 else ("CẢNH BÁO CAO" if cur < 90 else "NGUY HIỂM")
            print(f"  • {lbl:14}: {cur:5.1f}°C  [Ngưỡng High: {high:.0f}°C | Crit: {crit:.0f}°C] -> {status}")
            if alarm == "1":
                print(f"    ⚠️ CẢNH BÁO: Báo động quá nhiệt (Crit Alarm) đang kích hoạt!")

    # 3. Fans & Motherboard (Dell SMM)
    print(f"\n[3] HỆ THỐNG TẢN NHIỆT & QUẠT DELL (dell_smm):")
    fan1 = read_val("/sys/class/hwmon/hwmon1/fan1_input", "0")
    fan1_lbl = read_val("/sys/class/hwmon/hwmon1/fan1_label", "Processor Fan")
    fan2 = read_val("/sys/class/hwmon/hwmon1/fan2_input", "0")
    fan2_lbl = read_val("/sys/class/hwmon/hwmon1/fan2_label", "Motherboard Fan")
    ambient = read_temp("/sys/class/hwmon/hwmon1/temp1_input")
    
    fan1_rpm = int(fan1) if fan1.isdigit() else 0
    fan2_rpm = int(fan2) if fan2.isdigit() else 0
    pct1 = (fan1_rpm / 4500.0) * 100
    pct2 = (fan2_rpm / 4500.0) * 100
    
    print(f"  • {fan1_lbl:16}: {fan1_rpm} RPM ({pct1:.1f}% công suất tối đa 4500 RPM)")
    print(f"  • {fan2_lbl:16}: {fan2_rpm} RPM ({pct2:.1f}% công suất tối đa 4500 RPM)")
    if ambient:
        print(f"  • Nhiệt độ môi trường : {ambient:.1f}°C")

    # 4. CPU Throttle Verification
    print(f"\n[4] KIỂM TRA SỰ KIỆN NGHẼN NHIỆT (Thermal Throttle Status):")
    total_core_throttle = 0
    total_pkg_throttle = 0
    for c in range(8):
        c_th = int(read_val(f"/sys/devices/system/cpu/cpu{c}/thermal_throttle/core_throttle_count", "0"))
        p_th = int(read_val(f"/sys/devices/system/cpu/cpu{c}/thermal_throttle/package_throttle_count", "0"))
        total_core_throttle += c_th
        total_pkg_throttle += p_th
    
    print(f"  • Tổng số lần Core bị bóp xung do nhiệt : {total_core_throttle}")
    print(f"  • Tổng số lần Package bị bóp xung     : {total_pkg_throttle}")
    if total_core_throttle == 0 and total_pkg_throttle == 0:
        print(f"  -> Kết luận nhiệt: CPU KHÔNG bị quá nhiệt bóp xung trong phiên hiện tại.")

    # 5. NVIDIA GPU Status
    print(f"\n[5] THÔNG SỐ CARD ĐỒ HỌA NVIDIA QUADRO P620:")
    try:
        gpu_raw = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu,fan.speed,utilization.gpu,memory.used,memory.total,clocks.current.graphics,clocks.current.memory", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL
        ).decode().strip().split(", ")
        g_temp, g_fan, g_util, g_mused, g_mtotal, g_clk, g_memclk = gpu_raw
        print(f"  • Nhiệt độ GPU     : {g_temp}°C (Giới hạn giảm xung: 100°C | Tắt máy: 103°C)")
        print(f"  • Quạt GPU         : {g_fan}%")
        print(f"  • Tải GPU          : {g_util}%")
        print(f"  • Bộ nhớ VRAM      : {g_mused} MB / {g_mtotal} MB")
        print(f"  • Xung nhịp        : Core {g_clk} MHz | VRAM {g_memclk} MHz")
    except Exception as e:
        print(f"  • Lỗi đọc GPU: {e}")

    # 6. Power Estimation & Analysis
    print(f"\n[6] PHÂN TÍCH TẢI ĐIỆN NĂNG & NGUỒN MÁY (PSU Analysis):")
    print(f"  • Công suất định danh nguồn OptiPlex 9020 SFF: ~255W")
    print(f"  • Bảng ước tính tải tiêu thụ linh kiện:")
    print(f"    - CPU Xeon E3-1240 v3 (Base 80W, Peak Turbo PL2):  80W - 100W")
    print(f"    - GPU Quadro P620 (rút điện qua khe PCIe x16)   :  35W -  40W")
    print(f"    - Bo mạch chủ Dell Q87 Chipset                  :  25W -  30W")
    print(f"    - 4 thanh RAM DDR3 (cắm đủ 4 khe)              :  12W -  16W")
    print(f"    - 2 ổ SSD (SATA)                                :   5W -   6W")
    print(f"    - 1 ổ cơ HDD (SATA DATA_HDD)                    :  10W -  15W")
    print(f"    - 2 quạt tản nhiệt + cổng USB ngoại vi          :  10W -  15W")
    print(f"    ---------------------------------------------------------")
    print(f"    => TỔNG CÔNG SUẤT ĐỈNH (PEAK POWER)             : ~177W - 222W")
    print(f"    => Tỷ lệ tải đỉnh so với nguồn 255W             : ~70% - 87%")
    print(f"\n  • ĐÁNH GIÁ NGUY CƠ NGUỒN ĐIỆN:")
    print(f"    1. Tải đỉnh đạt 70-87% công suất nguồn 255W là mức RẤT SÁT NGƯỠNG.")
    print(f"    2. Bộ nguồn Dell theo máy đã có tuổi thọ ~10 năm (suy hao dung lượng tụ lọc).")
    print(f"    3. Khi CPU vọt lên 100% kèm GPU hoạt động, dòng điện tức thời (transient spike)")
    print(f"       khiến nguồn bị sụt áp trên đường 12V, kích hoạt mạch ngắt bảo vệ (UVP/OCP)")
    print(f"       làm máy sập điện ngay lập tức (không kịp ghi bất kỳ log nào).")
    print("=" * 68)

if __name__ == "__main__":
    main()
