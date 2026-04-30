---
name: webnovel-writing
description: 用于根据一段中文小说简介，规划、起稿、续写、改写中文网文。重点覆盖选材、构思、分卷、章纲、开头、节奏、章末、模仿检索、去 AI 味。
---

# 中文网文写作 Skill

## 定位

这是一个面向中文网文的写作 skill。

它解决的不是“文学表达够不够高级”，而是这些更实际的问题：

- 这个点子值不值得写成网文
- 这本书到底卖什么
- 前 10-20 章靠什么持续推进
- 开头怎么成交
- 中段怎么不散
- 章末怎么留后劲
- 怎么检索相似范本再借结构
- 怎么在全过程里避免 AI 味

## 默认输入

输入默认就是：

`一段对目标小说的简要描述`

默认行为：

1. 先从简介里提炼题材、卖点、冲突、故事引擎、目标长度。
2. 先判断当前任务属于前置规划、开头、章纲、单章、局部修复还是完稿审查。
3. 如果信息够用，直接进入当前最需要的一层；如果不够，只补最少量澄清。

## 输出原则

默认只输出当前最需要的一层，不把所有东西一次性堆满。

常见输出层：

- 题材诊断
- 一句话 hook
- premise
- 故事引擎说明
- 第一卷规划
- 前 10-20 章章纲
- 开头重写
- 单章正文
- 章末加压
- 节奏体检
- 模仿参考清单

## 总流程

1. 先判断问题在前置规划、结构、单章执行还是完稿审查。
2. 如果问题已经明显收束到某一个写作环节，优先调用专项模块，不要只做泛建议。
3. 默认先匹配模块例子或本地语料，再总结结构，再写新内容。
4. 去 AI 味不是最后随便润色，而是从构思、场景、对白、章末就开始约束。
5. 每章写完默认必须过审查模块，不能直接交稿。

## 模块职责速查

- `concept_planning`
  作用：把简介压成题材、消费点、hook、premise、故事引擎、长度判断和第一卷方向。
  阶段：前置规划层。
- `opening`
  作用：把卖点、异常局面和主角亮相落到开头成交区。
  阶段：开篇执行层。
- `volume_outline`
  作用：把故事引擎展开成黄金三章、分卷和前 10-20 章章纲。
  阶段：中长线结构层。
- `plot_logic`
  作用：修动机、触发、决策、后果、兑现这条因果链。
  阶段：正文执行层的底层结构模块。
- `character_consistency`
  作用：修目标、情绪、关系、身体、声音五类人物连续性。
  阶段：正文执行层的人物状态模块。
- `transition`
  作用：处理时间跳切、空间切换、情绪承接、视角切换和章末接下章。
  阶段：正文执行层的场景桥梁模块。
- `dialogue`
  作用：处理关系压力、人物声音、信息嵌入和对白刀口。
  阶段：正文执行层的对白模块。
- `chapter_ending`
  作用：处理章末拉力、余韵、回钩和下章承接。
  阶段：正文执行层的章节收束模块。
- `anti_ai_voice`
  作用：清理空泛总结、套话氛围、说明书式对白和统一腔调。
  阶段：正文执行层的风格约束模块。
- `consistency_review`
  作用：统一复查六种一致性，阻止问题章直接交稿。
  阶段：完稿收口层。

## 模块关系

默认把模块理解成三段链路，而不是十个平铺开关：

1. 前置规划链：
   `concept_planning -> opening / volume_outline`
2. 正文执行链：
   `plot_logic + character_consistency + transition + dialogue + chapter_ending + anti_ai_voice`
3. 完稿收口链：
   `consistency_review`

如果一个问题同时跨多个模块，优先级通常是：

1. `plot_logic` / `character_consistency`
2. `transition` / `dialogue` / `chapter_ending`
3. `anti_ai_voice`

不要把结构问题直接误修成文风问题。

## 前置规划

涉及这些问题时，默认调用 `concept_planning` 模块：

- 这个点子能不能写成网文
- 题材和消费点清不清
- 卖点和异常局面亮不亮
- hook / premise 立不立得住
- 故事引擎能不能跑过前 10-20 章
- 更适合短篇、中篇、长篇还是连载
- 第一卷最小目标和卷末变化清不清

这一步的硬要求是：

- 先判断值不值得写，再写正文
- 先给卖点、冲突、故事引擎，再给大设定
- 简介压不成最小骨架时，不要急着开写

## 开头

涉及这些问题时，默认调用 `opening` 模块：

- 开头没抓手
- 卖点露头太慢
- 异常局面不够立
- 黄金三章起得慢

默认要求：

- 前 300-500 字给抓手
- 前 1500-3000 字给卖点
- 前 6000 字让读者知道主角是谁、遇到什么、卖点是什么、接下来想看什么

## 黄金三章、分卷与章纲

涉及这些问题时，默认调用 `volume_outline` 模块：

- 黄金三章推进无力
- 第一卷跑法不清
- 前 10-20 章章纲散
- 中段容易发散
- 卷末没有兑现点

长篇网文默认必须写章纲。

没有章纲，最容易出现这些问题：

- 支线乱长
- 设定膨胀
- 章末疲软
- 追更点断掉

## 逐章写作

### 每章必须回答四件事

1. 主角这章想做什么
2. 谁或什么阻止他
3. 这章结束后局面变成什么
4. 为什么读者还要往下看

### 场景最小结构

每场戏至少要有：

- 目标
- 阻碍
- 变化

没有变化的场景，默认删、并、压缩。

### 局部问题默认路由

