# -*- coding: utf-8 -*-
"""QQ登录整合单文件版本，无需拆分模块，直接运行"""
import tkinter as tk
from tkinter import messagebox
import bcrypt

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
USER_DB = {
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

def get_user_info(account: str):
    return USER_DB.get(account, None)

def account_exists(account: str) -> bool:
    return account in USER_DB

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

# ====================== 主页窗口类 ======================
class MainWindow:
    def __init__(self, root, login_account, user_info):
        try:
            self.root = root
            self.account = login_account
            self.user = user_info
            self.root.title("QQ主页")
            self.root.resizable(False, False)
            self._center_window(MAIN_W, MAIN_H)
            self._build_header()
            self._build_profile_card()
            self._build_info_detail()
            self._build_func_area()
            self._build_logout_btn()
        except Exception as e:
            messagebox.showerror("页面异常", f"主页初始化失败：{str(e)}")

    def _center_window(self, w, h):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self):
        header = tk.Frame(self.root, bg=HEADER_COLOR, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        close_btn = tk.Label(header, text="✕", fg="white", bg=HEADER_COLOR, font=FONT_SMALL, cursor="hand2")
        close_btn.place(x=390, y=8)
        close_btn.bind("<Button-1>", lambda e: self.root.quit())
        tk.Label(header, text="QQ主页", fg="white", bg=HEADER_COLOR, font=FONT_TITLE).place(x=20, y=15)
        tk.Label(header, text=f"当前登录账号：{self.account}", fg="#E8F7FF", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=55)

    def _build_profile_card(self):
        card = tk.Frame(self.root, bg=CARD_BG, height=130)
        card.pack(fill="x", padx=20, pady=(15, 5))
        card.pack_propagate(False)
        tk.Label(card, text="🐧", bg=CARD_BG, font=FONT_EMOJI).place(x=20, y=25)
        tk.Label(card, text=self.user["nickname"], bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei",16,"bold")).place(x=110, y=30)
        tk.Label(card, text=f"签名：{self.user['signature']}", bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).place(x=110, y=70)
        tk.Label(card, text="● 在线", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).place(x=110, y=95)

    def _build_info_detail(self):
        detail = tk.Frame(self.root, bg=CARD_BG)
        detail.pack(fill="x", padx=20, pady=(5, 10))
        tk.Label(detail, text="个人信息", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei",12,"bold")).pack(anchor="w", padx=15, pady=(10,5))
        tk.Frame(detail, bg=DIVIDER_GRAY, height=1).pack(fill="x", padx=15)
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
            row.pack(fill="x", padx=15, pady=6)
            tk.Label(row, text=label, bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=CARD_BG, fg=TEXT_BLACK, font=FONT_NORMAL, anchor="w").pack(side="left", fill="x", expand=True)

    def _build_func_area(self):
        func_frame = tk.Frame(self.root, bg=CARD_BG)
        func_frame.pack(fill="x", padx=20, pady=(0,10))
        tk.Label(func_frame, text="快捷功能", bg=CARD_BG, fg=TEXT_BLACK, font=("Microsoft YaHei",12,"bold")).pack(anchor="w", padx=15, pady=(10,5))
        tk.Frame(func_frame, bg=DIVIDER_GRAY, height=1).pack(fill="x", padx=15)
        func_items = [
            ("👥  我的好友", "好友列表演示页面"),
            ("💬  我的消息", "消息列表演示页面"),
            ("📝  我的动态", "动态发布页面"),
            ("⚙️  系统设置", "账号与隐私设置"),
        ]
        for text, tip in func_items:
            lab = tk.Label(func_frame, text=text, bg=CARD_BG, fg=TEXT_BLACK, font=FONT_NORMAL, cursor="hand2", anchor="w")
            lab.pack(fill="x", padx=15, pady=8)
            lab.bind("<Button-1>", lambda e, t=tip: messagebox.showinfo("功能提示", t))

    def _build_logout_btn(self):
        tk.Button(
            self.root, text="退出登录", command=self._logout,
            bg=LOGOUT_BG, fg="white", activebackground=LOGOUT_ACTIVE, activeforeground="white",
            font=FONT_LOGOUT, relief="flat", cursor="hand2", bd=0
        ).pack(fill="x", padx=40, ipady=6, pady=(5,15))

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
        tk.Label(header, text="QQ", fg="white", bg=HEADER_COLOR, font=("Microsoft YaHei",22,"bold")).place(x=20, y=20)
        tk.Label(header, text="每一天，乐在沟通", fg="#E8F7FF", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=22, y=60)

    def _build_avatar(self):
        avatar_frame = tk.Frame(self.root, bg=BG_COLOR, height=90)
        avatar_frame.pack(fill="x")
        avatar_frame.pack_propagate(False)
        tk.Label(avatar_frame, text="🐧", bg=BG_COLOR, font=FONT_EMOJI).pack(pady=15)

    def _build_input_area(self):
        input_frame = tk.Frame(self.root, bg=BG_COLOR)
        input_frame.pack(fill="x", padx=40, pady=(5,10))
        tk.Label(input_frame, text="账号", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        acc_entry = tk.Entry(
            input_frame, textvariable=self.account_var, font=FONT_NORMAL,
            relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER
        )
        acc_entry.pack(fill="x", ipady=6, pady=(2,12))
        tk.Label(input_frame, text="密码", bg=BG_COLOR, fg=TEXT_GRAY, font=FONT_SMALL).pack(anchor="w")
        pwd_entry = tk.Entry(
            input_frame, textvariable=self.password_var, show="●", font=FONT_NORMAL,
            relief="flat", bd=0, highlightthickness=1, highlightcolor=INPUT_HIGHLIGHT, highlightbackground=INPUT_BORDER
        )
        pwd_entry.pack(fill="x", ipady=6, pady=(2,0))
        pwd_entry.bind("<Return>", lambda e: self._login_action())

    def _build_option_area(self):
        opt_frame = tk.Frame(self.root, bg=BG_COLOR)
        opt_frame.pack(fill="x", padx=40, pady=(5,15))
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
        except Exception as err:
            messagebox.showerror("登录异常", f"程序出错：{str(err)}")

def run_login_window():
    root = tk.Tk()
    QQLoginWindow(root)

    root.mainloop()

if __name__ == "__main__":
    run_login_window()