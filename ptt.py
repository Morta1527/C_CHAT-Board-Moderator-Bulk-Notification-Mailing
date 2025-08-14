#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
import sys
import re
import PyPtt
from pathlib import Path
from typing import List, Set, Tuple, Dict

CONFIG_PATH = Path(__file__).with_name("config.json")
MAIL_LIST_PATH = Path("mail_group.txt")  # s 選項匯出的 ID 名單（每行一個帳號）

def load_config(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"找不到設定檔：{path}")
    with path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    required = ["PTT_ID", "PTT_PW", "BOARD", "PUSH_TEXT"]
    for k in required:
        if cfg.get(k) in [None, ""]:
            raise ValueError(f"設定檔缺少必要欄位：{k}")
    return cfg

def parse_index_range(r: str) -> List[int]:
    if not r:
        return []
    r = r.strip()
    if "-" not in r:
        try:
            return [int(r)]
        except:
            raise ValueError(f"INDEX_RANGE 格式錯誤：{r}")
    a, b = r.split("-", 1)
    a, b = a.strip(), b.strip()
    if not a.isdigit() or not b.isdigit():
        raise ValueError(f"INDEX_RANGE 必須是 'start-end'，收到：{r}")
    s, e = int(a), int(b)
    if s <= 0 or e <= 0 or e < s:
        raise ValueError(f"INDEX_RANGE 數值錯誤：{r}")
    return list(range(s, e + 1))

def comment_type_from_text(name: str) -> PyPtt.CommentType:
    name = (name or "PUSH").upper()
    mapping = {
        "PUSH": PyPtt.CommentType.PUSH,
        "BOO": PyPtt.CommentType.BOO,
        "ARROW": PyPtt.CommentType.ARROW,
    }
    if name not in mapping:
        raise ValueError(f"COMMENT_TYPE 不支援：{name}（可用：PUSH/BOO/ARROW）")
    return mapping[name]

def sleep_between(sec: int = 3):   
    print(f"休息 {sec} 秒以避免過於頻繁...")
    time.sleep(sec)

def fetch_post_info(api: PyPtt.API, board: str, index: int) -> Dict[str, str]:
    """
    回傳 {'index', 'author', 'date', 'title'}；若抓取失敗，會丟出例外由上層處理。
    PyPtt.get_post() 回傳 dict，常見鍵值：'author', 'date', 'title', 'content', 'comments', ...
    """
    post = api.get_post(board=board, index=index)
    author = str(post.get("author", "")).strip()
    date   = str(post.get("date", "")).strip()     # PTT 文章頁上的時間字串
    title  = str(post.get("title", "")).strip()
    return {
        "index": str(index),
        "author": author or "(未知作者)",
        "date": date or "(未知時間)",
        "title": title or "(無標題)"
    }

def preview_targets(api: PyPtt.API, board: str, indices: List[int]) -> List[Dict[str, str]]:
    """
    逐一抓取文章資訊，組成預覽清單（成功的才列入）。
    若某篇抓取失敗，會印出警告並略過那篇。
    """
    print("\n=== 預覽即將推文的文章 ===")
    rows: List[Dict[str, str]] = []
    for idx in sorted(indices):
        try:
            info = fetch_post_info(api, board, idx)
            rows.append(info)
        except PyPtt.exceptions.NoPermission:
            print(f"[警告] 無權限存取：[{board}] index={idx}（NoPermission），略過。", file=sys.stderr)
        except Exception as e:
            print(f"[警告] 無法取得文章：[{board}] index={idx}，原因：{e}，略過。", file=sys.stderr)

    if not rows:
        print("（沒有可預覽的文章，將無法進行推文）")
        return []

    # 簡易表格輸出
    print(f"\n看板：{board}，共 {len(rows)} 筆")
    print("-" * 120)
    print(f"{'Index':<8} {'作者':<16} {'時間':<24} 標題")
    print("-" * 120)
    for r in rows:
        author = (r['author'][:14] + '…') if len(r['author']) > 15 else r['author']
        date   = (r['date'][:22] + '…') if len(r['date']) > 23 else r['date']
        title  = r['title']
        print(f"{r['index']:<8} {author:<16} {date:<24} {title}")
    print("-" * 120)
    return rows

def confirm_to_proceed() -> str:
    ans = input("以上為將要推文的文章清單，是否繼續執行推文？(y=推文 / n=取消 / s=匯出被檢舉ID)：").strip().lower()
    if ans in ("y", "n", "s"):
        return ans
    return "n"


