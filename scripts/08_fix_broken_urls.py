import os
import re
from pathlib import Path

def fix_corruption_and_urls():
    owner = "boyn149"
    branch = "main"
    
    # 1. Fix repo_name.txt first (ensure it's clean ASCII/UTF-8)
    repo_name = "project_20260525_125904"
    with open("repo_name.txt", "w", encoding="utf-8") as f:
        f.write(repo_name)
    print(f"✅ Fixed repo_name.txt: {repo_name}")

    book_file = Path("book/book_book1/book_book1_เสน่ห์เงียบทรงพลัง_ Passive Attractive ฉบับผู้หญิง INFJ.md")
    if not book_file.exists():
        print(f"File not found: {book_file}")
        return

    with open(book_file, "rb") as f:
        raw_content = f.read()
    
    # Try to decode, ignoring errors to see the text, or just work with bytes if it's very messy
    # But since we see the pattern in the tool output, we can use a regex on the decoded string.
    # The tool output showed null bytes as \0 and other stuff.
    
    # Let's read it as utf-8 but handle errors
    content = raw_content.decode("utf-8", errors="ignore")

    # The broken URL pattern:
    # ![Infographic](https://raw.githubusercontent.com/boyn149/[MESS]/main/book/book_book1/pic_book1/infographic_book1_N.png)
    
    # We want to replace it with the correct URL.
    def replace_url(match):
        img_num = match.group(1)
        return f"![Infographic](https://raw.githubusercontent.com/{owner}/{repo_name}/{branch}/book/book_book1/pic_book1/infographic_book1_{img_num}.png)"

    # Regex to match the broken URLs. We'll be flexible with the "messy" part.
    # It starts after "boyn149/" and ends before "/main/"
    pattern = r'!\[Infographic\]\(https://raw\.githubusercontent\.com/boyn149/.*?/main/book/book_book1/pic_book1/infographic_book1_(\d+)\.png\)'
    
    new_content = re.sub(pattern, replace_url, content, flags=re.DOTALL)
    
    # Also clean any remaining null bytes or weirdness that might have been introduced
    new_content = new_content.replace('\x00', '').replace('\ufeff', '').replace('\xff\xfe', '')

    with open(book_file, "w", encoding="utf-8") as f:
        f.write(new_content)
    
    print(f"✅ Fixed broken URLs in {book_file}")

if __name__ == "__main__":
    fix_corruption_and_urls()
