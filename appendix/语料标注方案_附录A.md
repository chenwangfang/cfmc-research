## 附录A 语料标注方案

### 第一部分：总体设计

#### 1.1 研究目标

本标注方案旨在支撑以下三个核心研究问题的实证分析：

- **Q1 (类型特征)**：汉语系表隐喻构式呈现哪些类型及其特征？该问题采用双维度分类体系 (认知通达度×映射方向)，识别12类构式并验证其原型梯度结构。

- **Q2 (网络组织)**：汉语系表隐喻构式如何组织为构式网络？该问题基于Goldberg四类链接关系，检验构式网络的小世界性质。

- **Q3 (认知机制)**：汉语系表隐喻构式的认知编码机制是什么？该问题验证四阶段认知编码机制 (认知域激活→认知参照点锚定→跨域映射→语言编码)，阐明12类构式共享的认知加工过程。

#### 1.2 语料来源与规模

- **原始标注语料**：6,022条；去除33条已确认重复记录，并进一步裁定18组历史遗留重复记录后，形成5,971条当前发布标注语料，其中核心隐喻构式为5,908条，另有63条边界/对照记录
- **来源**：北京语言大学BCC语料库
- **时间跨度**：1836年至2018年
- **语体分布**：文学、新闻、学术、网络、对话五类语体

#### 1.3 CFMC-33标注体系概览

本研究采用CFMC-33标注体系，将隐喻构式认知框架(CFMC)转化为可操作的标注规范。本附录所称CFMC-33，指以33项必填字段为核心的标注规范；完整标注方案包含33项必填字段和8项选填字段，共41项。当前发布标注语料文件在此基础上另保留派生字段和管理字段，实际数据字段为45项。完整的字段定义、取值范围和编码规范详见附录B。

**表A-1 CFMC-33字段体系概览**

| 层级 | 字段类别 | 字段数 | 性质 | 主要字段示例 |
|:-----|:---------|:------:|:-----|:-------------|
| 基础字段 | 语料管理 | 6项 | 必填 | original_id, full_sentence, genre |
| Level 1 | 核心字段 | 23项 | 必填 | source_domain, cognitive_accessibility, link_type |
| Level 2 | 补充字段 | 4项 | 必填 | copula_type, holistic_imagery, relational_thinking |
| Level 3-4 | 选填字段 | 8项 | 选填 | family_marker, mapping_content |

**设计原则**：CFMC-33的字段设计遵循“理论驱动+研究问题导向”原则。这里的Level 1核心字段 (23项)指CFMC-33标注体系中的必填字段层级；主稿所称“五个核心分析字段”则专指在Q1类型划分、Q2网络解释和Q3部分间接指标设置中承担重点分析角色的认知通达度、映射方向、概念复杂度、源域和目标域五项。Level 2补充字段 (4项)测量汉语语法特点，其中holistic_imagery(整体性意象)和relational_thinking(关系性思维)用于检验汉语相关文本指标的探索性调节效应；Level 3-4选填字段 (8项)用于典型案例的深度分析。

#### 1.4 四阶段认知编码机制

CFMC-33的核心设计依据是四阶段认知编码机制，该机制将Sullivan (2013) 的两步描述发展为可检验的形式化模型。当前四阶段机制采用10个观测指标进入SEM；mapping_basis保留为映射方式的辅助描述字段，不纳入当前*η*₃测量模型。

**表A-2 四阶段认知编码机制与字段对应**

| 阶段 | 名称 | 理论来源 | CFMC-33字段 | SEM角色 |
|:-----|:-----|:---------|:------------|:--------|
| 阶段1 | 认知域激活 | Sullivan evocation + Langacker域理论 | embodied_experience, source_domain, target_domain | 潜变量*η*₁ (3指标) |
| 阶段2 | 认知参照点锚定 | Langacker认知参照点模型 | conventionality, cognitive_accessibility, prototype_distance | 潜变量*η*₂ (3指标) |
| 阶段3 | 跨域映射 | Sullivan自主—依存原则 | mapping_direction, systematicity, entailment_richness | 潜变量*η*₃ (3指标；mapping_basis为辅助描述字段) |
| 阶段4 | 语言编码 | Halliday/Higgins系词功能分类，结合Sullivan构式映射边界 | copula_function | 结果观测变量Y |

#### 1.5 双维度分类体系

标注方案支持双维度分类体系的操作化测量：

- **认知通达度**：5级量表 (1=最难通达，5=最易通达)，归并为3级 (高：4-5级；中：3级；低：1-2级)
- **概念复杂度**：目标域概念化难度的1-4级评分变量；操作分类中，映射方向按4类记录 (具体→具体、具体→抽象、抽象→抽象、抽象→具体)

