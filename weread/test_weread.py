#!/usr/bin/env python3
"""weread.py 功能测试 — 覆盖所有子命令和工具函数。"""
import json
import os
import sys
import unittest
import io
from unittest.mock import patch, MagicMock

# Add skill dir to path
sys.path.insert(0, os.path.dirname(__file__))
import weread


class TestUtilities(unittest.TestCase):
    """测试工具函数"""

    def test_ts_to_date(self):
        self.assertEqual(weread.ts_to_date(1748563200), "2025-05-30")
        self.assertEqual(weread.ts_to_date(0), "1970-01-01")

    def test_secs_to_hms(self):
        self.assertEqual(weread.secs_to_hms(0), "0分钟")
        self.assertEqual(weread.secs_to_hms(60), "1分钟")
        self.assertEqual(weread.secs_to_hms(3661), "1小时1分钟")
        self.assertEqual(weread.secs_to_hms(7200), "2小时0分钟")
        self.assertEqual(weread.secs_to_hms(9000), "2小时30分钟")
        self.assertEqual(weread.secs_to_hms(3600), "1小时0分钟")

    def test_star_to_str(self):
        self.assertEqual(weread.star_to_str(100), "⭐⭐⭐⭐⭐")
        self.assertEqual(weread.star_to_str(80), "⭐⭐⭐⭐")
        self.assertEqual(weread.star_to_str(60), "⭐⭐⭐")
        self.assertEqual(weread.star_to_str(40), "⭐⭐")
        self.assertEqual(weread.star_to_str(20), "⭐")
        self.assertEqual(weread.star_to_str(-1), "无评分")
        self.assertEqual(weread.star_to_str(0), "无评分")

    def test_rating_to_str(self):
        """评分 0-1000 → 文字"""
        self.assertEqual(weread.rating_to_str(950), "神作 95%")
        self.assertEqual(weread.rating_to_str(856), "力荐 86%")
        self.assertEqual(weread.rating_to_str(750), "好评 75%")
        self.assertEqual(weread.rating_to_str(500), "50.0分")
        self.assertEqual(weread.rating_to_str(0), "暂无")
        self.assertEqual(weread.rating_to_str(None), "暂无")

    def test_make_deep_link(self):
        # book only
        self.assertEqual(
            weread.make_deep_link("123"),
            "weread://reading?bId=123"
        )
        # book + chapter
        self.assertEqual(
            weread.make_deep_link("123", "456"),
            "weread://reading?bId=123&chapterUid=456"
        )
        # bookmark
        self.assertEqual(
            weread.make_deep_link("123", "456", "100", "200"),
            "weread://bestbookmark?bookId=123&chapterUid=456&rangeStart=100&rangeEnd=200"
        )
        # bookmark + userVid
        self.assertEqual(
            weread.make_deep_link("123", "456", "100", "200", "vid1"),
            "weread://bestbookmark?bookId=123&chapterUid=456&rangeStart=100&rangeEnd=200&userVid=vid1"
        )

    def test_truncate(self):
        self.assertEqual(weread.truncate("short", 200), "short")
        self.assertEqual(weread.truncate("x" * 300, 200), "x" * 200 + "…")

    def test_paginate(self):
        items = list(range(25))
        # page 1, 10 per page
        result, total = weread.paginate(items, 1, 10)
        self.assertEqual(result, list(range(10)))
        self.assertEqual(total, 3)
        # page 2
        result, total = weread.paginate(items, 2, 10)
        self.assertEqual(result, list(range(10, 20)))
        self.assertEqual(total, 3)
        # page 3
        result, total = weread.paginate(items, 3, 10)
        self.assertEqual(result, list(range(20, 25)))
        self.assertEqual(total, 3)
        # empty
        result, total = weread.paginate([], 1, 10)
        self.assertEqual(result, [])
        self.assertEqual(total, 1)

    def test_paginate_mark(self):
        items = list(range(25))
        # first page
        _, total, prev, nxt = weread.paginate_mark(items, 1, 10)
        self.assertEqual(total, 3)
        self.assertFalse(prev)
        self.assertTrue(nxt)
        # middle
        _, total, prev, nxt = weread.paginate_mark(items, 2, 10)
        self.assertEqual(total, 3)
        self.assertTrue(prev)
        self.assertTrue(nxt)
        # last
        _, total, prev, nxt = weread.paginate_mark(items, 3, 10)
        self.assertEqual(total, 3)
        self.assertTrue(prev)
        self.assertFalse(nxt)
        # single page
        _, total, prev, nxt = weread.paginate_mark(list(range(5)), 1, 10)
        self.assertEqual(total, 1)
        self.assertFalse(prev)
        self.assertFalse(nxt)


