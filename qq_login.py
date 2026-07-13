# -*- coding: utf-8 -*-
"""QQ登录整合单文件版本，无需拆分模块，直接运行"""
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import bcrypt
import random
from datetime import datetime, date
import json
import os
from calendar import monthrange
from shutil import copy2
import sys
from checkin_db import get_checkin_status, do_checkin, get_month_records
from chat_db import send_message, load_conversation
from friends_db import (
    get_friend_list, get_pending_requests, send_friend_request,
    accept_friend_request, reject_friend_request, remove_friend, search_users
)

# ====================== 全局配置 ======================
HEADER_COLOR = "#12B7F5"
BG_COLOR = "#F5F6FA"
BTN_COLOR = "#12B7F5"
BTN_ACTIVE = "#0E9BD6"
CARD_BG = "#FFFFFF"
LOGOUT_BG = "#FF4D4F"
LOGOUT_ACTIVE = "#D9363E"

LOGIN_W = 380
LOGIN_H = 540
REGISTER_W = 360
REGISTER_H = 480
MAIN_W = 420
MAIN_H = 620

FONT_TITLE = ("Microsoft YaHei", 18, "bold")
FONT_SUBTITLE = ("Microsoft YaHei", 10)
FONT_NORMAL = ("Microsoft YaHei", 11)
FONT_SMALL = ("Microsoft YaHei", 9)
FONT_BTN = ("Microsoft YaHei", 12, "bold")
FONT_LOGOUT = ("Microsoft YaHei", 11, "bold")
FONT_EMOJI = ("Segoe UI Emoji", 40)

INPUT_HIGHLIGHT = HEADER_COLOR
INPUT_BORDER = "#DDDDDD"
TEXT_GRAY = "#666666"
TEXT_LIGHT_GRAY = "#999999"
TEXT_BLACK = "#333333"
ONLINE_GREEN = "#52C41A"
DIVIDER_GRAY = "#EEEEEE"

# ====================== 用户加密工具 & 数据库 ======================
USER_DB_FILE = "user_db.json"

DEFAULT_USERS = {
    "123456": {
        "hash_pwd": b'$2b$12$cV8xR9w0F1N8aG7tXyKzOuJdZ7bQ5sL9mN0pR6dT',
        "nickname": "小明",
        "signature": "每一天，乐在沟通",
        "gender": "男",
        "age": "22",
        "city": "深圳",
        "mood": "😊开心",
    },
    "admin": {
        "hash_pwd": b'$2b$12$dE9sK2pQ7zR5aT8xYbN0cJdF3gH6lM4vW1eS9',
        "nickname": "管理员",
        "signature": "好好学习，天天向上",
        "gender": "男",
        "age": "25",
        "city": "北京",
        "mood": "😊开心",
    },
    "qquser": {
        "hash_pwd": b'$2b$12$fR3gT7vB9nD2zP5sC8kX0jL6hM1wQ4aE7dS2',
        "nickname": "QQ用户",
        "signature": "这个人很懒，什么都没留下",
        "gender": "女",
        "age": "20",
        "city": "上海",
        "mood": "😊开心",
    },
}

USER_DB_FILE = "user_db.json"
MOMENTS_FILE = "moments.json"
MOMENTS_PHOTO_DIR = "moments_photos"
MOMENTS_VIDEO_DIR = "moments_videos"
CHAT_FILE = "chat_record.json"

os.makedirs(MOMENTS_PHOTO_DIR, exist_ok=True)
os.makedirs(MOMENTS_VIDEO_DIR, exist_ok=True)

def load_user_db():
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            db = {}
            for account, info in raw.items():
                info["hash_pwd"] = info["hash_pwd"].encode("utf-8")
                db[account] = info
            return db
        except Exception:
            try:
                os.remove(USER_DB_FILE)
            except Exception:
                pass
    return {account: dict(info) for account, info in DEFAULT_USERS.items()}

def save_user_db(db):
    to_save = {}
    for account, info in db.items():
        saved = dict(info)
        saved["hash_pwd"] = saved["hash_pwd"].decode("utf-8")
        if "level_stars" not in saved:
            saved["level_stars"] = 0
        to_save[account] = saved
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)

def save_level_stars(account: str, stars: int):
    if account in USER_DB:
        USER_DB[account]["level_stars"] = stars
        save_user_db(USER_DB)

USER_DB = load_user_db()

def hash_password(raw_pwd: str) -> bytes:
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(raw_pwd.encode("utf-8"), salt)

def verify_password(raw_pwd: str, stored_hash: bytes) -> bool:
    try:
        return bcrypt.checkpw(raw_pwd.encode("utf-8"), stored_hash)
    except Exception:
        return False

def create_new_user(account: str, nickname: str, raw_pwd: str):
    new_hash = hash_password(raw_pwd)
    USER_DB[account] = {
        "hash_pwd": new_hash,
        "nickname": nickname,
        "signature": "这个人很懒，什么都没留下",
        "gender": "保密",
        "age": "未知",
        "city": "未知",
        "level_stars": 0,
        "mood": "😊开心",
    }
    save_user_db(USER_DB)

def get_user_info(account: str):
    return USER_DB.get(account, None)

def account_exists(account: str) -> bool:
    return account in USER_DB

# ====================== 动态（朋友圈）数据层 ======================

