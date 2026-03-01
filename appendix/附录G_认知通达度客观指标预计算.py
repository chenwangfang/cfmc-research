#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
附录G 认知通达度客观指标预计算脚本
====================================

本脚本为CFMC语料库标注工作的辅助工具，预先计算认知通达度(CA)测量框架中
的客观指标，生成标注者参考数据表。标注者在标注时参照这些预计算的客观数值，
结合人工评分成分（文化共享度、映射对应度），依据公式的权重结构做出1-5级的
综合判断。

测量框架（详见附录C）
--------------------
公式3-5:  CA = 0.55 × D_reg + 0.45 × D_trans

  D_reg  = 0.4 × L_entrench + 0.4 × C_entrench + 0.2 × Cul_share    (公式3-2)
  D_trans = 0.5 × Sem_dist   + 0.5 × Map_corr                        (公式3-3)
  D_context = Con_cue + Gen_dep                                        (公式3-4)

其中客观可计算指标为：
  - L_entrench  词汇固化度    基于BCC语料库词频
  - C_entrench  构式固化度    基于CFMC语料库源域频率
  - Sem_dist    语义距离      基于词向量余弦相似度
  - Con_cue     语境线索强度  基于修饰成分与主谓的语义关联

人工评分指标为：
  - Cul_share   文化共享度    标注者独立评分(1-5级)
  - Map_corr    映射对应度    标注者独立评分(1-5级)
  - Gen_dep     体裁依赖度    标注者独立评分(0-3分)

使用方法
--------
# 仅计算构式固化度（无需外部数据）
python 附录G_认知通达度客观指标预计算.py

# 加载BCC词频文件，计算词汇固化度
python 附录G_认知通达度客观指标预计算.py --bcc-freq BCC_word_freq.txt

# 加载词向量模型，计算语义距离
python 附录G_认知通达度客观指标预计算.py --word-vec Tencent_AILab_ChineseEmbedding.txt

# 完整计算（所有客观指标）
python 附录G_认知通达度客观指标预计算.py \\
    --bcc-freq BCC_word_freq.txt \\
    --word-vec Tencent_AILab_ChineseEmbedding.txt \\
    --extract-modifiers

依赖环境
--------
Python环境: /home/tomja/miniconda3/envs/m_s/bin/python
必需:  numpy, pandas
可选:  gensim (词向量加载), spacy + zh_core_web_sm (中文分词与依存分析)

词向量模型下载
--------------
腾讯AI Lab中文词向量(800万词, 200维):
https://ai.tencent.com/ailab/nlp/zh/embedding.html

BCC词频文件格式
---------------
制表符分隔的文本文件，每行一个词条:
    词语\\t频次
    的\\t500000000
    是\\t300000000
    ...
