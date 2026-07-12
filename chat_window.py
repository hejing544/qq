# -*- coding: utf-8 -*-
"""主窗口 / 聊天窗口 UI 模块"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
import random
from datetime import datetime

from config import (
    MAIN_W, MAIN_H,
    HEADER_COLOR, BG_COLOR, BTN_COLOR, BTN_ACTIVE, CARD_BG,
    LOGOUT_BG, LOGOUT_ACTIVE, INPUT_HIGHLIGHT, INPUT_BORDER,
    TEXT_GRAY, TEXT_LIGHT_GRAY, TEXT_BLACK, ONLINE_GREEN,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL, FONT_BTN, FONT_EMOJI,
)
from chat_db import load_chat_data, save_chat_data
from user_db import USER_DB, _save_user_db
from moments_db import (
    load_moments_data, add_moment, delete_moment, toggle_like_moment,
)
from checkin_db import (
    get_checkin_status, do_checkin, get_month_records,
)
from calendar import monthrange


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
            tk.Button(self.side_frame, text="每日打卡", width=12, height=2,
                       command=self.show_checkin_page).pack(pady=8)
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
        tk.Label(header, text="QQ主页", fg="white", bg=HEADER_COLOR,
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"当前登录账号：{self.account}",
                 fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR,
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        # 头像卡片
        card = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        card.pack(fill="x", padx=20, pady=15)
        avatar_text = self.user.get("avatar", "🐧")
        tk.Label(card, text=avatar_text, font=FONT_EMOJI, bg=CARD_BG).pack(side="left")
        info_frame = tk.Frame(card, bg=CARD_BG)
        info_frame.pack(side="left", padx=15)
        tk.Label(info_frame, text=self.user["nickname"], bg=CARD_BG,
                 fg=TEXT_BLACK, font=("Microsoft YaHei", 16, "bold")).pack(anchor="w")
        tk.Label(info_frame, text=f"签名：{self.user['signature']}",
                 bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w", pady=5)
        tk.Label(info_frame, text="● 在线", bg=CARD_BG, fg=ONLINE_GREEN, font=FONT_SMALL).pack(anchor="w")

        # 个人信息面板
        detail = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        detail.pack(fill="x", padx=20)
        tk.Label(detail, text="个人信息", bg=CARD_BG, fg=TEXT_BLACK,
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
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
            tk.Label(row, text=label, bg=CARD_BG, fg=TEXT_GRAY,
                     font=FONT_NORMAL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=CARD_BG, fg=TEXT_BLACK,
                     font=FONT_NORMAL, anchor="w").pack(side="left")

        # 快捷功能区
        func_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        func_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(func_frame, text="快捷功能", bg=CARD_BG, fg=TEXT_BLACK,
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
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
        self.msg_display = scrolledtext.ScrolledText(
            chat_area, bg=BG_COLOR, fg=TEXT_BLACK,
            font=FONT_NORMAL, wrap="word", state="disabled")
        self.msg_display.pack(fill="both", expand=True, padx=10, pady=5)

        # 输入栏
        input_frame = tk.Frame(chat_area, bg="white")
        input_frame.pack(fill="x", padx=10, pady=10)
        self.msg_input = tk.Entry(input_frame, font=FONT_NORMAL, highlightthickness=1,
                                  highlightcolor=HEADER_COLOR, highlightbackground=INPUT_BORDER)
        self.msg_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.msg_input.bind("<Return>", lambda e: self.send_chat_msg())
        tk.Button(input_frame, text="发送", bg=BTN_COLOR, fg="white",
                  command=self.send_chat_msg).pack(side="right", padx=5)

    def load_target_chat(self, event):
        """选中好友加载聊天记录"""
        sel = self.chat_listbox.curselection()
        if not sel:
            return
        target_name = self.chat_listbox.get(sel[0])
        self.current_chat_target = target_name
        self.chat_title.config(text=f"和【{target_name}】聊天")

        if target_name not in self.chat_history:
            self.chat_history[target_name] = []

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
        my_msg = {"sender": self.user["nickname"], "content": text, "time": now_time}
        self.chat_history[target].append(my_msg)

        self.msg_display.config(state="normal")
        self.msg_display.insert(tk.END, f"[{now_time}] 我：{text}\n")
        self.msg_display.config(state="disabled")
        self.msg_input.delete(0, tk.END)
        save_chat_data(self.chat_history)

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
        pop.geometry("400x480")
        pop.transient(self.root)
        pop.resizable(False, False)
        pop.grab_set()

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
            tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g,
                           font=FONT_NORMAL).pack(side="left", padx=5)

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

                # 更新内存中的用户信息
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

                # 同步到全局 USER_DB 并保存
                if self.account in USER_DB:
                    USER_DB[self.account]["nickname"] = self.user["nickname"]
                    USER_DB[self.account]["gender"] = self.user["gender"]
                    USER_DB[self.account]["age"] = self.user["age"]
                    USER_DB[self.account]["city"] = self.user["city"]
                    USER_DB[self.account]["signature"] = self.user["signature"]
                    USER_DB[self.account]["avatar"] = self.user["avatar"]

                _save_user_db()

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

        canvas.create_window((0, 0), window=self.moments_scroll_frame, anchor="nw", width=430)
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

    def _do_publish_moment(self):
        """发布动态"""
        content = self.moment_input.get().strip()
        if not content:
            messagebox.showwarning("提示", "请输入动态内容！")
            return
        try:
            add_moment(
                account=self.account,
                nickname=self.user["nickname"],
                avatar=self.user.get("avatar", "🐧"),
                content=content,
            )
            self.moment_input.delete(0, tk.END)
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
                                 font=FONT_NORMAL, anchor="w", justify="left", wraplength=380)
        content_label.pack(fill="x", pady=(8, 5))

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

    # ==================== 每日打卡页面 ====================

    def show_checkin_page(self):
        """呈现每日打卡页面：打卡统计 + 打卡日历 + 签到按钮"""
        self.current_page = "checkin"
        self.clear_main_container()

        # ----- 顶部标题栏 -----
        header = tk.Frame(self.main_container, bg=HEADER_COLOR, height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="每日打卡", fg="white", bg=HEADER_COLOR,
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"{self.user['nickname']}，坚持就是胜利！",
                 fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR,
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        # 获取打卡状态
        status = get_checkin_status(self.account)

        # ----- 打卡统计卡片 -----
        stat_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        stat_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(stat_frame, text="打卡统计", bg=CARD_BG, fg=TEXT_BLACK,
                 font=("Microsoft YaHei", 14, "bold")).pack(anchor="w", pady=(0, 10))

        # 总天数 & 连续天数
        stats_row = tk.Frame(stat_frame, bg=CARD_BG)
        stats_row.pack(fill="x", pady=5)

        # 总打卡天数
        total_frame = tk.Frame(stats_row, bg=CARD_BG)
        total_frame.pack(side="left", expand=True)
        tk.Label(total_frame, text=f"{status['total']}", fg=HEADER_COLOR,
                 bg=CARD_BG, font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(total_frame, text="总打卡天数", bg=CARD_BG, fg=TEXT_GRAY,
                 font=FONT_SMALL).pack()

        # 连续打卡天数
        streak_frame = tk.Frame(stats_row, bg=CARD_BG)
        streak_frame.pack(side="left", expand=True)
        tk.Label(streak_frame, text=f"{status['streak']}", fg="#FF6B35",
                 bg=CARD_BG, font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(streak_frame, text="连续打卡天数", bg=CARD_BG, fg=TEXT_GRAY,
                 font=FONT_SMALL).pack()

        # 打卡按钮
        self.checkin_btn_frame = tk.Frame(self.main_container, bg=BG_COLOR)
        self.checkin_btn_frame.pack(fill="x", padx=20, pady=10)

        if status["checked_in"]:
            # 今日已打卡
            btn = tk.Button(
                self.checkin_btn_frame, text="✅ 今日已打卡",
                bg="#52C41A", fg="white", font=FONT_BTN, relief="flat",
                state="disabled", padx=20, pady=10
            )
            btn.pack()
            tk.Label(self.checkin_btn_frame, text="太棒了，明天继续加油！",
                     bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(pady=5)
        else:
            # 尚未打卡
            tk.Label(self.checkin_btn_frame, text="今天还没有打卡哦，快来打卡吧！",
                     bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL).pack(pady=(0, 10))
            btn = tk.Button(
                self.checkin_btn_frame, text="🎯 立即打卡",
                bg=BTN_COLOR, fg="white", font=FONT_BTN, relief="flat",
                padx=30, pady=12, command=self._do_checkin_action
            )
            btn.pack()

        # ----- 本月打卡日历 -----
        cal_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        cal_frame.pack(fill="x", padx=20, pady=15)

        today = datetime.now()
        year = today.year
        month = today.month
        _, days_in_month = monthrange(year, month)
        month_records = get_month_records(self.account, year, month)

        tk.Label(cal_frame, text=f"{year}年{month}月打卡日历",
                 bg=CARD_BG, fg=TEXT_BLACK,
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))

        # 星期标题
        weekday_frame = tk.Frame(cal_frame, bg=CARD_BG)
        weekday_frame.pack(fill="x")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        for wd in weekdays:
            tk.Label(weekday_frame, text=wd, bg=CARD_BG, fg=TEXT_GRAY,
                     font=FONT_SMALL, width=4, anchor="center").pack(side="left", padx=4)

        # 日历网格
        grid_frame = tk.Frame(cal_frame, bg=CARD_BG)
        grid_frame.pack(fill="x", pady=(5, 0))

        first_weekday = datetime(year, month, 1).weekday()  # 周一=0
        # 转换为周日=0格式
        first_weekday_sun = (first_weekday + 1) % 7

        # 前面填充空白
        col = 0
        for _ in range(first_weekday_sun):
            tk.Label(grid_frame, text="", bg=CARD_BG, width=4).pack(side="left", padx=4)
            col += 1

        for day in range(1, days_in_month + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            is_checked = date_str in month_records

            if is_checked:
                day_label = tk.Label(
                    grid_frame, text=f"{day}✅", bg="#E8F5E9", fg="#2E7D32",
                    font=FONT_SMALL, width=4, relief="solid", bd=1
                )
            else:
                is_today = (day == today.day)
                if is_today:
                    day_label = tk.Label(
                        grid_frame, text=str(day), bg="#E3F2FD", fg=HEADER_COLOR,
                        font=FONT_SMALL, width=4, relief="solid", bd=1
                    )
                else:
                    day_label = tk.Label(
                        grid_frame, text=str(day), bg=CARD_BG, fg=TEXT_BLACK,
                        font=FONT_SMALL, width=4, bd=1
                    )
            day_label.pack(side="left", padx=4, pady=2)
            col += 1
            if col >= 7:
                col = 0

    def _do_checkin_action(self):
        """执行打卡操作"""
        try:
            result = do_checkin(self.account)
            if result["already"]:
                messagebox.showinfo("提示", "今天已经打过卡了哦！")
            else:
                messagebox.showinfo("打卡成功", f"🎉 打卡成功！\n\n"
                                              f"连续打卡：{result['streak']} 天\n"
                                              f"总打卡次数：{result['total']} 次\n\n"
                                              f"继续坚持！")
            self.show_checkin_page()
        except Exception as e:
            messagebox.showerror("打卡失败", f"打卡操作出错：{str(e)}")

    def _logout(self):
        confirm = messagebox.askyesno("确认退出", "确定要退出当前账号返回登录页？")
        if confirm:
            self.root.destroy()
            # 延迟导入避免模块级循环依赖
            from login_window import run_login_window
            run_login_window()
