# QQ 桌面版

基于 Python + Tkinter 的 QQ 桌面客户端 + Vue 服务端管理面板。

## 项目结构

```
qq/
├── client/                   # QQ 桌面客户端（Python + Tkinter）
│   ├── main.py               # 程序入口
│   ├── config.py             # 全局常量（颜色、字体、尺寸、文件路径）
│   ├── theme.py              # 日/夜间主题切换
│   ├── user_db.py            # 用户数据层（bcrypt 加密 + JSON 持久化）
│   ├── chat_db.py            # 聊天记录持久化层
│   ├── friends_db.py         # 好友数据管理
│   ├── group_db.py           # 群组数据管理
│   ├── moments_db.py         # 朋友圈数据管理
│   ├── checkin_db.py         # 签到数据管理
│   ├── login_window.py       # 登录窗口界面
│   ├── register_window.py    # 注册窗口界面
│   ├── chat_window.py        # 主页/聊天窗口界面
│   ├── qq_login.py           # QQ 登录逻辑
│   └── fix_qq.py             # 修复工具
│
├── srv/                      # 服务端管理面板（Node.js + Vue 3）
│   ├── server.js             # Express REST API + WebSocket 服务
│   ├── package.json          # Node.js 依赖配置
│   ├── vite.config.js        # Vite 构建配置
│   ├── index.html            # HTML 入口
│   ├── src/
│   │   ├── main.js           # Vue 应用入口
│   │   ├── App.vue           # 主布局（Tab 导航）
│   │   └── components/
│   │       └── UserList.vue  # 用户列表组件
│   └── data/
│       └── user_db.json      # 服务端用户数据
│
├── .gitignore                # Git 忽略规则
└── README.md                 # 项目说明
```

## 功能特性

### 客户端（client）

- **用户登录**：支持账号密码登录，记住密码与自动登录选项
- **用户注册**：新账号在线注册，支持昵称设置与密码确认
- **个人主页**：展示用户头像、昵称、个性签名、性别、年龄、城市等信息
- **个人资料修改**：支持修改头像、昵称、性别、年龄、城市、个性签名
- **即时聊天**：好友列表选择，发送与接收消息
- **群聊功能**：创建群组、群聊消息
- **朋友圈**：发布文字、照片、视频动态
- **签到功能**：每日签到打卡
- **日夜间模式**：支持亮色/暗色主题切换
- **自动回复**：好友自动回复模拟
- **聊天记录持久化**：消息自动保存到本地 JSON 文件

### 服务端（srv）

- **REST API**：用户注册、登录、信息查询与修改
- **WebSocket**：实时推送用户上下线、注册等事件
- **管理面板**：Vue 3 构建的 Web 后台，Tab 页展示：
  - 👥 用户管理 — 表格展示所有注册用户，支持搜索、分页、详情查看、删除
  - 📊 数据统计 — 注册总数、在线连接、性别分布、城市分布
  - 📡 API 文档 — 接口列表与方法说明
- **实时日志**：底部日志栏滚动显示服务端事件

## 环境要求

### 客户端

- Python 3.8+
- 依赖：`bcrypt`, `tkinter`（Python 标准库自带）

### 服务端

- Node.js 18+
- npm 或 yarn

## 快速开始

### 1. 启动客户端

```bash
cd client
pip install bcrypt
python main.py
```

### 2. 启动服务端

```bash
cd srv
npm install
npm run dev        # 开发模式（Vite 热更新 + Express API）
# 或
npm run build      # 构建前端
npm start          # 生产模式（Express 同时服务 API 和静态页面）
```

启动后访问：http://localhost:3000 打开管理面板，或 http://localhost:5173 进行前端开发。

### 预置测试账号

| 账号 | 密码 | 昵称 |
|------|------|------|
| 123456 | 123456 | 小明 |
| admin | admin | 管理员 |
| qquser | qquser | QQ用户 |

## 服务端 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/users` | 获取所有注册用户 |
| GET | `/api/users/:account` | 获取指定用户 |
| POST | `/api/register` | 注册新用户 `{account, nickname, password}` |
| POST | `/api/login` | 登录验证 `{account, password}` |
| PUT | `/api/users/:account` | 更新用户资料 |
| DELETE | `/api/users/:account` | 删除用户 |
| GET | `/api/stats` | 获取服务统计 |
| WS | `ws://localhost:3000` | WebSocket 实时推送 |

## 技术栈

- **客户端 GUI**：Tkinter（Python 标准库）
- **密码加密**：bcrypt（12 轮加盐哈希）
- **数据存储**：JSON 文件持久化
- **后端服务**：Express.js + WebSocket（ws）
- **前端面板**：Vue 3 + Vite
- **主题系统**：日间/夜间模式动态切换

## 许可证

MIT
