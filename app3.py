# conda activate webexp
# ngrok http 5000

from flask import Flask, request
import base64
import os
import re

app = Flask(__name__)

# ===================== 配置 =====================
PAGE_TITLE = "RenderGuard - Single Article View"
ICON_SIZE = "80px"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_PNG = os.path.join(BASE_DIR, "input_image.png")
# ✅ 你现在的输出目录
OUTPUT_PNG_DIR = os.path.join(BASE_DIR, "encoded_images1")
# ✅ 你现在的 mapping 文件
KEY_INFO_FILE = os.path.join(BASE_DIR, "articles_key_mapping.txt")

# 防 AI/爬虫关键词
AI_KEYWORDS = [
    'bot', 'crawler', 'spider', 'curl', 'wget', 'python', 'requests', 'scrapy',
    'playwright', 'puppeteer', 'chatgpt', 'gpt', 'claude', 'bingbot',
    'googlebot', 'baiduspider'
]

# -------------------------- 工具函数 --------------------------
def reject_ai_crawler():
    """简单UA拦截：返回 (blocked: bool, response_html, status_code)"""
    user_agent = request.headers.get('User-Agent', '').lower()
    if any(k in user_agent for k in AI_KEYWORDS) or re.match(r'^python-requests/\d+\.\d+', user_agent):
        html = """<html><head><meta charset="utf-8"></head>
        <body style="text-align:center;margin-top:100px;font-size:20px;">
        禁止爬虫/AI访问！
        </body></html>"""
        return True, html, 403
    return False, "", 200

def read_article_mapping(mapping_file: str) -> dict:
    """
    读取文章-图片-密钥映射关系
    返回 dict: { article_id: {img_path, aes_key_b64, payload_len} }
    期望格式(含表头)：
    ARTICLE_ID\tIMAGE_PATH\tAES_KEY_B64\tPAYLOAD_LEN
    """
    mp = {}
    with open(mapping_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if not lines:
        raise RuntimeError("映射文件为空")

    for line in lines[1:]:  # 跳过表头
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            # 容错：遇到异常行直接跳过
            continue
        article_id, img_path, aes_key_b64, payload_len = parts
        mp[article_id] = {
            "id": article_id,
            "img_path": img_path,
            "aes_key_b64": aes_key_b64,
            "payload_len": int(payload_len),
        }
    return mp

def img_to_base64(img_path: str) -> str:
    """将本地图片转为Base64 DataURL"""
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"

def safe_title(s: str) -> str:
    """避免把 sample_id 里奇怪字符带进 HTML"""
    return re.sub(r"[^a-zA-Z0-9_\-]", "", s)

# -------------------------- 路由：索引页（列表） --------------------------
@app.get("/")
def index_page():
    blocked, html, code = reject_ai_crawler()
    if blocked:
        return html, code

    mapping = read_article_mapping(KEY_INFO_FILE)
    base_img_b64 = img_to_base64(INPUT_PNG)

    # 生成列表（点击进入 /sample_001 这种）
    ids = sorted(mapping.keys())

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{PAGE_TITLE}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
    <style>
      body {{
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        padding: 25px;
        margin: 0;
        background: #f8f8f8;
      }}
      #steg-icon {{
        position: fixed;
        top: 25px;
        left: 25px;
        width: {ICON_SIZE};
        height: {ICON_SIZE};
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        z-index: 9999;
        object-fit: cover;
      }}
      .container {{
        width: 800px;
        margin: 0 auto;
      }}
      .title {{
        text-align:center;
        font-size: 22px;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 8px;
      }}
      .hint {{
        text-align:center;
        color:#666;
        margin-bottom: 18px;
      }}
      .list {{
        background:#fff;
        border-radius: 8px;
        padding: 14px 18px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
      }}
      .item {{
        padding: 10px 6px;
        border-bottom: 1px solid #eee;
      }}
      .item:last-child {{
        border-bottom: none;
      }}
      a {{
        text-decoration:none;
        color:#1a73e8;
      }}
      a:hover {{
        text-decoration: underline;
      }}
    </style>
  </head>
  <body>
    <img id="steg-icon" src="{base_img_b64}" alt="base icon">
    <div class="container">
      <div class="title">RenderGuard</div>
      <div class="hint">点击 sample_id 进入详情页（每页仅解密展示一篇文章）</div>
      <div class="list">
        {''.join([f'<div class="item"><a href="/{safe_title(i)}">{safe_title(i)}</a></div>' for i in ids])}
      </div>
    </div>
  </body>
