# ⚡ 𝗠𝗘𝗗𝗜𝗔 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗘𝗥 𝗕𝗢𝗧 ⚡

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blueviolet?style=for-the-badge&logo=python)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-cyan?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/docker-compatible-ff69b4?style=for-the-badge&logo=docker)](https://www.docker.com/)

An ultra-premium, high-speed **All-in-One Social Media Downloader Telegram Bot** built with Python, programmatic `yt-dlp`, and `pyTelegramBotAPI`. Feeds on links from YouTube, Instagram Reels, TikTok, Twitter/X, and Pinterest, compressing and serving high-fidelity video streams directly back to you.

Styled with a highly aesthetic **Vaporwave / Cyberpunk Mathematical Sans-serif** typography layout, custom dynamic asset banners, and pure high-vibe GenZ energy.

---

## ✨ Key Features
- **Alphanumeric Mathematical Fonts**: Dynamic runtime converters style every interaction header with sleek mathematical sans pseudo-fonts (`𝗔𝗕𝗖`, `𝘢𝘣𝘤`, `𝘼𝘽𝘾`).
- **Dynamic Photo Banners**: Transmits breathtaking neon custom graphics for every bot state (Welcome, Downloading, Success).
- **Auto Resolution Scaling**: Automatically fallbacks and optimizes video streams (`bestvideo[filesize<45M] + bestaudio[filesize<5M]`) to bypass Telegram's strict **50MB bot upload limit** flawlessly.
- **Throttled Live Progress Tracking**: A state-tracked progress hook updates download percentage, speeds, and ETA every `3.5s` to strictly avoid Telegram rate-limits while keeping you hyped.
- **Zero Disk Storage Footprint**: Auto-wipes temporary downloads immediately upon uploading so your hard drive stays clean.

---

## 📸 Dynamic User Interface

| 🪐 1. Welcome Greeting | ⚡ 2. Live Downloading | 🏆 3. Slayed Delivery |
|---|---|---|
| ![Welcome Banner](assets/welcome.png) | ![Downloading Banner](assets/cooking.png) | ![Success Banner](assets/success.png) |

---

## 🚀 Quick Setup & Local Run

### Prerequisites
- Python 3.11+
- FFmpeg installed and added to your system `PATH` (essential for merging download streams)

### Installation
1. Clone this repository to your local machine:
   ```bash
   git clone <your-github-repo-url>
   cd tg-media-downloader
   ```
2. Create and activate a python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure your token:
   - Duplicate `.env.example` and rename to `.env`
   - Paste your bot token from `@BotFather`:
     ```env
     BOT_TOKEN=8067370938:AAFo3XFFhGgLLTdwZAK43mlCx82vP0ds_Zw
     ```
5. Run the bot:
   ```bash
   python bot.py
   ```

---

## 🐳 Docker Deployment (VPS, Render, Railway, etc.)

This repository contains a fully self-contained `Dockerfile` that packages Python and automatically configures `FFmpeg`.

1. Build the docker image:
   ```bash
   docker build -t tg-media-downloader .
   ```
2. Run the container:
   ```bash
   docker run -d --name downloader-bot --env-file .env tg-media-downloader
   ```

---

## ⚡ Cloud Deployments

### 1. Railway (Recommended)
Railway is extremely fast and natively supports Dockerfile deployment:
- Install the [Railway CLI](https://docs.railway.app/reference/cli-api): `npm i -g @railway/cli`
- Link your project and deploy:
  ```bash
  railway login
  railway init
  railway up
  ```
- In the Railway Dashboard, add the following **Environment Variable**:
  - `BOT_TOKEN`: `YourTelegramBotTokenHere`

### 2. Heroku Deployment
You can deploy to Heroku using the standard `Procfile` worker or Heroku Docker containers:
- Log in to Heroku CLI: `heroku login`
- Create an app: `heroku create your-bot-name`
- Set your environment variables:
  ```bash
  heroku config:set BOT_TOKEN=your_telegram_bot_token_here
  ```
- **Crucial**: Heroku requires FFmpeg to merge files. Add the FFmpeg Buildpack:
  ```bash
  heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
  heroku buildpacks:add heroku/python
  ```
- Push to deploy:
  ```bash
  git push heroku main
  ```

---

## 🛠️ Tech Stack
- **Core Engine**: Python 3.11+
- **API wrapper**: [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) (telebot)
- **Engine Room**: [yt-dlp](https://github.com/yt-dlp/yt-dlp) & System FFmpeg
- **Vibe Level**: Infinite 🪐
