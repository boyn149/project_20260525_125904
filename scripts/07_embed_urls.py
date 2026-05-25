import os
import re
from pathlib import Path

def embed_urls():
    owner = "boyn149"
    branch = "main"
    
    # อ่านชื่อ repo
    try:
        with open("repo_name.txt", "r") as f:
            repo_name = f.read().strip()
    except:
        print("Error reading repo_name.txt")
        return

    book_file = Path("book/book_book1/book_book1_เสน่ห์เงียบทรงพลัง_ Passive Attractive ฉบับผู้หญิง INFJ.md")
    if not book_file.exists():
        print(f"File not found: {book_file}")
        return

    with open(book_file, "r", encoding="utf-8") as f:
        content = f.read()

    # นิยาม Prompts และ URLs
    prompts_map = [
        {
            "pattern": r'\[PROMPT: A minimal 16:8 informational infographic about INFJ Cognitive Functions \(Ni and Fe\) in Thai language\. White background, simple and elegant design\. The infographic must show how "Ni" represents Mystery and "Fe" represents Warmth/Empathy\. All text in the image MUST be in Thai language only\.\]',
            "filename": "infographic_book1_1.png"
        },
        {
            "pattern": r'\[PROMPT: A minimal 16:8 illustration of a magnetic chess piece gently pulling another piece towards it without touching, using soft pastel colors on a clean white background, symbolizing passive attraction and psychological pull\.\]',
            "filename": "infographic_book1_2.png"
        },
        {
            "pattern": r'\[PROMPT: A minimal 16:8 Educational Infographic \(Process Infographic\) showing a 3-step passive attraction strategy for INFJ\. Step 1: \'สังเกตและเข้าใจ \(Fe\)\'\. Step 2: \'เว้นระยะห่าง \(Introversion\)\'\. Step 3: \'สร้างความลึกลับน่าค้นหา \(Ni\)\'\. Use soft pastel arrows and icons on a clean white background\. All text in the image MUST be completely in Thai language\.\]',
            "filename": "infographic_book1_3.png"
        }
    ]

    for item in prompts_map:
        raw_url = f"![Infographic](https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/book/book_book1/pic_book1/{item['filename']})"
        content = re.sub(item['pattern'], raw_url, content)

    # จัดการกรณี prompt ที่เหลือ (ถ้ามีที่หาไม่เจอด้วย regex เป๊ะๆ)
    # ลองใช้แบบยืดหยุ่นขึ้นนิดหน่อย
    flexible_prompts = re.findall(r'\[PROMPT:.*?\]', content)
    for fp in flexible_prompts:
        print(f"Warning: Found unreplaced prompt: {fp}")

    with open(book_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✅ Embedded URLs into {book_file}")

if __name__ == "__main__":
    embed_urls()
