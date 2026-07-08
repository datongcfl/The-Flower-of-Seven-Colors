from playwright.sync_api import sync_playwright
import sys

OUT = r"D:\福昶工作目录\datongcfl-repository\pms_frontend_shot.png"
URL = "http://127.0.0.1:5173/"

try:
    CHROME = r"C:\Users\Administrator\AppData\Local\ms-playwright\chromium-1223\chrome-win64\chrome.exe"
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.goto(URL, wait_until="networkidle", timeout=30000)
        pg.wait_for_timeout(2500)
        pg.screenshot(path=OUT, full_page=True)
        b.close()
    print("SHOT_OK:" + OUT)
except Exception as e:
    print("SHOT_ERR:" + repr(e))
    sys.exit(1)
