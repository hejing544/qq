# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

class MainWindow:
    def __init__(self, root, account, user_info):
        self.root = root
        self.account = account
        self.user_info = user_info
        
        self.root.title(f'QQ - {user_info["nickname"]}')
        self.width = 900
        self.height = 650
        self._center_window(self.width, self.height)
        self.root.resizable(True, True)
        
        # 颜色配置
        self.bg_color = '#F5F6FA'
        self.sidebar_color = '#2C3E50'
        self.header_color = '#12B7F5'
        self.btn_color = '#12B7F5'
        self.btn_active = '#0E9BD6'
        self.text_color = '#2C3E50'
        
        # 当前页面
        self.current_page = 'home'
        
        # 聊天记录
        self.chat_history = {}
        
        self._build_ui()
    
    def _center_window(self, w, h):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    
    def _build_ui(self):
        # 主容器
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill='both', expand=True)
        
        # 侧边栏
        self._build_sidebar(main_container)
        
        # 内容区域
        self.content_frame = tk.Frame(main_container, bg=self.bg_color)
        self.content_frame.pack(side='right', fill='both', expand=True)
        
        # 显示主页
        self._show_home_page()
    
    def _build_sidebar(self, parent):
        sidebar = tk.Frame(parent, bg=self.sidebar_color, width=200)
        sidebar.pack(side='left', fill='y')
        sidebar.pack_propagate(False)
        
        # 用户信息
        user_frame = tk.Frame(sidebar, bg=self.sidebar_color)
        user_frame.pack(fill='x', padx=10, pady=20)
        
        self.sidebar_avatar = tk.Label(user_frame, text=self.user_info.get('avatar', '👤'),
                                       bg=self.sidebar_color, fg='white',
                                       font=('Microsoft YaHei', 24))
        self.sidebar_avatar.pack()

        self.sidebar_nickname = tk.Label(user_frame, text=self.user_info['nickname'],
                                         bg=self.sidebar_color, fg='white',
                                         font=('Microsoft YaHei', 12, 'bold'))
        self.sidebar_nickname.pack(pady=5)
        
        account = tk.Label(user_frame, text=f'账号: {self.account}',
                          bg=self.sidebar_color, fg='#BDC3C7',
                          font=('Microsoft YaHei', 9))
        account.pack()
        
        # 分隔线
        separator = tk.Frame(sidebar, bg='#34495E', height=1)
        separator.pack(fill='x', padx=10, pady=10)
        
        # 导航按钮
        self.home_btn = tk.Button(sidebar, text='🏠 主页', command=self._show_home_page,
                                 bg=self.sidebar_color, fg='white', activebackground='#34495E',
                                 activeforeground='white', font=('Microsoft YaHei', 11),
                                 relief='flat', cursor='hand2', bd=0, anchor='w')
        self.home_btn.pack(fill='x', padx=10, pady=5)

        self.chat_btn = tk.Button(sidebar, text='💬 聊天', command=self._show_chat_page,
                                 bg=self.sidebar_color, fg='white', activebackground='#34495E',
                                 activeforeground='white', font=('Microsoft YaHei', 11),
                                 relief='flat', cursor='hand2', bd=0, anchor='w')
        self.chat_btn.pack(fill='x', padx=10, pady=5)

        # 分隔线
        separator2 = tk.Frame(sidebar, bg='#34495E', height=1)
        separator2.pack(fill='x', padx=10, pady=10)

        # 退出按钮
        logout_btn = tk.Button(sidebar, text='🚪 退出登录', command=self._logout,
                              bg=self.sidebar_color, fg='#E74C3C', activebackground='#34495E',
                              activeforeground='#E74C3C', font=('Microsoft YaHei', 11),
                              relief='flat', cursor='hand2', bd=0, anchor='w')
        logout_btn.pack(fill='x', padx=10, pady=5)
    
    def _clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def _show_home_page(self):
        self.current_page = 'home'
        self._clear_content()
        
        # 更新按钮状态
        self.home_btn.config(bg='#34495E')
        self.chat_btn.config(bg=self.sidebar_color)
        
        # 主页内容
        home_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        home_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # 欢迎标题
        welcome = tk.Label(home_frame, text=f'欢迎回来，{self.user_info["nickname"]}！',
                          bg=self.bg_color, fg=self.text_color,
                          font=('Microsoft YaHei', 24, 'bold'))
        welcome.pack(pady=20)
        
        # 用户信息卡片
        info_frame = tk.Frame(home_frame, bg='white', relief='flat', bd=1)
        info_frame.pack(fill='x', pady=10)
        
        tk.Label(info_frame, text='个人信息', bg='white', fg=self.header_color,
                font=('Microsoft YaHei', 14, 'bold')).pack(pady=10)
        
        info_content = tk.Frame(info_frame, bg='white')
        info_content.pack(fill='x', padx=20, pady=10)
        
        info_items = [
            ('账号', self.account),
            ('昵称', self.user_info['nickname']),
            ('签名', self.user_info['signature']),
            ('性别', self.user_info['gender']),
            ('年龄', self.user_info['age']),
            ('城市', self.user_info['city'])
        ]
        
        for i, (label, value) in enumerate(info_items):
            row_frame = tk.Frame(info_content, bg='white')
            row_frame.pack(fill='x', pady=5)
            
            tk.Label(row_frame, text=f'{label}：', bg='white', fg='#666666',
                    font=('Microsoft YaHei', 10), width=8, anchor='e').pack(side='left')
            tk.Label(row_frame, text=value, bg='white', fg=self.text_color,
                    font=('Microsoft YaHei', 10), anchor='w').pack(side='left')
        
        # 快捷操作
        action_frame = tk.Frame(home_frame, bg='white', relief='flat', bd=1)
        action_frame.pack(fill='x', pady=10)
        
        tk.Label(action_frame, text='快捷操作', bg='white', fg=self.header_color,
                font=('Microsoft YaHei', 14, 'bold')).pack(pady=10)
        
        button_frame = tk.Frame(action_frame, bg='white')
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text='开始聊天', command=self._show_chat_page,
                 bg=self.btn_color, fg='white', activebackground=self.btn_active,
                 font=('Microsoft YaHei', 11), relief='flat', cursor='hand2',
                 bd=0, padx=20, pady=8).pack(side='left', padx=10)
        
        tk.Button(button_frame, text='修改资料', command=self._edit_profile,
                 bg='#95A5A6', fg='white', activebackground='#7F8C8D',
                 font=('Microsoft YaHei', 11), relief='flat', cursor='hand2',
                 bd=0, padx=20, pady=8).pack(side='left', padx=10)
    
    def _show_chat_page(self):
        self.current_page = 'chat'
        self._clear_content()
        
        # 更新按钮状态
        self.home_btn.config(bg=self.sidebar_color)
        self.chat_btn.config(bg='#34495E')
        
        # 聊天页面
        chat_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        chat_frame.pack(fill='both', expand=True)
        
        # 聊天列表和聊天区域
        chat_container = tk.Frame(chat_frame, bg=self.bg_color)
        chat_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 左侧聊天列表
        list_frame = tk.Frame(chat_container, bg='white', width=250)
        list_frame.pack(side='left', fill='y')
        list_frame.pack_propagate(False)
        
        tk.Label(list_frame, text='聊天列表', bg='white', fg=self.header_color,
                font=('Microsoft YaHei', 12, 'bold')).pack(pady=10)
        
        # 聊天列表
        self.chat_listbox = tk.Listbox(list_frame, bg='white', fg=self.text_color,
                                      font=('Microsoft YaHei', 10), relief='flat',
                                      bd=0, highlightthickness=0)
        self.chat_listbox.pack(fill='both', expand=True, padx=5, pady=5)
        self.chat_listbox.bind('<<ListboxSelect>>', self._on_chat_select)
        
        # 添加示例聊天
        sample_chats = ['小明', '小红', '工作群', '家庭群', '同学群']
        for chat in sample_chats:
            self.chat_listbox.insert(tk.END, chat)
            if chat not in self.chat_history:
                self.chat_history[chat] = []
        
        # 右侧聊天区域
        chat_area = tk.Frame(chat_container, bg='white')
        chat_area.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        # 聊天标题
        self.chat_title = tk.Label(chat_area, text='选择一个聊天', bg='white',
                                  fg=self.text_color, font=('Microsoft YaHei', 12, 'bold'))
        self.chat_title.pack(fill='x', pady=10)
        
        # 消息显示区域
        self.message_display = scrolledtext.ScrolledText(chat_area, bg='#F5F6FA',
                                                         fg=self.text_color,
                                                         font=('Microsoft YaHei', 10),
                                                         relief='flat', bd=0,
                                                         wrap='word', state='disabled')
        self.message_display.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 消息输入区域
        input_frame = tk.Frame(chat_area, bg='white')
        input_frame.pack(fill='x', padx=10, pady=10)
        
        self.message_input = tk.Entry(input_frame, font=('Microsoft YaHei', 10),
                                     relief='flat', bd=0, highlightthickness=1,
                                     highlightcolor=self.header_color,
                                     highlightbackground='#DDDDDD')
        self.message_input.pack(side='left', fill='x', expand=True, ipady=5)
        self.message_input.bind('<Return>', lambda e: self._send_message())
        
        send_btn = tk.Button(input_frame, text='发送', command=self._send_message,
                           bg=self.btn_color, fg='white', activebackground=self.btn_active,
                           font=('Microsoft YaHei', 10), relief='flat', cursor='hand2',
                           bd=0, padx=15)
        send_btn.pack(side='right', padx=(5, 0))
    
    def _on_chat_select(self, event):
        selection = self.chat_listbox.curselection()
        if selection:
            chat_name = self.chat_listbox.get(selection[0])
            self.chat_title.config(text=f'与 {chat_name} 聊天')
            self._display_messages(chat_name)
    
    def _display_messages(self, chat_name):
        self.message_display.config(state='normal')
        self.message_display.delete(1.0, tk.END)
        
        if chat_name in self.chat_history:
            for msg in self.chat_history[chat_name]:
                self._append_message(msg['sender'], msg['content'], msg['time'])
        
        self.message_display.config(state='disabled')
        self.message_display.see(tk.END)
    
    def _append_message(self, sender, content, time):
        self.message_display.config(state='normal')
        
        if sender == self.user_info['nickname']:
            # 自己的消息
            self.message_display.insert(tk.END, f'\n{time} {sender}\n', 'my_time')
            self.message_display.insert(tk.END, f'{content}\n', 'my_message')
        else:
            # 对方的消息
            self.message_display.insert(tk.END, f'\n{time} {sender}\n', 'other_time')
            self.message_display.insert(tk.END, f'{content}\n', 'other_message')
        
        # 配置标签样式
        self.message_display.tag_config('my_time', foreground='#12B7F5', font=('Microsoft YaHei', 8))
        self.message_display.tag_config('my_message', foreground='#2C3E50', font=('Microsoft YaHei', 10))
        self.message_display.tag_config('other_time', foreground='#95A5A6', font=('Microsoft YaHei', 8))
        self.message_display.tag_config('other_message', foreground='#2C3E50', font=('Microsoft YaHei', 10))
        
        self.message_display.config(state='disabled')
        self.message_display.see(tk.END)
    
    def _send_message(self):
        selection = self.chat_listbox.curselection()
        if not selection:
            messagebox.showwarning('提示', '请先选择一个聊天！')
            return
        
        chat_name = self.chat_listbox.get(selection[0])
        content = self.message_input.get().strip()
        
        if not content:
            return
        
        # 添加消息到历史记录
        time_str = datetime.now().strftime('%H:%M')
        message = {
            'sender': self.user_info['nickname'],
            'content': content,
            'time': time_str
        }
        
        if chat_name not in self.chat_history:
            self.chat_history[chat_name] = []
        
        self.chat_history[chat_name].append(message)
        
        # 显示消息
        self._append_message(message['sender'], message['content'], message['time'])
        
        # 清空输入框
        self.message_input.delete(0, tk.END)
        
        # 模拟自动回复
        self._simulate_reply(chat_name)
    
    def _simulate_reply(self, chat_name):
        import random
        replies = [
            '好的，收到！',
            '明白了~',
            '👍',
            '哈哈，有意思',
            '稍等，我看看',
            '没问题！',
            '好的好的',
            '了解~'
        ]
        
        reply = random.choice(replies)
        time_str = datetime.now().strftime('%H:%M')
        
        message = {
            'sender': chat_name,
            'content': reply,
            'time': time_str
        }
        
        self.chat_history[chat_name].append(message)
        
        # 延迟显示回复
        self.root.after(1000, lambda: self._append_message(message['sender'], message['content'], message['time']))
    
    def _edit_profile(self):
        """修改资料弹窗（含性别、年龄、城市、签名、头像等，自动保存到文件）"""
        import user_db

        pop = tk.Toplevel(self.root)
        pop.title("修改个人资料")
        pop.geometry("400x480")
        pop.transient(self.root)
        pop.resizable(False, False)
        pop.grab_set()  # 模态弹窗

        # 头像选择
        tk.Label(pop, text="头像：", font=('Microsoft YaHei', 11)).pack(anchor="w", padx=30, pady=(15, 0))
        avatar_var = tk.StringVar(value=self.user_info.get("avatar", "🐧"))
        avatars = ["🐧", "🐶", "🐱", "🐼", "🐨", "🦊", "🐰", "🐯"]
        avatar_frame = tk.Frame(pop)
        avatar_frame.pack(pady=3)
        for ava in avatars:
            tk.Radiobutton(avatar_frame, text=ava, variable=avatar_var, value=ava,
                           font=("Segoe UI Emoji", 16)).pack(side="left")

        # 昵称
        tk.Label(pop, text="昵称：", font=('Microsoft YaHei', 11)).pack(anchor="w", padx=30, pady=(5, 0))
        nick_var = tk.StringVar(value=self.user_info["nickname"])
        tk.Entry(pop, textvariable=nick_var, width=30, font=('Microsoft YaHei', 11)).pack(pady=3)

        # 性别
        tk.Label(pop, text="性别：", font=('Microsoft YaHei', 11)).pack(anchor="w", padx=30, pady=(5, 0))
        gender_var = tk.StringVar(value=self.user_info.get("gender", "保密"))
        gender_frame = tk.Frame(pop)
        gender_frame.pack(pady=3)
        for g in ["男", "女", "保密"]:
            tk.Radiobutton(gender_frame, text=g, variable=gender_var, value=g,
                           font=('Microsoft YaHei', 11)).pack(side="left", padx=5)

        # 年龄
        tk.Label(pop, text="年龄：", font=('Microsoft YaHei', 11)).pack(anchor="w", padx=30, pady=(5, 0))
        age_var = tk.StringVar(value=self.user_info.get("age", "未知"))
        tk.Entry(pop, textvariable=age_var, width=30, font=('Microsoft YaHei', 11)).pack(pady=3)

        # 城市
        tk.Label(pop, text="城市：", font=('Microsoft YaHei', 11)).pack(anchor="w", padx=30, pady=(5, 0))
        city_var = tk.StringVar(value=self.user_info.get("city", "未知"))
        tk.Entry(pop, textvariable=city_var, width=30, font=('Microsoft YaHei', 11)).pack(pady=3)

        # 个性签名
        tk.Label(pop, text="个性签名：", font=('Microsoft YaHei', 11)).pack(anchor="w", padx=30, pady=(5, 0))
        sign_var = tk.StringVar(value=self.user_info.get("signature", ""))
        tk.Entry(pop, textvariable=sign_var, width=30, font=('Microsoft YaHei', 11)).pack(pady=3)

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
                self.user_info["avatar"] = new_avatar
                if new_nick:
                    self.user_info["nickname"] = new_nick
                self.user_info["gender"] = new_gender
                if new_age:
                    self.user_info["age"] = new_age
                if new_city:
                    self.user_info["city"] = new_city
                if new_sign:
                    self.user_info["signature"] = new_sign

                # 保存到文件
                user_db.save_user_db()

                # 刷新侧边栏的用户信息显示
                self.sidebar_nickname.config(text=self.user_info["nickname"])
                self.sidebar_avatar.config(text=self.user_info.get("avatar", "👤"))

                messagebox.showinfo("成功", "资料修改完成！")
                pop.destroy()
                self._show_home_page()
            except Exception as e:
                messagebox.showerror("保存失败", f"修改资料时发生错误：{str(e)}")

        tk.Button(pop, text="保存修改", bg=self.btn_color, fg="white",
                  font=('Microsoft YaHei', 12, 'bold'), command=save_info).pack(pady=15)
    
    def _logout(self):
        if messagebox.askyesno('确认退出', '确定要退出登录吗？'):
            self.root.destroy()
            # 重新打开登录窗口
            import tkinter as tk
            from login_window import QQLoginWindow
            new_root = tk.Tk()
            QQLoginWindow(new_root)
            new_root.mainloop()


if __name__ == "__main__":
    import tkinter as tk
    from login_window import QQLoginWindow
    root = tk.Tk()
    QQLoginWindow(root)
    root.mainloop()
        