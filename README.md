
# 📧 Multimodal Email Productivity Agent

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-FF4B4B.svg)
![LangGraph](https://img.shields.io/badge/LangGraph-Agentic-orange.svg)
![Gemini](https://img.shields.io/badge/AI-Gemini%202.5-8E44AD.svg)

**Transform your inbox into an intelligent, actionable dashboard.**

This application is a powerful **AI-driven email assistant** that uses Google's **Gemini 2.5 Flash** and **LangGraph** to process, categorize, and interact with your emails. It supports **multimodal input**, meaning it can "see" images attached to your emails (like receipts or screenshots) to make smarter decisions.

---

## ✨ Key Features

### 🧠 Intelligent Agent Brain
*   **Batch Processing**: Processes emails in parallel batches for high efficiency.
*   **Multimodal Understanding**: Analyzes both text and images to categorize emails accurately.
*   **Customizable Prompts**: You control the AI! Edit instructions for categorization, extraction, and drafting directly from the UI.

### 📥 Smart Inbox
*   **Auto-Categorization**: Sorts emails into *Work, Personal, Spam, or Newsletter*.
*   **Action Item Extraction**: Automatically pulls out tasks, deadlines, and meetings.
*   **Draft Generation**: Pre-writes professional replies for you to review and send.
*   **Visual Dashboard**: A beautiful, dark-mode UI built with Streamlit.

### 🤖 Interactive Chat
*   **Chat with Your Inbox**: Ask questions like *"What tasks do I have due this week?"* or *"Summarize the newsletter from TechWeekly."*
*   **Context-Aware**: The chat agent understands the specific context of selected emails.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   A Google Cloud Project with **Gemini API** access.
*   (Optional) Gmail OAuth credentials for real inbox access.

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/yourusername/email-agent.git
    cd email-agent
    ```

2.  **Create a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up Environment**
    *   You can enter your `GOOGLE_API_KEY` directly in the UI sidebar.
    *   For Gmail integration, place your `client_secret.json` in the root directory.

### Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## 🛠️ Tech Stack

*   **Frontend**: [Streamlit](https://streamlit.io/) - For a fast, interactive, and beautiful UI.
*   **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) - For building stateful, multi-actor agent workflows.
*   **LLM**: [Google Gemini](https://deepmind.google/technologies/gemini/) - For multimodal reasoning and generation.
*   **Database**: SQLite - For local, lightweight data persistence.
*   **Email**: `imap-tools` & Google OAuth - For secure inbox access.

---

## 📂 Project Structure

```
email_agent/
├── app.py              # Main Streamlit application entry point
├── src/
│   ├── graph.py        # LangGraph agent definition (Batch Processor)
│   ├── processor.py    # Batch processing logic
│   ├── ingestion.py    # Email fetching (Mock & IMAP)
│   ├── db_utils.py     # Database operations
│   └── styles.py       # Custom CSS for the UI
├── data/
│   ├── mock_inbox.json # Sample data for testing
│   └── email_agent.db  # Local database (ignored in git)
└── requirements.txt    # Project dependencies
```

---

## 🛡️ Privacy & Security

*   **Local Processing**: Emails are stored locally in your SQLite database.
*   **Secure Auth**: Uses official Google OAuth flows for Gmail access.
*   **No Data Training**: Your email data is not used to train the public models.

---

Made with ❤️ by [Your Name]
