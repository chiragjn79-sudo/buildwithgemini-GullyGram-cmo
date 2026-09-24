import asyncio
import os
import shutil
from playwright.async_api import async_playwright

OUTPUT_DIR = "/config/.gemini/antigravity/brain/85508562-8a8d-4770-bc53-48a78970ca96"
TEMP_VIDEO_DIR = os.path.join(OUTPUT_DIR, "temp_video")
FINAL_VIDEO_PATH = os.path.join(OUTPUT_DIR, "gullygram_cmo_demo.webm")

APP_URL = "https://gullygram-cmo-frontend-287012207859.us-east1.run.app"

async def record_demo():
    os.makedirs(TEMP_VIDEO_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=TEMP_VIDEO_DIR,
            record_video_size={"width": 1280, "height": 720}
        )
        page = await context.new_page()

        print("1. Opening Gullygram CMO web app...")
        await page.goto(APP_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        print("2. Prompt 1: Core App Feature - Viral Badminton Tournament Post...")
        prompt1 = "Generate a viral social media post for Gullygram badminton tournament in HSR Layout society"
        await page.fill("#input", prompt1)
        await page.wait_for_timeout(1000)
        await page.click("button.send-btn")
        
        # Wait for agent response to populate
        print("Waiting for Agent response...")
        await page.wait_for_selector(".msg.agent .bubble", timeout=90000)
        await page.wait_for_timeout(5000)

        print("3. Prompt 2: Richer Prompt - Database Tool Lookup & Marketing ROI Calculation...")
        prompt2 = "Look up our marketing channels from Firestore and calculate marketing ROI for 50000 INR budget on Society Whatsapp Groups"
        await page.fill("#input", prompt2)
        await page.wait_for_timeout(1000)
        await page.click("button.send-btn")
        
        # Wait for second response
        await page.wait_for_timeout(15000)
        await page.wait_for_timeout(4000)

        print("4. Demonstrating Indian Festival Posts Studio...")
        await page.click("#tab-festivals")
        await page.wait_for_timeout(3000)

        # Select Eid festival pill
        print("Selecting festival pill...")
        pills = await page.query_selector_all(".fest-pill")
        if len(pills) > 1:
            await pills[1].click()
            await page.wait_for_timeout(2000)

        # Edit caption text
        print("Editing caption live...")
        await page.fill("#editor-caption", "🌙 Eid Mubarak from Gullygram & HSR Layout Society! 🌙\nWishing all residents peace, joy, and victory on the badminton court!")
        await page.wait_for_timeout(2000)

        # Click Copy Caption
        print("Clicking Copy Caption...")
        copy_btns = await page.query_selector_all("button.btn-action")
        if copy_btns:
            await copy_btns[0].click()
            await page.wait_for_timeout(2000)

        await page.wait_for_timeout(3000)

        await context.close()
        await browser.close()

        # Retrieve recorded video file
        files = os.listdir(TEMP_VIDEO_DIR)
        if files:
            src_path = os.path.join(TEMP_VIDEO_DIR, files[0])
            shutil.copy(src_path, FINAL_VIDEO_PATH)
            print(f"✅ Demo video recorded successfully: {FINAL_VIDEO_PATH}")
            shutil.rmtree(TEMP_VIDEO_DIR)
        else:
            print("❌ Video file recording failed")

if __name__ == "__main__":
    asyncio.run(record_demo())
