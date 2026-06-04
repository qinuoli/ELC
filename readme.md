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

## Environment

- Python: `3.13.5`
- Verified local virtual environment: `.venv`
- Main dependencies:
  - `Flask`
  - `Pillow`
  - `cryptography`

If you use a different Python 3 version, recreate `.venv` and reinstall dependencies with `pip install -r requirements.txt`.

## Encryption

`en.py` converts plaintext article files into ELC-protected PNG artifacts.

Inputs:

- `article/*.txt`: plaintext article files
- `input_image.png`: carrier image used for LSB embedding

Outputs:

- `encoded_images/*.png`: encrypted stego images
- `article_key_mapping.txt`: article name, image path, AES key, and payload length

Run the encryption step with:

```bash
cd /mnt/shared-storage-user/liqinuo/ELC/ELC
source .venv/bin/activate
python en.py
```

After `en.py` finishes, start the website with `python app.py`.

## Setup

```bash
cd /mnt/shared-storage-user/liqinuo/ELC/ELC
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run

```bash
cd /mnt/shared-storage-user/liqinuo/ELC/ELC
source .venv/bin/activate
python app.py
```

Then open:

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/principle`
