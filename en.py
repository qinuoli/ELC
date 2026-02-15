import os
import struct
from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64

# -------------------------- 核心工具函数 --------------------------
def aes_gcm_encrypt(plaintext: str, key: bytes) -> tuple[bytes, bytes]:
    """AES-GCM加密，返回(nonce, 带tag的密文)"""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # GCM标准12字节nonce
    pt_bytes = plaintext.encode("utf-8")
    ct = aesgcm.encrypt(nonce, pt_bytes, None)
    return nonce, ct

def bytes_to_lsb_bits(data: bytes) -> list[int]:
    """字节流转为0/1位列表（LSB隐写用）"""
    bits = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits

def embed_data_in_png(input_png: str, output_png: str, data: bytes) -> None:
    """将二进制数据隐写到PNG的RGB通道LSB"""
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_png), exist_ok=True)
    # 打开图片并转为RGB（兼容RGBA）
    try:
        img = Image.open(input_png).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError(f"载体图片不存在：{input_png}")
    pixels = img.load()
    w, h = img.size

    bits = bytes_to_lsb_bits(data)
    bit_len = len(bits)
    max_bits = w * h * 3  # 每个像素3通道，每通道1位
    if bit_len > max_bits:
        raise ValueError(f"数据过大！需要{bit_len}位，图片仅支持{max_bits}位（换更大的PNG）")

    # 逐像素写入LSB
    bit_idx = 0
    for y in range(h):
        for x in range(w):
            if bit_idx >= bit_len:
                break
            r, g, b = pixels[x, y]
            # R通道
            r = (r & 0xFE) | bits[bit_idx]
            bit_idx += 1
            if bit_idx >= bit_len:
                pixels[x, y] = (r, g, b)
                break
            # G通道
            g = (g & 0xFE) | bits[bit_idx]
            bit_idx += 1
            if bit_idx >= bit_len:
                pixels[x, y] = (r, g, b)
                break
            # B通道
            b = (b & 0xFE) | bits[bit_idx]
            bit_idx += 1
            pixels[x, y] = (r, g, b)
        if bit_idx >= bit_len:
            break

    img.save(output_png, format="PNG")
    print(f"隐写图片已保存：{output_png}")

def encrypt_and_steg_png(plaintext: str, key: bytes, input_png: str, output_png: str) -> int:
    """封装：加密+打包+隐写，返回嵌入的总字节数"""
    nonce, ct = aes_gcm_encrypt(plaintext, key)
    ct_len = len(ct)
    payload = nonce + struct.pack(">I", ct_len) + ct  # 打包结构：nonce+密文长度+密文
    embed_data_in_png(input_png, output_png, payload)
    return len(payload)

# -------------------------- 主执行逻辑 --------------------------
if __name__ == "__main__":
    # ===== 配置项（可自行修改）=====
    INPUT_PNG = "./input_image.png"                    # 基础载体PNG路径
    OUTPUT_PNG_DIR = "./encoded_images"                # 隐写后图片输出目录
    KEY_INFO_FILE = "./article_key_mapping.txt"        # 文章-图片-密钥对应关系文件
    ARTICLE_DIR = "./article"                              # 待处理txt文章目录
    AES_BIT_LENGTH = 128                                 # AES密钥长度(128/256)

    # 确保目录存在
    os.makedirs(OUTPUT_PNG_DIR, exist_ok=True)
    os.makedirs(ARTICLE_DIR, exist_ok=True)

    # 获取article目录下所有txt文件
    txt_files = [f for f in os.listdir(ARTICLE_DIR) if f.lower().endswith(".txt")]
    if not txt_files:
        print(f"警告：{ARTICLE_DIR}目录下未找到任何txt文件")
        exit(0)

    # 写入文章-图片-密钥映射关系（覆盖写入，保证最新）
    with open(KEY_INFO_FILE, "w", encoding="utf-8") as f:
        f.write("ARTICLE_NAME\tIMAGE_PATH\tAES_KEY_B64\tPAYLOAD_LEN\n")
        print("===== 开始批量加密+隐写 =====")
        for txt_file in txt_files:
            # 读取文章内容
            article_path = os.path.join(ARTICLE_DIR, txt_file)
            with open(article_path, "r", encoding="utf-8") as af:
                secret_text = af.read().strip()
            if not secret_text:
                print(f"跳过空文件：{txt_file}")
                continue

            # 生成专属AES密钥
            aes_key = AESGCM.generate_key(bit_length=AES_BIT_LENGTH)
            aes_key_b64 = base64.b64encode(aes_key).decode("utf-8")

            # 定义对应隐写图片路径（与文章同名，改后缀为png）
            img_name = os.path.splitext(txt_file)[0] + ".png"
            output_png = os.path.join(OUTPUT_PNG_DIR, img_name)

            # 加密隐写并获取载荷长度
            try:
                payload_len = encrypt_and_steg_png(
                    plaintext=secret_text,
                    key=aes_key,
                    input_png=INPUT_PNG,
                    output_png=output_png
                )
                # 写入映射关系（制表符分隔，方便网页解析）
                f.write(f"{txt_file}\t{output_png}\t{aes_key_b64}\t{payload_len}\n")
                print(f"处理完成：{txt_file} -> {img_name}")
            except Exception as e:
                print(f"处理失败：{txt_file} - {str(e)}")

    print(f"\n批量处理完成！")
    print(f"文章-图片-密钥映射文件：{KEY_INFO_FILE}")
    print(f"隐写图片存储目录：{OUTPUT_PNG_DIR}")
    print(f"网页可解析 {KEY_INFO_FILE} 获取文章列表与对应图片/密钥")