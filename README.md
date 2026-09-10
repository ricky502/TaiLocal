# TaiLocal 最台繁

> **Taiwan + Localization** — 简体中文 → 台湾繁體中文 的专业批量转换工具

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 這是什麼 / What is this

把簡體中文產品文案批量轉換成「台灣人一眼覺得自然」的繁體中文。

**簡轉繁不是字符轉換，是在地化。** 通用工具只會把「内存」轉成「內存」，台灣用戶一看就知道是對岸寫的。TaiLocal 轉出來的是：

| 簡體原文 | 普通工具輸出 | TaiLocal 輸出 |
|---|---|---|
| 内存不足 | 內存不足 | **記憶體**不足 |
| 卸载驱动 | 卸載驅動 | **解除安裝**驅動 |
| 网络设置 | 網絡設置 | **網路設定** |
| 项目参数 | 項目參數 | **專案參數** |

## ✨ 特性 / Features

- **🖥️ 圖形界面**：打開軟體 → 選 Excel → 翻譯完成。檔案叫什麼名字、在哪個碟都行，輸出自動存在原檔案旁邊
- **📚 兩級術語庫**：`terms.csv` 公共術語（千條級）+ `terms_private.csv` 個人術語（自動疊加，長詞優先）
- **🔒 英文語義鎖定**：根據英文原文鎖定譯法 —— `unmount→卸載`、`uninstall→解除安裝`、`remove→移除`，杜絕 OpenCC 誤翻
- **🛡️ HTML 保護**：`<b>软件设置</b>` 轉換後標籤完好無損
- **🔧 post_fix 二次修正**：OpenCC 轉完再過一遍人工校對規則（`滑鼠`、`帆船`、` connection埠` 這類坑全部兜住）
- **📋 全程 Log**：每條輸出記錄原文/結果/命中術語/未命中術語，方便審計與補詞

## 🚀 快速開始 / Quick Start

### 方式一：直接運行（需 Python 3.8+）

```bash
pip install -r requirements.txt
python tailocal.py        # 打開圖形界面
```

### 方式二：命令行

```bash
python tailocal.py 你的文件.xlsx
```

### 方式三：打包成免安裝軟體（推薦給非技術用戶）

```bash
# Windows：雙擊 build_exe.bat，或命令行：
pip install pyinstaller
pyinstaller --onefile --noconsole --name TaiLocal tailocal.py
# → dist/TaiLocal.exe 雙擊即用

# macOS：
pyinstaller --onefile --windowed --name TaiLocal tailocal.py
# → dist/TaiLocal
```

## 📖 Excel 格式 / Input Format

任意的 `.xlsx`，自動檢測列名：

| 中文（或任何簡中列） | en-US_lang（英文列，可選，用於語義鎖定） |
|---|---|
| 卸载应用程序 | Uninstall the app |

英文列不是必須，但**強烈建議提供** —— 「卸载」在 unmount/uninstall/remove 語境下譯法完全不同。

## 📚 更新術語庫 / Update the terminology database

### 方法 A：直接編輯 `terms.csv`

用任何表格軟體打開，兩列格式（UTF-8）：

```
source,target
内存,記憶體
软件,軟體
```

加一行就生效，重啟軟體即可。

### 方法 B：從 Excel 術語總表重建

維護一份 `術語表.xlsx`（A列=簡體，B列=台繁），然後：

```bash
python build_terms.py
```

自動去重、去空行，重新生成 `terms.csv`。

### 個人術語（不影響別人）

建一個 `terms_private.csv`（同樣格式），會自動疊加到公共術語之上。此檔案已被 `.gitignore` 排除，**不會被提交到倉庫** —— 公司/產品专属術語放這裡。

## 🏗️ 轉換流水線 / Pipeline

```
原文 → 引號正規化「」
     → 英文語義鎖定（uninstall/unmount/remove/argument/project…）
     → 術語表替換（長詞優先，佔位符保護）
     → OpenCC s2twp
     → post_fix.csv 二次修正
     → 還原 HTML 標籤與佔位符
     → 輸出 *_tw_*.xlsx + 審計 log
```

## 📄 License

MIT · 歡迎 Star / Fork / PR
