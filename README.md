---
title: AI Debate Arena
emoji: 🎭
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.0.0
app_file: app.py
pinned: false
---

# 🎭 AI Debate Arena

Watch two AI agents debate any topic using **Reflection Patterns** - they critique and improve their own arguments over 3 rounds!

## 🎯 What Makes This Different?

This implements the **Reflection Pattern** from Andrew Ng's Agentic AI Course:

1. **🥊 Round 1:** Agents make initial arguments
2. **🔍 Reflection:** Agents critique their own logic, biases, and manipulation tactics
3. **📈 Round 2:** Agents improve arguments based on self-critique
4. **🔍 Reflection:** Second round of self-analysis
5. **🎯 Round 3:** Final polished arguments
6. **⚖️ Verdict:** Judge analyzes the debate

---

## 🚀 How to Use (Hugging Face)

**You need an API key:**
- Get free credits at [console.anthropic.com](https://console.anthropic.com) ($5 free)
- Or use [platform.openai.com](https://platform.openai.com) for GPT models

**Then:**
1. Enter your debate topic
2. Configure Agent Pro and Agent Con (model & API key)
3. Watch them debate and improve in real-time!

---

## 💻 Running Locally

### Prerequisites
- Python 3.12+ (recommended)
- pip (Python package manager)

### Step 1: Clone the Repository
```bash
git clone https://github.com/raghulmukundan/ai-debate-arena.git
cd ai-debate-arena
```

### Step 2: Create Virtual Environment

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Set Up API Keys

**Create a `.env` file** in the project root:
```bash
# On Windows
type nul > .env

# On Mac/Linux
touch .env
```

**Edit `.env` and add your API keys:**
```env
# Anthropic API Key (for Claude models)
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxx

# OpenAI API Key (for GPT models) - Optional
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

⚠️ **Important:** The `.env` file is gitignored to keep your keys private!

### Step 5: Run the Application
```bash
python app.py
```

**Open your browser to:** `http://localhost:7860`

### Troubleshooting

**"ModuleNotFoundError"**
- Make sure venv is activated: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- Run: `pip install -r requirements.txt`

**"Invalid API key"**
- Check `.env` file has correct keys
- Anthropic keys start with `sk-ant-`
- OpenAI keys start with `sk-`

**"Port already in use"**
- Change port in `app.py`: `interface.launch(server_port=7861)`

---

## 🎨 Features

- **Multi-Model Support:** Claude vs Claude, Claude vs GPT, or any combination
- **Real-time Streaming:** Watch arguments develop live
- **Split Screen:** Easy side-by-side comparison
- **Full Reflections:** See complete self-critiques (not sanitized!)
- **Verdict Analysis:** AI judge evaluates argument quality

## 🧠 Interesting Discoveries

- AI catches itself making up statistics
- Arguments evolve from emotional to analytical
- By Round 3, agents often ask questions instead of arguing
- Different models show different reasoning styles
- Claude works better for debates; GPT sometimes goes neutral

## 💰 Cost Estimates

**Per Debate (3 rounds):**
- Claude Sonnet 4.5: ~$0.02-0.03
- GPT-4o: ~$0.015-0.025
- Claude Haiku: ~$0.005-0.01 (budget option)

**With Free Credits:**
- $5 gets you 200-250 debates!

## 💻 Tech Stack

- **Framework:** Gradio 4.0+
- **Models:** Claude Sonnet 4.5, Claude Opus 4, GPT-4o, GPT-4-turbo
- **Pattern:** Reflection (Agentic AI)
- **Language:** Python 3.12

## 📁 Project Structure
```
ai-debate-arena/
├── app.py              # Gradio web interface
├── debate_engine.py    # Core debate logic with reflection
├── requirements.txt    # Python dependencies
├── .env               # API keys (create this yourself)
├── .gitignore         # Ignore sensitive files
└── README.md          # This file
```

## 👨‍💻 Built By

**Raghul Mukundan** | Following [@andrewng](https://twitter.com/andrewyng)'s Agentic AI Course

**Source Code:** [GitHub](https://github.com/raghulmukundan/ai-debate-arena)

## 📝 Example Topics

**Simple choices:**
- Should I order pizza or sushi?
- Morning or evening gym?
- iPhone or Samsung?

**Career decisions:**
- Should I accept the job offer or stay?
- Should I negotiate my salary?

**Philosophical:**
- Should I depend on luck?
- Is failure necessary for success?

## 🔒 Privacy

Your API keys are only used for this session and never stored.

---

## 🙏 Acknowledgments

- **Andrew Ng** - For the Agentic AI course on DeepLearning.AI
- **Anthropic** - For Claude API and models
- **OpenAI** - For GPT models
- **Gradio** - For the web framework

---

*Note: This is a demonstration of agentic AI patterns. Results may vary based on model, topic, and prompt sensitivity.*

**Enjoy watching AI debate itself! 🎭**