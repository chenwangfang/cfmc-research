## 附录A 语料标注方案

### 第一部分：总体设计

#### 1.1 研究目标

本标注方案旨在支撑以下三个核心研究问题的实证分析：
- **Q1（类型特征）**：汉语系表隐喻构式呈现哪些类型及其特征？该问题采用双维度分类体系（认知通达度×映射方向），识别12类构式并验证其原型梯度结构。
- **Q2（网络组织）**：汉语系表隐喻构式如何组织为构式网络？该问题基于Goldberg四类链接关系，检验构式网络的小世界性质。
- **Q3（认知机制）**：汉语系表隐喻构式的认知编码机制是什么？该问题验证四阶段认知编码机制（认知域激活→认知参照点锚定→跨域映射→语言编码），阐明12类构式共享的认知加工过程。


#### 1.2 语料设计

##### 总体规模与来源
- **原始总量**：6,022条
- **有效语料**：5,989条（去除33条重复语料）
- **来源**：北京语言大学BCC语料库
- **时间跨度**：1836年至2018年

##### 语体分布（实际）

| 语体 | 条数 | 占比 |
|------|------|------|
| 文学 | 3,048 | 50.9% |
| 新闻 | 2,522 | 42.1% |
| 网络 | 359 | 6.0% |
| 学术 | 58 | 1.0% |
| 对话 | 2 | 0.03% |

##### 双维度分布（实际）

**认知通达度分布**（归并为3级后）：

| 等级 | CA原始值 | 条数 | 占比 |
|------|---------|------|------|
| 高通达度 | 4-5 | 4,104 | 68.5% |
| 中通达度 | 3 | 1,825 | 30.5% |
| 低通达度 | 1-2 | 60 | 1.0% |

**映射方向分布**：

| 编码 | 映射方向 | 条数 | 占比 |
|------|---------|------|------|
| 3 | 抽象→抽象 | 2,001 | 33.4% |
| 1 | 具体→具体 | 1,690 | 28.2% |
| 2 | 具体→抽象 | 1,551 | 25.9% |
| 4 | 抽象→具体 | 747 | 12.5% |

#### 1.3 CFMC-33标注体系概览

本研究采用CFMC-33标注体系（Cognitive Framework for Metaphorical Constructions-33），将CFMC理论框架转化为可操作的标注规范。CFMC-33共包含41项字段（33项必填+8项选填），采用四层级结构。

##### 标注层级设计

| 层级 | 字段类别 | 字段数 | 性质 | 主要字段示例 |
|------|---------|--------|------|-------------|
| 基础字段 | 语料管理 | 6项 | 必填 | original_id, full_sentence, genre |
| Level 1 | 核心字段 | 23项 | 必填 | source_domain, cognitive_accessibility, link_type |
| Level 2 | 补充字段 | 4项 | 必填 | copula_type, holistic_imagery, metaphor_novelty |
| Level 3 | 深化字段 | 2项 | 选填 | family_marker, inheritance_relation |
| Level 4 | 质性字段 | 6项 | 选填 | mapping_content, entailment |

**设计原则**：CFMC-33的字段设计遵循"理论驱动+研究问题导向"原则。Level 1核心字段（23项）直接服务于Q1-Q3三个研究问题的假设检验，是统计分析的主要数据来源；Level 2补充字段（4项）测量汉语语法特点及认知细化维度；Level 3-4选填字段（8项）用于典型案例的深度分析。

**选填字段标注情况**：
- Level 3 family_marker：约1,216条有有效值
- Level 3 inheritance_relation：约5,986条有值（大部分为"继承自基本系表构式"）
- Level 4 质性字段：220条语料完成了全部6项质性标注

**后期补充字段（3项）**：
- pragmatic_function（语用功能）
- context_sensitivity（语境敏感度）
- discourse_type（语篇类型）

这3项字段在标注完成后批量补充，不计入CFMC-33的33项必填字段。

##### 标注员分工体系

