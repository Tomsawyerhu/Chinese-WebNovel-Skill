# webnovel-writing-skill

note:目前写了几个短篇，质量大家可以自己判断

这是一个面向中文网文写作的 Codex skill。它的目标不是讨论“文学性”本身，而是把网文写作里最实用、最可复用的部分沉淀下来，让模型在收到一个小说简介后，能更稳定地完成这些工作：

- 判断题材和卖点是否适合写成网文
- 把简介压成 hook、premise、故事引擎、卷规划和章纲
- 生成开头、单章、章末和改写版本
- 先检索本地范本，再做结构化借鉴
- 尽量减少空泛、平均、同质化的 AI 味

`SKILL.md` 是给模型运行时读取的说明；这份 `README.md` 是给维护这个 skill 的人看的，重点解释目录结构、语料资产，以及“新来一批小说时该怎么蒸馏它们”。

## 目录结构

```text
webnovel-writing-skill/
├── SKILL.md
├── README.md
├── agents/
│   └── openai.yaml
├── references/
│   ├── webnovel_outline_template.md
│   ├── webnovel_chapter_template.md
│   ├── webnovel_quality_checklist.md
│   └── webnovel_corpus_guide.md
├── scripts/
│   ├── scrape_yanxuan_recent_posts.py
│   ├── fetch_content_raw.py
│   ├── build_webnovel_corpus_assets.py
│   └── search_corpus_examples.py
├── data/
│   ├── metadata.csv
│   ├── metadata.jsonl
│   └── articles/
└── analysis/
    ├── article_profiles.csv
    ├── article_profiles.jsonl
    ├── excerpts.csv
    ├── excerpts.jsonl
    ├── imitation_index.md
    └── stats.json
```

## 这个 skill 怎么工作

它大致分成两层：

1. `SKILL.md` 规定运行时策略。
   模型收到“帮我写一个真假千金女频文开头”之类请求时，先做题材诊断、结构拆解，再决定要不要先查范本。

2. `data/` + `analysis/` 提供本地语料支持。
   `data/articles/` 放原始小说文本；`analysis/` 是从这些原文自动蒸馏出来的摘要、标签、摘录和索引，供检索脚本和模型模仿流程使用。

换句话说，这个 skill 的上限，很大一部分取决于语料蒸馏得好不好。

## 日常使用

### 1. 直接用 skill 写东西

只要用户给一个简介，skill 会优先产出当前最需要的一层，例如：

- 题材诊断
- 一句话 hook
- premise
- 故事引擎
- 第一卷规划
- 前 10-20 章章纲
- 开头重写
- 单章正文

### 2. 先查本地范本

当任务涉及开头、对白、章末、题材模仿、盐选风借鉴时，优先用本地语料检索。

常用命令：

```bash
python3 scripts/search_corpus_examples.py --list-tags
python3 scripts/search_corpus_examples.py --list-types
python3 scripts/search_corpus_examples.py --type '开头钩子' --tag '危机压身' --limit 5
python3 scripts/search_corpus_examples.py --type '高张力对白' --tag '关系破裂' --limit 5
python3 scripts/search_corpus_examples.py --keyword '真假千金' --limit 10
```

检索到摘录后，不要停在一句话层面。要回查 `analysis/imitation_index.md` 和 `data/articles/` 的上下文，看它前面怎么铺、后面怎么收。

## 新小说来了，怎么蒸馏

这是这份 README 最重要的一节。

这里说的“蒸馏”，不是把新小说全文塞进 prompt 里，也不是把某篇文“训练成模型记忆”。这里的蒸馏是指：

- 把原文变成可检索、可归纳、可复用的本地资产
- 保留结构信息，不保留不可迁移的表面句子
- 让模型学到“这种文是怎么起势、怎么投信息、怎么留章末”的规律

最实用的理解方式是：

`原文 -> 清洗 -> 摘要 -> 标签 -> 结构摘录 -> 索引 -> 检索使用`

### 一、先决定值不值得进库

不是所有小说都值得蒸馏。优先收这些：

- 开头有明显抓手，前 300-500 字就能看出异常局面
- 卖点和冲突绑得紧，不是纯设定介绍
- 题材足够典型，能代表一个常见消费点
- 某个局部特别强，比如开头、主角亮相、对白、章末
- 能补足当前语料缺口，比如某类题材太少、某种关系流不够

不建议优先进库这些：

- 设定很大但前几章不起事
- 情绪很多但事件很弱
- 语言表面花哨，但结构价值不高
- 和现有样本高度重复，不能带来新的结构信息

蒸馏的核心不是“这篇文好不好看”，而是“它有没有可迁移的结构价值”。

### 二、把原文放进 `data/articles/`

这个仓库现在的构建脚本会直接扫描 `data/articles/*.txt`。

每篇文章应满足这些约定：

- 文件编码用 UTF-8
- 第一行是标题
- 后续正文按自然段分行
- 文件名延续当前的四位数字前缀，例如 `0167-标题.txt`

推荐继续用递增编号，而不是改旧文件名。原因很简单：

- `build_webnovel_corpus_assets.py` 会按 `data/articles/*.txt` 的排序重新生成 `A001`、`A002` 这类文章编号
- 如果你随意重命名旧文件，后续索引编号会整体漂移
- 用新的四位数字前缀往后追加，可以尽量保证旧索引稳定

### 三、同步元数据