def do_comment(api: PyPtt.API, board: str, index: int, content: str,
               ctype: PyPtt.CommentType, skip_if_same: bool,
               retry_on_fast: bool, retry_max: int, backoff_base: int):
    # 先抓文，視需要檢查是否已有相同留言
    post = api.get_post(board=board, index=index)
    print(f"取得文章成功：[{board}] index={index}")

    if skip_if_same:
        comments = post.get("comments", [])
        if any((c.get("content", "").strip() == content.strip()) for c in comments):
            print("偵測到相同內容已存在；依設定 SKIP_IF_SAME_EXISTS=True → 略過。")
            return

    attempt = 0
    while True:
        try:
            api.comment(board=board, comment_type=ctype, content=content, index=index)
            print(f"已推文：[{board}] index={index} → {content}")
            return
        except PyPtt.exceptions.NoFastComment:
            attempt += 1
            if not retry_on_fast or attempt > retry_max:
                raise
            wait_s = backoff_base * (2 ** (attempt - 1))
            print(f"推文過於頻繁（NoFastComment），第 {attempt} 次退避 {wait_s} 秒後重試...")
            time.sleep(wait_s)

def extract_report_id_from_title(title: str):
    """從標題擷取 [檢舉] <ID> 4-XX 的 <ID>，不符則回 None"""
    if not title:
        return None
    m = re.match(r'^\[檢舉\]\s+([A-Za-z0-9_]+)\s+4-(\d+)\b', title.strip())
    return m.group(1) if m else None

def export_ids_to_file(ids: list[str]):
    """將擷取到的 ID 清單匯出到檔案（覆蓋寫入）。"""
    uniq = sorted(set(x.strip() for x in ids if x and x.strip()))
    with MAIL_LIST_PATH.open("w", encoding="utf-8") as f:
        for x in uniq:
            f.write(x + "\n")
    print(f"已匯出 {len(uniq)} 個 ID 到 {MAIL_LIST_PATH.name}")

def load_mail_list(path: Path = MAIL_LIST_PATH) -> list[str]:
    """讀取寄信名單，一行一個 ID；自動去重、過濾空白行。"""
    try:
        with path.open("r", encoding="utf-8") as f:
            ids = [ln.strip() for ln in f if ln.strip()]
    except FileNotFoundError:
        print(f"[錯誤] 找不到 {path}，請先用 s 選項匯出名單或確認路徑。")
        return []
    # 去重並保持原有順序
    seen = set()
    uniq = []
    for x in ids:
        if x not in seen:
            seen.add(x)
            uniq.append(x)
    return uniq

def preview_mail_targets(ids: list[str]) -> None:
    """在畫面預覽收件人名單。"""
    print("\n=== 郵件收件人預覽 ===")
    if not ids:
        print("(名單為空)")
        return
    for i, uid in enumerate(ids, 1):
        print(f"{i:>3}. {uid}")
    print(f"—— 共 {len(ids)} 位 ——")

def send_bulk_mail(api, ids: list[str], title: str, body: str, interval_sec: int = 3) -> None:
    """逐一寄信（固定間隔），成功/失敗顯示在畫面，不輸出檔案。"""
    if not ids:
        print("沒有收件人，已取消寄信。")
        return
    ok = 0
    fail = 0
    print("\n=== 開始寄送 ===")
    for idx, uid in enumerate(ids, 1):
        try:
            api.mail(ptt_id=uid, title=title, content=body)  # 可選：sign_file=0, backup=True
            ok += 1
            print(f"[{idx}/{len(ids)}] ✅ 已寄出：{uid}")
        except PyPtt.exceptions.NoSuchUser:
            fail += 1
            print(f"[{idx}/{len(ids)}] ❌ 失敗（使用者不存在）：{uid}")
        except PyPtt.exceptions.UnregisteredUser:
            fail += 1
            print(f"[{idx}/{len(ids)}] ❌ 失敗（未註冊或停權）：{uid}")
        except Exception as e:
            fail += 1
            print(f"[{idx}/{len(ids)}] ❌ 寄給 {uid} 失敗：{e}")
        time.sleep(interval_sec)  # 固定 3 秒間隔
    print(f"=== 完成：成功 {ok}、失敗 {fail} ===\n")

def ptt_newlines(s: str) -> str:
    # 去掉 UTF-8 BOM（若有）
    s = s.lstrip("\ufeff")
    # 先統一成 LF
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # 再把 LF 改成 CR（PTT 編輯器偏好 CR）
    s = s.replace("\n", "\r")
    # 保證最後有一個換行，避免最後一行被接在上一行後面
    if not s.endswith("\r"):
        s += "\r"
    return s


