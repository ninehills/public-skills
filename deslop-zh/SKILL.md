---
name: deslop-zh
description: 整合式去 AI 味写作技能 — 覆盖中文技术文档、博客、社交媒体、发行说明、科学论文等多场景。统合 stop-slop、skill-deslop、tropes.fyi、anti-slop-writing、talk-normal、tech-doc-style-chinese、write、Wikipedia AI 特征等资源。当用户要求「去 AI 味」「改写」「润色」「写一段」「审稿」「翻译腔太重」或在写作/编辑场景中自然触发。
metadata:
  trigger: 去AI味, 改写, 润色, 写一段, 审稿, 改稿, 翻译腔, 自然一点, 像人写的, 技术文档, 博客, 推文, 发行说明, release notes, 文章, polish, rewrite, de-AI, deslop
  sources:
    - https://github.com/hardikpandya/stop-slop
    - https://github.com/stephenturner/skill-deslop
    - https://tropes.fyi
    - https://github.com/coderjatin/anti-slop-writing
    - https://github.com/hexiecs/talk-normal
    - https://github.com/ninehills/skills (write, tech-doc-style-chinese)
    - https://zh.wikipedia.org/wiki/Wikipedia:AI生成文的特徵
---

# 去 AI 味写作指南

整合多来源的 AI 写作模式识别与改写规则，覆盖中文技术文档、博客、社交媒体、发行说明、科学论文等场景。

---

## 一、核心原则

### 1. 自然 > 风格化
最高优先级：**读起来自然，而非读起来像「努力装人」**。
- 不要为了去 AI 味而硬塞口语词（「说白了」「居然」「谁能想到」「太太太」）
- 不要为「更像人」把技术文改得像口播稿
- 如果原句已经自然、准确、清楚，不改

### 2. 减法优先
去 AI 味是做减法，不是做加法：
- 先删：解释腔、总结腔、多余转折、套话填充
- 再调：句式节奏、标点、用词口语化程度
- 不改：代码字面量、URL、API 路径、JSON 键名、数据库字段名

### 3. 保语义 > 去 AI 味
先确认事实、逻辑、因果不变。为「更口语」改坏原意 = 失败改写。

### 4. 场景决定策略
不同写作目标有不同标准：
- **技术文档**：克制、准确、可扫读，不用第二人称
- **博客/技术长文**：自然稳重的工程师口吻，不做报告腔也不做口播腔
- **社交媒体**：有性格，有立场，不列功能清单
- **发行说明**：一句话说用户效果，条目密度匹配项目风格
- **科学论文**：保持学术正式度但不用空洞套话

---

## 二、速查清单（写完后过一遍）

**中文：**
- [ ] 段末有「这说明」「可以看出」「到这里」开头的收尾总结句？→ 删
- [ ] 有「不是...而是...」对比句式？→ 只说结论
- [ ] 有「随着...的发展」「在当今...时代」开篇套话？→ 删
- [ ] 有「赋能」「抓手」「闭环」「拉通」「沉淀」等黑话？→ 替换
- [ ] 用了破折号（—）？→ 逗号或句号替代
- [ ] 有四五个短句连发像打电报？→ 合并或变节奏
- [ ] 章节间有「上面这些讲的是...下面我们看...」过渡句？→ 删
- [ ] 中文和英文/数字之间没加空格？→ 加
- [ ] 用了「非常」「极其」「值得注意的是」「综上所述」「例如」？→ 换成「很」「比如」
- [ ] 有升华句（把技术观察上升到人生道理）？→ 删
- [ ] 用了第二人称「你」「您」？→ 技术文档应避免；博客可酌情
- [ ] 有「一句话总结」「简而言之」等总结标签？→ 直接说结论

**通用：**
- [ ] 有任何 -ly 副词（-ly words）？→ 删
- [ ] 有被动语态藏起行动者？→ 找出主语
- [ ] 无生命事物做了人类动词（「决策浮现」「数据告诉我们」）？→ 命名真人
- [ ] 「serves as」「stands as」？→ 直接用「是」
- [ ] 三连结构用太多？→ 换二连或一连
- [ ] 自问自答？→ 直接陈述
- [ ] 「It's worth noting」「Notably」「Interestingly」？→ 删
- [ ] 段落结尾是 punchy 短句？→ 换节奏
- [ ] em dash 出现？→ 最多每 500 字一个
- [ ] 每个列表项都是 bold 关键词开头？→ 换格式
- [ ] 「Despite its...」「Faces challenges...」配方？→ 具体说
- [ ] 用 「showcase」「delve」「tapestry」「landscape」「crucial」「pivotal」？→ 替换