```
标注员配置与职责：
├── 专家标注员（2人）
│   ├── 负责理论判断要求高的项目
│   ├── Level 3深化字段标注
│   ├── Level 4质性字段标注（选择性）
│   └── 疑难案例最终裁决
├── 高级标注员（3人）
│   ├── 负责Level 1核心标注
│   ├── Level 2补充标注
│   ├── 质量复核
│   └── 初步争议解决
└── 普通标注员（3人）
    ├── 负责基础字段标注
    ├── Level 1基础识别类标注
    ├── 数据预处理
    └── 格式规范检查
```

#### 1.4 基础字段（标注前必须完成）

**在进行标注前，每条语料必须先记录以下6个基础字段：**

1. **原始编号**（original_id）：语料唯一标识符（如zh55588）
2. **完整句子**（full_sentence）：包含系表隐喻构式的完整句子
3. **构式**（construction）：提取的系表隐喻构式（如"总路线是建设社会主义的锐利武器"）
4. **时间**（time）：语料来源时间（如1959）
5. **来源**（source）：语料来源（如"人民日报"）
6. **语体**（genre）：语体类型（**文学**、**新闻**、**学术**、**网络**、**对话**五种之一）

#### 语体分类说明

本研究采用五种核心语体分类：

##### 1. 文学语体
- **定义**：文学作品，包括小说、散文、诗歌等
- **典型来源**：小说、散文、诗歌、戏剧
- **语料占比**：50.9%（3,048条）

##### 2. 新闻语体
- **定义**：新闻报道、评论等新闻语体
- **典型来源**：人民日报、新华社报道、新闻评论
- **语料占比**：42.1%（2,522条）

##### 3. 网络语体
- **定义**：社交媒体、网络平台上的语言表达
- **典型来源**：微博、微信、网络论坛、社交媒体平台
- **语料占比**：6.0%（359条）

##### 4. 学术语体
- **定义**：学术论文、学术著作等正式学术语体
- **典型来源**：学术期刊论文、专著、学术报告
- **语料占比**：1.0%（58条）

##### 5. 对话语体
- **定义**：口语对话、访谈、日常交流等对话语体
- **典型来源**：日常对话、访谈记录、口语语料
- **语料占比**：0.03%（2条）

**语体判定优先级**：
1. 如果来源明确为"微博"、"论坛"、"社交媒体" → **网络语体**
2. 如果来源明确为"访谈"、"对话记录"、"口语语料" → **对话语体**
3. 如果语料包含明显的网络用语、表情符号、话题标签 → **网络语体**
4. 如果语料包含对话标记（"他说"、"我问"）或口语标记 → **对话语体**

---

### 第二部分：理论基础

#### 2.1 理论框架：一主干、三向整合

CFMC-33的设计遵循"一主干、三向整合"原则。

**主干理论：Sullivan隐喻构式理论**

Sullivan (2013) 的自主—依存原则为CFMC-33提供核心分析框架。在系表隐喻构式"NP₁是NP₂"中，NP₁为自主元素（唤起目标域），NP₂为依存元素（唤起源域）。

**三向整合**

1. **Langacker认知语法**：深化微观认知机制，为认知参照点、侧显/基底、认知域等概念提供操作化依据，对应C区字段（cognitive_accessibility）和D区字段（embodied_experience）。

2. **Goldberg构式网络理论**：补充网络视角，四类链接关系（隐喻扩展链接、多义链接、实例链接、子部分链接）直接对应E区字段（link_type）。

3. **汉语类型学特征**：实现语言适应，整体性思维等汉语特色对应G区字段（holistic_imagery, relational_thinking）和F区字段（copula_type设置"零系词"选项）。

#### 2.2 四阶段认知编码机制

四阶段认知编码机制是本研究为回答Q3（认知机制）而构建的核心理论工具，将Sullivan (2013) 的两步描述发展为可检验的形式化模型。四阶段机制采用11个CFMC-33字段作为SEM测量指标。

