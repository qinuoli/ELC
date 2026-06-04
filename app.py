from flask import Flask
import base64

app = Flask(__name__)

PAGE_TITLE = "ELC Demo"
KEY_INFO_FILE = "./article_key_mapping.txt"
INPUT_PNG = "./input_image.png"


def clean_article_name(name: str) -> str:
    if name.lower().endswith(".txt"):
        return name[:-4]
    return name


def read_article_mapping(mapping_file: str) -> list[dict]:
    article_list = []
    with open(mapping_file, "r", encoding="utf-8") as f:
        lines = f.readlines()
        for line in lines[1:]:
            line = line.strip()
            if not line:
                continue
            art_name, img_path, aes_key_b64, payload_len = line.split("\t")
            article_list.append(
                {
                    "name": art_name,
                    "display_name": clean_article_name(art_name),
                    "img_path": img_path,
                    "aes_key_b64": aes_key_b64,
                    "payload_len": int(payload_len),
                }
            )
    return article_list


def img_to_base64(img_path: str) -> str:
    with open(img_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{b64}"


article_mapping = read_article_mapping(KEY_INFO_FILE)
for article in article_mapping:
    article["img_b64"] = img_to_base64(article["img_path"])

CARRIER_B64 = img_to_base64(INPUT_PNG)


def render_nav(current: str) -> str:
    tabs = [
        ("/", "Protected Website", "protected"),
        ("/principle", "Principle", "principle"),
    ]
    links = "".join(
        [
            f'<a class="nav-link {"active" if current == key else ""}" href="{href}">{label}</a>'
            for href, label, key in tabs
        ]
    )
    return f"""
    <header class="topbar">
      <div class="brand-block">
        <img class="brand-icon" src="{CARRIER_B64}" alt="ELC logo">
        <div>
          <div class="brand-name">ELC Demo</div>
          <div class="brand-subtitle">Limiting LLM crawling through client-side rendering recovery</div>
        </div>
      </div>
      <nav class="nav-row">
        {links}
      </nav>
    </header>
    """


def base_styles() -> str:
    return """
    <style>
      :root {
        --page-bg: #f4f6fb;
        --card-bg: #ffffff;
        --border: #d9dfec;
        --ink: #1f2937;
        --muted: #6b7280;
        --blue: #2563eb;
        --green: #0f9f6e;
        --soft-blue: #eef4ff;
        --soft-green: #ecfdf5;
      }
      * {
        box-sizing: border-box;
      }
      body {
        font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
        padding: 24px;
        margin: 0;
        color: var(--ink);
        background: linear-gradient(180deg, #f7f9fc 0%, #eef3fb 100%);
      }
      .page-shell {
        max-width: 1120px;
        margin: 0 auto;
      }
      .topbar {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: center;
        margin-bottom: 24px;
        flex-wrap: wrap;
      }
      .brand-block {
        display: flex;
        gap: 14px;
        align-items: center;
      }
      .brand-icon {
        height: 56px;
        width: auto;
        max-width: 132px;
        border-radius: 10px;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
        object-fit: contain;
      }
      .brand-name {
        font-size: 24px;
        font-weight: 700;
      }
      .brand-subtitle {
        color: var(--muted);
        font-size: 14px;
      }
      .nav-row {
        display: flex;
        gap: 10px;
        flex-wrap: wrap;
      }
      .nav-link {
        text-decoration: none;
        color: var(--muted);
        border: 1px solid var(--border);
        background: rgba(255, 255, 255, 0.88);
        border-radius: 999px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 700;
      }
      .nav-link.active {
        color: var(--ink);
        background: #ffffff;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.08);
      }
      .hero {
        padding: 8px 0 18px;
        margin: 0 auto 18px;
      }
      .page-title {
        font-size: 30px;
        font-weight: 700;
        margin: 0 0 10px;
      }
      .hint {
        color: var(--muted);
        font-size: 15px;
        max-width: 860px;
        line-height: 1.6;
      }
      .site-frame {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
      }
      .site-frame-header {
        display: flex;
        justify-content: space-between;
        gap: 14px;
        align-items: center;
        padding: 16px 20px;
        border-bottom: 1px solid var(--border);
        background: #fbfcfe;
      }
      .site-logo {
        font-size: 20px;
        font-weight: 700;
      }
      .site-nav {
        display: flex;
        gap: 18px;
        color: var(--muted);
        font-size: 14px;
      }
      .site-hero {
        padding: 28px 22px 16px;
      }
      .site-hero h1 {
        margin: 0 0 10px;
        font-size: 30px;
      }
      .site-hero p {
        margin: 0;
        color: var(--muted);
        font-size: 15px;
        line-height: 1.6;
        max-width: 760px;
      }
      .site-article-list {
        display: flex;
        flex-direction: column;
        gap: 14px;
        padding: 0 22px 22px;
      }
      .site-article-card {
        border: 1px solid var(--border);
        background: #ffffff;
        border-radius: 14px;
        padding: 18px;
      }
      .article-title {
        font-size: 21px;
        font-weight: 700;
        margin-bottom: 8px;
      }
      .article-subtitle {
        font-size: 14px;
        color: var(--muted);
        line-height: 1.5;
        margin-bottom: 12px;
      }
      .content {
        font-size: 17px;
        line-height: 1.7;
        white-space: pre-wrap;
      }
      .content-loading {
        color: #8a93a3;
        font-style: italic;
      }
      .flow-card {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px;
        backdrop-filter: blur(8px);
        margin-bottom: 20px;
      }
      .flow-title {
        font-size: 14px;
        font-weight: 700;
        color: var(--muted);
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }
      .flow-subtitle {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.5;
        max-width: 780px;
        margin-bottom: 14px;
      }
      .flow-bar {
        display: grid;
        grid-template-columns: repeat(5, minmax(0, 1fr));
        gap: 10px;
      }
      .flow-step {
        cursor: pointer;
        background: #f8fafc;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 12px;
        min-height: 94px;
        transition: 0.2s ease;
      }
      .flow-step.active {
        border-color: #9fc0ff;
        background: var(--soft-blue);
      }
      .flow-step.done {
        border-color: #9bddc2;
        background: var(--soft-green);
      }
      .step-index {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 26px;
        height: 26px;
        border-radius: 999px;
        background: #dbe6fb;
        color: #24478f;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 10px;
      }
      .flow-step.done .step-index {
        background: #cceedd;
        color: #0e6c4c;
      }
      .step-name {
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 6px;
      }
      .step-copy {
        font-size: 13px;
        color: var(--muted);
        line-height: 1.45;
      }
      .control-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 14px;
        flex-wrap: wrap;
        margin-bottom: 16px;
      }
      .mode-group,
      .action-group,
      .toggle-group {
        display: flex;
        gap: 10px;
        align-items: center;
        flex-wrap: wrap;
      }
      .control-pill {
        border: 1px solid var(--border);
        background: #ffffff;
        color: var(--muted);
        border-radius: 999px;
        padding: 9px 14px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
      }
      .control-pill.active {
        color: var(--ink);
        background: var(--soft-blue);
        border-color: #9fc0ff;
      }
      .control-button {
        border: 1px solid var(--border);
        background: #ffffff;
        color: var(--ink);
        border-radius: 10px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 700;
        cursor: pointer;
      }
      .control-button:disabled {
        color: #9aa3b1;
        cursor: default;
        background: #f8fafc;
      }
      .toggle-label {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13px;
        color: var(--muted);
        font-weight: 600;
      }
      .article-container {
        display: flex;
        flex-direction: column;
        gap: 18px;
      }
      .article-card {
        background: var(--card-bg);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
      }
      .article-header {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        align-items: flex-start;
        margin-bottom: 16px;
      }
      .article-meta {
        display: flex;
        flex-direction: column;
        gap: 6px;
      }
      .payload-badge {
        border: 1px solid var(--border);
        background: #f8fafc;
        color: var(--muted);
        border-radius: 999px;
        padding: 8px 12px;
        font-size: 13px;
        font-weight: 600;
        white-space: nowrap;
      }
      .comparison-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px;
      }
      .view-panel {
        border-radius: 14px;
        padding: 16px;
        border: 1px solid var(--border);
        min-height: 280px;
      }
      .llm-view {
        background: #f8fafc;
      }
      .human-view {
        background: #fbfffd;
      }
      .panel-label {
        font-size: 13px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 14px;
      }
      .preview-image {
        width: 100%;
        max-height: 160px;
        object-fit: contain;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid var(--border);
        margin-bottom: 14px;
      }
      .panel-note {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 6px;
      }
      .panel-muted {
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
      }
      .status-line {
        font-size: 13px;
        font-weight: 700;
        color: var(--blue);
        margin-bottom: 12px;
      }
      .status-card {
        border: 1px solid var(--border);
        background: #f8fafc;
        border-radius: 10px;
        padding: 12px;
        color: var(--muted);
        font-size: 14px;
        line-height: 1.55;
        margin-bottom: 12px;
      }
      .detail-card {
        border: 1px solid var(--border);
        background: #ffffff;
        border-radius: 10px;
        padding: 12px;
        color: var(--muted);
        font-size: 13px;
        line-height: 1.6;
        margin-bottom: 12px;
        white-space: pre-wrap;
        display: none;
      }
      .detail-card.visible {
        display: block;
      }
      @media (max-width: 900px) {
        body {
          padding: 18px;
        }
        .comparison-grid,
        .flow-bar {
          grid-template-columns: 1fr;
        }
        .article-header,
        .site-frame-header,
        .topbar {
          flex-direction: column;
          align-items: flex-start;
        }
      }
    </style>
    """


def page_shell(current: str, hero_html: str, body_html: str, script_html: str) -> str:
    return f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>{PAGE_TITLE}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {base_styles()}
  </head>
  <body>
    <main class="page-shell">
      {render_nav(current)}
      {hero_html}
      {body_html}
    </main>
    {script_html}
  </body>
</html>"""


@app.get("/")
def protected_website_page():
    article_cards = "".join(
        [
            f"""
      <section class="site-article-card" data-key="{article['aes_key_b64']}" data-payload="{article['payload_len']}" data-img="{article['img_b64']}">
        <div class="article-title">{article['display_name']}</div>
        <div class="article-subtitle">Readable content is restored through client-side rendering for human readers.</div>
        <div class="content content-loading">(rendering protected content...)</div>
      </section>
      """
            for article in article_mapping
        ]
    )
    hero_html = """
      <section class="hero">
        <h1 class="page-title">ELC-protected Website for Human Readers</h1>
        <div class="hint">
          This page presents the human-facing usage effect of ELC. The page structure is delivered normally, while the readable article content is restored through client-side rendering after the browser recovers the protected payload.
        </div>
      </section>
    """
    body_html = f"""
      <section class="site-frame">
        <div class="site-frame-header">
          <div class="site-logo">ELC-protected Website</div>
          <div class="site-nav">
            <div>Articles</div>
            <div>Archive</div>
            <div>About</div>
          </div>
        </div>
        <div class="site-hero">
          <h1>Readable content is recovered in the browser</h1>
          <p>
            Human readers access the page as a normal website. The page remains usable without extra login or manual key operations, while the meaningful text appears after client-side rendering.
          </p>
        </div>
        <div class="site-article-list">
          {article_cards}
        </div>
      </section>
    """
    script_html = """
    <script>
      function b64ToBytes(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
      }
      function lsbBitsToBytes(bits) {
        const data = new Uint8Array(Math.floor(bits.length / 8));
        for (let i = 0; i < data.length; i++) {
          let byte = 0;
          for (let j = 0; j < 8; j++) {
            if (i + j >= bits.length) break;
            byte = (byte << 1) | bits[i * 8 + j];
          }
          data[i] = byte;
        }
        return data;
      }
      async function extractDataFromPng(imgB64, dataLen) {
        const img = new Image();
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        await new Promise((resolve, reject) => {
          img.crossOrigin = 'anonymous';
          img.onload = resolve;
          img.onerror = () => reject(new Error('Image load failed'));
          img.src = imgB64;
        });
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = imageData.data;
        const w = canvas.width;
        const h = canvas.height;
        const needBits = dataLen * 8;
        const maxBits = w * h * 3;
        if (needBits > maxBits) throw new Error('Payload too large for the current image.');
        const bits = [];
        let bitIdx = 0;
        for (let y = 0; y < h && bitIdx < needBits; y++) {
          for (let x = 0; x < w && bitIdx < needBits; x++) {
            const pixelOffset = (y * w + x) * 4;
            bits.push(pixels[pixelOffset] & 1); bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(pixels[pixelOffset + 1] & 1); bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(pixels[pixelOffset + 2] & 1); bitIdx++;
            if (bitIdx >= needBits) break;
          }
        }
        return lsbBitsToBytes(bits);
      }
      async function aesGcmDecrypt(nonce, ct, key) {
        const cryptoKey = await window.crypto.subtle.importKey('raw', key, { name: 'AES-GCM' }, false, ['decrypt']);
        const plainBuf = await window.crypto.subtle.decrypt({ name: 'AES-GCM', iv: nonce }, cryptoKey, ct);
        return new TextDecoder('utf-8').decode(plainBuf);
      }
      async function extractAndDecryptPng(key, imgB64, totalPayloadLen) {
        const payload = await extractDataFromPng(imgB64, totalPayloadLen);
        const nonce = payload.slice(0, 12);
        const ctLenView = new DataView(payload.buffer, 12, 4);
        const ctLen = ctLenView.getUint32(0, false);
        const ct = payload.slice(16, 16 + ctLen);
        return await aesGcmDecrypt(nonce, ct, key);
      }
      async function decryptAllArticles() {
        const cards = document.querySelectorAll('.site-article-card');
        for (const card of cards) {
          try {
            const key = b64ToBytes(card.dataset.key);
            const payloadLen = parseInt(card.dataset.payload, 10);
            const imgB64 = card.dataset.img;
            const plaintext = await extractAndDecryptPng(key, imgB64, payloadLen);
            const content = card.querySelector('.content');
            content.textContent = plaintext;
            content.className = 'content';
          } catch (e) {
            const content = card.querySelector('.content');
            content.textContent = 'Content could not be recovered in the browser.';
            content.className = 'content content-loading';
          }
        }
      }
      window.onload = decryptAllArticles;
    </script>
    """
    return page_shell("protected", hero_html, body_html, script_html)


@app.get("/principle")
def principle_page():
    article_cards = "".join(
        [
            f"""
      <section class="article-card" data-key="{article['aes_key_b64']}" data-payload="{article['payload_len']}" data-img="{article['img_b64']}">
        <div class="article-header">
          <div class="article-meta">
            <div class="article-title">{article['display_name']}</div>
            <div class="article-subtitle">The LLM-facing exposure layer reveals only the carrier image, while the human-readable content appears after client-side rendering.</div>
          </div>
          <div class="payload-badge">{article['payload_len']} bytes</div>
        </div>
        <div class="comparison-grid">
          <div class="view-panel llm-view">
            <div class="panel-label">LLM-facing View</div>
            <img class="preview-image" src="{article['img_b64']}" alt="{article['display_name']} encoded image">
            <div class="panel-note">Visible artifact: carrier image only</div>
            <div class="panel-muted">The exposure layer does not contain a semantic plaintext article body for LLM crawling.</div>
          </div>
          <div class="view-panel human-view">
            <div class="panel-label">Human-readable View</div>
            <div class="status-line"></div>
            <div class="status-card"></div>
            <div class="detail-card"></div>
            <div class="content content-loading">Protected content is being prepared in the browser.</div>
          </div>
        </div>
      </section>
      """
            for article in article_mapping
        ]
    )
    hero_html = """
      <section class="hero">
        <h1 class="page-title">Principle</h1>
        <div class="hint">
          ELC limits LLM crawling by exposing a carrier image at the LLM-facing layer and restoring readable content only after client-side rendering in the human user’s browser.
        </div>
      </section>
    """
    body_html = f"""
      <section class="flow-card">
        <div class="flow-title">Recovery Flow</div>
        <div class="flow-subtitle">
          The browser recovers the protected article through a fixed five-step process while the LLM-facing layer remains without semantic plaintext.
        </div>
        <div class="control-row">
          <div class="mode-group">
            <button class="control-pill active" id="mode-auto" type="button">Automatic</button>
            <button class="control-pill" id="mode-manual" type="button">Manual</button>
          </div>
          <div class="action-group">
            <button class="control-button" id="step-back" type="button">Previous Step</button>
            <button class="control-button" id="step-forward" type="button">Advance Step</button>
            <button class="control-button" id="replay-flow" type="button">Replay Flow</button>
          </div>
          <div class="toggle-group">
            <label class="toggle-label">
              <input type="checkbox" id="show-details">
              Show technical details
            </label>
          </div>
        </div>
        <div class="flow-bar">
          <div class="flow-step active" id="step-1">
            <div class="step-index">1</div>
            <div class="step-name">Carrier Image</div>
            <div class="step-copy">The page delivers a normal PNG as the visible artifact.</div>
          </div>
          <div class="flow-step" id="step-2">
            <div class="step-index">2</div>
            <div class="step-name">Payload Extraction</div>
            <div class="step-copy">The browser reads RGB least significant bits from the PNG.</div>
          </div>
          <div class="flow-step" id="step-3">
            <div class="step-index">3</div>
            <div class="step-name">Structure Parsing</div>
            <div class="step-copy">The embedded bytes are parsed into nonce, length, and ciphertext.</div>
          </div>
          <div class="flow-step" id="step-4">
            <div class="step-index">4</div>
            <div class="step-name">Client-side Decryption</div>
            <div class="step-copy">The browser decrypts the payload with the mapped AES-GCM key.</div>
          </div>
          <div class="flow-step" id="step-5">
            <div class="step-index">5</div>
            <div class="step-name">Readable Article</div>
            <div class="step-copy">The human user sees readable article text after client-side rendering.</div>
          </div>
        </div>
      </section>
      <div class="article-container">
        {article_cards}
      </div>
    """
    script_html = """
    <script>
      const stepDelayMs = 800;
      const articleStates = [];
      let currentStage = 1;
      let currentMode = 'auto';
      let autoRunToken = 0;
      let showDetails = false;

      function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
      }
      function setFlowState(activeStep) {
        for (let i = 1; i <= 5; i++) {
          const step = document.getElementById(`step-${i}`);
          step.classList.remove('active', 'done');
          if (i < activeStep) step.classList.add('done');
          else if (i === activeStep) step.classList.add('active');
        }
      }
      function setMode(mode) {
        currentMode = mode;
        document.getElementById('mode-auto').classList.toggle('active', mode === 'auto');
        document.getElementById('mode-manual').classList.toggle('active', mode === 'manual');
        document.getElementById('step-back').disabled = mode !== 'manual' || currentStage <= 1;
        document.getElementById('step-forward').disabled = mode !== 'manual' || currentStage >= 5;
      }
      function b64ToBytes(b64) {
        const bin = atob(b64);
        const bytes = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
        return bytes;
      }
      function lsbBitsToBytes(bits) {
        const data = new Uint8Array(Math.floor(bits.length / 8));
        for (let i = 0; i < data.length; i++) {
          let byte = 0;
          for (let j = 0; j < 8; j++) {
            if (i + j >= bits.length) break;
            byte = (byte << 1) | bits[i * 8 + j];
          }
          data[i] = byte;
        }
        return data;
      }
      async function extractDataFromPng(imgB64, dataLen) {
        const img = new Image();
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        await new Promise((resolve, reject) => {
          img.crossOrigin = 'anonymous';
          img.onload = resolve;
          img.onerror = () => reject(new Error('Image load failed'));
          img.src = imgB64;
        });
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const pixels = imageData.data;
        const w = canvas.width;
        const h = canvas.height;
        const needBits = dataLen * 8;
        const maxBits = w * h * 3;
        if (needBits > maxBits) throw new Error('Payload too large for the current image.');
        const bits = [];
        let bitIdx = 0;
        for (let y = 0; y < h && bitIdx < needBits; y++) {
          for (let x = 0; x < w && bitIdx < needBits; x++) {
            const pixelOffset = (y * w + x) * 4;
            bits.push(pixels[pixelOffset] & 1); bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(pixels[pixelOffset + 1] & 1); bitIdx++;
            if (bitIdx >= needBits) break;
            bits.push(pixels[pixelOffset + 2] & 1); bitIdx++;
            if (bitIdx >= needBits) break;
          }
        }
        return lsbBitsToBytes(bits);
      }
      async function aesGcmDecrypt(nonce, ct, key) {
        const cryptoKey = await window.crypto.subtle.importKey('raw', key, { name: 'AES-GCM' }, false, ['decrypt']);
        const plainBuf = await window.crypto.subtle.decrypt({ name: 'AES-GCM', iv: nonce }, cryptoKey, ct);
        return new TextDecoder('utf-8').decode(plainBuf);
      }
      function initArticleStates() {
        document.querySelectorAll('.article-card').forEach(card => {
          articleStates.push({
            card,
            key: b64ToBytes(card.dataset.key),
            payloadLen: parseInt(card.dataset.payload, 10),
            imgB64: card.dataset.img,
            payload: null,
            nonce: null,
            ctLen: null,
            ciphertext: null,
            plaintext: null,
          });
        });
      }
      function stageMessage(stage) {
        if (stage === 1) return ['Carrier image delivered.', 'The LLM-facing layer exposes an image artifact rather than semantic article text.'];
        if (stage === 2) return ['Payload extracted in the browser.', 'The browser has recovered hidden bits from the carrier image.'];
        if (stage === 3) return ['Protected structure parsed.', 'The browser has identified nonce, length, and ciphertext structure for recovery.'];
        if (stage === 4) return ['Client-side decryption completed.', 'The protected content has been decrypted locally inside the browser.'];
        return ['Readable article rendered.', 'The human user can now read the recovered article content after client-side rendering.'];
      }
      function stageDetails(state, stage) {
        if (stage === 1) {
          return `Carrier image size: ${state.payloadLen} payload bytes mapped to the visible PNG artifact.`;
        }
        if (stage === 2) {
          return `Payload extracted: ${state.payloadLen} bytes from RGB least significant bits.`;
        }
        if (stage === 3) {
          const nonceLen = state.nonce ? state.nonce.length : 0;
          const ctLen = state.ctLen || 0;
          return `Parsed structure\\nnonce: ${nonceLen} bytes\\nciphertext length: ${ctLen} bytes`;
        }
        if (stage === 4) {
          return 'AES-GCM decryption executed locally in the browser with the mapped article key.';
        }
        return 'Plaintext article content has been restored and rendered on the client side.';
      }
      function renderHumanView(stage) {
        const [headline, summary] = stageMessage(stage);
        articleStates.forEach(state => {
          const statusLine = state.card.querySelector('.status-line');
          const statusCard = state.card.querySelector('.status-card');
          const detailCard = state.card.querySelector('.detail-card');
          const content = state.card.querySelector('.content');
          statusLine.textContent = headline;
          statusCard.textContent = summary;
          detailCard.textContent = stageDetails(state, stage);
          detailCard.classList.toggle('visible', showDetails);
          if (stage < 5) {
            content.textContent = 'Client-side rendering is in progress.';
            content.className = 'content content-loading';
          } else {
            content.textContent = state.plaintext || '';
            content.className = 'content';
          }
        });
      }
      async function computeStageTwo(state) {
        if (!state.payload) state.payload = await extractDataFromPng(state.imgB64, state.payloadLen);
      }
      function computeStageThree(state) {
        if (!state.nonce) {
          state.nonce = state.payload.slice(0, 12);
          const ctLenView = new DataView(state.payload.buffer, 12, 4);
          state.ctLen = ctLenView.getUint32(0, false);
          state.ciphertext = state.payload.slice(16, 16 + state.ctLen);
        }
      }
      async function computeStageFour(state) {
        if (!state.plaintext) state.plaintext = await aesGcmDecrypt(state.nonce, state.ciphertext, state.key);
      }
      async function ensureStage(stage) {
        if (stage >= 2) for (const state of articleStates) await computeStageTwo(state);
        if (stage >= 3) for (const state of articleStates) computeStageThree(state);
        if (stage >= 4) for (const state of articleStates) await computeStageFour(state);
      }
      async function goToStage(stage) {
        currentStage = stage;
        await ensureStage(stage);
        setFlowState(stage);
        renderHumanView(stage);
        document.getElementById('step-back').disabled = currentMode !== 'manual' || currentStage <= 1;
        document.getElementById('step-forward').disabled = currentMode !== 'manual' || currentStage >= 5;
      }
      async function runAutomaticFlow() {
        const token = ++autoRunToken;
        setMode('auto');
        for (let stage = 1; stage <= 5; stage++) {
          if (token !== autoRunToken || currentMode !== 'auto') return;
          await goToStage(stage);
          if (stage < 5) await sleep(stepDelayMs);
        }
      }
      function bindControls() {
        document.getElementById('mode-auto').addEventListener('click', () => {
          runAutomaticFlow();
        });
        document.getElementById('mode-manual').addEventListener('click', async () => {
          autoRunToken++;
          setMode('manual');
          await goToStage(currentStage);
        });
        document.getElementById('step-back').addEventListener('click', async () => {
          if (currentMode !== 'manual' || currentStage <= 1) return;
          await goToStage(currentStage - 1);
        });
        document.getElementById('step-forward').addEventListener('click', async () => {
          if (currentMode !== 'manual' || currentStage >= 5) return;
          await goToStage(currentStage + 1);
        });
        document.getElementById('replay-flow').addEventListener('click', async () => {
          autoRunToken++;
          currentStage = 1;
          await goToStage(1);
          if (currentMode === 'auto') {
            runAutomaticFlow();
          }
        });
        document.getElementById('show-details').addEventListener('change', event => {
          showDetails = event.target.checked;
          renderHumanView(currentStage);
        });
        document.querySelectorAll('.flow-step').forEach((stepEl, index) => {
          stepEl.addEventListener('click', async () => {
            autoRunToken++;
            if (currentMode !== 'manual') {
              setMode('manual');
            }
            await goToStage(index + 1);
          });
        });
      }
      async function runPrincipleDemo() {
        initArticleStates();
        bindControls();
        await goToStage(1);
        runAutomaticFlow();
      }
      window.onload = runPrincipleDemo;
    </script>
    """
    return page_shell("principle", hero_html, body_html, script_html)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
