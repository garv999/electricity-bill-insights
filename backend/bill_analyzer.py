import openai
import json
from datetime import datetime
import re

class ElectricityBillAnalyzer:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.analysis_prompt = """
        You are an expert electricity bill analyzer. Analyze the following electricity bill data and provide comprehensive insights:

        BILL DATA:
        {bill_text}

        Please provide analysis in the following JSON format:
        {{
            "bill_summary": {{
                "billing_period": "extracted period",
                "total_amount": "extracted amount",
                "units_consumed": "extracted units",
                "rate_per_unit": "calculated rate"
            }},
            "consumption_analysis": {{
                "consumption_trend": "analysis of usage pattern",
                "peak_usage_period": "when highest consumption occurred",
                "efficiency_rating": "poor/average/good/excellent"
            }},
            "cost_insights": {{
                "cost_breakdown": "breakdown of charges",
                "hidden_charges": "any additional fees identified",
                "savings_potential": "estimated savings possible"
            }},
            "recommendations": [
                "specific actionable recommendation 1",
                "specific actionable recommendation 2",
                "specific actionable recommendation 3"
            ],
            "anomalies": [
                "any unusual patterns or charges identified"
            ],
            "comparison_metrics": {{
                "average_household_comparison": "how this compares to average",
                "seasonal_factors": "seasonal considerations"
            }},
            "action_items": [
                "immediate actions to take",
                "long-term improvements"
            ]
        }}
        
        Make the analysis detailed, actionable, and easy to understand for homeowners.
        """
    
    def analyze_bill(self, bill_text):
        """Analyze electricity bill using OpenAI GPT-4"""
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert electricity bill analyzer providing detailed insights."
                    },
                    {
                        "role": "user",
                        "content": self.analysis_prompt.format(bill_text=bill_text)
                    }
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            analysis_text = response.choices[0].message.content

            if "It seems like your message was empty" in analysis_text:
                return {
                    "error": "OpenAI did not return valid insights.",
                    "raw_analysis": analysis_text,
                    "analysis_date": datetime.now().isoformat()
                }
            
            try:
                json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
                if json_match:
                    analysis_json = json.loads(json_match.group())
                else:
                    analysis_json = self.parse_text_to_json(analysis_text)
            except json.JSONDecodeError:
                analysis_json = self.parse_text_to_json(analysis_text)
            
            analysis_json['analysis_date'] = datetime.now().isoformat()
            analysis_json['raw_analysis'] = analysis_text
            
            return analysis_json
            
        except Exception as e:
            return {
                'error': str(e),
                'analysis_date': datetime.now().isoformat()
            }
    
    def parse_text_to_json(self, text):
        """Fallback method to structure text analysis"""
        return {
            'bill_summary': {
                'analysis_text': text[:500] + '...' if len(text) > 500 else text
            },
            'recommendations': [
                'Review the detailed analysis provided',
                'Contact utility company for clarification if needed'
            ],
            'analysis_date': datetime.now().isoformat()
        }
    
    def format_for_dashboard(self, analysis):
        """Format analysis for dashboard display"""
        if 'error' in analysis:
            return {
                'status': 'error',
                'message': analysis['error'],
                'timestamp': analysis['analysis_date']
            }
        
        formatted = {
            'status': 'success',
            'timestamp': analysis['analysis_date'],
            'summary': {
                'total_amount': analysis.get('bill_summary', {}).get('total_amount', 'N/A'),
                'units_consumed': analysis.get('bill_summary', {}).get('units_consumed', 'N/A'),
                'efficiency_rating': analysis.get('consumption_analysis', {}).get('efficiency_rating', 'N/A')
            },
            'key_insights': analysis.get('recommendations', [])[:3],
            'anomalies': analysis.get('anomalies', []),
            'action_items': analysis.get('action_items', [])
        }
        
        return formatted

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/analyze-bill', methods=['POST'])
def analyze_bill_api():
    try:
        data = request.json
        bill_text = data.get('bill_text')
        openai_api_key = data.get('openai_api_key')
        
        if not bill_text or not openai_api_key:
            return jsonify({'error': 'bill_text and openai_api_key are required'}), 400
        
        analyzer = ElectricityBillAnalyzer(openai_api_key)
        analysis = analyzer.analyze_bill(bill_text)
        formatted_analysis = analyzer.format_for_dashboard(analysis)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'formatted_analysis': formatted_analysis
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)