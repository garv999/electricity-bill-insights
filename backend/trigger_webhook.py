import requests

webhook_url = "https://electricity-insights.app.n8n.cloud/webhook-test/electricity-bill-upload"

payload = {
    "file_url": "https://drive.google.com/file/d/1-EINJthvwPX4PAcMM0XloAOVErfDBF7n/view?usp=sharing",
    "file_type": "pdf"
}

file_url = payload["file_url"]
file_type = payload["file_type"]
if not file_url.startswith(("http://", "https://")):
    print("Invalid file URL. Must start with http or https.")
    exit()
try:
    head_response = requests.head(file_url, timeout=10)
    if head_response.status_code != 200:
        print(f"File not accessible. Status code: {head_response.status_code}")
        exit()
except Exception as e:
    print(f"Error checking file URL: {e}")
    exit()

try:
    response = requests.post(webhook_url, json=payload, timeout=15)
    print("Request sent to n8n.")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print(f"Error sending request to webhook: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
