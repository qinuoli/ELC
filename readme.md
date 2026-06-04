# ELC Demo

This directory contains the conference demo variant built from `ELC_cleanup_compare_view`.

## Pages

1. `http://127.0.0.1:5000/`
   - `Protected Website`
   - human-facing website experience
   - readable content restored through client-side rendering

2. `http://127.0.0.1:5000/principle`
   - `Principle`
   - recovery workflow demonstration
   - `LLM-facing View` and `Human-readable View`

## Workflow

The underlying content pipeline remains the same:

1. Put plaintext article files in `article/`
2. Run `en.py`
3. Generated encrypted stego images are written to `encoded_images/`
4. The article-to-image/key mapping is written to `article_key_mapping.txt`
5. Run `app.py`

## Setup

```bash
cd /mnt/shared-storage-user/liqinuo/ELC/ELC_v2
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
cd /mnt/shared-storage-user/liqinuo/ELC/ELC_v2
source .venv/bin/activate
python app.py
```

Then open:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/principle`
