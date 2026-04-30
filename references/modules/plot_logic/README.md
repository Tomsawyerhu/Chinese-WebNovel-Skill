# 剧情逻辑模块

这是一个专门处理网文剧情逻辑问题的专项模块。

它主要解决：

- 剧情逻辑不符
- 因果断裂
- 动机不足
- 事件推进靠作者硬推
- 伏笔回收失衡
- 爽点、反转、误会、打脸没有前提支撑

## 什么时候调用

当任务明确涉及这些问题时，优先调用本模块：

- 用户说“剧情逻辑不通”
- 人物忽然做了一个缺前提的决定
- 重要事件像从天而降
- 误会、反转、掉马、打脸来得太硬
- 章节与章节之间像靠作者拖动，而不是靠人物和局势自发推进

## 建议阅读顺序

1. 先读 [tutorial.md](tutorial.md)。
2. 再读 [runtime.md](runtime.md)。
3. 去 [good_examples.md](good_examples.md) 找近似结构。
4. 去 [bad_examples.md](bad_examples.md) 找近似断点。
5. 先写因果链计划，再改正文。

## 文件说明

- [tutorial.md](tutorial.md)
  把剧情逻辑拆成动机、触发、决策、后果、兑现五层。
- [runtime.md](runtime.md)
  给模型的实际处理顺序。
- [good_examples.md](good_examples.md)
  用结构化正例说明什么叫“因果接得住”。
- [bad_examples.md](bad_examples.md)
  集中列最常见的逻辑断裂。
- [source_index.md](source_index.md)
  标明本模块目前主要来自主 skill 的结构要求。
