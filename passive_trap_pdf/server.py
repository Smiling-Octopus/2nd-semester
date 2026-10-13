#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
추적 로그 수집 서버 (실전판)
- /track : JS 디바이스 지문 수신 (Acrobat 계열)
- /pixel : 이미지 로드 트랩 수신 (모든 PDF 뷰어)
- 응답으로 항상 1x1 투명 GIF를 반환 → 어떤 뷰어에서도 오류 없이 렌더링됨

실행:  pip install flask && python3 server.py
확인:  tail -f track.log
"""

import struct
from datetime import datetime, timezone
from flask import Flask, request

app = Flask(__name__)
LOG_FILE = "track.log"

GIF_1x1 = (
    b"GIF89a" + struct.pack("<HH", 1, 1)
    + bytes([0x80, 0, 0, 0]) + bytes([0, 0, 0])
    + b"\x21\xF9\x04\x01\x00\x00\x00\x00"
    + b"\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3B"
)


def log(kind, req):
    line = (
        f"[{datetime.now(timezone.utc).isoformat()}] kind={kind} "
        f"ip={req.headers.get('X-Forwarded-For', req.remote_addr)} "
        f"ua={req.headers.get('User-Agent', '-')} "
        f"params={dict(req.args)}\n"
    )
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


@app.route("/track")
def track():
    log("JS_FINGERPRINT", request)
    return GIF_1x1, 200, {"Content-Type": "image/gif",
                          "Cache-Control": "no-store"}


@app.route("/pixel")
def pixel():
    log("IMAGE_TRAP", request)
    return GIF_1x1, 200, {"Content-Type": "image/gif",
                          "Cache-Control": "no-store"}


if __name__ == "__main__":
    print("수집 서버 시작: http://0.0.0.0:5000  (track.log 기록 중)")
    app.run(host="0.0.0.0", port=5000)