"""

import argparse
import json
import logging
import math
import os
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 可选依赖
# ---------------------------------------------------------------------------
try:
    from gensim.models import KeyedVectors
    HAS_GENSIM = True
except ImportError:
    HAS_GENSIM = False

try:
    import spacy
    HAS_SPACY = True
except ImportError:
    HAS_SPACY = False

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
# 以下权重系数基于试点研究(n=500)的探索性因子分析确定(Schmid, 2007)
# 详见附录C §2.5.1

# CA主效应模型权重（公式3-5）
W_D_REG = 0.55          # 认知域规约化程度权重
W_D_TRANS = 0.45         # 映射关联透明度权重

# D_reg子维度权重（公式3-2）
W_L_ENTRENCH = 0.40      # 词汇固化度权重
W_C_ENTRENCH = 0.40      # 构式固化度权重
W_CUL_SHARE = 0.20       # 文化共享度权重（人工评分）

# D_trans子维度权重（公式3-3）
W_SEM_DIST = 0.50         # 语义距离权重
W_MAP_CORR = 0.50         # 映射对应度权重（人工评分）

# BCC语料库参数
# BCC语料库(150亿字规模)中最高频词"的"约5亿次
BCC_F_MAX = 500_000_000

# OOV默认语义相似度（语料库平均值，详见附录C §2.3.2）
OOV_DEFAULT_SIMILARITY = 0.35

# 映射方向代码
MD_LABELS = {
    1: "具体→具体",
    2: "具体→抽象",
    3: "抽象→抽象",
    4: "抽象→具体",
}

# 源域代码与中文名映射
SOURCE_DOMAIN_NAMES = {
    "OB": "物体", "HM": "人体", "ST": "结构", "AB": "抽象",
    "LV": "生命", "BD": "建筑", "SP": "空间", "WR": "战争",
    "NT": "自然", "SN": "感知", "EM": "情感", "EC": "经济",
    "MR": "机器", "EV": "事件", "TH": "思维", "FC": "力量",
    "SC": "社会", "FD": "食物", "TR": "交通", "TM": "时间",
    "MC": "医疗", "LF": "光线", "GM": "游戏", "CM": "通讯",
    "MV": "运动",
}


# ===================================================================
# 第二部分  数据加载
# ===================================================================

def load_cfmc_data(json_path: str) -> tuple[pd.DataFrame, dict]:
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

    # 整数字段类型转换（JSON中存储为float）
    int_fields = [
        "mapping_direction", "cognitive_accessibility",
        "conceptual_complexity", "prototype_distance",
        "link_type", "function_in_network",
    ]
    for col in int_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")

    logger.info(
        f"加载完成: {len(df)} 条构式, "
        f"{len(df.columns)} 个字段"
    )
    return df, metadata


def load_bcc_freq(freq_path: str) -> dict[str, int]:
    """
    加载BCC语料库词频文件。

    文件格式：制表符分隔，每行"词语\\t频次"

    Parameters
    ----------
    freq_path : str
        BCC词频文件路径

    Returns
    -------
    freq_dict : dict
        {词语: 频次} 映射
    """
    logger.info(f"加载BCC词频文件: {freq_path}")
    freq_dict = {}
    with open(freq_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("\t")
            if len(parts) >= 2:
                word = parts[0].strip()
                try:
                    freq = int(parts[1].strip())
                    freq_dict[word] = freq
                except ValueError:
                    continue
    logger.info(f"词频表加载完成: {len(freq_dict)} 个词条")
    return freq_dict


def load_word_vectors(vec_path: str) -> "KeyedVectors":
    """
    加载预训练词向量模型。

    支持Tencent AI Lab中文词向量(800万词, 200维)等Word2Vec格式模型。
    下载地址: https://ai.tencent.com/ailab/nlp/zh/embedding.html

    Parameters
    ----------
    vec_path : str
        词向量文件路径(.txt或.bin格式)

    Returns
    -------
    model : KeyedVectors
        gensim词向量模型
    """
    if not HAS_GENSIM:
        raise ImportError(
            "需要安装gensim库: pip install gensim"
        )
    logger.info(f"加载词向量模型: {vec_path}")
    logger.info("（首次加载大型词向量文件可能需要数分钟）")

    is_binary = vec_path.endswith(".bin")
    model = KeyedVectors.load_word2vec_format(
        vec_path, binary=is_binary
    )
    logger.info(
        f"词向量加载完成: {len(model)} 个词, "
        f"{model.vector_size} 维"
    )
    return model


# ===================================================================
# 第三部分  中文文本处理
# ===================================================================

def load_spacy_model():
    """加载spaCy中文模型，用于分词和依存句法分析。"""
    if not HAS_SPACY:
        logger.warning("spaCy不可用，将使用简化的中文处理方法")
        return None
    try:
        nlp = spacy.load("zh_core_web_sm")
        logger.info("spaCy中文模型(zh_core_web_sm)加载完成")
        return nlp
    except OSError:
        logger.warning(
            "spaCy中文模型未安装，请运行: "
            "python -m spacy download zh_core_web_sm"
        )
        return None


def extract_head_word(phrase: str, nlp=None) -> str:
    """
    从短语中提取中心词（核心名词）。

    系表隐喻构式中，表语(NP2)可能是短语（如"建设社会主义的锐利武器"），
    需提取核心隐喻词（如"武器"）用于BCC词频查询和词向量计算。

    Parameters
    ----------
    phrase : str
        待处理的短语
    nlp : spacy.Language or None
        spaCy中文模型实例

    Returns
    -------
    head : str
        提取的中心词

    策略
    ----
    1. spaCy可用时：
       a. ROOT为名词 → 直接使用
       b. ROOT为动词 → 取最后一个名词（汉语偏正结构中核心名词在末尾）
    2. spaCy不可用时：取"的"后部分的末尾名词
    """
    if not phrase or not isinstance(phrase, str):
        return phrase or ""

    phrase = phrase.strip()

    # 单字或双字词直接返回
    if len(phrase) <= 2:
        return phrase

    # 方法1: spaCy依存分析
    if nlp is not None:
        doc = nlp(phrase)
        # 找ROOT词
        root_token = None
        for token in doc:
            if token.dep_ == "ROOT":
                root_token = token
                break
        # 若ROOT是名词，直接使用
        if root_token and root_token.pos_ in ("NOUN", "PROPN"):
            return root_token.text
        # 若ROOT是动词（如"建设社会主义的锐利武器"中的"建设"），
        # 取最后一个名词——汉语偏正结构中核心名词通常在短语末尾
        nouns = [t.text for t in doc if t.pos_ in ("NOUN", "PROPN")]
        if nouns:
            return nouns[-1]
        # 无名词时使用ROOT
        if root_token:
            return root_token.text

    # 方法2: 简化规则——取"的"后面内容的末尾词
    if "的" in phrase:
        after_de = phrase.split("的")[-1].strip()
        if len(after_de) >= 2:
            return after_de if len(after_de) <= 4 else after_de[-2:]
        elif after_de:
            return after_de

    # 方法3: 取末尾2-4字
    return phrase[-2:] if len(phrase) > 4 else phrase


def extract_modifiers_from_sentence(
    sentence: str, subject: str, predicate: str, nlp=None
) -> list[str]:
    """
    从完整句子中提取修饰成分（定语、状语）。

    用于计算语境线索强度(Con_cue)。提取规则参见附录C §2.4.2。

    Parameters
    ----------
    sentence : str
        完整原句
    subject : str
        主语（目标域表达）
    predicate : str
        谓语（源域表达）
    nlp : spacy.Language or None
        spaCy中文模型实例

    Returns
    -------
    modifiers : list[str]
        修饰成分列表
    """
    if not sentence or nlp is None:
        return []

    doc = nlp(sentence)
    modifiers = []
    for token in doc:
        # 提取定语(ATT)和状语(ADV)关系的成分
        if token.dep_ in ("amod", "nmod", "advmod", "attr", "nummod"):
            # 排除主语和谓语本身
            if token.text not in (subject, predicate) and len(token.text) >= 2:
                modifiers.append(token.text)

    return modifiers


# ===================================================================
# 第四部分  客观指标计算函数
# ===================================================================

def compute_l_entrench(f_source: int, f_max: int = BCC_F_MAX) -> float:
    """
    计算词汇固化度 L_entrench（公式3-2子指标1）。

    公式: L_entrench = log₁₀(f_source + 1) / log₁₀(f_max + 1)

    理论依据: 对数转换符合Zipf定律(Zipf, 1949)，反映词频与认知
    通达度的非线性关系——高频词的固化度边际递减。

    Parameters
    ----------
    f_source : int
        源域表达(表语NP₂)在BCC语料库中的总频次
    f_max : int
        BCC语料库中最高频词的频次(默认: "的"≈5亿次)

    Returns
    -------
    float
        词汇固化度，范围[0, 1]
    """
    if f_source <= 0:
        return 0.0
    return math.log10(f_source + 1) / math.log10(f_max + 1)


def compute_c_entrench(f_metaphor: int, f_max_metaphor: int) -> float:
    """
    计算构式固化度 C_entrench（公式3-2子指标2）。

    公式: C_entrench = log₁₀(f_metaphor + 1) / log₁₀(f_max_metaphor + 1)

    理论依据: 源域在隐喻构式中的出现频率反映了该源域在系表隐喻
    构式框架中的认知固化程度(Langacker, 2008: 220-235)。

    Parameters
    ----------
    f_metaphor : int
        该源域在CFMC语料库中的系表隐喻构式频次
    f_max_metaphor : int
        CFMC中最高频源域的频次

    Returns
    -------
    float
        构式固化度，范围[0, 1]
    """
    if f_metaphor <= 0:
        return 0.0
    return math.log10(f_metaphor + 1) / math.log10(f_max_metaphor + 1)


def compute_sem_dist(
    vec_source: np.ndarray, vec_target: np.ndarray
) -> float:
    """
    计算语义距离 Sem_dist（公式3-3子指标1）。

    公式: Sem_dist = (1 + cos(v_source, v_target)) / 2

    理论依据: Sullivan (2013: 104-110) 指出，源域与目标域在概念空间中
    的语义距离越近，映射路径越直接，认知加工越容易。

    Parameters
    ----------
    vec_source : np.ndarray
        源域(表语NP₂)的词向量
    vec_target : np.ndarray
        目标域(主语NP₁)的词向量

    Returns
    -------
    float
        语义距离（归一化），范围[0, 1]
    """
    norm_s = np.linalg.norm(vec_source)
    norm_t = np.linalg.norm(vec_target)
    if norm_s == 0 or norm_t == 0:
        return OOV_DEFAULT_SIMILARITY
    cos_sim = np.dot(vec_source, vec_target) / (norm_s * norm_t)
    return (1.0 + float(cos_sim)) / 2.0


def compute_con_cue(
    model: "KeyedVectors",
    modifiers: list[str],
    subject: str,
    predicate: str,
) -> float:
    """
    计算语境线索强度 Con_cue（公式3-4子指标1）。

    对于每个修饰成分w，计算其与主语和谓语的最大语义相似度:
        M_semantic(w) = max(cos(w, 主语), cos(w, 谓语))
    多个修饰成分取平均后标准化到[0, 1]:
        Con_cue = (M_avg + 1) / 2

    无修饰成分时返回0.5（中性值，无支持也无阻碍）。

    Parameters
    ----------
    model : KeyedVectors
        预训练词向量模型
    modifiers : list[str]
        修饰成分列表
    subject : str
        主语（目标域表达）
    predicate : str
        谓语（源域表达）

    Returns
    -------
    float
        语境线索强度，范围[0, 1]
    """
    if not modifiers:
        return 0.5

    scores = []
    for w in modifiers:
        try:
            sim_subj = model.similarity(w, subject)
        except KeyError:
            sim_subj = OOV_DEFAULT_SIMILARITY
        try:
            sim_pred = model.similarity(w, predicate)
        except KeyError:
            sim_pred = OOV_DEFAULT_SIMILARITY
        scores.append(max(sim_subj, sim_pred))

    m_avg = sum(scores) / len(scores)
    return (m_avg + 1.0) / 2.0


def get_word_vector(
    model: "KeyedVectors", word: str, nlp=None
) -> np.ndarray | None:
    """
    获取词语的词向量，含OOV回退策略。

    OOV处理（附录C §2.3.2）:
    1. 直接查询
    2. 提取中心词后查询
    3. 字向量平均
    4. 返回None（标记为OOV）

    Parameters
    ----------
    model : KeyedVectors
        词向量模型
    word : str
        目标词语
    nlp : optional
        spaCy模型（用于提取中心词）

    Returns
    -------
    np.ndarray or None
        词向量，OOV时返回None
    """
    if not word:
        return None

    # 策略1: 直接查询
    if word in model:
        return model[word]

    # 策略2: 提取中心词
    head = extract_head_word(word, nlp)
    if head != word and head in model:
        return model[head]

    # 策略3: 字向量平均
    char_vecs = [model[ch] for ch in word if ch in model]
    if char_vecs:
        return np.mean(char_vecs, axis=0)

    return None


# ===================================================================
# 第五部分  综合指标整合
# ===================================================================

def compute_d_reg_objective(
    l_entrench: float | None,
    c_entrench: float,
) -> float | None:
    """
    计算D_reg的客观成分基线值。

    公式3-2: D_reg = 0.4 × L_entrench + 0.4 × C_entrench + 0.2 × Cul_share
    其中Cul_share为人工评分，此处仅计算客观成分(L + C)。

    标注者可据此判断: 若客观基线已较高(>0.5)，则D_reg总值大概率在中高区间。

    Returns
    -------
    float or None
        客观成分值 (0.4L + 0.4C)，若L_entrench不可用则仅返回0.4C
    """
    if l_entrench is not None:
        return W_L_ENTRENCH * l_entrench + W_C_ENTRENCH * c_entrench
    else:
        return W_C_ENTRENCH * c_entrench


def compute_d_trans_objective(sem_dist: float | None) -> float | None:
    """
    计算D_trans的客观成分基线值。

    公式3-3: D_trans = 0.5 × Sem_dist + 0.5 × Map_corr
    其中Map_corr为人工评分，此处仅计算客观成分。

    Returns
    -------
    float or None
        客观成分值 (0.5 × Sem_dist)，Sem_dist不可用时返回None
    """
    if sem_dist is not None:
        return W_SEM_DIST * sem_dist
    return None


def ca_score_to_level(score: float) -> int:
    """
    将CA原始分([0,1])转换为1-5级量表。

    方法1（等距分段，附录C §2.5.3）:
        [0.80, 1.00] → 5级(极高通达)
        [0.60, 0.80) → 4级(高通达)
        [0.40, 0.60) → 3级(中等通达)
        [0.20, 0.40) → 2级(低通达)
        [0.00, 0.20) → 1级(极低通达)

    Parameters
    ----------
    score : float
        CA原始分，范围[0, 1]

    Returns
    -------
    int
        1-5级量表值
    """
    if score >= 0.80:
        return 5
    elif score >= 0.60:
        return 4
    elif score >= 0.40:
        return 3
    elif score >= 0.20:
        return 2
    else:
        return 1


# ===================================================================
# 第六部分  批量计算引擎
# ===================================================================

def precompute_all(
    df: pd.DataFrame,
    bcc_freq: dict[str, int] | None = None,
    wv_model: "KeyedVectors | None" = None,
    nlp=None,
    extract_mod: bool = False,
) -> pd.DataFrame:
    """
    对全部构式批量计算客观指标。

    Parameters
    ----------
    df : pd.DataFrame
        CFMC语料数据
    bcc_freq : dict or None
        BCC词频字典 {词: 频次}
    wv_model : KeyedVectors or None
        词向量模型
    nlp : spacy.Language or None
        spaCy中文模型
    extract_mod : bool
        是否提取修饰成分并计算Con_cue

    Returns
    -------
    result : pd.DataFrame
        含客观指标的参考数据表
    """
    n = len(df)
    logger.info(f"开始批量计算，共{n}条构式")

    # ---------- 构式固化度 C_entrench ----------
    # 统计CFMC中各源域的频次
    sd_freq = Counter(df["source_domain"].tolist())
    f_max_metaphor = max(sd_freq.values())  # 最高频源域频次
    logger.info(
        f"CFMC源域频率统计完成: {len(sd_freq)}个源域, "
        f"最高频={f_max_metaphor}"
    )

    # ---------- 逐条计算 ----------
    results = []
    oov_count_l = 0
    oov_count_sem = 0

    for i, row in df.iterrows():
        rid = row.get("id", f"row_{i}")
        subject = str(row.get("subject", ""))
        predicate = str(row.get("predicate", ""))
        source_domain = str(row.get("source_domain", ""))
        target_domain = str(row.get("target_domain", ""))
        md = row.get("mapping_direction", None)
        full_sentence = str(row.get("full_sentence", ""))

        # 提取中心词（用于BCC查询和词向量查询）
        pred_head = extract_head_word(predicate, nlp)
        subj_head = extract_head_word(subject, nlp)

        # --- C_entrench ---
        f_metaphor = sd_freq.get(source_domain, 0)
        c_entrench = compute_c_entrench(f_metaphor, f_max_metaphor)

        # --- L_entrench ---
        l_entrench = None
        bcc_freq_val = None
        if bcc_freq is not None:
            # 尝试: 完整谓语 → 中心词 → 主语
            bcc_freq_val = bcc_freq.get(predicate)
            if bcc_freq_val is None:
                bcc_freq_val = bcc_freq.get(pred_head)
            if bcc_freq_val is not None:
                l_entrench = compute_l_entrench(bcc_freq_val)
            else:
                oov_count_l += 1

        # --- Sem_dist ---
        sem_dist = None
        cos_sim_raw = None
        if wv_model is not None:
            vec_s = get_word_vector(wv_model, pred_head or predicate, nlp)
            vec_t = get_word_vector(wv_model, subj_head or subject, nlp)
            if vec_s is not None and vec_t is not None:
                sem_dist = compute_sem_dist(vec_s, vec_t)
                # 保留原始余弦相似度供参考
                norm_s = np.linalg.norm(vec_s)
                norm_t = np.linalg.norm(vec_t)
                if norm_s > 0 and norm_t > 0:
                    cos_sim_raw = float(
                        np.dot(vec_s, vec_t) / (norm_s * norm_t)
                    )
            else:
                oov_count_sem += 1

        # --- Con_cue ---
        con_cue = None
        modifiers_str = ""
        if extract_mod and wv_model is not None and nlp is not None:
            modifiers = extract_modifiers_from_sentence(
                full_sentence, subject, predicate, nlp
            )
            if modifiers:
                modifiers_str = "; ".join(modifiers)
                con_cue = compute_con_cue(
                    wv_model, modifiers,
                    subj_head or subject,
                    pred_head or predicate,
                )

        # --- 综合基线 ---
        d_reg_obj = compute_d_reg_objective(l_entrench, c_entrench)
        d_trans_obj = compute_d_trans_objective(sem_dist)

        # --- CA客观基线估计 ---
        # 仅包含客观成分的CA估计值，供标注者参考
        ca_obj = None
        if d_reg_obj is not None and d_trans_obj is not None:
            ca_obj = W_D_REG * d_reg_obj + W_D_TRANS * d_trans_obj
        elif d_reg_obj is not None:
            ca_obj = W_D_REG * d_reg_obj

        results.append({
            "语例ID": rid,
            "主语(目标域)": subject,
            "谓语(源域)": predicate,
            "谓语中心词": pred_head,
            "主语中心词": subj_head,
            "源域": source_domain,
            "源域名称": SOURCE_DOMAIN_NAMES.get(source_domain, source_domain),
            "目标域": target_domain,
            "目标域名称": SOURCE_DOMAIN_NAMES.get(target_domain, target_domain),
            "映射方向": md,
            "映射方向标签": MD_LABELS.get(md, ""),
            # --- C_entrench ---
            "CFMC源域频次": f_metaphor,
            "C_entrench": round(c_entrench, 4),
            # --- L_entrench ---
            "BCC词频": bcc_freq_val,
            "L_entrench": round(l_entrench, 4) if l_entrench is not None else None,
            # --- Sem_dist ---
            "余弦相似度": round(cos_sim_raw, 4) if cos_sim_raw is not None else None,
            "Sem_dist": round(sem_dist, 4) if sem_dist is not None else None,
            # --- Con_cue ---
            "修饰成分": modifiers_str if extract_mod else None,
            "Con_cue": round(con_cue, 4) if con_cue is not None else None,
            # --- 综合基线 ---
            "D_reg客观基线": round(d_reg_obj, 4) if d_reg_obj is not None else None,
            "D_trans客观基线": round(d_trans_obj, 4) if d_trans_obj is not None else None,
            "CA客观基线": round(ca_obj, 4) if ca_obj is not None else None,
            "CA基线等级": ca_score_to_level(ca_obj) if ca_obj is not None else None,
        })

        # 进度报告
        if (i + 1) % 1000 == 0:
            logger.info(f"  已处理 {i + 1}/{n} 条")

    result_df = pd.DataFrame(results)

    # 统计报告
    logger.info(f"计算完成: {n}条构式")
    logger.info(f"  C_entrench: 全部可用 ({n}/{n})")
    if bcc_freq is not None:
        available_l = n - oov_count_l
        logger.info(
            f"  L_entrench: {available_l}/{n}可用, "
            f"{oov_count_l}条BCC未收录"
        )
    else:
        logger.info("  L_entrench: 未计算（未提供BCC词频文件）")
    if wv_model is not None:
        available_sem = n - oov_count_sem
        logger.info(
            f"  Sem_dist: {available_sem}/{n}可用, "
            f"{oov_count_sem}条词向量未覆盖"
        )
    else:
        logger.info("  Sem_dist: 未计算（未提供词向量模型）")

    return result_df


# ===================================================================
# 第七部分  输出与报告
# ===================================================================

def save_results(
    result_df: pd.DataFrame,
    output_path: str,
    metadata: dict | None = None,
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
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write("认知通达度客观指标预计算 — 汇总报告\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 70 + "\n\n")

        if metadata:
            f.write(f"语料库: {metadata.get('description', 'CFMC')}\n")
            f.write(
                f"语料总数: {metadata.get('construction_count', len(result_df))}\n"
            )
            f.write("\n")

        # C_entrench统计
        f.write("--- 构式固化度 C_entrench ---\n")
        c_vals = result_df["C_entrench"]
        f.write(f"  范围: [{c_vals.min():.4f}, {c_vals.max():.4f}]\n")
        f.write(f"  均值: {c_vals.mean():.4f}\n")
        f.write(f"  标准差: {c_vals.std():.4f}\n")
        f.write("\n  源域频次分布:\n")
        sd_stats = (
            result_df.groupby(["源域", "源域名称"])["CFMC源域频次"]
            .first()
            .reset_index()
            .sort_values("CFMC源域频次", ascending=False)
        )
        for _, r in sd_stats.iterrows():
            f.write(
                f"    {r['源域']}({r['源域名称']}): "
                f"{r['CFMC源域频次']}次, "
                f"C={compute_c_entrench(r['CFMC源域频次'], sd_stats['CFMC源域频次'].max()):.4f}\n"
            )

        # L_entrench统计
        l_col = result_df["L_entrench"].dropna()
        if len(l_col) > 0:
            f.write(f"\n--- 词汇固化度 L_entrench ---\n")
            f.write(f"  可用: {len(l_col)}/{len(result_df)}条\n")
            f.write(f"  范围: [{l_col.min():.4f}, {l_col.max():.4f}]\n")
            f.write(f"  均值: {l_col.mean():.4f}\n")
            f.write(f"  标准差: {l_col.std():.4f}\n")
        else:
            f.write(f"\n--- 词汇固化度 L_entrench ---\n")
            f.write("  未计算（未提供BCC词频文件）\n")

        # Sem_dist统计
        sem_col = result_df["Sem_dist"].dropna()
        if len(sem_col) > 0:
            f.write(f"\n--- 语义距离 Sem_dist ---\n")
            f.write(f"  可用: {len(sem_col)}/{len(result_df)}条\n")
            f.write(f"  范围: [{sem_col.min():.4f}, {sem_col.max():.4f}]\n")
            f.write(f"  均值: {sem_col.mean():.4f}\n")
            f.write(f"  标准差: {sem_col.std():.4f}\n")
        else:
            f.write(f"\n--- 语义距离 Sem_dist ---\n")
            f.write("  未计算（未提供词向量模型）\n")

        # Con_cue统计
        cue_col = result_df["Con_cue"].dropna()
        if len(cue_col) > 0:
            f.write(f"\n--- 语境线索强度 Con_cue ---\n")
            f.write(f"  可用: {len(cue_col)}/{len(result_df)}条\n")
            f.write(f"  范围: [{cue_col.min():.4f}, {cue_col.max():.4f}]\n")
            f.write(f"  均值: {cue_col.mean():.4f}\n")

        # CA客观基线统计
        ca_col = result_df["CA客观基线"].dropna()
        if len(ca_col) > 0:
            f.write(f"\n--- CA客观基线 ---\n")
            f.write(f"  可用: {len(ca_col)}/{len(result_df)}条\n")
            f.write(f"  范围: [{ca_col.min():.4f}, {ca_col.max():.4f}]\n")
            f.write(f"  均值: {ca_col.mean():.4f}\n")
            f.write(f"  标准差: {ca_col.std():.4f}\n")
            level_col = result_df["CA基线等级"].dropna()
            if len(level_col) > 0:
                f.write("  等级分布:\n")
                for lv in range(1, 6):
                    count = (level_col == lv).sum()
                    pct = count / len(level_col) * 100
                    f.write(f"    {lv}级: {count}条 ({pct:.1f}%)\n")

        # 权重参数记录
        f.write(f"\n--- 权重参数（附录C）---\n")
        f.write(f"  CA = {W_D_REG} × D_reg + {W_D_TRANS} × D_trans\n")
        f.write(
            f"  D_reg = {W_L_ENTRENCH} × L + "
            f"{W_C_ENTRENCH} × C + "
            f"{W_CUL_SHARE} × Cul_share\n"
        )
        f.write(
            f"  D_trans = {W_SEM_DIST} × Sem + "
            f"{W_MAP_CORR} × Map_corr\n"
        )
        f.write(f"  BCC f_max = {BCC_F_MAX:,}\n")

        f.write("\n" + "=" * 70 + "\n")
        f.write(
            "说明: 本表为客观指标参考值。标注者在此基础上综合文化共享度\n"
            "和映射对应度的独立评分，依据公式的权重结构做出1-5级的综合判断。\n"
        )

    logger.info(f"汇总报告已保存: {report_path}")


# ===================================================================
# 第八部分  主程序
# ===================================================================

def build_parser() -> argparse.ArgumentParser:
    """构建命令行参数解析器。"""
    parser = argparse.ArgumentParser(
        description="认知通达度客观指标预计算（附录G）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 仅计算构式固化度
  python %(prog)s

  # 加载BCC词频
  python %(prog)s --bcc-freq BCC_word_freq.txt

  # 完整计算
  python %(prog)s --bcc-freq BCC_word_freq.txt --word-vec Tencent.txt --extract-modifiers
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
        "--bcc-freq",
        default=None,
        help="BCC词频文件路径（制表符分隔: 词语\\t频次）",
    )
    parser.add_argument(
        "--word-vec",
        default=None,
        help="预训练词向量文件路径（Word2Vec格式）",
    )
    parser.add_argument(
        "--extract-modifiers",
        action="store_true",
        help="是否提取修饰成分并计算Con_cue（需要spaCy和词向量）",
    )
    parser.add_argument(
        "-o", "--output",
        default=None,
        help="输出CSV路径（默认: 与脚本同目录下的 附录G_预计算参考数据.csv）",
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
        output_path = os.path.join(script_dir, "附录G_预计算参考数据.csv")

    # ---------- 加载CFMC数据 ----------
    if not os.path.exists(args.cfmc):
        logger.error(f"语料库文件不存在: {args.cfmc}")
        sys.exit(1)
    df, metadata = load_cfmc_data(args.cfmc)

    # ---------- 加载BCC词频 ----------
    bcc_freq = None
    if args.bcc_freq:
        if os.path.exists(args.bcc_freq):
            bcc_freq = load_bcc_freq(args.bcc_freq)
        else:
            logger.warning(f"BCC词频文件不存在: {args.bcc_freq}")

    # ---------- 加载词向量 ----------
    wv_model = None
    if args.word_vec:
        if os.path.exists(args.word_vec):
            wv_model = load_word_vectors(args.word_vec)
        else:
            logger.warning(f"词向量文件不存在: {args.word_vec}")

    # ---------- 加载spaCy ----------
    nlp = None
    if args.extract_modifiers or True:
        # 始终尝试加载spaCy（用于中心词提取）
        nlp = load_spacy_model()

    # ---------- 批量计算 ----------
    result_df = precompute_all(
        df,
        bcc_freq=bcc_freq,
        wv_model=wv_model,
        nlp=nlp,
        extract_mod=args.extract_modifiers,
    )

    # ---------- 保存结果 ----------
    save_results(result_df, output_path, metadata)

    logger.info("全部完成。")


if __name__ == "__main__":
    main()
