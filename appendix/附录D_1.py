#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
附录D_1 概念复杂度指标预计算脚本
====================================

本脚本为CFMC语料库标注工作的辅助工具，基于概念复杂度(CC)测量框架中的
公式体系，为每条构式预计算CC的子指标默认值和综合得分，生成标注者参考
数据表。标注者在标注时参照这些预计算值，结合人工判定对子指标进行校准，
最终给出1-5级的概念复杂度综合评分。

测量框架（详见附录D）
--------------------
公式3-8:  CC = 0.55 × D_abstract + 0.45 × D_processing    (D-3)

  D_abstract  = 0.25 × F_field + 0.50 × A_level + 0.25 × D_number    (D-1, 公式3-6)
  D_processing = 0.60 × I_depth + 0.40 × S_schema                     (D-2, 公式3-7)

子指标说明
----------
维度一（认知域抽象程度 D_abstract）:
  - F_field    领域类型        5级 (0.20/0.40/0.60/0.80/1.00)
  - A_level    抽象性等级      4级 (0/0.33/0.67/1.00)
  - D_number   认知域数量      5级 (0.20/0.40/0.60/0.80/1.00)

维度二（映射加工深度 D_processing）:
  - I_depth    推理深度等级    4级 (0/0.33/0.67/1.00)
  - S_schema   意象图式复杂度  4级 (0/0.33/0.67/1.00)

自动推荐策略
------------
由于CC的五个子指标均为人工判定，本脚本基于以下可用信息提供默认推荐值:
  - target_domain (目标域)  → 推荐 F_field, A_level, D_number
  - mapping_direction (映射方向) → 推荐 I_depth, S_schema

推荐值仅为参考基线，标注者应根据具体语境进行校准。

使用方法
--------
# 基础模式：使用默认推荐值计算CC
python 附录D_1.py

# 指定CFMC语料库路径
python 附录D_1.py --cfmc /path/to/CFMC_5989.json

# 指定输出路径
python 附录D_1.py -o /path/to/output.csv

# 加载外部子指标标注文件（覆盖默认推荐值）
python 附录D_1.py --annotations cc_annotations.csv