def main():
    cfg = load_config(CONFIG_PATH)

    ptt_id = cfg["PTT_ID"]
    ptt_pw = cfg["PTT_PW"]
    board  = cfg["BOARD"].strip()
    push_text = (cfg["PUSH_TEXT"] or "").strip()
    if not push_text:
        raise ValueError("PUSH_TEXT 不能為空")

    ctype = comment_type_from_text(cfg.get("COMMENT_TYPE"))

    # 任務列表：由 INDEX_RANGE 與 INDEX_LIST 合併去重
    index_set: Set[int] = set()
    index_set.update(parse_index_range(cfg.get("INDEX_RANGE", "")))
    for x in (cfg.get("INDEX_LIST") or []):
        if not isinstance(x, int) or x <= 0:
            raise ValueError(f"INDEX_LIST 內含非法值：{x}")
        index_set.add(x)

    if not index_set:
        raise ValueError("請至少透過 INDEX_RANGE 或 INDEX_LIST 指定一篇以上的 index")

    skip_if_same    = bool(cfg.get("SKIP_IF_SAME_EXISTS", False))  # 你要允許重複 → 預設 False
    sleep_min = int(cfg.get("SLEEP_SECONDS_MIN", 6))
    sleep_max = int(cfg.get("SLEEP_SECONDS_MAX", 12))
    if sleep_min < 0 or sleep_max < sleep_min:
        raise ValueError("SLEEP_SECONDS_MIN/MAX 設定不合理")

    retry_on_fast   = bool(cfg.get("RETRY_ON_FAST", True))
    retry_max       = int(cfg.get("RETRY_MAX", 3))
    backoff_base    = int(cfg.get("RETRY_BACKOFF_BASE", 8))

    api = PyPtt.API()
    try:
        api.login(ptt_id=ptt_id, ptt_pw=ptt_pw, kick_other_session=True)
        print(f"登入成功：{ptt_id}")

        targets = sorted(index_set)

        # === 新增：推文前預覽 & 確認 ===
        preview_rows = preview_targets(api, board, targets)
        if not preview_rows:
            print("沒有可推文的目標（預覽失敗或全數略過），結束。")
            return

        choice = confirm_to_proceed()
        if choice == "n":
            print("使用者取消推文。")
            return
        elif choice == "s":
            ids = []
            for row in preview_rows:
                tid = extract_report_id_from_title(row["title"])
                if tid:
                    ids.append(tid)

            if ids:
                export_ids_to_file(ids)
                print("已匯出 ID 名單，不進行推文。")
            else:
                print("沒有任何符合『[檢舉] <ID> 4-XX』格式的標題，未匯出。")
            # 2) 不結束！讓使用者決定下一步
            #    m=寄信（之後會串接寄信流程）、y=推文、n=取消
            choice = input("下一步？(m=寄信 / y=推文 / n=取消)：").strip().lower()
            if choice == "n":
                print("使用者取消。")
                return
        # choice 會在下面繼續判斷

        # 確認後開始逐篇推文（choice == 'y'）
        if choice == "y":
            for idx in targets:
                try:
                    do_comment(api, board, idx, push_text, ctype,
                            skip_if_same, retry_on_fast, retry_max, backoff_base)
                except PyPtt.exceptions.NoPermission:
                    print(f"[警告] 無權限在 {board} index={idx} 推文（NoPermission），已略過。", file=sys.stderr)
                except PyPtt.exceptions.NoFastComment:
                    print(f"[錯誤] {board} index={idx} 推文過於頻繁且重試上限已到，請放慢速度或稍後再試。", file=sys.stderr)
                except Exception as e:
                    print(f"[錯誤] {board} index={idx} 推文失敗：{e}", file=sys.stderr)

                # 兩篇之間休息（固定 3 秒）
                sleep_between(3)
        elif choice == "m":
            # 讀名單
            ids = load_mail_list()  # 預設讀 mail_group.txt
            preview_mail_targets(ids)
            if not ids:
                return

            # 顯示並二次確認
            go = input("確認要寄出嗎？(y/N)：").strip().lower()
            if go != "y":
                print("已取消寄信。")
                return

            # 從 config 取得標題/內文；若沒有就當場詢問
        mail_title = (cfg.get("MAIL_TITLE") or "").strip()
        if not mail_title:
            mail_title = input("請輸入郵件標題：").strip()
        
        mail_body_file = cfg.get("MAIL_BODY_FILE")
        mail_body = ""

        if mail_body_file:
            try:
                mail_body = Path(mail_body_file).read_text(encoding="utf-8")
            except FileNotFoundError:
                print(f"[警告] 找不到 {mail_body_file}，改用其他來源。")

        mail_body_to_send = ptt_newlines(mail_body)
        print("\n=== 郵件預覽 ===")
        print(mail_title)
        print("-" * 40)
        print(mail_body)
        print("-" * 40)
        go2 = input("以上為寄出的內容，是否寄出？(y/N)：").strip().lower()
        if go2 != "y":
            print("已取消寄信。")
            return

        # 寄送
        send_bulk_mail(api, ids, mail_title, mail_body_to_send, interval_sec=3)
        # 結束後直接返回 main()，照你的程式流程會接著 logout()
        return

    finally:
        try:
            api.logout()
            print("已登出。")
        except Exception:
            pass
if __name__ == "__main__":
    main()

