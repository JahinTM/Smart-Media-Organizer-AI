from pathlib import Path
import tempfile
from PIL import Image, ImageOps, ImageDraw
import imagehash
import cv2

def safe_copy_name(target):
    target = Path(target)
    if not target.exists():
        return target
    stem, suffix = target.stem, target.suffix
    counter = 1
    while True:
        candidate = target.with_name(f"{stem}_{counter}{suffix}")
        if not candidate.exists():
            return candidate
        counter += 1

def image_phash(path):
    try:
        with Image.open(path) as im:
            return imagehash.phash(im.convert("RGB"))
    except Exception:
        return None

def make_video_contact_sheet(video_path, sample_count=4):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total <= 0:
        cap.release()
        return None
    frames = []
    for i in range(sample_count):
        frame_no = int(total * (i + 1) / (sample_count + 1))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        ok, frame = cap.read()
        if ok:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            im = Image.fromarray(rgb)
            im.thumbnail((320, 220))
            canvas = Image.new("RGB", (320, 220), "white")
            canvas.paste(im, ((320-im.width)//2, (220-im.height)//2))
            frames.append(canvas)
    cap.release()
    if not frames:
        return None
    sheet = Image.new("RGB", (640, 440), "#eeeeee")
    for idx, im in enumerate(frames[:4]):
        x = (idx % 2) * 320
        y = (idx // 2) * 220
        sheet.paste(im, (x, y))
    out = Path(tempfile.gettempdir()) / f"media_contact_{abs(hash(str(video_path)))}.jpg"
    sheet.save(out, quality=85)
    return out
