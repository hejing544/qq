# -*- coding: utf-8 -*-
"""主窗口 / 聊天窗口 UI 模块"""
import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
from datetime import datetime

from config import (
    MAIN_W, MAIN_H,
    HEADER_COLOR, BG_COLOR, BTN_COLOR, BTN_ACTIVE, CARD_BG,
    LOGOUT_BG, LOGOUT_ACTIVE, INPUT_HIGHLIGHT, INPUT_BORDER,
    TEXT_GRAY, TEXT_LIGHT_GRAY, TEXT_BLACK, ONLINE_GREEN, DIVIDER_GRAY,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL, FONT_BTN, FONT_EMOJI,
    SIDEBAR_BG, SIDEBAR_BTN_BG, SIDEBAR_TEXT,
    CHAT_TITLE_BG, CHAT_AREA_BG, MSG_DISPLAY_BG,
    LEFT_BOX_BG, LEFT_BOX_TEXT, POPUP_HEADER_BG,
    INPUT_BG, BTN_GREEN, BTN_RED, FRAME_BORDER,
    TEXT_WHITE, TEXT_PRIMARY,
    CAL_CHECKED_BG, CAL_CHECKED_FG, CAL_TODAY_BG, CAL_TODAY_FG,
    BINDING_LABEL_FG,
)
from theme import get_theme_mode, toggle_theme, set_theme, get_theme
from user_db import USER_DB, _save_user_db, save_theme_preference, get_theme_preference
from friends_db import (
    get_friend_list, get_pending_requests, send_friend_request,
    accept_friend_request, reject_friend_request, remove_friend, search_users
)
from moments_db import (
    load_moments_data, add_moment, delete_moment, toggle_like_moment,
)
from config import MOMENTS_PHOTOS_DIR, MOMENTS_VIDEOS_DIR
import subprocess
import os
import sys
from PIL import Image, ImageTk
from group_db import (
    create_group, get_my_groups, search_groups, get_group_info, get_group_members,
    send_join_request, get_pending_join_requests, accept_join_request,
    reject_join_request, remove_group_member, disband_group,
    send_group_message, load_group_conversation, is_group_member,
)
from checkin_db import (
    get_checkin_status, do_checkin, get_month_records,
)
from calendar import monthrange
from heartbeat import Heartbeat