---

## 三、中文专属 AI 味模式

### 3.1 段末收尾总结句（最高频，优先检查）
一段刚解释完某机制，结尾再重述一遍。

**信号词**：这说明 / 到这里 / 可以看出 / 这本身就是 / 通过以上分析 / 由此可见

> ❌ 「到这里，我们已经看到了内存分配器在 allocation 路径上的三个关键优化点。」
> ✅ 直接删掉，上一句已经说完。

### 3.2 升华句
把具体工程观察上升到普适人生道理。

> ❌ 「这其实和产品设计一样：好的抽象不是为了炫技，而是为了让使用者少犯错。」
> ✅ 直接给具体建议：「所以设计抽象时，先用调用方的视角写一遍调用代码，再决定接口长什么样。」

### 3.3 对比句式（「不是...而是...」）
这是硬约束：**禁止用否定式对比结构**。任何形式的「不是 X，而是 Y」「不是 X，是 Y」「X 本身没有价值，真正有用的是 Y」「X 已经不是瓶颈，Y 才是」全部重写。

> ❌ 「真正的创新者不是有创意的人，而是五种特质同时拉满的人。」
> ✅ 「真正的创新者是五种特质同时拉满的人。」

> ❌ 「这更像创始人筛选框架，不是交易信号。」
> ✅ 「这是一个创始人筛选框架。」

> ❌ 「性能瓶颈已经不是 I/O，而是锁竞争。」
> ✅ 「锁竞争现在是主要性能瓶颈。」

### 3.4 讲解腔 / 训人感起手
> ❌ 「真拆开看...」「这背后是同一个变化...」「真正关键的问题是...」
> ❌ 「先问问是不是」「你要先明白」
> ✅ 直接说。「先确认...」「可以先看...」

### 3.5 总结腔标签
不要在结尾前加总结标签。

> ❌ 一句话总结 / 简而言之 / 概括来说 / 总而言之 / 综上所述 / 总结一下
> ❌ 一句话落地 / 一句话讲 / 一句话概括
> ✅ 直接给 punchline，不加标签。

### 3.6 文章开篇套话
> ❌ 「随着 AI 技术的不断发展...」
> ❌ 「在当今数字化浪潮中...」
> ❌ 「近年来，XXX 受到了越来越多的关注...」
> ✅ 直接开头。「用了不到一个月后...」「先说结论...」「这次想把 X 这条链路讲清楚...」

### 3.7 中文黑话 / 互联网黑话
以下词默认不用（除非引用原文或行业固定术语）：
- **绝对禁用**：赋能、抓手、闭环、沉淀、对齐、对标、拉通、打通、协同、联动、洞察、赛道、心智、调性、战役、链路、势能、兜底
- **谨慎使用**：场景、生态、体系、路径、触点、卡点、布局、矩阵、颗粒度、复盘、梳理、输出、提炼

> ❌ 「通过数据沉淀赋能业务闭环」
> ✅ 「积累数据后，业务能形成完整流程」

### 3.8 用词去正式化
| 不用 | 用 |
|------|-----|
| 非常 / 极其 | 很 |
| 值得注意的是 | （直接说结论） |
| 综上所述 | （直接收尾） |
| 例如 | 比如 |
| 购买 / 使用 | 买 / 用 |
| 很多同学 / 不少同学 | 很多人 / 不少人 |
| 这几个事 | 这几件事 |

### 3.9 标点规则
- 使用直角引号 `「」`，不用弯引号 `""`
- 禁止破折号（—），用逗号或分号替代
- 不用感叹号（除非推文/社交场景且确有情绪）
- 中文标点：，。；：！？、`「」`『』【】
- 四五个句号连发 = 打电报 → 合成长句或用逗号连

### 3.10 中英混排留白
- 中文和英文之间加空格：`CN 文字 EN` → `CN 文字 EN`
- 中文和数字之间加空格：`版本 2.0`
- 不加空格的对象：代码块、JSON 键名、URL、内联代码

### 3.11 第二人称
- **技术文档**：禁用「你」「您」。用「开发者」「技术负责人」等角色词，或不直接称呼读者
- **博客**：可以用「你」，但不要通篇「你会发现」「你需要」「你可以看到」

