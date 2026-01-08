## 附录B CFMC-33标注字段体系

### B.1 体系说明

CFMC-33是本研究设计的汉语系表隐喻构式标注字段体系（Cognitive Framework for Metaphorical Constructions-33），用于系统标注语料的认知语言学属性。CFMC-33与CFMC理论框架需明确区分：CFMC是理论框架，提供概念工具和分析逻辑；CFMC-33是操作化工具，将理论框架转化为可标注、可编码的字段规范。

CFMC-33共包含41项字段（33项必填+8项选填），其设计追溯至三大理论来源：

- Sullivan (2013) 隐喻构式理论为映射分析提供核心框架，相关字段包括mapping_direction（映射方向）、mapping_basis（映射基础）、copula_function（系词功能）等，这些字段直接服务于自主—依存原则的操作化验证。
- Langacker (1987, 2008) 认知语法为微观认知机制提供分析工具，相关字段包括embodied_experience（具身体验强度）、cognitive_reference_point（认知参照点）、entailment_richness（蕴涵丰富性）等，这些字段支撑四阶段认知编码机制的实证检验。
- Goldberg (1995, 2006) 构式网络理论为网络关系分析提供维度框架，相关字段包括link_type（链接类型）、inter_construction_links（构式间链接）、function_in_network（网络功能）等，这些字段服务于构式网络拓扑结构的建模分析。

CFMC-33的字段设计遵循"理论驱动+研究问题导向"原则。Level 1核心字段（23项）直接服务于Q1-Q3三个研究问题的假设检验，是统计分析的主要数据来源；Level 2补充字段（4项）测量汉语语法特点及认知细化维度；Level 3-4选填字段（8项）用于典型案例的深度分析。

---

### B.2 字段体系概览

| 层级 | 字段类别 | 字段数 | 性质 | 主要字段示例 |
|:-----|:---------|:------:|:----:|:-------------|
| 基础字段 | 语料管理 | 6项 | 必填 | original_id, full_sentence, genre |
| Level 1 | A_基础识别 | 4项 | 必填 | construction_type, subject, copula, predicate |
|  | B_隐喻成分 | 7项 | 必填 | source_domain, target_domain, mapping_direction |
|  | C_认知机制 | 3项 | 必填 | cognitive_accessibility, conceptual_complexity |
|  | D_认知生成路径 | 3项 | 必填 | embodied_experience, entailment_richness |
|  | E_网络关系 | 6项 | 必填 | link_type, prototype_distance, systematicity |
| Level 2 | F_句法特征 | 1项 | 必填 | copula_type |
|  | G_汉语特色 | 2项 | 必填 | holistic_imagery, relational_thinking |
|  | H_认知细化 | 1项 | 必填 | metaphor_novelty |
| Level 3 | 深化字段 | 2项 | 选填 | family_marker, inheritance_relation |
| Level 4 | 质性字段 | 6项 | 选填 | mapping_content, entailment |

**说明**：Level 1核心字段（23项）直接服务于Q1-Q3三个研究问题的假设检验，是统计分析的主要数据来源。Level 2补充字段（4项）测量汉语语法特点及认知细化维度，其中holistic_imagery（整体性意象）和relational_thinking（关系性思维）两个字段用于检验汉语认知特色的调节效应（EA-2探索性分析）。Level 3-4选填字段（8项）用于典型案例的深度分析，约60至100条语料需完成这些字段的质性标注。

---

### B.3 必填字段详解（33项）

#### B.3.1 基础字段（6项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| original_id | 原始编号 | String | 语料唯一标识符 |
| full_sentence | 完整句子 | String | 含构式的原始语句 |
| construction | 构式形式 | String | 提取的系表隐喻构式 |
| time | 时间 | String | 语料来源时间 |
| source | 来源 | String | 语料出处（书籍、期刊等） |
| genre | 体裁 | String | 语料文体类型（文学、新闻、学术、网络、对话） |

---

#### B.3.2 Level 1 核心字段（23项）

##### A_基础识别（4项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| construction_type | 构式类型 | String | T1-T12分类标签（基于3级认知通达度×4类映射方向） |
| subject | 主语 | String | NP₁成分（目标域载体） |
| copula | 系词 | String | 系词形式（"是"/"为"/"乃"/∅） |
| predicate | 谓语 | String | NP₂成分（源域载体） |

##### B_隐喻成分（7项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| source_domain | 源域 | String | 隐喻源域类别（四阶段机制阶段1指标） |
| target_domain | 目标域 | String | 隐喻目标域类别（四阶段机制阶段1指标） |
| mapping_direction | 映射方向 | 1-4定类 | MD值：1=具→具，2=具→抽，3=抽→抽，4=抽→具（阶段3指标） |
| metaphor_type | 隐喻类型 | String | 概念隐喻分类 |
| thematic_role | 题元角色 | String | 主语的语义角色 |
| copula_function | 系词功能 | 1-3定序 | 系词功能类型：1=equative等同，2=predicational述谓，3=specificational指称（阶段4结果变量X₁₁） |
| constructional_meaning | 构式义 | String | 构式整体意义 |