双维度交叉形成3×4=12类构式，并在理论上预期其呈现全局原型梯度结构(中心—次中心—边缘)。

### 第二部分：字段体系说明

#### 2.1 CFMC-33字段体系概览

CFMC-33 (Cognitive Framework for Metaphorical Constructions-33) 是本研究构建的汉语系表隐喻构式标注字段体系。其核心规范为33项必填字段，完整标注方案另含8项选填字段，共41项；当前发布语料文件为便于清洗、追踪和统计分析，另保留派生字段和管理字段，共45项。该体系将本研究构建的CFMC理论框架转化为可操作的标注规范。

**表A-3 CFMC-33字段体系结构**

| 层级 | 字段类别 | 字段数 | 性质 | 主要字段示例 |
|:-----|:---------|:------:|:-----|:-------------|
| 基础字段 | 语料管理 | 6项 | 必填 | original_id, full_sentence, genre |
| Level 1 | A_基础识别 | 4项 | 必填 | construction_type, subject, copula, predicate |
| | B_隐喻成分 | 7项 | 必填 | source_domain, target_domain, mapping_direction |
| | C_认知机制 | 3项 | 必填 | cognitive_accessibility, conceptual_complexity |
| | D_认知生成路径 | 3项 | 必填 | embodied_experience, entailment_richness |
| | E_网络关系 | 6项 | 必填 | link_type, prototype_distance, systematicity |
| Level 2 | F_句法特征 | 1项 | 必填 | copula_type |
| | G_汉语特色 | 2项 | 必填 | holistic_imagery, relational_thinking |
| | H_认知细化 | 1项 | 必填 | metaphor_novelty |
| Level 3 | 深化字段 | 2项 | 选填 | family_marker, inheritance_relation |
| Level 4 | 质性字段 | 6项 | 选填 | mapping_content, entailment |

基础字段、Level 1字段和Level 2字段合计33项，均为必填字段，构成本研究的标注核心；Level 3-4的8项选填字段用于深度个案分析。其中，Level 1核心字段 (23项)是字段体系层面的核心必填项；主稿中的五个核心分析字段，是第4章围绕变量操作化、信效度论证和Q1-Q3分层分析确定的五项重点字段，不能与23项Level 1字段混用。

#### 2.2 理论基础：一主干、三向整合

CFMC-33的设计遵循"一主干、三向整合"原则。

**主干理论：Sullivan隐喻构式理论**

Sullivan (2013) 的自主—依存原则为CFMC-33提供核心分析框架。在系表隐喻构式"NP₁是NP₂"中，NP₁为自主元素 (唤起目标域)，NP₂为依存元素 (唤起源域)。这一原则直接对应A区字段 (subject, copula, predicate)和B区字段 (source_domain, target_domain)的设计。

**三向整合**

1. **Langacker认知语法**：深化微观认知机制，为认知参照点、侧显/基底、认知域等概念提供操作化依据，对应C区字段 (cognitive_accessibility)和D区字段 (embodied_experience)。

2. **Goldberg构式网络理论**：补充网络视角，四类链接关系 (隐喻扩展链接、多义链接、实例链接、子部分链接)直接对应E区字段 (link_type)。

3. **汉语类型学特征**：实现语言适应，零系词构式、话题突出结构、整体性思维等汉语特色对应G区字段 (holistic_imagery, relational_thinking)和F区字段（`copula_type`保留历史`zero`细分标签）。

**CFMC三层结构**

| 层次 | 名称 | 核心工具 | 对应字段类别 |
|:-----|:-----|:---------|:-------------|
| 层次1 | 映射机制层次 | Langacker认知语法 | C区、D区 |
| 层次2 | 语码实现层次 | Sullivan自主—依存原则 | A区、B区、F区、H区 |
| 层次3 | 网络关联层次 | Goldberg四类链接 | E区 |

#### 2.3 四阶段认知编码机制与字段对应

四阶段认知编码机制是本研究为回答Q3 (认知机制)而构建的核心理论工具，将Sullivan (2013) 的两步描述发展为可检验的形式化模型。

**表A-4 四阶段认知编码机制与CFMC-33字段对应**

| 阶段 | 名称 | 理论来源 | CFMC-33字段 | SEM角色 |
|:-----|:-----|:---------|:------------|:--------|
| 阶段1 | 认知域激活 | Sullivan evocation + Langacker域理论 | embodied_experience, source_domain, target_domain | 潜变量*η*₁ (3指标) |
| 阶段2 | 认知参照点锚定 | Langacker认知参照点模型 | conventionality, cognitive_accessibility, prototype_distance | 潜变量*η*₂ (3指标) |
| 阶段3 | 跨域映射 | Sullivan自主—依存原则 | mapping_direction, systematicity, entailment_richness | 潜变量*η*₃ (3指标；mapping_basis为辅助描述字段) |
| 阶段4 | 语言编码 | Halliday/Higgins系词功能分类，结合Sullivan构式映射边界 | copula_function | 结果观测变量Y |

