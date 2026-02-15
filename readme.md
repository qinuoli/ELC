# ELC: Anti-AI Crawling Web Application

ELC is a web application combining **AES-GCM encryption** and **LSB steganography** technology, designed to prevent automatic content crawling by AI models. By embedding encrypted data into images, information can only be read after decryption via client-side (rendering layer) JavaScript, significantly enhancing content protection. This project is suitable for displaying multiple articles, where the ciphertext of each article is embedded into an image file.

## Core Features
- Encrypt text content using **AES-GCM encryption** algorithm for secure data protection.
- Embed encrypted ciphertext into the **Least Significant Bit (LSB)** of images, using images as the storage medium for ciphertext.
- Decrypt ciphertext from images via front-end JavaScript, avoiding exposure of sensitive data on the backend.
- Support display and decryption of multiple articles simultaneously.

## Usage Notes
1. Place new article text files into the `article/` directory.
2. Run `en.py` to:
   - Generate AES-GCM encryption keys for new articles
   - Embed encrypted ciphertext into images (stored in `encoded_images/`)
   - Update the mapping relationship in `article_key_mapping.txt`
3. Start the web application with `app.py` to serve the protected articles.
4. Clients will decrypt the image-embedded ciphertext via front-end JavaScript to view the original content.