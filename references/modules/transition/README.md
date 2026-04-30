# 转场模块

这是一个专门处理中文网文转场问题的独立模块。

这次模块的组织方式，已经按 `sources/raw/` 里的最新资料重排过，不再把转场仅仅当成“几种技巧”，而是拆成四层：

- 新手能立刻上手的常用法
- 按时间/空间/视角/情绪分类的方法库
- 更底层的“借力、关联、镜头、蒙太奇、空镜”思维
- 适配网文写作时的运行顺序

## 模块目标

这个模块主要解决：

- 转场生硬
- 场景切换突兀
- 时间跳切像硬剪
- 空间切换只报地点、不带事件
- 情绪承接断裂
- 视角切换像强行插播
- 章末和下一场接不上
- 回忆、插叙、梦境、蒙太奇边界混乱

## 现在这套模块怎么读

推荐按这个顺序用：

1. 先读 [source_index.md](source_index.md)，知道这批资料的来源和重点。
2. 再读 [tutorial.md](tutorial.md)，建立统一的转场方法框架。
3. 写作或改稿时，按 [runtime.md](runtime.md) 的顺序判断问题类型。
4. 去 [good_examples.md](good_examples.md) 找 2-4 个近似正例。
5. 去 [bad_examples.md](bad_examples.md) 找 1-2 个近似反例。
6. 先搭桥，再写正文。

## 文件说明

- [tutorial.md](tutorial.md)
  这份是主教程，已经把 `raw` 里的教程重新整成一套可执行框架。
- [good_examples.md](good_examples.md)
  15+ 个正例，重点看“为什么顺”。
- [bad_examples.md](bad_examples.md)
  15+ 个反例，重点看“断在哪里”。
- [runtime.md](runtime.md)
  给模型的执行顺序，不是理论材料。
- [source_index.md](source_index.md)
  对 `raw` 原始资料做了分组、去重和重点提炼。

## 文件结构

```text
transition/
├── README.md
├── tutorial.md
├── good_examples.md
├── bad_examples.md
├── runtime.md
├── source_index.md
└── sources/
    ├── raw/
    └── raw_html/
```

## 说明

- 当前模块的“主参考”是 `sources/raw/` 里的最新资料。
- `raw_html/` 保留的是额外网页原件，方便后续补档，但本轮重组不以它为主。
- 正例强调可迁移结构，不强调句子皮相。
- 反例不是为了嘲笑拙劣写法，而是为了帮助模型识别硬切、漏因果、断情绪这些常见失误。