**阶段功能说明**：

- **阶段1 (认知域激活)**：激活源域和目标域的认知基础，具身经验是域激活的认知前提。
- **阶段2 (认知参照点锚定)**：建立认知参照点R (NP₁)，确定从参照点到目标的认知路径。
- **阶段3 (跨域映射)**：执行源域→目标域的概念映射，涉及映射方向、基础、系统性、蕴涵丰富性。
- **阶段4 (语言编码)**：将映射关系实现为具体的系词功能选择。

四个阶段形成级联加工关系：阶段1→阶段2→阶段3→阶段4。当前PLS-SEM模型采用10个观测指标：前三个潜变量各含3个形成性指标，系词功能作为结果观测变量Y。`mapping_basis`保留为映射方式的辅助描述字段，不进入当前*η*₃测量模型。

#### 2.4 双维度分类体系与字段对应

双维度分类体系是本研究为回答Q1 (类型特征)而构建的核心分析工具，基于Sullivan自主—依存原则发展出两个对称维度。

**认知通达度维度**

认知通达度测量隐喻映射关系的规约化程度和理解难度：
- 原始量表：5级 (1=最难通达，5=最易通达)
- 归并分级：3级 (低：1-2级；中：3级；高：4-5级)
- 核心字段：cognitive_accessibility, conventionality, metaphor_novelty

**概念复杂度维度**

概念复杂度采用1-4级有序评分，主要衡量目标域概念化负荷及其映射整合成本。映射方向不是概念复杂度的替代变量，而是与概念复杂度相关的4类操作分类桥梁：
- 具体→抽象 (具抽)：最常见的隐喻方向
- 具体→具体 (具具)：同层级映射
- 抽象→抽象 (抽抽)：高阶抽象映射
- 抽象→具体 (抽具)：逆向映射
- 核心字段：conceptual_complexity, mapping_direction, source_domain, target_domain

**双维度交叉分类**

3级认知通达度 × 4类映射方向 = 12类构式：

| 类型编号 | 认知通达度 | 映射方向 | 原型地位 |
|:---------|:-----------|:---------|:---------|
| T1-T4 | 低 | 具抽/具具/抽抽/抽具 | 边缘成员 |
| T5-T8 | 中 | 具抽/具具/抽抽/抽具 | 次中心成员 |
| T9-T12 | 高 | 具抽/具具/抽抽/抽具 | 中心成员 |

**表A-5 双维度与CFMC-33字段对应**

| 维度 | 核心功能 | CFMC-33字段 | 字段类型 |
|:-----|:---------|:------------|:---------|
| 认知通达度 | 测量源域规约化程度 | cognitive_accessibility | 定距 (1-5) |
| | 常规度指标 | conventionality | 连续评分 (0.0-1.0) |
| | 新颖度指标 | metaphor_novelty | 连续评分 (0.0-1.0) |
| 概念复杂度 | 目标域概念化负荷及映射整合成本 | conceptual_complexity | 定距 (1-4) |
| 操作分类桥梁 | 映射方向分类 | mapping_direction | 定类 (4类) |
| | 源域类型 | source_domain | 定类 |
| | 目标域类型 | target_domain | 定类 |
| 原型梯度 | 原型距离测量 | prototype_distance | 定序 (1-3) |

#### 2.5 字段与研究问题对应

CFMC-33字段按功能分配服务于三个研究问题。

**表A-6 字段与研究问题对应关系**

| 研究问题 | 分析维度 | 核心CFMC-33字段 |
|:---------|:---------|:----------------|
| Q1类型特征 | 认知通达度与操作分类 | cognitive_accessibility, mapping_direction |
| | 概念复杂度与相关效度 | conceptual_complexity |
| | 源域/目标域判定与域类解释 | source_domain, target_domain |
| | 原型梯度 | prototype_distance |
| | 规约化与新颖度补充 | conventionality, metaphor_novelty |
| Q2网络组织 | 宏观类型节点属性 | cognitive_accessibility, mapping_direction |
| | 实例层链接类型 | link_type |
| | 网络边与功能角色 | inter_construction_links, function_in_network |
| Q3认知机制 | 认知域激活 | embodied_experience, source_domain, target_domain |
| | 认知参照点 | conventionality, cognitive_accessibility, prototype_distance |
| | 跨域映射 | mapping_direction, systematicity, entailment_richness；mapping_basis为辅助描述字段 |
| | 语言编码 | copula_function |

**字段复用说明**：

