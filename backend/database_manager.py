import sqlite3
import json
from datetime import datetime
import pandas as pd

class BillDatabase:
    def __init__(self, db_path='electricity_bills.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_url TEXT,
                file_type TEXT,
                extracted_text TEXT,
                analysis_json TEXT,
                total_amount REAL,
                units_consumed REAL,
                billing_period TEXT,
                efficiency_rating TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bill_id INTEGER,
                insight_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                insight_type TEXT,
                insight_text TEXT,
                FOREIGN KEY (bill_id) REFERENCES bills (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                month_year TEXT,
                total_consumption REAL,
                total_cost REAL,
                average_rate REAL,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def store_bill_analysis(self, file_url, file_type, extracted_text, analysis):
        """Store bill and its analysis in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        bill_summary = analysis.get('bill_summary', {})
        consumption_analysis = analysis.get('consumption_analysis', {})
        
        cursor.execute('''
            INSERT INTO bills (file_url, file_type, extracted_text, analysis_json, 
                             total_amount, units_consumed, billing_period, efficiency_rating)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_url,
            file_type,
            extracted_text,
            json.dumps(analysis),
            self.extract_numeric(bill_summary.get('total_amount')),
            self.extract_numeric(bill_summary.get('units_consumed')),
            bill_summary.get('billing_period'),
            consumption_analysis.get('efficiency_rating')
        ))
        
        bill_id = cursor.lastrowid
        
        for recommendation in analysis.get('recommendations', []):
            cursor.execute('''
                INSERT INTO insights (bill_id, insight_type, insight_text)
                VALUES (?, ?, ?)
            ''', (bill_id, 'recommendation', recommendation))
        
        for anomaly in analysis.get('anomalies', []):
            cursor.execute('''
                INSERT INTO insights (bill_id, insight_type, insight_text)
                VALUES (?, ?, ?)
            ''', (bill_id, 'anomaly', anomaly))
        
        conn.commit()
        conn.close()
        
        return bill_id
    
    def extract_numeric(self, value):
        """Extract numeric value from string"""
        if not value:
            return None
        try:
            import re
            numbers = re.findall(r'[\d.]+', str(value))
            return float(numbers[0]) if numbers else None
        except:
            return None
    
    def get_monthly_trends(self, months=12):
        """Get monthly consumption trends"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT 
                strftime('%Y-%m', upload_date) as month_year,
                AVG(total_amount) as avg_cost,
                AVG(units_consumed) as avg_consumption,
                COUNT(*) as bill_count
            FROM bills 
            WHERE upload_date >= date('now', '-{} months')
            GROUP BY strftime('%Y-%m', upload_date)
            ORDER BY month_year
        '''.format(months)
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        return df.to_dict('records')
    
    def get_recent_insights(self, limit=10):
        """Get recent insights for dashboard"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT i.insight_text, i.insight_type, i.insight_date, b.total_amount, b.efficiency_rating
            FROM insights i
            JOIN bills b ON i.bill_id = b.id
            ORDER BY i.insight_date DESC
            LIMIT ?
        '''
        
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        results = cursor.fetchall()
        conn.close()
        
        return [
            {
                'insight': row[0],
                'type': row[1],
                'date': row[2],
                'bill_amount': row[3],
                'efficiency': row[4]
            }
            for row in results
        ]

from flask import Flask, request, jsonify

app = Flask(__name__)
db = BillDatabase()

@app.route('/store-analysis', methods=['POST'])
def store_analysis():
    try:
        data = request.json
        file_url = data.get('file_url')
        file_type = data.get('file_type')
        extracted_text = data.get('extracted_text')
        analysis = data.get('analysis')
        
        bill_id = db.store_bill_analysis(file_url, file_type, extracted_text, analysis)
        
        return jsonify({
            'success': True,
            'bill_id': bill_id,
            'message': 'Analysis stored successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-trends', methods=['GET'])
def get_trends():
    try:
        months = request.args.get('months', 12, type=int)
        trends = db.get_monthly_trends(months)
        return jsonify({'trends': trends})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-insights', methods=['GET'])
def get_insights():
    try:
        limit = request.args.get('limit', 10, type=int)
        insights = db.get_recent_insights(limit)
        return jsonify({'insights': insights})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)