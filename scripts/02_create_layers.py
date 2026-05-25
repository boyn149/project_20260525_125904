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

async def create_layers():
    """
    Phase 1: สร้าง Layer 1-4 ของทุกเล่ม
    """
    print("🚀 Starting Phase 1: Creating Layers 1-4")
    
    # อ่าน Notebook ID
    try:
        with open("notebook_id.txt", "r") as f:
            notebook_id = f.read().strip()
    except FileNotFoundError:
        print("❌ Error: notebook_id.txt not found. Please run Phase 0 first.")
        return

    book_codes = ["book1", "book2"]
    layers = ["layer1", "layer2", "layer3", "layer4"]
    
    conversation_id = None
    
    async with await NotebookLMClient.from_storage() as client:
        for layer in layers:
            for book_code in book_codes:
                print(f"Generating {layer} for {book_code}...")
                
                # เตรียม prompt
                prompt = f"{layer} {book_code} ไม่ใช้สำนวน esther และใช้ชื่อหนังสือตามใน details.md"
                
                # ส่ง prompt
                result = await client.chat.ask(
                    notebook_id, 
                    prompt, 
                    conversation_id=conversation_id
                )
                
                # เก็บ conversation_id ไว้ใช้ต่อ
                if conversation_id is None:
                    conversation_id = result.conversation_id
                    print(f"  Captured Conversation ID: {conversation_id}")
                
                # บันทึกไฟล์
                book_dir = Path(f"book/book_{book_code}")
                book_dir.mkdir(parents=True, exist_ok=True)
                
                file_path = book_dir / f"{layer}.md"
                
                clean_answer = clean_citations(result.answer)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(clean_answer)
                
                print(f"  ✅ Saved to: {file_path}")
                
                # หน่วงเวลาเล็กน้อยเพื่อป้องกัน Rate Limit
                await asyncio.sleep(5)

    print("\n✨ Phase 1 completed successfully.")

if __name__ == "__main__":
    asyncio.run(create_layers())
