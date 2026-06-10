# SMS Assistant
A personal SMS Assistant built originally to show me the train times of my commonly used routes [Liverpool & Southport] but turned into a fully fledged text bot that also allows for AI responses and live stock price checks & **EVEN MORE**

## Deployment
I am personally running this on a used Lenovo ThinkCentre M900 Tiny PC running ZimaOS with the Flask app exposed to the internet using Cloudflare Tunnels so that Twilio can send requests to my Lenovo PC.

↓ The links to the software and APIs required to reproduce my setup are listed below ↓

## Features

- **Live Train Times** — Real-Time departures times for preset routes (easily modified within the code) using the Realtime Trains API, showing scheduled time, expected time, and platform where the train will arrive
- **Stock Prices** — Look up any ticker or check a default portfolio (S&P 500, Google, Apple, Microsoft) with percentage change vs. previous close
- **AI Chat** — Ask anything via the `.ai` command, powered by Gemini Flash via OpenRouter. Supports web search, per-number conversation history, and a `clear` command to reset it
- **Message Logging** — All incoming messages and responses are saved to a local SQLite database
- **Containerised** — Runs in Docker via Docker Compose, self-hosted on a homelab server

## Commands

| Command | Description |
|---|---|
| `.ping` | Check the connection is alive |
| `.train default` | Southport → Liverpool Central |
| `.train liverpool` | Liverpool Central → Southport |
| `.train moorfields` | Moorfields → Southport |
| `.stock` | Default portfolio (S&P 500, Google, Apple, Microsoft) |
| `.stock <ticker>` | Any stock by ticker (e.g. `.stock TSLA`) |
| `.ai <question>` | Ask the AI anything (supports web search) |
| `.ai clear` | Clear your conversation history |
| `.phone` | Returns your phone number |

## Tech Stack

- **Language:** Python
- **Web Framework:** Flask
- **SMS:** Twilio
- **AI:** Google Gemini Flash via OpenRouter (with built-in web search tooling)
- **Train Data:** Realtime Trains API
- **Stock Data:** yfinance API
- **Database:** SQLite
- **Deployment:** Docker Compose, self-hosted on homelab

## Project Structure

```
sms-assistant/
├── textapp.py          # Main Flask app and command router
├── services/
│   ├── ai.py           # AI chat, conversation history, OpenRouter integration
│   ├── trains.py       # Live train times via Realtime Trains API
│   ├── stocks.py       # Stock prices via yfinance
│   └── database.py     # SQLite message logging
├── docker-compose.yml
├── requirements.txt
└── .env                # Not committed — see setup below
```

## Setup

### Prerequisites
- Docker + Docker Compose
- A [Twilio](https://www.twilio.com) account with an SMS-capable number
- An [OpenRouter](https://openrouter.ai) API key
- A [Realtime Trains](https://www.realtimetrains.co.uk) API key
- A public URL pointing to port 5000 for Twilio's webhook — personally I use [Cloudflare Tunnels](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/) running on [ZimaOS](https://www.zimaspace.com/zimaos)

### Environment Variables

Create a `.env` file with the following:

```
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_PHONE=your_twilio_number
PERSONAL_PHONE=your_personal_number
TRAIN_API=your_realtime_trains_api_key
AI_API=your_openrouter_api_key
```

### Running with Docker Compose

```bash
docker compose up -d
```

Then point your Twilio SMS webhook to `http://<your-server>:5000/sms`.
