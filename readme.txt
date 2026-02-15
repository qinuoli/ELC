RenderGuard 是一个结合了 AES-GCM 加密 和 LSB 隐写技术 的网页应用，旨在防止 AI 自动抓取网页内容。通过将加密数据隐写到图像中，信息只有在客户端（渲染层）通过 JavaScript 解密后才可读取，增强了对内容的保护。此项目适用于多篇文章的展示，每篇文章的密文都嵌入到图像文件中。

功能：

使用 AES-GCM 加密技术对文本内容进行加密。

将加密后的密文嵌入图片的最低有效位（LSB），通过图像来存储密文。

通过前端 JavaScript 解密图像中的密文，避免后端暴露敏感数据。

支持多篇文章的展示和解密。


文件结构
.
├── app.py                                                                          ##网页程序
├── article                                                                           ##存放文章的文件夹
│   ├── A Child's Biography.txt
│   ├── About Magnanimous-Incident Literature.txt
│   └── 春江花月夜.txt
├── article_key_mapping.txt                                                 ##存放 文章密钥-文章长度-图片 对应关系的文件
├── en.py                                                                            ##加密程序 运行之后更新文章密钥，更新隐写图片，将新文章放入 article文件夹后应运行此程序
├── encoded_images                                                           ##存放加密信息的图片
│   ├── A Child's Biography.png
│   ├── About Magnanimous-Incident Literature.png
│   └── 春江花月夜.png
├── input_image.png                                                            ##网站图标，同时也是存放信息前的原图片
└── readme.txt                                                                     ##本文件，介绍如何使用