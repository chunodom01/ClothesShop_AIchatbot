# ClothesShop Fanpage Chatbot 🛍️

An LLM-powered Messenger assistant for a clothing shop fanpage. It wraps an LLM
with tools, memory, and a persona following a **Speak → Think → Know → Act**
pipeline.

> Capstone project for *Creating AI Applications Using Python* — STEP IT
> Academy, Phnom Penh.

- **Business name:** ClothesShop
- **Persona:** Friendly clothing shop assistant (English)

## What this is

- Uses Google Gemini (`gemini-flash-latest`) as the language model.
- Built as an agent system: persona prompt, FAQ search tool, booking/order
  tool, and per-customer memory.
- Connects directly to Facebook Messenger via webhook.

> **Note on Gemini model names:** Google frequently deprecates older Gemini
> model versions (e.g. `gemini-1.5-flash`, `gemini-2.5-flash` have both been
> retired for new users as of writing). This project uses the
> `gemini-flash-latest` alias, which always points to Google's current
> default Flash model, so it keeps working without needing manual updates.

## Architecture

```
Messenger user ──▶ app/webhook.py   (Speak: receives & verifies FB events)
                        │
                        ▼
                    app/agent.py    (Think: LangChain agent + per-user memory)
                        │
              ┌─────────┴─────────┐
              ▼                   ▼
   app/tools/faq_search.py   app/tools/sheets.py
   (Know: Pinecone RAG)      (Act: save_order → SheetDB)
                        │
                        ▼
                app/messenger.py   (Send API reply back to Messenger)
```

| Stage | Module | What it does |
|---|---|---|
| **Speak** | `app/webhook.py` | Verifies and receives incoming Facebook Messenger events. |
| **Think** | `app/agent.py` | Runs the LangChain agent, holding per-user conversation memory and deciding which tool to call. |
| **Know** | `app/tools/faq_search.py` | Searches a Pinecone vector index of FAQ content to ground answers. |
| **Act** | `app/tools/sheets.py` | Saves confirmed orders/bookings to a Google Sheet via SheetDB. |
| **Reply** | `app/messenger.py` | Sends the agent's response back through the Messenger Send API. |

## Setup

**1. Create a virtual environment and install dependencies**

macOS/Linux:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows:
```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**2. Configure environment variables**

Copy `.env.example` → `.env` and fill in:

| Variable | Purpose |
|---|---|
| `GOOGLE_API_KEY` | Gemini API key (used as the LLM) |
| `FB_VERIFY_TOKEN` | Token used to verify the Messenger webhook |
| `FB_PAGE_ACCESS_TOKEN` | Page access token for sending Messenger replies |
| `PINECONE_API_KEY` | Vector DB key for FAQ search (RAG) |
| `SHEETDB_API` | Your SheetDB endpoint for logging orders/bookings |

**3. Add your FAQ data**

Edit `data/faqs.csv` with at least 15 Q&A pairs covering sizes, prices, hours,
delivery, and payment. Example rows:

```csv
question,answer
What sizes do you carry?,We carry S to XXL for most items.
Do you deliver outside Phnom Penh?,Yes, delivery is available nationwide via GHS Express.
What payment methods do you accept?,We accept ABA, Wing, and cash on delivery.
```

## Testing locally (no Messenger / no publishing required)

The whole agent pipeline (FAQ lookup, booking tool, memory) can be exercised
directly in the terminal — you don't need Facebook, ngrok, or a published app
to prove it works:

```bash
python -m scripts.local_test
```

This drops you into a simple prompt:

```
Type a message (or 'quit'):
You: hi
Bot: ...
```

Type messages as if you were the customer and confirm the bot responds
correctly (FAQ answers, and that a booking gets logged to your Google Sheet
when you confirm an order). This is the easiest way for anyone reviewing the
project — teacher included — to see it working, since it doesn't require
being invited to the Facebook app or the fanpage being live.

## Running the full Messenger integration (optional)

Only needed if you actually want to test through Facebook Messenger itself:

```bash
uvicorn app.main:app --reload
ngrok http 8000
```

Then connect the webhook to Facebook:

1. In the [Meta for Developers](https://developers.facebook.com/) dashboard,
   open your app → **Messenger** → **Settings**.
2. Under **Webhooks**, click **Add Callback URL** and paste your ngrok HTTPS
   URL followed by your webhook path (e.g. `https://xxxx.ngrok.io/webhook`).
3. Enter the same value you set for `FB_VERIFY_TOKEN` as the **Verify Token**.
4. Subscribe the webhook to the `messages` field, and subscribe your fanpage
   to the app.

**Important:** while the Facebook app is in Development mode, only accounts
added as a Tester/Developer/Admin on the app can message the page and get a
response — anyone else's messages are silently dropped by Facebook before
they ever reach the webhook. This is expected behavior, not a bug in the
code. Publishing the app (App Review) isn't required for grading — local
testing above covers a working demo without it.

## Example conversation

```
User:  Hi! Do you have any dresses in size M?
Bot:   Yes! We have several dress styles in size M 👗 Would you like
       me to show you our current collection or check a specific style?

User:  I'd like to book the floral one for pickup Saturday.
Bot:   Great choice! I've noted a pickup booking for the floral dress
       (size M) on Saturday. You'll get a confirmation shortly 🎉
```
(Behind the scenes: the first reply comes from the FAQ search tool; the
second triggers the order tool, which logs the booking to Google Sheets.)

## Notes

- If you swap Gemini for OpenAI, set `OPENAI_API_KEY` instead and update the
  model config in `app/agent.py`.
- ngrok URLs change on restart (unless you're on a paid plan) — remember to
  update the Facebook webhook callback URL each time you restart ngrok.