部分字段同时服务于多个研究问题。例如，source_domain和target_domain在Q1中用于判定映射方向并辅助解释概念复杂度，在Q3中则转化为认知域激活的频率代理；cognitive_accessibility既是Q1双维度分类的核心变量，也是Q3阶段2的测量指标；prototype_distance在原始标注中反映Q1的原型梯度等级，在Q3中则由Q1_05脚本替换为CA-MD空间中的连续标准化欧氏距离。概念复杂度本身主要服务Q1的认知分工检验，不作为当前Q3形成性模型的直接观测指标。这种字段复用体现了CFMC-33的设计经济性：41项字段充分覆盖三个研究问题的分析需求。

### 第三部分：字段详细说明

本部分详述CFMC-33字段体系的具体内容。字段按"基础字段→Level 1必填→Level 2补充→Level 3-4选填"的层级递进结构组织，共计41项 (33项必填+8项选填)。

#### 3.1 基础字段 (6项)

基础字段提供语料管理的元数据信息，确保每条语料可追溯、可定位。

**表A-7 基础字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 原始编号 | original_id | String | 唯一标识符 (如CFMC_0001) |
| 完整句子 | full_sentence | String | 包含系表隐喻构式的完整句子 |
| 构式形式 | construction | String | 提取的系表隐喻构式 (如"NP₁是NP₂") |
| 时间 | time | String | 语料来源时间 (如2020年) |
| 来源 | source | String | 语料来源 (如BCC语料库、《人民日报》) |
| 体裁 | genre | String | 新闻/文学/学术/口语/网络 |

#### 3.2 Level 1必填字段 (23项)

Level 1字段为核心必填项，覆盖五大类别 (A-E)，支撑四阶段认知编码机制的分析。其中10个观测指标进入当前SEM模型：

- **阶段一 (认知域激活)**：embodied_experience(具身经验)、source_domain(源域)、target_domain(目标域)
- **阶段二 (认知参照点锚定)**：conventionality(常规度)、cognitive_accessibility(认知通达度)、prototype_distance(原型距离)
- **阶段三 (跨域映射)**：mapping_direction(映射方向)、systematicity(系统性)、entailment_richness(蕴涵丰富度)；mapping_basis(映射基础)保留为辅助描述字段
- **结果变量**：copula_function(系词功能)

##### 3.2.1 A_基础识别 (4项)

**表A-8 A_基础识别字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 构式类型 | construction_type | String | 当前发布数据中的构式边界类型；Q1的12类操作类型由认知通达度等级与映射方向派生为`construction_type_12` |
| 主语 | subject | String | 主语成分 (NP₁，唤起目标域) |
| 系词 | copula | String | 系词列表 (是/为/即/成/等于等) |
| 表语 | predicate | String | 表语成分 (NP₂，唤起源域) |

**说明**：A类字段识别系表隐喻构式的基本句法成分。典型述谓型构式通常以主语 (NP₁)承载目标域、表语 (NP₂)提供源域；识别式、倒装式及其他非标准分配案例，须依据具体语境中的跨域映射关系标注，不按线性位置机械判定。

##### 3.2.2 B_隐喻成分 (7项)

**表A-9 B_隐喻成分字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 源域 | source_domain | String | 提供理解基础的概念域 (如JOURNEY, CONTAINER等) |
| 目标域 | target_domain | String | 被理解和表达的概念域 (如LIFE, EMOTION等) |
| 映射方向 | mapping_direction | Integer | 1-4定类 (1=具→具，2=具→抽，3=抽→抽，4=抽→具) |
| 隐喻类型 | metaphor_type | String | 概念隐喻分类 |
| 题元角色 | thematic_role | String | 主语的语义角色 |
| 系词功能 | copula_function | String-Coded | equative/attributive/identificational；Q3中重编码为阶段4结果变量Y |
| 构式义 | constructional_meaning | String | 构式整体意义 |

**说明**：B类字段描述隐喻的概念结构。源域和目标域是概念隐喻的核心要素，按跨域语义角色判定：典型述谓型构式通常以NP₂提供源域、NP₁承载目标域；识别式、倒装式及其他非标准分配案例，须依据具体语境中的跨域映射关系标注。mapping_direction是双维度分类的关键维度，与认知通达度共同决定构式的12类归属。

##### 3.2.3 C_认知机制 (3项)

**表A-10 C_认知机制字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 认知通达度 | cognitive_accessibility | Integer | 1-5级 (1=最难通达，5=最易通达) |
| 映射基础 | mapping_basis | String-Coded | 隐喻映射方式的辅助描述字段，不进入当前PLS-SEM的*η*₃测量模型 |
| 概念复杂度 | conceptual_complexity | Integer | 1-4级 (1=低，4=高) |

