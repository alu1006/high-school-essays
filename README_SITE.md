# 台灣高中小論文競賽作品集網站

## 網站功能

- **作品展示**: 展示718篇特優小論文作品
- **分類瀏覽**: 依資訊類、工程技術類、商業類分類
- **智慧搜索**: 支援標題、作者、學校、指導老師搜索
- **期數篩選**: 可依競賽期數篩選作品
- **PDF查看**: 直接連結到原始PDF文件
- **響應式設計**: 支援桌面和行動裝置

## 技術架構

- **前端**: HTML5 + Bootstrap 5 + Vanilla JavaScript  
- **資料格式**: JSON (由Excel轉換而來)
- **部署**: GitHub Pages
- **自訂域名**: high-school-essays.codinglu.tw

## 資料來源

資料來源於台灣高中學科能力競賽小論文組的特優作品，包含：

- **資訊類**: 230篇
- **工程技術類**: 238篇  
- **商業類**: 250篇
- **總計**: 718篇作品

## 網站設定

網站使用GitHub Pages自動部署，透過CNAME檔案設定自訂域名 high-school-essays.codinglu.tw

## 更新資料

1. 更新 `shs_essays_complete.xlsx`
2. 執行 `python convert_to_json.py`
3. 推送到GitHub即可自動更新網站