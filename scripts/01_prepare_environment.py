import asyncio
import os
import re
from pathlib import Path
from datetime import datetime
from notebooklm import NotebookLMClient, ChatGoal, SourceStatus

async def wait_for_sources(client, notebook_id):
    """
    รอให้ sources ทั้งหมดใน notebook อยู่ในสถานะ READY
    """
    print("Waiting for sources to be ready...")
    while True:
        # หมายเหตุ: ใน python-api.md ไม่ได้ระบุว่า Source object มี field status โดยตรง 
        # แต่อ้างอิงจาก SourceStatus Enum และพฤติกรรมทั่วไปของ API
        # เราจะลองใช้ get_metadata หรือ list เพื่อดูสถานะ
        try:
            sources = await client.sources.list(notebook_id)
            all_ready = True
            for src in sources:
                # ลองตรวจสอบ attribute status ถ้ามี
                status = getattr(src, 'status', None)
                if status is not None and status != SourceStatus.READY:
                    all_ready = False
                    print(f"  Source '{src.title}' is still {status.name if hasattr(status, 'name') else status}")
                    break
            
            if all_ready:
                print("All sources are ready.")
                break
        except Exception as e:
            print(f"  Error checking sources: {e}")
        
        await asyncio.sleep(5)

def clean_citations(text):
    """
    ลบ citation เช่น [1], [1, 2], [1 - 3] ออกจากข้อความ
    """
    # ลบ [1], [1, 2], [1-2], [1,2,3] ฯลฯ
    pattern = r'\[\d+(?:[\s\-\,]+\d+)*\]'
    return re.sub(pattern, '', text)

async def prepare_environment():
    """
    Phase 0: เตรียม NotebookLM Environment
    """
    print("🚀 Starting Phase 0: Preparing NotebookLM Environment")
    
    # 1. Initialize client
    async with await NotebookLMClient.from_storage() as client:
        # 2. Create notebook
        current_date_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        notebook_title = f"project_{current_date_time}"
        print(f"Creating notebook: {notebook_title}")
        nb = await client.notebooks.create(notebook_title)
        notebook_id = nb.id
        print(f"Created notebook ID: {notebook_id}")

        # 3. Add sources
        sources_to_add = [
            Path("notebooklm/context.md"),
            Path("notebooklm/project.md")
        ]
        
        # Add files from src/
        src_dir = Path("src")
        if src_dir.exists():
            for file in src_dir.glob("*"):
                if file.is_file():
                    sources_to_add.append(file)
            
        print(f"Adding {len(sources_to_add)} sources...")
        for source_path in sources_to_add:
            print(f"  Adding: {source_path}")
            await client.sources.add_file(notebook_id, source_path)
        
        # รอให้ sources พร้อม (ถ้า API รองรับการเช็คสถานะ)
        # หากไม่แน่ใจ ให้ sleep สักครู่
        await asyncio.sleep(10) 
        # await wait_for_sources(client, notebook_id)

        # 4. Inject instruction.md เข้า Configure Chat
        instruction_path = Path("notebooklm/instruction.md")
        if instruction_path.exists():
            with open(instruction_path, "r", encoding="utf-8") as f:
                instruction_content = f.read()
            
            print("Configuring chat with instruction.md...")
            await client.chat.configure(
                notebook_id,
                goal=ChatGoal.CUSTOM,
                custom_prompt=instruction_content
            )
        else:
            print(f"⚠️ Warning: {instruction_path} not found.")

        # 5. Send prompt: "details โดยอ้างอิงจาก project.md"
        print("Sending prompt: 'details โดยอ้างอิงจาก project.md'...")
        result = await client.chat.ask(notebook_id, "details โดยอ้างอิงจาก project.md")
        
        # 6. Save answer to book/details.md
        book_dir = Path("book")
        book_dir.mkdir(exist_ok=True)
        details_path = book_dir / "details.md"
        
        clean_answer = clean_citations(result.answer)

        with open(details_path, "w", encoding="utf-8") as f:
            f.write(clean_answer)
        print(f"✅ Saved details to: {details_path}")

        # 7. Add details.md as a source
        print(f"Adding {details_path} to sources...")
        await client.sources.add_file(notebook_id, details_path)
        
        print("\n✨ Phase 0 completed successfully.")
        print(f"Notebook ID: {notebook_id}")
        
        # บันทึก Notebook ID ไว้ใช้งานใน Phase ต่อไป
        with open("notebook_id.txt", "w") as f:
            f.write(notebook_id)

if __name__ == "__main__":
    asyncio.run(prepare_environment())
