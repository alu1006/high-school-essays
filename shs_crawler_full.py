"""
SHS Full Crawler - 完整版台灣高中小論文競賽爬蟲
爬取所有競賽期數的特優作品資料
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import logging
import json
from datetime import datetime
import os
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('crawler.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)


class SHSCrawlerFull:
    """完整版高中小論文爬蟲"""
    
    def __init__(self, headless: bool = True, max_retries: int = 3):
        """
        初始化爬蟲
        
        Args:
            headless: 是否使用無頭模式運行瀏覽器
            max_retries: 最大重試次數
        """
        self.base_url = "https://www.shs.edu.tw/Customer/Winning/EssayIndex"
        self.headless = headless
        self.max_retries = max_retries
        self.checkpoint_file = "crawler_checkpoint.json"
        
    def load_checkpoint(self) -> dict:
        """載入斷點續爬的進度"""
        if os.path.exists(self.checkpoint_file):
            try:
                with open(self.checkpoint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"無法載入進度檔: {e}")
        return {'completed': [], 'essays': []}
    
    def save_checkpoint(self, checkpoint: dict):
        """儲存爬蟲進度"""
        try:
            with open(self.checkpoint_file, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            logger.info(f"進度已儲存: {len(checkpoint['completed'])} 個組合完成")
        except Exception as e:
            logger.error(f"儲存進度失敗: {e}")
    
    async def get_all_periods(self, page) -> list:
        """獲取所有競賽期數"""
        periods = await page.evaluate('''
            () => {
                const select = document.querySelector('#contest-no');
                return Array.from(select.options)
                    .filter(opt => opt.value !== '')
                    .map(opt => ({
                        value: opt.value,
                        text: opt.text.trim()
                    }));
            }
        ''')
        return periods
    
    @staticmethod
    def extract_valid_categories(options: list) -> list:
        """Return every category option that can be selected for crawling."""
        return [
            option
            for option in options
            if option.get('value') and option.get('text')
        ]
    
    async def get_target_categories(self, page) -> list:
        """獲取所有可用類別"""
        category_options = await page.evaluate('''
            () => {
                const select = document.querySelector('#cate-id');
                return Array.from(select.options)
                    .map(opt => ({
                        value: opt.value,
                        text: opt.text.trim()
                    }));
            }
        ''')
        return self.extract_valid_categories(category_options)
    
    async def search_essays(self, page, period: dict, category: dict) -> bool:
        """執行搜尋"""
        try:
            # 選擇期數
            await page.select_option('#contest-no', period['value'])
            await page.wait_for_timeout(500)
            
            # 選擇類別
            await page.select_option('#cate-id', category['value'])
            await page.wait_for_timeout(500)
            
            # 選擇特優
            await page.select_option('#ranking', '1')
            await page.wait_for_timeout(500)
            
            # 點擊搜尋按鈕
            submit_btn = await page.wait_for_selector('#btnSearch', timeout=10000)
            await submit_btn.click()
            await page.wait_for_load_state('networkidle', timeout=30000)
            await page.wait_for_timeout(2000)
            
            return True
            
        except Exception as e:
            logger.warning(f"搜尋失敗 {period['text']}-{category['text']}: {e}")
            return False
    
    async def extract_essays(self, page, period: dict, category: dict) -> list:
        """從頁面提取論文資料"""
        essays = await page.evaluate('''
            () => {
                const essays = [];
                const rows = document.querySelectorAll('table tbody tr');
                
                rows.forEach((row) => {
                    const cells = row.querySelectorAll('td');
                    if (cells.length >= 4) {
                        // 提取 PDF 連結的 ID 和 Key
                        const viewBtn = row.querySelector('button.btn-info, a[onclick*="ShowWorkEssay"]');
                        let essayId = '';
                        let key = '';
                        let pdfLink = '';
                        
                        if (viewBtn) {
                            const onclick = viewBtn.getAttribute('onclick') || '';
                            const match = onclick.match(/ShowWorkEssay\\('(\\d+)',\\s*'([^']+)'\\)/);
                            if (match) {
                                essayId = match[1];
                                key = match[2];
                                pdfLink = `https://www.shs.edu.tw/Customer/Winning/ShowWorkEssay?id=${essayId}&key=${key}`;
                            }
                        }
                        
                        essays.push({
                            id: essayId,
                            region: cells[1]?.textContent?.trim() || '',
                            district: cells[2]?.textContent?.trim() || '',
                            school: cells[3]?.textContent?.trim() || '',
                            department: cells[4]?.textContent?.trim() || '',
                            grade: cells[5]?.textContent?.trim() || '',
                            class_name: cells[6]?.textContent?.trim() || '',
                            author: cells[7]?.textContent?.trim() || '',
                            supervisor: cells[8]?.textContent?.trim() || '',
                            title: cells[9]?.textContent?.trim() || '',
                            ranking: cells[10]?.textContent?.trim() || '特優',
                            pdf_link: pdfLink
                        });
                    }
                });
                
                return essays;
            }
        ''')
        
        # 添加元資料
        for essay in essays:
            essay['competition_period'] = period['text']
            essay['category'] = category['text']
        
        return essays
    
    async def crawl_with_retry(self, page, period: dict, category: dict, retries: int = 0) -> list:
        """帶重試機制的爬取"""
        try:
            success = await self.search_essays(page, period, category)
            if not success:
                raise Exception("搜尋失敗")
            
            essays = await self.extract_essays(page, period, category)
            return essays
            
        except Exception as e:
            if retries < self.max_retries:
                logger.warning(f"重試 {retries + 1}/{self.max_retries}: {period['text']}-{category['text']}")
                await page.wait_for_timeout(2000)
                return await self.crawl_with_retry(page, period, category, retries + 1)
            else:
                logger.error(f"達到最大重試次數: {period['text']}-{category['text']}: {e}")
                return []
    
    async def run_full_crawl(self, resume: bool = True):
        """
        執行完整爬取
        
        Args:
            resume: 是否從上次進度繼續
        """
        # 載入進度
        checkpoint = self.load_checkpoint() if resume else {'completed': [], 'essays': []}
        all_essays = checkpoint.get('essays', [])
        completed_combinations = set(checkpoint.get('completed', []))
        
        logger.info(f"開始爬取，已完成 {len(completed_combinations)} 個組合，已收集 {len(all_essays)} 篇文章")
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                page.set_default_timeout(60000)
                
                # 訪問主頁
                await page.goto(self.base_url, wait_until='networkidle')
                await page.wait_for_timeout(3000)
                
                # 獲取所有期數和類別
                periods = await self.get_all_periods(page)
                categories = await self.get_target_categories(page)
                
                total_combinations = len(periods) * len(categories)
                logger.info(f"共有 {len(periods)} 個期數, {len(categories)} 個類別")
                logger.info(f"總計需處理 {total_combinations} 個組合")
                logger.info(f"期數列表: {[p['text'] for p in periods]}")
                logger.info(f"類別列表: {[c['text'] for c in categories]}")
                
                # 處理每個組合
                processed = 0
                for period in periods:
                    for category in categories:
                        combination_key = f"{period['value']}_{category['value']}"
                        
                        # 跳過已完成的組合
                        if combination_key in completed_combinations:
                            processed += 1
                            continue
                        
                        logger.info(f"處理中 [{processed + 1}/{total_combinations}]: {period['text']} - {category['text']}")
                        
                        # 爬取資料
                        essays = await self.crawl_with_retry(page, period, category)
                        
                        if essays:
                            all_essays.extend(essays)
                            logger.info(f"  找到 {len(essays)} 篇文章")
                        else:
                            logger.info(f"  此組合無資料")
                        
                        # 更新進度
                        completed_combinations.add(combination_key)
                        processed += 1
                        
                        # 每處理 5 個組合儲存一次進度
                        if processed % 5 == 0:
                            self.save_checkpoint({
                                'completed': list(completed_combinations),
                                'essays': all_essays
                            })
                        
                        # 延遲避免過於頻繁
                        await page.wait_for_timeout(1000)
                
                await browser.close()
        
        except Exception as e:
            logger.error(f"爬取過程發生錯誤: {e}")
            # 儲存進度
            self.save_checkpoint({
                'completed': list(completed_combinations),
                'essays': all_essays
            })
            raise
        
        # 最終儲存
        self.save_checkpoint({
            'completed': list(completed_combinations),
            'essays': all_essays
        })
        
        return all_essays
    
    def save_to_excel(self, essays: list, filename: str = "shs_essays_complete.xlsx"):
        """
        儲存資料到 Excel
        
        Args:
            essays: 論文資料列表
            filename: 輸出檔名
        """
        if not essays:
            logger.warning("沒有資料可儲存")
            return None
        
        df = pd.DataFrame(essays)
        
        # 重新排列欄位順序
        columns_order = [
            'competition_period', 'category', 'school', 'author', 
            'supervisor', 'title', 'grade', 'ranking', 'pdf_link', 
            'id', 'region', 'district', 'department', 'class_name'
        ]
        df = df.reindex(columns=[col for col in columns_order if col in df.columns])
        
        # 建立 Excel Writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 主要資料
            df.to_excel(writer, sheet_name='全部資料', index=False)
            
            # 按類別分類
            for category in df['category'].unique():
                cat_df = df[df['category'] == category]
                sheet_name = category[:30]  # Excel 工作表名稱限制 31 字元
                cat_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 統計資料
            summary_data = {
                '類別': df['category'].value_counts().index.tolist(),
                '數量': df['category'].value_counts().values.tolist()
            }
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='統計', index=False)
        
        logger.info(f"資料已儲存至 {filename}")
        logger.info(f"總計 {len(df)} 篇文章")
        
        return df
    
    def save_to_json(self, essays: list, filename: str = "essays_data.json"):
        """
        儲存資料到 JSON (供網站使用)
        
        Args:
            essays: 論文資料列表
            filename: 輸出檔名
        """
        if not essays:
            logger.warning("沒有資料可儲存")
            return None
        
        df = pd.DataFrame(essays)
        
        # 建立元資料
        data = {
            'metadata': {
                'total_essays': len(essays),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'categories': df['category'].value_counts().to_dict(),
                'periods_covered': len(df['competition_period'].unique())
            },
            'essays': essays
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON 資料已儲存至 {filename}")
        
        return data
    
    def cleanup_checkpoint(self):
        """清除進度檔案（爬取完成後）"""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
            logger.info("進度檔案已清除")


async def main():
    """主程式"""
    import argparse
    
    parser = argparse.ArgumentParser(description='台灣高中小論文競賽爬蟲 (完整版)')
    parser.add_argument('--headless', action='store_true', default=True,
                        help='使用無頭模式 (預設: True)')
    parser.add_argument('--no-headless', dest='headless', action='store_false',
                        help='顯示瀏覽器視窗')
    parser.add_argument('--no-resume', action='store_true',
                        help='不使用斷點續爬，從頭開始')
    parser.add_argument('--retries', type=int, default=3,
                        help='最大重試次數 (預設: 3)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("台灣高中小論文競賽爬蟲 (完整版)")
    print("=" * 60)
    print(f"無頭模式: {args.headless}")
    print(f"斷點續爬: {not args.no_resume}")
    print(f"最大重試: {args.retries}")
    print("=" * 60)
    print()
    
    # 建立爬蟲實例
    crawler = SHSCrawlerFull(
        headless=args.headless,
        max_retries=args.retries
    )
    
    try:
        # 執行爬取
        essays = await crawler.run_full_crawl(resume=not args.no_resume)
        
        if essays:
            # 儲存結果
            crawler.save_to_excel(essays)
            crawler.save_to_json(essays)
            
            # 清除進度檔
            crawler.cleanup_checkpoint()
            
            # 顯示統計
            print("\n" + "=" * 60)
            print("爬取完成！")
            print("=" * 60)
            print(f"總計文章數: {len(essays)}")
            
            df = pd.DataFrame(essays)
            print("\n按類別統計:")
            for cat, count in df['category'].value_counts().items():
                print(f"  {cat}: {count} 篇")
            
            print(f"\n涵蓋期數: {df['competition_period'].nunique()} 個")
            print("\n輸出檔案:")
            print("  - shs_essays_complete.xlsx")
            print("  - essays_data.json")
        else:
            print("未找到任何資料")
            
    except KeyboardInterrupt:
        print("\n使用者中斷，進度已儲存")
    except Exception as e:
        print(f"\n發生錯誤: {e}")
        print("進度已儲存，可使用 --resume 繼續")


if __name__ == "__main__":
    asyncio.run(main())