class MainWindow:
    def __init__(self, root, login_account, user_info):
        try:
            self.root = root
            self.account = login_account
            self.user = user_info
            self.root.title(f"QQ - {self.user['nickname']}")
            self.root.geometry(f"{MAIN_W}x{MAIN_H}")
            self.root.resizable(False, False)
            self.root.protocol("WM_DELETE_WINDOW", self._on_close)

            self.current_page = "home"
            self.current_chat_target_account = None
            self.current_chat_target_nickname = None
            self.last_msg_count = 0
            self.polling_id = None

            # 群聊相关状态
            self.current_group_id = None
            self.current_group_name = None
            self.group_last_msg_count = 0
            self.group_polling_id = None

            self.level_stars = self.user.get("level_stars", 0)
            self.level_timer_id = None
            self._start_level_timer()

            # 心跳上报在线状态
            self.heartbeat = Heartbeat(self.account, self.user.get("nickname", self.account))
            self.heartbeat.start()

            self.side_frame = tk.Frame(self.root, bg=SIDEBAR_BG(), width=120)
            self.side_frame.pack(side="left", fill="y")
            self.side_frame.pack_propagate(False)

            # 侧边栏按钮公共样式
            self._add_sidebar_btn("主页", self.show_home_page)
            self._add_sidebar_btn("开始聊天", self.show_chat_page)
            self._add_sidebar_btn("群聊", self.show_group_page)
            self._add_sidebar_btn("朋友圈", self.show_moments_page)
            self._add_sidebar_btn("每日打卡", self.show_checkin_page)

            # 主题切换按钮
            self.theme_btn = tk.Button(
                self.side_frame, text="", width=12, height=2,
                bg=SIDEBAR_BTN_BG(), fg=SIDEBAR_TEXT(), relief="flat",
                command=self._toggle_theme
            )
            self.theme_btn.pack(pady=(20, 5))
            self._update_theme_btn_text()

            tk.Button(self.side_frame, text="退出登录", width=12, height=2,
                      bg=LOGOUT_BG(), fg="white", command=self._logout).pack(pady=10)

            self.main_container = tk.Frame(self.root, bg=BG_COLOR())
            self.main_container.pack(side="right", fill="both", expand=True)

            self.show_home_page()

        except Exception as e:
            messagebox.showerror("页面异常", f"主页初始化失败：{str(e)}")

    def _add_sidebar_btn(self, text, command):
        tk.Button(
            self.side_frame, text=text, width=12, height=2,
            bg=SIDEBAR_BTN_BG(), fg=SIDEBAR_TEXT(), relief="flat",
            command=command
        ).pack(pady=3)

    def _update_theme_btn_text(self):
        mode = get_theme_mode()
        self.theme_btn.config(text="🌙 夜间" if mode == "day" else "☀️ 日间")

    def _toggle_theme(self):
        new_mode = toggle_theme()
        save_theme_preference(new_mode)
        self._rebuild_all()

    def _rebuild_all(self):
        """切换主题时重建整个界面"""
        self._update_theme_btn_text()
        # 重新设置侧边栏颜色
        self.side_frame.config(bg=SIDEBAR_BG())
        for w in self.side_frame.winfo_children():
            if isinstance(w, tk.Button):
                if w.cget("text") in ("退出登录",):
                    w.config(bg=LOGOUT_BG())
                else:
                    w.config(bg=SIDEBAR_BTN_BG(), fg=SIDEBAR_TEXT())
        self.main_container.config(bg=BG_COLOR())

        # 刷新当前页面
        page = self.current_page
        self.current_page = ""
        if page == "home":
            self.show_home_page()
        elif page == "chat":
            self.show_chat_page()
        elif page == "group":
            self.show_group_page()
        elif page == "moments":
            self.show_moments_page()
        elif page == "checkin":
            self.show_checkin_page()

    def clear_main_container(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()
        if self.polling_id:
            self.root.after_cancel(self.polling_id)
            self.polling_id = None
        if self.group_polling_id:
            self.root.after_cancel(self.group_polling_id)
            self.group_polling_id = None

    def show_home_page(self):
        self.current_page = "home"
        self.clear_main_container()

        header = tk.Frame(self.main_container, bg=HEADER_COLOR(), height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="QQ主页", fg="white", bg=HEADER_COLOR(),
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"当前登录账号：{self.account}",
                 fg="#E8F4FD", bg=HEADER_COLOR(), font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR(),
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        card = tk.Frame(self.main_container, bg=CARD_BG(), padx=15, pady=15)
        card.pack(fill="x", padx=20, pady=15)
        avatar_text = self.user.get("avatar", "🐧")
        tk.Label(card, text=avatar_text, font=FONT_EMOJI, bg=CARD_BG()).pack(side="left")
        info_frame = tk.Frame(card, bg=CARD_BG())
        info_frame.pack(side="left", padx=15)
        top_info_row = tk.Frame(info_frame, bg=CARD_BG())
        top_info_row.pack(anchor="w", fill="x")
        tk.Label(top_info_row, text=self.user["nickname"], bg=CARD_BG(),
                 fg=TEXT_BLACK(), font=("Microsoft YaHei", 16, "bold")).pack(side="left")
        mood_val = self.user.get("mood", "😊开心")
        self.mood_label = tk.Label(top_info_row, text=mood_val, bg=CARD_BG(),
                                    font=("Segoe UI Emoji", 14), cursor="hand2")
        self.mood_label.pack(side="left", padx=(8, 0))
        self.mood_label.bind("<Button-1>", lambda e: self._change_mood_popup())
        tk.Label(info_frame, text=f"签名：{self.user['signature']}",
                 bg=CARD_BG(), fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(anchor="w", pady=5)
        tk.Label(info_frame, text="● 在线", bg=CARD_BG(), fg=ONLINE_GREEN(), font=FONT_SMALL).pack(anchor="w")

        detail = tk.Frame(self.main_container, bg=CARD_BG(), padx=15, pady=15)
        detail.pack(fill="x", padx=20)
        tk.Label(detail, text="个人信息", bg=CARD_BG(), fg=TEXT_BLACK(),
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        display_text, total_stars = self.get_level_stars_display()
        info_list = [
            ("账    号", self.account),
            ("昵    称", self.user["nickname"]),
            ("性    别", self.user["gender"]),
            ("年    龄", self.user["age"]),
            ("城    市", self.user["city"]),
            ("个性签名", self.user["signature"]),
            ("QQ等级", display_text),
        ]
        for label, val in info_list:
            row = tk.Frame(detail, bg=CARD_BG())
            row.pack(fill="x", pady=4)
            tk.Label(row, text=label, bg=CARD_BG(), fg=TEXT_GRAY(),
                     font=FONT_NORMAL, width=10, anchor="w").pack(side="left")
            tk.Label(row, text=val, bg=CARD_BG(), fg=TEXT_BLACK(),
                     font=FONT_NORMAL, anchor="w").pack(side="left")

        func_frame = tk.Frame(self.main_container, bg=CARD_BG(), padx=15, pady=15)
        func_frame.pack(fill="x", padx=20, pady=15)
        tk.Label(func_frame, text="快捷功能", bg=CARD_BG(), fg=TEXT_BLACK(),
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))
        func_items = [
            ("👥  我的好友", lambda: messagebox.showinfo("提示", "好友功能开发中")),
            ("💬  我的消息", lambda: self.show_chat_page()),
            ("📝  我的动态", lambda: self.show_moments_page()),
            ("⚙️  系统设置", lambda: messagebox.showinfo("提示", "设置功能开发中")),
            ("✏️  修改个人资料", self.edit_profile_pop)
        ]
        for text, cmd in func_items:
            tk.Button(func_frame, text=text, bg=CARD_BG(), relief="flat", anchor="w",
                      font=FONT_NORMAL, command=cmd).pack(fill="x", pady=3)

    # ==================== 心情状态切换 ====================
    def _change_mood_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("设置心情状态")
        pop.geometry("300x200")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)
        tk.Label(pop, text="选择你的心情状态：", font=FONT_NORMAL).pack(pady=(20, 10))
        moods = [("😊开心", "😊开心"), ("😢伤心", "😢伤心"), ("😐平静", "😐平静")]
        def set_mood(mood_val):
            self.user["mood"] = mood_val
            self.mood_label.config(text=mood_val)
            if self.account in USER_DB:
                USER_DB[self.account]["mood"] = mood_val
                _save_user_db()
            pop.destroy()
        for display, value in moods:
            tk.Button(pop, text=display, font=("Segoe UI Emoji", 16),
                      bg=CARD_BG(), relief="flat", anchor="w", padx=20,
                      command=lambda v=value: set_mood(v)).pack(fill="x", padx=30, pady=3)

    # ==================== QQ等级系统 ====================
    def _start_level_timer(self):
        self._add_star()
        self.level_timer_id = self.root.after(60000, self._start_level_timer)

    def _add_star(self):
        self.level_stars += 1
        self.user["level_stars"] = self.level_stars
        from user_db import save_level_stars
        save_level_stars(self.account, self.level_stars)

    def _stop_level_timer(self):
        if self.level_timer_id:
            self.root.after_cancel(self.level_timer_id)
            self.level_timer_id = None
        from user_db import save_level_stars
        save_level_stars(self.account, self.level_stars)

    def get_level_stars_display(self):
        stars = self.level_stars
        parts = []
        if stars // 64:
            parts.append(f"☀️×{stars // 64}")
        if (stars % 64) // 16:
            parts.append(f"🌙×{(stars % 64) // 16}")
        star_count = stars % 16
        parts.append(f"⭐×{star_count if parts else stars}")
        return "  ".join(parts), stars

    # ==================== 聊天页面（含好友系统） ====================

    def show_chat_page(self):
        self.current_page = "chat"
        self.clear_main_container()

        left_box = tk.Frame(self.main_container, bg=LEFT_BOX_BG(), width=140)
        left_box.pack(side="left", fill="y")
        tk.Label(left_box, text="我的好友", bg=LEFT_BOX_BG(), font=FONT_NORMAL,
                 fg=LEFT_BOX_TEXT()).pack(pady=5)

        btn_frame = tk.Frame(left_box, bg=LEFT_BOX_BG())
        btn_frame.pack(fill="x", padx=5, pady=2)
        tk.Button(btn_frame, text="➕ 添加好友", bg=CARD_BG(), relief="flat",
                  font=FONT_SMALL, fg=TEXT_BLACK(),
                  command=self._show_add_friend_popup).pack(fill="x")
        tk.Button(btn_frame, text="📩 好友请求", bg=CARD_BG(), relief="flat",
                  font=FONT_SMALL, fg=TEXT_BLACK(),
                  command=self._show_pending_requests).pack(fill="x", pady=(2,0))

        self.chat_listbox = tk.Listbox(left_box, font=FONT_NORMAL,
                                       bg=CARD_BG(), fg=TEXT_BLACK(),
                                       selectbackground=HEADER_COLOR())
        self.chat_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.friend_accounts = []
        self._refresh_friend_list()

        self.chat_listbox.bind("<<ListboxSelect>>", self.load_target_chat)

        chat_area = tk.Frame(self.main_container, bg=CHAT_AREA_BG())
        chat_area.pack(side="right", fill="both", expand=True, padx=5)
        self.chat_title = tk.Label(chat_area, text="请选择好友开始聊天",
                                   bg=CHAT_TITLE_BG(), font=FONT_TITLE,
                                   fg=TEXT_BLACK())
        self.chat_title.pack(fill="x", pady=10)

        self.msg_display = scrolledtext.ScrolledText(
            chat_area, bg=MSG_DISPLAY_BG(), fg=TEXT_BLACK(),
            font=FONT_NORMAL, wrap="word", state="disabled",
            insertbackground=TEXT_BLACK())
        self.msg_display.pack(fill="both", expand=True, padx=10, pady=5)

        input_frame = tk.Frame(chat_area, bg=CHAT_AREA_BG())
        input_frame.pack(fill="x", padx=10, pady=10)
        self.msg_input = tk.Entry(input_frame, font=FONT_NORMAL, highlightthickness=1,
                                  highlightcolor=HEADER_COLOR(), highlightbackground=FRAME_BORDER(),
                                  bg=INPUT_BG(), fg=TEXT_BLACK())
        self.msg_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.msg_input.bind("<Return>", lambda e: self.send_chat_msg())
        tk.Button(input_frame, text="发送", bg=BTN_COLOR(), fg="white",
                  font=FONT_NORMAL, relief="flat",
                  command=self.send_chat_msg).pack(side="right", padx=5)

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
        pop.title("添加好友")
        pop.geometry("400x420")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)

        tk.Label(pop, text="🔍 搜索用户", font=FONT_TITLE,
                 bg=POPUP_HEADER_BG(), fg="white").pack(fill="x", ipady=10)

        search_frame = tk.Frame(pop, bg=CARD_BG())
        search_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(search_frame, text="输入账号或昵称：", font=FONT_NORMAL,
                 bg=CARD_BG(), fg=TEXT_BLACK()).pack(anchor="w")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=FONT_NORMAL,
                                highlightthickness=1, highlightcolor=HEADER_COLOR(),
                                highlightbackground=FRAME_BORDER(),
                                bg=INPUT_BG(), fg=TEXT_BLACK())
        search_entry.pack(fill="x", ipady=4, pady=5)
        search_entry.focus()

        result_frame = tk.Frame(pop, bg=BG_COLOR())
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        result_canvas = tk.Canvas(result_frame, bg=BG_COLOR(), highlightthickness=0, height=120)
        result_scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=result_canvas.yview)
        result_inner = tk.Frame(result_canvas, bg=BG_COLOR())
        result_inner.bind("<Configure>", lambda e: result_canvas.configure(
            scrollregion=result_canvas.bbox("all")))
        result_canvas.create_window((0, 0), window=result_inner, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)
        result_canvas.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")

        def do_search():
            keyword = search_var.get().strip()
            if not keyword:
                return
            for w in result_inner.winfo_children():
                w.destroy()

            results = search_users(keyword)
            friends = get_friend_list(self.account)
            friend_accounts = [f["account"] for f in friends]

            if not results:
                tk.Label(result_inner, text="未找到匹配的用户", bg=BG_COLOR(),
                         fg=TEXT_LIGHT_GRAY(), font=FONT_NORMAL).pack(pady=20)
                return

            for user in results:
                if user["account"] == self.account or user["account"] in friend_accounts:
                    continue
                row = tk.Frame(result_inner, bg=CARD_BG(), padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{user['account']} - {user['nickname']}",
                         bg=CARD_BG(), font=FONT_NORMAL, fg=TEXT_BLACK()).pack(side="left")
                tk.Button(row, text="添加好友", bg=BTN_COLOR(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=8,
                          command=lambda a=user["account"], n=user["nickname"], r=row:
                            _do_add(a, n, r)).pack(side="right")

        def _do_add(target_account, target_nickname, row_widget):
            ok = send_friend_request(self.account, self.user["nickname"], target_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已发送请求", bg=CARD_BG(),
                         fg=ONLINE_GREEN(), font=FONT_SMALL).pack(side="left")
            else:
                messagebox.showinfo("提示", "请求发送失败，可能已是好友或已发送过请求", parent=pop)

        search_entry.bind("<Return>", lambda e: do_search())
        tk.Button(search_frame, text="搜索", bg=BTN_COLOR(), fg="white",
                  font=FONT_BTN, command=do_search).pack(fill="x", ipady=4)

        tk.Frame(pop, bg=DIVIDER_GRAY(), height=1).pack(fill="x", padx=20)
        tk.Label(pop, text="📩 收到的好友请求", font=("Microsoft YaHei", 11, "bold"),
                 bg=BG_COLOR(), fg=TEXT_BLACK()).pack(anchor="w", padx=20, pady=(10, 0))

        pending_frame = tk.Frame(pop, bg=BG_COLOR())
        pending_frame.pack(fill="x", padx=20, pady=5)

        requests = get_pending_requests(self.account)
        if not requests:
            tk.Label(pending_frame, text="暂无好友请求", bg=BG_COLOR(),
                     fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(anchor="w")
        else:
            for req in requests:
                req_row = tk.Frame(pending_frame, bg=CARD_BG(), padx=10, pady=5)
                req_row.pack(fill="x", pady=3)
                tk.Label(req_row, text=f"{req['from_account']} - {req['from_nickname']}",
                         bg=CARD_BG(), font=FONT_NORMAL, fg=TEXT_BLACK()).pack(side="left")
                tk.Button(req_row, text="接受", bg=BTN_GREEN(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], n=req["from_nickname"], r=req_row:
                            _do_accept(a, n, r)).pack(side="right", padx=2)
                tk.Button(req_row, text="拒绝", bg=BTN_RED(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], r=req_row:
                            _do_reject(a, r)).pack(side="right", padx=2)

        def _do_accept(from_account, from_nickname, row_widget):
            ok = accept_friend_request(self.account, from_account, from_nickname,
                                       self.user["nickname"])
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已接受", bg=CARD_BG(),
                         fg=ONLINE_GREEN(), font=FONT_SMALL).pack(side="left")
                self._refresh_friend_list()

        def _do_reject(from_account, row_widget):
            ok = reject_friend_request(self.account, from_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG(),
                         fg=TEXT_GRAY(), font=FONT_SMALL).pack(side="left")

    def _show_pending_requests(self):
        pop = tk.Toplevel(self.root)
        pop.title("好友请求")
        pop.geometry("380x300")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)

        tk.Label(pop, text="📩 好友请求管理", font=FONT_TITLE,
                 bg=POPUP_HEADER_BG(), fg="white").pack(fill="x", ipady=10)

        tk.Label(pop, text="收到的请求", font=("Microsoft YaHei", 11, "bold"),
                 bg=BG_COLOR(), fg=TEXT_BLACK()).pack(anchor="w", padx=20, pady=(10, 0))

        in_frame = tk.Frame(pop, bg=BG_COLOR())
        in_frame.pack(fill="x", padx=20, pady=5)

        requests = get_pending_requests(self.account)
        if not requests:
            tk.Label(in_frame, text="暂无收到的好友请求", bg=BG_COLOR(),
                     fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(anchor="w", pady=10)
        else:
            for req in requests:
                row = tk.Frame(in_frame, bg=CARD_BG(), padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{req['from_account']} - {req['from_nickname']}",
                         bg=CARD_BG(), font=FONT_NORMAL, fg=TEXT_BLACK()).pack(side="left")
                tk.Button(row, text="接受", bg=BTN_GREEN(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], n=req["from_nickname"], r=row:
                            _acc(a, n, r)).pack(side="right", padx=2)
                tk.Button(row, text="拒绝", bg=BTN_RED(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], r=row:
                            _rej(a, r)).pack(side="right", padx=2)

        def _acc(from_account, from_nickname, row_widget):
            ok = accept_friend_request(self.account, from_account, from_nickname,
                                       self.user["nickname"])
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已接受", bg=CARD_BG(),
                         fg=ONLINE_GREEN(), font=FONT_SMALL).pack(side="left")
                self._refresh_friend_list()

        def _rej(from_account, row_widget):
            ok = reject_friend_request(self.account, from_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG(),
                         fg=TEXT_GRAY(), font=FONT_SMALL).pack(side="left")

        tk.Frame(pop, bg=DIVIDER_GRAY(), height=1).pack(fill="x", padx=20, pady=10)
        tk.Label(pop, text="💡 在聊天界面点击「添加好友」搜索并添加好友",
                 bg=BG_COLOR(), fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(pady=5)

    def load_target_chat(self, event):
        sel = self.chat_listbox.curselection()
        if not sel:
            return
        if not self.friend_accounts:
            return
        idx = sel[0]
        if idx >= len(self.friend_accounts):
            return
        target_account = self.friend_accounts[idx]
        target_nickname = USER_DB.get(target_account, {}).get("nickname", target_account)

        self.current_chat_target_account = target_account
        self.current_chat_target_nickname = target_nickname
        self.chat_title.config(text=f"和【{target_nickname}】聊天")

        self._refresh_chat_display()
        self._start_polling()

    def _refresh_chat_display(self):
        if not self.current_chat_target_account:
            return
        messages = load_conversation(self.account, self.current_chat_target_account)
        self.last_msg_count = len(messages)

        self.msg_display.config(state="normal")
        self.msg_display.delete(1.0, tk.END)

        self.msg_display.insert(tk.END, f"--- 与 {self.current_chat_target_nickname} 的聊天 ---\n")
        self.msg_display.insert(tk.END, "\n")

        for msg in messages:
            sender = msg.get("sender_nickname", msg.get("sender_account", "未知"))
            send_time = msg.get("time", "")
            content = msg.get("content", "")
            self.msg_display.insert(tk.END, f"[{send_time}] {sender}：{content}\n")

        self.msg_display.config(state="disabled")
        self.msg_display.see(tk.END)

    def _start_polling(self):
        if self.polling_id:
            self.root.after_cancel(self.polling_id)
            self.polling_id = None

        def poll():
            if self.current_page != "chat" or not self.current_chat_target_account:
                return
            messages = load_conversation(self.account, self.current_chat_target_account)
            if len(messages) != self.last_msg_count:
                self._refresh_chat_display()
            self.polling_id = self.root.after(2000, poll)

        self.polling_id = self.root.after(2000, poll)

    def send_chat_msg(self):
        if not self.current_chat_target_account:
            messagebox.showwarning("提示", "请先选择好友！")
            return
        text = self.msg_input.get().strip()
        if not text:
            return

        send_message(
            sender_account=self.account,
            sender_nickname=self.user["nickname"],
            target_account=self.current_chat_target_account,
            content=text
        )

        self.msg_input.delete(0, tk.END)
        self._refresh_chat_display()

    # ==================== 群聊功能 ====================

    def show_group_page(self):
        self.current_page = "group"
        self.clear_main_container()

        left_box = tk.Frame(self.main_container, bg=LEFT_BOX_BG(), width=140)
        left_box.pack(side="left", fill="y")
        tk.Label(left_box, text="我的群聊", bg=LEFT_BOX_BG(), font=FONT_NORMAL,
                 fg=LEFT_BOX_TEXT()).pack(pady=5)

        btn_frame = tk.Frame(left_box, bg=LEFT_BOX_BG())
        btn_frame.pack(fill="x", padx=5, pady=2)
        tk.Button(btn_frame, text="✚ 创建群", bg=CARD_BG(), relief="flat",
                  font=FONT_SMALL, fg=TEXT_BLACK(),
                  command=self._show_create_group_popup).pack(fill="x")
        tk.Button(btn_frame, text="🔍 加入群", bg=CARD_BG(), relief="flat",
                  font=FONT_SMALL, fg=TEXT_BLACK(),
                  command=self._show_join_group_popup).pack(fill="x", pady=(2,0))

        self.group_listbox = tk.Listbox(left_box, font=FONT_NORMAL,
                                        bg=CARD_BG(), fg=TEXT_BLACK(),
                                        selectbackground=HEADER_COLOR())
        self.group_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.my_groups_data = []
        self._refresh_group_list()

        self.group_listbox.bind("<<ListboxSelect>>", self.load_target_group)

        chat_area = tk.Frame(self.main_container, bg=CHAT_AREA_BG())
        chat_area.pack(side="right", fill="both", expand=True, padx=5)

        title_frame = tk.Frame(chat_area, bg=CHAT_TITLE_BG())
        title_frame.pack(fill="x")
        self.group_chat_title = tk.Label(title_frame, text="请选择群开始聊天",
                                         bg=CHAT_TITLE_BG(), font=FONT_TITLE,
                                         fg=TEXT_BLACK())
        self.group_chat_title.pack(side="left", pady=10, padx=5)
        self.group_mgmt_btn = tk.Button(
            title_frame, text="⚙ 群管理", bg=CARD_BG(), relief="flat",
            font=FONT_SMALL, fg=TEXT_BLACK(),
            command=self._show_group_management_popup
        )
        self.group_mgmt_btn.pack(side="right", padx=10)
        self.group_mgmt_btn.pack_forget()

        self.group_msg_display = scrolledtext.ScrolledText(
            chat_area, bg=MSG_DISPLAY_BG(), fg=TEXT_BLACK(),
            font=FONT_NORMAL, wrap="word", state="disabled",
            insertbackground=TEXT_BLACK())
        self.group_msg_display.pack(fill="both", expand=True, padx=10, pady=5)

        input_frame = tk.Frame(chat_area, bg=CHAT_AREA_BG())
        input_frame.pack(fill="x", padx=10, pady=10)
        self.group_msg_input = tk.Entry(input_frame, font=FONT_NORMAL, highlightthickness=1,
                                        highlightcolor=HEADER_COLOR(), highlightbackground=FRAME_BORDER(),
                                        bg=INPUT_BG(), fg=TEXT_BLACK())
        self.group_msg_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.group_msg_input.bind("<Return>", lambda e: self.send_group_msg())
        tk.Button(input_frame, text="发送", bg=BTN_COLOR(), fg="white",
                  font=FONT_NORMAL, relief="flat",
                  command=self.send_group_msg).pack(side="right", padx=5)

    def _refresh_group_list(self):
        self.group_listbox.delete(0, tk.END)
        self.my_groups_data = get_my_groups(self.account)
        if not self.my_groups_data:
            self.group_listbox.insert(tk.END, "（暂无群聊）")
            return
        for g in self.my_groups_data:
            display = f"{g['group_name']} ({g['group_id']}) {g['member_count']}人"
            self.group_listbox.insert(tk.END, display)

    def _show_create_group_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("创建群")
        pop.geometry("350x180")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)

        tk.Label(pop, text="✚ 创建新群", font=FONT_TITLE,
                 bg=POPUP_HEADER_BG(), fg="white").pack(fill="x", ipady=10)

        tk.Label(pop, text="群名称：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(15, 5))
        name_var = tk.StringVar()
        entry = tk.Entry(pop, textvariable=name_var, font=FONT_NORMAL,
                         highlightthickness=1, highlightcolor=HEADER_COLOR(),
                         highlightbackground=FRAME_BORDER(),
                         bg=INPUT_BG(), fg=TEXT_BLACK())
        entry.pack(fill="x", padx=30, ipady=4)
        entry.focus()
        entry.bind("<Return>", lambda e: _do_create())

        def _do_create():
            name = name_var.get().strip()
            if not name:
                messagebox.showwarning("提示", "请输入群名称！", parent=pop)
                return
            result = create_group(self.account, self.user["nickname"], name)
            if result:
                messagebox.showinfo("成功", f"群创建成功！\n群号：{result['group_id']}\n群名：{result['group_name']}", parent=pop)
                pop.destroy()
                self._refresh_group_list()
            else:
                messagebox.showerror("失败", "群创建失败，请重试", parent=pop)

        tk.Button(pop, text="创建", bg=BTN_COLOR(), fg="white",
                  font=FONT_BTN, command=_do_create).pack(pady=15)

    def _show_join_group_popup(self):
        pop = tk.Toplevel(self.root)
        pop.title("加入群")
        pop.geometry("400x400")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)

        tk.Label(pop, text="🔍 搜索并加入群", font=FONT_TITLE,
                 bg=POPUP_HEADER_BG(), fg="white").pack(fill="x", ipady=10)

        search_frame = tk.Frame(pop, bg=CARD_BG())
        search_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(search_frame, text="输入群号或群名：", font=FONT_NORMAL,
                 bg=CARD_BG(), fg=TEXT_BLACK()).pack(anchor="w")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=FONT_NORMAL,
                                highlightthickness=1, highlightcolor=HEADER_COLOR(),
                                highlightbackground=FRAME_BORDER(),
                                bg=INPUT_BG(), fg=TEXT_BLACK())
        search_entry.pack(fill="x", ipady=4, pady=5)
        search_entry.focus()

        result_frame = tk.Frame(pop, bg=BG_COLOR())
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        result_canvas = tk.Canvas(result_frame, bg=BG_COLOR(), highlightthickness=0, height=150)
        result_scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=result_canvas.yview)
        result_inner = tk.Frame(result_canvas, bg=BG_COLOR())
        result_inner.bind("<Configure>", lambda e: result_canvas.configure(
            scrollregion=result_canvas.bbox("all")))
        result_canvas.create_window((0, 0), window=result_inner, anchor="nw")
        result_canvas.configure(yscrollcommand=result_scrollbar.set)
        result_canvas.pack(side="left", fill="both", expand=True)
        result_scrollbar.pack(side="right", fill="y")

        def do_search():
            keyword = search_var.get().strip()
            if not keyword:
                return
            for w in result_inner.winfo_children():
                w.destroy()

            results = search_groups(keyword)
            if not results:
                tk.Label(result_inner, text="未找到匹配的群", bg=BG_COLOR(),
                         fg=TEXT_LIGHT_GRAY(), font=FONT_NORMAL).pack(pady=20)
                return

            for g in results:
                row = tk.Frame(result_inner, bg=CARD_BG(), padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{g['group_name']} ({g['group_id']}) {g['member_count']}人",
                         bg=CARD_BG(), font=FONT_NORMAL, fg=TEXT_BLACK()).pack(side="left")
                tk.Button(row, text="申请加入", bg=BTN_COLOR(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=8,
                          command=lambda gid=g["group_id"], gn=g["group_name"], r=row:
                            _do_join(gid, gn, r)).pack(side="right")

        def _do_join(group_id, group_name, row_widget):
            result = send_join_request(self.account, self.user["nickname"], group_id)
            if result == "ok":
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已发送申请，等待群主审核", bg=CARD_BG(),
                         fg=ONLINE_GREEN(), font=FONT_SMALL).pack(side="left")
            elif result == "already_member":
                messagebox.showinfo("提示", "你已经是该群成员了！", parent=pop)
            elif result == "already_requested":
                messagebox.showinfo("提示", "你已经发送过申请了，请等待审核！", parent=pop)
            else:
                messagebox.showerror("错误", "群不存在或其他错误", parent=pop)

        search_entry.bind("<Return>", lambda e: do_search())
        tk.Button(search_frame, text="搜索", bg=BTN_COLOR(), fg="white",
                  font=FONT_BTN, command=do_search).pack(fill="x", ipady=4)

    def _show_group_management_popup(self):
        if not self.current_group_id:
            return
        group_info = get_group_info(self.current_group_id)
        if not group_info:
            return

        members = group_info.get("members", [])
        is_owner = (group_info.get("creator") == self.account)
        is_admin = is_owner
        if not is_owner:
            for m in members:
                if m["account"] == self.account and m.get("role") == "admin":
                    is_admin = True
                    break

        pop = tk.Toplevel(self.root)
        pop.title(f"群管理 - {group_info['group_name']}")
        pop.geometry("400x480")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)

        tk.Label(pop, text=f"📋 {group_info['group_name']} ({self.current_group_id})",
                 font=FONT_TITLE, bg=POPUP_HEADER_BG(), fg="white").pack(fill="x", ipady=10)

        info_frame = tk.Frame(pop, bg=CARD_BG(), padx=15, pady=10)
        info_frame.pack(fill="x", padx=15, pady=10)
        tk.Label(info_frame, text=f"群主：{group_info.get('creator', '')}", bg=CARD_BG(),
                 font=FONT_NORMAL, fg=TEXT_BLACK(), anchor="w").pack(fill="x")
        tk.Label(info_frame, text=f"成员：{len(members)} 人", bg=CARD_BG(),
                 font=FONT_NORMAL, fg=TEXT_BLACK(), anchor="w").pack(fill="x")
        tk.Label(info_frame, text=f"创建时间：{group_info.get('created_time', '')}", bg=CARD_BG(),
                 font=FONT_NORMAL, fg=TEXT_BLACK(), anchor="w").pack(fill="x")

        tk.Label(pop, text="入群申请", font=("Microsoft YaHei", 11, "bold"),
                 bg=BG_COLOR(), fg=TEXT_BLACK()).pack(anchor="w", padx=15, pady=(5, 0))
        pending_frame = tk.Frame(pop, bg=BG_COLOR())
        pending_frame.pack(fill="x", padx=15, pady=5)

        pending_reqs = get_pending_join_requests(self.current_group_id)
        if not pending_reqs:
            tk.Label(pending_frame, text="暂无入群申请", bg=BG_COLOR(),
                     fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(anchor="w", pady=5)
        else:
            for req in pending_reqs:
                row = tk.Frame(pending_frame, bg=CARD_BG(), padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{req['from_account']} - {req['from_nickname']}",
                         bg=CARD_BG(), font=FONT_NORMAL, fg=TEXT_BLACK()).pack(side="left")
                if is_admin:
                    tk.Button(row, text="同意", bg=BTN_GREEN(), fg="white",
                              font=FONT_SMALL, relief="flat", padx=6,
                              command=lambda a=req["from_account"], n=req["from_nickname"], r=row:
                                _acc_join(a, n, r)).pack(side="right", padx=2)
                    tk.Button(row, text="拒绝", bg=BTN_RED(), fg="white",
                              font=FONT_SMALL, relief="flat", padx=6,
                              command=lambda a=req["from_account"], r=row:
                                _rej_join(a, r)).pack(side="right", padx=2)

        def _acc_join(from_account, from_nickname, row_widget):
            ok = accept_join_request(self.current_group_id, from_account, from_nickname, self.account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已同意", bg=CARD_BG(),
                         fg=ONLINE_GREEN(), font=FONT_SMALL).pack(side="left")
                self._refresh_group_list()
            else:
                messagebox.showerror("操作失败", "同意入群失败，请重试", parent=pop)

        def _rej_join(from_account, row_widget):
            ok = reject_join_request(self.current_group_id, from_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG(),
                         fg=TEXT_GRAY(), font=FONT_SMALL).pack(side="left")

        tk.Label(pop, text="成员列表", font=("Microsoft YaHei", 11, "bold"),
                 bg=BG_COLOR(), fg=TEXT_BLACK()).pack(anchor="w", padx=15, pady=(10, 0))
        member_frame = tk.Frame(pop, bg=BG_COLOR())
        member_frame.pack(fill="both", expand=True, padx=15, pady=5)

        member_canvas = tk.Canvas(member_frame, bg=BG_COLOR(), highlightthickness=0, height=120)
        member_scrollbar = tk.Scrollbar(member_frame, orient="vertical", command=member_canvas.yview)
        member_inner = tk.Frame(member_canvas, bg=BG_COLOR())
        member_inner.bind("<Configure>", lambda e: member_canvas.configure(
            scrollregion=member_canvas.bbox("all")))
        member_canvas.create_window((0, 0), window=member_inner, anchor="nw")
        member_canvas.configure(yscrollcommand=member_scrollbar.set)
        member_canvas.pack(side="left", fill="both", expand=True)
        member_scrollbar.pack(side="right", fill="y")

        for m in members:
            role_text = "👑 群主" if m.get("role") == "owner" else ("🛡 管理员" if m.get("role") == "admin" else "成员")
            row = tk.Frame(member_inner, bg=CARD_BG(), padx=10, pady=4)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{m['nickname']} ({m['account']}) [{role_text}]",
                     bg=CARD_BG(), font=FONT_SMALL, fg=TEXT_BLACK()).pack(side="left")
            if is_owner and m["account"] != self.account:
                def _kick(target_account, target_nickname):
                    confirm = messagebox.askyesno("确认踢出",
                                                  f"确定要将 {target_nickname} 踢出群吗？", parent=pop)
                    if confirm:
                        ok = remove_group_member(self.current_group_id, target_account, self.account)
                        if ok:
                            messagebox.showinfo("成功", f"已将 {target_nickname} 踢出群", parent=pop)
                            pop.destroy()
                            self._refresh_group_list()
                        else:
                            messagebox.showerror("失败", "踢出操作失败", parent=pop)

                tk.Button(row, text="踢出", bg=BTN_RED(), fg="white",
                          font=FONT_SMALL, relief="flat", padx=4,
                          command=lambda a=m["account"], n=m["nickname"]: _kick(a, n)).pack(side="right", padx=2)

                def _toggle_admin(target_account, target_nickname, current_role):
                    new_role = "admin" if current_role == "member" else "member"
                    action = "设置管理员" if new_role == "admin" else "取消管理员"
                    confirm = messagebox.askyesno("确认操作",
                                                  f"确定要{action} {target_nickname} 吗？", parent=pop)
                    if confirm:
                        from group_db import assign_admin
                        ok = assign_admin(self.current_group_id, target_account, self.account)
                        if ok:
                            messagebox.showinfo("成功", f"已{action} {target_nickname}", parent=pop)
                            pop.destroy()
                        else:
                            messagebox.showerror("失败", f"{action}失败", parent=pop)

                if m.get("role") in ("member", "admin"):
                    btn_text = "取消管理" if m.get("role") == "admin" else "设为管理"
                    tk.Button(row, text=btn_text, bg=BTN_COLOR(), fg="white",
                              font=FONT_SMALL, relief="flat", padx=4,
                              command=lambda a=m["account"], n=m["nickname"], r=m.get("role"):
                                _toggle_admin(a, n, r)).pack(side="right", padx=2)

        if is_owner:
            op_frame = tk.Frame(pop, bg=BG_COLOR())
            op_frame.pack(fill="x", padx=15, pady=10)
            tk.Button(op_frame, text="🗑 解散群", bg=BTN_RED(), fg="white",
                      font=FONT_BTN, command=self._do_disband_group).pack(side="left", padx=5)
            tk.Button(op_frame, text="🔁 转让群主", bg=HEADER_COLOR(), fg="white",
                      font=FONT_BTN, command=lambda: self._do_transfer_owner(pop)).pack(side="right", padx=5)

    def _do_disband_group(self):
        if not self.current_group_id:
            return
        confirm = messagebox.askyesno("确认解散", "确定要解散当前群吗？\n此操作不可恢复！")
        if confirm:
            ok = disband_group(self.current_group_id, self.account)
            if ok:
                messagebox.showinfo("成功", "群已解散")
                self.current_group_id = None
                self.current_group_name = None
                self._refresh_group_list()
                self.show_group_page()
            else:
                messagebox.showerror("失败", "解散失败，只有群主可以解散群")

    def _do_transfer_owner(self, parent_pop):
        if not self.current_group_id:
            return
        members = get_group_members(self.current_group_id)
        members = [m for m in members if m["account"] != self.account]
        if not members:
            messagebox.showinfo("提示", "群内没有其他成员可以转让", parent=parent_pop)
            return

        trans_pop = tk.Toplevel(self.root)
        trans_pop.title("转让群主")
        trans_pop.geometry("300x300")
        trans_pop.transient(self.root)
        trans_pop.grab_set()
        trans_pop.resizable(False, False)

        tk.Label(trans_pop, text="选择新群主", font=FONT_TITLE,
                 bg=POPUP_HEADER_BG(), fg="white").pack(fill="x", ipady=10)

        listbox = tk.Listbox(trans_pop, font=FONT_NORMAL,
                             bg=CARD_BG(), fg=TEXT_BLACK())
        listbox.pack(fill="both", expand=True, padx=20, pady=15)

        for m in members:
            listbox.insert(tk.END, f"{m['nickname']} ({m['account']})")

        def do_transfer():
            sel = listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请选择新群主", parent=trans_pop)
                return
            idx = sel[0]
            target_account = members[idx]["account"]
            confirm = messagebox.askyesno("确认转让", f"确定将群主转让给 {members[idx]['nickname']} 吗？")
            if confirm:
                from group_db import transfer_owner
                ok = transfer_owner(self.current_group_id, target_account, self.account)
                if ok:
                    messagebox.showinfo("成功", "群主转让成功")
                    trans_pop.destroy()
                    parent_pop.destroy()
                    self._refresh_group_list()
                else:
                    messagebox.showerror("失败", "转让失败，请重试")

        tk.Button(trans_pop, text="确认转让", bg=BTN_COLOR(), fg="white",
                  font=FONT_BTN, command=do_transfer).pack(pady=10)

    def load_target_group(self, event):
        sel = self.group_listbox.curselection()
        if not sel:
            return
        if not self.my_groups_data:
            return
        idx = sel[0]
        if idx >= len(self.my_groups_data):
            return
        group_info = self.my_groups_data[idx]
        self.current_group_id = group_info["group_id"]
        self.current_group_name = group_info["group_name"]
        self.group_chat_title.config(text=f"💬 {group_info['group_name']} ({group_info['group_id']})")

        self.group_mgmt_btn.pack(side="right", padx=10)

        self._refresh_group_chat_display()
        self._start_group_polling()

    def _refresh_group_chat_display(self):
        if not self.current_group_id:
            return
        messages = load_group_conversation(self.current_group_id)
        self.group_last_msg_count = len(messages)

        self.group_msg_display.config(state="normal")
        self.group_msg_display.delete(1.0, tk.END)

        self.group_msg_display.insert(tk.END, f"--- {self.current_group_name} 群聊 ---\n")
        self.group_msg_display.insert(tk.END, "\n")

        for msg in messages:
            sender = msg.get("sender_nickname", msg.get("sender_account", "未知"))
            send_time = msg.get("time", "")
            content = msg.get("content", "")
            self.group_msg_display.insert(tk.END, f"[{send_time}] {sender}：{content}\n")

        self.group_msg_display.config(state="disabled")
        self.group_msg_display.see(tk.END)

    def _start_group_polling(self):
        if self.group_polling_id:
            self.root.after_cancel(self.group_polling_id)
            self.group_polling_id = None

        def poll():
            if self.current_page != "group" or not self.current_group_id:
                return
            messages = load_group_conversation(self.current_group_id)
            if len(messages) != self.group_last_msg_count:
                self._refresh_group_chat_display()
            self.group_polling_id = self.root.after(2000, poll)

        self.group_polling_id = self.root.after(2000, poll)

    def send_group_msg(self):
        if not self.current_group_id:
            messagebox.showwarning("提示", "请先选择一个群！")
            return
        text = self.group_msg_input.get().strip()
        if not text:
            return

        send_group_message(
            sender_account=self.account,
            sender_nickname=self.user["nickname"],
            group_id=self.current_group_id,
            content=text,
        )

        self.group_msg_input.delete(0, tk.END)
        self._refresh_group_chat_display()

    def edit_profile_pop(self):
        pop = tk.Toplevel(self.root)
        pop.title("修改个人资料")
        pop.geometry("400x480")
        pop.transient(self.root)
        pop.resizable(False, False)
        pop.grab_set()

        tk.Label(pop, text="头像：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(15, 0))
        avatar_var = tk.StringVar(value=self.user.get("avatar", "🐧"))
        avatars = ["🐧", "🐶", "🐱", "🐼", "🐨", "🦊", "🐰", "🐯"]
        avatar_frame = tk.Frame(pop, bg=BG_COLOR())
        avatar_frame.pack(pady=3)
        for ava in avatars:
            tk.Radiobutton(avatar_frame, text=ava, variable=avatar_var, value=ava,
                           font=("Segoe UI Emoji", 16), bg=BG_COLOR(),
                           fg=TEXT_BLACK(), selectcolor=BG_COLOR()).pack(side="left")

        tk.Label(pop, text="昵称：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(5, 0))
        nick_var = tk.StringVar(value=self.user["nickname"])
        tk.Entry(pop, textvariable=nick_var, width=30, font=FONT_NORMAL,
                 bg=INPUT_BG(), fg=TEXT_BLACK()).pack(pady=3)

        tk.Label(pop, text="性别：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(5, 0))
        gender_var = tk.StringVar(value=self.user.get("gender", "保密"))
        gender_frame = tk.Frame(pop, bg=BG_COLOR())
        gender_frame.pack(pady=3)
        for g in ["男", "女", "保密"]:
            tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g,
                           font=FONT_NORMAL, bg=BG_COLOR(), fg=TEXT_BLACK(),
                           selectcolor=BG_COLOR()).pack(side="left", padx=5)

        tk.Label(pop, text="年龄：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(5, 0))
        age_var = tk.StringVar(value=self.user.get("age", "未知"))
        tk.Entry(pop, textvariable=age_var, width=30, font=FONT_NORMAL,
                 bg=INPUT_BG(), fg=TEXT_BLACK()).pack(pady=3)

        tk.Label(pop, text="城市：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(5, 0))
        city_var = tk.StringVar(value=self.user.get("city", "未知"))
        tk.Entry(pop, textvariable=city_var, width=30, font=FONT_NORMAL,
                 bg=INPUT_BG(), fg=TEXT_BLACK()).pack(pady=3)

        tk.Label(pop, text="个性签名：", font=FONT_NORMAL, bg=BG_COLOR(),
                 fg=TEXT_BLACK()).pack(anchor="w", padx=30, pady=(5, 0))
        sign_var = tk.StringVar(value=self.user.get("signature", ""))
        tk.Entry(pop, textvariable=sign_var, width=30, font=FONT_NORMAL,
                 bg=INPUT_BG(), fg=TEXT_BLACK()).pack(pady=3)

        def save_info():
            try:
                new_avatar = avatar_var.get()
                new_nick = nick_var.get().strip()
                new_gender = gender_var.get()
                new_age = age_var.get().strip()
                new_city = city_var.get().strip()
                new_sign = sign_var.get().strip()

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

        tk.Button(pop, text="保存修改", bg=BTN_COLOR(), fg="white",
                  font=FONT_BTN, command=save_info).pack(pady=15)

    # ==================== 动态（朋友圈）页面 ====================

    def show_moments_page(self):
        self.current_page = "moments"
        self.clear_main_container()

        header = tk.Frame(self.main_container, bg=HEADER_COLOR(), height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="朋友圈", fg="white", bg=HEADER_COLOR(),
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"{self.user['nickname']} 的动态",
                 fg="#E8F4FD", bg=HEADER_COLOR(), font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR(),
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        post_frame = tk.Frame(self.main_container, bg=CARD_BG(), padx=15, pady=10)
        post_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(post_frame, text="发动态", bg=CARD_BG(), fg=TEXT_BLACK(),
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w")

        input_row = tk.Frame(post_frame, bg=CARD_BG())
        input_row.pack(fill="x", pady=(5, 0))

        self.moment_input = tk.Entry(input_row, font=FONT_NORMAL,
                                     highlightthickness=1,
                                     highlightcolor=HEADER_COLOR(),
                                     highlightbackground=FRAME_BORDER(),
                                     bg=INPUT_BG(), fg=TEXT_BLACK())
        self.moment_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.moment_input.bind("<Return>", lambda e: self._do_publish_moment())

        self.photo_path_var = tk.StringVar()
        photo_btn = tk.Button(
            input_row, text="📷", font=("Segoe UI Emoji", 14),
            bg=CARD_BG(), relief="flat", command=self._select_photo
        )
        photo_btn.pack(side="right", padx=(4, 4))
        self.photo_label = tk.Label(
            input_row, text="", bg=CARD_BG(), fg=TEXT_LIGHT_GRAY(),
            font=FONT_SMALL, width=10, anchor="e"
        )
        self.photo_label.pack(side="right")

        self.moment_video_path = ""
        self.video_label_var = tk.StringVar(value="")
        tk.Label(input_row, textvariable=self.video_label_var,
                 bg=CARD_BG(), fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(side="right", padx=(0, 2))

        tk.Button(input_row, text="🎬", font=("Segoe UI Emoji", 12),
                  bg=CARD_BG(), relief="flat",
                  command=self._select_moment_video).pack(side="right", padx=2)

        tk.Button(input_row, text="发布", bg=BTN_COLOR(), fg="white",
                  command=self._do_publish_moment).pack(side="right", padx=(8, 0))

        list_container = tk.Frame(self.main_container, bg=BG_COLOR())
        list_container.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        canvas = tk.Canvas(list_container, bg=BG_COLOR(), highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.moments_scroll_frame = tk.Frame(canvas, bg=BG_COLOR())

        self.moments_scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.moments_scroll_frame, anchor="nw", width=430)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        self._canvas = canvas

        self._refresh_moments_list()

    def _select_photo(self):
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

    def _select_moment_video(self):
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            parent=self.root,
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.moment_video_path = file_path
            fname = os.path.basename(file_path)
            if len(fname) > 12:
                fname = fname[:10] + "…"
            self.video_label_var.set(f"🎬{fname}")

    def _do_publish_moment(self):
        content = self.moment_input.get().strip()
        if not content and not self.moment_video_path and not self.photo_path_var.get():
            messagebox.showwarning("提示", "请输入动态内容或选择图片/视频！")
            return
        try:
            photo = self.photo_path_var.get()
            video_path = self.moment_video_path if self.moment_video_path else ""
            add_moment(
                account=self.account,
                nickname=self.user["nickname"],
                avatar=self.user.get("avatar", "🐧"),
                content=content,
                photo_path=photo,
                video_path=video_path,
            )
            self.moment_input.delete(0, tk.END)
            self.photo_path_var.set("")
            self.photo_label.config(text="")
            self.moment_video_path = ""
            self.video_label_var.set("")
            self._refresh_moments_list()
        except Exception as e:
            messagebox.showerror("发布失败", f"动态发布出错：{str(e)}")

    def _refresh_moments_list(self):
        for w in self.moments_scroll_frame.winfo_children():
            w.destroy()

        moments = load_moments_data()
        if not moments:
            empty_label = tk.Label(
                self.moments_scroll_frame, text="暂无动态，快来发第一条吧 ✨",
                bg=BG_COLOR(), fg=TEXT_LIGHT_GRAY(), font=FONT_NORMAL, pady=40
            )
            empty_label.pack()
            return

        for m in moments:
            self._render_moment_card(m)

    def _render_moment_card(self, m):
        card = tk.Frame(self.moments_scroll_frame, bg=CARD_BG(), padx=12, pady=10)
        card.pack(fill="x", pady=6)

        top_row = tk.Frame(card, bg=CARD_BG())
        top_row.pack(fill="x")

        avatar_text = m.get("avatar", "🐧")
        tk.Label(top_row, text=avatar_text, font=("Segoe UI Emoji", 24),
                 bg=CARD_BG()).pack(side="left", padx=(0, 8))

        info_col = tk.Frame(top_row, bg=CARD_BG())
        info_col.pack(side="left", fill="x", expand=True)

        tk.Label(info_col, text=m["nickname"], bg=CARD_BG(), fg=HEADER_COLOR(),
                 font=("Microsoft YaHei", 11, "bold"), anchor="w").pack(fill="x")

        tk.Label(info_col, text=m["time"], bg=CARD_BG(), fg=TEXT_LIGHT_GRAY(),
                 font=FONT_SMALL, anchor="w").pack(fill="x")

        content_label = tk.Label(card, text=m["content"], bg=CARD_BG(), fg=TEXT_BLACK(),
                                 font=FONT_NORMAL, anchor="w", justify="left", wraplength=380)
        content_label.pack(fill="x", pady=(8, 5))

        video_path = m.get("video", "")
        if video_path and os.path.isfile(video_path):
            video_frame = tk.Frame(card, bg="#F0F0F0", padx=8, pady=6)
            video_frame.pack(fill="x", pady=(0, 5))
            tk.Label(video_frame, text="🎬 视频附件",
                     bg="#F0F0F0", fg=HEADER_COLOR(),
                     font=("Microsoft YaHei", 10, "bold")).pack(side="left")
            tk.Button(video_frame, text="▶ 播放", bg=BTN_COLOR(), fg="white",
                      font=FONT_SMALL, relief="flat", padx=10,
                      command=lambda p=video_path: self._play_video(p)).pack(side="right")

        photo_name = m.get("photo", "")
        if photo_name:
            photo_full = os.path.join(MOMENTS_PHOTOS_DIR, photo_name)
            if os.path.exists(photo_full):
                try:
                    img = Image.open(photo_full)
                    img.thumbnail((260, 400), Image.LANCZOS)
                    tk_img = ImageTk.PhotoImage(img)
                    img_label = tk.Label(card, image=tk_img, bg=CARD_BG())
                    img_label.image = tk_img
                    img_label.pack(pady=(0, 5))
                    img_label.bind("<Button-1>", lambda e, p=photo_full: self._show_photo_popup(p))
                except Exception:
                    pass

        action_row = tk.Frame(card, bg=CARD_BG())
        action_row.pack(fill="x")

        liked = self.account in m.get("liked_accounts", [])
        like_text = f"❤️ {m['likes']}" if liked else f"🤍 {m['likes']}"
        like_btn = tk.Button(
            action_row, text=like_text, bg=CARD_BG(), relief="flat",
            font=FONT_SMALL, fg=TEXT_GRAY(),
            command=lambda mid=m["id"]: self._do_toggle_like(mid)
        )
        like_btn.pack(side="left", padx=(0, 10))

        if m.get("account") == self.account:
            tk.Button(
                action_row, text="🗑 删除", bg=CARD_BG(), relief="flat",
                font=FONT_SMALL, fg="red",
                command=lambda mid=m["id"]: self._do_delete_moment(mid)
            ).pack(side="left")

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
            pop = tk.Toplevel(self.root)
            pop.title("查看照片")
            img = Image.open(photo_full_path)
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

    def _do_toggle_like(self, moment_id):
        result = toggle_like_moment(moment_id, self.account)
        if result:
            self._refresh_moments_list()

    def _do_delete_moment(self, moment_id):
        confirm = messagebox.askyesno("确认删除", "确定要删除这条动态吗？")
        if confirm:
            if delete_moment(moment_id, self.account):
                self._refresh_moments_list()

    # ==================== 每日打卡页面 ====================

    def show_checkin_page(self):
        self.current_page = "checkin"
        self.clear_main_container()

        header = tk.Frame(self.main_container, bg=HEADER_COLOR(), height=120)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="每日打卡", fg="white", bg=HEADER_COLOR(),
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"{self.user['nickname']}，坚持就是胜利！",
                 fg="#E8F4FD", bg=HEADER_COLOR(), font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR(),
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

        status = get_checkin_status(self.account)

        stat_frame = tk.Frame(self.main_container, bg=CARD_BG(), padx=15, pady=15)
        stat_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(stat_frame, text="打卡统计", bg=CARD_BG(), fg=TEXT_BLACK(),
                 font=("Microsoft YaHei", 14, "bold")).pack(anchor="w", pady=(0, 10))

        stats_row = tk.Frame(stat_frame, bg=CARD_BG())
        stats_row.pack(fill="x", pady=5)

        total_frame = tk.Frame(stats_row, bg=CARD_BG())
        total_frame.pack(side="left", expand=True)
        tk.Label(total_frame, text=f"{status['total']}", fg=HEADER_COLOR(),
                 bg=CARD_BG(), font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(total_frame, text="总打卡天数", bg=CARD_BG(), fg=TEXT_GRAY(),
                 font=FONT_SMALL).pack()

        streak_frame = tk.Frame(stats_row, bg=CARD_BG())
        streak_frame.pack(side="left", expand=True)
        tk.Label(streak_frame, text=f"{status['streak']}", fg="#FF6B35",
                 bg=CARD_BG(), font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(streak_frame, text="连续打卡天数", bg=CARD_BG(), fg=TEXT_GRAY(),
                 font=FONT_SMALL).pack()

        self.checkin_btn_frame = tk.Frame(self.main_container, bg=BG_COLOR())
        self.checkin_btn_frame.pack(fill="x", padx=20, pady=10)

        if status["checked_in"]:
            btn = tk.Button(
                self.checkin_btn_frame, text="✅ 今日已打卡",
                bg=BTN_GREEN(), fg="white", font=FONT_BTN, relief="flat",
                state="disabled", padx=20, pady=10
            )
            btn.pack()
            tk.Label(self.checkin_btn_frame, text="太棒了，明天继续加油！",
                     bg=BG_COLOR(), fg=TEXT_LIGHT_GRAY(), font=FONT_SMALL).pack(pady=5)
        else:
            tk.Label(self.checkin_btn_frame, text="今天还没有打卡哦，快来打卡吧！",
                     bg=BG_COLOR(), fg=TEXT_LIGHT_GRAY(), font=FONT_NORMAL).pack(pady=(0, 10))
            btn = tk.Button(
                self.checkin_btn_frame, text="🎯 立即打卡",
                bg=BTN_COLOR(), fg="white", font=FONT_BTN, relief="flat",
                padx=30, pady=12, command=self._do_checkin_action
            )
            btn.pack()

        cal_frame = tk.Frame(self.main_container, bg=CARD_BG(), padx=15, pady=15)
        cal_frame.pack(fill="x", padx=20, pady=15)

        today = datetime.now()
        year = today.year
        month = today.month
        _, days_in_month = monthrange(year, month)
        month_records = get_month_records(self.account, year, month)

        tk.Label(cal_frame, text=f"{year}年{month}月打卡日历",
                 bg=CARD_BG(), fg=TEXT_BLACK(),
                 font=("Microsoft YaHei", 12, "bold")).pack(anchor="w", pady=(0, 10))

        weekday_frame = tk.Frame(cal_frame, bg=CARD_BG())
        weekday_frame.pack(fill="x")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        for wd in weekdays:
            tk.Label(weekday_frame, text=wd, bg=CARD_BG(), fg=TEXT_GRAY(),
                     font=FONT_SMALL, width=4, anchor="center").pack(side="left", padx=4)

        grid_frame = tk.Frame(cal_frame, bg=CARD_BG())
        grid_frame.pack(fill="x", pady=(5, 0))

        first_weekday = datetime(year, month, 1).weekday()
        first_weekday_sun = (first_weekday + 1) % 7

        col = 0
        for _ in range(first_weekday_sun):
            tk.Label(grid_frame, text="", bg=CARD_BG(), width=4).pack(side="left", padx=4)
            col += 1

        for day in range(1, days_in_month + 1):
            date_str = f"{year:04d}-{month:02d}-{day:02d}"
            is_checked = date_str in month_records

            if is_checked:
                day_label = tk.Label(
                    grid_frame, text=f"{day}✅", bg=CAL_CHECKED_BG(), fg=CAL_CHECKED_FG(),
                    font=FONT_SMALL, width=4, relief="solid", bd=1
                )
            else:
                is_today = (day == today.day)
                if is_today:
                    day_label = tk.Label(
                        grid_frame, text=str(day), bg=CAL_TODAY_BG(), fg=CAL_TODAY_FG(),
                        font=FONT_SMALL, width=4, relief="solid", bd=1
                    )
                else:
                    day_label = tk.Label(
                        grid_frame, text=str(day), bg=CARD_BG(), fg=TEXT_BLACK(),
                        font=FONT_SMALL, width=4, bd=1
                    )
            day_label.pack(side="left", padx=4, pady=2)
            col += 1
            if col >= 7:
                col = 0

    def _do_checkin_action(self):
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
            if self.polling_id:
                self.root.after_cancel(self.polling_id)
                self.polling_id = None
            if self.group_polling_id:
                self.root.after_cancel(self.group_polling_id)
                self.group_polling_id = None
            self._stop_level_timer()
            self.heartbeat.stop()
            self.root.destroy()
            from login_window import run_login_window
            run_login_window()

    def _on_close(self):
        """窗口关闭（点击 X 按钮）"""
        if self.polling_id:
            self.root.after_cancel(self.polling_id)
            self.polling_id = None
        if self.group_polling_id:
            self.root.after_cancel(self.group_polling_id)
            self.group_polling_id = None
        self._stop_level_timer()
        self.heartbeat.stop()
        self.root.destroy()