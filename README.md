# 🛡️ Cybersecurity Log Analyzer using Gemma (Lightweight LLM)

A real-time cybersecurity log analysis dashboard powered by **Google's Gemma 2B**, a state-of-the-art lightweight LLM.

This tool automatically ingests security logs (such as failed logins, firewall drops, SQL injection attempts) and uses the Gemma model to summarize the event, classify the attack type, determine the risk level, and suggest actionable remediation steps—all locally and securely.

![Gemma Log Analyzer](https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/log_analyzer_placeholder.png) <!-- Update with your own screenshot -->

## 🌟 Key Features

1. **Lightweight & Local**: Runs entirely on your local machine using the `google/gemma-2b-it` model. Ensures sensitive logs never leave your network for processing.
2. **Secure Authentication**: Uses Hugging Face tokens to authenticate access to the gated Gemma repository.
2. **Streamlit Web Dashboard**: A sleek, user-friendly UI for manual analysis, bulk log processing, and real-time monitoring.
3. **Real-Time Log Monitoring**: Automatically reads incoming logs from `live_logs.txt` and performs instant threat analysis.
4. **Structured Threat Intelligence**: Extracts critical information from raw logs:
   - **Summary**: Plain English description of the event.
   - **Risk Level**: Low / Medium / High classification.
   - **Attack Type**: E.g., Brute Force, SQL Injection, DDoS.
   - **Recommended Actions**: Immediate steps to mitigate the threat.

## 🚀 Getting Started

### 1. Prerequisites
You need Python 3.11+ and an environment capable of running PyTorch. A system with at least 8GB of RAM is recommended.

### 2. Installation
Clone the repository and install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Authentication (Required)
The `google/gemma-2b-it` model is a gated repository. To use it:
1. Visit the [Gemma Model Page](https://huggingface.co/google/gemma-2b-it) and click **Acknowledge license**.
2. Create a Hugging Face token with **Read** access in your [Account Settings](https://huggingface.co/settings/tokens).
3. You will paste this token directly into the Streamlit Web UI.

### 4. Usage

**Running the Dashboard**
Start the Streamlit web application:
```bash
streamlit run app.py
```

**Real-Time Monitoring Simulation**
To test the real-time monitoring feature, open a *second terminal* and run the log generator:
```bash
python log_generator.py
```
This will start writing simulated cybersecurity events to `live_logs.txt`. Switch to the "Real-Time Monitoring" tab in the Streamlit app and check the "Auto-Refresh" box to see Gemma analyze attacks as they happen!

## 📁 Project Structure

- `app.py`: The main Streamlit web application.
- `gemma_log_analyzer.py`: Core logic for loading the Gemma model and formatting prompts.
- `log_generator.py`: A utility script that simulates live network logs.
- `requirements.txt`: Python dependencies.

## 🧠 Why Gemma?
Google's Gemma models offer exceptional reasoning capabilities in a small parameter size. By using `gemma-2b-it`, this project achieves high-quality threat analysis while remaining lightweight enough to run on standard hardware.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## 📜 License
MIT License