虽然分析脚本主要依赖 `data/articles/`，但 `data/metadata.csv` 和 `data/metadata.jsonl` 仍然应该同步更新，用来保留这些来源信息：

- 原始标题
- 发布时间
- 来源 URL
- 对应文件路径
- 抓取是否成功
- 字数和报错信息

如果是从站点批量抓取，先抓到临时目录，不要直接覆盖当前 `data/`：

```bash
python3 scripts/scrape_yanxuan_recent_posts.py --output-dir tmp/yanxuan-import --limit 20
```

它会：

- 抓首页 recent posts
- 提取正文
- 在临时目录下写入 `articles/`
- 同时生成该批次的 `metadata.csv` 和 `metadata.jsonl`

这样做的原因是：

- 这个抓取脚本当前会从 `0001` 开始给文件编号
- 如果直接输出到现有 `data/`，很容易覆盖旧语料
- 正确做法是先抓一批候选，再人工挑选值得蒸馏的文本，并按主库编号规则并入 `data/articles/`

如果是手工补录，也建议按现有字段格式补齐元数据，不要只丢一个 txt 文件进去。

### 四、重建蒸馏资产

原文入库后，执行：

```bash
python3 scripts/build_webnovel_corpus_assets.py
```

这个脚本会自动生成：

- `analysis/article_profiles.csv`
- `analysis/article_profiles.jsonl`
- `analysis/excerpts.csv`
- `analysis/excerpts.jsonl`
- `analysis/imitation_index.md`
- `analysis/stats.json`

它当前做的蒸馏主要包括：

- 从前几段抽取文章摘要
- 根据关键词打题材标签
- 为每篇文固定抽四类结构摘录
- 生成总索引，方便回查原文

当前固定四类摘录是：

- 开头钩子
- 主角亮相
- 高张力对白
- 结尾余韵

这四类不是文学分类，而是“写作最常复用的结构部件”。

### 五、做一轮人工校验

自动构建只是第一步，蒸馏有没有价值，最后还是要靠人工过一遍。

至少检查这些问题：

- 标题和摘要是不是基本对应
- 标签有没有明显打错
- 开头摘录是不是确实抓到了前期卖点
- 对白摘录是不是有真实张力，而不是随便抓到一句话
- 章末摘录是不是停在变化上，而不是收束废话
- 新样本有没有补到现有语料的空白区

推荐跑几条检索命令做 spot check：

```bash
python3 scripts/search_corpus_examples.py --list-tags
python3 scripts/search_corpus_examples.py --type '开头钩子' --tag '身份反差' --limit 5
python3 scripts/search_corpus_examples.py --type '结尾余韵' --tag '危机感' --limit 5
python3 scripts/search_corpus_examples.py --keyword '你刚新增的题材词' --limit 10
```

然后手看：

- `analysis/imitation_index.md`
- `analysis/article_profiles.csv`
- `analysis/excerpts.csv`

### 六、必要时改规则，不要硬塞脏数据

如果你发现新小说反复蒸馏不好，先别急着往库里硬塞，优先判断是哪一层出了问题：

- 如果摘要不准，可能是正文清洗规则有问题
- 如果标签不准，可能需要补 `KEYWORD_TAGS`
- 如果对白老是抓歪，可能需要改 `score_dialogue`
- 如果开头和章末总抽不准，可能需要调整摘录策略

这些规则都在：

- `scripts/build_webnovel_corpus_assets.py`

维护原则很简单：

- 优先改规则，让同类样本都变好
- 不要为某一篇特例写一堆硬编码
- 不要把“作者句子好看”误当成“适合蒸馏”

## 蒸馏时到底该保留什么

建议重点保留这些信息：

- 题材标签
- 核心卖点
- 冲突起势方式
- 主角出场方式
- 信息投放方式
- 对白如何带身份差和后果
- 章末停在哪个变化点上

不要把这些当作蒸馏重点：

- 某一句漂亮文案
- 某个作者习惯用的口头禅
- 过强的表面修辞
- 可以直接识别来源的句式复制

一句话概括：

蒸馏的是结构，不是腔调；是机制，不是原句。

## 什么时候该补新样本

通常有四种信号：

1. 模型在某类题材上总给出很泛的答案，说明本地范本不够。
2. 某种需求经常出现，但现有标签检索不到合适案例。
3. 某个类型的开头、对白或章末明显不够强。
4. 新平台、新题材、新关系模式已经形成稳定套路，但语料库还没覆盖。

补样本时，不要只追数量。对这个 skill 来说，`更全的题材覆盖 + 更清晰的结构标签`，通常比单纯多几十篇相似小说更有用。

## 推荐维护节奏

- 每次新增一批小说后，立刻重建一次 `analysis/`
- 每隔一段时间看一次 `analysis/stats.json`，确认标签分布有没有失衡
- 如果某类检索结果一直很差，先回头修蒸馏规则，再继续加样本
- 新增 reference 时，尽量放“操作说明”或“判断标准”，不要重复 `SKILL.md`

## 相关文件

- `SKILL.md`: skill 的运行时总说明
- `references/webnovel_corpus_guide.md`: 怎么检索和借鉴本地范本
- `references/webnovel_quality_checklist.md`: 开头、章末、场景、连载检查项
- `references/webnovel_outline_template.md`: 大纲模板
- `references/webnovel_chapter_template.md`: 章节模板

如果后面要继续扩这个 skill，最值得优先投入的方向通常不是“再写更多说明文”，而是把语料蒸馏得更稳、更干净、更容易检索。