依赖环境
--------
Python环境: /home/tomja/miniconda3/envs/m_s/bin/python
必需:  numpy, pandas
"""

import argparse
import json
import logging
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 日志配置
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ===================================================================
# 第一部分  常量与权重参数
# ===================================================================
# 以下权重系数基于试点研究(n=500)的探索性因子分析确定
# 详见附录D §1.4 及 §2.4.1

# CC主效应模型权重（公式D-3，对应论文公式3-8）
W_D_ABSTRACT = 0.55     # 认知域抽象程度权重
W_D_PROCESSING = 0.45   # 映射加工深度权重

# D_abstract子维度权重（公式D-1，对应论文公式3-6）
W_F_FIELD = 0.25        # 领域类型权重
W_A_LEVEL = 0.50        # 抽象性等级权重（最核心指标）
W_D_NUMBER = 0.25       # 认知域数量权重

# D_processing子维度权重（公式D-2，对应论文公式3-7）
W_I_DEPTH = 0.60        # 推理深度权重（核心指标）
W_S_SCHEMA = 0.40       # 意象图式复杂度权重

# 映射方向代码
MD_LABELS = {
    1: "具体→具体",
    2: "具体→抽象",
    3: "抽象→抽象",
    4: "抽象→具体",
}

# 目标域/源域代码与中文名映射
DOMAIN_NAMES = {
    "OB": "物体", "HM": "人体", "ST": "结构", "AB": "抽象",
    "LV": "生命", "BD": "建筑", "SP": "空间", "WR": "战争",
    "NT": "自然", "SN": "感知", "EM": "情感", "EC": "经济",
    "MR": "机器", "EV": "事件", "TH": "思维", "FC": "力量",
    "SC": "社会", "FD": "食物", "TR": "交通", "TM": "时间",
    "MC": "医疗", "LF": "光线", "GM": "游戏", "CM": "通讯",
    "MV": "运动",
}


# ===================================================================
# 第二部分  目标域分类与子指标默认值
# ===================================================================
# 基于附录D §2.2.2（领域类型）和 §2.2.4（认知域数量默认值）

# 领域类型分类（F_field）
# 理论依据: Langacker (1987: 147-166) 的认知域理论
FIELD_TYPE_MAP = {
    # --- 日常具体领域 (F_field=0.20) ---
    # 根植于直接感知经验 (Lakoff, 1987: 267-289)
    "OB": 0.20,   # 物体：可直接感知的物理实体
    "HM": 0.20,   # 人体：直接身体经验
    "NT": 0.20,   # 自然：自然界可感知现象
    "FD": 0.20,   # 食物：日常感知对象
    "SP": 0.20,   # 空间：基本感知域
    "SN": 0.20,   # 感知：感官直接体验
    "LF": 0.20,   # 光线：视觉感知
    "MV": 0.20,   # 运动：身体运动经验
    "TR": 0.20,   # 交通：日常可感知

    # --- 日常抽象领域 (F_field=0.40) ---
    # 从具体域隐喻投射而来的常规概念
    "TM": 0.40,   # 时间：从空间域投射的一阶抽象
    "EM": 0.40,   # 情感：从身体经验投射的一阶抽象
    "LV": 0.40,   # 生命：具有抽象延伸的日常概念
    "WR": 0.40,   # 战争：事件域的抽象延伸
    "FC": 0.40,   # 力量：从身体经验投射
    "EV": 0.40,   # 事件：日常抽象概念
    "GM": 0.40,   # 游戏：日常活动的抽象化

    # --- 专业具体领域 (F_field=0.60) ---
    # 需要专业知识但可感知的领域
    "BD": 0.60,   # 建筑：需要专业知识的可感知结构
    "MR": 0.60,   # 机器：需要技术知识的物理对象
    "MC": 0.60,   # 医疗：需要专业知识的身体经验
    "CM": 0.60,   # 通讯：需要技术知识的信息传递

    # --- 专业抽象领域 (F_field=0.80) ---
    # 需要专业知识的抽象概念
    "SC": 0.80,   # 社会：复杂抽象的社会关系域
    "EC": 0.80,   # 经济：需要专业知识的抽象系统
    "TH": 0.80,   # 思维：认知/心理抽象域
    "ST": 0.80,   # 结构：需要抽象思维的组织概念

    # --- 哲学抽象领域 (F_field=1.00) ---
    # 高度抽象的概念
    "AB": 0.80,   # 抽象：广义抽象概念（默认为专业抽象）
    # 注: AB域涵盖范围较广，部分条目可能属于哲学抽象(1.00)，
    # 标注者应根据具体语境调整
}

# 抽象性等级默认值（A_level）
# 理论依据: Lakoff & Johnson (1999: 45-59)
ABSTRACTNESS_LEVEL_MAP = {
    # 1级: 具体感知 (0)
    "OB": 0.00, "HM": 0.00, "NT": 0.00, "FD": 0.00,
    "SP": 0.00, "SN": 0.00, "LF": 0.00, "MV": 0.00, "TR": 0.00,

    # 2级: 一阶抽象 (0.33)
    "TM": 0.33, "EM": 0.33, "LV": 0.33, "WR": 0.33,
    "FC": 0.33, "EV": 0.33, "GM": 0.33,
    "BD": 0.33, "MR": 0.33, "MC": 0.33, "CM": 0.33,

    # 3级: 二阶抽象 (0.67)
    "SC": 0.67, "EC": 0.67, "TH": 0.67, "ST": 0.67,

    # AB域默认为二阶抽象，部分可能为高阶抽象
    "AB": 0.67,
}

# 认知域数量默认值（D_number）
# 基于附录D §2.2.4 (阶段2, 任务3)
D_NUMBER_DEFAULTS = {
    0.20: 0.40,   # 日常具体 → 2-3个基本域
    0.40: 0.60,   # 日常抽象 → 4-5个域
    0.60: 0.60,   # 专业具体 → 4-5个域（涉及专业感知经验）
    0.80: 0.80,   # 专业抽象 → 6+个域或复杂抽象域
    1.00: 1.00,   # 哲学抽象 → 高度复杂抽象域矩阵
}

# 推理深度默认值（I_depth），基于映射方向
# 理论依据: Sullivan (2013: 104-110) + Grady (1997)
I_DEPTH_DEFAULTS = {
    1: 0.00,    # 具体→具体: 直接映射，相似性映射为主
    2: 0.33,    # 具体→抽象: 一步推理，常规隐喻路径
    3: 0.67,    # 抽象→抽象: 多步推理，缺乏意象支撑
    4: 0.67,    # 抽象→具体: 多步推理，逆向映射
}

# 意象图式复杂度默认值（S_schema），基于映射方向
# 理论依据: Johnson (1987: 18-40)
S_SCHEMA_DEFAULTS = {
    1: 0.00,    # 具体→具体: 单一简单图式
    2: 0.33,    # 具体→抽象: 单一复杂图式
    3: 0.33,    # 抽象→抽象: 单一复杂图式至多图式
    4: 0.67,    # 抽象→具体: 多图式组合
}


# ===================================================================
# 第三部分  数据加载
# ===================================================================

def load_cfmc_data(json_path: str) -> tuple:
    """
    加载CFMC-33标注语料库JSON文件。

    Parameters
    ----------
    json_path : str
        CFMC_5989.json的完整路径

    Returns
    -------
    df : pd.DataFrame
        语料数据表（每行一条构式）
    metadata : dict
        语料库元信息
    """
    logger.info(f"加载语料库: {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    metadata = data.get("metadata", {})
    constructions = data.get("constructions", [])
    df = pd.DataFrame(constructions)

    # 整数字段类型转换
    int_fields = [
        "mapping_direction", "cognitive_accessibility",
        "conceptual_complexity",
    ]
    for col in int_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    logger.info(
        f"加载完成: {len(df)} 条构式, "
        f"{len(df.columns)} 个字段"
    )
    return df, metadata


def load_annotations(anno_path: str) -> pd.DataFrame:
    """
    加载外部子指标标注文件（可选）。

    标注文件为CSV格式，至少包含"语例ID"列，以及以下子指标列（部分或全部）:
    F_field, A_level, D_number, I_depth, S_schema

    Parameters
    ----------
    anno_path : str
        标注文件路径

    Returns
    -------
    anno_df : pd.DataFrame
        子指标标注数据
    """
    logger.info(f"加载外部标注文件: {anno_path}")
    anno_df = pd.read_csv(anno_path, encoding="utf-8-sig")
    valid_cols = {"语例ID", "F_field", "A_level", "D_number",
                  "I_depth", "S_schema"}
    found = set(anno_df.columns) & valid_cols
    logger.info(f"标注文件字段: {sorted(found)}")
    return anno_df


# ===================================================================
# 第四部分  子指标计算函数
# ===================================================================

def get_f_field(target_domain: str) -> float:
    """
    获取领域类型 F_field 的默认值。

    基于目标域代码查找预设分类表(FIELD_TYPE_MAP)。

    Parameters
    ----------
    target_domain : str
        目标域代码（如"AB", "HM", "SC"等）

    Returns
    -------
    float
        领域类型得分，范围{0.20, 0.40, 0.60, 0.80, 1.00}
    """
    return FIELD_TYPE_MAP.get(target_domain, 0.40)


def get_a_level(target_domain: str) -> float:
    """
    获取抽象性等级 A_level 的默认值。

    基于目标域代码查找预设分类表(ABSTRACTNESS_LEVEL_MAP)。

    Parameters
    ----------
    target_domain : str
        目标域代码

    Returns
    -------
    float
        抽象性等级得分，范围{0, 0.33, 0.67, 1.00}
    """
    return ABSTRACTNESS_LEVEL_MAP.get(target_domain, 0.33)


def get_d_number(f_field: float) -> float:
    """
    获取认知域数量 D_number 的默认值。

    基于F_field值查找默认表(D_NUMBER_DEFAULTS)，遵循附录D §2.2.4的规则:
    日常具体→0.40, 日常抽象→0.60, 专业具体→0.60, 专业抽象→0.80, 哲学抽象→1.00

    Parameters
    ----------
    f_field : float
        领域类型得分

    Returns
    -------
    float
        认知域数量得分，范围{0.20, 0.40, 0.60, 0.80, 1.00}
    """
    return D_NUMBER_DEFAULTS.get(f_field, 0.60)


def get_i_depth(mapping_direction: int) -> float:
    """
    获取推理深度等级 I_depth 的默认值。

    基于映射方向推荐默认推理深度:
    - MD=1 (具体→具体): 直接映射 (0)
    - MD=2 (具体→抽象): 一步推理 (0.33)
    - MD=3 (抽象→抽象): 多步推理 (0.67)
    - MD=4 (抽象→具体): 多步推理 (0.67)

    Parameters
    ----------
    mapping_direction : int
        映射方向 (1-4)

    Returns
    -------
    float
        推理深度得分，范围{0, 0.33, 0.67, 1.00}
    """
    return I_DEPTH_DEFAULTS.get(mapping_direction, 0.33)


def get_s_schema(mapping_direction: int) -> float:
    """
    获取意象图式复杂度 S_schema 的默认值。

    基于映射方向推荐默认图式复杂度:
    - MD=1 (具体→具体): 单一简单图式 (0)
    - MD=2 (具体→抽象): 单一复杂图式 (0.33)
    - MD=3 (抽象→抽象): 单一复杂图式 (0.33)
    - MD=4 (抽象→具体): 多图式组合 (0.67)

    Parameters
    ----------
    mapping_direction : int
        映射方向 (1-4)

    Returns
    -------
    float
        意象图式复杂度得分，范围{0, 0.33, 0.67, 1.00}
    """
    return S_SCHEMA_DEFAULTS.get(mapping_direction, 0.33)


# ===================================================================
# 第五部分  综合得分计算
# ===================================================================

def compute_d_abstract(
    f_field: float, a_level: float, d_number: float
) -> float:
    """
    计算维度一: 认知域抽象程度 D_abstract。

    公式D-1（对应论文公式3-6）:
        D_abstract = 0.25 × F_field + 0.50 × A_level + 0.25 × D_number

    权重分配理论依据 (Barsalou, 1999; Lakoff & Johnson, 1999: 45-59):
    - 抽象性等级 (0.50): 最核心指标，直接反映概念的抽象程度
    - 领域类型 (0.25): 区分日常/专业/哲学
    - 认知域数量 (0.25): 辅助指标，域数量的影响权重小于抽象程度

    Parameters
    ----------
    f_field : float
        领域类型得分
    a_level : float
        抽象性等级得分
    d_number : float
        认知域数量得分

    Returns
    -------
    float
        认知域抽象程度，范围[0, 1]
    """
    return W_F_FIELD * f_field + W_A_LEVEL * a_level + W_D_NUMBER * d_number


def compute_d_processing(i_depth: float, s_schema: float) -> float:
    """
    计算维度二: 映射加工深度 D_processing。

    公式D-2（对应论文公式3-7）:
        D_processing = 0.60 × I_depth + 0.40 × S_schema

    权重分配:
    - 推理深度 (0.60): 核心指标，直接反映映射加工的复杂度
    - 意象图式复杂度 (0.40): 辅助指标，反映认知图式的激活复杂度

    Parameters
    ----------
    i_depth : float
        推理深度等级得分
    s_schema : float
        意象图式复杂度得分

    Returns
    -------
    float
        映射加工深度，范围[0, 1]
    """
    return W_I_DEPTH * i_depth + W_S_SCHEMA * s_schema


def compute_cc_continuous(d_abstract: float, d_processing: float) -> float:
    """
    计算概念复杂度连续值 CC_continuous。

    公式D-3（对应论文公式3-8）:
        CC = 0.55 × D_abstract + 0.45 × D_processing

    权重分配遵循"概念表征优先于映射加工"原则:
    - 认知域抽象程度 (0.55): 目标域固有表征特征的测量
    - 映射加工深度 (0.45): 映射关系特征的测量

    Parameters
    ----------
    d_abstract : float
        认知域抽象程度
    d_processing : float
        映射加工深度

    Returns
    -------
    float
        概念复杂度连续值，范围[0, 1]
    """
    return W_D_ABSTRACT * d_abstract + W_D_PROCESSING * d_processing


def cc_continuous_to_level_quintile(
    cc_values: np.ndarray, cc_single: float
) -> int:
    """
    将CC连续值转换为1-5级量表（五分位法）。

    基于附录D §2.4.2:
    计算全部语料的五分位数，按分位数划分等级:
        [Q0, Q20)  → 1级 (极简单)
        [Q20, Q40) → 2级 (较简单)
        [Q40, Q60) → 3级 (中等)
        [Q60, Q80) → 4级 (较复杂)
        [Q80, Q100] → 5级 (极复杂)

    Parameters
    ----------
    cc_values : np.ndarray
        全部语料的CC连续值
    cc_single : float
        当前语例的CC连续值

    Returns
    -------
    int
        1-5级量表值
    """
    q20, q40, q60, q80 = np.percentile(cc_values, [20, 40, 60, 80])
    if cc_single >= q80:
        return 5
    elif cc_single >= q60:
        return 4
    elif cc_single >= q40:
        return 3
    elif cc_single >= q20:
        return 2
    else:
        return 1


def cc_continuous_to_level_equidistant(cc_score: float) -> int:
    """
    将CC连续值转换为1-5级量表（等距分段法）。

    将[0, 1]区间等分为5段:
        [0.00, 0.20) → 1级
        [0.20, 0.40) → 2级
        [0.40, 0.60) → 3级
        [0.60, 0.80) → 4级
        [0.80, 1.00] → 5级

    Parameters
    ----------
    cc_score : float
        CC连续值，范围[0, 1]

    Returns
    -------
    int
        1-5级量表值
    """
    if cc_score >= 0.80:
        return 5
    elif cc_score >= 0.60:
        return 4
    elif cc_score >= 0.40:
        return 3
    elif cc_score >= 0.20:
        return 2
    else:
        return 1


# ===================================================================
# 第六部分  批量计算引擎
# ===================================================================

def precompute_all(
    df: pd.DataFrame,
    annotations: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    对全部构式批量计算概念复杂度子指标和综合得分。

    计算流程:
    1. 基于target_domain推荐F_field, A_level, D_number默认值
    2. 基于mapping_direction推荐I_depth, S_schema默认值
    3. 若提供外部标注文件，用标注值覆盖默认值
    4. 计算D_abstract, D_processing, CC连续值
    5. 转换为1-5级量表（五分位法和等距法）

    Parameters
    ----------
    df : pd.DataFrame
        CFMC语料数据
    annotations : pd.DataFrame or None
        外部子指标标注数据（可选）

    Returns
    -------
    result : pd.DataFrame
        含子指标和综合得分的参考数据表
    """
    n = len(df)
    logger.info(f"开始批量计算，共{n}条构式")

    # 构建标注查找表（若提供）
    anno_dict = {}
    if annotations is not None:
        anno_cols = [c for c in annotations.columns
                     if c in {"F_field", "A_level", "D_number",
                              "I_depth", "S_schema"}]
        if "语例ID" in annotations.columns:
            for _, row in annotations.iterrows():
                rid = row["语例ID"]
                anno_dict[rid] = {
                    c: row[c] for c in anno_cols if pd.notna(row[c])
                }
            logger.info(
                f"外部标注覆盖 {len(anno_dict)} 条, "
                f"字段: {anno_cols}"
            )

    # ---------- 逐条计算 ----------
    results = []

    for i, row in df.iterrows():
        rid = row.get("id", f"row_{i}")
        subject = str(row.get("subject", ""))
        predicate = str(row.get("predicate", ""))
        target_domain = str(row.get("target_domain", ""))
        source_domain = str(row.get("source_domain", ""))
        md = row.get("mapping_direction", None)
        cc_annotated = row.get("conceptual_complexity", None)

        # --- 子指标默认值 ---
        f_field = get_f_field(target_domain)
        a_level = get_a_level(target_domain)
        d_number = get_d_number(f_field)
        i_depth = get_i_depth(md) if pd.notna(md) else 0.33
        s_schema = get_s_schema(md) if pd.notna(md) else 0.33

        # --- 外部标注覆盖 ---
        is_overridden = False
        if rid in anno_dict:
            anno = anno_dict[rid]
            if "F_field" in anno:
                f_field = anno["F_field"]
                is_overridden = True
            if "A_level" in anno:
                a_level = anno["A_level"]
                is_overridden = True
            if "D_number" in anno:
                d_number = anno["D_number"]
                is_overridden = True
            if "I_depth" in anno:
                i_depth = anno["I_depth"]
                is_overridden = True
            if "S_schema" in anno:
                s_schema = anno["S_schema"]
                is_overridden = True

        # --- 维度得分 ---
        d_abstract = compute_d_abstract(f_field, a_level, d_number)
        d_processing = compute_d_processing(i_depth, s_schema)

        # --- CC连续值 ---
        cc_continuous = compute_cc_continuous(d_abstract, d_processing)

        # --- 等距法等级 ---
        cc_level_eq = cc_continuous_to_level_equidistant(cc_continuous)

        results.append({
            "语例ID": rid,
            "主语(目标域)": subject,
            "谓语(源域)": predicate,
            "目标域": target_domain,
            "目标域名称": DOMAIN_NAMES.get(target_domain, target_domain),
            "源域": source_domain,
            "源域名称": DOMAIN_NAMES.get(source_domain, source_domain),
            "映射方向": md,
            "映射方向标签": MD_LABELS.get(md, ""),
            # --- 维度一子指标 ---
            "F_field": round(f_field, 2),
            "A_level": round(a_level, 2),
            "D_number": round(d_number, 2),
            "D_abstract": round(d_abstract, 4),
            # --- 维度二子指标 ---
            "I_depth": round(i_depth, 2),
            "S_schema": round(s_schema, 2),
            "D_processing": round(d_processing, 4),
            # --- 综合得分 ---
            "CC连续值": round(cc_continuous, 4),
            "CC等级(等距法)": cc_level_eq,
            "标注覆盖": "是" if is_overridden else "否",
            # --- 对照 ---
            "CC标注值": cc_annotated,
        })

        # 进度报告
        if (i + 1) % 1000 == 0:
            logger.info(f"  已处理 {i + 1}/{n} 条")

    result_df = pd.DataFrame(results)

    # ---------- 五分位法等级 ----------
    cc_values = result_df["CC连续值"].values
    quintile_levels = []
    q20, q40, q60, q80 = np.percentile(cc_values, [20, 40, 60, 80])
    for v in cc_values:
        quintile_levels.append(
            cc_continuous_to_level_quintile(cc_values, v)
        )
    result_df["CC等级(五分位法)"] = quintile_levels

    # ---------- 一致性统计 ----------
    if "CC标注值" in result_df.columns:
        annotated = result_df["CC标注值"].dropna()
        if len(annotated) > 0:
            eq_match = (
                result_df["CC等级(等距法)"] == result_df["CC标注值"]
            ).sum()
            qt_match = (
                result_df["CC等级(五分位法)"] == result_df["CC标注值"]
            ).sum()
            logger.info(
                f"与标注值的一致性: "
                f"等距法 {eq_match}/{len(annotated)} "
                f"({eq_match / len(annotated) * 100:.1f}%), "
                f"五分位法 {qt_match}/{len(annotated)} "
                f"({qt_match / len(annotated) * 100:.1f}%)"
            )

    logger.info(f"计算完成: {n}条构式")
    logger.info(
        f"  五分位数阈值: Q20={q20:.4f}, Q40={q40:.4f}, "
        f"Q60={q60:.4f}, Q80={q80:.4f}"
    )

    return result_df


