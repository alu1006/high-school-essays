"""
Test version of SHS Crawler - processes only 2 periods for quick testing
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import logging
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSHSCrawler:
    def __init__(self):
        self.base_url = "https://www.shs.edu.tw/Customer/Winning/EssayIndex"
        self.target_category_keywords = ['資訊', '工程技術', '商業']
        
    async def run_test_crawl(self):
        """Run a limited crawl for testing"""
        all_essays = []
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                page.set_default_timeout(60000)  # Increase timeout to 60 seconds
                
                await page.goto(self.base_url, wait_until='networkidle')
                await page.wait_for_timeout(5000)
                
                # Get only first 2 periods and target categories
                periods = await page.evaluate('''
                    () => {
                        const select = document.querySelector('#contest-no');
                        return Array.from(select.options).slice(1, 3).map(opt => ({
                            value: opt.value,
                            text: opt.text.trim()
                        }));
                    }
                ''')
                
                categories = await page.evaluate('''
                    () => {
                        const select = document.querySelector('#cate-id');
                        const all = Array.from(select.options).map(opt => ({
                            value: opt.value,
                            text: opt.text.trim()
                        }));
                        
                        // Filter for target categories with correct values
                        // Based on discovered values: 資訊類=13, 商業類=11, 工程技術類=8
                        return all.filter(cat => 
                            cat.value === '13' || cat.value === '11' || cat.value === '8'
                        );
                    }
                ''')
                
                logger.info(f"Testing with {len(periods)} periods and {len(categories)} categories")
                logger.info(f"Periods: {[p['text'] for p in periods]}")
                logger.info(f"Categories: {[c['text'] for c in categories]}")
                
                # Process combinations
                for period in periods:
                    for category in categories:
                        logger.info(f"Processing: {period['text']} - {category['text']}")
                        
                        # Select options
                        await page.select_option('#contest-no', period['value'])
                        await page.wait_for_timeout(500)
                        
                        await page.select_option('#cate-id', category['value'])
                        await page.wait_for_timeout(500)
                        
                        await page.select_option('#ranking', '1')  # 特優
                        await page.wait_for_timeout(500)
                        
                        # Submit search using correct btnSearch selector
                        try:
                            submit_btn = await page.wait_for_selector('#btnSearch', timeout=10000)
                            await submit_btn.click()
                            await page.wait_for_load_state('networkidle', timeout=30000)
                            await page.wait_for_timeout(3000)
                        except Exception as e:
                            logger.warning(f"Submit error for {period['text']}-{category['text']}: {e}")
                            # Try alternative selectors
                            try:
                                submit_btn = await page.wait_for_selector('button[type="submit"], input[type="submit"]', timeout=5000)
                                await submit_btn.click()
                                await page.wait_for_load_state('networkidle', timeout=30000)
                                await page.wait_for_timeout(3000)
                            except Exception as e2:
                                logger.error(f"All submit methods failed: {e2}")
                                continue
                        
                        # Extract essay data with PDF keys from onclick attributes
                        essays = await page.evaluate('''
                            () => {
                                const essays = [];
                                const rows = document.querySelectorAll('table tbody tr');
                                
                                rows.forEach((row, index) => {
                                    const cells = row.querySelectorAll('td');
                                    if (cells.length >= 4) {
                                        // Look for view button with onclick
                                        const viewBtn = row.querySelector('button.btn-info, a[onclick*="ShowWorkEssay"]');
                                        let essayId = '';
                                        let key = '';
                                        let pdfLink = '';
                                        
                                        if (viewBtn) {
                                            const onclick = viewBtn.getAttribute('onclick') || '';
                                            // Extract ID and key from onclick: ShowWorkEssay('id', 'key')
                                            const match = onclick.match(/ShowWorkEssay\\('(\\d+)',\\s*'([^']+)'\\)/);
                                            if (match) {
                                                essayId = match[1];
                                                key = match[2];
                                                pdfLink = `https://www.shs.edu.tw/Customer/Winning/ShowWorkEssay?id=${essayId}&key=${key}`;
                                            }
                                        }
                                        
                                        essays.push({
                                            id: essayId,
                                            category: cells[0]?.textContent?.trim() || '',
                                            region: cells[1]?.textContent?.trim() || '',
                                            district: cells[2]?.textContent?.trim() || '',
                                            school: cells[3]?.textContent?.trim() || '',
                                            department: cells[4]?.textContent?.trim() || '',
                                            grade: cells[5]?.textContent?.trim() || '',
                                            class: cells[6]?.textContent?.trim() || '',
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
                        
                        # Add metadata
                        for essay in essays:
                            essay['competition_period'] = period['text']
                            essay['category'] = category['text']
                        
                        all_essays.extend(essays)
                        logger.info(f"Found {len(essays)} essays")
                        
                        await page.wait_for_timeout(1000)
                
                await browser.close()
                
        except Exception as e:
            logger.error(f"Error in test crawler: {e}")
        
        return all_essays
    
    def save_to_excel(self, essays, filename="test_results.xlsx"):
        """Save test results to Excel"""
        if not essays:
            logger.warning("No data to save")
            return
            
        df = pd.DataFrame(essays)
        
        # Reorder columns
        columns = ['competition_period', 'category', 'school', 'author', 'supervisor', 'title', 'grade', 'ranking', 'pdf_link', 'id']
        df = df.reindex(columns=[col for col in columns if col in df.columns])
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='測試資料', index=False)
            
            # Add summary
            if 'category' in df.columns:
                summary = df['category'].value_counts().reset_index()
                summary.columns = ['類別', '數量']
                summary.to_excel(writer, sheet_name='統計', index=False)
        
        logger.info(f"Test results saved to {filename}")
        logger.info(f"Total essays: {len(df)}")
        
        return df

async def main():
    crawler = TestSHSCrawler()
    essays = await crawler.run_test_crawl()
    
    if essays:
        df = crawler.save_to_excel(essays)
        print("\n=== Test Results Summary ===")
        print(f"Total essays found: {len(essays)}")
        if 'category' in df.columns:
            print("\nBy category:")
            for cat, count in df['category'].value_counts().items():
                print(f"  {cat}: {count}")
    else:
        print("No essays found in test run")

if __name__ == "__main__":
    asyncio.run(main())