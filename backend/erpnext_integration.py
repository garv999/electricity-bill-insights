import requests
import json
from datetime import datetime

class ERPNextIntegration:
    def __init__(self, erpnext_url, api_key, api_secret):
        self.base_url = erpnext_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.headers = {
            'Authorization': f'token {api_key}:{api_secret}',
            'Content-Type': 'application/json'
        }

    def create_communication(self, subject, content, reference_doctype=None, reference_name=None):
        data = {
            'doctype': 'Communication',
            'subject': subject,
            'content': content,
            'communication_type': 'Comment',
            'sent_or_received': 'Sent',
            'status': 'Open'
        }
        if reference_doctype and reference_name:
            data['reference_doctype'] = reference_doctype
            data['reference_name'] = reference_name

        try:
            response = requests.post(f'{self.base_url}/api/resource/Communication', headers=self.headers, json=data)
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_todo(self, description, priority='Medium', reference_type=None, reference_name=None):
        data = {
            'doctype': 'ToDo',
            'description': description,
            'priority': priority,
            'status': 'Open'
        }
        if reference_type and reference_name:
            data['reference_type'] = reference_type
            data['reference_name'] = reference_name

        try:
            response = requests.post(f'{self.base_url}/api/resource/ToDo', headers=self.headers, json=data)
            if response.status_code == 200:
                return {'success': True, 'data': response.json()}
            else:
                return {'success': False, 'error': response.text}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_bill_insight(self, bill_id, analysis, communication_name=None):
        print(f"[INFO] Called create_bill_insight for bill_id: {bill_id}")
        try:
            insight_payload = {
                "linked_upload": bill_id,
                "billing_period": analysis.get("bill_summary", {}).get("billing_period", ""),
                "total_amount": float(analysis.get("bill_summary", {}).get("total_amount", "0").replace("₹", "").strip()),
                "units_consumed": analysis.get("bill_summary", {}).get("units_consumed", ""),
                "rate_per_unit": analysis.get("bill_summary", {}).get("rate_per_unit", ""),
                "efficiency_rating": analysis.get("consumption_analysis", {}).get("efficiency_rating", ""),
                "consumption_trend": analysis.get("consumption_analysis", {}).get("consumption_trend", ""),
                "peak_usage_period": analysis.get("consumption_analysis", {}).get("peak_usage_period", ""),
                "anomalies": "\n".join(analysis.get("anomalies", [])),
                "recommendations": "\n".join(analysis.get("recommendations", [])),
                "analysis_date": analysis.get("analysis_date", datetime.now().strftime('%Y-%m-%d %H:%M')),
                "communication_reference": communication_name
            }

            print(f"[DEBUG] Payload to Electricity Bill Insight:\n{json.dumps(insight_payload, indent=2)}")

            create_response = requests.post(
                f'{self.base_url}/api/resource/Electricity Bill Insight',
                headers=self.headers,
                json=insight_payload
            )

            print(f"[DEBUG] ERPNext responded with {create_response.status_code}:\n{create_response.text}")

            if create_response.status_code == 200:
                return {'success': True, 'data': create_response.json(), 'created': True}
            else:
                return {'success': False, 'error': create_response.text, 'created': False}

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post_electricity_bill_insights(self, analysis, bill_id):
        try:
            subject = f"🔌 Electricity Bill Analysis - Bill #{bill_id}"
            content = self.format_analysis_for_erpnext(analysis)
            comm_result = self.create_communication(subject, content)

            comm_name = comm_result['data']['data']['name'] if comm_result.get('success') else None

            todo_results = []
            for recommendation in analysis.get('recommendations', [])[:3]:
                todo_result = self.create_todo(
                    description=f"⚡ [Bill #{bill_id}] {recommendation}",
                    priority='High',
                    reference_type='Communication',
                    reference_name=comm_name
                )
                todo_results.append(todo_result)

            insight_result = self.create_bill_insight(bill_id, analysis, communication_name=comm_name)

            return {
                'success': True,
                'communication': comm_result,
                'todos': todo_results,
                'insight': insight_result
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def post_raw_text_insight(self, raw_text, bill_id):
        try:
            subject = f"🔌 Electricity Bill Summary - Bill #{bill_id}"
            content = f"<div style='font-family: monospace; white-space: pre-wrap;'>{raw_text}</div>"
            return self.create_communication(subject, content)
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def format_analysis_for_erpnext(self, analysis):
        content = f"""
<div style="font-family: Arial, sans-serif;">
<h3>🔌 Electricity Bill Analysis Report</h3>
<p><strong>Analysis Date:</strong> {analysis.get('analysis_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}</p>
<h4>📊 Bill Summary</h4>
<ul>
<li><strong>Billing Period:</strong> {analysis.get('bill_summary', {}).get('billing_period', 'N/A')}</li>
<li><strong>Total Amount:</strong> {analysis.get('bill_summary', {}).get('total_amount', 'N/A')}</li>
<li><strong>Units Consumed:</strong> {analysis.get('bill_summary', {}).get('units_consumed', 'N/A')}</li>
<li><strong>Rate per Unit:</strong> {analysis.get('bill_summary', {}).get('rate_per_unit', 'N/A')}</li>
</ul>
<h4>📈 Consumption Analysis</h4>
<ul>
<li><strong>Efficiency Rating:</strong> {analysis.get('consumption_analysis', {}).get('efficiency_rating', 'N/A')}</li>
<li><strong>Consumption Trend:</strong> {analysis.get('consumption_analysis', {}).get('consumption_trend', 'N/A')}</li>
<li><strong>Peak Usage Period:</strong> {analysis.get('consumption_analysis', {}).get('peak_usage_period', 'N/A')}</li>
</ul>
<h4>💡 Key Recommendations</h4>
<ol>"""
        for rec in analysis.get('recommendations', []):
            content += f"<li>{rec}</li>"
        content += "</ol>"

        if analysis.get('anomalies'):
            content += "<h4>⚠️ Anomalies Detected</h4><ul>"
            for anomaly in analysis.get('anomalies', []):
                content += f"<li>{anomaly}</li>"
            content += "</ul>"

        content += "</div>"
        return content


from flask import Flask, request, jsonify
import json
import re
from erpnext_integration import ERPNextIntegration

app = Flask(__name__)

@app.route('/post-to-erpnext', methods=['POST'])
def post_to_erpnext():
    try:
        data = request.json
        erpnext_url = data.get('erpnext_url')
        api_key = data.get('api_key')
        api_secret = data.get('api_secret')
        analysis = data.get('analysis')
        raw_insight_text = data.get('raw_insight_text')
        bill_id = data.get('bill_id')

        if not all([erpnext_url, api_key, api_secret, bill_id]):
            return jsonify({'error': 'Missing required parameters'}), 400

        erp = ERPNextIntegration(erpnext_url, api_key, api_secret)

        if not analysis and raw_insight_text:
            json_str = None

            match = re.search(r"```json\s*(.*?)```", raw_insight_text, re.DOTALL)
            if match:
                json_str = match.group(1)

            elif '<div' in raw_insight_text:
                match = re.search(r"<div[^>]*>(.*?)</div>", raw_insight_text, re.DOTALL)
                if match:
                    json_str = match.group(1)

            if json_str:
                try:
                    analysis = json.loads(json_str)
                except Exception as parse_err:
                    return jsonify({'error': f'Failed to parse JSON: {parse_err}'}), 400

        if analysis:
            result = erp.post_electricity_bill_insights(analysis, bill_id)
        elif raw_insight_text:
            result = erp.post_raw_text_insight(raw_insight_text, bill_id)
        else:
            return jsonify({'error': 'Either "analysis" or "raw_insight_text" must be provided.'}), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)































# app = Flask(__name__)

# @app.route('/post-to-erpnext', methods=['POST'])
# def post_to_erpnext():
#     try:
#         data = request.json
#         erpnext_url = data.get('erpnext_url')
#         api_key = data.get('api_key')
#         api_secret = data.get('api_secret')
#         analysis = data.get('analysis')
#         raw_insight_text = data.get('raw_insight_text')
#         bill_id = data.get('bill_id')

#         if not all([erpnext_url, api_key, api_secret, bill_id]):
#             return jsonify({'error': 'Missing required parameters'}), 400

#         erp = ERPNextIntegration(erpnext_url, api_key, api_secret)

#         if analysis:
#             result = erp.post_electricity_bill_insights(analysis, bill_id)
#         elif raw_insight_text:
#             result = erp.post_raw_text_insight(raw_insight_text, bill_id)
#         else:
#             return jsonify({'error': 'Either "analysis" or "raw_insight_text" must be provided.'}), 400

#         return jsonify(result)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500