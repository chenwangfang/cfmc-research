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

> **快速链接**：[语料库](CFMC_5989.json) | [理论框架](CFMC.md) | [在线演示](https://chenwangfang.github.io/cfmc-research/visualization/) | [English](README_EN.md)

## 项目简介

本研究基于Sullivan (2013) 的隐喻构式理论，构建**汉语系表隐喻构式认知框架（CFMC: Cognitive Framework for Metaphorical Constructions）**，通过5989条标注语料验证四阶段认知编码机制。

### 研究目标

1. **类型体系**：建立基于认知通达度-概念复杂度双维度的12类构式分类体系
2. **网络组织**：揭示构式网络的小世界结构特征与社区组织规律
3. **认知机制**：通过结构方程建模（SEM）验证四阶段认知编码机制

### 核心贡献

- **语料库**：5989条双盲标注的汉语系表隐喻构式
- **字段体系**：CFMC-33字段体系（33项必填+8项选填）
- **分类体系**：12类构式类型的GMM聚类验证
- **网络模型**：两层构式网络（构式层+类型层）
- **认知模型**：四阶段认知编码机制的SEM验证

---

## 研究问题与假设

| 问题 | 内容 | 假设 | 章节 |
|:-----|:-----|:-----|:-----|
| **Q1** | 类型体系 | H1-1: 认知通达度与概念复杂度负相关 (*r* = -0.40至-0.60)<br>H1-2: GMM聚类验证12类构式分类 (*k*=12, 轮廓系数≥0.30) | 第5章 |
| **Q2** | 网络组织 | H2: 构式网络呈现小世界特征 (*C*≥0.60, *L*≤3.0, σ>1) | 第6章 |
| **Q3** | 认知机制 | H3-1: SEM验证四阶段路径 (CFI>0.90, RMSEA<0.08, *β*≥0.40)<br>H3-2: 类型差异调节效应 (*r*≥0.30, *p*<0.05) | 第7章 |

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
├── CFMC.md                      # 理论框架文档
├── SEM_modeling_design.md       # SEM建模方案
│
├── data/                        # 统计分析结果（59个CSV + 59个JSON）
│   ├── 表58_认知通达度分布.*
│   ├── 表59_映射类型分布.*
│   └── ...
│
├── figures/                     # 可视化图表（41个PNG）
│   ├── 图1_研究路径图.png
│   ├── 图5_CFMC三层框架结构图.png
│   └── ...
│
├── scripts/                     # Python分析脚本（29个）
│   ├── Q1_01_描述统计.py
│   ├── Q2_01_网络构建.py
│   ├── Q3_01_描述统计.py
│   └── 一键运行全部脚本.py
│
├── appendix/                    # 附录文档
│   ├── 语料标注方案_附录A.md
│   ├── CFMC-33字段体系_附录B.md
│   ├── 认知通达度的构念界定与测量方案_附录C.md
│   ├── 概念复杂度的构念界定与测量方案_附录D.md
│   └── 信度效度验证_附录E/
│
└── visualization/               # 交互式可视化
    ├── index.html
    ├── research_flowchart.html
    └── literature_review.html
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
| `cognitive_accessibility` | 4.0 | 公式：0.55×D_reg + 0.45×D_trans；"武器"为高频常规隐喻，D_reg≈0.8，D_trans≈0.7，计算值≈0.76，对应4级（0.60-0.79） |
| `conceptual_complexity` | 2.0 | 公式：0.55×D_abstract + 0.45×D_processing；政治→军事为近域转换，基本层级，单一维度，计算值≈2.0，与MD=2类型均值（2.002±0.853）一致 |

> 详细测量方案见附录C（认知通达度）和附录D（概念复杂度）。


### 数据表索引

**Q1类型体系分析（第5章）**：表58-72
**Q2网络组织分析（第6章）**：表73-88
**Q3认知机制分析（第7章）**：表92-110

详见 `data/` 目录。

---

## 使用方法

### 环境要求

- Python 3.8+
- 依赖包：

```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn networkx semopy statsmodels
```

### 运行脚本

**一键运行全部分析**：

```bash
cd scripts/
python 一键运行全部脚本.py
```

**单独运行模块**：

```bash
# Q1: 类型体系分析
python Q1_01_描述统计.py
python Q1_02_H1_1相关分析.py
python Q1_03_GMM聚类.py

# Q2: 网络组织分析
python Q2_01_网络构建.py
python Q2_02_小世界检验.py

# Q3: 认知机制分析
python Q3_01_描述统计.py
python Q3_02_SEM基础模型.py
python Q3_03_SEM完整模型.py
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

*最后更新：2026年1月*
