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
or 
docker run --rm --env-file .env alpha-project --ask "How do I connect Zoom Rooms to OptiSigns Digital Signage?"
```

## Daily Schedule

[text](https://github.com/trtrnguyen14104/my-alpha-mini-project/actions/runs/28732846949/job/85201597237)

## Screenshot

![alt text](<Screenshot 2026-07-05 131334.png>)