### 3.12 翻译腔套路
> ❌ 「接住」「击穿」「锋利」「不崩」「不爆」「打穿」「扛住」等物理动作动词用在了抽象认知上
> ✅ 换成日常中文：「你这几条我都收到了」「这个假设不成立」

> ❌ 抽象名词做主语：`工程上的现实比这些数字难看`
> ✅ 重写，人/动作做主语。

### 3.13 空泛形容词预判
> ❌ 「更干净：xxx」「逻辑很清晰：xxx」
> ✅ 删掉形容词预判，直接说 xxx。

### 3.14 Wikipedia 中文 AI 特征
来自中文维基百科的识别点：
- **过度强调重要性**：对普通主题用「至关重要」「意义重大」「关键时刻」「转折点」
- **过度强调来源和知名度**：「依据多家媒体报道...」「显示其于产业中具一定能见度」
- **表面分析**：以分词短语附加空洞评论，如「反映了当代中国社会的变迁」
- **推广语气**：强调「文化遗产」「文化底蕴」等
- **模糊归因**：「据业内人士指出」「有评论认为」
- **固定的展望章节**：「尽管（主题）有其（正面词）的意义，但其面临的挑战有...」

---

## 四、跨语言通用 AI 味模式

### 4.1 喉清开场（Throat-Clearing Openers）
> ❌ Here's the thing: / The truth is, / Let me be clear / It turns out / I'm going to be honest / Can we talk about
> ✅ 直接说内容。任何 "here's what/this/that" 结构都删。

### 4.2 副词（Adverbs）
**全部删。** 任何 -ly 副词、软化词、强化词、模糊限定词。
> ❌ really, just, literally, genuinely, honestly, simply, actually, deeply, truly, fundamentally, inherently, inevitably, interestingly, importantly, crucially, quietly, remarkably, arguably

### 4.3 被动语态 / 假主体（Passive Voice & False Agency）
**每条句子都要有人类主语在做动作。** 不要让无生命事物「做」人类动词。

> ❌ 「the complaint becomes a fix」→ 投诉什么都没做，有人修了它
> ❌ 「a bet lives or dies in days」→ 赌注没有寿命，有个人砍了或交付了项目
> ❌ 「the decision emerges」→ 决策不会自己浮现，有人做了决策
> ❌ 「the culture shifts」→ 文化不会自己移，人们改变了行为
> ❌ 「the data tells us」→ 数据摆在那，有人读了并下了结论
> ❌ 「the market rewards」→ 市场没有奖赏，买家付了钱

✅ 命名人。「The team fixed it that week」打败「the complaint becomes a fix」。找不到具体人就用「you」或「we」。

### 4.4 二元对比 / 否定并列（Binary Contrasts & Negative Parallelism）
最常见的 AI 写作信号。

> ❌ 「It's not X — it's Y.」「Not because X. Because Y.」「The question isn't X. It's Y.」「It feels like X. It's actually Y.」
> ✅ 直接说 Y。「The problem is Y.」丢掉否定部分。

### 4.5 三连滥用（Tricolon Abuse）
> ❌ 「Products impress people; platforms empower them. Products solve problems; platforms create worlds. Products scale linearly; platforms scale exponentially.」
> ✅ 用二连或一连。一个三连可以，背靠背的三连是模式识别失败。

### 4.6 自问自答（Self-Posed Rhetorical Questions）
> ❌ 「The result? Devastating.」「The worst part? Nobody saw it coming.」「What if I told you...」
> ✅ 直接陈述。「The result was devastating.」

### 4.7 戏剧化碎片（Dramatic Fragmentation）
> ❌ 「[Noun]. That's it. That's the [thing].」「He published this. Openly. In a book. As a priest.」
> ✅ 用完整句。信任内容，不靠排版制造强调。

### 4.8 元评论（Meta-Commentary）
> ❌ 「In this section, we'll explore...」「As we'll see...」「Let me walk you through...」「The rest of this essay...」
> ✅ 删掉。让文章自己前行，不预告结构。

### 4.9 「Serves As」回避系词
> ❌ serves as / stands as / marks / represents / constitutes / boasts / features (as 'has')
> ✅ 直接用 is / are / has。

### 4.10 强调拐杖（Emphasis Crutches）
> ❌ Full stop. / Period. / Let that sink in. / This matters because. / Make no mistake.
> ✅ 删。