**说明**：C类字段测量认知加工的核心维度。认知通达度和概念复杂度构成理论双维度；12类构式的操作分类由3级CA与4类映射方向交叉形成，概念复杂度用于检验双维度负相关和原型梯度的相关效度，不直接进入当前Q3形成性模型。mapping_basis仅保留为映射方式的辅助描述字段。详细测量方案见附录C和附录D。

##### 3.2.4 D_认知生成路径 (3项)

**表A-11 D_认知生成路径字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 具身体验 | embodied_experience | Float | 0.0-1.0 (具身经验相关度) |
| 认知参照点 | cognitive_reference_point | String | 参照点类型描述 |
| 蕴涵丰富度 | entailment_richness | Float | 0.0-1.0连续评分，值越高表示映射蕴涵越丰富 |

**说明**：D类字段描述认知生成路径的特征。embodied_experience测量隐喻与具身经验的关联程度；cognitive_reference_point提供参照点类型描述；entailment_richness测量映射所携带的推理潜力，是阶段3跨域映射的核心指标。

##### 3.2.5 E_网络关系 (6项)

**表A-12 E_网络关系字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 原型距离 | prototype_distance | Integer/Float | 原始1=中心、2=次中心、3=边缘；Q3分析中替换为连续标准化欧氏距离 |
| 链接类型 | link_type | Integer | 1=隐喻扩展，2=多义，3=子部分，4=实例 |
| 构式间链接 | inter_construction_links | String | 关联构式标识列表 |
| 系统性 | systematicity | Float | 0.0-1.0连续评分，值越高表示映射越系统 |
| 常规度 | conventionality | Float | 0.0-1.0连续评分，值越高表示越规约 |
| 网络功能 | function_in_network | Integer | 1=中心，2=边缘，3=桥接，4=创新，5=模块核心 |

**说明**：E类字段描述构式的网络属性，支撑Q2构式网络组织研究。link_type对应Goldberg四类链接关系；prototype_distance在原始标注中用于说明原型梯度，进入Q3时改用Q1_05重算的连续距离；inter_construction_links和function_in_network支撑实例层网络解释；conventionality反映隐喻规约化程度，并在Q3阶段2中作为形成性间接指标。

#### 3.3 Level 2补充字段 (4项)

Level 2字段为必填的补充信息，用于捕捉汉语系表隐喻构式的语言特色和认知细节。

##### 3.3.1 F_句法特征 (1项)

**表A-13 F_句法特征字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 系词类型 | copula_type | String-Coded | 历史细分标签；数据中的zero不等于严格零系词样本 |

**说明**：copula_type为历史细分标签，当前Q1/Q2/Q3主体脚本不直接使用。数据中若出现zero，不得直接理解为严格零系词隐喻样本；严格零系词须同时满足无显性系词、NP₁ NP₂并置、可还原为"NP₁是NP₂"且存在跨域映射。copula_function是Q3模型的结果变量Y，编码为equative、attributive和identificational三类功能。

##### 3.3.2 G_汉语特色 (2项)

**表A-14 G_汉语特色字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 整体性意象 | holistic_imagery | Float | 0.0-2.0连续评分 (0=无，1=弱，2=强) |
| 关系性思维 | relational_thinking | Float | 0.0-2.0连续评分 (0=无，1=弱，2=强) |

**说明**：整体性意象测量隐喻表达是否体现汉语的整体性认知特征，关系性思维测量隐喻表达是否强调事物间的关系而非实体属性。两变量基于Nisbett (2003) 的分析-整体认知风格理论进行操作化。

##### 3.3.3 H_认知细化 (1项)

**表A-15 H_认知细化字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 隐喻新颖度 | metaphor_novelty | Float | 0.0-1.0连续评分，值越高表示越新颖 |

**说明**：隐喻新颖度作为认知通达度 (CA) 的补充测量指标，采用0.0-1.0连续评分，测量隐喻表达的规约化程度与创新程度。

#### 3.4 Level 3-4选填字段 (8项)

Level 3-4字段为选填项，Level 3用于深度研究需要，Level 4为质性字段 (用于深度个案分析)。

##### 3.4.1 Level 3研究选填 (2项)

**表A-16 Level 3研究选填字段说明**

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|:-------|:-------|:---------|:--------------|
| 家族标记 | family_marker | String | 构式家族标识 (如[时间隐喻构式群]、[情感隐喻构式群]) |
| 继承关系 | inheritance_relation | String | 父构式/子构式标识及继承类型 |

**说明**：Level 3字段用于深化构式网络分析。family_marker标识构式所属的语义家族；inheritance_relation描述构式间的上下位继承关系，支撑Q2网络拓扑结构分析。

##### 3.4.2 Level 4质性字段 (6项)

**表A-17 Level 4质性字段说明**

