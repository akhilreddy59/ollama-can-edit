## 🤖 Ollama Setup & Recommended Models

Before running `local-dev`, make sure Ollama is installed and running on your machine:
* Download it for free from [ollama.com](https://ollama.com)
* Start the Ollama application.

Our tool will automatically look at your computer and use whatever active model you have downloaded. For the best code-editing results, we recommend downloading one of these models depending on your computer's power:

### ⚡ Recommended Coding Models

| Machine Setup | Recommended Model | Command to Download | Description |
| :--- | :--- | :--- | :--- |
| **Mac M1/M2/M3 (Base), Thin Laptops, 8GB-16GB RAM** | `qwen2.5-coder:7b` | `ollama run qwen2.5-coder:7b` | **Highly Recommended.** Insanely fast, uses very little RAM, and punches way above its weight for code edits. |
| **Gaming PCs, Mac Studio, 32GB+ RAM** | `qwen2.5-coder:14b` or `32b` | `ollama run qwen2.5-coder:32b` | Incredible reasoning power. Understands complex, multi-file code structures deeply. |
| **Meta Open-Source Fans** | `codellama:7b` | `ollama run codellama:7b` | Meta's classic, stable model highly optimized strictly for software engineering tasks. |
| **Ultra-Lightweight / Weak Laptops** | `qwen2.5-coder:1.5b` | `ollama run qwen2.5-coder:1.5b` | Runs smoothly on almost any potato laptop. Good for small, simple file changes. |

> 💡 **Tip:** If you have multiple models installed, the tool will automatically default to `qwen2.5-coder:7b` if it finds it. Otherwise, it will fallback safely to any model you currently have active in your system!

# ⚡ ollama local file editor

A privacy-first, zero-dependency, open-source AI developer engine that sits directly on top of your local **Ollama** workspace instances. It maps out your workspace file trees, dynamically discovers files to edit based on your natural language inputs, and automatically modifies them for you with built-in git diff safety confirmation checks.

## 🚀 One-Command Execution

You can run this application instantly inside any development project workspace without downloading or installing any local files manually by typing this single command:

```bash
curl -sSL https://githubusercontent.com | python3
```

*(Note: Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username once you create your repository).*

## 🛠️ Prerequisites
1. **Python 3** installed on your system path.
2. **Ollama** running locally on your computer with a code model available (e.g., `qwen2.5-coder:7b` or `codellama`).

## 📦 How to Test it Manually
If running locally from this source directory directly:
```bash
pip install -r requirements.txt
python3 local_dev.py
```
