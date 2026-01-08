# CFMC-Research

**A Corpus-Based Study on the Cognitive Mechanisms of Chinese Copular Metaphorical Constructions**

*汉语系表隐喻构式认知框架研究*

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.XXXXXXX-blue)](https://doi.org/10.5281/zenodo.XXXXXXX)
[![Corpus](https://img.shields.io/badge/Corpus-5989%20constructions-blue)](CFMC_5989.json)
[![Scripts](https://img.shields.io/badge/Scripts-29%20Python-green)](scripts/)
[![License](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey)](LICENSE)
[![GitHub Pages](https://img.shields.io/badge/Demo-GitHub%20Pages-brightgreen)](https://chenwangfang.github.io/cfmc-research/visualization/)
[![中文](https://img.shields.io/badge/中文-README-red)](README.md)

---

> **Quick Links**: [Corpus](CFMC_5989.json) | [Framework](CFMC.md) | [Live Demo](https://chenwangfang.github.io/cfmc-research/visualization/) | [中文](README.md)

## Overview

This research builds upon Sullivan's (2013) theory of metaphorical constructions to develop the **Cognitive Framework for Metaphorical Constructions (CFMC)** for Chinese copular metaphors. The framework is validated through a corpus of 5,989 annotated constructions, testing a four-stage cognitive encoding mechanism.

### Research Objectives

1. **Typological System**: Establish a 12-type classification based on cognitive accessibility and conceptual complexity
2. **Network Organization**: Reveal small-world structure characteristics and community organization patterns
3. **Cognitive Mechanism**: Validate the four-stage cognitive encoding mechanism through Structural Equation Modeling (SEM)

### Key Contributions

- **Corpus**: 5,989 double-blind annotated Chinese copular metaphorical constructions
- **Field System**: CFMC-33 field system (33 required + 8 optional fields)
- **Classification**: GMM clustering validation of 12 construction types
- **Network Model**: Two-layer construction network (construction layer + type layer)
- **Cognitive Model**: SEM validation of four-stage cognitive encoding mechanism

---

## Research Questions and Hypotheses

| Question | Content | Hypotheses | Chapter |
|:---------|:--------|:-----------|:--------|
| **Q1** | Typological System | H1-1: Negative correlation between cognitive accessibility and conceptual complexity (*r* = -0.40 to -0.60)<br>H1-2: GMM clustering validates 12 types (*k*=12, silhouette coefficient ≥0.30) | Ch.5 |
| **Q2** | Network Organization | H2: Construction network exhibits small-world properties (*C*≥0.60, *L*≤3.0, σ>1) | Ch.6 |
| **Q3** | Cognitive Mechanism | H3-1: SEM validates four-stage pathways (CFI>0.90, RMSEA<0.08, *β*≥0.40)<br>H3-2: Type differences show moderation effects (*r*≥0.30, *p*<0.05) | Ch.7 |

---

## Repository Structure

```
cfmc-research/
├── README.md                    # Chinese documentation
├── README_EN.md                 # English documentation
├── LICENSE                      # CC BY-NC 4.0 License
├── CITATION.cff                 # Citation info (GitHub auto-detected)
├── .gitignore                   # Git ignore configuration
│
├── CFMC_5989.json               # Core corpus (5,989 entries, 13MB)
├── CFMC.md                      # Theoretical framework
├── SEM_modeling_design.md       # SEM modeling design
│
├── data/                        # Statistical results (59 CSV + 59 JSON)
│   ├── 表58_认知通达度分布.*    # Table 58: Cognitive accessibility distribution
│   ├── 表59_映射类型分布.*      # Table 59: Mapping type distribution
│   └── ...
│
├── figures/                     # Visualizations (41 PNG files)
│   ├── 图1_研究路径图.png       # Figure 1: Research pathway
│   ├── 图5_CFMC三层框架结构图.png  # Figure 5: CFMC three-layer framework
│   └── ...
│
├── scripts/                     # Python analysis scripts (29 files)
│   ├── Q1_01_描述统计.py        # Q1_01: Descriptive statistics
│   ├── Q2_01_网络构建.py        # Q2_01: Network construction
│   ├── Q3_01_描述统计.py        # Q3_01: Descriptive statistics
│   └── 一键运行全部脚本.py      # Run all scripts
│
├── appendix/                    # Appendix documents
│   ├── 语料标注方案_附录A.md    # Appendix A: Annotation scheme
│   ├── CFMC-33字段体系_附录B.md # Appendix B: CFMC-33 field system
│   ├── 认知通达度的构念界定与测量方案_附录C.md  # Appendix C: Cognitive accessibility
│   ├── 概念复杂度的构念界定与测量方案_附录D.md  # Appendix D: Conceptual complexity
│   └── 信度效度验证_附录E/      # Appendix E: Reliability and validity
│
└── visualization/               # Interactive visualizations
    ├── index.html
    ├── research_flowchart.html
    └── literature_review.html
```

---

## Data Description

### CFMC_5989.json

The core corpus containing 5,989 fully annotated Chinese copular metaphorical constructions.

**Field System (CFMC-33)**:

| Level | Fields | Content |
|:------|:------:|:--------|
| Basic Identification | 6 | ID, sentence, construction form, source, etc. |
| Level 1 Core Fields | 23 | Cognitive accessibility, conceptual complexity, mapping direction, copula function, etc. |
| Level 2 Supplementary | 4 | Chinese-specific features |
| Level 3-4 Optional | 8 | Qualitative annotation content |

**Sample Structure**:
```json
{
  "metadata": {
    "description": "CFMC-33 Chinese Copular Metaphorical Construction Corpus",
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

**Field Calculation Process** (Example: zh55588):

| Field | Value | Calculation/Determination |
|:------|:-----:|:--------------------------|
| `mapping_direction` | 2.0 | Source "sharp weapon" (concrete) → Target "general line" (abstract), classified as "concrete→abstract", coded as 2 |
| `cognitive_accessibility` | 4.0 | Formula: 0.55×*D*reg + 0.45×*D*trans; "weapon" is high-frequency conventional metaphor, *D*reg≈0.8, *D*trans≈0.7, raw score≈0.76 (relatively high), converted to Level 4 via quintile method |
| `conceptual_complexity` | 2.0 | Raw score converted via quintile method; this construction falls in the 20-40% percentile (relatively simple), consistent with MD=2 type mean (2.002±0.853) |

> See Appendix C (Cognitive Accessibility) and Appendix D (Conceptual Complexity) for detailed measurement schemes.

<details>
<summary><strong>Conceptual Complexity Formula System</strong> (click to expand)</summary>

**Formula D-3 (Final Formula)**:
```
Conceptual_Complexity_Raw = 0.55 × D_abstract + 0.45 × D_processing
```
Raw score range [0, 1], converted to 1-5 scale via quintile method.

**Formula D-1: Cognitive Domain Abstraction**
```
D_abstract = 0.25×F_field + 0.50×A_level + 0.25×D_number
```

| Parameter | Meaning | Values |
|:----------|:--------|:-------|
| *F*field | Domain type | Everyday concrete=0.20, Everyday abstract=0.40, Professional concrete=0.60, Professional abstract=0.80, Philosophical abstract=1.00 |
| *A*level | Abstraction level | Basic concrete=0, First-order abstract=0.33, Second-order abstract=0.67, Higher-order abstract=1.00 |
| *D*number | Cognitive domain count | Single=0.20, 2-3 domains=0.40, 4-5 domains=0.60, 6+ domains=0.80, Highly complex=1.00 |

**Formula D-2: Mapping Processing Depth**
```
D_processing = 0.6×I_depth + 0.4×S_schema
```

| Parameter | Meaning | Values |
|:----------|:--------|:-------|
| *I*depth | Inference depth | Direct mapping=0, Single-step=0.33, Multi-step=0.67, Deep inference=1.00 |
| *S*schema | Image schema complexity | Single simple=0, Single complex=0.33, Multi-schema=0.67, Complex network=1.00 |

**Quintile Conversion**:
- [0%, 20%) → Level 1 (Very simple)
- [20%, 40%) → Level 2 (Relatively simple)
- [40%, 60%) → Level 3 (Moderate)
- [60%, 80%) → Level 4 (Relatively complex)
- [80%, 100%] → Level 5 (Very complex)

**Example zh55588 Verification** ("General line is a sharp weapon for building socialism", MD=2):

| Parameter | Value | Description |
|:----------|:-----:|:------------|
| *F*field | 0.80 | Target "general line" is professional abstract domain (political concept) |
| *A*level | 0.33 | First-order abstract (abstracted from concrete policies) |
| *D*number | 0.40 | Activates 2-3 cognitive domains (political, action, goal) |
| *I*depth | 0.33 | Single-step inference (weapon functionality → general line's role) |
| *S*schema | 0 | Single simple schema (force schema) |

Calculation: *D*abstract = 0.25×0.80 + 0.50×0.33 + 0.25×0.40 = 0.465, *D*processing = 0.6×0.33 + 0.4×0 = 0.198, Raw score = 0.55×0.465 + 0.45×0.198 ≈ 0.345 (relatively low). Annotated value 2.0 is consistent with MD=2 type mean.

</details>


### Data Tables Index

- **Q1 Typological Analysis (Chapter 5)**: Tables 58-72
- **Q2 Network Analysis (Chapter 6)**: Tables 73-88
- **Q3 Cognitive Mechanism Analysis (Chapter 7)**: Tables 92-110

See `data/` directory for details.

---

## Usage

### Requirements

- Python 3.8+
- Dependencies:

```bash
pip install pandas numpy scipy scikit-learn matplotlib seaborn networkx semopy statsmodels
```

### Running Scripts

**Run all analyses**:

```bash
cd scripts/
python 一键运行全部脚本.py
```

**Run individual modules**:

```bash
# Q1: Typological analysis
python Q1_01_描述统计.py
python Q1_02_H1_1相关分析.py
python Q1_03_GMM聚类.py

# Q2: Network analysis
python Q2_01_网络构建.py
python Q2_02_小世界检验.py

# Q3: Cognitive mechanism analysis
python Q3_01_描述统计.py
python Q3_02_SEM基础模型.py
python Q3_03_SEM完整模型.py
```

**Execution Order**:
1. Q1 module must run first (Q1_03 generates cluster labels for subsequent use)
2. Q2 and Q3 modules depend on Q1_03 output

---

## Reliability and Validity

| Metric | Standard | Actual Value |
|:-------|:---------|:-------------|
| Initial Agreement *κ* | ≥0.70 | 0.757 |
| Inter-rater *κ* | ≥0.75 | 0.810 |
| Inter-rater *ICC* | ≥0.78 | 0.981 |
| Overall Reliability *α* | ≥0.80 | 0.86 |
| Agreement Rate | ≥85% | 90.5% |
| Test-retest *r* | ≥0.85 | 0.974 |

See `appendix/信度效度验证_附录E/` for details.

---

## Citation

If you use this corpus or code in your research, please cite:

```bibtex
@phdthesis{chen2026cfmc,
  title     = {A Corpus-Based Study on the Cognitive Mechanisms of Chinese Copular Metaphorical Construction Networks},
  author    = {Chen, Fang},
  school    = {Beijing Normal University},
  year      = {2026},
  type      = {PhD Dissertation}
}
```

---

## License

This project is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

- Sharing and adaptation permitted
- Attribution required
- Non-commercial use only

---

## Contact

**First Author**: Fang Chen
- Affiliation: School of Foreign Languages and Literature, Beijing Normal University
- Email: 15397647129@163.com
- ORCID: [0009-0001-9317-7694](https://orcid.org/0009-0001-9317-7694)

**Supervisor**: Deliang Wang
- Affiliation: School of Foreign Languages and Literature, Beijing Normal University
- Email: wangdeliang@bnu.edu.cn
- ORCID: [0000-0001-6142-1624](https://orcid.org/0000-0001-6142-1624)

---

## Acknowledgments

We thank the School of Foreign Languages and Literature at Beijing Normal University for supporting this research.

---

*Last updated: January 2026*
