# 人物一致性模块

这是一个专门处理人物一致性问题的专项模块。

它主要解决：

- 人物形象不符
- 情绪跳变
- 行为和既有人设不匹配
- 关系状态断片
- 身体状态和伤势忘记了
- 说话方式前后不一致

## 什么时候调用

当任务明确涉及这些问题时，优先调用本模块：

- 用户说“人物崩了”“不像这个人会做的事”
- 上一场和下一场像两个人
- 前面恨得发抖，后面忽然温柔体贴
- 伤势、目标、秘密、关系状态跨场景丢失

## 建议阅读顺序

1. 先读 [tutorial.md](tutorial.md)。
2. 再读 [runtime.md](runtime.md)。
3. 去 [good_examples.md](good_examples.md) 找对应的连续性结构。
4. 去 [bad_examples.md](bad_examples.md) 看断片类型。
5. 先写状态连续计划，再改正文。

## 文件说明

- [tutorial.md](tutorial.md)
  把人物一致性拆成目标、情绪、关系、身体、声音五层。
- [runtime.md](runtime.md)
  给模型的实际处理顺序。
- [good_examples.md](good_examples.md)
  先用结构正例描述什么叫“前后对得上”。
- [bad_examples.md](bad_examples.md)
  集中列常见崩人设写法。
- [source_index.md](source_index.md)
  标明本模块与转场、对白模块的关系。
