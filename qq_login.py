# -*- coding: utf-8 -*-
"""QQ登录整合单文件版本，无需拆分模块，直接运行"""
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from PIL import Image, ImageTk
import bcrypt
import random
from datetime import datetime
import json
import os
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
    },
    "admin": {
        "hash_pwd": b'$2b$12$dE9sK2pQ7zR5aT8xYbN0cJdF3gH6lM4vW1eS9',
        "nickname": "管理员",
        "signature": "好好学习，天天向上",
        "gender": "男",
        "age": "25",
        "city": "北京",
    },
    "qquser": {
        "hash_pwd": b'$2b$12$fR3gT7vB9nD2zP5sC8kX0jL6hM1wQ4aE7dS2',
        "nickname": "QQ用户",
        "signature": "这个人很懒，什么都没留下",
        "gender": "女",
        "age": "20",
        "city": "上海",
    },
}

def load_user_db():
    """从本地文件加载用户数据库，若文件不存在或损坏则使用默认用户"""
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
            # 文件损坏时删除损坏文件，使用默认用户
            try:
                os.remove(USER_DB_FILE)
            except Exception:
                pass
    return {account: dict(info) for account, info in DEFAULT_USERS.items()}

def save_user_db(db):
    """将用户数据库保存到本地文件"""
    to_save = {}
    for account, info in db.items():
        saved = dict(info)
        saved["hash_pwd"] = saved["hash_pwd"].decode("utf-8")
        to_save[account] = saved
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)

# 启动时加载用户数据库
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
    }
    save_user_db(USER_DB)

def get_user_info(account: str):
    return USER_DB.get(account, None)

def account_exists(account: str) -> bool:
    return account in USER_DB

# 聊天记录文件路径
CHAT_FILE = "chat_record.json"

# ====================== 动态（朋友圈）数据层 ======================
MOMENTS_FILE = "moments.json"
MOMENTS_PHOTO_DIR = "moments_photos"

# 确保照片目录存在
os.makedirs(MOMENTS_PHOTO_DIR, exist_ok=True)

