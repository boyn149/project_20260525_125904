import asyncio
import os
import re
from pathlib import Path
from notebooklm import NotebookLMClient

def clean_citations(text):
    """
    ลบ citation เช่น [1], [1, 2], [1 - 3] ออกจากข้อความ
    """
    pattern = r'\[\d+(?:[\s\-\,]+\d+)*\]'
    return re.sub(pattern, '', text)

def sanitize_filename(filename):
    """
    ล้างชื่อไฟล์สำหรับ Windows
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

async def write_book2():
    """
    Phase 2: เขียนเนื้อหาสำหรับ book2
    """
    print("🚀 Starting Phase 2: Writing Content for book2")
    
    # อ่าน Notebook ID
    try:
        with open("notebook_id.txt", "r") as f:
            notebook_id = f.read().strip()
    except FileNotFoundError:
        print("❌ Error: notebook_id.txt not found.")
        return

    book_code = "book2"
    book_name = "กลไกปิดตายความรู้สึก: เจาะลึกปรากฏการณ์ Door Slam ของ INFJ"
    
    # กำหนดไฟล์ output
    safe_book_name = sanitize_filename(book_name)
    output_path = Path(f"book/book_{book_code}/book_{book_code}_{safe_book_name}.md")
    
    # เคลียร์ไฟล์เก่า
    if output_path.exists():
        os.remove(output_path)

    async with await NotebookLMClient.from_storage() as client:
        # 1. ตรวจสอบและลบ source อื่นๆ ที่เป็น layer (ถ้ามี)
        print("Checking for existing layer sources...")
        sources = await client.sources.list(notebook_id)
        for src in sources:
            if "layer" in src.title.lower():
                print(f"  Removing old layer source: {src.title}")
                await client.sources.delete(notebook_id, src.id)

        # 2. Add layer1-4.md ของ book2 เข้า sources
        layer_files = [
            Path(f"book/book_{book_code}/layer1.md"),
            Path(f"book/book_{book_code}/layer2.md"),
            Path(f"book/book_{book_code}/layer3.md"),
            Path(f"book/book_{book_code}/layer4.md")
        ]
        
        added_sources = []
        print(f"Adding layers for {book_code} to sources...")
        for lp in layer_files:
            if lp.exists():
                src = await client.sources.add_file(notebook_id, lp)
                added_sources.append(src.id)
                print(f"  Added: {lp}")
        
        await asyncio.sleep(5) # รอประมวลผล

        # 3. เริ่มเขียนเนื้อหาตามลำดับ
        prompts = [
            (f"preface {book_code}", "Writing Preface..."),
            (f"con-1-1-1 {book_code} ใช้หัวข้อตาม outline ใน layer3.md", "Writing Chapter 1 Topic 1.1..."),
            (f"con-1-1-2 {book_code} ใช้หัวข้อตาม outline ใน layer3.md", "Writing Chapter 1 Topic 1.2..."),
            (f"reference {book_code}", "Writing Reference..."),
            (f"bio {book_code}", "Writing Bio..."),
            (f"contact {book_code}", "Writing Contact...")
        ]

        conversation_id = None
        
        for i, (prompt, desc) in enumerate(prompts):
            print(desc)
            
            # กฎ: แยกบทใช้ conversation_id ใหม่
            is_con = prompt.startswith("con-")
            
            result = await client.chat.ask(
                notebook_id, 
                prompt, 
                conversation_id=conversation_id if is_con else None
            )
            
            if is_con:
                conversation_id = result.conversation_id
            
            clean_answer = clean_citations(result.answer)
            
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(clean_answer)
                f.write("\n\n")
            
            print(f"  ✓ Finished {prompt}")
            await asyncio.sleep(5)

        # 4. ลบ layer sources
        print(f"Cleaning up layers for {book_code} from sources...")
        for src_id in added_sources:
            try:
                await client.sources.delete(notebook_id, src_id)
            except Exception as e:
                print(f"  Failed to delete source {src_id}: {e}")

    print(f"\n✨ Finished writing {book_name}")
    print(f"📄 Output: {output_path}")

if __name__ == "__main__":
    asyncio.run(write_book2())
