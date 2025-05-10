import tkinter as tk
from tkinter import messagebox
import time
import random
import sys
import os
import threading
import pygame

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ReminderApp:
    def open_break_settings(self):
        break_win = tk.Toplevel()
        break_win.title("休息设置")
        
        tk.Label(break_win, text="休息时长(秒):").grid(row=0, column=0)
        self.break_entry = tk.Entry(break_win)
        self.break_entry.insert(0, str(self.break_duration // 1000))
        self.break_entry.grid(row=0, column=1)
        
        tk.Button(break_win, text="保存", command=lambda: self.save_break_settings(
            self.break_entry.get(),
            break_win
        )).grid(row=1, columnspan=2)
    
    def save_break_settings(self, duration, win):
        try:
            self.break_duration = int(duration) * 1000
            win.destroy()
            messagebox.showinfo("成功", "休息时长已更新")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的整数")

    def update_time_display(self):
        if self.is_running:
            elapsed = (time.time() - self.start_time) // 60
            self.time_label.config(text=f"已运行: {int(elapsed)} 分钟")
            self.root.after(1000, self.update_time_display)

    def play_sound(self, sound_path):
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(sound_path)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            pygame.mixer.quit()
        except Exception as e:
            error_msg = f"无法播放提示音: {str(e)}\n文件路径: {sound_path}"
            print(error_msg)
            self.root.after(0, lambda: messagebox.showerror("错误", error_msg))
    
    def show_reminder_sequence(self):
        threading.Thread(target=lambda: self.play_sound(self.current_break_sound), daemon=True).start()
        
        self.root.iconify()
        self.root.deiconify()
        response = messagebox.askokcancel("休息提醒", "该站起来休息一下了！", parent=self.root)
        if response:
            self.root.after(self.break_duration, self.on_break_end)
        else:
            self.root.after(5000, self.show_reminder_sequence)

    def on_break_end(self):
        threading.Thread(target=lambda: self.play_sound(self.current_end_sound), daemon=True).start()
        messagebox.showinfo("休息结束", "可以继续工作了!")
        self.schedule_next_reminder()

    def __init__(self):
        self.break_duration = 10000  # 默认10秒
        self.root = tk.Tk()
        self.root.title("智能休息提醒器")
        self.is_running = False
        self.start_time = 0
        
        self.min_interval = 180
        self.max_interval = 300
        self.total_duration = 90
        
        # 初始化声音设置
        self.sound_options = {
            "提示音1": resource_path(os.path.join("sounds", "cat_2.mp3")),
            "提示音2": resource_path(os.path.join("sounds", "dog_2.mp3")),
            "提示音3": resource_path(os.path.join("sounds", "piano_1.mp3")),
            "提示音4": resource_path(os.path.join("sounds", "guitar_1.mp3")),
            "提示音5": resource_path(os.path.join("sounds", "poka_1.mp3"))
        }
        self.current_break_sound = self.sound_options["提示音5"]
        self.current_end_sound = self.sound_options["提示音3"]
        
        self.setup_ui()
        self.setup_menu()

    def setup_ui(self):
        self.frame = tk.Frame(self.root, padx=20, pady=20)
        self.frame.pack()
        
        self.status_label = tk.Label(self.frame, text="状态: 未运行", font=('微软雅黑', 12))
        self.status_label.pack(pady=10)
        
        self.start_btn = tk.Button(self.frame, text="开始", command=self.toggle_reminder,
                                 bg='#4CAF50', fg='white', font=('微软雅黑', 10))
        self.start_btn.pack(pady=5)
        
        self.time_label = tk.Label(self.frame, text="已运行: 0 分钟", font=('微软雅黑', 10))
        self.time_label.pack(pady=5)

    def toggle_reminder(self):
        if not self.is_running:
            self.start_reminder()
        else:
            self.stop_reminder()

    def start_reminder(self):
        self.is_running = True
        self.start_time = time.time()
        self.update_time_display()
        self.status_label.config(text="状态: 运行中")
        self.start_btn.config(text="停止", bg='#f44336')
        self.schedule_next_reminder()

    def stop_reminder(self):
        self.is_running = False
        self.status_label.config(text="状态: 已停止") 
        self.start_btn.config(text="开始", bg='#4CAF50')

    def setup_menu(self):
        menubar = tk.Menu(self.root)
        
        # 设置菜单
        config_menu = tk.Menu(menubar, tearoff=0)
        config_menu.add_command(label="参数设置", command=self.open_settings)
        menubar.add_cascade(label="设置", menu=config_menu)
        
        # 休息菜单
        break_menu = tk.Menu(menubar, tearoff=0)
        break_menu.add_command(label="休息设置", command=self.open_break_settings)
        menubar.add_cascade(label="休息", menu=break_menu)
        
        # 声音菜单
        sound_menu = tk.Menu(menubar, tearoff=0)
        
        # 休息提示音子菜单
        break_sound_menu = tk.Menu(sound_menu, tearoff=0)
        self.break_sound_var = tk.StringVar(value=self.current_break_sound)
        for name, path in self.sound_options.items():
            break_sound_menu.add_radiobutton(
                label=name,
                variable=self.break_sound_var,
                value=path,
                command=lambda p=path: self.set_break_sound(p)
            )
        
        # 结束提示音子菜单
        end_sound_menu = tk.Menu(sound_menu, tearoff=0)
        self.end_sound_var = tk.StringVar(value=self.current_end_sound)
        for name, path in self.sound_options.items():
            end_sound_menu.add_radiobutton(
                label=name,
                variable=self.end_sound_var,
                value=path,
                command=lambda p=path: self.set_end_sound(p)
            )
        
        sound_menu.add_cascade(label="休息提示音", menu=break_sound_menu)
        sound_menu.add_cascade(label="结束提示音", menu=end_sound_menu)
        
        menubar.add_cascade(label="声音", menu=sound_menu)
        
        self.root.config(menu=menubar)

    def set_break_sound(self, sound_path):
        if os.path.exists(sound_path):
            self.current_break_sound = sound_path
        else:
            messagebox.showerror("错误", f"声音文件不存在: {sound_path}")

    def set_end_sound(self, sound_path):
        if os.path.exists(sound_path):
            self.current_end_sound = sound_path
        else:
            messagebox.showerror("错误", f"声音文件不存在: {sound_path}")

    def open_settings(self):
        settings_win = tk.Toplevel()
        settings_win.title("参数设置")
        
        tk.Label(settings_win, text="最小间隔(秒):").grid(row=0, column=0)
        min_entry = tk.Entry(settings_win)
        min_entry.insert(0, str(self.min_interval))
        min_entry.grid(row=0, column=1)
        
        tk.Label(settings_win, text="最大间隔(秒):").grid(row=1, column=0)
        max_entry = tk.Entry(settings_win)
        max_entry.insert(0, str(self.max_interval))
        max_entry.grid(row=1, column=1)
        
        tk.Label(settings_win, text="总时长(分钟):").grid(row=2, column=0)
        duration_entry = tk.Entry(settings_win)
        duration_entry.insert(0, str(self.total_duration))
        duration_entry.grid(row=2, column=1)
        
        tk.Button(settings_win, text="保存", command=lambda: self.save_settings(
            min_entry.get(),
            max_entry.get(),
            duration_entry.get(),
            settings_win
        )).grid(row=3, columnspan=2)

    def save_settings(self, min_val, max_val, duration, win):
        try:
            if not (0 < int(min_val) <= int(max_val)):
                raise ValueError("时间范围无效")
            if int(duration) <= 0:
                raise ValueError("总时长必须大于0")
                
            self.min_interval = int(min_val)
            self.max_interval = int(max_val)
            self.total_duration = int(duration)
            win.destroy()
            messagebox.showinfo("成功", "参数已更新")
        except ValueError as e:
            messagebox.showerror("输入错误", f"无效参数: {str(e)}")

    def schedule_next_reminder(self):
        if not self.is_running:
            return
        elapsed = (time.time() - self.start_time) / 60
        if elapsed >= self.total_duration:
            self.stop_reminder()
            self.root.after(0, lambda: messagebox.showinfo("完成", f"{self.total_duration}分钟计时已完成！"))
            return
        interval = random.randint(self.min_interval, self.max_interval)
        self.root.after(interval * 1000, self.show_reminder_sequence)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.is_running = False
            self.root.quit()

if __name__ == "__main__":
    app = ReminderApp()
    app.run()