# -*- coding: utf-8 -*-
"""动态（QQ空间/朋友圈）数据持久化层 — JSON 文件读写"""
import json
import os
from datetime import datetime

from config import MOMENTS_FILE


def load_moments_data():
    """从本地文件读取所有动态，文件不存在返回空列表"""
    if os.path.exists(MOMENTS_FILE):
        with open(MOMENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_moments_data(moments_list: list):
    """将所有动态保存到本地 JSON 文件"""
    with open(MOMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(moments_list, f, ensure_ascii=False, indent=2)


def add_moment(account: str, nickname: str, avatar: str, content: str) -> dict:
    """添加一条新动态，返回新创建的动态字典"""
    moments = load_moments_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_moment = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "account": account,
        "nickname": nickname,
        "avatar": avatar,
        "content": content.strip(),
        "time": now,
        "likes": 0,
        "liked_accounts": [],  # 记录点赞的账号列表，防止重复点赞
    }
    # 最新动态插到最前面
    moments.insert(0, new_moment)
    save_moments_data(moments)
    return new_moment


def delete_moment(moment_id: str, account: str) -> bool:
    """删除指定动态（仅作者可删），成功返回 True"""
    moments = load_moments_data()
    for i, m in enumerate(moments):
        if m["id"] == moment_id and m["account"] == account:
            moments.pop(i)
            save_moments_data(moments)
            return True
    return False


def toggle_like_moment(moment_id: str, account: str) -> dict:
    """点赞/取消点赞，返回更新后的动态字典，不存在返回 None"""
    moments = load_moments_data()
    for m in moments:
        if m["id"] == moment_id:
            if "liked_accounts" not in m:
                m["liked_accounts"] = []
            if account in m["liked_accounts"]:
                # 已点赞 → 取消点赞
                m["liked_accounts"].remove(account)
                m["likes"] = len(m["liked_accounts"])
            else:
                # 未点赞 → 点赞
                m["liked_accounts"].append(account)
                m["likes"] = len(m["liked_accounts"])
            save_moments_data(moments)
            return m
    return None