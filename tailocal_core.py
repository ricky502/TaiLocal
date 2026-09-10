#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TaiLocal 最台繁 · 核心转换引擎
Simplified Chinese → Taiwanese Traditional Chinese
Pipeline: 术语表(长词优先) → OpenCC s2twp → post_fix 二次修正
特性: HTML标签保护 / 英文语义锁定(uninstall≠卸載) / 全程log
"""
import re
import pandas as pd
from opencc import OpenCC

_cc = OpenCC('s2twp')

ZH_COL_CANDIDATES = ["中文", "zh-cn", "zh_cn", "zh-hans", "simplified", "sc", "cn"]
EN_COL_HINTS = ["en-us", "en_us", "en-", "english", "en"]


def _find_col(cols, candidates, hints=None):
    lower = [str(c).strip().lower() for c in cols]
    for cand in candidates:
        for i, c in enumerate(lower):
            if c == cand:
                return cols[i]
    if hints:
        for hint in hints:
            for i, c in enumerate(lower):
                if hint in c:
                    return cols[i]
    return None


def load_mapping(paths):
    """加载术语表（多个文件自动叠加，长词优先）"""
    mapping = {}
    loaded = []
    for p in paths:
        if not p or not os.path.exists(p):
            continue
        try:
            df = pd.read_csv(p, encoding="utf-8-sig")
            cols_lower = [str(c).strip().lower() for c in df.columns]
            if "source" in cols_lower and "target" in cols_lower:
                sc, tc = df.columns[cols_lower.index("source")], df.columns[cols_lower.index("target")]
            else:
                sc, tc = df.columns[0], df.columns[1]
            n = 0
            for _, row in df.iterrows():
                s, t = str(row[sc]).strip(), str(row[tc]).strip()
                if s and t and s.lower() != "nan" and t.lower() != "nan":
                    mapping[s] = t
                    n += 1
            loaded.append((os.path.basename(p), n))
        except Exception as e:
            loaded.append((os.path.basename(p), f"ERR {e}"))
    mapping = dict(sorted(mapping.items(), key=lambda x: len(x[0]), reverse=True))
    return mapping, loaded


import os


def load_post_fix(path):
    if not os.path.exists(path):
        return {}
    try:
        df = pd.read_csv(path, encoding="utf-8-sig")
        m = {}
        for _, row in df.iterrows():
            s, t = row.iloc[0], row.iloc[1]
            if pd.notna(s) and pd.notna(t):
                m[str(s).strip()] = str(t).strip()
        return dict(sorted(m.items(), key=lambda x: len(x[0]), reverse=True))
    except Exception:
        return {}


def classify_context(en):
    if pd.isna(en) or not str(en).strip():
        return "text"
    en = str(en).lower()
    if en in ["apply", "cancel", "delete", "save", "ok"]:
        return "action"
    if "app" in en or "application" in en:
        return "product"
    if "success" in en or "failed" in en or "completed" in en:
        return "status"
    return "text"


def convert_text(text, en, mapping, post_fix, log=None):
    """转换单条文本。log: 可传dict收集命中/未命中术语"""
    if pd.isna(text):
        return ""
    en_lower = str(en).lower() if en and not pd.isna(en) else ""
    if str(en).strip().upper() == "TIPS":
        return "提示"
    text = str(text)
    original = text
    context = classify_context(en)

    matched, missed = [], []

    # 引号→直角引号
    text = re.sub(r'"(.*?)"', r'「\1」', text)
    text = text.replace("\u201c", "「").replace("\u201d", "」")

    # 英文语义锁定（OpenCC/术语表都容易翻错的词）
    if "卸载" in text:
        if "unmount" in en_lower:
            text = text.replace("卸载", "__UNMOUNT__")
        elif "uninstall" in en_lower:
            text = text.replace("卸载", "__UNINSTALL__")
        elif en_lower.strip() == "remove":
            text = text.replace("卸载", "__REMOVE__")
    if re.search(r"\b(argument|arguments|arg|args)\b", en_lower):
        text = re.sub(r"参数|引数|參數|引數", "__ARG__", text)
    elif re.search(r"\b(parameter|parameters|param|params)\b", en_lower):
        text = re.sub(r"参数|引数|參數|引數", "__PARAM__", text)
    if re.search(r"\b(project|projects)\b", en_lower):
        text = re.sub(r"项目|項目", "__PROJECT__", text)
    if re.search(r"用户端|客户端|用戶端|客戶端", text):
        text = re.sub(r"用户端|客户端|用戶端|客戶端", "__CLIENT__", text)

    # HTML标签保护
    tags = {}
    def protect(m):
        k = f"__TAG_{len(tags)}__"
        tags[k] = m.group(0)
        return k
    text = re.sub(r"<[^>]+>", protect, text)

    # 术语替换（占位符防二次转换）
    placeholders = {}
    idx = 0
    for src, dst in mapping.items():
        if src == "应用":
            if context == "action":
                continue
            if context == "product":
                dst = "應用程式"
        if src in text:
            k = f"__TERM_{idx}__"
            idx += 1
            placeholders[k] = dst
            text = text.replace(src, k)
            matched.append(f"{src} -> {dst}")
        elif src in original:
            missed.append(src)

    converted = _cc.convert(text)

    for k, v in tags.items():
        converted = converted.replace(k, v)
    for s, d in post_fix.items():
        converted = converted.replace(s, d)
    for k, v in placeholders.items():
        converted = converted.replace(k, v)

    for k, v in [
        ("__UNMOUNT__", "卸載"), ("__UNINSTALL__", "解除安裝"), ("__REMOVE__", "移除"),
        ("__ARG__", "引數"), ("__PARAM__", "參數"), ("__PROJECT__", "專案"), ("__CLIENT__", "用戶端"),
    ]:
        converted = converted.replace(k, v)

    if log is not None:
        log.append({"original": original, "result": converted, "context": context,
                    "matched_terms": "; ".join(matched), "missed_terms": "; ".join(missed)})
    return converted


def convert_excel(input_file, terms_paths, post_fix_path, log_rows=None):
    """转换Excel：自动检测中文列/英文列，输出(_tw.xlsx)到原目录"""
    df = pd.read_excel(input_file)
    zh_col = _find_col(df.columns, ZH_COL_CANDIDATES)
    if zh_col is None:
        zh_col = df.columns[0]
    en_col = _find_col(df.columns, [], EN_COL_HINTS)

    mapping, loaded = load_mapping(terms_paths)
    post_fix = load_post_fix(post_fix_path)

    def conv(row):
        en = row[en_col] if en_col else ""
        return convert_text(row[zh_col], en, mapping, post_fix, log_rows)

    df["_zh-TW"] = df.apply(conv, axis=1)
    return df, loaded, len(mapping), len(post_fix)