| 阶段 | 名称 | 理论来源 | CFMC-33字段 | SEM角色 |
|------|------|---------|------------|---------|
| 阶段1 | 认知域激活 | Sullivan evocation + Langacker域理论 | embodied_experience, source_domain, target_domain | 潜变量*η*₁（3指标） |
| 阶段2 | 认知参照点锚定 | Langacker认知参照点模型 | conventionality, cognitive_accessibility, prototype_distance | 潜变量*η*₂（3指标） |
| 阶段3 | 跨域映射 | Sullivan自主—依存原则 | mapping_direction, mapping_basis, systematicity, entailment_richness | 潜变量*η*₃（4指标） |
| 阶段4 | 语言编码 | Sullivan + Goldberg | copula_function | *η*₃的结果观测变量X₁₁ |

#### 2.3 双维度分类体系

双维度分类体系是本研究为回答Q1（类型特征）而构建的核心分析工具。

**认知通达度维度**：
- 原始量表：1-5级（1=最难通达，5=最易通达）
- 归并分级：3级（低：1-2级；中：3级；高：4-5级）
- 核心字段：cognitive_accessibility

**概念复杂度维度**：
- 操作化为映射方向的4类分类
- 核心字段：mapping_direction（1=具→具，2=具→抽，3=抽→抽，4=抽→具）

**双维度交叉分类**：3级认知通达度 × 4类映射方向 = 12类构式

| 类型编号 | 认知通达度 | 映射方向 | 原型地位 |
|---------|-----------|---------|---------|
| T1-T4 | 低 | 具抽/具具/抽抽/抽具 | 边缘成员 |
| T5-T8 | 中 | 具抽/具具/抽抽/抽具 | 次中心成员 |
| T9-T12 | 高 | 具抽/具具/抽抽/抽具 | 中心成员 |

#### 2.4 Q1-Q3研究问题与字段对应

| 研究问题 | 分析维度 | 核心CFMC-33字段 |
|---------|---------|----------------|
| Q1类型特征 | 认知通达度 | cognitive_accessibility, conventionality, metaphor_novelty |
| | 概念复杂度 | mapping_direction, source_domain, target_domain |
| | 原型梯度 | prototype_distance |
| Q2网络组织 | 链接类型 | link_type |
| | 网络边 | inter_construction_links, function_in_network |
| Q3认知机制 | 认知域激活 | embodied_experience, source_domain, target_domain |
| | 认知参照点 | conventionality, cognitive_accessibility, prototype_distance |
| | 跨域映射 | mapping_direction, mapping_basis, systematicity, entailment_richness |
| | 语言编码 | copula_function |

---

### 第三部分：字段详细说明

#### 3.1 基础字段（6项）

基础字段提供语料管理的元数据信息，确保每条语料可追溯、可定位。

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 原始编号 | original_id | String | 唯一标识符（如zh55588） |
| 完整句子 | full_sentence | String | 包含系表隐喻构式的完整句子 |
| 构式形式 | construction | String | 提取的系表隐喻构式 |
| 时间 | time | String | 语料来源时间（如1959） |
| 来源 | source | String | 语料来源（如"人民日报"） |
| 体裁 | genre | String | 文学/新闻/学术/网络/对话 |

#### 3.2 Level 1 核心字段（23项）

Level 1字段为核心必填项，覆盖五大类别（A-E），支撑四阶段认知编码机制的分析。

##### A. 基础识别（4项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 构式类型 | construction_type | String | copular_metaphor（主体，5,926条）/ 其他少量类型 |
| 主语 | subject | String | 主语成分（NP₁，唤起目标域） |
| 系词 | copula | String | 系词形式（"是"占95.5%，其余包括"即""就是""为"等） |
| 表语 | predicate | String | 表语成分（NP₂，唤起源域） |

**说明**：A类字段识别系表隐喻构式的基本句法成分。主语（NP₁）与目标域对应，表语（NP₂）与源域对应。

