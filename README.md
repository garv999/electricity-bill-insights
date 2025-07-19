# ⚡ Electricity Bill Insights Automation 

This project automates the end-to-end workflow of extracting, analyzing, and logging insights from electricity bills (PDFs, images, or Excel files). It utilizes **n8n**, **OpenAI**, and **ERPNext** for intelligent parsing, structured insight generation, and seamless integration into business systems.

---

## 🚀 Features

- Upload electricity bills in **PDF**, **Image**, or **Excel** format
- Extract raw text using **PDF.co**
- Generate detailed insights using **OpenAI (via OpenRouter API)**
- Automatically create:
  - ✅ Communication entries in **ERPNext**
  - 📌 Actionable ToDo items
- Scalable and fully automated workflow using **n8n**

---

## 🛠️ Tech Stack

| Tool / Service     | Purpose                                      |
|--------------------|----------------------------------------------|
| `n8n`              | Workflow Automation                          |
| `Flask`            | Backend APIs for analysis and trigger        |
| `PDF.co`           | File extraction (PDF/Image/Excel to text)    |
| `OpenRouter`       | Access to GPT-4 model for text insights      |
| `ERPNext API`      | Posting insights and tasks into ERP          |
| `Ngrok`            | Expose local Flask server to n8n             |

---

## 📁 Project Structure

```text
ELECTRICITY_INSIGHT_PROJECT/
├── backend/
│ ├── bill_analyzer.py # Insight generation logic
│ ├── trigger_webhook.py # Script to trigger n8n webhook
│ ├── database_manager.py # (Optional) Bill metadata storage
│ └── erpnext_integration.py # ERPNext Communication + ToDo API
```


---

## 🌐 n8n Workflow Overview

```plaintext
Webhook
   ↓
PDF.co (Extract URL)
   ↓
PDF.co (Extract Text)
   ↓
OpenRouter GPT-4 (Generate Insights)
   ↓
ERPNext (POST Communication & ToDos)
```

## ▶️ How to Run Locally

### 1. Clone this repo:
```bash
git clone https://github.com/yourusername/electricity-insight-project.git
cd electricity-insight-project/backend
```
### 2. Install requirements:
```bash
pip install -r requirements.txt
```
### 3. Start Flask backend:
```bash
python trigger_webhook.py
```
### 4. Expose local server:
```bash
ngrok http 5000
```
### 5. Connect the ngrok URL to your n8n webhook

## 🔒 Environment Variables

Create a `.env` file in the `backend/` directory with the following content:

```env
ERP_URL=https://your.erpnext.instance
ERP_API_KEY=your_key
ERP_API_SECRET=your_secret
OPENROUTER_API_KEY=your_openrouter_key
```
## 🤝 Contributing

Pull requests and suggestions are welcome!
For major changes, please open an issue first to discuss what you would like to change.

---

*Let me know if you'd like to:*
- 📸 Embed images or diagrams
- ⭐ Add GitHub badges (stars, forks, license)
- 🎥 Link to a demo video or walkthrough


