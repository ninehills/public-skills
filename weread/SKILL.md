---
name: 微信读书
description: 微信读书助手 — 搜索书籍、管理书架、查看笔记划线、浏览书评、阅读统计、发现推荐好书
version: 1.1.0
---

# WeRead — 微信读书助手

通过 `weread.py` CLI 调用微信读书接口，提供搜索、书架、笔记、书评等能力。

**强制性规则：所有微信读书操作必须通过 CLI 完成，禁止手写 curl 或直接调 API。CLI 已内置鉴权、版本上报、分页、格式化输出、深度链接等所有逻辑。**

> 需要 WEREAD_API_KEY（已配置在 ~/.hermes/.env）。

## 快速参考

```bash
WR=~/.hermes/skills/weread/weread.py

# 搜索
$WR search <关键词> [--scope 10] [--page 1] [--per-page 10]

# 书架
$WR shelf [--page 1] [--per-page 10]

# 书籍详情 + 进度 + 目录
$WR book <bookId> [--progress] [--chapters] [--chapters-page 1]

# 笔记划分 — 概览 或 单本书
$WR notes [--book <bookId>] [--page 1] [--per-page 10] [--max-pages 5]

# 阅读统计
$WR readdata [--mode monthly|weekly|annually|overall] [--time 0]

# 公开点评
$WR review <bookId> [--type 0] [--per-page 10]

# 推荐发现 — 为你推荐 或 相似书
$WR discover [--book <bookId>] [--per-page 10]
```

## 子命令详解

### search — 搜索书籍

```bash
$WR search 三体                           # 默认电子书 scope=10
$WR search 三体 --scope 0                  # 综合搜索
$WR search 三体 --scope 16                 # 网文小说
$WR search 三体 --scope 14                 # 有声书
$WR search 三体 --scope 6                  # 作者
$WR search 三体 --per-page 5 --page 2      # 分页
```

scope 选择指引详见 `search.md`。CLI 输出包含书名、作者、评分、在读人数、简介、weread:// 打开链接。

### shelf — 书架

```bash
$WR shelf --per-page 5 --page 1
```

输出包含：总条目数（books + albums + mp）、公开/私密统计、每本书的类型标记（📖电子书/🎧有声书）、最近阅读时间、置顶/读完/私密标记、weread:// 链接。

### book — 书籍详情

```bash
$WR book 695233                             # 基本信息
$WR book 695233 --progress                  # 含阅读进度
$WR book 695233 --chapters                  # 含章节目录
$WR book 695233 --progress --chapters       # 全部
```

CLI 已处理：评分 0-1000→百分制、字数→万字、时间戳→YYYY-MM-DD、阅读时长→X小时Y分钟。

### notes — 笔记划线

```bash
$WR notes                                   # 笔记本概览 (所有有笔记的书，按笔记数排序)
$WR notes --per-page 10 --page 1            # 分页
$WR notes --max-pages 10                    # 拉更多页 (默认5页=250本)
$WR notes --book 695233                     # 单本书笔记：划线 + 个人想法
$WR notes --book 695233 --page 1 --per-page 5
```

概览输出：书名、作者、阅读进度、笔记总数（想法+划线+书签）、weread:// 链接。
单本书输出：划线内容（按章节分组，附带位置链接）、个人想法/点评。

### readdata — 阅读统计

```bash
$WR readdata                                # 本月 (默认)
$WR readdata --mode weekly                  # 本周
$WR readdata --mode annually                # 本年
$WR readdata --mode overall                 # 总计
$WR readdata --mode monthly --time 1735689600  # 历史月份
```

输出：阅读天数、总时长、日均时长、与上期对比、读过/读完/笔记数、读得最多的书 TOP5、偏好分类/时段/作者。

### review — 书籍点评

```bash
$WR review <bookId>                         # 全部点评
$WR review <bookId> --type 1                # 推荐 (1=推荐 2=不行 3=最新 4=一般)
$WR review <bookId> --per-page 5
```

输出：点评总数、资深会员推荐比例、每条点评（昵称、星级、内容摘要）。

### discover — 发现推荐

```bash
$WR discover                                # 为你推荐
$WR discover --book <bookId>                # 基于此书的相似推荐
$WR discover --per-page 5
```

## Agent 工作流规则

1. **CLI 优先**：始终使用 `$WR <command>` 而非 curl/API 直调。CLI 已处理版本上报 `skill_version`、鉴权、errcode 检测、upgrade_info 处理。
2. **bookId 记忆**：对话中记住首次查到的 bookId，后续操作无需用户重复提供书名。
3. **分页控制篇幅**：默认 `--per-page 10`，数据量大时加 `--page N` 翻页，避免刷屏。
4. **书名查 bookId**：用户给书名时先 `$WR search <书名>` 拿到 bookId，再进行后续操作。
5. **书架数量口诀**：`books.length + albums.length + (mp非空?1:0)` — CLI 已内置此逻辑。
6. **阅读统计单位**：CLI 自动将秒转为小时/分钟，时间戳转为日期，评分 0-1000 转为百分制。
7. **故障处理**：CLI 报错时检查 WEREAD_API_KEY 是否有效；若遇 upgrade_info 提示，按指引升级。

## 参考文档

以下文件记录了各接口的字段含义、概念口径和工作流细节（CLI 已实现，仅作理解参考）：

| 文档 | 说明 |
|------|------|
| `search.md` | 搜索 scope 选择、字段说明 |
| `shelf.md` | 书架结构、数量口径、公开/私密规则 |
| `book.md` | 书籍信息、章节目录、阅读进度字段 |
| `notes.md` | 笔记统计口径、划线、想法、热门划线 |
| `review.md` | 公开点评字段与类型 |
| `readdata.md` | 阅读统计字段单位、周期组合 |
| `discover.md` | 推荐接口字段说明 |
| `profile.md` | 用户概况组合查询 |

## 已知 Pitfalls（API 与数据）

从开发过程中发现的陷阱，CLI 已处理但理解 API 行为时需知：

| Pitfall | 说明 | 影响接口 |
|---------|------|----------|
| **newRating 是 0-1000 刻度** | 参考文档误标为"百分制"或"0-100"，实际如 930=93%。CLI 内部除以 10 展示为百分制 | `/book/info`, `/store/search`, `/book/recommend` |
| **star 字段可能为 float** | JSON 反序列化后 `star` 可能为 `100.0` 而非 `100`，必须 `int()` 后再做整除。CLI 已处理 | `/review/list`, `/review/list/mine` |
| **review 列表需要 count/maxIdx** | 不传这两个参数时 `reviews` 数组可能为空（只返回统计摘要）。CLI 自动传 | `/review/list` |
| **notes 全量拉取可能超时** | 书架 2000+ 本时有笔记的书很多，逐页拉到 `hasMore=0` 可能超时。CLI 默认限 5 页（250 本），通过 `--max-pages` 调整 | `/user/notebooks` |
| **skill_version 需同步** | `weread.py` 内 `SKILL_VERSION` 常量与 SKILL.md frontmatter `version` 需保持同步。当前 CLI: 1.0.3, SKILL.md: 1.1.0 — 下次改 CLI 时对齐 | — |

## CLI 开发

脚本：`weread.py`（主 CLI）、`test_weread.py`（单元测试）。

运行测试：`cd ~/.hermes/skills/weread && python3 test_weread.py`