| 字段名 | 英文名 | 数据类型 | 说明 |
|:-------|:-------|:---------|:-----|
| 映射内容 | mapping_content | String | 具体映射关系描述 |
| 蕴涵 | entailment | String | 隐喻蕴涵详细说明 |
| 继承链接详情 | inheritance_links_detail | String | 继承关系的详细描述 |
| 多义链接详情 | polysemy_links_detail | String | 多义关系的详细描述 |
| 子部分链接详情 | subpart_links_detail | String | 子部分关系的详细描述 |
| 认知参照点描述 | cognitive_reference_point_description | String | 参照点的详细说明 |

**说明**：Level 4质性字段用于深度个案分析，提供隐喻映射、蕴涵关系和构式网络链接的详细文本描述。这些字段为选填项，主要用于质性分析和案例研究。

#### 3.5 小结

本部分详述了CFMC-33字段体系的具体内容。41个字段按"基础字段→Level 1必填→Level 2补充→Level 3-4选填"的层级递进结构组织：

1. **基础字段** (6项)：提供语料管理的基本元数据，确保数据可追溯
2. **Level 1必填** (23项)：覆盖五大核心类别，支撑四阶段认知编码机制的10个观测指标提取
3. **Level 2补充** (4项)：捕捉句法特征、汉语特色和认知细节
4. **Level 3-4选填** (8项)：Level 3深化字段支撑网络分析，Level 4质性字段用于个案深度描述

该体系设计遵循"一主干、三向整合"理论框架，既保证了标注的系统性和可操作性，又为多角度分析提供了数据支撑。各字段的详细定义、取值规范和标注示例，详见附录B《CFMC-33字段体系》。


### 第四部分：标注操作流程

本部分规定CFMC-33字段体系的标注操作流程，确保标注工作的系统性和规范性。

#### 4.1 标注流程总览

标注流程分为四个阶段，对应CFMC-33字段体系的层级结构：

```
标注完整流程
├── 阶段1：数据准备
│   ├── 读取语料
│   ├── 识别系表隐喻构式
│   └── 完成6个基础字段
├── 阶段2：Level 1标注 (23项必填)
│   ├── A_基础识别 (4项)
│   ├── B_隐喻成分 (7项)
│   ├── C_认知机制 (3项)
│   ├── D_认知生成路径 (3项)
│   └── E_网络关系 (6项)
├── 阶段3：Level 2标注 (4项必填)
│   ├── F_句法特征 (1项)
│   ├── G_汉语特色 (2项)
│   └── H_认知细化 (1项)
└── 阶段4：质量检查
    ├── 完整性检查 (33项必填字段)
    ├── 格式规范检查
    └── 逻辑一致性检查

说明：Level 3-4选填字段 (8项)根据研究需要选择性标注。
```

#### 4.2 标注操作步骤

##### 4.2.1 阶段1：数据准备

**步骤1：语料读取**
- 从语料库读取原始句子
- 记录来源、语体等元数据

**步骤2：构式识别**
- 识别"NP₁+系词+NP₂"结构
- 确认存在隐喻映射关系
- 排除明喻 (含"像""如""似"等标记词)

**步骤3：基础字段填写**

完成6个基础字段的标注：

| 字段 | 内容 |
|:-----|:-----|
| original_id | 语料唯一编号 |
| full_sentence | 包含构式的完整句子 |
| construction | 提取的系表隐喻构式 |
| time | 语料来源时间 |
| source | 语料来源 |
| genre | 体裁类型 |

##### 4.2.2 阶段2：Level 1标注

按四阶段认知编码机制的顺序进行标注：

**A_基础识别 (4项)**：识别构式的句法成分
- construction_type：记录当前发布数据中的构式边界类型；Q1的12类操作类型另由`construction_type_12`表示
- subject：提取主语成分(NP₁)
- copula：识别系词
- predicate：提取表语成分(NP₂)

**B_隐喻成分 (7项)**：分析概念隐喻结构
- source_domain/target_domain：确定源域和目标域 (如JOURNEY、LIFE等)
- mapping_direction：确定映射方向 (1=具→具，2=具→抽，3=抽→抽，4=抽→具)
- metaphor_type：记录概念隐喻分类
- thematic_role：记录主语语义角色
- copula_function：记录系词功能，Q3中作为语言编码结果变量Y
- constructional_meaning：记录构式整体意义

**C_认知机制 (3项)**：评估认知加工维度
- cognitive_accessibility：按1-5级评定认知通达度
- mapping_basis：记录映射方式，作为辅助描述字段，不进入当前PLS-SEM模型
- conceptual_complexity：按1-4级评定概念复杂度

**D_认知生成路径 (3项)**：描述认知生成路径特征
- embodied_experience：评估具身经验相关度 (0.0-1.0连续评分)
- cognitive_reference_point：记录参照点类型描述
- entailment_richness：评估蕴涵丰富度 (0.0-1.0连续评分)