### 4.11 商业黑话（Business Jargon）
| 不用 | 用 |
|------|-----|
| navigate (challenges) | handle, address |
| unpack | explain, examine |
| lean into | accept, embrace |
| landscape | situation, field |
| game-changer | significant, important |
| double down | commit, increase |
| deep dive | analysis, examination |
| leverage (verb) | use |
| utilize | use |
| robust | strong, solid |
| streamline | simplify |
| harness | use, apply |
| paradigm | model, approach |
| ecosystem | system, field, community |
| synergy | cooperation, combined effect |

### 4.12 AI 词汇印记（AI Vocabulary Tells）
> ❌ delve, tapestry, nuanced, certainly, realm, nexus, interplay, cornerstone, beacon, pillar, catalyst, crucible, confluence, odyssey, multifaceted, holistic, compelling, profound, indelible, paramount, indispensable, invaluable, quintessential
> ✅ 用日常词。

### 4.13 灌输腔（Pedagogical Hand-Holding）
> ❌ Let's break this down. / Let's unpack this. / Let's dive in. / Think of it as... / Imagine a world where...
> ✅ 直接说。

### 4.14 表面分析附加（Superficial Participle Analyses）
> ❌ 「contributing to the region's rich cultural heritage」「highlighting its importance」「underscoring the need」
> ✅ 如果分析句对任何主题都适用，就是废话。删，或给具体证据。

### 4.15 格式 AI 信号（Formatting Tells）
- **bold-开头的列表项**：每个列表项以粗体关键词开头，接冒号，接描述。→ AI 印记极强。改散文或用无粗体的简单列表。
- **em dash 堆砌**：最多每 500 字用一个 em dash。中文用逗号或分号替代破折号。
- **「Despite these challenges...」配方**：提到问题后必定跟模糊乐观的「ongoing initiatives」→ 要么具体说，要么删。
- **穿风衣的列表体（Listicle in a Trench Coat）**：以「The first... The second...」「First... Second... Third...」伪装的列表。→ 真需要列表就直接列表，别伪装成散文段落。

### 4.16 强调知名度/来源列举（Notability Overemphasis）
> ❌ 「Her views have been featured in Forbes, TechCrunch, Wired, and The New York Times...」
> ✅ 只在自然引用的地方提，不要罗列来源来证明「配得上被写」。

### 4.17 过度归因（Vague Attribution）
> ❌ 「Experts argue...」「Many believe...」「Studies show...」「It is widely regarded...」「Observers note...」
> ✅ 要么说清谁说的，要么不说。

### 4.18 假诚实（False Vulnerability / Performative Emphasis）
> ❌ 「And yes, I'm openly...」「This is not a rant; it's a diagnosis」「I promise」「They exist, I promise」「creeps in」
> ✅ 删。

### 4.19 假范围（False Ranges）
> ❌ 「From innovation to implementation to cultural transformation.」
> ✅ X 和 Y 之间没有真实谱系就不要用「from X to Y」结构。

### 4.20 优雅变体（Elegant Variation）
AI 为避免重复而循环使用同义词，有时重复更清晰。
> ❌ 「Soviet artistic constraints... non-conformist artists... their creativity... state-imposed artistic norms... the artistic aspirations...」
> ✅ 需要清晰时直接重复。「The Soviet government told artists what they could and couldn't paint. Yankilevsky painted what he wanted anyway.」

### 4.21 比喻滥用（Patronizing Analogies）
> ❌ 「Think of it as a Swiss Army knife.」「Think of it like a highway system for data.」
> ✅ 除非比喻能承担论证重量且经得起深究，否则直接解释概念。

---

## 五、分场景策略

### 5.1 技术文档 / API 文档 / 产品文案
**触发**：「技术文档」「API 文档」「产品文案」「界面文案」「帮助文档」

- 语气：克制、直接、可扫读
- 不用第二人称（「你」「您」）
- 不用「领先」「强大」「重磅」「颠覆」「震惊」「炸裂」等宣传形容词
- 不用「赋能」「抓手」「闭环」等黑话
- 不用感叹号
- 直角引号 `「」`
- 中英留白
- 不改代码字面量、JSON 键名、URL、API 路径
- 术语首次出现标注，后续不重复解释
- 不用「Hello」「Hi」等问候开篇
- 目标：说清楚「它是什么、用来做什么、下一步看哪里」

### 5.2 技术博客 / 长文
**触发**：「博客」「技术文章」「技术长文」「写一篇」「科普」

