# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import messagebox
from user_db import verify_user
from register_window import RegisterWindow
from main_window import MainWindow
class QQLoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title('QQ登录')
        self.width = 380
        self.height = 540
        self._center_window(self.width, self.height)
        self.root.resizable(False, False)
        self.bg_color = '#F5F6FA'
        self.header_color = '#12B7F5'
        self.btn_color = '#12B7F5'
        self.btn_active = '#0E9BD6'
        self._build_header()
        self._build_avatar()
        self._build_input_area()
        self._build_options_area()
        self._build_login_button()
        self._build_footer()
    def _center_window(self, w, h):
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - w) // 2
        y = (screen_h - h) // 2
        self.root.geometry(f'{w}x{h}+{x}+{y}')
    def _build_header(self):
        header = tk.Frame(self.root, bg=self.header_color, height=140)
        header.pack(fill='x')
        header.pack_propagate(False)
        close_btn = tk.Label(header, text='X', fg='white', bg=self.header_color, font=('Microsoft YaHei', 12, 'bold'), cursor='hand2')
        close_btn.place(x=350, y=8)
        close_btn.bind('<Button-1>', lambda e: self.root.quit())
        title = tk.Label(header, text='QQ', fg='white', bg=self.header_color, font=('Microsoft YaHei', 22, 'bold'))
        title.place(x=20, y=20)
        subtitle = tk.Label(header, text='每一天，乐在沟通', fg='#E8F7FF', bg=self.header_color, font=('Microsoft YaHei', 10))
        subtitle.place(x=22, y=60)
    def _build_avatar(self):
        avatar_frame = tk.Frame(self.root, bg=self.bg_color, height=90)
        avatar_frame.pack(fill='x')
        avatar_frame.pack_propagate(False)
        avatar = tk.Label(avatar_frame, text='QQ', bg=self.bg_color, font=('Microsoft YaHei', 40))
        avatar.pack(pady=15)
    def _build_input_area(self):
        input_frame = tk.Frame(self.root, bg=self.bg_color)
        input_frame.pack(fill='x', padx=40, pady=(5, 10))
        tk.Label(input_frame, text='账号', bg=self.bg_color, fg='#666666', font=('Microsoft YaHei', 9)).pack(anchor='w')
        self.account_var = tk.StringVar()
        account_entry = tk.Entry(input_frame, textvariable=self.account_var, font=('Microsoft YaHei', 11), relief='flat', bd=0, highlightthickness=1, highlightcolor=self.header_color, highlightbackground='#DDDDDD')
        account_entry.pack(fill='x', ipady=6, pady=(2, 12))
        tk.Label(input_frame, text='密码', bg=self.bg_color, fg='#666666', font=('Microsoft YaHei', 9)).pack(anchor='w')
        self.password_var = tk.StringVar()
        password_entry = tk.Entry(input_frame, textvariable=self.password_var, show='*', font=('Microsoft YaHei', 11), relief='flat', bd=0, highlightthickness=1, highlightcolor=self.header_color, highlightbackground='#DDDDDD')
        password_entry.pack(fill='x', ipady=6, pady=(2, 0))
        password_entry.bind('<Return>', lambda e: self._on_login())
    def _build_options_area(self):
        opt_frame = tk.Frame(self.root, bg=self.bg_color)
        opt_frame.pack(fill='x', padx=40, pady=(5, 15))
        self.remember_var = tk.IntVar(value=1)
        self.auto_login_var = tk.IntVar(value=0)
        tk.Checkbutton(opt_frame, text='记住密码', variable=self.remember_var, bg=self.bg_color, activebackground=self.bg_color, font=('Microsoft YaHei', 9), fg='#666666', selectcolor=self.bg_color, bd=0).pack(side='left')
        tk.Checkbutton(opt_frame, text='自动登录', variable=self.auto_login_var, bg=self.bg_color, activebackground=self.bg_color, font=('Microsoft YaHei', 9), fg='#666666', selectcolor=self.bg_color, bd=0).pack(side='right')
    def _build_login_button(self):
        login_btn = tk.Button(self.root, text='登 录', command=self._on_login, bg=self.btn_color, fg='white', activebackground=self.btn_active, activeforeground='white', font=('Microsoft YaHei', 12, 'bold'), relief='flat', cursor='hand2', bd=0)
        login_btn.pack(fill='x', padx=40, ipady=8)
    def _build_footer(self):
        footer = tk.Frame(self.root, bg=self.bg_color)
        footer.pack(fill='x', padx=40, pady=15)
        reg_label = tk.Label(footer, text='注册账号', fg=self.header_color, bg=self.bg_color, font=('Microsoft YaHei', 9), cursor='hand2')
        reg_label.pack(side='left')
        reg_label.bind('<Button-1>', lambda e: self._open_register())
        forgot_label = tk.Label(footer, text='找回密码', fg=self.header_color, bg=self.bg_color, font=('Microsoft YaHei', 9), cursor='hand2')
        forgot_label.pack(side='right')
        forgot_label.bind('<Button-1>', lambda e: messagebox.showinfo('提示', '跳转到找回密码页面（示例）'))
    def _on_login(self):
        account = self.account_var.get().strip()
        password = self.password_var.get().strip()
        if not account:
            messagebox.showwarning('提示', '请输入账号！')
            return
        if not password:
            messagebox.showwarning('提示', '请输入密码！')
            return
        user_info = verify_user(account, password)
        if user_info is not None:
            nickname = user_info['nickname']
            messagebox.showinfo('登录成功', f'欢迎回来，{nickname}！\n正在进入主面板...')
            self.root.destroy()
            main_root = tk.Tk()
            MainWindow(main_root, account, user_info)
            main_root.mainloop()
        else:
            messagebox.showerror('登录失败', '账号或密码错误，请重新输入！')
    def _open_register(self):
        RegisterWindow(self.root)