**E_网络关系 (6项)**：标注构式网络属性
- link_type：确定链接类型 (隐喻扩展/多义/实例/子部分链接)
- prototype_distance：记录原始原型距离等级；Q3中使用连续标准化欧氏距离
- systematicity：评估系统性程度 (0.0-1.0连续评分)
- inter_construction_links：记录关联构式标识列表
- conventionality：评定常规度 (0.0-1.0连续评分)
- function_in_network：评定网络功能 (1=中心，2=边缘，3=桥接，4=创新，5=模块核心)

##### 4.2.3 阶段3：Level 2标注

**F_句法特征 (1项)**
- copula_type：历史系词类型标签；不直接作为严格零系词证据

**G_汉语特色 (2项)**
- holistic_imagery：整体性意象程度 (0.0-2.0连续评分，0=无，1=弱，2=强)
- relational_thinking：关系性思维程度 (0.0-2.0连续评分，0=无，1=弱，2=强)

**H_认知细化 (1项)**
- metaphor_novelty：隐喻新颖度 (0.0-1.0连续评分，值越高表示越新颖)

##### 4.2.4 阶段4：质量检查

1. **完整性检查**：确保33项必填字段全部填写，无空值
2. **格式规范检查**：验证数据类型和取值范围符合规范
3. **逻辑一致性检查**：验证字段间逻辑关系合理

#### 4.3 质量控制标准

##### 4.3.1 标注一致性要求

**表A-18 标注一致性标准**

| 字段类别 | 一致性指标 | 标准值 | 适用范围 |
|:---------|:-----------|:-------|:---------|
| 分类变量 | Cohen's Kappa | ≥0.75 | construction_type, mapping_direction等 |
| 连续变量 | ICC | ≥0.78 | cognitive_accessibility, conceptual_complexity等 |
| 文本字段 | 双人核查 | 100% | subject, predicate, source_domain等 |
| 标注者内信度 | 间隔两周重复标注 | 一致率≥85% | 全部字段 |

##### 4.3.2 完整性要求

- 33项必填字段 (6基础+23Level1+4Level2)须全部填写
- 8项选填字段 (Level 3-4)根据研究需要选择性填写
- 格式须符合附录B《CFMC-33字段体系》规范

##### 4.3.3 逻辑一致性检查

标注完成后，需进行以下逻辑验证：

1. **源域-目标域与映射方向一致性**：mapping_direction应与source_domain、target_domain的具体/抽象判定相容；当前字段体系不另设源域/目标域具体度字段
2. **通达度-复杂度关联**：高认知通达度通常对应较低概念复杂度，但该关系用于总体相关效度检查，不作为单条语料的机械裁定规则
3. **原型距离验证**：中心成员(prototype_distance=1)应接近CA—MD经验中心；概念复杂度另作相关效度检验，不预设其必然最低
4. **双维度分类验证**：认知通达度 (3级) × 映射方向 (4类)应正确对应12类构式

#### 4.4 小结

本部分规定了CFMC-33字段体系的标注操作流程。标注分为四个阶段：数据准备(6项基础字段)、Level 1标注(23项核心字段)、Level 2标注(4项补充字段)和质量检查。标注顺序遵循四阶段认知编码机制的理论逻辑：

1. **认知域激活**：识别源域、目标域并评估具身经验
2. **认知参照点锚定**：评估常规度、认知通达度和原型距离
3. **跨域映射**：分析映射方向、系统性和蕴涵丰富度，mapping_basis仅作辅助描述
4. **语言编码**：记录copula_function作为结果变量；E类网络字段另服务Q2构式网络分析

质量控制采用双人独立标注和Cohen's Kappa一致性检验，确保标注结果的信度。各字段的详细取值规范和标注示例，详见附录B《CFMC-33字段体系》。


### 第五部分：数据处理与分析

#### 5.1 数据预处理

##### 数据清洗
- 删除重复构式
- 检查字段完整性
- 验证数据格式规范
- 识别异常值和离群值

##### 数据格式转换
- Markdown → CSV格式转换 (用于统计分析)
- 编码统一为UTF-8
- 字段名称标准化
- 时间戳统一为ISO格式

#### 5.2 描述性统计分析

**8个分析层次**：
1. 基础分布：系词分布、语体分布、时间分布
2. 认知机制分布：认知通达度、概念复杂度、映射方向
3. 双维度交叉：3×4矩阵热力图(认知通达度×映射方向)
4. 域配对分布：源域-目标域高频配对
5. 构式特征分布：原型距离、链接类型、网络功能
6. 汉语特色分析：整体性意象、关系性思维、隐喻新颖度
7. 标记词通达度匹配：系词类型与认知通达度关联
8. 语体差异对比：不同语体的隐喻密度和类型偏好