</html>
"""
# -------------------------- 路由：详情页（单文章） --------------------------
@app.get("/<article_id>")
def article_page(article_id: str):
    blocked, html, code = reject_ai_crawler()
    if blocked:
        return html, code

    article_id = safe_title(article_id)
    mapping = read_article_mapping(KEY_INFO_FILE)

    if article_id not in mapping:
        return f"""<html><head><meta charset="utf-8"></head>
        <body style="font-family:system-ui;padding:30px;">
        <h3>404: Article not found</h3>
        <p>Unknown id: <b>{article_id}</b></p>
        <p><a href="/">Back to index</a></p>
        </body></html>""", 404

    art = mapping[article_id]
    base_img_b64 = img_to_base64(INPUT_PNG)

    # 单篇文章对应的隐写图片
    img_b64 = img_to_base64(art["img_path"])

    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{PAGE_TITLE} - {article_id}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <meta name="robots" content="noindex, nofollow, noarchive, nosnippet">

    <style>
      body {{
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        padding: 25px;
        margin: 0;
        background: #f8f8f8;
      }}
      #steg-icon {{
        position: fixed;
        top: 25px;
        left: 25px;
        width: {ICON_SIZE};
        height: {ICON_SIZE};
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        z-index: 9999;
        object-fit: cover;
      }}
      .wrap {{
        width: 800px;
        margin: 0 auto;
      }}
      .topbar {{
        display:flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
      }}
      .page-title {{
        font-size: 22px;
        font-weight: 600;
        color: #2d3748;
      }}
      .back a {{
        color:#1a73e8;
        text-decoration:none;
      }}
      .back a:hover {{
        text-decoration: underline;
      }}
      .card {{
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
        padding: 25px;
        background: #ffffff;
        border-radius: 8px;
        box-shadow: 0 1px 6px rgba(0,0,0,0.06);
        user-select: none;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
      }}
      .article-title {{
        font-size: 20px;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px solid #eee;
      }}
      .content-loading {{
        color: #999;
        font-style: italic;
      }}
      ::selection {{background: transparent;}}
      ::-moz-selection {{background: transparent;}}
    </style>

    <script>
      // 防AI爬取：禁止右键/查看源码/复制（基础）
      document.addEventListener('contextmenu', e => e.preventDefault());
      document.addEventListener('keydown', e => {{
        if ((e.ctrlKey && e.key === 'u') || (e.ctrlKey && e.key === 'c') || (e.shiftKey && e.key === 'i')) {{
          e.preventDefault();
        }}
      }});
    </script>
  </head>

  <body>
    <img id="steg-icon" src="{base_img_b64}" alt="base icon">
    <div class="wrap">
      <div class="topbar">
        <div class="page-title">RenderGuard</div>
        <div class="back"><a href="/">Back</a></div>
      </div>

      <div class="card"
           id="article-card"
           data-key="{art['aes_key_b64']}"
           data-payload="{art['payload_len']}"
           data-img="{img_b64}">
        <div class="article-title">{article_id}</div>
        <div class="content content-loading" id="content">(loading...)</div>
      </div>
    </div>

    <script>
      function b64ToBytes(b64) {{
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) {{
          bytes[i] = bin.charCodeAt(i);
        }}
        return bytes;
      }}

      function lsbBitsToBytes(bits) {{
        const data = new Uint8Array(Math.floor(bits.length / 8));
        for (let i = 0; i < data.length; i++) {{
          let byte = 0;
          for (let j = 0; j < 8; j++) {{
            if (i + j >= bits.length) break;
            byte = (byte << 1) | bits[i * 8 + j];
          }}
          data[i] = byte;
        }}
        return data;
      }}

      async function extractDataFromPng(imgB64, dataLen) {{
        const img = new Image();
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        await new Promise((resolve, reject) => {{
          img.crossOrigin = 'anonymous';
          img.onload = resolve;
          img.onerror = () => reject(new Error("图片加载失败"));
          img.src = imgB64;
        }});

        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);

        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = imageData.data;
        const w = canvas.width, h = canvas.height;

        const needBits = dataLen * 8;
        const maxBits = w * h * 3;
        if (needBits > maxBits) {{
          throw new Error(`提取数据过长！需要${{needBits}}位，图片仅含${{maxBits}}位`);
        }}

        const bits = [];
        let bitIdx = 0;
        for (let y = 0; y < h && bitIdx < needBits; y++) {{
          for (let x = 0; x < w && bitIdx < needBits; x++) {{
            const off = (y * w + x) * 4;
            const r = pixels[off];
            const g = pixels[off + 1];
            const b = pixels[off + 2];

            bits.push(r & 1); bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(g & 1); bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(b & 1); bitIdx++;
            if (bitIdx >= needBits) break;
          }}
        }}
        return lsbBitsToBytes(bits);
      }}

      async function aesGcmDecrypt(nonce, ct, key) {{
        const cryptoKey = await window.crypto.subtle.importKey(
          'raw', key, {{ name: 'AES-GCM' }}, false, ['decrypt']
        );
        const plainBuf = await window.crypto.subtle.decrypt(
          {{ name: 'AES-GCM', iv: nonce }}, cryptoKey, ct
        );
        return new TextDecoder('utf-8').decode(plainBuf);
      }}

      async function extractAndDecryptPng(key, imgB64, totalPayloadLen) {{
        const payload = await extractDataFromPng(imgB64, totalPayloadLen);
        const nonce = payload.slice(0, 12);
        const ctLenView = new DataView(payload.buffer, 12, 4);
        const ctLen = ctLenView.getUint32(0, false);
        const ct = payload.slice(16, 16 + ctLen);
        return await aesGcmDecrypt(nonce, ct, key);
      }}

      async function decryptOne() {{
        const card = document.getElementById('article-card');
        const out = document.getElementById('content');

        try {{
          const keyB64 = card.dataset.key;
          const payloadLen = parseInt(card.dataset.payload);
          const imgB64 = card.dataset.img;

          const key = b64ToBytes(keyB64);
          const plaintext = await extractAndDecryptPng(key, imgB64, payloadLen);
          out.textContent = plaintext;
          out.classList.remove('content-loading');
        }} catch (e) {{
          out.textContent = "解密失败: " + e.message;
          out.style.color = "#ff4444";
        }}
      }}

      // 延迟解密：确保函数已定义后再执行
      setTimeout(() => {{
        window.onload = decryptOne;
      }}, 1);
    </script>
  </body>
</html>
"""
if __name__ == "__main__":
    # 本地跑：127.0.0.1:5000
    # ngrok http 5000
    app.run(host="127.0.0.1", port=5000, debug=True)