- 时间跳切、空间切换、情绪承接、视角切换、章末接下章：调用 `transition`
- 高张力对白、人物声音、关系施压、信息嵌入：调用 `dialogue`
- 章节收束、余韵、回钩、追更拉力、下章承接：调用 `chapter_ending`
- 因果断裂、动机不足、触发不成立、后果不落地：调用 `plot_logic`
- 人设崩、目标漂移、情绪断片、关系断片、身体和声音连续性丢失：调用 `character_consistency`
- 空泛总结、套话氛围、对白像说明书、人物一个腔调：调用 `anti_ai_voice`

### 章节完稿后的强制审查

每一章写完，都不要直接交付，默认必须先调用 `consistency_review` 模块。

每章必查这六种一致性：

1. 剧情逻辑一致性：
   关键事件有没有前提；
   关键决定有没有触发；
   关键变化有没有后果。
2. 人物目标一致性：
   主角这章到底想做什么；
   过程中有没有无故漂移。
3. 情绪与关系一致性：
   情绪有没有来路；
   关系温度是不是和上一场对得上。
4. 身体与信息状态一致性：
   伤势、疲劳、秘密、误会、已知信息有没有丢。
5. 场景与转场一致性：
   读者会不会迷路；
   上一场余力有没有被带到下一场。
6. 章末承接一致性：
   章末有没有收在变化上；
   下一章第一拍能不能接住。

任意两项不稳，不要直接交稿，先回对应专项模块修。

## 模块调用总则

如果问题已经明显收束到某一个写作环节，不要只做泛建议，默认优先调用专项模块。

通用顺序是：

1. 先判断这是不是专项问题，而不是纯文风问题。
2. 先看 [references/modules/README.md](references/modules/README.md)，再进入对应模块目录。
3. 先读模块自己的 `README.md`，再按模块推荐顺序进入 `tutorial.md`、`runtime.md` 和例库。
4. 先按模块里的层级和分类法判断故障点。
5. 去模块例库里选 `2-4` 个正例和 `1-2` 个反例。
6. 先做局部修复计划，再写诊断、改写或正文。

如果一个问题同时跨多个模块，先修更底层、更硬的那一层，再修更表层的问题。

## 模仿与检索

这个 skill 默认要求在写作中多搜索相似范本，再借结构写新内容。

不是只有用户说“请模仿”时才查。只要任务涉及这些内容，就优先先查本地语料：

- 某种题材
- 某种开头
- 某种对白
- 某种章末
- 某种关系流

如果问题已经明确收束到某个专项环节，也要优先调用专项模块，而不是只停留在泛检索。

### 找模块的方式

1. 先看 [references/modules/README.md](references/modules/README.md)。
2. 再按问题关键词直达模块目录：
   `concept_planning / opening / transition / dialogue / chapter_ending / plot_logic / character_consistency / consistency_review / volume_outline / anti_ai_voice`
3. 进模块后先读模块 `README.md`，再按该模块自己的建议顺序读 `tutorial.md`、`runtime.md`、`good_examples.md`、`bad_examples.md`。

### 当前本地语料

主要文件：

- [analysis/article_profiles.csv](analysis/article_profiles.csv)
- [analysis/excerpts.csv](analysis/excerpts.csv)
- [analysis/imitation_index.md](analysis/imitation_index.md)
- [references/webnovel_corpus_guide.md](references/webnovel_corpus_guide.md)

### 检索脚本

使用：

- [scripts/search_corpus_examples.py](scripts/search_corpus_examples.py)

常用命令：

```bash
python3 scripts/search_corpus_examples.py --list-tags
python3 scripts/search_corpus_examples.py --list-types
python3 scripts/search_corpus_examples.py --type '开头钩子' --tag '危机压身' --limit 5
python3 scripts/search_corpus_examples.py --type '高张力对白' --tag '关系破裂' --limit 5
python3 scripts/search_corpus_examples.py --keyword '真假千金' --limit 10
```

### 模仿流程

1. 先判断用户在写什么。
2. 去索引里找 `2-4` 个相似例子。
3. 总结这些例子的共同结构。
4. 再写新内容。

如果是专项问题，改成：

1. 先判断是不是该调用专项模块。
2. 在专项模块里判层级和类型。
3. 按专项模块的例库分组去选材。
4. 先做桥梁或结构计划。
5. 再写正文。

如果已经写完一章，还要补一步：

6. 调用 `consistency_review`，过完六种一致性后再交稿。

## 去 AI 味

这是硬要求，但主 skill 不再重复铺完整教程。

当任务集中在这些问题上时，直接调用 `anti_ai_voice` 模块：

- 空泛总结太多
- 气氛句和形容词套话太多
- 对白像说明书
- 角色说话一个腔调
- 句子太平均、太工整、太像模板生成

仍然保留的硬规则：

- 能用动作，不用总结
- 能用对白，不用解释
- 能写具体，不写抽象
- 每个人说话必须带身份感
- 不要把“去 AI 味”理解成故意粗糙

## 边界

### 不要做的事

- 不要空谈“人物要立体”“故事要有灵魂”
- 不要只给世界观，不给前几章方案
- 不要只给人设，不给冲突和事件
- 不要默认慢热
- 不要把模仿当成照抄
- 不要让对白全都一个腔调
- 不要输出像课程讲义一样的废话段落

### 默认鼓励的事

- 多举具体例子
- 多做正反对照
- 多给可落地写法
- 多查本地范本
- 多用结构借鉴替代空泛建议

## 模块与搜索

- 模块总入口：
  [references/modules/README.md](references/modules/README.md)
- 模块模板：
  [references/modules/module_template.md](references/modules/module_template.md)
- 语料检索总说明：
  [references/webnovel_corpus_guide.md](references/webnovel_corpus_guide.md)
- 检索脚本：
  [scripts/search_corpus_examples.py](scripts/search_corpus_examples.py)
