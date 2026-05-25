import os
import re
from pathlib import Path

def embed_urls():
    """
    เวอร์ชันปรับปรุง: ใช้ Regex ที่ยืดหยุ่นขึ้นในการค้นหา [PROMPT: ...]
    และแทนที่ด้วย URL ตามลำดับที่พบ
    """
    owner = "boyn149"
    branch = "main"
    
    # อ่านชื่อ repo
    try:
        with open("repo_name.txt", "r", encoding="utf-8") as f:
            repo_name = f.read().strip()
    except:
        print("Error reading repo_name.txt")
        return

    book_code = "book1"
    book_file = Path(f"book/book_{book_code}/book_{book_code}_เสน่ห์เงียบทรงพลัง_ Passive Attractive ฉบับผู้หญิง INFJ.md")
    
    if not book_file.exists():
        print(f"File not found: {book_file}")
        return

    with open(book_file, "r", encoding="utf-8") as f:
        content = f.read()

    # ค้นหา [PROMPT: ...] ทั้งหมดในไฟล์
    prompts = re.findall(r'\[PROMPT:.*?\]', content, re.DOTALL)
    
    print(f"Found {len(prompts)} prompts to replace.")
    
    for i, p in enumerate(prompts, 1):
        # สร้าง URL ตามลำดับ (infographic_book1_1, _2, _3)
        filename = f"infographic_{book_code}_{i}.png"
        raw_url = f"![Infographic](https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/book/book_{book_code}/pic_{book_code}/{filename})"
        
        # แทนที่ prompt นั้นๆ (ใช้ replace แบบจำกัดจำนวนครั้งละ 1 เพื่อความแม่นยำตามลำดับ)
        content = content.replace(p, raw_url, 1)
        print(f"  ✅ Replaced prompt {i} with {filename}")

    with open(book_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"✨ Finalized embedding for {book_file}")

if __name__ == "__main__":
    embed_urls()