- 默认模式：资深工程师给同事讲系统的口吻
- 可以口语，但不俚语化
- 减少情绪词、感叹词、口头禅
- 少用「说白了 / 其实 / 你会发现 / 谁能想到」推进行文
- 优先追求：清楚、稳、具体、节奏自然
- 优先做减法：删解释腔、删总结腔、删多余转折
- 把润色做成减法，不是重写
- 如果原句已经自然，不改
- 非工程师受众：先去「不懂技术的同学」等居高临下词，去「你必须」等训人腔，去太深术语。走「我怎么用的，你试试」路径，不走「系统综述 + 框架表 + 长分析段落」

### 5.3 社交媒体 / 推文
**触发**：「推文」「X推文」「twitter」「社交发文」「post」

五规则：
1. **社区先行**：开头用社区锚点（star 数、感谢用户、谁的反馈推动），改动清单放后面
2. **亮点不全量**：挑 2-4 个最有意思的，读者要故事不是 changelog
3. **用户感受帧**：写法用「你用它的时候...」「有一种...的感觉」，不是「这个工具做了...」
4. **一条立场**：至少一句表明决策原因的意见句
5. **中文节奏**：用地道表达，避免翻译腔和正式词

- 结尾用邀请，不用 CTA
- 身份和敏感信号脱敏
- 不踩竞品
- 公开前扫三件事：脱敏、不踩竞品、用户感受先于功能清单

### 5.4 发行说明 / Release Notes
**触发**：「release」「changelog」「版本」「发行说明」

- 结构：Breaking Changes → New Features → Fixes & Improvements → Deprecations
- 格式：优先匹配目标项目最近一次 release 风格
- 条目：5-8 条，每条约一句话，只说用户效果
- title：版本号 + 最核心改动或主题，不超过 10 个词
- 不要加 emoji（除非项目本身庆祝风格）
- 不加「不再更新」「final release」「停止维护」等终止信号（除非真实情况）
- 中英双语：条目一一对应，不混写，英文在前

### 5.5 科学论文 / 学术写作
**触发**：「论文」「abstract」「cover letter」「grant」「manuscript」

- 保持学术正式度，但删除空洞套话
- 用「we」指自己工作（不用被动躲闪）
- 引用具体作者，不用「researchers have shown」
- 不用「It has long been recognized that...」
- 给出具体数字：「Each additional week of lead time added roughly 15% to the mean WIS」
- 不用「In today's rapidly evolving landscape」
- 不用「This paradigm shift has far-reaching implications」
- 不用「The results emerged from our analysis」
- 不用「It was observed that」

### 5.6 双语内容
**触发**：「双语」「中英」「bilingual」「翻译」

- 中英字符间加空格
- 不混用标点：中文用中文标点，英文用英文标点
- 术语跨全文一致
- 术语首次出现：保留英文 + 中文注解（或中文前置 + 英文括注）
- 后续只用中文，不要中英混用
- 常见可替换：context→上下文、state→状态、cache→缓存、claim→断言、runtime→运行时
- 术语未收敛的（prompt、embedding、tokenizer）保留英文合理
- 双语版：条目编号一一对应，确认 EN/CN 意思一致，标记翻译损失
- 禁止破折号

---

## 六、词汇替换表

### 6.1 中文替换（正式 → 口语）
| 不用 | 用 |
|------|-----|
| 非常 / 极其 | 很 |
| 值得注意的是 | 直接说结论 |
| 综上所述 / 总之 | 直接收尾 |
| 例如 | 比如 |
| 购买 | 买 |
| 使用 | 用 |
| 拥有 | 有 |
| 呈现 | 是 / 显得 |
| 进行（+动词）| 删掉「进行」，用动词本身 |
| 赋能 | 提供 / 帮助 |
| 抓手 | 关键措施 |
| 闭环 | 完整流程 |
| 沉淀 | 形成 / 积累 |
| 对齐 | 统一 |
| 拉通 / 打通 | 连接 / 贯通 |
| 洞察 | 分析结论 |
| 兜底 | 保障机制 |

### 6.2 英文替换
| 不用 | 用 |
|------|-----|
| serve as / stand as / marks / represents | is / are |
| boasts / features (as 'has') | has |
| leverage / utilize | use |
| harness | use / apply |
| streamline | simplify |
| navigate (challenges) | handle / address |
| unpack | explain / examine |
| deep dive | analysis / examination |
| delve | examine / look at / explore |
| robust | strong / solid / reliable |
| paradigm | model / system / approach |
| synergy | cooperation / combined effect |
| ecosystem | system / field / community |
| landscape | situation / field / area |
| tapestry | mix / combination / range |
| crucial / pivotal / vital | important / key |
| profound / indelible / paramount | significant (or delete) |
| showcase | show / display |
| underscore / highlight | point out / show |
| foster / cultivate | encourage / build |
| garner | get / receive |
| bolster | support / boost |
| facilitate | help / enable |
| consequently / thus / hence | so |
| furthermore / moreover / additionally | also / and |
| nonetheless / nevertheless | still / but |