def load_moments_data():
    """从本地文件读取所有动态，文件不存在返回空列表"""
    if os.path.exists(MOMENTS_FILE):
        with open(MOMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_moments_data(moments_list: list):
    """将所有动态保存到本地 JSON 文件"""
    with open(MOMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(moments_list, f, ensure_ascii=False, indent=2)

def add_moment(account: str, nickname: str, avatar: str, content: str,
               photo_path: str = "") -> dict:
    """添加一条新动态，返回新创建的动态字典"""
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
    # 分离文本内容和照片
    lines = content.strip().splitlines()
    new_moment["content"] = content.strip()
    # 照片路径（复制到本地目录）
    if photo_path:
        ext = os.path.splitext(photo_path)[1] or ".jpg"
        photo_id = new_moment["id"] + ext
        dest = os.path.join(MOMENTS_PHOTO_DIR, photo_id)
        try:
            from shutil import copy2
            copy2(photo_path, dest)
            new_moment["photo"] = photo_id
        except Exception:
            new_moment["photo"] = ""
    else:
        new_moment["photo"] = ""
    moments.insert(0, new_moment)
    save_moments_data(moments)
    return new_moment

def delete_moment(moment_id: str, account: str) -> bool:
    """删除指定动态（仅作者可删），同时删除关联的照片文件"""
    moments = load_moments_data()
    for i, m in enumerate(moments):
        if m["id"] == moment_id and m["account"] == account:
            # 删除关联的照片文件
            photo = m.get("photo", "")
            if photo:
                photo_full = os.path.join(MOMENTS_PHOTO_DIR, photo)
                try:
                    if os.path.exists(photo_full):
                        os.remove(photo_full)
                except Exception:
                    pass
            moments.pop(i)
            save_moments_data(moments)
            return True
    return False

def toggle_like_moment(moment_id: str, account: str) -> dict:
    """点赞/取消点赞"""
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

def load_chat_data():
    """读取本地聊天记录"""
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_chat_data(chat_dict):
    """保存聊天记录到本地"""
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_dict, f, ensure_ascii=False, indent=2)

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
        entry = tk.Entry(
            row, textvariable=var, show=show, font=FONT_NORMAL,
            relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER
        )
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
        confirm_entry = tk.Entry(
            confirm_frame, textvariable=self.reg_confirm_var, show="●", font=FONT_NORMAL,
            relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER
        )
        confirm_entry.pack(fill="x", ipady=6, pady=(2, 0))
        confirm_entry.bind("<Return>", lambda e: self._on_register())

    def _build_register_btn(self):
        tk.Button(
            self.top, text="立即注册", command=self._on_register,
            bg=BTN_COLOR, fg="white", activebackground=BTN_ACTIVE, activeforeground="white",
            font=FONT_BTN, relief="flat", cursor="hand2", bd=0
        ).pack(fill="x", padx=40, ipady=8, pady=(5, 0))

    def _on_register(self):
        try:
            account = self.reg_account_var.get().strip()
            nickname = self.reg_nickname_var.get().strip()
            pwd = self.reg_password_var.get().strip()
            confirm_pwd = self.reg_confirm_var.get().strip()
            if not account:
                messagebox.showwarning("提示", "请输入账号！", parent=self.top)
                return
            if not nickname:
                messagebox.showwarning("提示", "请输入昵称！", parent=self.top)
                return
            if not pwd:
                messagebox.showwarning("提示", "请输入密码！", parent=self.top)
                return
            if not confirm_pwd:
                messagebox.showwarning("提示", "请再次输入密码！", parent=self.top)
                return
            if not account.isalnum() or not (3 <= len(account) <= 16):
                messagebox.showwarning("格式错误", "账号仅支持字母/数字，长度3~16位", parent=self.top)
                return
            if not (6 <= len(pwd) <= 16):
                messagebox.showwarning("格式错误", "密码长度必须6~16位", parent=self.top)
                return
            if pwd != confirm_pwd:
                messagebox.showerror("错误", "两次输入密码不一致", parent=self.top)
                return
            if account_exists(account):
                messagebox.showerror("错误", f"账号 {account} 已被注册", parent=self.top)
                return
            create_new_user(account, nickname, pwd)
            messagebox.showinfo("注册成功", f"账号 {account} 注册完成，可返回登录！", parent=self.top)
            self.top.destroy()
        except Exception as err:
            messagebox.showerror("注册失败", f"程序异常：{str(err)}", parent=self.top)

# ====================== 主页窗口类（带聊天侧边栏完整版） ======================
class MainWindow:
    def __init__(self, root, login_account, user_info):
        try:
            self.root = root
            self.account = login_account
            self.user = user_info
            self.root.title(f"QQ - {self.user['nickname']}")
            self.root.geometry(f"{MAIN_W}x{MAIN_H}")
            self.root.resizable(False, False)

            # 聊天全局变量
            self.current_page = "home"
            self.chat_history = load_chat_data()
            self.friend_list = ["小明", "管理员", "QQ用户"]
            self.current_chat_target = None

            # 左侧侧边栏
            self.side_frame = tk.Frame(self.root, bg="#2C3E50", width=120)
            self.side_frame.pack(side="left", fill="y")
            self.side_frame.pack_propagate(False)

            # 侧边按钮
            tk.Button(self.side_frame, text="主页", width=12, height=2,
                      command=self.show_home_page).pack(pady=8)
            tk.Button(self.side_frame, text="开始聊天", width=12, height=2,
                      command=self.show_chat_page).pack(pady=8)
            tk.Button(self.side_frame, text="朋友圈", width=12, height=2,
                      command=self.show_moments_page).pack(pady=8)
            tk.Button(self.side_frame, text="退出登录", width=12, height=2,
                      bg=LOGOUT_BG, fg="white", command=self._logout).pack(pady=30)

            # 右侧主内容容器
            self.main_container = tk.Frame(self.root, bg=BG_COLOR)
            self.main_container.pack(side="right", fill="both", expand=True)

            # 默认打开主页
            self.show_home_page()

        except Exception as e:
            messagebox.showerror("页面异常", f"主页初始化失败：{str(e)}")

    def clear_main_container(self):
        """清空右侧区域，切换页面用"""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def show_home_page(self):
        """渲染个人主页"""
        self.current_page = "home"
        self.clear_main_container()

        # 顶部蓝色标题栏
        header = tk.Frame(self.main_container, bg=HEADER_COLOR, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="QQ主页", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"当前登录账号：{self.account}", fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR, font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        # 头像卡片（使用保存的头像，默认 🐧）
        card = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        card.pack(fill="x", padx=20, pady=15)
        avatar_text = self.user.get("avatar", "🐧")
        tk.Label(card, text=avatar_text, font=FONT_EMOJI, bg=CARD_BG).pack(side="left")
        info_frame = tk.Frame(card, bg=CARD_BG)
        info_frame.pack(side="left", padx=15)
        tk.Label(info_frame, text=self.user["nickname"], bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 16, "bold")).pack(anchor="w")
        tk.Label(info_frame, text=f"签名：{self.user['signature']}", bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w", pady=5)
        tk.Label(info_frame, text="● 在线", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).pack(anchor="w")

        # 个人信息面板
        detail = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        detail.pack(fill="x", padx=20)
        tk.Label(detail, text="个人信息", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        info_list = [
            ("账    号", self.account),
            ("昵    称", self.user["nickname"]),
            ("性    别", self.user["gender"]),
            ("年    龄", self.user["age"]),
            ("城    市", self.user["city"]),
            ("个性签名", self.user["signature"])
        ]
        for label, val in info_list:
            row = tk.Frame(detail, bg=CARD_BG)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=CARD_BG, fg=TEXT_GRAY, font=FONT_NORMAL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=CARD_BG, fg=TEXT_BLACK, font=FONT_NORMAL, anchor="w").pack(side="left")

        # 快捷功能区
        func_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        func_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(func_frame, text="快捷功能", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        func_items = [
            ("👥  我的好友", lambda: messagebox.showinfo("提示", "好友功能开发中")),
            ("💬  我的消息", lambda: self.show_chat_page()),
            ("📝  我的动态", lambda: self.show_moments_page()),
            ("⚙️  系统设置", lambda: messagebox.showinfo("提示", "设置功能开发中")),
            ("✏️  修改个人资料", self.edit_profile_pop)
        ]
        for text, cmd in func_items:
            tk.Button(func_frame, text=text, bg=CARD_BG, relief="flat", anchor="w",
                      font=FONT_NORMAL, command=cmd).pack(fill="x", pady=3)

    def show_chat_page(self):
        """聊天页面"""
        self.current_page = "chat"
        self.clear_main_container()

        # 左侧好友列表
        left_box = tk.Frame(self.main_container, bg="#EEEEEE", width=120)
        left_box.pack(side="left", fill="y")
        tk.Label(left_box, text="好友列表", bg="#EEEEEE", font=FONT_NORMAL).pack(pady=10)
        self.chat_listbox = tk.Listbox(left_box, font=FONT_NORMAL)
        self.chat_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        for name in self.friend_list:
            self.chat_listbox.insert(tk.END, name)
        self.chat_listbox.bind("<<ListboxSelect>>", self.load_target_chat)

        # 右侧聊天区域
        chat_area = tk.Frame(self.main_container, bg="white")
        chat_area.pack(side="right", fill="both", expand=True, padx=5)
        self.chat_title = tk.Label(chat_area, text="请选择好友开始聊天", bg="white", font=FONT_TITLE)
        self.chat_title.pack(fill="x", pady=10)

        # 消息滚动框
        self.msg_display = scrolledtext.ScrolledText(chat_area, bg=BG_COLOR, fg=TEXT_BLACK,
                                                     font=FONT_NORMAL, wrap="word", state="disabled")
        self.msg_display.pack(fill="both", expand=True, padx=10, pady=5)

        # 输入栏
        input_frame = tk.Frame(chat_area, bg="white")
        input_frame.pack(fill="x", padx=10, pady=10)
        self.msg_input = tk.Entry(input_frame, font=FONT_NORMAL, highlightthickness=1,
                                  highlightcolor=HEADER_COLOR, highlightbackground=INPUT_BORDER)
        self.msg_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.msg_input.bind("<Return>", lambda e: self.send_chat_msg())
        tk.Button(input_frame, text="发送", bg=BTN_COLOR, fg="white", command=self.send_chat_msg).pack(side="right", padx=5)

    def load_target_chat(self, event):
        """选中好友加载聊天记录"""
        sel = self.chat_listbox.curselection()
        if not sel:
            return
        target_name = self.chat_listbox.get(sel[0])
        self.current_chat_target = target_name
        self.chat_title.config(text=f"和【{target_name}】聊天")

        # 初始化空记录
        if target_name not in self.chat_history:
            self.chat_history[target_name] = []

        # 刷新消息框
        self.msg_display.config(state="normal")
        self.msg_display.delete(1.0, tk.END)
        for msg in self.chat_history[target_name]:
            self.msg_display.insert(tk.END, f"[{msg['time']}] {msg['sender']}：{msg['content']}\n")
        self.msg_display.config(state="disabled")
        self.msg_display.see(tk.END)

    def send_chat_msg(self):
        """发送消息 + 自动回复"""
        if not self.current_chat_target:
            messagebox.showwarning("提示", "请先选择好友！")
            return
        text = self.msg_input.get().strip()
        if not text:
            return

        target = self.current_chat_target
        now_time = datetime.now().strftime("%H:%M")
        # 我方消息
        my_msg = {"sender": self.user["nickname"], "content": text, "time": now_time}
        self.chat_history[target].append(my_msg)

        # 界面更新
        self.msg_display.config(state="normal")
        self.msg_display.insert(tk.END, f"[{now_time}] 我：{text}\n")
        self.msg_display.config(state="disabled")
        self.msg_input.delete(0, tk.END)
        save_chat_data(self.chat_history)

        # 延迟自动回复
        self.root.after(1000, lambda: self.auto_reply(target))

    def auto_reply(self, target_name):
        """模拟好友自动回复"""
        reply_pool = ["好的收到！", "明白了~", "哈哈有意思", "稍等我看看", "没问题！", "了解~"]
        reply_txt = random.choice(reply_pool)
        now_time = datetime.now().strftime("%H:%M")
        reply_msg = {"sender": target_name, "content": reply_txt, "time": now_time}
        self.chat_history[target_name].append(reply_msg)

        self.msg_display.config(state="normal")
        self.msg_display.insert(tk.END, f"[{now_time}] {target_name}：{reply_txt}\n")
        self.msg_display.config(state="disabled")
        self.msg_display.see(tk.END)
        save_chat_data(self.chat_history)

    def edit_profile_pop(self):
        """修改资料弹窗（含性别、年龄、地区、姓名等，自动保存到文件）"""
        pop = tk.Toplevel(self.root)
        pop.title("修改个人资料")
        pop.geometry("360x420")
        pop.transient(self.root)
        pop.resizable(False, False)

        # 头像
        tk.Label(pop, text="头像：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(15, 0))
        avatar_var = tk.StringVar(value=self.user.get("avatar", "🐧"))
        avatars = ["🐧", "🐶", "🐱", "🐼", "🐨", "🦊", "🐰", "🐯"]
        avatar_frame = tk.Frame(pop)
        avatar_frame.pack(pady=3)
        for ava in avatars:
            tk.Radiobutton(avatar_frame, text=ava, variable=avatar_var, value=ava,
                           font=("Segoe UI Emoji", 16)).pack(side="left")

        # 昵称
        tk.Label(pop, text="昵称：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        nick_var = tk.StringVar(value=self.user["nickname"])
        tk.Entry(pop, textvariable=nick_var, width=30, font=FONT_NORMAL).pack(pady=3)

        # 性别
        tk.Label(pop, text="性别：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        gender_var = tk.StringVar(value=self.user.get("gender", "保密"))
        gender_frame = tk.Frame(pop)
        gender_frame.pack(pady=3)
        for g in ["男", "女", "保密"]:
            tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g, font=FONT_NORMAL).pack(side="left", padx=5)

        # 年龄
        tk.Label(pop, text="年龄：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        age_var = tk.StringVar(value=self.user.get("age", "未知"))
        tk.Entry(pop, textvariable=age_var, width=30, font=FONT_NORMAL).pack(pady=3)

        # 城市
        tk.Label(pop, text="城市：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        city_var = tk.StringVar(value=self.user.get("city", "未知"))
        tk.Entry(pop, textvariable=city_var, width=30, font=FONT_NORMAL).pack(pady=3)

        # 个性签名
        tk.Label(pop, text="个性签名：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        sign_var = tk.StringVar(value=self.user.get("signature", ""))
        tk.Entry(pop, textvariable=sign_var, width=30, font=FONT_NORMAL).pack(pady=3)

        def save_info():
            """保存修改到内存和文件"""
            try:
                new_avatar = avatar_var.get()
                new_nick = nick_var.get().strip()
                new_gender = gender_var.get()
                new_age = age_var.get().strip()
                new_city = city_var.get().strip()
                new_sign = sign_var.get().strip()

                # 更新 self.user 对象
                self.user["avatar"] = new_avatar
                if new_nick:
                    self.user["nickname"] = new_nick
                self.user["gender"] = new_gender
                if new_age:
                    self.user["age"] = new_age
                if new_city:
                    self.user["city"] = new_city
                if new_sign:
                    self.user["signature"] = new_sign

                # 同步更新全局 USER_DB 并保存到文件
                if self.account in USER_DB:
                    USER_DB[self.account]["nickname"] = self.user["nickname"]
                    USER_DB[self.account]["gender"] = self.user["gender"]
                    USER_DB[self.account]["age"] = self.user["age"]
                    USER_DB[self.account]["city"] = self.user["city"]
                    USER_DB[self.account]["signature"] = self.user["signature"]
                    USER_DB[self.account]["avatar"] = self.user["avatar"]

                # 无论 USER_DB 中是否存在该账号，都调用保存（新注册用户创建于同一次运行中时可能在全局字典里）
                save_user_db(USER_DB)

                messagebox.showinfo("成功", "资料修改完成！")
                pop.destroy()
                self.show_home_page()
            except Exception as e:
                messagebox.showerror("保存失败", f"修改资料时发生错误：{str(e)}")

        tk.Button(pop, text="保存修改", bg=BTN_COLOR, fg="white",
                  font=FONT_BTN, command=save_info).pack(pady=15)

    # ==================== 动态（朋友圈）页面 ====================

    def show_moments_page(self):
        """呈现朋友圈页面：发布动态 + 动态列表 + 点赞/删除"""
        self.current_page = "moments"
        self.clear_main_container()

        # ----- 顶部标题栏 -----
        header = tk.Frame(self.main_container, bg=HEADER_COLOR, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="朋友圈", fg="white", bg=HEADER_COLOR,
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"{self.user['nickname']} 的动态",
                 fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR,
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        # ----- 发布动态区域 -----
        post_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=10)
        post_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(post_frame, text="发动态", bg=CARD_BG, fg=TEXT_BLACK,
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w")

        input_row = tk.Frame(post_frame, bg=CARD_BG)
        input_row.pack(fill="x", pady=(5, 0))

        self.moment_input = tk.Entry(input_row, font=FONT_NORMAL,
                                     highlightthickness=1,
                                     highlightcolor=HEADER_COLOR,
                                     highlightbackground=INPUT_BORDER)
        self.moment_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.moment_input.bind("<Return>", lambda e: self._do_publish_moment())

        # 照片选择按钮 + 照片文件名显示
        self.photo_path_var = tk.StringVar()
        photo_btn = tk.Button(
            input_row, text="📷", font=("Segoe UI Emoji", 14),
            bg=CARD_BG, relief="flat", command=self._select_photo
        )
        photo_btn.pack(side="right", padx=(4, 4))
        self.photo_label = tk.Label(
            input_row, text="", bg=CARD_BG, fg=TEXT_LIGHT_GRAY,
            font=FONT_SMALL, width=10, anchor="e"
        )
        self.photo_label.pack(side="right")

        tk.Button(input_row, text="发布", bg=BTN_COLOR, fg="white",
                  command=self._do_publish_moment).pack(side="right", padx=(8, 0))

        # ----- 动态列表（可滚动的 Canvas） -----
        list_container = tk.Frame(self.main_container, bg=BG_COLOR)
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        canvas = tk.Canvas(list_container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.moments_scroll_frame = tk.Frame(canvas, bg=BG_COLOR)

        self.moments_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.moments_scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮
        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        self._canvas = canvas

        # 渲染所有动态
        self._refresh_moments_list()

    def _select_photo(self):
        """选择照片文件"""
        path = filedialog.askopenfilename(
            title="选择照片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.gif *.bmp")]
        )
        if path:
            self.photo_path_var.set(path)
            name = os.path.basename(path)
            if len(name) > 12:
                name = name[:10] + "…"
            self.photo_label.config(text=f"📎{name}")

    def _do_publish_moment(self):
        """发布动态（含照片）"""
        content = self.moment_input.get().strip()
        if not content:
            messagebox.showwarning("提示", "请输入动态内容！")
            return
        try:
            photo = self.photo_path_var.get()
            add_moment(
                account=self.account,
                nickname=self.user["nickname"],
                avatar=self.user.get("avatar", "🐧"),
                content=content,
                photo_path=photo,
            )
            self.moment_input.delete(0, tk.END)
            self.photo_path_var.set("")
            self.photo_label.config(text="")
            self._refresh_moments_list()
        except Exception as e:
            messagebox.showerror("发布失败", f"动态发布出错：{str(e)}")

    def _refresh_moments_list(self):
        """重新渲染动态列表"""
        for w in self.moments_scroll_frame.winfo_children():
            w.destroy()

        moments = load_moments_data()
        if not moments:
            empty_label = tk.Label(
                self.moments_scroll_frame, text="暂无动态，快来发第一条吧 ✨",
                bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL, pady=40
            )
            empty_label.pack()
            return

        for m in moments:
            self._render_moment_card(m)

    def _render_moment_card(self, m):
        """渲染单条动态卡片"""
        card = tk.Frame(self.moments_scroll_frame, bg=CARD_BG, padx=12, pady=10)
        card.pack(fill="x", pady=6)

        # 头像 + 昵称 + 时间
        top_row = tk.Frame(card, bg=CARD_BG)
        top_row.pack(fill="x")

        avatar_text = m.get("avatar", "🐧")
        tk.Label(top_row, text=avatar_text, font=("Segoe UI Emoji", 24),
                 bg=CARD_BG).pack(side="left", padx=(0, 8))

        info_col = tk.Frame(top_row, bg=CARD_BG)
        info_col.pack(side="left", fill="x", expand=True)

        tk.Label(info_col, text=m["nickname"], bg=CARD_BG, fg=HEADER_COLOR,
                 font=("Microsoft YaHei", 11, "bold"), anchor="w").pack(fill="x")

        tk.Label(info_col, text=m["time"], bg=CARD_BG, fg=TEXT_LIGHT_GRAY,
                 font=FONT_SMALL, anchor="w").pack(fill="x")

        # 动态内容
        content_label = tk.Label(card, text=m["content"], bg=CARD_BG, fg=TEXT_BLACK,
                                 font=FONT_NORMAL, anchor="w", justify="left", wraplength=280)
        content_label.pack(fill="x", pady=(8, 5))

        # 照片显示
        photo_name = m.get("photo", "")
        if photo_name:
            photo_full = os.path.join(MOMENTS_PHOTO_DIR, photo_name)
            if os.path.exists(photo_full):
                try:
                    img = Image.open(photo_full)
                    img.thumbnail((260, 400), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    img_label = tk.Label(card, image=tk_img, bg=CARD_BG)
                    img_label.image = tk_img  # 防止被垃圾回收
                    img_label.pack(pady=(0, 5))
                    # 点击展开大图
                    img_label.bind("<Button-1>", lambda e, p=photo_full: self._show_photo_popup(p))
                except Exception:
                    pass

        # 底部操作栏
        action_row = tk.Frame(card, bg=CARD_BG)
        action_row.pack(fill="x")

        # 点赞按钮
        liked = self.account in m.get("liked_accounts", [])
        like_text = f"❤️ {m['likes']}" if liked else f"🤍 {m['likes']}"
        like_btn = tk.Button(
            action_row, text=like_text, bg=CARD_BG, relief="flat",
            font=FONT_SMALL, fg=TEXT_GRAY,
            command=lambda mid=m["id"]: self._do_toggle_like(mid)
        )
        like_btn.pack(side="left", padx=(0, 10))

        # 删除按钮（仅作者可见）
        if m.get("account") == self.account:
            tk.Button(
                action_row, text="🗑 删除", bg=CARD_BG, relief="flat",
                font=FONT_SMALL, fg="red",
                command=lambda mid=m["id"]: self._do_delete_moment(mid)
            ).pack(side="left")

    def _do_toggle_like(self, moment_id):
        """点赞/取消点赞"""
        result = toggle_like_moment(moment_id, self.account)
        if result:
            self._refresh_moments_list()

    def _do_delete_moment(self, moment_id):
        """删除动态"""
        confirm = messagebox.askyesno("确认删除", "确定要删除这条动态吗？")
        if confirm:
            if delete_moment(moment_id, self.account):
                self._refresh_moments_list()

    def _show_photo_popup(self, photo_full_path):
        """点击照片弹出大图窗口"""
        try:
            pop = tk.Toplevel(self.root)
            pop.title("查看照片")
            img = Image.open(photo_full_path)
            # 限制最大尺寸
            max_w, max_h = 600, 500
            w, h = img.size
            if w > max_w or h > max_h:
                ratio = min(max_w / w, max_h / h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            label = tk.Label(pop, image=tk_img)
            label.image = tk_img
            label.pack(padx=10, pady=10)
        except Exception as e:
            messagebox.showerror("错误", f"无法打开图片：{str(e)}")

    def _logout(self):
        confirm = messagebox.askyesno("确认退出", "确定要退出当前账号返回登录页？")
        if confirm:
            self.root.destroy()
            run_login_window()

# ====================== 登录窗口主类 ======================
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
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self):
        header = tk.Frame(self.root, bg=HEADER_COLOR, height=140)
        header.pack(fill="x")
        header.pack_propagate(False)
        close_btn = tk.Label(header, text="✕", fg="white", bg=HEADER_COLOR, font=FONT_SMALL, cursor="hand2")
        close_btn.place(x=350, y=8)
        close_btn.bind("<Button-1>", lambda e: self.root.quit())
        tk.Label(header, text="QQ", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei", 22, "bold")).place(x=20, y=20)
        tk.Label(header, text="每一天，乐在沟通", fg="#E8F7FF", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=22, y=60)

    def _build_avatar(self):
        avatar_frame = tk.Frame(self.root, bg=BG_COLOR, height=90)
        avatar_frame.pack(fill="x")
        avatar_frame.pack_propagate(False)
        tk.Label(avatar_frame, text="🐧", bg=BG_COLOR, font=FONT_EMOJI).pack(pady=15)

    def _build_input_area(self):
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(fill="x", padx=40, pady=(5, 10))
        tk.Label(input_frame, text="账号", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        acc_entry = tk.Entry(
            input_frame, textvariable=self.account_var, font=FONT_NORMAL,
            relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER
        )
        acc_entry.pack(fill="x", ipady=6, pady=(2, 12))
        tk.Label(input_frame, text="密码", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        pwd_entry = tk.Entry(
            input_frame, textvariable=self.password_var, show="●", font=FONT_NORMAL,
            relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER
        )
        pwd_entry.pack(fill="x", ipady=6, pady=(2, 0))
        pwd_entry.bind("<Return>", lambda e: self._login_action())

    def _build_option_area(self):
        opt_frame = tk.Frame(self.root, bg=BG_COLOR)
        opt_frame.pack(fill="x", padx=40, pady=(5, 15))
        tk.Checkbutton(
            opt_frame, text="记住密码", variable=self.remember_var, bg=BG_COLOR,
            activebackground=BG_COLOR, font=FONT_SMALL, fg=TEXT_GRAY, selectcolor=BG_COLOR, bd=0
        ).pack(side="left")
        tk.Checkbutton(
            opt_frame, text="自动登录", variable=self.auto_login_var, bg=BG_COLOR,
            activebackground=BG_COLOR, font=FONT_SMALL, fg=TEXT_GRAY, selectcolor=BG_COLOR, bd=0
        ).pack(side="right")

    def _build_login_btn(self):
        tk.Button(
            self.root, text="登 录", command=self._login_action,
            bg=BTN_COLOR, fg="white", activebackground=BTN_ACTIVE, activeforeground="white",
            font=FONT_BTN, relief="flat", cursor="hand2", bd=0
        ).pack(fill="x", padx=40, ipady=8)

    def _build_footer(self):
        footer = tk.Frame(self.root, bg=BG_COLOR)
        footer.pack(fill="x", padx=40, pady=15)
        reg_label = tk.Label(footer, text="注册账号", fg=HEADER_COLOR, bg=BG_COLOR, font=FONT_SMALL, cursor="hand2")
        reg_label.pack(side="left")
        reg_label.bind("<Button-1>", lambda e: RegisterWindow(self.root))
        forget_label = tk.Label(footer, text="找回密码", fg=HEADER_COLOR, bg=BG_COLOR, font=FONT_SMALL, cursor="hand2")
        forget_label.pack(side="right")
        forget_label.bind("<Button-1>", lambda e: messagebox.showinfo("提示", "找回密码功能待开发"))

    def _login_action(self):
        try:
            account = self.account_var.get().strip()
            raw_pwd = self.password_var.get().strip()
            if not account:
                messagebox.showwarning("输入提示", "请填写账号！")
                return
            if not raw_pwd:
                messagebox.showwarning("输入提示", "请填写密码！")
                return
            user_data = get_user_info(account)
            if user_data is None:
                messagebox.showerror("登录失败", "该账号不存在，请先注册！")
                return
            if not verify_password(raw_pwd, user_data["hash_pwd"]):
                messagebox.showerror("登录失败", "账号或密码错误！")
                return
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