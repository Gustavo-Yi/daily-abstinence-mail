from __future__ import annotations

import argparse
import json
import os
import smtplib
import ssl
import sys
from datetime import date, datetime, timedelta, timezone
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
CONTENT_PATH = SCRIPT_DIR / "traditional_abstinence_sources.jsonl"
CONTENT_START_DATE = date(2026, 6, 29)
CONTENT_END_DATE = date(2026, 12, 31)
CHINA_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")


THEME_GUIDES = {
    "戒色": {
        "lesson": "这条古训直指声色与欲念的边界。传统文化并不否认人有欲望，而是要求人以礼义、志气和清明之心驾驭欲望，不让一时色念夺走精神、时间和德行。",
        "action": "今天守住眼目与手机入口：不主动搜索、不停留观看、不在深夜独处时接触擦边或色情内容。",
    },
    "慎独": {
        "lesson": "慎独是古圣先贤反复强调的修身功夫。人在无人监督、独处一室、手机在手时，最容易看出真实定力；能在隐微处自守，才是真正把戒色落实到心上。",
        "action": "今天独处前先安排正事，把手机放到视线外；若起邪念，立刻起身换场景。",
    },
    "寡欲": {
        "lesson": "寡欲不是压坏身体，而是减少不必要的牵引。欲望越杂，心越散；心越散，志越弱。能少私寡欲，就能把精神收回到读书、做事、尽责和养德上。",
        "action": "今天减少一个会牵动欲念的入口，把省下的时间用于读书、运动或完成一件正事。",
    },
    "知止": {
        "lesson": "知止是戒色的重要关口。很多失守不是突然发生，而是明知应停却继续往前。古人讲知止、知足、不过度，正是让人在欲念刚起时守住分寸。",
        "action": "今天一旦发现自己在试探边界，就明确对自己说“到此为止”，然后离开页面或房间。",
    },
    "改过": {
        "lesson": "传统修身重在迁善改过。戒色不怕看见过失，怕的是掩饰、拖延和重复旧路。能日日知非、日日改过，失守也能变成增长定力的材料。",
        "action": "写下最近一次动念或失守前的三个诱因，今天先断其中一个。",
    },
    "自省": {
        "lesson": "自省是把心从外物拉回来的方法。戒色不是只怪环境，而是反求诸己：我在什么时刻最弱？我让什么内容进了眼耳？我有没有提前设防？",
        "action": "今天用三行文字复盘自己的眼、耳、心、行，找出一个最该修正的细节。",
    },
    "志向": {
        "lesson": "古人讲立志，是因为志气能统摄欲望。人若没有更高目标，就容易被眼前快感牵着走；志向立住，声色之诱就不容易成为生活的主人。",
        "action": "今天选一件能增长志气的事认真完成：读书半小时、运动半小时或推进一项工作。",
    },
    "节制": {
        "lesson": "节制是传统文化里的基本德目。酒色财气、饮食娱乐、手机短视频，表面不同，根上都是能否不过量、能否守分寸。戒色要从日常节制做起。",
        "action": "今天饮食、娱乐和手机使用都不过量，晚上给自己设一个清楚的停止时间。",
    },
    "养生": {
        "lesson": "医家讲养生，重在节欲、规律和精神内守。色欲失控常与熬夜、酒后、疲劳、情绪低落相连；先把起居调正，定力才有根基。",
        "action": "今晚固定睡觉时间，睡前不饮酒、不刷刺激内容，让精神先归于平稳。",
    },
    "勤学": {
        "lesson": "学问能养心，也能转移浮躁欲念。古人以读书明理、以实践成德；人有正事可做，心就不容易长期沉在声色刺激里。",
        "action": "今天读一段经典或学习一项技能三十分钟，读完写一句心得。",
    },
    "正心": {
        "lesson": "戒色的根不只在行为，更在正心。念头刚起时，若能觉察、端正、收束，后面的行为就少了许多危险。心正，则眼耳言动都有所依归。",
        "action": "欲念起时先停三次呼吸，再问自己：这件事是否损志、损德、损精神？",
    },
    "礼义": {
        "lesson": "礼义给欲望立边界。传统文化讲克己复礼，是让人尊重自己，也尊重他人，不把他人当作欲望对象，不让一念私欲破坏人格和关系。",
        "action": "今天凡遇声色诱惑，先以礼义自问：这是否合乎尊重、分寸和正道？",
    },
    "防微": {
        "lesson": "古人重视防微杜渐，因为大失守常由小放纵累积而成。第一眼、第一念、第一次点击，看似细小，正是最该设防的地方。",
        "action": "今天在欲念初起时就换场景，不等它发展成强烈冲动。",
    },
    "自胜": {
        "lesson": "胜过别人不如胜过自己。戒色真正训练的是自胜之力：欲望在场时，人仍能选择礼义、志向和长远利益，而不是被一时快感推着走。",
        "action": "今天遇到冲动时延迟十五分钟，期间走路、洗脸、整理房间或读一页书。",
    },
    "修身": {
        "lesson": "修身是中国传统文化的根本功夫。戒色不是孤立的一件事，而是整理作息、言行、朋友、环境和志向，让整个人重新归于正道。",
        "action": "今天整理一个外在环境：书桌、房间、手机首页或浏览器收藏夹。",
    },
}


