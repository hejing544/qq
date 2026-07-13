# -*- coding: utf-8 -*-
"""聊天记录持久化层 — JSON 文件读写，支持跨账号互发消息"""
import json
import os
from datetime import datetime
from shutil import copy2

from config import CHAT_FILE

CHAT_MEDIA_DIR = "chat_media"


def load_chat_data():
    """从本地文件读取聊天记录，文件不存在返回空字典"""
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_chat_data(chat_dict):
    """将聊天记录保存到本地 JSON 文件"""
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_dict, f, ensure_ascii=False, indent=2)


def get_conversation_key(account1: str, account2: str) -> str:
    """生成排序后的聊天会话键，确保两个账号无论顺序都能对应到同一会话"""
    accounts = sorted([account1, account2])
    return f"{accounts[0]}-{accounts[1]}"


def send_message(sender_account: str, sender_nickname: str, target_account: str,
                 content: str = "", photo_path: str = "", video_path: str = "") -> dict:
    """发送一条消息并保存到文件，返回消息字典。
    支持 content（文本）、photo_path（图片路径）、video_path（视频路径）"""
    key = get_conversation_key(sender_account, target_account)
    chat_data = load_chat_data()
    if key not in chat_data:
        chat_data[key] = []
    msg = {
        "sender_account": sender_account,
        "sender_nickname": sender_nickname,
        "content": content,
        "time": datetime.now().strftime("%H:%M"),
    }
    # 处理图片 - 只记录文件名
    if photo_path and os.path.isfile(photo_path):
        try:
            os.makedirs(CHAT_MEDIA_DIR, exist_ok=True)
            ext = os.path.splitext(photo_path)[1] or ".jpg"
            dest_name = f"{int(datetime.now().timestamp() * 1000)}{ext}"
            dest_path = os.path.join(CHAT_MEDIA_DIR, dest_name)
            copy2(photo_path, dest_path)
            msg["photo"] = dest_path
        except Exception:
            pass
    # 处理视频
    if video_path and os.path.isfile(video_path):
        try:
            os.makedirs(CHAT_MEDIA_DIR, exist_ok=True)
            ext = os.path.splitext(video_path)[1] or ".mp4"
            dest_name = f"{int(datetime.now().timestamp() * 1000)}{ext}"
            dest_path = os.path.join(CHAT_MEDIA_DIR, dest_name)
            copy2(video_path, dest_path)
            msg["video"] = dest_path
        except Exception:
            pass
    chat_data[key].append(msg)
    save_chat_data(chat_data)
    return msg


def load_conversation(account1: str, account2: str) -> list:
    """加载两个账号之间的聊天记录，返回消息列表"""
    key = get_conversation_key(account1, account2)
    chat_data = load_chat_data()
    return chat_data.get(key, [])