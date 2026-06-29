# -*- coding: utf-8 -*-
"""
QQ登录页面模拟
使用 Tkinter 实现一个类似 QQ 登录界面的桌面程序
功能：
  - 头像显示区
  - 账号、密码输入框
  - 记住密码、自动登录复选框
  - 登录、注册、找回密码按钮
  - 简单的登录校验逻辑
  - 登录成功后进入主页，显示个人信息
"""

import tkinter as tk
from tkinter import messagebox, font


# ---------- 模拟的用户数据库 ----------
# 每个账号存储：密码、昵称、签名、性别、年龄等信息
USER_DB = {
    "123456": {
        "password": "abc123",
        "nickname": "小明",
        "signature": "每一天，乐在沟通",
        "gender": "男",
        "age": "22",
        "city": "深圳",
    },
    "admin": {
        "password": "admin123",
        "nickname": "管理员",
        "signature": "好好学习，天天向上",
        "gender": "男",
        "age": "25",
        "city": "北京",
    },
    "qquser": {
        "password": "password",
        "nickname": "QQ用户",
        "signature": "这个人很懒，什么都没留下",
        "gender": "女",
        "age": "20",
        "city": "上海",
    },
}


class QQLoginWindow:
    """QQ 登录窗口主类"""

    def __init__(self, root):
        self.root = root
        self.root.title("QQ登录")
        # 固定窗口大小并居中
        self.width = 380
        self.height = 540
        self._center_window(self.width, self.height)
        # 禁止拉伸，保持 QQ 登录框的固定比例
        self.root.resizable(False, False)

        # 定义颜色主题（仿 QQ 蓝色风格）
        self.bg_color = "#F5F6FA"          # 主背景
        self.header_color = "#12B7F5"      # 顶部蓝色背景
        self.btn_color = "#12B7F5"         # 登录按钮颜色
        self.btn_active = "#0E9BD6"        # 登录按钮按下颜色

        # 构建 UI
        self._build_header()
        self._build_avatar()
        self._build_input_area()
        self._build_options_area()
        self._build_login_button()
        self._build_footer()

    # ---------- 工具方法 ----------
    def _center_window(self, w, h):
        """将窗口居中显示在屏幕上"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self):
        """顶部蓝色背景区域"""
        header = tk.Frame(self.root, bg=self.header_color, height=140)
        header.pack(fill="x")
        header.pack_propagate(False)

        # 右上角关闭按钮
        close_btn = tk.Label(
            header,
            text="✕",
            fg="white",
            bg=self.header_color,
            font=("Microsoft YaHei", 12, "bold"),
            cursor="hand2",
        )
        close_btn.place(x=350, y=8)
        close_btn.bind("<Button-1>", lambda e: self.root.quit())

        # 标题文字
        title = tk.Label(
            header,
            text="QQ",
            fg="white",
            bg=self.header_color,
            font=("Microsoft YaHei", 22, "bold"),
        )
        title.place(x=20, y=20)

        subtitle = tk.Label(
            header,
            text="每一天，乐在沟通",
            fg="#E8F7FF",
            bg=self.header_color,
            font=("Microsoft YaHei", 10),
        )
        subtitle.place(x=22, y=60)

    def _build_avatar(self):
        """头像显示区域"""
        avatar_frame = tk.Frame(self.root, bg=self.bg_color, height=90)
        avatar_frame.pack(fill="x")
        avatar_frame.pack_propagate(False)

        # 用一个圆形（用椭圆模拟）作为头像占位
        avatar = tk.Label(
            avatar_frame,
            text="🐧",
            bg=self.bg_color,
            font=("Segoe UI Emoji", 40),
        )
        avatar.pack(pady=15)

    def _build_input_area(self):
        """账号、密码输入区域"""
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill="x", padx=40, pady=(5, 10))

        # 账号输入框
        tk.Label(
            input_frame,
            text="账号",
            bg=self.bg_color,
            fg="#666666",
            font=("Microsoft YaHei", 9),
        ).pack(anchor="w")

        self.account_var = tk.StringVar()
        account_entry = tk.Entry(
            input_frame,
            textvariable=self.account_var,
            font=("Microsoft YaHei", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.header_color,
            highlightbackground="#DDDDDD",
        )
        account_entry.pack(fill="x", ipady=6, pady=(2, 12))

        # 密码输入框
        tk.Label(
            input_frame,
            text="密码",
            bg=self.bg_color,
            fg="#666666",
            font=("Microsoft YaHei", 9),
        ).pack(anchor="w")

        self.password_var = tk.StringVar()
        password_entry = tk.Entry(
            input_frame,
            textvariable=self.password_var,
            show="●",
            font=("Microsoft YaHei", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.header_color,
            highlightbackground="#DDDDDD",
        )
        password_entry.pack(fill="x", ipady=6, pady=(2, 0))

        # 绑定回车键登录
        password_entry.bind("<Return>", lambda e: self._on_login())

    def _build_options_area(self):
        """记住密码、自动登录等选项"""
        opt_frame = tk.Frame(self.root, bg=self.bg_color)
        opt_frame.pack(fill="x", padx=40, pady=(5, 15))

        self.remember_var = tk.IntVar(value=1)
        self.auto_login_var = tk.IntVar(value=0)

        tk.Checkbutton(
            opt_frame,
            text="记住密码",
            variable=self.remember_var,
            bg=self.bg_color,
            activebackground=self.bg_color,
            font=("Microsoft YaHei", 9),
            fg="#666666",
            selectcolor=self.bg_color,
            bd=0,
        ).pack(side="left")

        tk.Checkbutton(
            opt_frame,
            text="自动登录",
            variable=self.auto_login_var,
            bg=self.bg_color,
            activebackground=self.bg_color,
            font=("Microsoft YaHei", 9),
            fg="#666666",
            selectcolor=self.bg_color,
            bd=0,
        ).pack(side="right")

    def _build_login_button(self):
        """登录按钮"""
        login_btn = tk.Button(
            self.root,
            text="登 录",
            command=self._on_login,
            bg=self.btn_color,
            fg="white",
            activebackground=self.btn_active,
            activeforeground="white",
            font=("Microsoft YaHei", 12, "bold"),
            relief="flat",
            cursor="hand2",
            bd=0,
        )
        login_btn.pack(fill="x", padx=40, ipady=8)

    def _build_footer(self):
        """底部注册账号、找回密码链接"""
        footer = tk.Frame(self.root, bg=self.bg_color)
        footer.pack(fill="x", padx=40, pady=15)

        reg_label = tk.Label(
            footer,
            text="注册账号",
            fg=self.header_color,
            bg=self.bg_color,
            font=("Microsoft YaHei", 9),
            cursor="hand2",
        )
        reg_label.pack(side="left")
        reg_label.bind("<Button-1>", lambda e: self._open_register())

        forgot_label = tk.Label(
            footer,
            text="找回密码",
            fg=self.header_color,
            bg=self.bg_color,
            font=("Microsoft YaHei", 9),
            cursor="hand2",
        )
        forgot_label.pack(side="right")
        forgot_label.bind("<Button-1>", lambda e: messagebox.showinfo("提示", "跳转到找回密码页面（示例）"))

    # ---------- 业务逻辑 ----------
    def _on_login(self):
        """点击登录按钮的处理逻辑"""
        account = self.account_var.get().strip()
        password = self.password_var.get().strip()

        # 输入校验
        if not account:
            messagebox.showwarning("提示", "请输入账号！")
            return
        if not password:
            messagebox.showwarning("提示", "请输入密码！")
            return

        # 账号密码校验
        if account in USER_DB and USER_DB[account]["password"] == password:
            # 登录成功，关闭登录窗口，打开主页
            user_info = USER_DB[account]
            nickname = user_info["nickname"]
            messagebox.showinfo("登录成功", f"欢迎回来，{nickname}！\n正在进入主面板...")
            self.root.destroy()
            # 创建主页窗口
            main_root = tk.Tk()
            MainWindow(main_root, account, user_info)
            main_root.mainloop()
        else:
            messagebox.showerror("登录失败", "账号或密码错误，请重新输入！")

    def _open_register(self):
        """打开注册窗口"""
        RegisterWindow(self.root)


class RegisterWindow:
    """QQ 注册窗口"""

    def __init__(self, parent):
        # 使用 Toplevel 作为子窗口，与登录窗口共享同一 Tk 根
        self.top = tk.Toplevel(parent)
        self.top.title("注册QQ账号")
        self.width = 360
        self.height = 480
        self._center_window(self.width, self.height)
        self.top.resizable(False, False)
        # 注册窗口置顶并禁用父窗口交互（模态）
        self.top.transient(parent)
        self.top.grab_set()

        # 颜色主题（与登录窗口保持一致）
        self.bg_color = "#F5F6FA"
        self.header_color = "#12B7F5"
        self.btn_color = "#12B7F5"
        self.btn_active = "#0E9BD6"

        # 构建 UI
        self._build_header()
        self._build_form()
        self._build_register_button()

    # ---------- 工具方法 ----------
    def _center_window(self, w, h):
        """将窗口居中显示在屏幕上"""
        screen_w = self.top.winfo_screenwidth()
        screen_h = self.top.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.top.geometry(f"{w}x{h}+{x}+{y}")

    def _build_header(self):
        """顶部蓝色背景区域"""
        header = tk.Frame(self.top, bg=self.header_color, height=100)
        header.pack(fill="x")
        header.pack_propagate(False)

        # 标题
        tk.Label(
            header,
            text="注册QQ账号",
            fg="white",
            bg=self.header_color,
            font=("Microsoft YaHei", 18, "bold"),
        ).pack(pady=30)

    def _build_form(self):
        """注册表单：账号、昵称、密码、确认密码"""
        form = tk.Frame(self.top, bg=self.bg_color)
        form.pack(fill="x", padx=40, pady=(15, 10))

        # 账号
        tk.Label(
            form,
            text="账号",
            bg=self.bg_color,
            fg="#666666",
            font=("Microsoft YaHei", 9),
        ).pack(anchor="w")

        self.reg_account_var = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self.reg_account_var,
            font=("Microsoft YaHei", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.header_color,
            highlightbackground="#DDDDDD",
        ).pack(fill="x", ipady=6, pady=(2, 10))

        # 昵称
        tk.Label(
            form,
            text="昵称",
            bg=self.bg_color,
            fg="#666666",
            font=("Microsoft YaHei", 9),
        ).pack(anchor="w")

        self.reg_nickname_var = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self.reg_nickname_var,
            font=("Microsoft YaHei", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.header_color,
            highlightbackground="#DDDDDD",
        ).pack(fill="x", ipady=6, pady=(2, 10))

        # 密码
        tk.Label(
            form,
            text="密码（6-16位）",
            bg=self.bg_color,
            fg="#666666",
            font=("Microsoft YaHei", 9),
        ).pack(anchor="w")

        self.reg_password_var = tk.StringVar()
        tk.Entry(
            form,
            textvariable=self.reg_password_var,
            show="●",
            font=("Microsoft YaHei", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.header_color,
            highlightbackground="#DDDDDD",
        ).pack(fill="x", ipady=6, pady=(2, 10))

        # 确认密码
        tk.Label(
            form,
            text="确认密码",
            bg=self.bg_color,
            fg="#666666",
            font=("Microsoft YaHei", 9),
        ).pack(anchor="w")

        self.reg_confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(
            form,
            textvariable=self.reg_confirm_var,
            show="●",
            font=("Microsoft YaHei", 11),
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.header_color,
            highlightbackground="#DDDDDD",
        )
        confirm_entry.pack(fill="x", ipady=6, pady=(2, 0))
        # 绑定回车键提交注册
        confirm_entry.bind("<Return>", lambda e: self._on_register())

    def _build_register_button(self):
        """注册按钮"""
        tk.Button(
            self.top,
            text="立即注册",
            command=self._on_register,
            bg=self.btn_color,
            fg="white",
            activebackground=self.btn_active,
            activeforeground="white",
            font=("Microsoft YaHei", 12, "bold"),
            relief="flat",
            cursor="hand2",
            bd=0,
        ).pack(fill="x", padx=40, ipady=8, pady=(5, 0))

    # ---------- 业务逻辑 ----------
    def _on_register(self):
        """点击注册按钮的处理逻辑"""
        account = self.reg_account_var.get().strip()
        nickname = self.reg_nickname_var.get().strip()
        password = self.reg_password_var.get().strip()
        confirm = self.reg_confirm_var.get().strip()

        # 输入校验
        if not account:
            messagebox.showwarning("提示", "请输入账号！", parent=self.top)
            return
        if not nickname:
            messagebox.showwarning("提示", "请输入昵称！", parent=self.top)
            return
        if not password:
            messagebox.showwarning("提示", "请输入密码！", parent=self.top)
            return
        if not confirm:
            messagebox.showwarning("提示", "请再次输入密码！", parent=self.top)
            return

        # 账号格式校验：仅允许字母、数字，长度 3-16
        if not account.isalnum() or not (3 <= len(account) <= 16):
            messagebox.showwarning(
                "提示",
                "账号只能由字母和数字组成，且长度为 3-16 位！",
                parent=self.top,
            )
            return

        # 密码长度校验：6-16 位
        if not (6 <= len(password) <= 16):
            messagebox.showwarning(
                "提示",
                "密码长度必须为 6-16 位！",
                parent=self.top,
            )
            return

        # 两次密码一致性校验
        if password != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致！", parent=self.top)
            return

        # 账号是否已存在
        if account in USER_DB:
            messagebox.showerror("错误", f"账号 {account} 已存在，请更换账号！", parent=self.top)
            return

        # 注册成功，写入用户数据库（包含完整信息）
        USER_DB[account] = {
            "password": password,
            "nickname": nickname,
            "signature": "这个人很懒，什么都没留下",
            "gender": "保密",
            "age": "未知",
            "city": "未知",
        }
        messagebox.showinfo(
            "注册成功",
            f"恭喜！账号 {account} 注册成功！\n昵称：{nickname}\n现在可以使用该账号登录了。",
            parent=self.top,
        )
        self.top.destroy()


class MainWindow:
    """QQ 主页窗口：登录成功后显示用户个人信息"""

    def __init__(self, root, account, user_info):
        self.root = root
        self.account = account
        self.user_info = user_info

        self.root.title("QQ主页")
        self.width = 420
        self.height = 620
        self._center_window(self.width, self.height)
        self.root.resizable(False, False)

        # 颜色主题
        self.bg_color = "#F5F6FA"
        self.header_color = "#12B7F5"
        self.btn_color = "#12B7F5"
        self.btn_active = "#0E9BD6"
        self.card_color = "#FFFFFF"

        # 构建 UI
        self._build_header()
        self._build_profile_card()
        self._build_info_details()
        self._build_function_area()
        self._build_logout_button()

    # ---------- 工具方法 ----------
    def _center_window(self, w, h):
        """将窗口居中显示在屏幕上"""
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    # ---------- UI 构建 ----------
    def _build_header(self):
        """顶部蓝色背景区域，显示标题和账号"""
        header = tk.Frame(self.root, bg=self.header_color, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)

        # 右上角关闭按钮
        close_btn = tk.Label(
            header,
            text="✕",
            fg="white",
            bg=self.header_color,
            font=("Microsoft YaHei", 12, "bold"),
            cursor="hand2",
        )
        close_btn.place(x=390, y=8)
        close_btn.bind("<Button-1>", lambda e: self.root.quit())

        # 标题
        tk.Label(
            header,
            text="QQ主页",
            fg="white",
            bg=self.header_color,
            font=("Microsoft YaHei", 18, "bold"),
        ).place(x=20, y=15)

        # 当前登录账号
        tk.Label(
            header,
            text=f"当前账号：{self.account}",
            fg="#E8F7FF",
            bg=self.header_color,
            font=("Microsoft YaHei", 10),
        ).place(x=20, y=55)

    def _build_profile_card(self):
        """用户资料卡片：头像 + 昵称 + 签名"""
        card = tk.Frame(self.root, bg=self.card_color, height=130)
        card.pack(fill="x", padx=20, pady=(15, 5))
        card.pack_propagate(False)

        # 头像
        avatar = tk.Label(
            card,
            text="🐧",
            bg=self.card_color,
            font=("Segoe UI Emoji", 45),
        )
        avatar.place(x=20, y=25)

        # 昵称
        nickname = self.user_info.get("nickname", "未知用户")
        tk.Label(
            card,
            text=nickname,
            bg=self.card_color,
            fg="#333333",
            font=("Microsoft YaHei", 16, "bold"),
        ).place(x=110, y=30)

        # 签名
        signature = self.user_info.get("signature", "")
        tk.Label(
            card,
            text=f"签名：{signature}",
            bg=self.card_color,
            fg="#999999",
            font=("Microsoft YaHei", 9),
        ).place(x=110, y=70)

        # 在线状态
        tk.Label(
            card,
            text="● 在线",
            bg=self.card_color,
            fg="#52C41A",
            font=("Microsoft YaHei", 9),
        ).place(x=110, y=95)

    def _build_info_details(self):
        """个人信息详情区域"""
        detail_frame = tk.Frame(self.root, bg=self.card_color)
        detail_frame.pack(fill="x", padx=20, pady=(5, 10))

        # 标题
        tk.Label(
            detail_frame,
            text="个人信息",
            bg=self.card_color,
            fg="#333333",
            font=("Microsoft YaHei", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        # 分隔线
        tk.Frame(detail_frame, bg="#EEEEEE", height=1).pack(fill="x", padx=15)

        # 信息条目
        info_items = [
            ("账    号", self.account),
            ("昵    称", self.user_info.get("nickname", "未知")),
            ("性    别", self.user_info.get("gender", "保密")),
            ("年    龄", self.user_info.get("age", "未知")),
            ("城    市", self.user_info.get("city", "未知")),
            ("个 性 签 名", self.user_info.get("signature", "")),
        ]

        for label_text, value_text in info_items:
            row = tk.Frame(detail_frame, bg=self.card_color)
            row.pack(fill="x", padx=15, pady=6)

            tk.Label(
                row,
                text=label_text,
                bg=self.card_color,
                fg="#999999",
                font=("Microsoft YaHei", 10),
                width=10,
                anchor="w",
            ).pack(side="left")

            tk.Label(
                row,
                text=value_text,
                bg=self.card_color,
                fg="#333333",
                font=("Microsoft YaHei", 10),
                anchor="w",
            ).pack(side="left", fill="x", expand=True)

    def _build_function_area(self):
        """功能区：好友、设置等快捷入口"""
        func_frame = tk.Frame(self.root, bg=self.card_color)
        func_frame.pack(fill="x", padx=20, pady=(0, 10))

        tk.Label(
            func_frame,
            text="快捷功能",
            bg=self.card_color,
            fg="#333333",
            font=("Microsoft YaHei", 12, "bold"),
        ).pack(anchor="w", padx=15, pady=(10, 5))

        tk.Frame(func_frame, bg="#EEEEEE", height=1).pack(fill="x", padx=15)

        # 功能按钮列表
        functions = [
            ("👥  我的好友", "好友列表（示例）"),
            ("💬  我的消息", "消息列表（示例）"),
            ("📝  我的动态", "动态列表（示例）"),
            ("⚙️  系统设置", "设置页面（示例）"),
        ]

        for icon_text, tip in functions:
            btn = tk.Label(
                func_frame,
                text=icon_text,
                bg=self.card_color,
                fg="#333333",
                font=("Microsoft YaHei", 11),
                cursor="hand2",
                anchor="w",
            )
            btn.pack(fill="x", padx=15, pady=8)
            btn.bind("<Button-1>", lambda e, t=tip: messagebox.showinfo("提示", t))

    def _build_logout_button(self):
        """底部退出登录按钮"""
        logout_btn = tk.Button(
            self.root,
            text="退出登录",
            command=self._on_logout,
            bg="#FF4D4F",
            fg="white",
            activebackground="#D9363E",
            activeforeground="white",
            font=("Microsoft YaHei", 11, "bold"),
            relief="flat",
            cursor="hand2",
            bd=0,
        )
        logout_btn.pack(fill="x", padx=40, ipady=6, pady=(5, 15))

    # ---------- 业务逻辑 ----------
    def _on_logout(self):
        """退出登录，返回登录窗口"""
        result = messagebox.askyesno("确认", "确定要退出登录吗？")
        if result:
            self.root.destroy()
            # 重新打开登录窗口
            login_root = tk.Tk()
            QQLoginWindow(login_root)
            login_root.mainloop()


def main():
    """程序入口"""
    root = tk.Tk()
    app = QQLoginWindow(root)
    root.mainloop()


if __name__ == "__main__":
    main()