##### B. 隐喻成分（7项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 源域 | source_domain | String | 25个统一编码（见3.6节域分类体系） |
| 目标域 | target_domain | String | 24个编码（GM仅作为源域使用） |
| 映射方向 | mapping_direction | Integer | 1=具→具，2=具→抽，3=抽→抽，4=抽→具 |
| 隐喻类型 | metaphor_type | String | ontological（71.2%）/ structural（26.1%）/ 其他 |
| 题元角色 | thematic_role | String | 主语的语义角色描述 |
| 系词功能 | copula_function | String | attributive（48.1%）/ equative（40.1%）/ identificational（11.8%） |
| 构式义 | constructional_meaning | String | 构式整体意义描述 |

**说明**：B类字段描述隐喻的概念结构。mapping_direction是双维度分类的关键维度；copula_function是四阶段机制阶段4的结果变量。

**系词功能三分类**：
- **attributive（属性型）**：表达NP₁具有NP₂所描述的属性
- **equative（等同型）**：将NP₁等同于NP₂
- **identificational（识别型）**：通过NP₂识别或界定NP₁

##### C. 认知机制（3项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 认知通达度 | cognitive_accessibility | Integer | 1-5级（1=最难通达，5=最易通达；实际分布集中在3-5级） |
| 映射基础 | mapping_basis | String | similarity（90.9%）/ function / correlation / structure / causality / contiguity / function_similarity |
| 概念复杂度 | conceptual_complexity | Integer | 1-4级（1=极低，4=高；实际无5级取值） |

**说明**：C类字段测量认知加工的核心维度。cognitive_accessibility和mapping_direction共同决定12类构式归属（3级CA × 4类MD）。

**认知通达度判定标准**：
- 5级：高度规约隐喻（如"时间是金钱"）
- 4级：较常规隐喻
- 3级：中等新颖隐喻
- 2级：较新颖隐喻
- 1级：高度创新隐喻

**概念复杂度判定标准**：
- 1级：极低（具体简单概念）
- 2级：低（具体复杂或简单抽象概念，占50.8%）
- 3级：中等（中等抽象概念，占31.3%）
- 4级：高（高度抽象概念，占13.8%）

##### D. 认知生成路径（3项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 具身体验强度 | embodied_experience | Float | 0.0-1.0（具身经验相关度） |
| 认知参照点 | cognitive_reference_point | String | 参照点类型描述（全部5,989条有值） |
| 蕴涵丰富度 | entailment_richness | Float | 0.06-1.0（隐喻蕴涵程度） |

**说明**：D类字段描述认知生成路径。embodied_experience测量隐喻与具身经验的关联程度（阶段1指标）；entailment_richness测量映射所携带的推理潜力（阶段3指标）。

##### E. 网络关系（6项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 原型距离 | prototype_distance | Integer | 1=中心（58.6%），2=次中心（31.7%），3=边缘（9.8%） |
| 链接类型 | link_type | Integer | 1=隐喻扩展（84.9%），2=多义（9.4%），3=子部分（2.3%），4=实例（3.4%） |
| 构式间链接 | inter_construction_links | String | 与其他构式的关联描述（3-5个相关构式） |
| 系统性 | systematicity | Float | 0.2-1.0（隐喻系统性程度） |
| 常规度 | conventionality | Float | 0.1-1.0（隐喻规约化程度） |
| 网络功能 | function_in_network | Integer | 1=中心节点（51.0%），2=边缘节点（34.7%），3=桥接节点（5.6%），4=创新节点（4.0%），5=模块核心（4.7%） |

**Goldberg (2019) 四种链接类型**：
1. **隐喻扩展链接**（1）：通过隐喻映射建立的构式间联系
2. **多义链接**（2）：同一构式形式的不同意义/功能变体
3. **子部分链接**（3）：整体构式与其组成部分的关系
4. **实例链接**（4）：抽象构式图式的具体语言实例

**原型距离判定标准**：
- **中心成员（1）**：高通达度（CA=4-5），高规约化
- **次中心成员（2）**：中通达度（CA=3）
- **边缘成员（3）**：低通达度（CA=1-2），创新性强

#### 3.3 Level 2 补充字段（4项）

