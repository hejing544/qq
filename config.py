# -*- coding: utf-8 -*-
"""全局配置常量 — 颜色、字体、尺寸、文件路径、默认用户"""

# ====================== 颜色常量 ======================
HEADER_COLOR = "#12B7F5"
BG_COLOR = "#F5F6FA"
BTN_COLOR = "#12B7F5"
BTN_ACTIVE = "#0E9BD6"
CARD_BG = "#FFFFFF"
LOGOUT_BG = "#FF4D4F"
LOGOUT_ACTIVE = "#D9363E"

INPUT_HIGHLIGHT = HEADER_COLOR
INPUT_BORDER = "#DDDDDD"
TEXT_GRAY = "#666666"
TEXT_LIGHT_GRAY = "#999999"
TEXT_BLACK = "#333333"
ONLINE_GREEN = "#52C41A"
DIVIDER_GRAY = "#EEEEEE"

# ====================== 窗口尺寸 ======================
LOGIN_W = 380
LOGIN_H = 540
REGISTER_W = 360
REGISTER_H = 480
MAIN_W = 600
MAIN_H = 900

# ====================== 字体 ======================
FONT_TITLE = ("Microsoft YaHei", 18, "bold")
FONT_SUBTITLE = ("Microsoft YaHei", 10)
FONT_NORMAL = ("Microsoft YaHei", 11)
FONT_SMALL = ("Microsoft YaHei", 9)
FONT_BTN = ("Microsoft YaHei", 12, "bold")
FONT_LOGOUT = ("Microsoft YaHei", 11, "bold")
FONT_EMOJI = ("Segoe UI Emoji", 40)

# ====================== 文件路径 ======================
USER_DB_FILE = "user_db.json"
CHAT_FILE = "chat_record.json"
MOMENTS_FILE = "moments.json"
CHECKIN_FILE = "checkin_data.json"

# ====================== 默认用户（bcrypt 哈希，仅供首次运行） ======================
DEFAULT_USERS = {
    "123456": {
        "hash_pwd": b'$2b$12$cV8xR9w0F1N8aG7tXyKzOuJdZ7bQ5sL9mN0pR6dT',
        "nickname": "小明",
        "signature": "每一天，乐在沟通",
        "gender": "男",
        "age": "22",
        "city": "深圳",
    },
    "admin": {
        "hash_pwd": b'$2b$12$dE9sK2pQ7zR5aT8xYbN0cJdF3gH6lM4vW1eS9',
        "nickname": "管理员",
        "signature": "好好学习，天天向上",
        "gender": "男",
        "age": "25",
        "city": "北京",
    },
    "qquser": {
        "hash_pwd": b'$2b$12$fR3gT7vB9nD2zP5sC8kX0jL6hM1wQ4aE7dS2',
        "nickname": "QQ用户",
        "signature": "这个人很懒，什么都没留下",
        "gender": "女",
        "age": "20",
        "city": "上海",
    },
}
