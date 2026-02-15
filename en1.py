#本程序用于初始化samples，原文存储在./articles 中
# INPUT_PNG = os.path.join(BASE_DIR, "input_image.png")                 # 基础载体PNG路径
# OUTPUT_PNG_DIR = os.path.join(BASE_DIR, "encoded_images1")             # 隐写后图片输出目录
# KEY_INFO_FILE = os.path.join(BASE_DIR, "articles_key_mapping.txt")     # 文章-图片-密钥对应关系文件
# 对应的网页程序在app3.py

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import struct
import base64
from typing import Tuple, List

from PIL import Image
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# -------------------------- 核心工具函数 --------------------------
def aes_gcm_encrypt(plaintext: str, key: bytes) -> Tuple[bytes, bytes]:
    """AES-GCM加密，返回(nonce, 带tag的密文)"""
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)  # GCM标准12字节nonce
    pt_bytes = plaintext.encode("utf-8")
    ct = aesgcm.encrypt(nonce, pt_bytes, None)  # ct includes tag
    return nonce, ct


def bytes_to_lsb_bits(data: bytes) -> List[int]:
    """字节流转为0/1位列表（LSB隐写用）"""
    bits: List[int] = []
    for b in data:
        for i in range(7, -1, -1):
            bits.append((b >> i) & 1)
    return bits


def embed_data_in_png(input_png: str, output_png: str, data: bytes) -> None:
    """将二进制数据隐写到PNG的RGB通道LSB"""
    # 确保输出目录存在（如果 output_png 没有目录部分，也要兼容）
    out_dir = os.path.dirname(output_png) or "."
    os.makedirs(out_dir, exist_ok=True)

    # 打开图片并转为RGB（兼容RGBA）
    if not os.path.exists(input_png):
        raise FileNotFoundError(f"载体图片不存在：{input_png}")

    img = Image.open(input_png).convert("RGB")
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
    payload = nonce + struct.pack(">I", ct_len) + ct  # nonce(12) + ct_len(4) + ct
    embed_data_in_png(input_png, output_png, payload)
    return len(payload)


# -------------------------- 主执行逻辑 --------------------------
if __name__ == "__main__":
    # ===== 配置项（建议保持相对当前脚本目录，避免在别处运行时找不到文件）=====
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    INPUT_PNG = os.path.join(BASE_DIR, "input_image.png")                 # 基础载体PNG路径
    OUTPUT_PNG_DIR = os.path.join(BASE_DIR, "encoded_images1")             # 隐写后图片输出目录
    KEY_INFO_FILE = os.path.join(BASE_DIR, "articles_key_mapping.txt")     # 文章-图片-密钥对应关系文件

    # ✅ 你的切分文章目录是 ./articles（不是 ./article）
    ARTICLE_DIR = os.path.join(BASE_DIR, "articles")                      # 待处理txt文章目录

    AES_BIT_LENGTH = 128  # AES密钥长度(128/256)

    # 确保目录存在
    os.makedirs(OUTPUT_PNG_DIR, exist_ok=True)
    os.makedirs(ARTICLE_DIR, exist_ok=True)

    # 只处理 sample_*.txt，并排序保证输出稳定
    txt_files = sorted(
        [f for f in os.listdir(ARTICLE_DIR) if f.lower().endswith(".txt") and f.startswith("sample_")]
    )
    if not txt_files:
        print(f"警告：{ARTICLE_DIR}目录下未找到任何 sample_*.txt 文件")
        exit(0)

    # 写入文章-图片-密钥映射关系（覆盖写入，保证最新）
    with open(KEY_INFO_FILE, "w", encoding="utf-8") as f:
        # ✅ 第一列建议存 sample_id（不带 .txt），方便 Flask 做 /<sample_id> 路由
        f.write("ARTICLE_ID\tIMAGE_PATH\tAES_KEY_B64\tPAYLOAD_LEN\n")

        print("===== 开始批量加密+隐写 =====")
        for txt_file in txt_files:
            article_id = os.path.splitext(txt_file)[0]  # sample_001
            article_path = os.path.join(ARTICLE_DIR, txt_file)

            # 读取文章内容
            with open(article_path, "r", encoding="utf-8") as af:
                secret_text = af.read().strip()

            if not secret_text:
                print(f"跳过空文件：{txt_file}")
                continue

            # 生成专属AES密钥
            aes_key = AESGCM.generate_key(bit_length=AES_BIT_LENGTH)
            aes_key_b64 = base64.b64encode(aes_key).decode("utf-8")

            # 定义对应隐写图片路径（与 sample_id 同名）
            img_name = f"{article_id}.png"
            output_png = os.path.join(OUTPUT_PNG_DIR, img_name)

            # 加密隐写并获取载荷长度
            try:
                payload_len = encrypt_and_steg_png(
                    plaintext=secret_text,
                    key=aes_key,
                    input_png=INPUT_PNG,
                    output_png=output_png
                )
                # ✅ 写入映射：sample_id, png_path, key_b64, payload_len
                f.write(f"{article_id}\t{output_png}\t{aes_key_b64}\t{payload_len}\n")
                print(f"处理完成：{txt_file} -> {img_name}")
            except Exception as e:
                print(f"处理失败：{txt_file} - {str(e)}")

    print("\n批量处理完成！")
    print(f"文章-图片-密钥映射文件：{KEY_INFO_FILE}")
    print(f"隐写图片存储目录：{OUTPUT_PNG_DIR}")
    print(f"网页可解析 {KEY_INFO_FILE} 获取文章列表与对应图片/密钥")