##### F. 句法特征（1项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 系词类型 | copula_type | String | standard（95.2%）/ basic / emphatic / extended / negative / zero / transformative / 其他 |

**copula_type取值说明**：
- **standard**：标准系词（"是"）
- **basic**：基本系词（"为""即""乃"等）
- **emphatic**：强调型（"真是""简直是""才是"等）
- **extended**：扩展系词（"成为""作为""俨然"等）
- **negative**：否定系词（"不是""并不是"等）
- **zero**：零系词
- **transformative**：转化型（"成了""变成"等）

##### G. 汉语特色（2项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 整体性意象 | holistic_imagery | Float | 0.0-2.0（0=无，1=部分，2=完全） |
| 关系性思维 | relational_thinking | Float | 0.0-2.0（0=无，1=部分，2=完全） |

**整体意象评分指标**：
- 使用整体性量词（整个、全部、一片、满）
- 省略局部描写直接呈现整体
- 使用"大X"类整体概括（大海、大地、天地）
- 使用全称表达（万物、天下、四海）

**关系思维评分指标**：
- 使用关系名词（缘分、关系、联系、纽带）
- 强调动态关系（相生、相克、互动、呼应）
- 使用对偶结构（阴阳、表里、虚实、动静）
- 强调整体关联（和谐、平衡、统一、融合）

##### H. 认知细化（1项）

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 隐喻新颖度 | metaphor_novelty | Float | 0.0-1.0（0=高度规约，1=高度创新） |

#### 3.4 Level 3 深化字段（2项，选填）

| 字段名 | 英文名 | 数据类型 | 说明 |
|--------|--------|---------|------|
| 家族标记 | family_marker | String | 构式家族归属标识（约1,216条有有效值） |
| 继承关系 | inheritance_relation | String | 构式继承类型（多数为"继承自基本系表构式"） |

#### 3.5 Level 4 质性分析字段（6项，选填）

**适用范围**：选择性标注，用于典型案例的深度个案研究。实际标注220条。

| 字段名 | 英文名 | 数据类型 | 说明 |
|--------|--------|---------|------|
| 映射内容 | mapping_content | String | 源域→目标域的详细映射内容描述 |
| 蕴涵关系 | entailment | String | 隐喻推理链条的详细阐释 |
| 继承链接详情 | inheritance_links_detail | String | 继承关系的详细描述 |
| 多义链接详情 | polysemy_links_detail | String | 多义关系的详细描述 |
| 子部分链接详情 | subpart_links_detail | String | 子部分关系的详细描述 |
| 认知参照点描述 | cognitive_reference_point_description | String | 参照点的详细说明和理论分析 |

#### 3.6 统一域分类体系（25个编码）

源域和目标域采用统一的25编码分类体系。同一编码既可作为源域也可作为目标域（GM仅作为源域使用）。

