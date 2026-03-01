# CFMC-Research

**汉语系表隐喻构式认知框架研究**

*A Corpus-Based Study on the Cognitive Mechanisms of Chinese Copular Metaphorical Constructions*

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXXX-blue)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![Corpus](https://img.shields.io/badge/Corpus-5989%20constructions-blue)](CFMC_5989.json)
[![Scripts](https://img.shields.io/badge/Scripts-29%20Python-green)](scripts/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-brightgreen)](https://chenwangfang.github.io/cfmc-research/visualization/)
[![中文](https://img.shields.io/badge/中文-README-red)](README.md)
[![English](https://img.shields.io/badge/English-README-orange)](README_EN.md)

---

> **快速链接**：[语料库](CFMC_5989.json) | [PLS-SEM模型设计](PLS-SEM形成性测量模型设计.md) | [在线演示](https://chenwangfang.github.io/cfmc-research/visualization/) | [English](README_EN.md)

## 项目简介

本研究基于Sullivan (2013) 的隐喻构式理论，构建**汉语系表隐喻构式认知框架（CFMC: Cognitive Framework for Metaphorical Constructions）**，通过5989条标注语料，采用**PLS-SEM形成性测量模型**验证四阶段认知编码机制。

### 研究目标

1. **类型特征**：建立基于认知通达度—映射方向双维度的12类构式分类体系
2. **网络组织**：揭示构式网络的小世界结构特征与社区组织规律
3. **认知机制**：通过PLS-SEM形成性测量模型验证四阶段认知编码机制

### 核心贡献

- **语料库**：5989条双盲标注的汉语系表隐喻构式
- **字段体系**：CFMC-33字段体系（33项必填+8项选填）
- **分类体系**：12类构式类型的GMM聚类验证
- **网络模型**：两层构式网络（构式层+类型层）
- **认知模型**：四阶段认知编码机制的PLS-SEM形成性测量模型验证

---

## 研究问题与假设

| 问题 | 内容 | 假设 | 章节 |
|:-----|:-----|:-----|:-----|
| **Q1** | 类型特征 | H1-1: 认知通达度与概念复杂度负相关 (*r* = -0.40至-0.60)<br>H1-2: GMM聚类验证12类构式分类 (*k*=12, 轮廓系数≥0.30) | 第5章 |
| **Q2** | 网络组织 | H2: 构式网络呈现小世界特征 (*C*≥0.60, *L*≤3.0, σ>1) | 第6章 |
| **Q3** | 认知机制 | H3-1: PLS-SEM验证四阶段路径 (GoF>0.25, 路径系数显著 *p*<.05; PLS-MGA按系词功能分3组验证跨类型共享性)<br>H3-2: 类型差异调节效应 (*r*≥0.30, *p*<0.05) | 第7章 |

---

## 目录结构

```
cfmc-research/
├── README.md                    # 中文说明
├── README_EN.md                 # 英文说明
├── LICENSE                      # CC BY-NC 4.0许可证
├── CITATION.cff                 # 引用信息（GitHub自动识别）
├── .gitignore                   # Git忽略配置
│
├── CFMC_5989.json               # 核心语料库（5989条，13MB）
├── PLS-SEM形成性测量模型设计.md  # PLS-SEM形成性测量模型设计文档
│
├── Data/                        # 统计分析结果（67个CSV + 49个JSON + 2个GraphML）
│   ├── 表57a_源域分布.*
│   ├── PLS_路径系数表.csv
│   ├── PLS_模型拟合比较.csv
│   └── ...
│
├── figures/                     # 可视化图表（39个PNG）
│   ├── 图1 研究路径图.png
│   ├── 图29_四阶段认知编码机制路径与中介效应图.png
│   ├── PLS_路径模型图.png
│   └── ...
│
├── scripts/                     # Python分析脚本（29个）
│   ├── Q1_01_描述统计.py
│   ├── Q2_01_网络构建.py
│   ├── Q3_02_PLS_SEM基础模型.py
│   └── 一键运行全部脚本.py
│
├── appendix/                    # 附录文档
│   ├── 语料标注方案_附录A.md
│   ├── CFMC-33字段体系_附录B.md
│   ├── 认知通达度的构念界定与测量方案_附录C.md
│   ├── 附录C_1.csv                     # 附录C试点研究数据（500样本）
│   ├── 概念复杂度的构念界定与测量方案_附录D.md
│   ├── 信度效度验证_附录E/
│   ├── 统计分析补充材料_附录F.md
│   └── 概念复杂度和认知通达度快速取值手册.md
│
└── visualization/               # 交互式可视化
    └── index.html
```

---

## 数据说明

### CFMC_5989.json

核心语料库，包含5989条汉语系表隐喻构式的完整标注。

**字段体系（CFMC-33）**：

| 层级 | 字段数 | 内容 |
|:-----|:------:|:-----|
| 基础识别字段 | 6 | 编号、句子、构式形式、来源等 |
| Level 1核心字段 | 23 | 认知通达度、概念复杂度、映射方向、系词功能等 |
| Level 2补充字段 | 4 | 汉语特色特征 |
| Level 3-4选填字段 | 8 | 质性标注内容 |

**示例结构**：
```json
{
  "metadata": {
    "description": "CFMC-33汉语系表隐喻构式标注语料库",
    "field_count": 45,
    "construction_count": 5989
  },
  "constructions": [
    {
      "original_id": "zh55588",
      "full_sentence": "会议认为，总路线是建设社会主义的锐利武器...",
      "construction": "总路线是建设社会主义的锐利武器",
      "cognitive_accessibility": 4.0,
      "conceptual_complexity": 2.0,
      "mapping_direction": 2.0,
      ...
    }
  ]
}
```

**示例字段计算过程**（以zh55588为例）：

| 字段 | 值 | 计算/判定依据 |
|:-----|:--:|:--------------|
| `mapping_direction` | 2.0 | 源域"锐利武器"（具体）→ 目标域"总路线"（抽象），属"具→抽"类型，编码为2 |
| `cognitive_accessibility` | 4.0 | 公式：0.55×*D*reg + 0.45×*D*trans；"武器"为高频常规隐喻，*D*reg≈0.8，*D*trans≈0.7，原始分≈0.76（较高水平），经五分位数转换后标注为4级 |
| `conceptual_complexity` | 2.0 | 原始分经五分位数转换；该构式处于全体语料第20-40%分位（较简单级），与MD=2类型均值（2.002±0.853）一致 |

> 详细测量方案见附录C（认知通达度）和附录D（概念复杂度）。

<details>
<summary><strong>概念复杂度计算公式体系</strong>（点击展开）</summary>

**公式D-3（最终公式）**：
```
概念复杂度原始分 = 0.55 × D_abstract + 0.45 × D_processing
```
原始分范围[0, 1]，经五分位数法转换为1-5级量表。

**公式D-1：认知域抽象程度**
```
D_abstract = 0.25×F_field + 0.50×A_level + 0.25×D_number
```

| 参数 | 含义 | 取值 |
|:-----|:-----|:-----|
| *F*field | 领域类型 | 日常具体=0.20，日常抽象=0.40，专业具体=0.60，专业抽象=0.80，哲学抽象=1.00 |
| *A*level | 抽象等级 | 基本具体=0，一阶抽象=0.33，二阶抽象=0.67，高阶抽象=1.00 |
| *D*number | 认知域数量 | 单一域=0.20，2-3域=0.40，4-5域=0.60，6+域=0.80，高度复杂=1.00 |

**公式D-2：映射加工深度**
```
D_processing = 0.6×I_depth + 0.4×S_schema
```

| 参数 | 含义 | 取值 |
|:-----|:-----|:-----|
| *I*depth | 推理深度 | 直接映射=0，一步推理=0.33，多步推理=0.67，深层推理=1.00 |
| *S*schema | 意象图式复杂度 | 单一简单=0，单一复杂=0.33，多图式组合=0.67，复杂网络=1.00 |

**五分位数转换**：
- [0%, 20%) → 1级（极简单）
- [20%, 40%) → 2级（较简单）
- [40%, 60%) → 3级（中等）
- [60%, 80%) → 4级（较复杂）
- [80%, 100%] → 5级（极复杂）

**示例zh55588验证**（"总路线是建设社会主义的锐利武器"，MD=2）：

| 参数 | 值 | 说明 |
|:-----|:--:|:-----|
| *F*field | 0.80 | 目标域"总路线"属专业抽象领域（政治概念） |
| *A*level | 0.33 | 一阶抽象（从具体政策抽象而来） |
| *D*number | 0.40 | 激活2-3个认知域（政治域、行动域、目标域） |
| *I*depth | 0.33 | 一步推理（武器功能性→总路线作用） |
| *S*schema | 0 | 单一简单图式（力图式） |

计算：*D*abstract = 0.25×0.80 + 0.50×0.33 + 0.25×0.40 = 0.465，*D*processing = 0.6×0.33 + 0.4×0 = 0.198，原始分 = 0.55×0.465 + 0.45×0.198 ≈ 0.345（较低水平）。标注值2.0与MD=2类型均值（2.002±0.853）一致。

</details>


### 数据表索引

**Q1类型特征分析（第5章）**：表57-72 + 补充表S1-S6
**Q2网络组织分析（第6章）**：表73-87
**Q3认知机制分析（第7章）**：表92 + PLS-SEM系列数据文件（路径系数、模型拟合比较、外部权重与VIF、效应分解、Bootstrap结果、MGA置换检验、调节效应检验等）
**附录F统计补充**：表F1-F7

详见 `Data/` 目录。

---

## PLS-SEM形成性测量模型

本研究采用**PLS-SEM形成性测量模型**验证四阶段认知编码机制（η₁域激活 → η₂参照点锚定 → η₃跨域映射 → Y语言编码）。

### 为何采用形成性测量

CFMC标注字段是标注者独立编码的多维度属性，各指标共同**构成**（constitute）认知阶段，而非认知阶段的可互换**反映**（reflection）。形成性测量的三项判据——因果方向由指标到潜变量、指标间独立性、指标不可删除——均满足。

### 三模型比较

| 模型 | 结构 | 用途 |
|:-----|:-----|:-----|
| 模型A | η₁→η₂→η₃→Y（完整四阶段） | 验证核心假设 |
| 模型B | η₂→η₃→Y（三阶段对照） | 检验η₁阶段是否必要 |
| 模型C | 四阶段+直接跳跃路径 | 检验中间阶段是否可绕过 |

### 多组分析（PLS-MGA）

按系词功能（attributive/equative/identificational）分3组，通过PLS-MGA置换检验验证四阶段路径结构的跨类型共享性。

详见 [`PLS-SEM形成性测量模型设计.md`](PLS-SEM形成性测量模型设计.md)。

---

## 使用方法

### 环境要求

- Python 3.8+
- 依赖包：

```bash
pip install -r requirements.txt
```

### 运行脚本

**一键运行全部分析**：

```bash
cd scripts/
python 一键运行全部脚本.py
```

**单独运行模块**：

```bash
# Q1: 类型特征分析
python Q1_01_描述统计.py
python Q1_02_H1_1相关分析.py
python Q1_03_GMM聚类.py

# Q2: 网络组织分析
python Q2_01_网络构建.py
python Q2_02_小世界检验.py

# Q3: 认知机制分析（PLS-SEM）
python Q3_01_描述统计.py
python Q3_02_PLS_SEM基础模型.py
python Q3_04_PLS_多组比较.py
python Q3_06_PLS_调节效应.py
```

**脚本执行顺序**：
1. Q1模块必须首先运行（Q1_03生成聚类标签供后续使用）
2. Q2和Q3模块依赖Q1_03的输出

---

## 信度效度

| 指标 | 标准 | 实际值 |
|:-----|:-----|:-------|
| 初始一致性 *κ* | ≥0.70 | 0.757 |
| 标注者间 *κ* | ≥0.75 | 0.810 |
| 标注者间 *ICC* | ≥0.78 | 0.981 |
| 整体信度 *α* | ≥0.80 | 0.86 |
| 一致率 | ≥85% | 90.5% |
| 重测 *r* | ≥0.85 | 0.974 |

详见 `appendix/信度效度验证_附录E/`

---

## 引用方式

如果您使用了本研究的语料库或代码，请引用：

```bibtex
@phdthesis{chen2026cfmc,
  title     = {基于语料库的汉语系表隐喻构式网络认知机制研究},
  author    = {陈放},
  school    = {北京师范大学},
  year      = {2026},
  type      = {博士学位论文}
}
```

---

## 许可证

本项目采用 [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/deed.zh-hans) 许可证。

- 允许分享、改编
- 需署名原作者
- 禁止商业用途

---

## 联系方式

**第一作者**：陈放 (Fang Chen)
- 单位：北京师范大学外国语言文学学院
- 邮箱：15397647129@163.com
- ORCID：[0009-0001-9317-7694](https://orcid.org/0009-0001-9317-7694)

**指导老师**：王德亮 (Deliang Wang)
- 单位：北京师范大学外国语言文学学院
- 邮箱：wangdeliang@bnu.edu.cn
- ORCID：[0000-0001-6142-1624](https://orcid.org/0000-0001-6142-1624)

---

## 致谢

感谢北京师范大学外国语言文学学院对本研究的支持。

---

*最后更新：2026年3月*