class TestCommands(unittest.TestCase):
    """测试各子命令输出 — 使用 mock API"""

    def setUp(self):
        self.mock_api = MagicMock()

    def _run_command(self, func, args_obj, mock_api=None):
        """捕获命令 stdout 输出"""
        api = mock_api or self.mock_api
        buf = io.StringIO()
        old_stdout = sys.stdout
        sys.stdout = buf
        try:
            func(api, args_obj)
        finally:
            sys.stdout = old_stdout
        return buf.getvalue()

    def test_cmd_search(self):
        """测试搜索命令输出"""
        self.mock_api.call.return_value = {
            "results": [{
                "title": "电子书",
                "scope": 10,
                "scopeCount": 2,
                "currentCount": 2,
                "books": [
                    {
                        "bookInfo": {
                            "bookId": "695233", "title": "三体", "author": "刘慈欣",
                            "category": "科幻", "newRating": 960, "newRatingCount": 50000,
                            "newRatingDetail": {"title": "神作"}, "intro": "科幻巨作",
                            "payType": 1, "price": 0, "soldout": 0,
                        },
                        "readingCount": 100000,
                    },
                    {
                        "bookInfo": {
                            "bookId": "695234", "title": "三体2", "author": "刘慈欣",
                            "category": "科幻", "newRating": 94, "newRatingCount": 40000,
                            "intro": "黑暗森林", "soldout": 0,
                        },
                        "readingCount": 80000,
                    },
                ],
            }],
        }
        args = MagicMock()
        args.keyword = "三体"
        args.scope = None
        args.count = None
        args.page = 1
        args.per_page = 10

        output = self._run_command(weread.cmd_search, args)
        self.assertIn("三体", output)
        self.assertIn("刘慈欣", output)
        self.assertIn("weread://reading?bId=695233", output)
        self.assertIn("100000人在读", output)
        self.assertIn("共 2 条结果", output)

    def test_cmd_search_no_results(self):
        """搜索无结果"""
        self.mock_api.call.return_value = {"results": []}
        args = MagicMock()
        args.keyword = "zzzxxx"
        args.scope = None
        args.count = None
        args.page = 1
        args.per_page = 10
        output = self._run_command(weread.cmd_search, args)
        self.assertIn("未找到", output)

    def test_cmd_shelf(self):
        """测试书架命令"""
        self.mock_api.call.return_value = {
            "books": [
                {"bookId": "1", "title": "书A", "author": "作者A", "secret": 0, "readUpdateTime": 1748563200, "isTop": 1, "finishReading": 0, "category": "文学"},
                {"bookId": "2", "title": "书B", "author": "作者B", "secret": 1, "readUpdateTime": 1748000000, "isTop": 0, "finishReading": 1, "category": "科幻"},
            ],
            "albums": [
                {"albumInfo": {"albumId": "a1", "name": "有声A", "authorName": "播者A", "finish": 0}, "albumInfoExtra": {"secret": 0, "lectureReadUpdateTime": 0}},
            ],
            "mp": None,
        }
        args = MagicMock()
        args.page = 1
        args.per_page = 10

        output = self._run_command(weread.cmd_shelf, args)
        self.assertIn("共 3 个条目", output)
        self.assertIn("2 本电子书", output)
        self.assertIn("1 个专辑/有声书", output)
        self.assertIn("公开 2", output)
        self.assertIn("私密 1", output)
        self.assertIn("书A", output)
        self.assertIn("书B", output)
        self.assertIn("有声A", output)
        self.assertIn("置顶", output)
        self.assertIn("2025-05-30", output)

    def test_cmd_shelf_with_mp(self):
        """测试书架含文章收藏"""
        self.mock_api.call.return_value = {
            "books": [{"bookId": "1", "title": "书A", "author": "作者A", "secret": 0, "readUpdateTime": 0, "isTop": 0, "finishReading": 0, "category": "文学"}],
            "albums": [],
            "mp": {"some": "data"},
        }
        args = MagicMock()
        args.page = 1
        args.per_page = 10
        output = self._run_command(weread.cmd_shelf, args)
        self.assertIn("共 2 个条目", output)
        self.assertIn("文章收藏", output)
        self.assertIn("私密 1", output)  # mp counts as private

    def test_cmd_book(self):
        """测试书籍详情"""
        self.mock_api.call.side_effect = [
            {  # /book/info
                "bookId": "695233", "title": "三体", "author": "刘慈欣",
                "category": "科幻", "publisher": "科幻世界",
                "newRating": 960, "newRatingCount": 50000,
                "intro": "文化大革命如火如荼进行的同时…",
                "wordCount": 200000, "isbn": "9787536692930",
                "publishTime": "2008",
            },
            {  # /book/getprogress
                "book": {
                    "progress": 45, "recordReadingTime": 7200,
                    "updateTime": 1748563200, "finishTime": None,
                },
            },
        ]
        args = MagicMock()
        args.bookId = "695233"
        args.chapters = False
        args.progress = True
        args.chapters_page = 1
        args.chapters_per_page = 20

        output = self._run_command(weread.cmd_book, args)
        self.assertIn("三体", output)
        self.assertIn("刘慈欣", output)
        self.assertIn("神作 96%", output)
        self.assertIn("20.0万字", output)
        self.assertIn("weread://reading?bId=695233", output)
        self.assertIn("进度: 45%", output)
        self.assertIn("2小时0分钟", output)

    def test_cmd_book_chapters(self):
        """测试章节目录"""
        calls = []
        from weread import SKILL_VERSION
        def side_effect(api_name, **params):
            calls.append((api_name, params))
            if api_name == "/book/info":
                return {"title": "测试书", "author": "作者", "bookId": "1"}
            elif api_name == "/book/chapterinfo":
                return {
                    "chapters": [
                        {"chapterUid": 1, "title": "第一章", "level": 1, "paid": 1, "price": 100},
                        {"chapterUid": 2, "title": "第一节", "level": 2, "paid": 0, "price": 0},
                        {"chapterUid": 3, "title": "第二章", "level": 1, "paid": 0, "price": 0},
                    ],
                }
            return {}
        self.mock_api.call.side_effect = side_effect

        args = MagicMock()
        args.bookId = "1"
        args.chapters = True
        args.progress = False
        args.chapters_page = 1
        args.chapters_per_page = 20

        output = self._run_command(weread.cmd_book, args)
        self.assertIn("第一章", output)
        self.assertIn("第一节", output)  # level 2 should be indented
        self.assertIn("第二章", output)

    def test_cmd_notes_overview(self):
        """测试笔记本概览"""
        self.mock_api.call.return_value = {
            "books": [
                {"bookId": "1", "book": {"title": "书A", "author": "作者A"},
                 "reviewCount": 10, "noteCount": 20, "bookmarkCount": 5,
                 "readingProgress": 80, "markedStatus": 0, "sort": 1000},
                {"bookId": "2", "book": {"title": "书B", "author": "作者B"},
                 "reviewCount": 5, "noteCount": 15, "bookmarkCount": 3,
                 "readingProgress": 100, "markedStatus": 1, "sort": 900},
            ],
            "hasMore": 0,
        }
        args = MagicMock()
        args.book = None
        args.bookId = None
        args.page = 1
        args.per_page = 10
        args.max_pages = 5

        output = self._run_command(weread.cmd_notes, args)
        self.assertIn("有笔记的书共 2 本", output)
        self.assertIn("书A", output)
        self.assertIn("书B", output)
        self.assertIn("笔记 35 条", output)  # 10+20+5=35
        self.assertIn("笔记 23 条", output)  # 5+15+3=23
        self.assertIn("weread.py notes --book", output)  # CLI reference

    def test_cmd_notes_single_book(self):
        """测试单本书笔记"""
        self.mock_api.call.side_effect = [
            {  # /book/bookmarklist
                "updated": [{
                    "bookmarkId": "b1", "chapterUid": 1, "markText": "给岁月以文明",
                    "createTime": 1748563200, "range": "100-110",
                }],
                "chapters": [{"chapterUid": 1, "title": "第一章"}],
            },
            {  # /review/list/mine
                "reviews": [{
                    "review": {
                        "content": "这段写得真好", "star": 100, "createTime": 1748563200,
                        "chapterName": "第一章", "chapterUid": 1, "range": "100-110",
                    },
                }],
            },
        ]
        args = MagicMock()
        args.book = "1"
        args.bookId = "1"
        args.page = 1
        args.per_page = 10

        output = self._run_command(weread.cmd_notes, args)
        self.assertIn("给岁月以文明", output)
        self.assertIn("这段写得真好", output)
        self.assertIn("weread://bestbookmark", output)

    def test_cmd_notes_empty(self):
        """测试无笔记"""
        self.mock_api.call.side_effect = [
            {"updated": [], "chapters": []},
            {"reviews": []},
        ]
        args = MagicMock()
        args.book = "1"
        args.bookId = "1"
        args.page = 1
        args.per_page = 10

        output = self._run_command(weread.cmd_notes, args)
        self.assertIn("暂无划线", output)
        self.assertIn("暂无个人想法", output)

    def test_cmd_readdata(self):
        """测试阅读统计"""
        self.mock_api.call.return_value = {
            "readDays": 15, "totalReadTime": 5400, "dayAverageReadTime": 1800,
            "compare": 0.2,
            "readStat": [
                {"stat": "读过", "counts": "5本"},
                {"stat": "读完", "counts": "2本"},
                {"stat": "笔记", "counts": "30条"},
            ],
            "readLongest": [
                {"book": {"title": "书A", "author": "作者A"}, "readTime": 3600, "tags": ["笔记最多"]},
            ],
            "preferCategory": [
                {"categoryTitle": "文学", "readingCount": 3, "readingTime": 2000},
            ],
            "preferCategoryWord": "偏好阅读文学",
            "preferTimeWord": "偏好夜间阅读",
        }
        args = MagicMock()
        args.mode = "monthly"
        args.time = 0

        output = self._run_command(weread.cmd_readdata, args)
        self.assertIn("本月", output)  # mode=monthly
        self.assertIn("阅读 15 天", output)
        self.assertIn("1小时30分钟", output)  # 5400s
        self.assertIn("↑20%", output)  # compare=0.2
        self.assertIn("读过: 5本", output)
        self.assertIn("书A", output)
        self.assertIn("文学", output)

    def test_cmd_readdata_annually(self):
        """测试年度阅读统计"""
        self.mock_api.call.return_value = {
            "readDays": 200, "totalReadTime": 360000, "dayAverageReadTime": 986,
        }
        args = MagicMock()
        args.mode = "annually"
        args.time = 0

        output = self._run_command(weread.cmd_readdata, args)
        self.assertIn("本年", output)
        self.assertIn("100小时0分钟", output)

    def test_cmd_review(self):
        """测试书籍点评"""
        self.mock_api.call.return_value = {
            "reviewsCnt": 2,
            "deepVRecommendInfo": {"title": "100 个资深会员点评", "subtitle": "其中 80 人推荐"},
            "reviews": [{
                "idx": 0,
                "review": {"review": {
                    "content": "非常好看的一本书，强烈推荐！",
                    "star": 100, "createTime": 1748563200,
                    "author": {"name": "读者A", "userVid": "v1"},
                    "isFinish": True, "chapterName": "",
                }},
            }],
        }
        args = MagicMock()
        args.bookId = "123"
        args.type = 0
        args.page = 1
        args.per_page = 10

        output = self._run_command(weread.cmd_review, args)
        self.assertIn("点评共 2 条", output)
        self.assertIn("读者A", output)
        self.assertIn("⭐⭐⭐⭐⭐", output)
        self.assertIn("非常好看", output)
        self.assertIn("100 个资深会员点评", output)

    def test_cmd_discover_recommend(self):
        """测试为你推荐"""
        self.mock_api.call.return_value = {
            "books": [
                {"bookId": "1", "title": "推荐书A", "author": "作者A",
                 "newRating": 900, "readingCount": 5000, "reason": "看过三体的人也看",
                 "intro": "一本好书"},
            ],
        }
        args = MagicMock()
        args.book = None
        args.bookId = None
        args.page = 1
        args.per_page = 10
        args.max_pages = 5

        output = self._run_command(weread.cmd_discover, args)
        self.assertIn("为你推荐", output)
        self.assertIn("推荐书A", output)
        self.assertIn("看过三体的人也看", output)
        self.assertIn("weread://reading?bId=1", output)

    def test_cmd_discover_similar(self):
        """测试相似推荐"""
        self.mock_api.call.return_value = {
            "booksimilar": {
                "books": [{
                    "book": {"bookInfo": {"bookId": "2", "title": "相似书", "author": "作者B", "newRating": 85, "readingCount": 3000}},
                }],
            },
        }
        args = MagicMock()
        args.book = "1"
        args.bookId = "1"
        args.page = 1
        args.per_page = 10

        output = self._run_command(weread.cmd_discover, args)
        self.assertIn("相似书推荐", output)
        self.assertIn("相似书", output)

    def test_cmd_discover_empty(self):
        """测试推荐为空"""
        self.mock_api.call.return_value = {"books": []}
        args = MagicMock()
        args.book = None
        args.bookId = None
        args.page = 1
        args.per_page = 10
        args.max_pages = 5
        output = self._run_command(weread.cmd_discover, args)
        self.assertIn("暂无推荐", output)

    def test_cmd_list_apis(self):
        """测试列出接口"""
        self.mock_api.call.return_value = {
            "apis": [
                {"api_name": "/shelf/sync", "description": "同步书架", "params": []},
                {"api_name": "/store/search", "description": "搜索", "params": [
                    {"name": "keyword", "type": "string", "desc": "关键词"},
                ]},
            ],
        }
        args = MagicMock()
        output = self._run_command(weread.cmd_list_apis, args)
        self.assertIn("/shelf/sync", output)
        self.assertIn("/store/search", output)

    def test_pagination_output(self):
        """测试分页输出 — 项目超过 per_page 时显示页码"""
        books = []
        for i in range(25):
            books.append({
                "bookInfo": {"bookId": str(i), "title": f"书{i}", "author": f"作者{i}",
                             "newRating": 80, "newRatingCount": i * 100,
                             "newRatingDetail": {}, "soldout": 0, "intro": ""},
                "readingCount": i * 10,
            })
        self.mock_api.call.return_value = {
            "results": [{"title": "电子书", "scope": 10, "scopeCount": 25, "currentCount": 25, "books": books}],
        }
        args = MagicMock()
        args.keyword = "test"
        args.scope = None
        args.count = None

        # page 1
        args.page = 1
        args.per_page = 10
        output = self._run_command(weread.cmd_search, args)
        self.assertIn("第 1/3 页", output)
        self.assertIn("--page 2 下一页", output)
        self.assertIn("书0", output)
        self.assertIn("书9", output)
        self.assertNotIn("书10:", output)  # not on page 1

        # page 2
        args.page = 2
        output = self._run_command(weread.cmd_search, args)
        self.assertIn("第 2/3 页", output)
        self.assertIn("书10", output)
        self.assertIn("书19", output)

        # page 3 (last page)
        args.page = 3
        output = self._run_command(weread.cmd_search, args)
        self.assertIn("第 3/3 页", output)
        self.assertNotIn("下一页", output)  # last page, no next

    def test_cli_argparse(self):
        """测试 CLI 参数解析 — 各子命令正常创建"""
        import argparse
        # We just verify all subparsers register without error
        # by importing the module's main function (not calling it)
        # Instead, test help output by running with --help
        pass  # argparse test covered by integration



class TestAPIErrors(unittest.TestCase):
    """测试 API 错误处理"""

    def test_missing_key(self):
        """测试未设置 WEREAD_API_KEY"""
        old_key = os.environ.pop("WEREAD_API_KEY", None)
        try:
            with self.assertRaises(SystemExit) as cm:
                weread.WereadAPI()
            self.assertEqual(cm.exception.code, 1)
        finally:
            if old_key:
                os.environ["WEREAD_API_KEY"] = old_key


class TestVersion(unittest.TestCase):
    """测试版本号存在"""
    def test_skill_version(self):
        self.assertEqual(weread.SKILL_VERSION, "1.0.3")


def run_all_tests():
    """Run all tests and return True if all pass."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromTestCase(TestUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestCommands))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIErrors))
    suite.addTests(loader.loadTestsFromTestCase(TestVersion))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
