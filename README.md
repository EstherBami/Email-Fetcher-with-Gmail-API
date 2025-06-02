# 📬 Email Fetcher

## 🚀 Project Overview

This script authenticates with the Gmail API, fetches the latest emails from your inbox, groups them by thread, cleans the body content, and structures the output into a JSON format.

### 🎯 Use Cases
- Building email summarizers
- Training ML models on email content
- Archiving email threads for analysis
- Enhancing chatbots with real inbox data

---

## ⚙️ Features

- OAuth2 Gmail Authentication  
- Grouping Emails by Thread  
- HTML & Text Parsing  
- Cleaning Noise/Footers/Links  
- JSON Export for Summarization or DB Storage  

---

## 🛠️ Technologies Used

- Python 3.x  
- Gmail API (`google-api-python-client`)  
- BeautifulSoup  
- Standard libraries: `base64`, `re`, `datetime`

---

## 📥 Sample Output

See `samples/sample_output.json` for example email threads with metadata and cleaned body content.

---

## 💡 Future Work

- Add MongoDB integration for persistent storage  
- Build summarization pipeline using LangChain / HuggingFace  
- Create a Streamlit frontend for browsing or summarizing threads  

---

## 🧪 Setup & Usage

```bash
# Clone the repository
git clone https://github.com/yourusername/email-fetcher.git
cd email-fetcher

# Install dependencies
pip install -r requirements.txt

# Place your Gmail credentials in:
`config/email_credentials.json`

# Then run the fetcher:
`python fetcher.py`


