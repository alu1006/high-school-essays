# 台灣高中小論文競賽作品集 🎓

[![Website](https://img.shields.io/website?url=https%3A%2F%2Fhigh-school-essays.codinglu.tw)](https://high-school-essays.codinglu.tw)
[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live-brightgreen)](https://high-school-essays.codinglu.tw)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 一個完整的台灣高中學科能力競賽小論文作品爬蟲系統與線上展示平台

## 📖 專案簡介

本專案包含兩個主要部分：
1. **網路爬蟲系統** - 自動抓取台灣高中小論文競賽特優作品資料
2. **線上展示平台** - 提供搜索、篩選功能的響應式網站

### 🌐 線上展示
**網站地址**: [high-school-essays.codinglu.tw](https://high-school-essays.codinglu.tw)

## 📊 資料統計

- **總作品數**: 718篇特優作品
- **競賽類別**: 3個主要類別
  - 📊 **商業類**: 250篇
  - 🔧 **工程技術類**: 238篇  
  - 💻 **資訊類**: 230篇
- **涵蓋期數**: 25個競賽期數 (從1020331到1140315)
- **資料完整度**: 
  - 作者姓名: 100%
  - 作品標題: 100%  
  - PDF連結: 100%
  - 指導老師: 70.8%

## ✨ 主要功能

### 🕷️ 爬蟲系統特色
- **全自動化**: 支援所有26個競賽期數的完整爬取
- **動態鍵值**: 自動提取PDF檢視的動態key
- **錯誤處理**: 完整的錯誤處理與重試機制
- **資料驗證**: 自動驗證資料完整性
- **反偵測**: 模擬真實瀏覽器行為避免封鎖

### 🌐 網站功能
- **智慧搜索**: 支援作品標題、作者、學校、指導老師搜索
- **多重篩選**: 按類別、競賽期數篩選
- **響應式設計**: 完美支援桌面與行動裝置
- **PDF直連**: 每篇作品提供直接PDF下載連結
- **統計資訊**: 即時顯示資料統計與分布

## 🚀 快速開始

### 環境需求
- Python 3.8+
- Node.js (用於本地開發)
- Git

### 安裝步驟

1. **克隆專案**
   ```bash
   git clone https://github.com/alu1006/high-school-essays.git
   cd high-school-essays
   ```

2. **安裝Python依賴**
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **執行測試爬蟲**
   ```bash
   python test_crawler.py
   ```

4. **執行完整爬蟲** (預計2-3小時)
   ```bash
   python shs_crawler_full.py
   ```

5. **本地運行網站**
   ```bash
   python -m http.server 8000
   # 訪問 http://localhost:8000
   ```

## 📁 專案結構

```
├── 🕷️ 爬蟲系統
│   ├── shs_crawler_full.py      # 完整版爬蟲 (26期數)
│   ├── test_crawler.py          # 測試版爬蟲 (2期數)
│   └── requirements.txt         # Python依賴
│
├── 🌐 網站系統  
│   ├── index.html               # 主頁面
│   ├── essays_data.json         # 作品數據 (718篇)
│   ├── _config.yml              # Jekyll配置
│   └── CNAME                    # 自訂域名
│
├── 📊 資料檔案
│   ├── shs_essays_complete.xlsx # 完整Excel資料
│   └── test_results.xlsx        # 測試結果
│
└── 📝 文件
    ├── README.md                # 專案說明 (本檔案)
    ├── CLAUDE.md                # 開發指引
    └── README_SITE.md           # 網站說明
```

## 🛠️ 技術架構

### 後端爬蟲
- **語言**: Python 3.8+
- **框架**: Playwright (瀏覽器自動化)
- **資料處理**: Pandas, OpenPyXL
- **格式轉換**: JSON輸出

### 前端網站
- **框架**: 純HTML5 + CSS3 + JavaScript
- **UI**: Bootstrap 5
- **圖標**: Font Awesome 6
- **部署**: GitHub Pages
- **域名**: high-school-essays.codinglu.tw

## 📋 使用指南

### 爬蟲使用
```bash
# 快速測試 (2個期數)
python test_crawler.py

# 完整爬取 (26個期數，約2-3小時)
python shs_crawler_full.py

# 轉換資料為JSON格式
python convert_to_json.py
```

### 網站部署
1. Fork此專案到你的GitHub
2. 啟用GitHub Pages
3. 設定自訂域名 (可選)
4. 網站自動部署完成

## 🎯 主要特色

### 資料品質
- ✅ **100%完整度**: 作者、標題、PDF連結
- ✅ **高品質資料**: 僅收錄特優等級作品
- ✅ **結構化資料**: 完整的Excel和JSON格式
- ✅ **即時更新**: 支援新期數的擴充

### 技術亮點
- 🚀 **高效能爬蟲**: 平行處理與錯誤重試
- 🎨 **現代化介面**: 漸層設計與流暢動畫
- 📱 **響應式設計**: 完美支援各種裝置
- 🔍 **即時搜索**: 毫秒級搜索響應

## 📈 資料來源

**官方網站**: [台灣高中學科能力競賽](https://www.shs.edu.tw/Customer/Winning/EssayIndex)

### 競賽類別詳情
- **資訊類** (ID: 13): 計算機科學、資訊工程相關主題
- **工程技術類** (ID: 8): 工程技術、製造科技相關主題  
- **商業類** (ID: 11): 商業管理、經濟貿易相關主題

### 資料範圍
- **時間跨度**: 2013-2025年 (1020331-1140315)
- **獎項等級**: 僅收錄「特優」等級作品
- **資料欄位**: 作者、指導老師、學校、標題、PDF連結等

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

### 開發流程
1. Fork專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

### 報告問題
如果發現問題，請在[Issues](https://github.com/alu1006/high-school-essays/issues)頁面報告。

## 📄 授權條款

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 👥 貢獻者

- **主要開發**: [@alu1006](https://github.com/alu1006)
- **技術支援**: Claude Code (AI Assistant)

## 📞 聯絡資訊

- **專案主頁**: [GitHub Repository](https://github.com/alu1006/high-school-essays)
- **線上展示**: [high-school-essays.codinglu.tw](https://high-school-essays.codinglu.tw)
- **問題回報**: [GitHub Issues](https://github.com/alu1006/high-school-essays/issues)

---

<p align="center">
  <b>🎓 為台灣高中學術研究提供數位化支持 🎓</b>
</p>