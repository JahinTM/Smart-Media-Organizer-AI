from pathlib import Path
import shutil
import hashlib
import mimetypes
from PIL import Image
from .ai_engine import classify_image, classify_video
from .utils import make_video_contact_sheet, safe_copy_name, image_phash

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tif", ".tiff"}
VIDEO_EXTS = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v", ".3gp", ".webm"}

def sha256_file(path, chunk=1024 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(chunk), b""):
            h.update(block)
    return h.hexdigest()

def run_organization(source, destination, api_key="", use_online=True,
                     copy_duplicates=True, progress_cb=None):
    source, destination = Path(source), Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    files = [p for p in source.rglob("*") if p.is_file()
             and p.suffix.lower() in IMAGE_EXTS | VIDEO_EXTS
             and destination not in p.parents]
    seen_hashes = {}
    seen_phashes = []
    counts = {"scanned": 0, "copied": 0, "duplicates": 0, "errors": 0}
    total = len(files)

    for index, path in enumerate(files, 1):
        counts["scanned"] += 1
        if progress_cb:
            progress_cb(index, total, path.name)
        try:
            digest = sha256_file(path)
            duplicate = digest in seen_hashes
            category = "Unsorted"
            if not duplicate:
                seen_hashes[digest] = path
                if path.suffix.lower() in IMAGE_EXTS:
                    category = classify_image(path, api_key, use_online)
                    ph = image_phash(path)
                    if ph is not None:
                        for old_hash, old_path in seen_phashes:
                            if ph - old_hash <= 4:
                                duplicate = True
                                break
                        seen_phashes.append((ph, path))
                else:
                    sheet = make_video_contact_sheet(path)
                    if sheet:
                        category = classify_image(sheet, api_key, use_online)
                        try: sheet.unlink(missing_ok=True)
                        except Exception: pass
                    else:
                        category = classify_video(path, api_key, use_online)

            if duplicate:
                counts["duplicates"] += 1
                if copy_duplicates:
                    target_dir = destination / "Duplicates_Review"
                    target_dir.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(path, safe_copy_name(target_dir / path.name))
                    counts["copied"] += 1
                continue

            kind = "Photos" if path.suffix.lower() in IMAGE_EXTS else "Videos"
            target_dir = destination / kind / category
            target_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, safe_copy_name(target_dir / path.name))
            counts["copied"] += 1
        except Exception:
            counts["errors"] += 1
    return counts
