## Setup

```bash
python -m venv env
source env/Scripts/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with:

```text
SOURCE_API_URL=...
GOOGLE_API_KEY=...
FILE_SEARCH_STORE_DISPLAY_NAME=OptiBot Knowledge Base
CHAT_MODEL=gemini-2.5-flash
MAX_ARTICLES=0
```

## Run Locally

```bash
python main.py
python main.py --ask "How to i connect Zoom Rooms to OptiSigns Digital Signage?"
```

## Docker

```bash
docker build -t alpha-project .
docker run --rm --env-file .env alpha-project
```

For cloud jobs with persistent state:

```bash
docker run --rm \
  -e GOOGLE_API_KEY=... \
  -e SOURCE_API_URL=... \
  -e FILE_SEARCH_STORE_DISPLAY_NAME=... \
  -e STATE_FILE=/data/state.json \
  -e ARTICLES_DIR=/data/articles \
  -v "$(pwd)/data:/data" \
  kb-sync
```

The container runs `python main.py` once, logs the sync summary, and exits.

## Daily Schedule



## Screenshot

![alt text](<Screenshot 2026-07-05 131334.png>)
