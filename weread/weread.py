#!/usr/bin/env python3
"""微信读书 CLI — 统一命令行接口。

用法:
  weread.py search <keyword> [--scope 10] [--page 1] [--per-page 10]
  weread.py shelf [--page 1] [--per-page 10]
  weread.py book <bookId> [--chapters] [--progress]
  weread.py notes [--book <bookId>] [--page 1] [--per-page 10]
  weread.py readdata [--mode monthly] [--time 0]
  weread.py review <bookId> [--type 0] [--page 1] [--per-page 10]
  weread.py discover [--book <bookId>] [--page 1] [--per-page 10]
  weread.py list-apis

分页输出: 每条命令默认控制输出条目数，通过 --page / --per-page 控制。
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
from typing import Any

API_URL = "https://i.weread.qq.com/api/agent/gateway"
SKILL_VERSION = "1.0.3"

# ─── utilities ───────────────────────────────────────────────────────

def ts_to_date(ts: int | float) -> str:
    """Unix timestamp → YYYY-MM-DD"""
    return time.strftime("%Y-%m-%d", time.localtime(ts))

def secs_to_hms(secs: int) -> str:
    """秒 → X小时Y分钟"""
    h, m = divmod(secs, 3600)
    m = m // 60
    if h > 0:
        return f"{h}小时{m}分钟"
    return f"{m}分钟"

def star_to_str(score: int) -> str:
    """评分整数 → 星级。100=⭐⭐⭐⭐⭐, 80=⭐⭐⭐⭐, ..."""
    if score is None or score <= 0:
        return "无评分"
    stars = int(score) // 20
    return "⭐" * stars if stars else "无评分"

def rating_to_str(r: int | None) -> str:
    """评分 (0-1000) → 文字。"""
    if r is None or r == 0:
        return "暂无"
    score = r / 10  # 转为百分制
    if score >= 90:
        return f"神作 {score:.0f}%"
    if score >= 80:
        return f"力荐 {score:.0f}%"
    if score >= 70:
        return f"好评 {score:.0f}%"
    return f"{score:.1f}分"

def make_deep_link(book_id: str, chapter_uid: str = "", range_start: str = "",
                   range_end: str = "", user_vid: str = "") -> str:
    """构造微信读书深度链接。"""
    if chapter_uid and range_start and range_end:
        link = f"weread://bestbookmark?bookId={book_id}&chapterUid={chapter_uid}&rangeStart={range_start}&rangeEnd={range_end}"
        if user_vid:
            link += f"&userVid={user_vid}"
        return link
    if chapter_uid:
        return f"weread://reading?bId={book_id}&chapterUid={chapter_uid}"
    return f"weread://reading?bId={book_id}"

def paginate(items: list, page: int, per_page: int) -> tuple[list, int]:
    """Slice items for pagination. Returns (page_items, total_pages)."""
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages

def paginate_mark(items: list, page: int, per_page: int) -> tuple[list, int, bool, bool]:
    """Slice items with page boundary info."""
    total = len(items)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    return items[start:end], total_pages, page > 1, page < total_pages

def truncate(text: str, max_len: int = 200) -> str:
    """截断长文本。"""
    if len(text) <= max_len:
        return text
    return text[:max_len] + "…"


# ─── API client ───────────────────────────────────────────────────────

class WereadAPI:
    def __init__(self):
        self.key = os.environ.get("WEREAD_API_KEY", "")
        if not self.key:
            print("错误: WEREAD_API_KEY 未设置，请 export WEREAD_API_KEY=***", file=sys.stderr)
            sys.exit(1)

    def call(self, api_name: str, **params) -> dict:
        """调用 API，自动处理 errcode 和 upgrade_info。"""
        body = {"api_name": api_name, "skill_version": SKILL_VERSION, **params}
        data = json.dumps(body).encode("utf-8")
        req = urllib.request.Request(API_URL, data=data, headers={
            "Authorization": f"Bearer {self.key}",
            "Content-Type": "application/json",
        })
        try:
            resp = urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError as e:
            print(f"HTTP {e.code}: {e.reason}", file=sys.stderr)
            sys.exit(1)
        except urllib.error.URLError as e:
            print(f"网络错误: {e.reason}", file=sys.stderr)
            sys.exit(1)

        result = json.loads(resp.read())

        # 检查 upgrade_info
        if "upgrade_info" in result:
            msg = result.get("upgrade_info", {}).get("message", "技能版本需升级")
            print(f"⚠️  {msg}", file=sys.stderr)
            print("请根据指引升级 weread skill 后重试。", file=sys.stderr)
            sys.exit(2)

        errcode = result.get("errcode", 0)
        if errcode != 0:
            errmsg = result.get("errmsg", "未知错误")
            print(f"API 错误 (errcode={errcode}): {errmsg}", file=sys.stderr)
            sys.exit(1)

        return result


# ─── commands ─────────────────────────────────────────────────────────

def cmd_search(api: WereadAPI, args):
    """搜索书籍"""
    params = {"keyword": args.keyword}
    if getattr(args, "scope", None) is not None:
        params["scope"] = args.scope
    if getattr(args, "count", None):
        params["count"] = args.count

    result = api.call("/store/search", **params)
    results = result.get("results", [])
    if not results:
        print("未找到结果。")
        return

    page = getattr(args, "page", 1)
    per_page = getattr(args, "per_page", 10)

    # flatten books from all result groups
    all_books = []
    for group in results:
        group_title = group.get("title", "")
        group_scope = group.get("scope", 0)
        for b in group.get("books", []):
            bi = b.get("bookInfo", {})
            all_books.append({
                "bookId": bi.get("bookId", ""),
                "title": bi.get("title", ""),
                "author": bi.get("author", ""),
                "cover": bi.get("cover", ""),
                "intro": bi.get("intro", ""),
                "publisher": bi.get("publisher", ""),
                "category": bi.get("category", ""),
                "payType": bi.get("payType", 0),
                "price": bi.get("price", 0),
                "newRating": bi.get("newRating"),
                "newRatingCount": bi.get("newRatingCount", 0),
                "newRatingDetail": bi.get("newRatingDetail", {}).get("title", ""),
                "readingCount": b.get("readingCount", 0),
                "soldout": bi.get("soldout", 0),
                "group_title": group_title,
                "group_scope": group_scope,
            })

    page_items, total_pages, has_prev, has_next = paginate_mark(all_books, page, per_page)

    print(f"搜索: {args.keyword}  共 {len(all_books)} 条结果")
    if total_pages > 1:
        print(f"(第 {page}/{total_pages} 页，每页 {per_page} 条)")
    print()

    for i, b in enumerate(page_items, (page - 1) * per_page + 1):
        rating = rating_to_str(b["newRating"])
        status = " [已下架]" if b["soldout"] else ""
        group = f" [{b['group_title']}]" if b.get("group_title") else ""
        print(f"{i}. {b['title']}{status}{group}")
        print(f"   作者: {b['author']}  |  {rating}  |  {b['readingCount']}人在读")
        if b["price"] > 0:
            print(f"   价格: ¥{b['price']/100:.2f}  |  分类: {b['category']}")
        else:
            print(f"   分类: {b['category']}")
        if b["intro"]:
            print(f"   简介: {truncate(b['intro'], 100)}")
        print(f"   [打开]({make_deep_link(b['bookId'])})")
        print()

    if total_pages > 1:
        nav = []
        if has_prev:
            nav.append(f"--page {page-1} 上一页")
        if has_next:
            nav.append(f"--page {page+1} 下一页")
        print("  ".join(nav))


def cmd_shelf(api: WereadAPI, args):
    """书架管理"""
    result = api.call("/shelf/sync")
    books = result.get("books", [])
    albums = result.get("albums", [])
    mp = result.get("mp")

    total = len(books) + len(albums) + (1 if mp else 0)
    secret_books = sum(1 for b in books if b.get("secret") == 1)
    public_books = len(books) - secret_books
    secret_albums = sum(1 for a in albums if a.get("albumInfoExtra", {}).get("secret") == 1)
    public_albums = len(albums) - secret_albums

    print(f"书架共 {total} 个条目：{len(books)} 本电子书")
    if albums:
        print(f"  + {len(albums)} 个专辑/有声书")
    if mp:
        print(f"  + 1 个文章收藏")

    secret_total = secret_books + secret_albums + (1 if mp else 0)
    public_total = public_books + public_albums
    print(f"公开 {public_total}  |  私密 {secret_total}")
    print()

    # 合并所有条目用于分页
    all_items = []
    for b in books:
        all_items.append({
            "type": "📖",
            "id": b.get("bookId", ""),
            "title": b.get("title", ""),
            "author": b.get("author", ""),
            "cover": b.get("cover", ""),
            "category": b.get("category", ""),
            "readUpdateTime": b.get("readUpdateTime", 0),
            "finishReading": b.get("finishReading", 0),
            "isTop": b.get("isTop", 0),
            "secret": b.get("secret", 0),
        })
    for a in albums:
        ai = a.get("albumInfo", {})
        aie = a.get("albumInfoExtra", {})
        all_items.append({
            "type": "🎧",
            "id": ai.get("albumId", ""),
            "title": ai.get("name", ""),
            "author": ai.get("authorName", ""),
            "cover": ai.get("cover", ""),
            "category": "有声书",
            "readUpdateTime": aie.get("lectureReadUpdateTime", 0),
            "finishReading": 1 if ai.get("finish", 0) else 0,
            "isTop": aie.get("isTop", 0),
            "secret": aie.get("secret", 0),
        })

    page = getattr(args, "page", 1)
    per_page = getattr(args, "per_page", 10)
    page_items, total_pages, has_prev, has_next = paginate_mark(all_items, page, per_page)

    for i, item in enumerate(page_items, (page - 1) * per_page + 1):
        tags = []
        if item["isTop"]:
            tags.append("置顶")
        if item["finishReading"]:
            tags.append("已读完")
        if item["secret"]:
            tags.append("私密")
        tag_str = " " + " ".join(f"[{t}]" for t in tags) if tags else ""

        time_str = ""
        if item["readUpdateTime"]:
            time_str = f"  最近: {ts_to_date(item['readUpdateTime'])}"

        print(f"{i}. {item['type']} {item['title']}{tag_str}")
        print(f"   {item['author']}{time_str}")
        if item["id"]:
            bid = item["id"]
            if item["type"] == "📖":
                print(f"   [查看]({make_deep_link(bid)})")
        print()

    if total_pages > 1:
        nav = []
        if has_prev:
            nav.append(f"--page {page-1} 上一页")
        if has_next:
            nav.append(f"--page {page+1} 下一页")
        print("  ".join(nav))


def cmd_book(api: WereadAPI, args):
    """书籍信息"""
    book_id = args.bookId
    info = api.call("/book/info", bookId=book_id)

    print(f"《{info.get('title', '')}》")
    print(f"作者: {info.get('author', '')}")
    if info.get("translator"):
        print(f"译者: {info.get('translator', '')}")
    print(f"评分: {rating_to_str(info.get('newRating'))}  ({info.get('newRatingCount', 0)}人评)")
    print(f"分类: {info.get('category', '')}")
    print(f"出版社: {info.get('publisher', '')}")
    if info.get("publishTime"):
        print(f"出版: {info.get('publishTime', '')}")
    if info.get("isbn"):
        print(f"ISBN: {info.get('isbn', '')}")
    if info.get("wordCount"):
        wc = info["wordCount"]
        if wc >= 10000:
            print(f"字数: {wc/10000:.1f}万字")
        else:
            print(f"字数: {wc}字")
    if info.get("intro"):
        print(f"\n简介: {info['intro']}")
    print(f"\n[打开阅读]({make_deep_link(book_id)})")

    # chapters
    if getattr(args, "chapters", False):
        print("\n── 章节目录 ──")
        ch_info = api.call("/book/chapterinfo", bookId=book_id)
        chs = ch_info.get("chapters", [])
        page = getattr(args, "chapters_page", 1)
        per_page = getattr(args, "chapters_per_page", 20)
        page_items, total_pages, has_prev, has_next = paginate_mark(chs, page, per_page)

        for ch in page_items:
            indent = "  " * max(0, ch.get("level", 1) - 1)
            paid = "🔒" if ch.get("paid") == 1 and ch.get("price", 0) > 0 else ""
            mp = " [公众号]" if ch.get("isMPChapter") else ""
            title = ch.get("title", "")
            print(f"{indent}{title}{paid}{mp}")
        if total_pages > 1:
            print(f"\n(第 {page}/{total_pages} 页，--chapters-page N 翻页)")

    # progress
    if getattr(args, "progress", False):
        print("\n── 阅读进度 ──")
        prog = api.call("/book/getprogress", bookId=book_id)
        book = prog.get("book", {})
        pct = book.get("progress", 0)
        rec = book.get("recordReadingTime", 0)
        print(f"进度: {pct}%")
        print(f"累计阅读: {secs_to_hms(rec)}")
        if book.get("updateTime"):
            print(f"最后阅读: {ts_to_date(book['updateTime'])}")
        if book.get("finishTime"):
            print(f"读完: {ts_to_date(book['finishTime'])}")


def cmd_notes(api: WereadAPI, args):
    """笔记划线"""
    book_id = getattr(args, "book", None)

    if book_id:
        # 单本书笔记
        print("── 划线内容 ──")
        bm = api.call("/book/bookmarklist", bookId=book_id)
        updated = bm.get("updated", [])
        chapters_map = {c.get("chapterUid"): c for c in bm.get("chapters", [])}

        page = getattr(args, "page", 1)
        per_page = getattr(args, "per_page", 10)
        page_items, total_pages, has_prev, has_next = paginate_mark(updated, page, per_page)

        if not updated:
            print("暂无划线。")
        else:
            for i, u in enumerate(page_items, (page - 1) * per_page + 1):
                ch = chapters_map.get(u.get("chapterUid"), {})
                ch_title = ch.get("title", f"章节{u.get('chapterUid', '')}")
                print(f"{i}. [{ts_to_date(u.get('createTime', 0))}] {ch_title}")
                print(f"   > {u.get('markText', '')}")
                rng = u.get("range", "")
                if rng and "-" in rng:
                    rs, re = rng.split("-", 1)
                    link = make_deep_link(book_id, str(u.get("chapterUid", "")), rs, re)
                    print(f"   [位置]({link})")
                print()
            if total_pages > 1:
                print(f"(第 {page}/{total_pages} 页)")

        print("\n── 个人想法 ──")
        try:
            rv = api.call("/review/list/mine", bookid=book_id, count=50, synckey=0)
        except SystemExit:
            # 可能没有想法，跳过
            rv = {}
        reviews = rv.get("reviews", [])
        rv_page = getattr(args, "page", 1)
        rv_per_page = getattr(args, "per_page", 10)
        rv_items, rv_tp, _, _ = paginate_mark(reviews, rv_page, rv_per_page)

        if not reviews:
            print("暂无个人想法。")
        else:
            for i, r in enumerate(rv_items, (rv_page - 1) * rv_per_page + 1):
                rev = r.get("review", {})
                star = star_to_str(rev.get("star", -1))
                ch = rev.get("chapterName", "")
                loc = f" [{ch}]" if ch else ""
                print(f"{i}. {star}{loc}  {ts_to_date(rev.get('createTime', 0))}")
                print(f"   {rev.get('content', '')}")
                rng = rev.get("range", "")
                if rng and "-" in rng:
                    rs, re = rng.split("-", 1)
                    link = make_deep_link(book_id, str(rev.get("chapterUid", "")), rs, re)
                    print(f"   [位置]({link})")
                print()
            if rv_tp > 1:
                print(f"(第 {rv_page}/{rv_tp} 页)")

    else:
        # 笔记本概览
        all_books = []
        count = 50
        last_sort = 0
        max_pages = getattr(args, "max_pages", 5)  # 最多拉取页数
        pages_fetched = 0
        while pages_fetched < max_pages:
            params = {"count": count}
            if last_sort > 0:
                params["lastSort"] = last_sort
            result = api.call("/user/notebooks", **params)
            for b in result.get("books", []):
                bk = b.get("book", {})
                all_books.append({
                    "bookId": b.get("bookId", ""),
                    "title": bk.get("title", ""),
                    "author": bk.get("author", ""),
                    "reviewCount": b.get("reviewCount", 0),
                    "noteCount": b.get("noteCount", 0),
                    "bookmarkCount": b.get("bookmarkCount", 0),
                    "total": b.get("reviewCount", 0) + b.get("noteCount", 0) + b.get("bookmarkCount", 0),
                    "readingProgress": b.get("readingProgress", 0),
                    "markedStatus": b.get("markedStatus", 0),
                    "sort": b.get("sort", 0),
                })
            pages_fetched += 1
            if result.get("hasMore") != 1:
                break
            last_sort = all_books[-1]["sort"]

        all_books.sort(key=lambda x: x["total"], reverse=True)

        if pages_fetched >= max_pages:
            print(f"有笔记的书 (已获取 {pages_fetched} 页，使用 --max-pages N 获取更多)")
        else:
            print(f"有笔记的书共 {len(all_books)} 本")
        total_notes = sum(b["total"] for b in all_books)
        print(f"笔记总数: {total_notes} (想法{sum(b['reviewCount'] for b in all_books)} + 划线{sum(b['noteCount'] for b in all_books)} + 书签{sum(b['bookmarkCount'] for b in all_books)})")
        print()

        page = getattr(args, "page", 1)
        per_page = getattr(args, "per_page", 10)
        page_items, total_pages, has_prev, has_next = paginate_mark(all_books, page, per_page)

        for i, b in enumerate(page_items, (page - 1) * per_page + 1):
            status = "✓读完" if b["markedStatus"] == 1 else f"进度{b['readingProgress']}%"
            print(f"{i}. 《{b['title']}》 {b['author']}  [{status}]")
            print(f"   笔记 {b['total']} 条 (想法{b['reviewCount']} + 划线{b['noteCount']} + 书签{b['bookmarkCount']})")
            print(f"   [查看笔记] weread.py notes --book {b['bookId']}")
            if b["bookId"]:
                print(f"   [打开]({make_deep_link(b['bookId'])})")
            print()

        if total_pages > 1:
            nav = []
            if has_prev:
                nav.append(f"--page {page-1} 上一页")
            if has_next:
                nav.append(f"--page {page+1} 下一页")
            print("  ".join(nav))


def cmd_readdata(api: WereadAPI, args):
    """阅读统计"""
    mode = getattr(args, "mode", "monthly")
    base_time = getattr(args, "time", 0)

    result = api.call("/readdata/detail", mode=mode, baseTime=base_time)
    read_days = result.get("readDays", 0)
    total_secs = result.get("totalReadTime", 0)
    daily_avg = result.get("dayAverageReadTime", 0)
    compare = result.get("compare")

    mode_names = {"weekly": "本周", "monthly": "本月", "annually": "本年", "overall": "总计"}
    print(f"📊 {mode_names.get(mode, mode)}阅读统计")
    print(f"   阅读 {read_days} 天  |  总时长 {secs_to_hms(total_secs)}  |  日均 {secs_to_hms(daily_avg)}")
    if compare is not None:
        direction = "↑" if compare >= 0 else "↓"
        print(f"   较上期: {direction}{abs(compare)*100:.0f}%")

    # 阅读统计摘要
    read_stat = result.get("readStat", [])
    if read_stat:
        parts = []
        for s in read_stat:
            parts.append(f"{s.get('stat', '')}: {s.get('counts', '')}")
        print(f"   " + "  |  ".join(parts))

    print()

    # 读得最多的书
    longest = result.get("readLongest", [])
    if longest:
        print("读得最多:")
        for item in longest[:5]:
            bk = item.get("book", {})
            ai = item.get("albumInfo")
            rt = item.get("readTime", 0)
            name = bk.get("title", "") if bk else (ai.get("name", "") if ai else "未知")
            author = bk.get("author", "") if bk else (ai.get("authorName", "") if ai else "")
            tags = " ".join(f"[{t}]" for t in item.get("tags", []))
            print(f"  · {name}  {author}  {secs_to_hms(rt)}  {tags}")

    # 偏好
    pref_cat = result.get("preferCategory")
    if pref_cat:
        print(f"\n偏好分类: {result.get('preferCategoryWord', '偏好阅读')}")
        for c in pref_cat[:5]:
            print(f"  · {c.get('categoryTitle', '')}  {c.get('readingCount', 0)}本  {secs_to_hms(c.get('readingTime', 0))}")

    pref_time_word = result.get("preferTimeWord")
    if pref_time_word:
        print(f"偏好时段: {pref_time_word}")

    pref_author = result.get("preferAuthor")
    if pref_author:
        print(f"偏好作者:")
        for a in pref_author[:3]:
            print(f"  · {a.get('name', '')}  {a.get('count', 0)}本  {a.get('readTime', '')}")

    # readRate
    rr = result.get("readRate")
    if rr is not None:
        wr = result.get("wrReadTime", 0)
        wl = result.get("wrListenTime", 0)
        print(f"\n阅读/听书: 文字 {secs_to_hms(wr)} ({rr}%)  |  听书 {secs_to_hms(wl)}")

    print()


def cmd_review(api: WereadAPI, args):
    """书籍点评"""
    book_id = args.bookId
    rv_type = getattr(args, "type", 0)
    per_page = getattr(args, "per_page", 10)
    result = api.call("/review/list", bookId=book_id, reviewListType=rv_type,
                       count=per_page, maxIdx=0)

    reviews_cnt = result.get("reviewsCnt", 0)
    print(f"点评共 {reviews_cnt} 条")
    if result.get("deepVRecommendInfo"):
        info = result["deepVRecommendInfo"]
        print(f"{info.get('title', '')}  {info.get('subtitle', '')}")
    print()

    reviews = result.get("reviews", [])
    page = getattr(args, "page", 1)
    per_page = getattr(args, "per_page", 10)
    page_items, total_pages, has_prev, has_next = paginate_mark(reviews, page, per_page)

    for i, r in enumerate(page_items, (page - 1) * per_page + 1):
        rev = r.get("review", {}).get("review", {})
        author = rev.get("author", {})
        name = author.get("name", "匿名")
        star = star_to_str(rev.get("star", 0))
        is_finish = " · 已读完" if rev.get("isFinish") else ""
        ch = rev.get("chapterName", "")
        ch_str = f" · {ch}" if ch else ""
        print(f"{i}. {name}  {star}{is_finish}{ch_str}")
        content = rev.get("content", "")
        print(f"   {truncate(content, 200)}")
        print()

    if total_pages > 1:
        nav = []
        if has_prev:
            nav.append(f"--page {page-1} 上一页")
        if has_next:
            nav.append(f"--page {page+1} 下一页")
        print("  ".join(nav))


def cmd_discover(api: WereadAPI, args):
    """发现推荐"""
    book_id = getattr(args, "book", None)

    if book_id:
        result = api.call("/book/similar", bookId=book_id, count=getattr(args, "per_page", 10))
        books = result.get("booksimilar", {}).get("books", [])
        print("相似书推荐:")
    else:
        result = api.call("/book/recommend", count=getattr(args, "per_page", 10))
        books = result.get("books", [])
        print("为你推荐:")

    if not books:
        print("暂无推荐。")
        return

    page = getattr(args, "page", 1)
    per_page = getattr(args, "per_page", 10)
    page_items, total_pages, has_prev, has_next = paginate_mark(books, page, per_page)

    for i, b in enumerate(page_items, (page - 1) * per_page + 1):
        if book_id:
            bi = b.get("book", {}).get("bookInfo", {})
            reason = ""
        else:
            bi = b
            reason = b.get("reason", "")
        title = bi.get("title", "")
        author = bi.get("author", "")
        rating = rating_to_str(bi.get("newRating"))
        reading = bi.get("readingCount", 0)
        print(f"{i}. 《{title}》 {author}  |  {rating}  |  {reading}人在读")
        if reason:
            print(f"   推荐理由: {reason}")
        if bi.get("intro"):
            print(f"   简介: {truncate(bi['intro'], 100)}")
        print(f"   [打开]({make_deep_link(bi.get('bookId', ''))})")
        print()

    if total_pages > 1:
        nav = []
        if has_prev:
            nav.append(f"--page {page-1} 上一页")
        if has_next:
            nav.append(f"--page {page+1} 下一页")
        print("  ".join(nav))


def cmd_list_apis(api: WereadAPI, args):
    """列出可用接口"""
    result = api.call("/_list")
    apis = result.get("apis", [])
    if not apis:
        print("无可用接口。")
        return
    for a in apis:
        name = a.get("api_name", "")
        desc = a.get("description", "")
        params = a.get("params", [])
        print(f"{name}")
        if desc:
            print(f"  {desc}")
        if params:
            for p in params[:5]:
                print(f"    --{p.get('name', '')} ({p.get('type', '')}): {p.get('desc', '')}")
        print()


# ─── main ─────────────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="微信读书 CLI")
    sub = parser.add_subparsers(dest="command", help="子命令")

    # search
    p = sub.add_parser("search", help="搜索书籍")
    p.add_argument("keyword", help="搜索关键词")
    p.add_argument("--scope", type=int, help="搜索类型 (0=全部 10=电子书 16=网文 14=有声书 6=作者)")
    p.add_argument("--count", type=int, help="每页数量")
    p.add_argument("--page", type=int, default=1, help="页码")
    p.add_argument("--per-page", type=int, default=10, help="每页显示条数")
    p.set_defaults(func=cmd_search)

    # shelf
    p = sub.add_parser("shelf", help="查看书架")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)
    p.set_defaults(func=cmd_shelf)

    # book
    p = sub.add_parser("book", help="书籍详情")
    p.add_argument("bookId", help="书籍 ID")
    p.add_argument("--chapters", action="store_true", help="显示章节目录")
    p.add_argument("--progress", action="store_true", help="显示阅读进度")
    p.add_argument("--chapters-page", type=int, default=1)
    p.add_argument("--chapters-per-page", type=int, default=20)
    p.set_defaults(func=cmd_book)

    # notes
    p = sub.add_parser("notes", help="笔记/划线")
    p.add_argument("--book", dest="bookId", help="单本书 bookId，不传则显示笔记本概览")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)
    p.add_argument("--max-pages", type=int, default=5, help="笔记本概览最多拉取页数")
    p.set_defaults(func=cmd_notes)

    # readdata
    p = sub.add_parser("readdata", help="阅读统计")
    p.add_argument("--mode", choices=["weekly", "monthly", "annually", "overall"], default="monthly")
    p.add_argument("--time", type=int, default=0, help="基准时间戳 (0=当前)")
    p.set_defaults(func=cmd_readdata)

    # review
    p = sub.add_parser("review", help="书籍点评")
    p.add_argument("bookId", help="书籍 ID")
    p.add_argument("--type", type=int, default=0, help="0=全部 1=推荐 2=不行 3=最新 4=一般")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)
    p.set_defaults(func=cmd_review)

    # discover
    p = sub.add_parser("discover", help="发现推荐")
    p.add_argument("--book", dest="bookId", help="基于此书推荐相似书")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--per-page", type=int, default=10)
    p.set_defaults(func=cmd_discover)

    # list-apis
    p = sub.add_parser("list-apis", help="列出可用 API")
    p.set_defaults(func=cmd_list_apis)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    api = WereadAPI()
    args.func(api, args)


if __name__ == "__main__":
    main()
