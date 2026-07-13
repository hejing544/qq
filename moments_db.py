# -*- coding: utf-8 -*-
"""动态（QQ空间/朋友圈）数据持久化层 — JSON 文件读写"""
import json
import os
import shutil
from datetime import datetime

from config import MOMENTS_FILE, MOMENTS_VIDEOS_DIR


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


def _save_video_file(src_video_path: str) -> str:
    """将选中的视频文件复制到 moments_videos/ 目录，返回相对路径"""
    if not src_video_path or not os.path.isfile(src_video_path):
        return ""
    os.makedirs(MOMENTS_VIDEOS_DIR, exist_ok=True)
    ext = os.path.splitext(src_video_path)[1] or ".mp4"
    dest_name = f"{int(datetime.now().timestamp() * 1000)}{ext}"
    dest_path = os.path.join(MOMENTS_VIDEOS_DIR, dest_name)
    shutil.copy2(src_video_path, dest_path)
    return dest_path


def delete_video_file(video_path: str):
    """删除关联的视频文件"""
    if video_path and os.path.isfile(video_path):
        try:
            os.remove(video_path)
        except OSError:
            pass


def add_moment(account: str, nickname: str, avatar: str, content: str,
               video_path: str = "") -> dict:
    """添加一条新动态，返回新创建的动态字典"""
    moments = load_moments_data()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    saved_video = _save_video_file(video_path) if video_path else ""
    new_moment = {
        "id": str(int(datetime.now().timestamp() * 1000)),
        "account": account,
        "nickname": nickname,
        "avatar": avatar,
        "content": content.strip(),
        "time": now,
        "likes": 0,
        "liked_accounts": [],  # 记录点赞的账号列表，防止重复点赞
        "video": saved_video,  # 视频相对路径，空字符串表示无视频
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
            # 同时删除关联的视频文件
            delete_video_file(m.get("video", ""))
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