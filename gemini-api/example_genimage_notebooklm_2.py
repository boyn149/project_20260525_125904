import asyncio
from notebooklm import NotebookLMClient, InfographicOrientation, InfographicStyle

async def generate_infographic_from_prompt(notebook_id: str, prompt: str):
    """
    สร้าง infographic จาก text prompt
    
    Args:
        notebook_id: NotebookLM notebook ID
        prompt: Text prompt สำหรับสร้างรูป
    """
    
    async with await NotebookLMClient.from_storage() as client:
        
        # สร้าง infographic - ใช้ Enum ไม่ใช่ string
        result = await client.artifacts.generate_infographic(
            notebook_id,
            instructions=prompt,
            orientation=InfographicOrientation.LANDSCAPE,  # ใช้ Enum
            style=InfographicStyle.PROFESSIONAL            # ใช้ Enum
        )
        
        print(f"✓ Started generation")
        print(f"  Task ID: {result.task_id}")
        
        # รอให้สร้างเสร็จ
        print(f"⏳ Waiting for completion (max 10 minutes)...")
        final_status = await client.artifacts.wait_for_completion(
            notebook_id,
            result.task_id,
            timeout=600,      # 10 minutes
            poll_interval=15  # check ทุก 15 วินาที
        )
        
        if final_status.is_complete:
            print(f"✅ Generation completed!")
            return final_status.artifact_id
        else:
            print(f"❌ Generation failed or timed out")
            return None

# ตัวอย่างการใช้งาน
async def main():
    notebook_id = "305aa725-7f00-437b-a80d-2d9ef65746c0"
    prompt = "A minimal 16:8 Hierarchy Infographic showing the 3 steps of becoming The Ideal Lover using Ni function: 1. Deep Observation (Bottom) 2. Reflecting Unspoken Desires (Middle) 3. Maintaining Mystery (Top), using pastel tones on a white background"
    
    artifact_id = await generate_infographic_from_prompt(notebook_id, prompt)
    
    if artifact_id:
        print(f"🎨 Artifact ID: {artifact_id}")

asyncio.run(main())