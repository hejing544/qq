# QQ 桌面版

一个基于 Python + Tkinter 的 QQ 桌面客户端模拟实现。

## 功能特性

- **用户登录**：支持账号密码登录，记住密码与自动登录选项
- **用户注册**：新账号在线注册，支持昵称设置与密码确认
- **个人主页**：展示用户头像、昵称、个性签名、性别、年龄、城市等信息
- **个人资料修改**：支持修改头像、昵称、性别、年龄、城市、个性签名
- **即时聊天**：好友列表选择，发送与接收消息
- **自动回复**：好友自动回复模拟
- **聊天记录持久化**：消息自动保存到本地 JSON 文件

## 项目结构

```
qq/
├── main.py              # 程序入口（~6行，仅启动UI）
├── config.py            # 全局常量（颜色、字体、尺寸、文件路径）
├── user_db.py           # 用户数据层（bcrypt加密 + JSON持久化）
├── chat_db.py           # 聊天记录持久化层
├── login_window.py      # 登录窗口界面
├── register_window.py   # 注册窗口界面
├── chat_window.py       # 主页/聊天窗口界面（含个人资料修改）
├── chat_record.json     # 聊天记录文件（运行时自动生成）
├── user_db.json         # 用户数据文件（运行时自动生成）
├── .gitignore           # Git 忽略规则
└── readme.md            # 项目说明
```

## 环境要求

- Python 3.8+
- 依赖库：`bcrypt`

## 快速开始

```bash
# 1. 安装依赖
pip install bcrypt

# 2. 运行
python main.py
```

### 预置测试账号

| 账号 | 密码 | 昵称 |
|------|------|------|
| 123456 | abc123 | 小明 |
| admin | admin123 | 管理员 |
| qquser | password | QQ用户 |

> 注意：预置账号使用 bcrypt 哈希占位符，首次运行请先**注册新账号**再登录。

## 架构说明

```
main.py              ← 入口，仅创建 root + 启动 QQLoginWindow
config.py            ← 无项目内依赖，被所有模块导入
user_db.py           ← 依赖 config，提供 bcrypt 加解密 + JSON 持久化
chat_db.py           ← 依赖 config，提供聊天记录 JSON 读写
register_window.py   ← 依赖 config + user_db
chat_window.py       ← 依赖 config + user_db + chat_db
login_window.py      ← 依赖 config + user_db + register_window + chat_window
```

- **高内聚**：每个模块职责单一（数据/UI/配置分离）
- **低耦合**：模块间通过明确的函数接口通信，无模块级循环导入

## 技术栈

- **GUI 框架**：Tkinter（Python 标准库）
- **密码加密**：bcrypt（12轮加盐哈希）
- **数据存储**：JSON 文件持久化

## 许可证

MIT