| 编码 | 中文名 | 说明 | 作为源域频率 | 作为目标域频率 |
|------|--------|------|-------------|---------------|
| AB | 抽象概念 | 哲学、科学、逻辑等抽象概念 | 516 | 1,518 |
| BD | 身体部位 | 外部/内部器官、感觉器官 | 222 | 179 |
| CM | 语言交流 | 言语行为、语言形式、信息传递 | 7 | 42 |
| EC | 经济商业 | 金钱财富、交易买卖、商业运营 | 129 | 102 |
| EM | 情感 | 基本情绪、复杂情感、情感状态 | 135 | 234 |
| EV | 事件过程 | 自然/社会/个人/历史事件 | 121 | 274 |
| FC | 力量动力 | 推拉力、压力、支撑力、阻力 | 84 | 2 |
| FD | 食物饮食 | 食物类型、味道口感、烹饪方式 | 46 | 35 |
| GM | 游戏竞赛 | 体育竞技、棋牌游戏、竞赛规则 | 7 | — |
| HM | 人类活动 | 日常活动、工作劳动、娱乐社交 | 1,104 | 1,138 |
| LF | 人生 | 生命历程、人生阶段、人生意义 | 8 | 153 |
| LV | 生命体 | 动物、植物、生命过程 | 263 | 70 |
| MC | 机器机械 | 简单/复杂机器、电子设备 | 33 | 8 |
| MR | 道德品质 | 品德善恶、行为规范、人格特质 | 123 | 150 |
| MV | 物理运动 | 直线/曲线运动、速度、升降 | 6 | 2 |
| NT | 自然现象 | 天气、地质、水文、光学、季节 | 186 | 191 |
| OB | 物体实体 | 自然物体、人造物品、建筑、容器 | 1,196 | 229 |
| SC | 社会关系 | 人际关系、社会组织、社会现象 | 81 | 806 |
| SN | 感知觉 | 视觉、听觉、触觉、味嗅觉 | 147 | 83 |
| SP | 空间位置 | 垂直/水平空间、距离、方向定位 | 203 | 132 |
| ST | 状态变化 | 物理/心理/社会/发展状态 | 992 | 113 |
| TH | 思维认知 | 思维过程、认知能力、知识学习 | 101 | 396 |
| TM | 时间 | 时间流逝、时间节点、时间价值 | 40 | 112 |
| TR | 旅行路径 | 旅程阶段、道路类型、旅行障碍 | 41 | 6 |
| WR | 战争冲突 | 军事行动、武器装备、战略战术 | 198 | 14 |

#### 3.7 后期补充字段（3项）

以下字段在CFMC-33标注完成后批量补充，不计入33项必填字段。

| 字段名 | 英文名 | 数据类型 | 取值范围/说明 |
|--------|--------|---------|-------------|
| 语用功能 | pragmatic_function | String | categorization（71.2%）/ explanation（28.5%）/ evaluation（0.4%） |
| 语境敏感度 | context_sensitivity | Float | 0.3（82.0%）/ 0.5（15.9%）/ 0.7（2.1%） |
| 语篇类型 | discourse_type | String | 与genre字段一致（文学/新闻/学术/网络/对话） |

---

### 第四部分：字段体系结构图

```
CFMC-33字段体系（41项）+ 3项补充字段
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
├── 选填字段（8项）
│   │
│   ├── Level 3 深化字段（2项）
│   │   family_marker, inheritance_relation
│   │
│   └── Level 4 质性字段（6项）
│       mapping_content, entailment, inheritance_links_detail,
│       polysemy_links_detail, subpart_links_detail,
│       cognitive_reference_point_description
│
└── 后期补充字段（3项，不计入CFMC-33）
    pragmatic_function, context_sensitivity, discourse_type
```

---

### 第五部分：标注操作流程

#### 5.1 标注流程总览

```
标注完整流程
├── 阶段1：数据准备（1-2分钟）
│   ├── 从CSV读取语料
│   ├── 识别系表隐喻构式
│   └── 完成6个基础字段标注
├── 阶段2：Level 1标注（6-8分钟）
│   ├── A部分：基础识别（4项）
│   ├── B部分：隐喻成分（7项）
│   ├── C部分：认知机制（3项）
│   ├── D部分：认知生成路径（3项）
│   └── E部分：网络关系（6项）
├── 阶段3：Level 2标注（2-3分钟）
│   ├── F部分：句法特征（1项）
│   ├── G部分：汉语特色（2项）
│   └── H部分：认知细化（1项）
├── 阶段4：质量检查（2-3分钟）
│   ├── 完整性检查（33项必填字段）
│   ├── 格式规范检查
│   └── 逻辑一致性检查
└── 阶段5（选填）
    ├── Level 3：深化字段（2项）
    └── Level 4：质性分析（6项，40-60分钟/案例）

总时间：
- 必填标注：11-16分钟/条
- 质性分析：+40-60分钟/案例（选填）
```

#### 5.2 质量控制标准

##### 定量字段质量标准

| 指标 | 标准 | 适用范围 |
|------|------|---------|
| Cohen's Kappa | ≥ 0.75 | Level 1核心字段（23项） |
| Cohen's Kappa | ≥ 0.70 | Level 2补充字段（4项） |
| ICC | ≥ 0.75 | 所有Float类型字段 |