# ===================================================================
# 第七部分  输出与报告
# ===================================================================

def save_results(
    result_df: pd.DataFrame,
    output_path: str,
    metadata: dict = None,
):
    """
    保存预计算结果为CSV文件，并生成汇总报告。

    Parameters
    ----------
    result_df : pd.DataFrame
        预计算结果
    output_path : str
        输出CSV路径
    metadata : dict or None
        语料库元信息
    """
    # 保存CSV
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info(f"结果已保存: {output_path}")

    # 生成汇总报告
    report_path = output_path.replace(".csv", "_汇总报告.txt")
    n = len(result_df)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("概念复杂度指标预计算 — 汇总报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        if metadata:
            f.write(f"语料库: {metadata.get('description', 'CFMC')}\n")
            f.write(
                f"语料总数: {metadata.get('construction_count', n)}\n"
            )
            f.write("\n")

        # --- 公式体系 ---
        f.write("--- 公式体系 ---\n")
        f.write(f"  CC = {W_D_ABSTRACT} × D_abstract + "
                f"{W_D_PROCESSING} × D_processing    (公式3-8)\n")
        f.write(f"  D_abstract  = {W_F_FIELD} × F_field + "
                f"{W_A_LEVEL} × A_level + "
                f"{W_D_NUMBER} × D_number    (公式3-6)\n")
        f.write(f"  D_processing = {W_I_DEPTH} × I_depth + "
                f"{W_S_SCHEMA} × S_schema    (公式3-7)\n\n")

        # --- 子指标统计 ---
        for col, name in [
            ("F_field", "领域类型"),
            ("A_level", "抽象性等级"),
            ("D_number", "认知域数量"),
            ("I_depth", "推理深度"),
            ("S_schema", "意象图式复杂度"),
        ]:
            vals = result_df[col]
            f.write(f"--- {name} ({col}) ---\n")
            f.write(f"  均值: {vals.mean():.4f}\n")
            f.write(f"  标准差: {vals.std():.4f}\n")
            f.write("  取值分布:\n")
            for v, cnt in sorted(Counter(vals).items()):
                pct = cnt / n * 100
                f.write(f"    {v:.2f}: {cnt}条 ({pct:.1f}%)\n")
            f.write("\n")

        # --- 维度得分统计 ---
        for col, name in [
            ("D_abstract", "认知域抽象程度"),
            ("D_processing", "映射加工深度"),
        ]:
            vals = result_df[col]
            f.write(f"--- {name} ({col}) ---\n")
            f.write(f"  范围: [{vals.min():.4f}, {vals.max():.4f}]\n")
            f.write(f"  均值: {vals.mean():.4f}\n")
            f.write(f"  标准差: {vals.std():.4f}\n\n")

        # --- CC连续值统计 ---
        cc_vals = result_df["CC连续值"]
        f.write("--- CC连续值 ---\n")
        f.write(f"  范围: [{cc_vals.min():.4f}, {cc_vals.max():.4f}]\n")
        f.write(f"  均值: {cc_vals.mean():.4f}\n")
        f.write(f"  标准差: {cc_vals.std():.4f}\n")
        q20, q40, q60, q80 = np.percentile(cc_vals, [20, 40, 60, 80])
        f.write(f"  五分位数: Q20={q20:.4f}, Q40={q40:.4f}, "
                f"Q60={q60:.4f}, Q80={q80:.4f}\n\n")

        # --- 等级分布（等距法） ---
        f.write("--- CC等级分布（等距法）---\n")
        for lv in range(1, 6):
            cnt = (result_df["CC等级(等距法)"] == lv).sum()
            pct = cnt / n * 100
            f.write(f"  {lv}级: {cnt}条 ({pct:.1f}%)\n")
        f.write("\n")

        # --- 等级分布（五分位法） ---
        f.write("--- CC等级分布（五分位法）---\n")
        for lv in range(1, 6):
            cnt = (result_df["CC等级(五分位法)"] == lv).sum()
            pct = cnt / n * 100
            f.write(f"  {lv}级: {cnt}条 ({pct:.1f}%)\n")
        f.write("\n")

        # --- 按映射方向分组 ---
        f.write("--- CC连续值按映射方向分组 ---\n")
        for md in sorted(MD_LABELS.keys()):
            subset = result_df[result_df["映射方向"] == md]
            if len(subset) > 0:
                md_cc = subset["CC连续值"]
                f.write(
                    f"  MD={md} ({MD_LABELS[md]}): "
                    f"n={len(subset)}, "
                    f"M={md_cc.mean():.4f}, "
                    f"SD={md_cc.std():.4f}\n"
                )
        f.write("\n")

        # --- 按目标域分组 ---
        f.write("--- CC连续值按目标域分组（前10）---\n")
        td_stats = (
            result_df.groupby(["目标域", "目标域名称"])["CC连续值"]
            .agg(["count", "mean", "std"])
            .reset_index()
            .sort_values("count", ascending=False)
            .head(10)
        )
        for _, r in td_stats.iterrows():
            f.write(
                f"  {r['目标域']}({r['目标域名称']}): "
                f"n={r['count']}, "
                f"M={r['mean']:.4f}, "
                f"SD={r['std']:.4f}\n"
            )
        f.write("\n")

        # --- 与标注值对照 ---
        annotated = result_df["CC标注值"].dropna()
        if len(annotated) > 0:
            f.write("--- 与标注值对照 ---\n")
            eq_match = (
                result_df["CC等级(等距法)"] == result_df["CC标注值"]
            ).sum()
            qt_match = (
                result_df["CC等级(五分位法)"] == result_df["CC标注值"]
            ).sum()
            f.write(
                f"  等距法一致率: {eq_match}/{len(annotated)} "
                f"({eq_match / len(annotated) * 100:.1f}%)\n"
            )
            f.write(
                f"  五分位法一致率: {qt_match}/{len(annotated)} "
                f"({qt_match / len(annotated) * 100:.1f}%)\n"
            )

            # 差值分布
            diff_eq = (
                result_df["CC等级(等距法)"] - result_df["CC标注值"]
            ).dropna()
            if len(diff_eq) > 0:
                f.write(f"  等距法差值(预计算-标注): "
                        f"M={diff_eq.mean():.3f}, "
                        f"SD={diff_eq.std():.3f}\n")
                for d in range(-4, 5):
                    cnt = (diff_eq == d).sum()
                    if cnt > 0:
                        f.write(
                            f"    差值={d:+d}: {cnt}条 "
                            f"({cnt / len(diff_eq) * 100:.1f}%)\n"
                        )

            f.write("\n")

            # 按映射方向的一致率
            f.write("  按映射方向的等距法一致率:\n")
            for md in sorted(MD_LABELS.keys()):
                sub = result_df[result_df["映射方向"] == md]
                sub_anno = sub["CC标注值"].dropna()
                if len(sub_anno) > 0:
                    sub_match = (
                        sub["CC等级(等距法)"] == sub["CC标注值"]
                    ).sum()
                    f.write(
                        f"    MD={md} ({MD_LABELS[md]}): "
                        f"{sub_match}/{len(sub_anno)} "
                        f"({sub_match / len(sub_anno) * 100:.1f}%)\n"
                    )
            f.write("\n")

        f.write("=" * 70 + "\n")
        f.write(
            "说明: 本表为基于目标域和映射方向的默认推荐值。标注者应根据\n"
            "具体语例的语境特征，对子指标进行校准后给出最终评分。\n"
            "各子指标的详细判定标准见附录D。\n"
        )

    logger.info(f"汇总报告已保存: {report_path}")


# ===================================================================
# 第八部分  主程序
# ===================================================================

def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="概念复杂度指标预计算（附录D_1）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基础模式（使用默认推荐值）
  python %(prog)s

  # 指定语料库路径
  python %(prog)s --cfmc /path/to/CFMC_5989.json

  # 加载外部标注文件覆盖默认值
  python %(prog)s --annotations cc_annotations.csv

  # 指定输出路径
  python %(prog)s -o /path/to/output.csv
        """,
    )
    parser.add_argument(
        "--cfmc",
        default=os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "论文撰写", "统计分析", "语料_输入", "CFMC_5989.json",
        ),
        help="CFMC_5989.json路径 (默认: 自动定位)",
    )
    parser.add_argument(
        "--annotations",
        default=None,
        help="外部子指标标注文件路径（CSV格式，覆盖默认推荐值）",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="输出CSV路径（默认: 与脚本同目录下的 附录D_1_预计算参考数据.csv）",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # ---------- 确定输出路径 ----------
    if args.output:
        output_path = args.output
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        output_path = os.path.join(script_dir, "附录D_1_预计算参考数据.csv")

    # ---------- 加载CFMC数据 ----------
    if not os.path.exists(args.cfmc):
        logger.error(f"语料库文件不存在: {args.cfmc}")
        sys.exit(1)
    df, metadata = load_cfmc_data(args.cfmc)

    # ---------- 加载外部标注（可选）----------
    annotations = None
    if args.annotations:
        if os.path.exists(args.annotations):
            annotations = load_annotations(args.annotations)
        else:
            logger.warning(f"标注文件不存在: {args.annotations}")

    # ---------- 批量计算 ----------
    result_df = precompute_all(df, annotations=annotations)

    # ---------- 保存结果 ----------
    save_results(result_df, output_path, metadata)

    logger.info("全部完成。")


if __name__ == "__main__":
    main()
