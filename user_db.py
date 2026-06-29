# -*- coding: utf-8 -*-
"""
用户数据库模块
模拟用户数据存储，实际项目中应替换为真实的数据库或接口调用
"""

# ---------- 模拟的用户数据库 ----------
# 每个账号存储：密码、昵称、签名、性别、年龄等信息
USER_DB = {
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
    """添加新用户

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
    return USER_DB[account]