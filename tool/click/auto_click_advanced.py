import pyautogui
import customtkinter as ctk
import threading
import json
import os

class AutoClickerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Auto Clicker")
        self.master.geometry("400x400")
        ctk.set_appearance_mode("dark")
        self.master.wm_attributes("-topmost", 1)  # Đảm bảo ứng dụng luôn trên cùng

        self.running = False
        self.interval = 1000  # Thời gian giữa các lần click mặc định (ms)
        self.click_count = 10  # Số lần click mặc định
        self.current_clicks = 0

        # Nhãn hướng dẫn
        self.label = ctk.CTkLabel(master, text="Nhấn Start để bắt đầu Auto Click", font=("Arial", 14))
        self.label.pack(pady=10)

        # Nút chọn vị trí click
        self.position_button = ctk.CTkButton(master, text="Chọn Vị Trí Click (F1)", command=self.choose_position)
        self.position_button.pack(pady=5)

        # Nhãn hướng dẫn vị trí
        self.position_instruction = ctk.CTkLabel(master, text="", font=("Arial", 10))
        self.position_instruction.pack(pady=5)

        # Nút Start và Stop
        self.start_button = ctk.CTkButton(master, text="Start (F6)", command=self.start)
        self.start_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(master, text="Stop (F7)", command=self.stop)
        self.stop_button.pack(pady=5)

        # Nhập thời gian giữa các lần click
        self.interval_label = ctk.CTkLabel(master, text="Thời gian giữa các lần click (ms):")
        self.interval_label.pack(pady=5)

        self.interval_entry = ctk.CTkEntry(master)
        self.interval_entry.pack(pady=5)
        self.interval_entry.insert(0, "1000")

        # Nhập số lần click
        self.count_label = ctk.CTkLabel(master, text="Số lần click:")
        self.count_label.pack(pady=5)

        self.count_entry = ctk.CTkEntry(master)
        self.count_entry.pack(pady=5)
        self.count_entry.insert(0, "10")

        # Nhãn vị trí
        self.position_label = ctk.CTkLabel(master, text="Vị trí click hiện tại: (0, 0)")
        self.position_label.pack(pady=5)

        # Nhãn đếm ngược
        self.timer_label = ctk.CTkLabel(master, text="Thời gian còn lại cho lần click tiếp theo: 0 ms")
        self.timer_label.pack(pady=5)

        # Nút lưu và tải cài đặt
        self.save_button = ctk.CTkButton(master, text="Lưu Cài Đặt (F8)", command=self.save_settings)
        self.save_button.pack(pady=5)

        self.load_button = ctk.CTkButton(master, text="Tải Cài Đặt (F9)", command=self.load_settings)
        self.load_button.pack(pady=5)

        # Gán phím tắt
        self.master.bind('<F6>', lambda event: self.start())
        self.master.bind('<F7>', lambda event: self.stop())
        self.master.bind('<F1>', lambda event: self.choose_position())
        
    def choose_position(self):
        self.label.configure(text="Nhấn chuột trái để chọn vị trí.")
        self.position_instruction.configure(text="Nhấn Enter để xác nhận vị trí.")
        self.master.bind('<Button-1>', self.get_position)
        self.master.bind('<Return>', self.confirm_position)

    def get_position(self, event):
        x, y = event.x_root, event.y_root
        self.position_label.configure(text=f"Vị trí click hiện tại: ({x}, {y})")

    def confirm_position(self, event):
        self.label.configure(text="Vị trí đã được xác nhận!")
        self.master.unbind('<Button-1>')  # Bỏ gán chuột trái
        self.master.unbind('<Return>')    # Bỏ gán phím Enter
        self.position_instruction.configure(text="")

    def start(self):
        try:
            self.interval = int(self.interval_entry.get())
            self.click_count = int(self.count_entry.get())
            if self.interval <= 0 or self.click_count <= 0:
                raise ValueError("Thời gian và số lần click phải lớn hơn 0")
        except ValueError:
            self.label.configure(text="Vui lòng nhập số hợp lệ!")
            return
        
        self.running = True
        self.current_clicks = 0
        self.label.configure(text="Auto Click đang chạy...")
        threading.Thread(target=self.auto_click, daemon=True).start()

    def stop(self):
        self.running = False
        self.label.configure(text="Nhấn Start để bắt đầu Auto Click")

    def auto_click(self):
        while self.running and self.current_clicks < self.click_count:
            x, y = pyautogui.position()
            pyautogui.click(x, y)
            self.current_clicks += 1

            # Cập nhật vị trí click
            self.position_label.configure(text=f"Vị trí click hiện tại: ({x}, {y})")

            # Đếm ngược thời gian cho lần click tiếp theo
            for remaining in range(self.interval // 1000, 0, -1):
                self.timer_label.configure(text=f"Thời gian còn lại cho lần click tiếp theo: {remaining} giây")
                self.master.after(1000)  # Đợi 1 giây
            
            self.timer_label.configure(text="Thời gian còn lại cho lần click tiếp theo: 0 ms")
            self.master.after(self.interval % 1000)  # Đợi phần còn lại nếu có

        self.stop()  # Tự động dừng khi đủ số lần click

    def save_settings(self):
        settings = {
            'interval': self.interval,
            'click_count': self.click_count,
            'position': pyautogui.position()
        }
        with open('settings.json', 'w') as f:
            json.dump(settings, f)
            self.label.configure(text="Cài đặt đã được lưu!")

    def load_settings(self):
        if os.path.exists('settings.json'):
            with open('settings.json', 'r') as f:
                settings = json.load(f)
                self.interval_entry.delete(0, ctk.END)
                self.interval_entry.insert(0, str(settings['interval']))
                self.count_entry.delete(0, ctk.END)
                self.count_entry.insert(0, str(settings['click_count']))
                self.position_label.configure(text=f"Vị trí click hiện tại: {settings['position']}")
                self.label.configure(text="Cài đặt đã được tải!")
        else:
            self.label.configure(text="Không tìm thấy cài đặt để tải!")

def main():
    root = ctk.CTk()
    app = AutoClickerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