---

## 七、执行流程

1. **先识别场景**：博客？技术文档？推文？论文？确定语气标准。
2. **先保语义**：确认不被改坏。
3. **做减法**：
   - 先扫段末总结句（中文最高频 AI 痕迹）
   - 再扫对比句式（「不是...而是...」）
   - 再扫喉清开场、元评论、强调拐杖
   - 再扫副词、被动语态、假主体
   - 再扫黑话、空洞形容词
4. **再顺句子**：节奏、标点、中英留白、破折号
5. **最后回读**：优先修不自然处，不强改自然处
6. **输出**：只给改写后的文本。不加改动清单、解释、收尾话。除非用户明确要求。

---

## 八、改写示例

### 示例 1：中文技术博客

**改写前：**
> 众所周知，随着云原生技术的不断发展，Kubernetes 已经成为了容器编排领域的事实标准。值得注意的是，虽然 K8s 本身功能强大，但在实际落地过程中，很多同学会发现它并不是银弹。本文将从多个维度深入探讨企业在落地 Kubernetes 时面临的挑战和应对策略，希望能为正在考虑或已经踏上云原生之旅的各位带来一些启发。

**改写后：**
> 我们团队用 Kubernetes 跑了三年生产环境。最大的感受：K8s 解决了部署问题，但把复杂度转移到了别的地方。这篇文章记录我们踩过的五个坑，以及每个坑的止损方案。

**改动点**：删了开篇套话、删了「值得注意的是」「很多同学」、删了对比句式「不是银弹」、删了「从多个维度深入探讨」、删了升华式结尾、换成了具体事实和个人经验。

### 示例 2：英文博客

**改写前：**
> Here's the thing: building reliable distributed systems is genuinely hard. It's not about making individual components bulletproof — it's about designing for partial failure from the ground up. Let that sink in. The implications are significant.

**改写后：**
> Distributed systems break in predictable ways. Network partitions, clock drift, and GC pauses each create failure modes that unit tests can't catch. We found three patterns that helped: timeouts with jitter, circuit breakers, and idempotent writes.

**改动点**：删了喉清开场、删了「genuinely」、删了对比句式、删了「Let that sink in」、删了空洞宣告（「The implications are significant」）、换成了具体事例。

### 示例 3：技术文档

**改写前：**
> 你好！欢迎使用我们的 API 服务！我们的平台提供领先的、强大的数据处理能力，能够赋能您的业务，助力您在数字化转型的赛道上实现弯道超车。使用前，您需要先进行 API Key 的申请。

**改写后：**
> API 提供以下数据处理能力：批量查询、实时推送、数据清洗。调用前需先申请 API Key，详见「认证」章节。

**改动点**：删了问候语、删了感叹号、删了宣传形容词+黑话链条、删了第二人称、把废话换成了功能清单。

### 示例 4：对比句式修复

**改写前：**
> 微服务架构的价值不在"微"，而在于边界清晰。

**改写后：**
> 微服务架构的价值在于边界清晰。

### 示例 5：「serves as」修复

**改写前：**
> The FluSight initiative serves as a foundational framework for influenza forecasting in the United States, contributing to public health preparedness and underscoring the importance of collaborative forecasting efforts.

**改写后：**
> The FluSight initiative coordinates influenza forecasting across dozens of modeling groups in the United States. Since 2013, it has standardized targets, submission formats, and evaluation metrics.

---

## 九、质量评分（可选用）

五个维度，每维 1-10 分，低于 35/50 需修订：

| 维度 | 问题 |
|------|------|
| 直接性 | 是在陈述事实还是在预告/总结？ |
| 节奏 | 句子长短有变化还是千篇一律？ |
| 信任 | 有没有低估读者智商（解释过度、灌输腔）？ |
| 真实度 | 读起来像人写的还是像 AI 生成的？ |
| 密度 | 还有能删的吗？ |

---

## 十、相关技能

- `tech-doc-style-chinese`：中文技术文档排版专项（直角引号、中英留白、黑话规避）
- `write`：多场景中文写作（推文、发行说明、双语、文档审稿）
- 英文去 AI 味参考：本技能第四、六节已覆盖核心模式