def load_moments_data():
    if os.path.exists(MOMENTS_FILE):
        with open(MOMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_moments_data(moments_list: list):
    with open(MOMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(moments_list, f, ensure_ascii=False, indent=2)

def _save_video_file(src_video_path: str) -> str:
    if not src_video_path or not os.path.isfile(src_video_path):
        return ""
    os.makedirs(MOMENTS_VIDEO_DIR, exist_ok=True)
    ext = os.path.splitext(src_video_path)[1] or ".mp4"
    dest_name = f"{int(datetime.now().timestamp() * 1000)}{ext}"
    dest_path = os.path.join(MOMENTS_VIDEO_DIR, dest_name)
    copy2(src_video_path, dest_path)
    return dest_path

def delete_video_file(video_path: str):
    if video_path and os.path.isfile(video_path):
        try:
            os.remove(video_path)
        except OSError:
            pass

def add_moment(account: str, nickname: str, avatar: str, content: str,
               photo_path: str = "", video_path: str = "") -> dict:
    moments = load_moments_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_moment = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "account": account,
        "nickname": nickname,
        "avatar": avatar,
        "time": now,
        "likes": 0,
        "liked_accounts": [],
    }
    new_moment["content"] = content.strip()
    if photo_path:
        ext = os.path.splitext(photo_path)[1] or ".jpg"
        photo_id = new_moment["id"] + ext
        dest = os.path.join(MOMENTS_PHOTO_DIR, photo_id)
        try:
            copy2(photo_path, dest)
            new_moment["photo"] = photo_id
        except Exception:
            new_moment["photo"] = ""
    else:
        new_moment["photo"] = ""

    saved_video = _save_video_file(video_path) if video_path else ""
    new_moment["video"] = saved_video

    moments.insert(0, new_moment)
    save_moments_data(moments)
    return new_moment

def delete_moment(moment_id: str, account: str) -> bool:
    moments = load_moments_data()
    for i, m in enumerate(moments):
        if m["id"] == moment_id and m["account"] == account:
            photo = m.get("photo", "")
            if photo:
                photo_full = os.path.join(MOMENTS_PHOTO_DIR, photo)
                try:
                    if os.path.exists(photo_full):
                        os.remove(photo_full)
                except Exception:
                    pass
            delete_video_file(m.get("video", ""))
            moments.pop(i)
            save_moments_data(moments)
            return True
    return False

def toggle_like_moment(moment_id: str, account: str) -> dict:
    moments = load_moments_data()
    for m in moments:
        if m["id"] == moment_id:
            if "liked_accounts" not in m:
                m["liked_accounts"] = []
            if account in m["liked_accounts"]:
                m["liked_accounts"].remove(account)
                m["likes"] = len(m["liked_accounts"])
            else:
                m["liked_accounts"].append(account)
                m["likes"] = len(m["liked_accounts"])
            save_moments_data(moments)
            return m
    return None

# ====================== 注册窗口类 ======================
class RegisterWindow:
    def __init__(self, parent_root):
        try:
            self.top = tk.Toplevel(parent_root)
            self.parent = parent_root
            self.top.title("注册QQ账号")
            self.top.resizable(False, False)
            self._center_window(REGISTER_W, REGISTER_H)
            self.top.transient(parent_root)
            self.top.grab_set()
            self.reg_account_var = tk.StringVar()
            self.reg_nickname_var = tk.StringVar()
            self.reg_password_var = tk.StringVar()
            self.reg_confirm_var = tk.StringVar()
            self._build_header()
            self._build_form()
            self._build_register_btn()
        except Exception as e:
            messagebox.showerror("窗口异常", f"注册窗口初始化失败：{str(e)}")

    def _center_window(self, w, h):
        screen_w = self.top.winfo_screenwidth()
        screen_h = self.top.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.top.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self):
        header = tk.Frame(self.top, bg=HEADER_COLOR, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="注册QQ账号", fg="white", bg=HEADER_COLOR, font=FONT_TITLE).pack(pady=30)

    def _create_input_row(self, parent_frame, label_text, var, show=""):
        row = tk.Frame(parent_frame, bg=BG_COLOR)
        row.pack(fill="x", pady=(0, 10))
        tk.Label(row, text=label_text, bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        entry = tk.Entry(row, textvariable=var, show=show, font=FONT_NORMAL, relief="flat", bd=0,
                         highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER)
        entry.pack(fill="x", ipady=6, pady=(2, 0))

    def _build_form(self):
        form = tk.Frame(self.top, bg=BG_COLOR)
        form.pack(fill="x", padx=40, pady=(15, 10))
        self._create_input_row(form, "账号", self.reg_account_var)
        self._create_input_row(form, "昵称", self.reg_nickname_var)
        self._create_input_row(form, "密码（6-16位）", self.reg_password_var, show="●")
        confirm_frame = tk.Frame(form, bg=BG_COLOR)
        confirm_frame.pack(fill="x")
        tk.Label(confirm_frame, text="确认密码", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        confirm_entry = tk.Entry(confirm_frame, textvariable=self.reg_confirm_var, show="●",
                                 font=FONT_NORMAL, relief="flat", bd=0, highlightthickness=1,
                                 highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER)
        confirm_entry.pack(fill="x", ipady=6, pady=(2, 0))
        confirm_entry.bind("<Return>", lambda e: self._on_register())

    def _build_register_btn(self):
        tk.Button(self.top, text="立即注册", command=self._on_register, bg=BTN_COLOR, fg="white",
                  activebackground=BTN_ACTIVE, activeforeground="white", font=FONT_BTN,
                  relief="flat", cursor="hand2", bd=0).pack(fill="x", padx=40, ipady=8, pady=(5, 0))

    def _on_register(self):
        try:
            account = self.reg_account_var.get().strip()
            nickname = self.reg_nickname_var.get().strip()
            pwd = self.reg_password_var.get().strip()
            confirm_pwd = self.reg_confirm_var.get().strip()
            if not account:
                messagebox.showwarning("提示", "请输入账号！", parent=self.top); return
            if not nickname:
                messagebox.showwarning("提示", "请输入昵称！", parent=self.top); return
            if not pwd:
                messagebox.showwarning("提示", "请输入密码！", parent=self.top); return
            if not confirm_pwd:
                messagebox.showwarning("提示", "请再次输入密码！", parent=self.top); return
            if not account.isalnum() or not (3 <= len(account) <= 16):
                messagebox.showwarning("格式错误", "账号仅支持字母/数字，长度3~16位", parent=self.top); return
            if not (6 <= len(pwd) <= 16):
                messagebox.showwarning("格式错误", "密码长度必须6~16位", parent=self.top); return
            if pwd != confirm_pwd:
                messagebox.showerror("错误", "两次输入密码不一致", parent=self.top); return
            if account_exists(account):
                messagebox.showerror("错误", f"账号 {account} 已被注册", parent=self.top); return
            create_new_user(account, nickname, pwd)
            messagebox.showinfo("注册成功", f"账号 {account} 注册完成，可返回登录！", parent=self.top)
            self.top.destroy()
        except Exception as err:
            messagebox.showerror("注册失败", f"程序异常：{str(err)}", parent=self.top)

# ====================== 主页窗口类 ======================
class MainWindow:
    def __init__(self, root, login_account, user_info):
        try:
            self.root = root
            self.account = login_account
            self.user = user_info
            self.root.title(f"QQ - {self.user['nickname']}")
            self.root.geometry(f"{MAIN_W}x{MAIN_H}")
            self.root.resizable(False, False)

            self.current_page = "home"
            self.current_chat_target_account = None
            self.current_chat_target_nickname = None
            self.last_msg_count = 0
            self.polling_id = None
            self.chat_photo_path = ""
            self.chat_video_path = ""

            self.level_stars = self.user.get("level_stars", 0)
            self.level_timer_id = None
            self._start_level_timer()

            self.side_frame = tk.Frame(self.root, bg="#2C3E50", width=120)
            self.side_frame.pack(side="left", fill="y")
            self.side_frame.pack_propagate(False)

            tk.Button(self.side_frame, text="主页", width=12, height=2, command=self.show_home_page).pack(pady=8)
            tk.Button(self.side_frame, text="开始聊天", width=12, height=2, command=self.show_chat_page).pack(pady=8)
            tk.Button(self.side_frame, text="朋友圈", width=12, height=2, command=self.show_moments_page).pack(pady=8)
            tk.Button(self.side_frame, text="每日打卡", width=12, height=2, command=self.show_checkin_page).pack(pady=8)
            tk.Button(self.side_frame, text="退出登录", width=12, height=2, bg=LOGOUT_BG, fg="white", command=self._logout).pack(pady=30)

            self.main_container = tk.Frame(self.root, bg=BG_COLOR)
            self.main_container.pack(side="right", fill="both", expand=True)
            self.show_home_page()
        except Exception as e:
            messagebox.showerror("页面异常", f"主页初始化失败：{str(e)}")

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        if self.polling_id:
            self.root.after_cancel(self.polling_id)
            self.polling_id = None

    def show_home_page(self):
        self.current_page = "home"
        self.clear_main_container()

        header = tk.Frame(self.main_container, bg=HEADER_COLOR, height=120)
        header.pack(fill="x"); header.pack_propagate(False)
        tk.Label(header, text="QQ主页", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"当前登录账号：{self.account}", fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR, font=("Arial", 16), relief="flat", command=self.root.quit).place(x=370, y=10)

        card = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        card.pack(fill="x", padx=20, pady=15)
        avatar_text = self.user.get("avatar", "🐧")
        tk.Label(card, text=avatar_text, font=FONT_EMOJI, bg=CARD_BG).pack(side="left")
        info_frame = tk.Frame(card, bg=CARD_BG)
        info_frame.pack(side="left", padx=15)
        top_info_row = tk.Frame(info_frame, bg=CARD_BG)
        top_info_row.pack(anchor="w", fill="x")
        tk.Label(top_info_row, text=self.user["nickname"], bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 16, "bold")).pack(side="left")
        mood_val = self.user.get("mood", "😊开心")
        self.mood_label = tk.Label(top_info_row, text=mood_val, bg=CARD_BG, font=("Segoe UI Emoji", 14), cursor="hand2")
        self.mood_label.pack(side="left", padx=(8, 0))
        self.mood_label.bind("<Button-1>", lambda e: self._change_mood_popup())
        tk.Label(info_frame, text=f"签名：{self.user['signature']}", bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w", pady=5)
        tk.Label(info_frame, text="● 在线", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).pack(anchor="w")

        detail = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        detail.pack(fill="x", padx=20)
        tk.Label(detail, text="个人信息", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        display_text, total_stars = self.get_level_stars_display()
        info_list = [
            ("账    号", self.account), ("昵    称", self.user["nickname"]),
            ("性    别", self.user["gender"]), ("年    龄", self.user["age"]),
            ("城    市", self.user["city"]), ("个性签名", self.user["signature"]),
            ("QQ等级", display_text),
        ]
        for label, val in info_list:
            row = tk.Frame(detail, bg=CARD_BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=CARD_BG, fg=TEXT_GRAY, font=FONT_NORMAL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=CARD_BG, fg=TEXT_BLACK, font=FONT_NORMAL, anchor="w").pack(side="left")

        func_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        func_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(func_frame, text="快捷功能", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        func_items = [
            ("👥  我的好友", lambda: messagebox.showinfo("提示", "好友功能开发中")),
            ("💬  我的消息", lambda: self.show_chat_page()),
            ("📝  我的动态", lambda: self.show_moments_page()),
            ("⚙️  系统设置", lambda: messagebox.showinfo("提示", "设置功能开发中")),
            ("✏️  修改个人资料", self.edit_profile_pop),
        ]
        for text, cmd in func_items:
            tk.Button(func_frame, text=text, bg=CARD_BG, relief="flat", anchor="w", font=FONT_NORMAL, command=cmd).pack(fill="x", pady=3)

    # ==================== 聊天页面 ====================

    def show_chat_page(self):
        self.current_page = "chat"
        self.clear_main_container()
        # 重置聊天媒体文件路径
        self.chat_photo_path = ""
        self.chat_video_path = ""

        left_box = tk.Frame(self.main_container, bg="#EEEEEE", width=140)
        left_box.pack(side="left", fill="y")
        tk.Label(left_box, text="我的好友", bg="#EEEEEE", font=FONT_NORMAL).pack(pady=5)

        btn_frame = tk.Frame(left_box, bg="#EEEEEE")
        btn_frame.pack(fill="x", padx=5, pady=2)
        tk.Button(btn_frame, text="➕ 添加好友", bg=BG_COLOR, relief="flat", font=FONT_SMALL, command=self._show_add_friend_popup).pack(fill="x")
        tk.Button(btn_frame, text="📩 好友请求", bg=BG_COLOR, relief="flat", font=FONT_SMALL, command=self._show_pending_requests).pack(fill="x", pady=(2,0))

        self.chat_listbox = tk.Listbox(left_box, font=FONT_NORMAL)
        self.chat_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.friend_accounts = []
        self._refresh_friend_list()
        self.chat_listbox.bind("<<ListboxSelect>>", self.load_target_chat)

        chat_area = tk.Frame(self.main_container, bg="white")
        chat_area.pack(side="right", fill="both", expand=True, padx=5)
        self.chat_title = tk.Label(chat_area, text="请选择好友开始聊天", bg="white", font=FONT_TITLE)
        self.chat_title.pack(fill="x", pady=10)
        self.msg_display = scrolledtext.ScrolledText(chat_area, bg=BG_COLOR, fg=TEXT_BLACK, font=FONT_NORMAL, wrap="word", state="disabled")
        self.msg_display.pack(fill="both", expand=True, padx=10, pady=5)

        input_frame = tk.Frame(chat_area, bg="white")
        input_frame.pack(fill="x", padx=10, pady=(5, 10))

        # 媒体文件选择按钮和标签
        self.chat_photo_label = tk.Label(input_frame, text="", bg="white", fg=TEXT_LIGHT_GRAY, font=FONT_SMALL)
        self.chat_photo_label.pack(side="left", padx=(0, 2))
        tk.Button(input_frame, text="📷", font=("Segoe UI Emoji", 12), bg="white", relief="flat",
                  command=self._select_chat_photo).pack(side="left", padx=1)

        self.chat_video_label = tk.Label(input_frame, text="", bg="white", fg=TEXT_LIGHT_GRAY, font=FONT_SMALL)
        self.chat_video_label.pack(side="left", padx=(0, 2))
        tk.Button(input_frame, text="🎬", font=("Segoe UI Emoji", 12), bg="white", relief="flat",
                  command=self._select_chat_video).pack(side="left", padx=1)

        self.msg_input = tk.Entry(input_frame, font=FONT_NORMAL, highlightthickness=1, highlightcolor=HEADER_COLOR, highlightbackground=INPUT_BORDER)
        self.msg_input.pack(side="left", fill="x", expand=True, ipady=5, padx=(4, 4))
        self.msg_input.bind("<Return>", lambda e: self.send_chat_msg())
        tk.Button(input_frame, text="发送", bg=BTN_COLOR, fg="white", command=self.send_chat_msg).pack(side="right", padx=2)

    def _select_chat_photo(self):
        path = filedialog.askopenfilename(title="选择聊天图片", filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp")])
        if path:
            self.chat_photo_path = path
            name = os.path.basename(path)
            if len(name) > 10: name = name[:8] + "…"
            self.chat_photo_label.config(text=f"📎{name}")

    def _select_chat_video(self):
        path = filedialog.askopenfilename(title="选择聊天视频", filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv"), ("所有文件", "*.*")])
        if path:
            self.chat_video_path = path
            name = os.path.basename(path)
            if len(name) > 10: name = name[:8] + "…"
            self.chat_video_label.config(text=f"🎬{name}")

    def _refresh_friend_list(self):
        self.chat_listbox.delete(0, tk.END)
        self.friend_accounts = []
        friends = get_friend_list(self.account)
        if not friends:
            self.chat_listbox.insert(tk.END, "（暂无好友）")
            return
        for f in friends:
            self.chat_listbox.insert(tk.END, f"{f['account']} - {f['nickname']}")
            self.friend_accounts.append(f["account"])

    def _show_add_friend_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("添加好友"); pop.geometry("400x420"); pop.transient(self.root); pop.grab_set(); pop.resizable(False, False)
        tk.Label(pop, text="🔍 搜索用户", font=FONT_TITLE, bg=HEADER_COLOR, fg="white").pack(fill="x", ipady=10)
        search_frame = tk.Frame(pop, bg=CARD_BG)
        search_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(search_frame, text="输入账号或昵称：", font=FONT_NORMAL).pack(anchor="w")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=FONT_NORMAL, highlightthickness=1, highlightcolor=HEADER_COLOR, highlightbackground=INPUT_BORDER)
        search_entry.pack(fill="x", ipady=4, pady=5); search_entry.focus()
        result_frame = tk.Frame(pop, bg=BG_COLOR)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        result_canvas = tk.Canvas(result_frame, bg=BG_COLOR, highlightthickness=0, height=120)
        result_scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=result_canvas.yview)
        result_inner = tk.Frame(result_canvas, bg=BG_COLOR)
        result_inner.bind("<Configure>", lambda e: result_canvas.configure(scrollregion=result_canvas.bbox("all")))
        result_canvas.create_window((0, 0), window=result_inner, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)
        result_canvas.pack(side="left", fill="both", expand=True); result_scrollbar.pack(side="right", fill="y")
        def do_search():
            keyword = search_var.get().strip()
            if not keyword: return
            for w in result_inner.winfo_children(): w.destroy()
            results = search_users(keyword)
            friends = get_friend_list(self.account)
            friend_accounts = [f["account"] for f in friends]
            if not results:
                tk.Label(result_inner, text="未找到匹配的用户", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL).pack(pady=20); return
            for user in results:
                if user["account"] == self.account or user["account"] in friend_accounts: continue
                row = tk.Frame(result_inner, bg=CARD_BG, padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{user['account']} - {user['nickname']}", bg=CARD_BG, font=FONT_NORMAL).pack(side="left")
                tk.Button(row, text="添加好友", bg=BTN_COLOR, fg="white", font=FONT_SMALL, relief="flat", padx=8, command=lambda a=user["account"], n=user["nickname"], r=row: _do_add(a, n, r)).pack(side="right")
        def _do_add(target_account, target_nickname, row_widget):
            ok = send_friend_request(self.account, self.user["nickname"], target_account)
            if ok:
                for w in row_widget.winfo_children(): w.destroy()
                tk.Label(row_widget, text="✅ 已发送请求", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).pack(side="left")
            else:
                messagebox.showinfo("提示", "请求发送失败，可能已是好友或已发送过请求", parent=pop)
        search_entry.bind("<Return>", lambda e: do_search())
        tk.Button(search_frame, text="搜索", bg=BTN_COLOR, fg="white", font=FONT_BTN, command=do_search).pack(fill="x", ipady=4)
        tk.Frame(pop, bg=DIVIDER_GRAY, height=1).pack(fill="x", padx=20)
        tk.Label(pop, text="📩 收到的好友请求", font=("Microsoft YaHei", 11, "bold"), bg=BG_COLOR).pack(anchor="w", padx=20, pady=(10, 0))
        pending_frame = tk.Frame(pop, bg=BG_COLOR); pending_frame.pack(fill="x", padx=20, pady=5)
        requests = get_pending_requests(self.account)
        if not requests:
            tk.Label(pending_frame, text="暂无好友请求", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w")
        else:
            for req in requests:
                req_row = tk.Frame(pending_frame, bg=CARD_BG, padx=10, pady=5); req_row.pack(fill="x", pady=3)
                tk.Label(req_row, text=f"{req['from_account']} - {req['from_nickname']}", bg=CARD_BG, font=FONT_NORMAL).pack(side="left")
                tk.Button(req_row, text="接受", bg=ONLINE_GREEN, fg="white", font=FONT_SMALL, relief="flat", padx=6, command=lambda a=req["from_account"], n=req["from_nickname"], r=req_row: _do_accept(a, n, r)).pack(side="right", padx=2)
                tk.Button(req_row, text="拒绝", bg=LOGOUT_BG, fg="white", font=FONT_SMALL, relief="flat", padx=6, command=lambda a=req["from_account"], r=req_row: _do_reject(a, r)).pack(side="right", padx=2)
        def _do_accept(from_account, from_nickname, row_widget):
            ok = accept_friend_request(self.account, from_account, from_nickname, self.user["nickname"])
            if ok:
                for w in row_widget.winfo_children(): w.destroy()
                tk.Label(row_widget, text="✅ 已接受", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).pack(side="left")
                self._refresh_friend_list()
        def _do_reject(from_account, row_widget):
            ok = reject_friend_request(self.account, from_account)
            if ok:
                for w in row_widget.winfo_children(): w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG, fg=TEXT_GRAY, font=FONT_SMALL).pack(side="left")

    def _show_pending_requests(self):
        pop = tk.Toplevel(self.root)
        pop.title("好友请求"); pop.geometry("380x300"); pop.transient(self.root); pop.grab_set(); pop.resizable(False, False)
        tk.Label(pop, text="📩 好友请求管理", font=FONT_TITLE, bg=HEADER_COLOR, fg="white").pack(fill="x", ipady=10)
        tk.Label(pop, text="收到的请求", font=("Microsoft YaHei", 11, "bold"), bg=BG_COLOR).pack(anchor="w", padx=20, pady=(10, 0))
        in_frame = tk.Frame(pop, bg=BG_COLOR); in_frame.pack(fill="x", padx=20, pady=5)
        requests = get_pending_requests(self.account)
        if not requests:
            tk.Label(in_frame, text="暂无收到的好友请求", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w", pady=10)
        else:
            for req in requests:
                row = tk.Frame(in_frame, bg=CARD_BG, padx=10, pady=5); row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{req['from_account']} - {req['from_nickname']}", bg=CARD_BG, font=FONT_NORMAL).pack(side="left")
                tk.Button(row, text="接受", bg=ONLINE_GREEN, fg="white", font=FONT_SMALL, relief="flat", padx=6, command=lambda a=req["from_account"], n=req["from_nickname"], r=row: _acc(a, n, r)).pack(side="right", padx=2)
                tk.Button(row, text="拒绝", bg=LOGOUT_BG, fg="white", font=FONT_SMALL, relief="flat", padx=6, command=lambda a=req["from_account"], r=row: _rej(a, r)).pack(side="right", padx=2)
        def _acc(from_account, from_nickname, row_widget):
            ok = accept_friend_request(self.account, from_account, from_nickname, self.user["nickname"])
            if ok:
                for w in row_widget.winfo_children(): w.destroy()
                tk.Label(row_widget, text="✅ 已接受", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).pack(side="left")
                self._refresh_friend_list()
        def _rej(from_account, row_widget):
            ok = reject_friend_request(self.account, from_account)
            if ok:
                for w in row_widget.winfo_children(): w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG, fg=TEXT_GRAY, font=FONT_SMALL).pack(side="left")
        tk.Frame(pop, bg=DIVIDER_GRAY, height=1).pack(fill="x", padx=20, pady=10)
        tk.Label(pop, text="💡 在聊天界面点击「添加好友」搜索并添加好友", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(pady=5)

    def load_target_chat(self, event):
        sel = self.chat_listbox.curselection()
        if not sel or not self.friend_accounts: return
        idx = sel[0]
        if idx >= len(self.friend_accounts): return
        target_account = self.friend_accounts[idx]
        target_nickname = USER_DB.get(target_account, {}).get("nickname", target_account)
        self.current_chat_target_account = target_account
        self.current_chat_target_nickname = target_nickname
        self.chat_title.config(text=f"和【{target_nickname}】聊天")
        self._refresh_chat_display()
        self._start_polling()

    def _refresh_chat_display(self):
        if not self.current_chat_target_account: return
        messages = load_conversation(self.account, self.current_chat_target_account)
        self.last_msg_count = len(messages)
        self.msg_display.config(state="normal")
        self.msg_display.delete(1.0, tk.END)
        self.msg_display.insert(tk.END, f"--- 与 {self.current_chat_target_nickname} 的聊天 ---\n\n")
        for msg in messages:
            sender = msg.get("sender_nickname", msg.get("sender_account", "未知"))
            send_time = msg.get("time", ""); content = msg.get("content", "")
            line = f"[{send_time}] {sender}：{content}"
            # 显示图片标记
            photo_path = msg.get("photo", "")
            if photo_path:
                line += f" [📷图片]"
            # 显示视频标记
            video_path = msg.get("video", "")
            if video_path:
                line += f" [🎬视频]"
            self.msg_display.insert(tk.END, line + "\n")
        self.msg_display.config(state="disabled")
        self.msg_display.see(tk.END)

    def _start_polling(self):
        if self.polling_id:
            self.root.after_cancel(self.polling_id); self.polling_id = None
        def poll():
            if self.current_page != "chat" or not self.current_chat_target_account: return
            messages = load_conversation(self.account, self.current_chat_target_account)
            if len(messages) != self.last_msg_count: self._refresh_chat_display()
            self.polling_id = self.root.after(2000, poll)
        self.polling_id = self.root.after(2000, poll)

    def send_chat_msg(self):
        if not self.current_chat_target_account:
            messagebox.showwarning("提示", "请先选择好友！"); return
        text = self.msg_input.get().strip()
        if not text and not self.chat_photo_path and not self.chat_video_path:
            messagebox.showwarning("提示", "请输入消息内容或选择图片/视频！")
            return
        try:
            # 准备要发送的媒体路径，如果文件不存在则置空
            photo = self.chat_photo_path if self.chat_photo_path and os.path.isfile(self.chat_photo_path) else ""
            video = self.chat_video_path if self.chat_video_path and os.path.isfile(self.chat_video_path) else ""
            send_message(
                sender_account=self.account,
                sender_nickname=self.user["nickname"],
                target_account=self.current_chat_target_account,
                content=text,
                photo_path=photo,
                video_path=video,
            )
            self.msg_input.delete(0, tk.END)
            self.chat_photo_path = ""
            self.chat_video_path = ""
            self.chat_photo_label.config(text="")
            self.chat_video_label.config(text="")
            self._refresh_chat_display()
        except Exception as e:
            messagebox.showerror("发送失败", f"消息发送出错：{str(e)}\n\n请检查文件是否存在或格式是否正确")

    # ==================== 修改个人资料 ====================

    def edit_profile_pop(self):
        pop = tk.Toplevel(self.root)
        pop.title("修改个人资料"); pop.geometry("360x420"); pop.transient(self.root); pop.resizable(False, False)

        tk.Label(pop, text="头像：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(15, 0))
        avatar_var = tk.StringVar(value=self.user.get("avatar", "🐧"))
        avatars = ["🐧", "🐶", "🐱", "🐼", "🐨", "🦊", "🐰", "🐯"]
        avatar_frame = tk.Frame(pop); avatar_frame.pack(pady=3)
        for ava in avatars:
            tk.Radiobutton(avatar_frame, text=ava, variable=avatar_var, value=ava, font=("Segoe UI Emoji", 16)).pack(side="left")

        tk.Label(pop, text="昵称：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        nick_var = tk.StringVar(value=self.user["nickname"])
        tk.Entry(pop, textvariable=nick_var, width=30, font=FONT_NORMAL).pack(pady=3)

        tk.Label(pop, text="性别：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        gender_var = tk.StringVar(value=self.user.get("gender", "保密"))
        gender_frame = tk.Frame(pop); gender_frame.pack(pady=3)
        for g in ["男", "女", "保密"]:
            tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g, font=FONT_NORMAL).pack(side="left", padx=5)

        tk.Label(pop, text="年龄：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        age_var = tk.StringVar(value=self.user.get("age", "未知"))
        tk.Entry(pop, textvariable=age_var, width=30, font=FONT_NORMAL).pack(pady=3)

        tk.Label(pop, text="城市：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        city_var = tk.StringVar(value=self.user.get("city", "未知"))
        tk.Entry(pop, textvariable=city_var, width=30, font=FONT_NORMAL).pack(pady=3)

        tk.Label(pop, text="个性签名：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        sign_var = tk.StringVar(value=self.user.get("signature", ""))
        tk.Entry(pop, textvariable=sign_var, width=30, font=FONT_NORMAL).pack(pady=3)

        def save_info():
            try:
                new_avatar = avatar_var.get(); new_nick = nick_var.get().strip()
                new_gender = gender_var.get(); new_age = age_var.get().strip()
                new_city = city_var.get().strip(); new_sign = sign_var.get().strip()
                self.user["avatar"] = new_avatar
                if new_nick: self.user["nickname"] = new_nick
                self.user["gender"] = new_gender
                if new_age: self.user["age"] = new_age
                if new_city: self.user["city"] = new_city
                if new_sign: self.user["signature"] = new_sign
                if self.account in USER_DB:
                    USER_DB[self.account].update({
                        "nickname": self.user["nickname"], "gender": self.user["gender"],
                        "age": self.user["age"], "city": self.user["city"],
                        "signature": self.user["signature"], "avatar": self.user["avatar"],
                    })
                save_user_db(USER_DB)
                messagebox.showinfo("成功", "资料修改完成！")
                pop.destroy(); self.show_home_page()
            except Exception as e:
                messagebox.showerror("保存失败", f"修改资料时发生错误：{str(e)}")

        tk.Button(pop, text="保存修改", bg=BTN_COLOR, fg="white", font=FONT_BTN, command=save_info).pack(pady=15)

    # ==================== 朋友圈页面 ====================

    def show_moments_page(self):
        self.current_page = "moments"
        self.clear_main_container()

        header = tk.Frame(self.main_container, bg=HEADER_COLOR, height=120)
        header.pack(fill="x"); header.pack_propagate(False)
        tk.Label(header, text="朋友圈", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"{self.user['nickname']} 的动态", fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR, font=("Arial", 16), relief="flat", command=self.root.quit).place(x=370, y=10)

        post_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=10)
        post_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(post_frame, text="发动态", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 12, "bold")).pack(anchor="w")

        input_row = tk.Frame(post_frame, bg=CARD_BG)
        input_row.pack(fill="x", pady=(5, 0))

        self.moment_input = tk.Entry(input_row, font=FONT_NORMAL, highlightthickness=1, highlightcolor=HEADER_COLOR, highlightbackground=INPUT_BORDER)
        self.moment_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.moment_input.bind("<Return>", lambda e: self._do_publish_moment())

        self.photo_path_var = tk.StringVar()
        photo_btn = tk.Button(input_row, text="📷", font=("Segoe UI Emoji", 14), bg=CARD_BG, relief="flat", command=self._select_photo)
        photo_btn.pack(side="right", padx=(4, 4))
        self.photo_label = tk.Label(input_row, text="", bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL, width=10, anchor="e")
        self.photo_label.pack(side="right")

        self.moment_video_path = ""
        self.video_label_var = tk.StringVar(value="")
        tk.Label(input_row, textvariable=self.video_label_var, bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(side="right", padx=(0, 2))
        tk.Button(input_row, text="🎬", font=("Segoe UI Emoji", 12), bg=CARD_BG, relief="flat", command=self._select_moment_video).pack(side="right", padx=2)

        tk.Button(input_row, text="发布", bg=BTN_COLOR, fg="white", command=self._do_publish_moment).pack(side="right", padx=(8, 0))

        list_container = tk.Frame(self.main_container, bg=BG_COLOR)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        canvas = tk.Canvas(list_container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.moments_scroll_frame = tk.Frame(canvas, bg=BG_COLOR)
        self.moments_scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.moments_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True); scrollbar.pack(side="right", fill="y")

        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        self._canvas = canvas

        self._refresh_moments_list()

    def _select_photo(self):
        path = filedialog.askopenfilename(title="选择照片", filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp")])
        if path:
            self.photo_path_var.set(path)
            name = os.path.basename(path)
            if len(name) > 12: name = name[:10] + "…"
            self.photo_label.config(text=f"📎{name}")

    def _select_moment_video(self):
        file_path = filedialog.askopenfilename(title="选择视频文件", parent=self.root, filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("所有文件", "*.*")])
        if file_path:
            self.moment_video_path = file_path
            fname = os.path.basename(file_path)
            if len(fname) > 12: fname = fname[:10] + "…"
            self.video_label_var.set(f"🎬{fname}")

    def _do_publish_moment(self):
        content = self.moment_input.get().strip()
        if not content and not self.moment_video_path and not self.photo_path_var.get():
            messagebox.showwarning("提示", "请输入动态内容或选择图片/视频！"); return
        try:
            photo = self.photo_path_var.get()
            add_moment(account=self.account, nickname=self.user["nickname"], avatar=self.user.get("avatar", "🐧"), content=content, photo_path=photo, video_path=self.moment_video_path)
            self.moment_input.delete(0, tk.END)
            self.photo_path_var.set(""); self.photo_label.config(text="")
            self.moment_video_path = ""; self.video_label_var.set("")
            self._refresh_moments_list()
        except Exception as e:
            messagebox.showerror("发布失败", f"动态发布出错：{str(e)}")

    def _refresh_moments_list(self):
        for w in self.moments_scroll_frame.winfo_children(): w.destroy()
        moments = load_moments_data()
        if not moments:
            tk.Label(self.moments_scroll_frame, text="暂无动态，快来发第一条吧 ✨", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL, pady=40).pack()
            return
        for m in moments: self._render_moment_card(m)

    def _render_moment_card(self, m):
        card = tk.Frame(self.moments_scroll_frame, bg=CARD_BG, padx=12, pady=10)
        card.pack(fill="x", pady=6)
        top_row = tk.Frame(card, bg=CARD_BG); top_row.pack(fill="x")
        avatar_text = m.get("avatar", "🐧")
        tk.Label(top_row, text=avatar_text, font=("Segoe UI Emoji", 24), bg=CARD_BG).pack(side="left", padx=(0, 8))
        info_col = tk.Frame(top_row, bg=CARD_BG); info_col.pack(side="left", fill="x", expand=True)
        tk.Label(info_col, text=m["nickname"], bg=CARD_BG, fg=HEADER_COLOR, font=("Microsoft YaHei", 11, "bold"), anchor="w").pack(fill="x")
        tk.Label(info_col, text=m["time"], bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL, anchor="w").pack(fill="x")
        tk.Label(card, text=m["content"], bg=CARD_BG, fg=TEXT_BLACK, font=FONT_NORMAL, anchor="w", justify="left", wraplength=280).pack(fill="x", pady=(8, 5))

        video_path = m.get("video", "")
        if video_path and os.path.isfile(video_path):
            video_frame = tk.Frame(card, bg="#F0F0F0", padx=8, pady=6); video_frame.pack(fill="x", pady=(0, 5))
            tk.Label(video_frame, text="🎬 视频附件", bg="#F0F0F0", fg=HEADER_COLOR, font=("Microsoft YaHei", 10, "bold")).pack(side="left")
            tk.Button(video_frame, text="▶ 播放", bg=BTN_COLOR, fg="white", font=FONT_SMALL, relief="flat", padx=10, command=lambda p=video_path: self._play_video(p)).pack(side="right")

        photo_name = m.get("photo", "")
        if photo_name:
            photo_full = os.path.join(MOMENTS_PHOTO_DIR, photo_name)
            if os.path.exists(photo_full):
                try:
                    img = Image.open(photo_full); img.thumbnail((260, 400), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    img_label = tk.Label(card, image=tk_img, bg=CARD_BG); img_label.image = tk_img
                    img_label.pack(pady=(0, 5))
                    img_label.bind("<Button-1>", lambda e, p=photo_full: self._show_photo_popup(p))
                except Exception: pass

        action_row = tk.Frame(card, bg=CARD_BG); action_row.pack(fill="x")
        liked = self.account in m.get("liked_accounts", [])
        like_text = f"❤️ {m['likes']}" if liked else f"🤍 {m['likes']}"
        tk.Button(action_row, text=like_text, bg=CARD_BG, relief="flat", font=FONT_SMALL, fg=TEXT_GRAY, command=lambda mid=m["id"]: self._do_toggle_like(mid)).pack(side="left", padx=(0, 10))
        if m.get("account") == self.account:
            tk.Button(action_row, text="🗑 删除", bg=CARD_BG, relief="flat", font=FONT_SMALL, fg="red", command=lambda mid=m["id"]: self._do_delete_moment(mid)).pack(side="left")

    def _do_toggle_like(self, moment_id):
        result = toggle_like_moment(moment_id, self.account)
        if result: self._refresh_moments_list()

    def _do_delete_moment(self, moment_id):
        if messagebox.askyesno("确认删除", "确定要删除这条动态吗？"):
            if delete_moment(moment_id, self.account): self._refresh_moments_list()

    def _play_video(self, video_path):
        try:
            if os.name == 'nt':
                os.startfile(video_path)
            elif os.name == 'posix':
                subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', video_path))
        except Exception as e:
            messagebox.showerror("播放失败", f"无法打开视频文件：{str(e)}")

    def _show_photo_popup(self, photo_full_path):
        try:
            pop = tk.Toplevel(self.root); pop.title("查看照片")
            img = Image.open(photo_full_path)
            max_w, max_h = 600, 500; w, h = img.size
            if w > max_w or h > max_h:
                ratio = min(max_w / w, max_h / h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(pop, image=tk_img); label.image = tk_img; label.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片：{str(e)}")

    # ==================== 每日打卡页面 ====================

    def show_checkin_page(self):
        self.current_page = "checkin"
        self.clear_main_container()
        header = tk.Frame(self.main_container, bg=HEADER_COLOR, height=120)
        header.pack(fill="x"); header.pack_propagate(False)
        tk.Label(header, text="每日打卡", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"{self.user['nickname']}，坚持就是胜利！", fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR, font=("Arial", 16), relief="flat", command=self.root.quit).place(x=370, y=10)

        status = get_checkin_status(self.account)
        stat_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        stat_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(stat_frame, text="打卡统计", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 14, "bold")).pack(anchor="w", pady=(0, 10))
        stats_row = tk.Frame(stat_frame, bg=CARD_BG); stats_row.pack(fill="x", pady=5)
        total_frame = tk.Frame(stats_row, bg=CARD_BG); total_frame.pack(side="left", expand=True)
        tk.Label(total_frame, text=f"{status['total']}", fg=HEADER_COLOR, bg=CARD_BG, font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(total_frame, text="总打卡天数", bg=CARD_BG, fg=TEXT_GRAY, font=FONT_SMALL).pack()
        streak_frame = tk.Frame(stats_row, bg=CARD_BG); streak_frame.pack(side="left", expand=True)
        tk.Label(streak_frame, text=f"{status['streak']}", fg="#FF6B35", bg=CARD_BG, font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(streak_frame, text="连续打卡天数", bg=CARD_BG, fg=TEXT_GRAY, font=FONT_SMALL).pack()
        self.checkin_btn_frame = tk.Frame(self.main_container, bg=BG_COLOR); self.checkin_btn_frame.pack(fill="x", padx=20, pady=10)
        if status["checked_in"]:
            tk.Button(self.checkin_btn_frame, text="✅ 今日已打卡", bg="#52C41A", fg="white", font=FONT_BTN, relief="flat", state="disabled", padx=20, pady=10).pack()
            tk.Label(self.checkin_btn_frame, text="太棒了，明天继续加油！", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(pady=5)
        else:
            tk.Label(self.checkin_btn_frame, text="今天还没有打卡哦，快来打卡吧！", bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL).pack(pady=(0, 10))
            tk.Button(self.checkin_btn_frame, text="🎯 立即打卡", bg=BTN_COLOR, fg="white", font=FONT_BTN, relief="flat", padx=30, pady=12, command=self._do_checkin_action).pack()

        cal_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15); cal_frame.pack(fill="x", padx=20, pady=15)
        today = datetime.now(); year = today.year; month = today.month
        _, days_in_month = monthrange(year, month)
        month_records = get_month_records(self.account, year, month)
        tk.Label(cal_frame, text=f"{year}年{month}月打卡日历", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        weekday_frame = tk.Frame(cal_frame, bg=CARD_BG); weekday_frame.pack(fill="x")
        for wd in ["一", "二", "三", "四", "五", "六", "日"]:
            tk.Label(weekday_frame, text=wd, bg=CARD_BG, fg=TEXT_GRAY, font=FONT_SMALL, width=4, anchor="center").pack(side="left", padx=4)
        grid_frame = tk.Frame(cal_frame, bg=CARD_BG); grid_frame.pack(fill="x", pady=(5, 0))
        first_weekday_sun = (datetime(year, month, 1).weekday() + 1) % 7
        col = 0
        for _ in range(first_weekday_sun):
            tk.Label(grid_frame, text="", bg=CARD_BG, width=4).pack(side="left", padx=4); col += 1
        for day in range(1, days_in_month + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            is_checked = date_str in month_records
            if is_checked:
                tk.Label(grid_frame, text=f"{day}✅", bg="#E8F5E9", fg="#2E7D32", font=FONT_SMALL, width=4, relief="solid", bd=1).pack(side="left", padx=4, pady=2)
            elif day == today.day:
                tk.Label(grid_frame, text=str(day), bg="#E3F2FD", fg=HEADER_COLOR, font=FONT_SMALL, width=4, relief="solid", bd=1).pack(side="left", padx=4, pady=2)
            else:
                tk.Label(grid_frame, text=str(day), bg=CARD_BG, fg=TEXT_BLACK, font=FONT_SMALL, width=4, bd=1).pack(side="left", padx=4, pady=2)
            col += 1
            if col >= 7: col = 0

    def _do_checkin_action(self):
        try:
            result = do_checkin(self.account)
            if result["already"]:
                messagebox.showinfo("提示", "今天已经打过卡了哦！")
            else:
                messagebox.showinfo("打卡成功", f"🎉 打卡成功！\n\n连续打卡：{result['streak']} 天\n总打卡次数：{result['total']} 次\n\n继续坚持！")
            self.show_checkin_page()
        except Exception as e:
            messagebox.showerror("打卡失败", f"打卡操作出错：{str(e)}")

    # ==================== 心情状态切换 ====================
    def _change_mood_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("设置心情状态"); pop.geometry("300x200"); pop.transient(self.root); pop.grab_set(); pop.resizable(False, False)
        tk.Label(pop, text="选择你的心情状态：", font=FONT_NORMAL).pack(pady=(20, 10))
        moods = [("😊开心", "😊开心"), ("😢伤心", "😢伤心"), ("😐平静", "😐平静")]
        def set_mood(mood_val):
            self.user["mood"] = mood_val; self.mood_label.config(text=mood_val)
            if self.account in USER_DB:
                USER_DB[self.account]["mood"] = mood_val; save_user_db(USER_DB)
            pop.destroy()
        for display, value in moods:
            tk.Button(pop, text=display, font=("Segoe UI Emoji", 16), bg=CARD_BG, relief="flat", anchor="w", padx=20, command=lambda v=value: set_mood(v)).pack(fill="x", padx=30, pady=3)

    # ==================== QQ等级系统 ====================
    def _start_level_timer(self):
        self._add_star()
        self.level_timer_id = self.root.after(60000, self._start_level_timer)

    def _add_star(self):
        self.level_stars += 1
        self.user["level_stars"] = self.level_stars
        save_level_stars(self.account, self.level_stars)

    def _stop_level_timer(self):
        if self.level_timer_id:
            self.root.after_cancel(self.level_timer_id); self.level_timer_id = None
        save_level_stars(self.account, self.level_stars)

    def get_level_stars_display(self):
        stars = self.level_stars
        parts = []
        if stars // 64: parts.append(f"☀️×{stars // 64}")
        if (stars % 64) // 16: parts.append(f"🌙×{(stars % 64) // 16}")
        star_count = stars % 16
        parts.append(f"⭐×{star_count if parts else stars}")
        return "  ".join(parts), stars

    def _logout(self):
        if messagebox.askyesno("确认退出", "确定要退出当前账号返回登录页？"):
            if self.polling_id:
                self.root.after_cancel(self.polling_id); self.polling_id = None
            self._stop_level_timer()
            self.root.destroy()
            run_login_window()

# ====================== 登录窗口 ======================
class QQLoginWindow:
    def __init__(self, root):
        try:
            self.root = root
            self.root.title("QQ登录")
            self.root.resizable(False, False)
            self._center_window(LOGIN_W, LOGIN_H)
            self.account_var = tk.StringVar()
            self.password_var = tk.StringVar()
            self.remember_var = tk.IntVar(value=1)
            self.auto_login_var = tk.IntVar(value=0)
            self._build_header()
            self._build_avatar()
            self._build_input_area()
            self._build_option_area()
            self._build_login_btn()
            self._build_footer()
        except Exception as e:
            messagebox.showerror("启动异常", f"登录窗口初始化失败：{str(e)}")

    def _center_window(self, w, h):
        screen_w = self.root.winfo_screenwidth(); screen_h = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(screen_w-w)//2}+{(screen_h-h)//2}")

    def _build_header(self):
        header = tk.Frame(self.root, bg=HEADER_COLOR, height=140)
        header.pack(fill="x"); header.pack_propagate(False)
        close_btn = tk.Label(header, text="✕", fg="white", bg=HEADER_COLOR, font=FONT_SMALL, cursor="hand2")
        close_btn.place(x=350, y=8); close_btn.bind("<Button-1>", lambda e: self.root.quit())
        tk.Label(header, text="QQ", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei", 22, "bold")).place(x=20, y=20)
        tk.Label(header, text="每一天，乐在沟通", fg="#E8F7FF", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=22, y=60)

    def _build_avatar(self):
        avatar_frame = tk.Frame(self.root, bg=BG_COLOR, height=90)
        avatar_frame.pack(fill="x"); avatar_frame.pack_propagate(False)
        tk.Label(avatar_frame, text="🐧", bg=BG_COLOR, font=FONT_EMOJI).pack(pady=15)

    def _build_input_area(self):
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(fill="x", padx=40, pady=(5, 10))
        tk.Label(input_frame, text="账号", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        tk.Entry(input_frame, textvariable=self.account_var, font=FONT_NORMAL, relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER).pack(fill="x", ipady=6, pady=(2, 12))
        tk.Label(input_frame, text="密码", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        pwd_entry = tk.Entry(input_frame, textvariable=self.password_var, show="●", font=FONT_NORMAL, relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER)
        pwd_entry.pack(fill="x", ipady=6, pady=(2, 0))
        pwd_entry.bind("<Return>", lambda e: self._login_action())

    def _build_option_area(self):
        opt_frame = tk.Frame(self.root, bg=BG_COLOR)
        opt_frame.pack(fill="x", padx=40, pady=(5, 15))
        tk.Checkbutton(opt_frame, text="记住密码", variable=self.remember_var, bg=BG_COLOR, activebackground=BG_COLOR, font=FONT_SMALL, fg=TEXT_GRAY, selectcolor=BG_COLOR, bd=0).pack(side="left")
        tk.Checkbutton(opt_frame, text="自动登录", variable=self.auto_login_var, bg=BG_COLOR, activebackground=BG_COLOR, font=FONT_SMALL, fg=TEXT_GRAY, selectcolor=BG_COLOR, bd=0).pack(side="right")

    def _build_login_btn(self):
        tk.Button(self.root, text="登 录", command=self._login_action, bg=BTN_COLOR, fg="white", activebackground=BTN_ACTIVE, activeforeground="white", font=FONT_BTN, relief="flat", cursor="hand2", bd=0).pack(fill="x", padx=40, ipady=8)

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=BG_COLOR); footer.pack(fill="x", padx=40, pady=15)
        reg_label = tk.Label(footer, text="注册账号", fg=HEADER_COLOR, bg=BG_COLOR, font=FONT_SMALL, cursor="hand2")
        reg_label.pack(side="left"); reg_label.bind("<Button-1>", lambda e: RegisterWindow(self.root))
        forget_label = tk.Label(footer, text="找回密码", fg=HEADER_COLOR, bg=BG_COLOR, font=FONT_SMALL, cursor="hand2")
        forget_label.pack(side="right"); forget_label.bind("<Button-1>", lambda e: messagebox.showinfo("提示", "找回密码功能待开发"))

    def _login_action(self):
        try:
            account = self.account_var.get().strip(); raw_pwd = self.password_var.get().strip()
            if not account: messagebox.showwarning("输入提示", "请填写账号！"); return
            if not raw_pwd: messagebox.showwarning("输入提示", "请填写密码！"); return
            user_data = get_user_info(account)
            if user_data is None: messagebox.showerror("登录失败", "该账号不存在，请先注册！"); return
            if not verify_password(raw_pwd, user_data["hash_pwd"]): messagebox.showerror("登录失败", "账号或密码错误！"); return
            messagebox.showinfo("登录成功", f"欢迎 {user_data['nickname']}！正在进入主页")
            self.root.destroy()
            main_root = tk.Tk()
            MainWindow(main_root, account, user_data)
            main_root.mainloop()
        except Exception as err:
            messagebox.showerror("登录异常", f"程序出错：{str(err)}")

def run_login_window():
    root = tk.Tk()
    QQLoginWindow(root)
    root.mainloop()

if __name__ == "__main__":
    run_login_window()