**完整性要求**：33项必填字段全部填充，无空值。

##### 实际信度效度检验结果

| 指标 | 判断标准 | 实际值 |
|------|---------|--------|
| 初始一致性*κ* | ≥0.70 | 0.757 |
| 标注者间*κ* | ≥0.75 | 0.810 |
| 标注者间*ICC* | ≥0.78 | 0.981 |
| 整体*α* | ≥0.80 | 0.86 |
| 一致率 | ≥85% | 90.5% |
| 重测*r* | ≥0.85 | 0.974 |

详细验证过程见附录E。

---

### 第六部分：数据处理与分析

#### 6.1 数据预处理
- 删除重复语料（33条，保留年份较早的版本）
- 检查字段完整性
- 验证数据格式规范
- 后期批量补充pragmatic_function、context_sensitivity、discourse_type字段

#### 6.2 统计分析

**Q1类型特征分析**：
- GMM聚类分析：基于高斯混合模型识别12类构式
- LDA判别分析
- 原型梯度分析

**Q2网络组织分析**：
- 小世界性质检验
- 中心性分析
- 社区检测

**Q3认知机制分析**：
- PLS-SEM建模：四阶段认知编码机制的路径分析
- 中介效应分析
- 多组分析（按copula_function分3组）

---

### 第七部分：附录

#### 7.1 系词列表

**高频系词**（占比>0.1%）：

| 系词 | 频次 | 占比 |
|------|------|------|
| 是 | 5,722 | 95.5% |
| 即 | 112 | 1.9% |
| 就是 | 61 | 1.0% |
| 成了 | 7 | 0.1% |
| 便是 | 5 | 0.1% |

**低频系词**（各≤4条）：成为、才是、为、真是、不是、不过是、即是、都是、变成、成、并不是、也是、简直是、只是、乃是、俨然、等于是、还是、作为、可谓是等，共57种。

#### 7.2 常见问题解答

**Q1: 认知通达度和概念复杂度如何判定？**

- **认知通达度**（cognitive_accessibility）：判断隐喻映射的规约化程度。实际数据集中在3-5级（低通达度1-2级仅60条，占1%）。
- **概念复杂度**（conceptual_complexity）：判断目标域概念的抽象性和结构复杂度。实际取值1-4级（无5级取值）。
- **独立判定**：两个维度独立判定，不可相互影响。

**Q2: Level 4质性字段必须标注吗？**

Level 4质性字段为选填字段。实际共220条语料完成了全部6项质性标注。

**Q3: 系词功能三分类的术语来源是什么？**

copula_function的三分类（attributive/equative/identificational）源自Halliday (1967: 66) 和Higgins (1979) 的混合体系。

#### 7.3 参考文献

Goldberg, A. E. (1995). *Constructions: A construction grammar approach to argument structure*. Chicago: University of Chicago Press.

Goldberg, A. E. (2006). *Constructions at work: The nature of generalization in language*. Oxford: Oxford University Press.

Goldberg, A. E. (2019). *Explain me this: Creativity, competition, and the partial productivity of constructions*. Princeton: Princeton University Press.

Halliday, M. A. K. (1967). Notes on transitivity and theme in English: Part 1. *Journal of Linguistics*, 3(1), 37-81.

Higgins, F. R. (1979). *The pseudo-cleft construction in English*. New York: Garland.

Lakoff, G., & Johnson, M. (1980). *Metaphors we live by*. Chicago: University of Chicago Press.

Lakoff, G., & Johnson, M. (1999). *Philosophy in the flesh: The embodied mind and its challenge to western thought*. New York: Basic Books.

Langacker, R. W. (1993). Reference-point constructions. *Cognitive Linguistics*, 4(1), 1-38.

Langacker, R. W. (2008). *Cognitive grammar: A basic introduction*. Oxford: Oxford University Press.

Sullivan, K. (2013). *Frames and constructions in metaphoric language*. Amsterdam: John Benjamins.

---

*附录A 语料标注方案*
