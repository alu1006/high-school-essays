# 台灣高中職學生小論文競賽爬蟲

## 專案概述
本專案用於爬取台灣高中職學生小論文競賽的特優作品資料，專注於三個目標類別：資訊類、工程技術類、商業類。

## 核心提取欄位

### 🎯 主要欄位
1. **作者 (author)** - 學生姓名
2. **指導老師 (supervisor)** - 指導教師姓名  
3. **作品專題 (title)** - 小論文標題

### 📊 輔助欄位
- **學校 (school)** - 學校名稱
- **類別 (category)** - 競賽類別 (資訊類/工程技術類/商業類)
- **期數 (competition_period)** - 競賽期數
- **等級 (ranking)** - 獲獎等級 (特優)
- **PDF鏈接 (pdf_link)** - 完整的PDF下載連結

## 技術實現

### 網站結構
- **網站URL**: https://www.shs.edu.tw/Customer/Winning/EssayIndex
- **表單選擇器**: 
  - 期數: `#contest-no`
  - 類別: `#cate-id` (資訊類=13, 商業類=11, 工程技術類=8)
  - 等級: `#ranking` (特優=1)
- **搜尋按鈕**: `#btnSearch`
- **檢視按鈕**: `button.btn-info` (包含onclick屬性)

### PDF鏈接提取
- 從HTML onclick屬性直接提取：`ShowWorkEssay('id', 'key')`
- 使用正則表達式：`/ShowWorkEssay\\('(\\d+)',\\s*'([^']+)'\\)/`
- 生成完整URL：`https://www.shs.edu.tw/Customer/Winning/ShowWorkEssay?id={id}&key={key}`

## 使用方法

### 安裝依賴
```bash
pip install -r requirements.txt
playwright install chromium
```

### 執行測試爬蟲
```bash
python test_crawler.py
```

## 輸出格式
- **Excel檔案**: `test_results.xlsx`
- **主要工作表**: 測試資料
- **統計工作表**: 類別統計

## 資料品質
✅ 作者欄位: 100%完整  
✅ 指導老師欄位: 100%完整  
✅ 作品專題欄位: 100%完整  
✅ PDF下載鏈接: 100%功能