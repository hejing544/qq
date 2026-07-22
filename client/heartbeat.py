# -*- coding: utf-8 -*-
"""心跳模块 — 定时向服务端上报在线状态"""
import threading
import urllib.request
import json
import time

# 服务端地址（可修改为实际服务器地址）
SERVER_URL = "http://localhost:3000"

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 30


class Heartbeat:
    """后台心跳线程，定时 POST /api/heartbeat 上报在线状态"""

    def __init__(self, account: str, nickname: str):
        self.account = account
        self.nickname = nickname
        self._running = False
        self._thread = None

    def start(self):
        """启动心跳线程"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        print(f"[心跳] 已启动 ({self.account})")

    def stop(self):
        """停止心跳线程"""
        self._running = False
        # 发送一次下线通知（带特殊标记，服务端可立即标记离线）
        try:
            self._send_offline()
        except Exception:
            pass
        print(f"[心跳] 已停止 ({self.account})")

    def _send_offline(self):
        """发送下线通知"""
        req = urllib.request.Request(
            f"{SERVER_URL}/api/heartbeat/offline",
            data=json.dumps({"account": self.account}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=3)

    def _send_heartbeat(self):
        """发送一次心跳"""
        req = urllib.request.Request(
            f"{SERVER_URL}/api/heartbeat",
            data=json.dumps({
                "account": self.account,
                "nickname": self.nickname
            }).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        urllib.request.urlopen(req, timeout=5)

    def _loop(self):
        """心跳循环"""
        while self._running:
            try:
                self._send_heartbeat()
            except Exception as e:
                print(f"[心跳] 发送失败: {e}")
            # 等待 HEARTBEAT_INTERVAL 秒，期间每秒检查 _running 状态
            for _ in range(HEARTBEAT_INTERVAL):
                if not self._running:
                    break
                time.sleep(1)
