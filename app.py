from flask import Flask
import base64
import os

app = Flask(__name__)

# ===================== 可自定义配置（适配多文章）=====================
PAGE_TITLE = "LSB Steg AES-GCM 多文章解密展示"
ICON_SIZE = "80px"  # 自定义放大图标尺寸
INPUT_PNG = "./input_image.png"                    # 基础载体PNG路径
OUTPUT_PNG_DIR = "./encoded_images"                # 隐写后图片输出目录
KEY_INFO_FILE = "./article_key_mapping.txt"        # 文章-图片-密钥对应关系文件

# -------------------------- 工具函数（适配多文章解析） --------------------------
def read_article_mapping(mapping_file):
    """读取文章-图片-密钥映射关系，返回列表"""
    article_list = []
    try:
        with open(mapping_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[1:]:  # 跳过表头
                line = line.strip()
                if not line:
                    continue
                art_name, img_path, aes_key_b64, payload_len = line.split("\t")
                article_list.append({
                    "name": art_name,
                    "img_path": img_path,
                    "aes_key_b64": aes_key_b64,
                    "payload_len": int(payload_len)
                })
        return article_list
    except Exception as e:
        raise Exception(f"读取映射文件失败: {str(e)}")

def img_to_base64(img_path):
    """将本地图片转为Base64"""
    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{b64}"
    except Exception as e:
        raise Exception(f"读取图片失败{img_path}: {str(e)}")

# 预加载多文章映射关系
article_mapping = read_article_mapping(KEY_INFO_FILE)
# 预加载所有隐写图片Base64
for art in article_mapping:
    art["img_b64"] = img_to_base64(art["img_path"])

# -------------------------- 主页面（多文章展示） --------------------------
@app.get("/")
def page():
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{PAGE_TITLE}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
      body {{
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        padding: 25px;
        margin: 0;
        position: relative;
        min-height: 1vh;
        background: #f8f8f8 no-repeat center center;
        background-size: cover;
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
      .article-container {{
        width: 800px;
        box-sizing: border-box;
        margin: 20px auto 0;
        display: flex;
        flex-direction: column;
        gap: 20px;
      }}
      .article-card {{
        font-size: 18px;
        line-height: 1.6;
        white-space: pre-wrap;
        padding: 25px;
        background: #ffffff;
        border-radius: 6px;
      }}
      .article-title {{
        font-size: 20px;
        font-weight: 600;
        color: #2d3748;
        margin-bottom: 1px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
      }}
      .hint {{
        color: #666;
        margin-bottom: 16px;
        font-size: 16px;
        text-align: center;
        width: 800px;
        box-sizing: border-box;
        margin: 0 auto;
      }}
      .page-title {{
        font-size: 22px;
        font-weight: 600;
        color: #2d3748;
        text-align: center;
        width: 800px;
        box-sizing: border-box;
        margin: 0 auto 8px;
      }}
      .content-loading {{
        color: #999;
        font-style: italic;
      }}
    </style>
  </head>
  <body>
    <img id="steg-icon" src="{img_to_base64(INPUT_PNG)}" alt="基础载体图标">
    <div class="page-title">RenderGuard</div>
    <div class="hint">
      左上角为基础载体 → 自动解析所有隐写文章 → 前端JS解密展示
    </div>
    <div class="article-container">
      {"".join([f'''
      <div class="article-card" data-key="{art['aes_key_b64']}" data-payload="{art['payload_len']}" data-img="{art['img_b64']}">
        <div class="article-title">{art['name']}</div>
        <div class="content content-loading">(loading...)</div>
      </div>
      ''' for art in article_mapping])}
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
            const pixelOffset = (y * w + x) * 4;
            const r = pixels[pixelOffset];
            const g = pixels[pixelOffset + 1];
            const b = pixels[pixelOffset + 2];
            bits.push(r & 1);
            bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(g & 1);
            bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(b & 1);
            bitIdx++;
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
      // 批量解密所有文章
      async function decryptAllArticles() {{
        const articleCards = document.querySelectorAll('.article-card');
        for (const card of articleCards) {{
          try {{
            const keyB64 = card.dataset.key;
            const payloadLen = parseInt(card.dataset.payload);
            const imgB64 = card.dataset.img;
            const key = b64ToBytes(keyB64);
            const plaintext = await extractAndDecryptPng(key, imgB64, payloadLen);
            card.querySelector('.content').textContent = plaintext;
          }} catch (e) {{
            card.querySelector('.content').textContent = "解密失败: " + e.message;
            card.querySelector('.content').style.color = "#ff4444";
          }}
        }}
      }}
      // 页面加载完成后执行批量解密
      window.onload = decryptAllArticles;
    </script>
  </body>
</html>
"""

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)