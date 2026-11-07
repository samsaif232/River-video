"""Usage: python render.py voice.mp3 [output.mp4] [fps]
Renders index.html frame-by-frame (1080x1920, 9:16) and adds the voiceover."""
import subprocess, sys, os
from playwright.sync_api import sync_playwright
audio = sys.argv[1] if len(sys.argv) > 1 else "voice.mp3"
out = sys.argv[2] if len(sys.argv) > 2 else "river_crossing_9x16.mp4"
FPS = int(sys.argv[3]) if len(sys.argv) > 3 else 24
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",audio]))
n = int(dur * FPS)
ff = subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-",
    "-i",audio,"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
    "-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",out], stdin=subprocess.PIPE)
page_url = "file://" + os.path.abspath("index.html")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width":540,"height":960}, device_scale_factor=2)  # = 1080x1920
    pg.goto(page_url)
    pg.wait_for_timeout(500)
    for i in range(n):
        pg.evaluate(f"render({i/FPS})")
        ff.stdin.write(pg.screenshot(type="jpeg", quality=90))
        if i % 120 == 0: print(f"{i}/{n}", flush=True)
    ff.stdin.close(); ff.wait(); b.close()
print("Done ->", out)