def load_entries(path: Path = CONTENT_PATH) -> list[dict]:
    entries = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        if not {"id", "source", "quote"} <= set(entry):
            raise ValueError(f"Invalid content entry at line {lineno}")
        entries.append(entry)
    return entries


def infer_theme(entry: dict) -> str:
    text = f"{entry['source']} {entry['quote']}"
    if any(word in text for word in ["过量", "节饮食", "知足", "知止", "少私寡欲", "俭"]):
        return "节制"
    if any(word in text for word in ["色", "淫", "欲", "冶容"]):
        if any(word in text for word in ["欲速", "知足", "知止", "自得"]):
            return "知止"
        return "戒色"
    if any(word in text for word in ["独", "隐", "不睹", "不闻", "十目", "十手"]):
        return "慎独"
    if any(word in text for word in ["过", "改", "复", "悔", "省"]):
        return "改过"
    if any(word in text for word in ["反求", "反身", "求诸己", "三省"]):
        return "自省"
    if any(word in text for word in ["志", "弘毅", "任重", "道远", "大任"]):
        return "志向"
    if any(word in text for word in ["节", "俭", "知足", "知止", "不过", "不积", "戒"]):
        return "节制"
    if any(word in text for word in ["食", "起居", "精", "气", "病", "阴", "阳", "身", "养生"]):
        return "养生"
    if any(word in text for word in ["学", "知", "书", "问", "思", "辨", "行"]):
        return "勤学"
    if any(word in text for word in ["心", "诚", "静", "清", "素", "朴"]):
        return "正心"
    if any(word in text for word in ["礼", "义", "德", "敬", "仁"]):
        return "礼义"
    if any(word in text for word in ["微", "细", "豫", "未发", "始", "患"]):
        return "防微"
    if any(word in text for word in ["自胜", "胜人"]):
        return "自胜"
    return "修身"


def entry_for_date(day: date) -> tuple[dict, int, int]:
    entries = load_entries()
    expected_days = (CONTENT_END_DATE - CONTENT_START_DATE).days + 1
    if len(entries) < expected_days:
        raise ValueError(f"Need at least {expected_days} entries, found {len(entries)}")

    offset = (day - CONTENT_START_DATE).days
    if 0 <= offset < expected_days:
        return entries[offset], offset + 1, expected_days

    return entries[day.toordinal() % len(entries)], 0, expected_days


def build_body(now: datetime) -> str:
    entry, sequence, total = entry_for_date(now.date())
    guide = THEME_GUIDES[infer_theme(entry)]
    sequence_line = f"第 {sequence}/{total} 条" if sequence else "补充条目"

    return (
        f"{now:%Y-%m-%d}\n\n"
        "今日戒色知识（中国传统优良文化）\n\n"
        f"序号：{sequence_line}\n"
        f"依据：{entry['source']}\n"
        f"原文：{entry['quote']}\n\n"
        f"今解：{guide['lesson']}\n\n"
        f"今日功课：{guide['action']}"
    )


def send_mail(subject: str, body: str) -> None:
    smtp_user = os.environ["QQ_MAIL_USER"]
    auth_code = os.environ["QQ_MAIL_AUTH_CODE"]
    to_address = os.environ.get("QQ_MAIL_TO", smtp_user)
    from_name = os.environ.get("FROM_NAME", "每日戒色提醒")

    message = EmailMessage()
    message["From"] = formataddr((from_name, smtp_user))
    message["To"] = to_address
    message["Subject"] = subject
    message.set_content(body, subtype="plain", charset="utf-8")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.qq.com", 465, context=context, timeout=30) as smtp:
        smtp.login(smtp_user, auth_code)
        smtp.send_message(message)

    print(f"Sent '{subject}' to {to_address}")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send a daily traditional abstinence email.")
    parser.add_argument("--date", help="Override China date, format YYYY-MM-DD.")
    parser.add_argument("--dry-run", action="store_true", help="Print the email body without sending.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.date:
        current_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        now = datetime.combine(current_date, datetime.min.time(), tzinfo=CHINA_TZ)
    else:
        now = datetime.now(CHINA_TZ)

    subject = f"今日戒色知识 - {now:%Y-%m-%d}"
    body = build_body(now)

    if args.dry_run:
        print(subject)
        print()
        print(body)
        return 0

    send_mail(subject, body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
