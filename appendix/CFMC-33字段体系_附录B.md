## 附录B CFMC-33标注字段体系

### B.1 体系说明

CFMC-33是本研究设计的汉语系表隐喻构式标注字段体系（Cognitive Framework for Metaphorical Constructions-33），用于系统标注语料的认知语言学属性。CFMC-33与CFMC理论框架需明确区分：CFMC是理论框架，提供概念工具和分析逻辑；CFMC-33是操作化工具，将理论框架转化为可标注、可编码的字段规范。

本附录所称CFMC-33，指以33项必填字段为核心的汉语系表隐喻构式标注规范；完整标注方案另含8项选填字段，共41项。当前发布标注语料文件在此基础上保留派生字段和管理字段，实际数据字段为45项。因此，CFMC-33强调核心规范，41项强调完整标注方案，45项强调当前发布数据文件，三者属于不同层级，不应混用。其设计追溯至三大理论来源：

- Sullivan (2013) 隐喻构式理论为映射分析提供核心框架，相关字段包括mapping_direction（映射方向）、mapping_basis（映射基础）、copula_function（系词功能）等。其中，mapping_direction进入当前PLS-SEM模型，mapping_basis保留为映射方式的辅助描述字段，copula_function用于语言编码端点和多组分析分组。
- Langacker (1987, 2008) 认知语法为微观认知机制提供分析工具，相关字段包括embodied_experience（具身体验强度）、cognitive_reference_point（认知参照点）、entailment_richness（蕴涵丰富性）等，这些字段支撑四阶段认知编码机制的实证检验。
- Goldberg (1995, 2006) 构式网络理论为网络关系分析提供维度框架，相关字段包括link_type（链接类型）、inter_construction_links（构式间链接）、function_in_network（网络功能）等，这些字段服务于构式网络拓扑结构的建模分析。

CFMC-33的字段设计遵循“理论驱动+研究问题导向”原则。Level 1核心字段（23项）是字段体系层面的核心必填项，覆盖构式识别、隐喻成分、认知机制、认知生成路径和网络关系五类信息；主稿所称“五个核心分析字段”则专指第4章围绕变量操作化、信效度论证和Q1-Q3分层分析确定的认知通达度、映射方向、概念复杂度、源域和目标域五项。Level 2补充字段（4项）测量汉语语法特点及认知细化维度；Level 3-4选填字段（8项）用于典型案例的深度分析。

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

**说明**：Level 1核心字段（23项）是字段体系层面的核心必填项。主稿中的五个核心分析字段，是第4章围绕变量操作化、信效度论证和Q1-Q3分层分析确定的五项重点字段，不能与23项Level 1字段混用。具体而言，认知通达度、映射方向、概念复杂度、源域和目标域构成主稿第4章重点论证的五个核心分析字段；其余Level 1字段分别服务于构式边界、Q2实例层网络解释、Q3形成性模型指标或辅助描述。Level 2补充字段（4项）测量汉语语法特点及认知细化维度，其中holistic_imagery（整体性意象）和relational_thinking（关系性思维）用于探索整体性/关系性文本指标与四阶段近似路径关联强度之间的调节关系（EA-2探索性分析）。Level 3-4选填字段（8项）用于典型案例的深度分析，约60至100条语料需完成这些字段的质性标注。

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

#### B.3.2 Level 1 核心字段（23项）

##### A_基础识别（4项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| construction_type | 构式边界类型 | String | 当前发布数据中的原始边界标签，如核心隐喻构式、边界/对照记录等；Q1的T1-T12操作类型由认知通达度等级与映射方向派生为`construction_type_12` |
| subject | 主语 | String | NP₁成分（目标域载体） |
| copula | 系词 | String | 系词表面形式（如“是”/“即”/“就是”/“为”/“成为”/“成了”/∅） |
| predicate | 谓语 | String | NP₂成分（源域载体） |

##### B_隐喻成分（7项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| source_domain | 源域 | String | 隐喻源域类别（四阶段机制阶段1指标） |
| target_domain | 目标域 | String | 隐喻目标域类别（四阶段机制阶段1指标） |
| mapping_direction | 映射方向 | 1-4定类 | MD值：1=具→具，2=具→抽，3=抽→抽，4=抽→具（阶段3指标） |
| metaphor_type | 隐喻类型 | String | 概念隐喻分类 |
| thematic_role | 题元角色 | String | 主语的语义角色 |
| copula_function | 系词功能 | String-Coded；Q3中转为1-3定类 | 系词功能类型：equative等同、attributive属性、identificational识别；Q3中重编码为阶段4结果变量Y |
| constructional_meaning | 构式义 | String | 构式整体意义 |

##### C_认知机制（3项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| cognitive_accessibility | 认知通达度 | 1-5定距 | CA值：源域固化程度及映射可达性的复合指标（阶段2核心指标） |
| mapping_basis | 映射基础 | String | 隐喻映射方式的辅助描述字段，不进入当前PLS-SEM的*η*₃测量模型 |
| conceptual_complexity | 概念复杂度 | 1-4定距 | CC值：目标域概念化负荷及映射整合成本；用于Q1理论轴、H1-1检验和H1-2相关效度检验，不直接进入PLS-SEM的*η*₃测量模型 |

##### D_认知生成路径（3项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| embodied_experience | 具身经验 | 0.0-1.0连续评分 | 身体经验基础强度（阶段1核心指标） |
| cognitive_reference_point | 认知参照点 | String | 参照点类型描述（阶段2相关） |
| entailment_richness | 蕴涵丰富性 | 0.0-1.0连续评分 | 隐喻蕴涵程度（阶段3指标） |

##### E_网络关系（6项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| prototype_distance | 原型距离 | 原始1-3定序；Q3分析中替换为连续值 | 原始字段表示中心、次中心、边缘三层梯度；Q3分析使用Q1_05按CA—MD空间重算的连续标准化欧氏距离，作为阶段2相关代理指标 |
| link_type | 链接类型 | 1-4编码 | 构式间关系类型：1=隐喻扩展，2=多义，3=子部分，4=实例 |
| inter_construction_links | 构式间链接 | String | 与其他构式的关联描述 |
| systematicity | 系统性 | 0.0-1.0连续评分 | 隐喻系统性程度（阶段3指标） |
| conventionality | 常规度 | 0.0-1.0连续评分 | 隐喻规约化程度（阶段2指标） |
| function_in_network | 网络功能 | 1-5编码 | 在构式网络中的角色：1=中心，2=边缘，3=桥接，4=创新，5=模块核心 |

#### B.3.3 Level 2 补充字段（4项）

##### F_句法特征（1项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| copula_type | 系词类型 | String-Coded | 历史细分标签；数据中的zero不等于严格零系词样本，严格零系词按正文4.3.1标准另行判定 |

##### G_汉语特色（2项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| holistic_imagery | 整体性意象 | 0.0-2.0连续评分 | 语料文本中的整体场景化线索（EA-2探索性调节变量） |
| relational_thinking | 关系性思维 | 0.0-2.0连续评分 | 源域与目标域之间关系对应的显化程度（EA-2探索性调节变量） |

##### H_认知细化（1项）

| 字段名 | 中文名 | 取值类型 | 说明 |
|:-------|:-------|:---------|:-----|
| metaphor_novelty | 隐喻新颖度 | 0.0-1.0连续评分 | 新颖/规约隐喻区分 |

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

*说明：完整的字段编码规范详见附录A语料标注方案。*
