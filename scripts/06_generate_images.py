import asyncio
import os
import re
import json
from pathlib import Path
from datetime import datetime
from notebooklm import NotebookLMClient, InfographicOrientation, InfographicStyle

async def generate_images():
    """
    Phase 4: สร้างรูปภาพสำหรับ book1
    """
    # อ่าน Notebook ID
    try:
        with open("notebook_id.txt", "r") as f:
            notebook_id = f.read().strip()
    except FileNotFoundError:
        print("❌ Error: notebook_id.txt not found.")
        return

    book_code = "book1"
    output_dir = Path(f"book/book_{book_code}/pic_{book_code}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Prompts
    prompts = [
        {
            "id": 1,
            "prompt": "A minimal 16:8 informational infographic about INFJ Cognitive Functions (Ni and Fe) in Thai language. White background, simple and elegant design. The infographic must show how \"Ni\" represents Mystery and \"Fe\" represents Warmth/Empathy. All text in the image MUST be in Thai language only.",
            "filename": f"infographic_{book_code}_1.png"
        },
        {
            "id": 2,
            "prompt": "A minimal 16:8 illustration of a magnetic chess piece gently pulling another piece towards it without touching, using soft pastel colors on a clean white background, symbolizing passive attraction and psychological pull.",
            "filename": f"infographic_{book_code}_2.png"
        },
        {
            "id": 3,
            "prompt": "A minimal 16:8 Educational Infographic (Process Infographic) showing a 3-step passive attraction strategy for INFJ. Step 1: 'สังเกตและเข้าใจ (Fe)'. Step 2: 'เว้นระยะห่าง (Introversion)'. Step 3: 'สร้างความลึกลับน่าค้นหา (Ni)'. Use soft pastel arrows and icons on a clean white background. All text in the image MUST be completely in Thai language.",
            "filename": f"infographic_{book_code}_3.png"
        }
    ]

    print(f"🚀 Starting Phase 4: Image Generation for {book_code}")
    
    results = []

    async with await NotebookLMClient.from_storage() as client:
        for item in prompts:
            print(f"🎨 Image {item['id']}/{len(prompts)}: {item['filename']}")
            
            result_data = {
                "prompt_id": item['id'],
                "filename": item['filename'],
                "prompt": item['prompt'],
                "status": "pending",
                "output_path": None
            }
            
            try:
                # สร้าง infographic
                result = await client.artifacts.generate_infographic(
                    notebook_id,
                    instructions=item['prompt'],
                    orientation=InfographicOrientation.LANDSCAPE,
                    style=InfographicStyle.PROFESSIONAL
                )
                
                print(f"  ✓ Task ID: {result.task_id}")
                
                # รอให้สร้างเสร็จ
                final_status = await client.artifacts.wait_for_completion(
                    notebook_id,
                    result.task_id,
                    timeout=600,
                    initial_interval=30
                )
                
                if final_status.is_complete:
                    # หา artifact_id
                    artifacts = await client.artifacts.list(notebook_id)
                    infographics = [a for a in artifacts if a.kind == 'infographic' and a.is_completed]
                    
                    if infographics:
                        latest_infographic = infographics[0]
                        artifact_id = latest_infographic.id
                        
                        # ดาวน์โหลด
                        output_path = output_dir / item['filename']
                        await client.artifacts.download_infographic(
                            notebook_id, 
                            str(output_path), 
                            artifact_id=artifact_id
                        )
                        
                        result_data['status'] = 'completed'
                        result_data['output_path'] = str(output_path)
                        print(f"  ✅ Saved: {output_path}")
                    else:
                        print("  ❌ No infographic artifacts found")
                else:
                    print(f"  ❌ Failed: {final_status.status}")
            
            except Exception as e:
                print(f"  ❌ Error: {e}")
            
            results.append(result_data)
            await asyncio.sleep(10) # Delay ระหว่างรูป
    
    return results

if __name__ == "__main__":
    asyncio.run(generate_images())
