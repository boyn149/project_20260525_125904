import re
from pathlib import Path

def extract_prompts():
    """
    วิเคราะห์ prompt จากไฟล์หนังสือและบันทึกใน pic_ture_details.md
    """
    print("🔍 Extracting prompts from book files...")
    
    book_dirs = list(Path("book").glob("book_*"))
    pic_details = []
    
    for book_dir in book_dirs:
        book_code = book_dir.name.replace("book_", "")
        # หาไฟล์หนังสือ .md (ที่ไม่ใช่ layer)
        book_files = [f for f in book_dir.glob("*.md") if "layer" not in f.name]
        
        for book_file in book_files:
            with open(book_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # ค้นหา [PROMPT: ...]
            prompts = re.findall(r'\[PROMPT:\s*(.*?)\]', content)
            
            if prompts:
                pic_details.append(f"## Book Code: {book_code}")
                pic_details.append(f"File: {book_file.name}")
                pic_details.append(f"Total Prompts: {len(prompts)}")
                for i, p in enumerate(prompts, 1):
                    pic_details.append(f"{i}. {p}")
                pic_details.append("")

    if pic_details:
        with open("pic_ture_details.md", "w", encoding="utf-8") as f:
            f.write("# Picture Details\n\n")
            f.write("\n".join(pic_details))
        print("✅ Saved prompt details to pic_ture_details.md")
    else:
        print("ℹ️ No prompts found in any book files.")

if __name__ == "__main__":
    extract_prompts()
