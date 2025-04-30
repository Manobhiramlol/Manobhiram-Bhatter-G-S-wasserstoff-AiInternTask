# 🪨 What Beats Rock?

**An AI-powered twist on the classic game, where words, wit, and creativity battle the immovable rock!**

---

## 🎯 Overview

**What Beats Rock?** is an AI-enhanced conceptual word game where players try to outsmart “rock” with metaphors, logic, or clever reasoning. Whether you say “paper,” “dynamite,” or “existential crisis,” the backend AI evaluates your entry and delivers feedback — with the mood you choose: **serious** or **cheerful**.

---

## 🧠 How It Works

1. Enter your creative attempt to "beat rock."
2. Choose the tone: cheerful 🥳 or serious 🧠.
3. The AI evaluates your input and returns a response.
4. Results are stored and handled efficiently with Redis for quick access and fun leaderboard-style experiences.

---

## 🛠️ Tech Stack

| Layer         | Technology       |
|--------------|------------------|
| Frontend     | Streamlit        |
| Backend      | FastAPI (Python) |
| AI Engine    | Gemini (LLM)     |
| Database     | Redis            |
| Containerization | Docker       |

---

## 📁 Project Structure

```
.
├── frontend
│   ├── Dockerfile
│   ├── requirements.txt
│   └── frontend.py
├── backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   └── redis_client.py
├── docker-compose.yml
```

---

## 🚀 Getting Started

Follow these steps to run the project locally using Docker:

```bash
# Step 1: Clone the repository
git clone https://github.com/Manobhiramlol/Manobhiram-Bhatter-G-S-wasserstoff-AiInternTask.git
cd Manobhiram-Bhatter-G-S-wasserstoff-AiInternTask

# Step 2: Build and start the containers
docker-compose up --build
```

Once running, open your browser and visit:

> 🌐 `http://localhost:8501` to access the Streamlit frontend.

---

## 🔧 Features

- 🔮 AI-generated feedback powered by LLM (Gemini)
- 🤖 Backend logic served with FastAPI
- 🚀 Rapid performance with Redis caching
- 🐳 Full Docker-based containerization
- 🎭 Toggle between **serious** and **cheerful** AI tone modes

---

## 📦 Dependencies

All dependencies are defined in respective `requirements.txt` files under the `frontend` and `backend` directories. Docker handles installing them during the build process.

---

## 💡 Future Ideas

- Scoreboard and analytics for best responses
- Multiplayer mode
- Customizable AI personalities
- Voice input integration

---

