# -*- coding: utf-8 -*-
"""主窗口 / 聊天窗口 UI 模块"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime

from config import (
    MAIN_W, MAIN_H,
    HEADER_COLOR, BG_COLOR, BTN_COLOR, BTN_ACTIVE, CARD_BG,
    LOGOUT_BG, LOGOUT_ACTIVE, INPUT_HIGHLIGHT, INPUT_BORDER,
    TEXT_GRAY, TEXT_LIGHT_GRAY, TEXT_BLACK, ONLINE_GREEN, DIVIDER_GRAY,
    FONT_TITLE, FONT_SUBTITLE, FONT_NORMAL, FONT_SMALL, FONT_BTN, FONT_EMOJI,
)
from chat_db import send_message, load_conversation
from user_db import USER_DB, _save_user_db
from friends_db import (
    get_friend_list, get_pending_requests, send_friend_request,
    accept_friend_request, reject_friend_request, remove_friend, search_users
)
from moments_db import (
    load_moments_data, add_moment, delete_moment, toggle_like_moment,
)
import subprocess
import os
import sys
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

            self.current_page = "home"
            self.current_chat_target_account = None
            self.current_chat_target_nickname = None
            self.last_msg_count = 0
            self.polling_id = None

            self.side_frame = tk.Frame(self.root, bg="#2C3E50", width=120)
            self.side_frame.pack(side="left", fill="y")
            self.side_frame.pack_propagate(False)

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
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="QQ主页", fg="white", bg=HEADER_COLOR,
                 font=("Microsoft YaHei", 28, "bold")).place(x=20, y=15)
        tk.Label(header, text=f"当前登录账号：{self.account}",
                 fg="#E8F4FD", bg=HEADER_COLOR, font=FONT_SUBTITLE).place(x=20, y=65)
        tk.Button(header, text="×", fg="white", bg=HEADER_COLOR,
                  font=("Arial", 16), relief="flat",
                  command=self.root.quit).place(x=370, y=10)

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

    # ==================== 聊天页面（含好友系统） ====================

    def show_chat_page(self):
        self.current_page = "chat"
        self.clear_main_container()

        left_box = tk.Frame(self.main_container, bg="#EEEEEE", width=140)
        left_box.pack(side="left", fill="y")
        tk.Label(left_box, text="我的好友", bg="#EEEEEE", font=FONT_NORMAL).pack(pady=5)

        btn_frame = tk.Frame(left_box, bg="#EEEEEE")
        btn_frame.pack(fill="x", padx=5, pady=2)
        tk.Button(btn_frame, text="➕ 添加好友", bg=BG_COLOR, relief="flat",
                  font=FONT_SMALL, command=self._show_add_friend_popup).pack(fill="x")
        tk.Button(btn_frame, text="📩 好友请求", bg=BG_COLOR, relief="flat",
                  font=FONT_SMALL, command=self._show_pending_requests).pack(fill="x", pady=(2,0))

        self.chat_listbox = tk.Listbox(left_box, font=FONT_NORMAL)
        self.chat_listbox.pack(fill="both", expand=True, padx=5, pady=5)

        self.friend_accounts = []
        self._refresh_friend_list()

        self.chat_listbox.bind("<<ListboxSelect>>", self.load_target_chat)

        chat_area = tk.Frame(self.main_container, bg="white")
        chat_area.pack(side="right", fill="both", expand=True, padx=5)
        self.chat_title = tk.Label(chat_area, text="请选择好友开始聊天", bg="white", font=FONT_TITLE)
        self.chat_title.pack(fill="x", pady=10)

        self.msg_display = scrolledtext.ScrolledText(
            chat_area, bg=BG_COLOR, fg=TEXT_BLACK,
            font=FONT_NORMAL, wrap="word", state="disabled")
        self.msg_display.pack(fill="both", expand=True, padx=10, pady=5)

        input_frame = tk.Frame(chat_area, bg="white")
        input_frame.pack(fill="x", padx=10, pady=10)
        self.msg_input = tk.Entry(input_frame, font=FONT_NORMAL, highlightthickness=1,
                                  highlightcolor=HEADER_COLOR, highlightbackground=INPUT_BORDER)
        self.msg_input.pack(side="left", fill="x", expand=True, ipady=5)
        self.msg_input.bind("<Return>", lambda e: self.send_chat_msg())
        tk.Button(input_frame, text="发送", bg=BTN_COLOR, fg="white",
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
                 bg=HEADER_COLOR, fg="white").pack(fill="x", ipady=10)

        search_frame = tk.Frame(pop, bg=CARD_BG)
        search_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(search_frame, text="输入账号或昵称：", font=FONT_NORMAL).pack(anchor="w")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, font=FONT_NORMAL,
                                highlightthickness=1, highlightcolor=HEADER_COLOR,
                                highlightbackground=INPUT_BORDER)
        search_entry.pack(fill="x", ipady=4, pady=5)
        search_entry.focus()

        result_frame = tk.Frame(pop, bg=BG_COLOR)
        result_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        result_canvas = tk.Canvas(result_frame, bg=BG_COLOR, highlightthickness=0, height=120)
        result_scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=result_canvas.yview)
        result_inner = tk.Frame(result_canvas, bg=BG_COLOR)
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
                tk.Label(result_inner, text="未找到匹配的用户", bg=BG_COLOR,
                         fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL).pack(pady=20)
                return

            for user in results:
                if user["account"] == self.account or user["account"] in friend_accounts:
                    continue
                row = tk.Frame(result_inner, bg=CARD_BG, padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{user['account']} - {user['nickname']}",
                         bg=CARD_BG, font=FONT_NORMAL).pack(side="left")
                tk.Button(row, text="添加好友", bg=BTN_COLOR, fg="white",
                          font=FONT_SMALL, relief="flat", padx=8,
                          command=lambda a=user["account"], n=user["nickname"], r=row:
                            _do_add(a, n, r)).pack(side="right")

        def _do_add(target_account, target_nickname, row_widget):
            ok = send_friend_request(self.account, self.user["nickname"], target_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已发送请求", bg=CARD_BG,
                         fg=ONLINE_GREEN, font=FONT_SMALL).pack(side="left")
            else:
                messagebox.showinfo("提示", "请求发送失败，可能已是好友或已发送过请求", parent=pop)

        search_entry.bind("<Return>", lambda e: do_search())
        tk.Button(search_frame, text="搜索", bg=BTN_COLOR, fg="white",
                  font=FONT_BTN, command=do_search).pack(fill="x", ipady=4)

        tk.Frame(pop, bg=DIVIDER_GRAY, height=1).pack(fill="x", padx=20)
        tk.Label(pop, text="📩 收到的好友请求", font=("Microsoft YaHei", 11, "bold"),
                 bg=BG_COLOR).pack(anchor="w", padx=20, pady=(10, 0))

        pending_frame = tk.Frame(pop, bg=BG_COLOR)
        pending_frame.pack(fill="x", padx=20, pady=5)

        requests = get_pending_requests(self.account)
        if not requests:
            tk.Label(pending_frame, text="暂无好友请求", bg=BG_COLOR,
                     fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w")
        else:
            for req in requests:
                req_row = tk.Frame(pending_frame, bg=CARD_BG, padx=10, pady=5)
                req_row.pack(fill="x", pady=3)
                tk.Label(req_row, text=f"{req['from_account']} - {req['from_nickname']}",
                         bg=CARD_BG, font=FONT_NORMAL).pack(side="left")
                tk.Button(req_row, text="接受", bg=ONLINE_GREEN, fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], n=req["from_nickname"], r=req_row:
                            _do_accept(a, n, r)).pack(side="right", padx=2)
                tk.Button(req_row, text="拒绝", bg=LOGOUT_BG, fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], r=req_row:
                            _do_reject(a, r)).pack(side="right", padx=2)

        def _do_accept(from_account, from_nickname, row_widget):
            ok = accept_friend_request(self.account, from_account, from_nickname,
                                       self.user["nickname"])
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已接受", bg=CARD_BG,
                         fg=ONLINE_GREEN, font=FONT_SMALL).pack(side="left")
                self._refresh_friend_list()

        def _do_reject(from_account, row_widget):
            ok = reject_friend_request(self.account, from_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG,
                         fg=TEXT_GRAY, font=FONT_SMALL).pack(side="left")

    def _show_pending_requests(self):
        pop = tk.Toplevel(self.root)
        pop.title("好友请求")
        pop.geometry("380x300")
        pop.transient(self.root)
        pop.grab_set()
        pop.resizable(False, False)

        tk.Label(pop, text="📩 好友请求管理", font=FONT_TITLE,
                 bg=HEADER_COLOR, fg="white").pack(fill="x", ipady=10)

        tk.Label(pop, text="收到的请求", font=("Microsoft YaHei", 11, "bold"),
                 bg=BG_COLOR).pack(anchor="w", padx=20, pady=(10, 0))

        in_frame = tk.Frame(pop, bg=BG_COLOR)
        in_frame.pack(fill="x", padx=20, pady=5)

        requests = get_pending_requests(self.account)
        if not requests:
            tk.Label(in_frame, text="暂无收到的好友请求", bg=BG_COLOR,
                     fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(anchor="w", pady=10)
        else:
            for req in requests:
                row = tk.Frame(in_frame, bg=CARD_BG, padx=10, pady=5)
                row.pack(fill="x", pady=3)
                tk.Label(row, text=f"{req['from_account']} - {req['from_nickname']}",
                         bg=CARD_BG, font=FONT_NORMAL).pack(side="left")
                tk.Button(row, text="接受", bg=ONLINE_GREEN, fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], n=req["from_nickname"], r=row:
                            _acc(a, n, r)).pack(side="right", padx=2)
                tk.Button(row, text="拒绝", bg=LOGOUT_BG, fg="white",
                          font=FONT_SMALL, relief="flat", padx=6,
                          command=lambda a=req["from_account"], r=row:
                            _rej(a, r)).pack(side="right", padx=2)

        def _acc(from_account, from_nickname, row_widget):
            ok = accept_friend_request(self.account, from_account, from_nickname,
                                       self.user["nickname"])
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="✅ 已接受", bg=CARD_BG,
                         fg=ONLINE_GREEN, font=FONT_SMALL).pack(side="left")
                self._refresh_friend_list()

        def _rej(from_account, row_widget):
            ok = reject_friend_request(self.account, from_account)
            if ok:
                for w in row_widget.winfo_children():
                    w.destroy()
                tk.Label(row_widget, text="❌ 已拒绝", bg=CARD_BG,
                         fg=TEXT_GRAY, font=FONT_SMALL).pack(side="left")

        tk.Frame(pop, bg=DIVIDER_GRAY, height=1).pack(fill="x", padx=20, pady=10)
        tk.Label(pop, text="💡 在聊天界面点击「添加好友」搜索并添加好友",
                 bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(pady=5)

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

    def edit_profile_pop(self):
        pop = tk.Toplevel(self.root)
        pop.title("修改个人资料")
        pop.geometry("400x480")
        pop.transient(self.root)
        pop.resizable(False, False)
        pop.grab_set()

        tk.Label(pop, text="头像：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(15, 0))
        avatar_var = tk.StringVar(value=self.user.get("avatar", "🐧"))
        avatars = ["🐧", "🐶", "🐱", "🐼", "🐨", "🦊", "🐰", "🐯"]
        avatar_frame = tk.Frame(pop)
        avatar_frame.pack(pady=3)
        for ava in avatars:
            tk.Radiobutton(avatar_frame, text=ava, variable=avatar_var, value=ava,
                           font=("Segoe UI Emoji", 16)).pack(side="left")

        tk.Label(pop, text="昵称：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        nick_var = tk.StringVar(value=self.user["nickname"])
        tk.Entry(pop, textvariable=nick_var, width=30, font=FONT_NORMAL).pack(pady=3)

        tk.Label(pop, text="性别：", font=FONT_NORMAL).pack(anchor="w", padx=30, pady=(5, 0))
        gender_var = tk.StringVar(value=self.user.get("gender", "保密"))
        gender_frame = tk.Frame(pop)
        gender_frame.pack(pady=3)
        for g in ["男", "女", "保密"]:
            tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g,
                           font=FONT_NORMAL).pack(side="left", padx=5)

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

        tk.Button(pop, text="保存修改", bg=BTN_COLOR, fg="white",
                  font=FONT_BTN, command=save_info).pack(pady=15)

    # ==================== 动态（朋友圈）页面 ====================

    def show_moments_page(self):
        self.current_page = "moments"
        self.clear_main_container()

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

        # 视频选择相关
        self.moment_video_path = ""
        self.video_label_var = tk.StringVar(value="未选择视频")
        tk.Label(input_row, textvariable=self.video_label_var,
                 bg=CARD_BG, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(side="right", padx=(0, 4))

        tk.Button(input_row, text="🎬 选视频", bg=BTN_COLOR, fg="white",
                  font=FONT_SMALL, relief="flat", padx=6,
                  command=self._select_moment_video).pack(side="right", padx=2)

        tk.Button(input_row, text="发布", bg=BTN_COLOR, fg="white",
                  command=self._do_publish_moment).pack(side="right", padx=(8, 0))

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

        def _on_mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
        self._canvas = canvas

        self._refresh_moments_list()

    def _select_moment_video(self):
        """弹出文件选择对话框选择视频文件"""
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(
            title="选择视频文件",
            parent=self.root,
            filetypes=[("视频文件", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"), ("所有文件", "*.*")]
        )
        if file_path:
            self.moment_video_path = file_path
            fname = os.path.basename(file_path)
            self.video_label_var.set(f"🎬 {fname}")

    def _do_publish_moment(self):
        content = self.moment_input.get().strip()
        if not content and not self.moment_video_path:
            messagebox.showwarning("提示", "请输入动态内容或选择视频！")
            return
        try:
            video_path = self.moment_video_path if self.moment_video_path else ""
            add_moment(
                account=self.account,
                nickname=self.user["nickname"],
                avatar=self.user.get("avatar", "🐧"),
                content=content,
                video_path=video_path,
            )
            self.moment_input.delete(0, tk.END)
            self.moment_video_path = ""
            self.video_label_var.set("未选择视频")
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
                bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL, pady=40
            )
            empty_label.pack()
            return

        for m in moments:
            self._render_moment_card(m)

    def _render_moment_card(self, m):
        card = tk.Frame(self.moments_scroll_frame, bg=CARD_BG, padx=12, pady=10)
        card.pack(fill="x", pady=6)

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

        content_label = tk.Label(card, text=m["content"], bg=CARD_BG, fg=TEXT_BLACK,
                                 font=FONT_NORMAL, anchor="w", justify="left", wraplength=380)
        content_label.pack(fill="x", pady=(8, 5))

        # 显示视频附件
        video_path = m.get("video", "")
        if video_path and os.path.isfile(video_path):
            video_frame = tk.Frame(card, bg="#F0F0F0", padx=8, pady=6)
            video_frame.pack(fill="x", pady=(0, 5))
            tk.Label(video_frame, text="🎬 视频附件",
                     bg="#F0F0F0", fg=HEADER_COLOR,
                     font=("Microsoft YaHei", 10, "bold")).pack(side="left")
            tk.Button(video_frame, text="▶ 播放", bg=BTN_COLOR, fg="white",
                      font=FONT_SMALL, relief="flat", padx=10,
                      command=lambda p=video_path: self._play_video(p)).pack(side="right")

        action_row = tk.Frame(card, bg=CARD_BG)
        action_row.pack(fill="x")

        liked = self.account in m.get("liked_accounts", [])
        like_text = f"❤️ {m['likes']}" if liked else f"🤍 {m['likes']}"
        like_btn = tk.Button(
            action_row, text=like_text, bg=CARD_BG, relief="flat",
            font=FONT_SMALL, fg=TEXT_GRAY,
            command=lambda mid=m["id"]: self._do_toggle_like(mid)
        )
        like_btn.pack(side="left", padx=(0, 10))

        if m.get("account") == self.account:
            tk.Button(
                action_row, text="🗑 删除", bg=CARD_BG, relief="flat",
                font=FONT_SMALL, fg="red",
                command=lambda mid=m["id"]: self._do_delete_moment(mid)
            ).pack(side="left")

    def _play_video(self, video_path):
        """使用系统默认播放器打开视频文件"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(video_path)
            elif os.name == 'posix':  # macOS / Linux
                subprocess.call(('open' if sys.platform == 'darwin' else 'xdg-open', video_path))
        except Exception as e:
            messagebox.showerror("播放失败", f"无法打开视频文件：{str(e)}")

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

        status = get_checkin_status(self.account)

        stat_frame = tk.Frame(self.main_container, bg=CARD_BG, padx=15, pady=15)
        stat_frame.pack(fill="x", padx=20, pady=15)

        tk.Label(stat_frame, text="打卡统计", bg=CARD_BG, fg=TEXT_BLACK,
                 font=("Microsoft YaHei", 14, "bold")).pack(anchor="w", pady=(0, 10))

        stats_row = tk.Frame(stat_frame, bg=CARD_BG)
        stats_row.pack(fill="x", pady=5)

        total_frame = tk.Frame(stats_row, bg=CARD_BG)
        total_frame.pack(side="left", expand=True)
        tk.Label(total_frame, text=f"{status['total']}", fg=HEADER_COLOR,
                 bg=CARD_BG, font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(total_frame, text="总打卡天数", bg=CARD_BG, fg=TEXT_GRAY,
                 font=FONT_SMALL).pack()

        streak_frame = tk.Frame(stats_row, bg=CARD_BG)
        streak_frame.pack(side="left", expand=True)
        tk.Label(streak_frame, text=f"{status['streak']}", fg="#FF6B35",
                 bg=CARD_BG, font=("Microsoft YaHei", 36, "bold")).pack()
        tk.Label(streak_frame, text="连续打卡天数", bg=CARD_BG, fg=TEXT_GRAY,
                 font=FONT_SMALL).pack()

        self.checkin_btn_frame = tk.Frame(self.main_container, bg=BG_COLOR)
        self.checkin_btn_frame.pack(fill="x", padx=20, pady=10)

        if status["checked_in"]:
            btn = tk.Button(
                self.checkin_btn_frame, text="✅ 今日已打卡",
                bg="#52C41A", fg="white", font=FONT_BTN, relief="flat",
                state="disabled", padx=20, pady=10
            )
            btn.pack()
            tk.Label(self.checkin_btn_frame, text="太棒了，明天继续加油！",
                     bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_SMALL).pack(pady=5)
        else:
            tk.Label(self.checkin_btn_frame, text="今天还没有打卡哦，快来打卡吧！",
                     bg=BG_COLOR, fg=TEXT_LIGHT_GRAY, font=FONT_NORMAL).pack(pady=(0, 10))
            btn = tk.Button(
                self.checkin_btn_frame, text="🎯 立即打卡",
                bg=BTN_COLOR, fg="white", font=FONT_BTN, relief="flat",
                padx=30, pady=12, command=self._do_checkin_action
            )
            btn.pack()

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

        weekday_frame = tk.Frame(cal_frame, bg=CARD_BG)
        weekday_frame.pack(fill="x")
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        for wd in weekdays:
            tk.Label(weekday_frame, text=wd, bg=CARD_BG, fg=TEXT_GRAY,
                     font=FONT_SMALL, width=4, anchor="center").pack(side="left", padx=4)

        grid_frame = tk.Frame(cal_frame, bg=CARD_BG)
        grid_frame.pack(fill="x", pady=(5, 0))

        first_weekday = datetime(year, month, 1).weekday()
        first_weekday_sun = (first_weekday + 1) % 7

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
            self.root.destroy()
            from login_window import run_login_window
            run_login_window()