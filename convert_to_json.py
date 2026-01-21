"""
Convert Excel data to JSON format for GitHub Pages
"""
import pandas as pd
import json
from datetime import datetime

def convert_excel_to_json():
    try:
        # Read the Excel file
        df = pd.read_excel('shs_essays_complete.xlsx', sheet_name='全部資料')
        
        # Clean and prepare data
        df = df.fillna('')  # Replace NaN with empty strings
        
        # Convert to list of dictionaries
        essays = df.to_dict('records')
        
        # Add some metadata
        data = {
            'metadata': {
                'total_essays': len(essays),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'categories': df['category'].value_counts().to_dict(),
                'periods_covered': len(df['competition_period'].unique())
            },
            'essays': essays
        }
        
        # Save as JSON
        with open('essays_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"Converted {len(essays)} essays to JSON format")
        print(f"Saved as: essays_data.json")
        
        return data
        
    except Exception as e:
        print(f"Error converting to JSON: {e}")
        return None

if __name__ == "__main__":
    convert_excel_to_json()