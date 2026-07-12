# -*- coding: utf-8 -*-
"""打卡数据持久化层 — JSON 文件读写"""
import json
import os
from datetime import datetime, date, timedelta

from config import CHECKIN_FILE


def load_checkin_data():
    """从本地文件读取所有打卡记录，文件不存在返回空字典"""
    if os.path.exists(CHECKIN_FILE):
        with open(CHECKIN_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_checkin_data(data: dict):
    """将所有打卡记录保存到本地 JSON 文件"""
    with open(CHECKIN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def do_checkin(account: str) -> dict:
    """执行打卡操作，返回包含今日状态的结果字典"""
    data = load_checkin_data()
    if account not in data:
        data[account] = {
            "records": [],       # 打卡日期列表 ["2026-07-13", ...]
            "streak": 0,         # 连续打卡天数
            "total": 0,          # 总打卡次数
        }

    today_str = date.today().isoformat()

    # 如果今天已经打过卡，直接返回
    if today_str in data[account]["records"]:
        return {
            "checked_in": True,
            "already": True,
            "streak": data[account]["streak"],
            "total": data[account]["total"],
            "records": data[account]["records"],
        }

    # 计算连续打卡天数
    records = data[account]["records"]
    if records:
        last_date_str = records[-1]
        last_date = date.fromisoformat(last_date_str)
        today = date.today()
        # 如果上次打卡是昨天或今天（今天已排除），则连续
        if (today - last_date).days == 1:
            data[account]["streak"] += 1
        else:
            data[account]["streak"] = 1
    else:
        data[account]["streak"] = 1

    data[account]["records"].append(today_str)
    data[account]["total"] += 1
    save_checkin_data(data)

    return {
        "checked_in": True,
        "already": False,
        "streak": data[account]["streak"],
        "total": data[account]["total"],
        "records": data[account]["records"],
    }


def get_checkin_status(account: str) -> dict:
    """获取打卡状态，不执行打卡"""
    data = load_checkin_data()
    if account not in data:
        return {
            "checked_in": False,
            "streak": 0,
            "total": 0,
            "records": [],
        }

    today_str = date.today().isoformat()
    records = data[account]["records"]
    checked_in = today_str in records

    return {
        "checked_in": checked_in,
        "streak": data[account].get("streak", 0),
        "total": data[account].get("total", 0),
        "records": records,
    }


def get_month_records(account: str, year: int, month: int) -> list:
    """获取某个月的打卡记录，返回该月所有打卡日期列表"""
    data = load_checkin_data()
    if account not in data:
        return []
    records = data[account].get("records", [])
    prefix = f"{year:04d}-{month:02d}"
    return [r for r in records if r.startswith(prefix)]