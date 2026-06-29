# -*- coding: utf-8 -*-
"""
主页窗口模块
登录成功后显示用户个人信息的主界面
"""

import tkinter as tk
from tkinter import messagebox


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