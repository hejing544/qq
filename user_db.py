# -*- coding: utf-8 -*-
"""用户数据层 — bcrypt 密码加密 + JSON 文件持久化"""
import json
import os
import bcrypt

from config import USER_DB_FILE, DEFAULT_USERS


def _load_user_db():
    """从 JSON 文件加载用户数据库，文件不存在或损坏时使用默认数据"""
    if os.path.exists(USER_DB_FILE):
        try:
            with open(USER_DB_FILE, "r", encoding="utf-8") as f:
                raw = json.load(f)
            db = {}
            for account, info in raw.items():
                info["hash_pwd"] = info["hash_pwd"].encode("utf-8")
                db[account] = info
            return db
        except Exception:
            try:
                os.remove(USER_DB_FILE)
            except Exception:
                pass
    return {account: dict(info) for account, info in DEFAULT_USERS.items()}


def _save_user_db():
    """将当前 USER_DB 保存到 JSON 文件"""
    to_save = {}
    for account, info in USER_DB.items():
        saved = dict(info)
        saved["hash_pwd"] = saved["hash_pwd"].decode("utf-8")
        to_save[account] = saved
    with open(USER_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(to_save, f, ensure_ascii=False, indent=2)


# ---------- 全局用户数据库（模块加载时初始化） ----------
USER_DB = _load_user_db()


# ---------- 密码相关 ----------

def hash_password(raw_pwd: str) -> bytes:
    """对明文密码进行 bcrypt 哈希"""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(raw_pwd.encode("utf-8"), salt)


def verify_password(raw_pwd: str, stored_hash: bytes) -> bool:
    """验证密码是否匹配"""
    try:
        return bcrypt.checkpw(raw_pwd.encode("utf-8"), stored_hash)
    except Exception:
        return False


# ---------- 用户查询 ----------

def get_user_info(account: str):
    """获取用户完整信息，不存在返回 None"""
    return USER_DB.get(account, None)


def account_exists(account: str) -> bool:
    """检查账号是否已注册"""
    return account in USER_DB


# ---------- 用户创建 ----------

def create_user(account: str, nickname: str, raw_pwd: str):
    """注册新用户，自动保存到文件"""
    USER_DB[account] = {
        "hash_pwd": hash_password(raw_pwd),
        "nickname": nickname,
        "signature": "这个人很懒，什么都没留下",
        "gender": "保密",
        "age": "未知",
        "city": "未知",
    }
    _save_user_db()


# ---------- 用户资料修改 ----------

def save_level_stars(account: str, stars: int):
    """保存用户的QQ等级星星数"""
    if account in USER_DB:
        USER_DB[account]["level_stars"] = stars
        _save_user_db()


def update_user_info(account: str, **kwargs):
    """更新用户资料字段，自动保存到文件。返回更新后的用户信息，账号不存在返回 None"""
    if account not in USER_DB:
        return None
    for key, value in kwargs.items():
        USER_DB[account][key] = value
    _save_user_db()
    return USER_DB[account]
