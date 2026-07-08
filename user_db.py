# -*- coding: utf-8 -*-
"""
用户数据库模块
模拟用户数据存储，支持 JSON 文件持久化
"""
import json
import os

# ---------- 文件路径 ----------
USER_DB_FILE = "user_db.json"

# ---------- 默认用户数据（首次运行时使用） ----------
DEFAULT_USERS = {
    "123456": {
        "password": "abc123",
        "nickname": "小明",
        "signature": "每一天，乐在沟通",
        "gender": "男",
        "age": "22",
        "city": "深圳",
    },
    "admin": {
        "password": "admin123",
        "nickname": "管理员",
        "signature": "好好学习，天天向上",
        "gender": "男",
        "age": "25",
        "city": "北京",
    },
    "qquser": {
        "password": "password",
        "nickname": "QQ用户",
        "signature": "这个人很懒，什么都没留下",
        "gender": "女",
        "age": "20",
        "city": "上海",
    },
}


def _load_user_db():
    """从 JSON 文件加载用户数据库，文件不存在时使用默认数据"""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            # 文件损坏时删除并回退到默认数据
            try:
                os.remove(USER_DB_FILE)
            except Exception:
                pass
    # 深拷贝默认数据
    return {account: dict(info) for account, info in DEFAULT_USERS.items()}


def save_user_db():
    """将当前用户数据库保存到 JSON 文件"""
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(USER_DB, f, ensure_ascii=False, indent=2)


# ---------- 全局用户数据库（模块加载时从文件读取） ----------
USER_DB = _load_user_db()


# ---------- 对外接口 ----------

def verify_user(account, password):
    """验证用户账号和密码

    Args:
        account: 账号
        password: 密码

    Returns:
        验证成功返回用户信息字典，失败返回 None
    """
    if account in USER_DB and USER_DB[account]["password"] == password:
        return USER_DB[account]
    return None


def user_exists(account):
    """检查账号是否已存在

    Args:
        account: 账号

    Returns:
        存在返回 True，否则返回 False
    """
    return account in USER_DB


def add_user(account, password, nickname):
    """添加新用户（自动保存到文件）

    Args:
        account: 账号
        password: 密码
        nickname: 昵称

    Returns:
        新创建的用户信息字典
    """
    USER_DB[account] = {
        "password": password,
        "nickname": nickname,
        "signature": "这个人很懒，什么都没留下",
        "gender": "保密",
        "age": "未知",
        "city": "未知",
    }
    save_user_db()
    return USER_DB[account]


def update_user_info(account, **kwargs):
    """更新用户资料（自动保存到文件）

    Args:
        account: 账号
        **kwargs: 要更新的字段，如 nickname, gender, age, city, signature, avatar

    Returns:
        更新后的用户信息字典，账号不存在返回 None
    """
    if account not in USER_DB:
        return None
    for key, value in kwargs.items():
        USER_DB[account][key] = value
    save_user_db()
    return USER_DB[account]