#### 5.3 推断性统计分析

**7类分析内容**：
1. 数据质量检验：正态性检验、方差齐性检验
2. 假设检验：t检验、方差分析、卡方检验
3. 认知路径分析：结构方程模型 (SEM)验证四阶段认知编码机制
4. 聚类分析：基于高斯混合模型 (GMM)的构式类型识别
5. 因子分析：提取核心认知维度
6. 网络分析：构式网络的小世界性质、中心性分析
7. 相关性分析：认知通达度×概念复杂度×原型距离关联

#### 5.4 质性数据分析

**个案分析方法**：
- 典型案例深度阐释
- 理论三角验证
- 跨案例比较分析
- 历时演化路径追踪

**混合分析策略**：
- 定量数据识别关键案例
- 质性数据深化理论解释
- 定量-质性相互印证
- 理论-数据双向对话

### 第六部分：附录

#### 6.1 系词列表

**基本系词(4个)**：是、为、即、乃

**否定系词(5个)**：不是、非、并非、不为、绝非

**动态系词(15个)**：成为、变成、作为、当作、算是、称为、叫做、号称、堪称、可谓、正是、便是、就是、成、成了

**扩展系词(26个)**：乃是、实为、诚为、确为、系、属、算、当、做、充当、担任、扮演、化身、象征、代表、意味着、等同于、相当于、酷似、神似、貌似、俨然、无异、等于、属于、谓之

**强调型系词(2个)**：真是、简直是

**特殊系词(4个)**：只是、也是、还是、等于是

#### 6.2 明喻标记(排除标注)

像、如、似、如同、好比、仿佛、犹如、宛如、恰似、宛然、好似、类如、若

**说明**：包含明喻标记的构式不属于系表隐喻构式，应排除标注。本研究采用汉语语义优先原则，严格区分系词构式与明喻构式。

#### 6.3 常见问题解答

**Q1: 如何区分"像"和"酷似"？**

- "像" = 明喻标记 → 不标注 (程度未达阈值)
- "酷似" = 扩展系词 → 可标注 (强相似，程度≥90%)
- 依据：汉语语义优先原则 + 程度阈值原则

**Q2: 为什么英语"He is like a teacher"属于系表结构，但汉语"他像老师"不属于？**

语言类型学差异：
- 英语(屈折语)：形态句法优先，be是系动词，构成系表结构
- 汉语(孤立语)：语义优先，"像"是比拟词，构成明喻构式

本研究遵循汉语语义优先原则，严格区分系词构式与明喻构式。

**Q3: 如何判断认知通达度和概念复杂度？**

**认知通达度** (1-5级)：判断隐喻映射的规约化程度
- 5级：高度规约隐喻(如"时间是金钱")
- 4级：较规约隐喻
- 3级：中等规约隐喻
- 2级：较新颖隐喻
- 1级：高度创新隐喻

**概念复杂度** (1-4级)：判断目标域概念的抽象性和结构复杂度
- 1级：低(具体简单概念)
- 2级：较低(具体复杂概念或简单抽象概念)
- 3级：中等(中等抽象概念或结构较复杂概念)
- 4级：高(高度抽象或结构复杂的概念)

**说明**：认知通达度和概念复杂度构成理论双维度；12类构式的操作分类由认知通达度和映射方向交叉形成。详细测量方案见附录C和附录D。

#### 6.4 参考文献

**核心理论文献**：

Fauconnier, G., & Turner, M. (2002). *The way we think: Conceptual blending and the mind's hidden complexities*. New York: Basic Books.

Goldberg, A. E. (1995). *Constructions: A construction grammar approach to argument structure*. Chicago: University of Chicago Press.

Goldberg, A. E. (2006). *Constructions at work: The nature of generalization in language*. Oxford: Oxford University Press.

Goldberg, A. E. (2019). *Explain me this: Creativity, competition, and the partial productivity of constructions*. Princeton: Princeton University Press.

Kövecses, Z. (2010). *Metaphor: A practical introduction* (2nd ed.). Oxford: Oxford University Press.

Lakoff, G., & Johnson, M. (1980). *Metaphors we live by*. Chicago: University of Chicago Press.

Lakoff, G., & Johnson, M. (1999). *Philosophy in the flesh: The embodied mind and its challenge to western thought*. New York: Basic Books.

Langacker, R. W. (1993). Reference-point constructions. *Cognitive Linguistics*, 4(1), 1-38.

Langacker, R. W. (2008). *Cognitive grammar: A basic introduction*. Oxford: Oxford University Press.

Sullivan, K. (2013). *Frames and constructions in metaphoric language*. Amsterdam: John Benjamins.

*附录A 语料标注方案*