##### C_认知机制（3项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| cognitive_accessibility | 认知通达度 | 1-5定距 | CA值：源域激活难易程度（阶段2核心指标） |
| mapping_basis | 映射基础 | String | 隐喻映射的认知基础（阶段3指标） |
| conceptual_complexity | 概念复杂度 | 1-5定距 | CC值：目标域概念加工复杂度（阶段3指标） |

##### D_认知生成路径（3项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| embodied_experience | 具身经验 | 1-5定距 | 身体经验基础强度（阶段1核心指标） |
| cognitive_reference_point | 认知参照点 | String | 参照点类型描述（阶段2相关） |
| entailment_richness | 蕴涵丰富性 | 1-5定距 | 隐喻蕴涵程度（阶段3指标） |

##### E_网络关系（6项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| prototype_distance | 原型距离 | 1-3定序 | 与原型构式的距离：1=中心，2=次中心，3=边缘（阶段2指标） |
| link_type | 链接类型 | String | 构式间关系类型（隐喻扩展/多义/实例/子部分） |
| inter_construction_links | 构式间链接 | String | 与其他构式的关联描述 |
| systematicity | 系统性 | 1-5定距 | 隐喻系统性程度（阶段3指标） |
| conventionality | 常规度 | 1-5定距 | 隐喻规约化程度（阶段2指标） |
| function_in_network | 网络功能 | String | 在构式网络中的角色 |

---

#### B.3.3 Level 2 补充字段（4项）

##### F_句法特征（1项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| copula_type | 系词类型 | String | 形态分类：基本/扩展/否定/零 |

##### G_汉语特色（2项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| holistic_imagery | 整体性意象 | 1-5定距 | 汉语整体性思维特征（调节变量） |
| relational_thinking | 关系性思维 | 1-5定距 | 汉语关系性认知特征（调节变量） |

##### H_认知细化（1项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| metaphor_novelty | 隐喻新颖度 | 1-5定距 | 新颖/规约隐喻区分 |

---

### B.4 选填字段详解（8项）

选填字段用于典型案例的深度分析，约60至100条语料需完成这些字段的质性标注。

#### B.4.1 Level 3 深化字段（2项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| family_marker | 家族标记 | String | 构式家族归属标识 |
| inheritance_relation | 继承关系 | String | 构式继承类型 |

#### B.4.2 Level 4 质性字段（6项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| mapping_content | 映射内容 | String | 具体映射关系描述 |
| entailment | 蕴涵 | String | 隐喻蕴涵详细说明 |
| inheritance_links_detail | 继承链接详情 | String | 继承关系的详细描述 |
| polysemy_links_detail | 多义链接详情 | String | 多义关系的详细描述 |
| subpart_links_detail | 子部分链接详情 | String | 子部分关系的详细描述 |
| cognitive_reference_point_description | 认知参照点描述 | String | 参照点的详细说明 |

---

### B.5 字段体系结构图

```
CFMC-33字段体系（41项）
│
├── 必填字段（33项）
│   │
│   ├── 基础字段（6项）
│   │   original_id, full_sentence, construction, time, source, genre
│   │
│   ├── Level 1 核心字段（23项）
│   │   ├── A_基础识别（4项）
│   │   │   construction_type, subject, copula, predicate
│   │   ├── B_隐喻成分（7项）
│   │   │   source_domain, target_domain, mapping_direction,
│   │   │   metaphor_type, thematic_role, copula_function, constructional_meaning
│   │   ├── C_认知机制（3项）
│   │   │   cognitive_accessibility, mapping_basis, conceptual_complexity
│   │   ├── D_认知生成路径（3项）
│   │   │   embodied_experience, cognitive_reference_point, entailment_richness
│   │   └── E_网络关系（6项）
│   │       prototype_distance, link_type, inter_construction_links,
│   │       systematicity, conventionality, function_in_network
│   │
│   └── Level 2 补充字段（4项）
│       ├── F_句法特征（1项）：copula_type
│       ├── G_汉语特色（2项）：holistic_imagery, relational_thinking
│       └── H_认知细化（1项）：metaphor_novelty
│
└── 选填字段（8项）
    │
    ├── Level 3 深化字段（2项）
    │   family_marker, inheritance_relation
    │
    └── Level 4 质性字段（6项）
        mapping_content, entailment, inheritance_links_detail,
        polysemy_links_detail, subpart_links_detail,
        cognitive_reference_point_description
```

---

*说明：完整的字段编码规范详见附录A语料标注方案。*
