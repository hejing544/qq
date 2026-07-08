# QQ 桌面版

一个基于 Python + Tkinter 的 QQ 桌面客户端模拟实现。

## 功能特性

- **用户登录**：支持账号密码登录，记住密码与自动登录选项
- **用户注册**：新账号在线注册，支持昵称设置与密码确认
- **个人主页**：展示用户头像、昵称、个性签名、性别、年龄、城市等信息
- **个人资料修改**：支持修改头像、昵称、个性签名、城市
- **即时聊天**：好友列表选择，发送与接收消息
- **自动回复**：好友自动回复模拟
- **聊天记录持久化**：消息自动保存到本地 JSON 文件

## 项目结构

```
qq/
├── qq_login.py         # 单文件整合版本（可直接运行）
├── login_window.py     # 登录窗口模块
├── register_window.py  # 注册窗口模块
├── main_window.py      # 主窗口/聊天窗口模块
├── user_db.py          # 用户数据库模块
├── chat_record.json    # 聊天记录文件（运行时自动生成）
├── .gitignore          # Git 忽略规则
└── readme.md           # 项目说明
```

## 环境要求

- Python 3.8+
- 依赖库：`bcrypt`

## 快速开始

```bash
# 1. 安装依赖
pip install bcrypt

# 2. 运行（单文件整合版）
python qq_login.py
```

### 预置测试账号

| 账号 | 密码 | 昵称 |
|------|------|------|
| 123456 | abc123 | 小明 |
| admin | admin123 | 管理员 |
| qquser | password | QQ用户 |

## 技术栈

- **GUI 框架**：Tkinter（Python 标准库）
- **密码加密**：bcrypt（仅 `qq_login.py` 整合版使用）
- **数据存储**：内存字典 + JSON 文件持久化

## 许可证

MIT
abc
def