from pathlib import Path
import base64
import io
import re
from PIL import Image

CATEGORIES = [
    "Travel", "People", "Family", "Friends", "Food", "Nature",
    "Animals", "Vehicles", "Buildings", "Documents", "Screenshots",
    "Events", "Sports", "Art", "Products", "Other"
]

def filename_fallback(path):
    name = path.stem.lower()
    rules = {
        "Screenshots": ["screenshot", "screen shot", "snip"],
        "Travel": ["travel", "trip", "tour", "beach", "cox", "sylhet"],
        "Food": ["food", "biryani", "restaurant", "lunch", "dinner"],
        "Events": ["birthday", "wedding", "party", "event", "program"],
        "Documents": ["scan", "document", "nid", "passport", "certificate"],
        "Friends": ["friend", "classmate"],
    }
    for category, words in rules.items():
        if any(word in name for word in words):
            return category
    return "Other"

def _online_classify(path, api_key):
    from openai import OpenAI
    image = Image.open(path).convert("RGB")
    image.thumbnail((1000, 1000))
    buf = io.BytesIO()
    image.save(buf, format="JPEG", quality=82)
    encoded = base64.b64encode(buf.getvalue()).decode("utf-8")
    client = OpenAI(api_key=api_key)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[{
            "role": "user",
            "content": [
                {"type": "input_text", "text":
                 "Classify this image into exactly one category from: " +
                 ", ".join(CATEGORIES) +
                 ". Reply with only the category name. Do not identify people."},
                {"type": "input_image", "image_url": f"data:image/jpeg;base64,{encoded}", "detail": "low"}
            ]
        }],
        max_output_tokens=20
    )
    answer = response.output_text.strip()
    for category in CATEGORIES:
        if category.lower() in answer.lower():
            return category
    return "Other"

def _local_clip_classify(path):
    # Optional offline AI: install torch + transformers to enable this.
    from transformers import pipeline
    global _clip_classifier
    try:
        classifier = _clip_classifier
    except NameError:
        _clip_classifier = pipeline(
            "zero-shot-image-classification",
            model="openai/clip-vit-base-patch32"
        )
        classifier = _clip_classifier
    labels = [
        "travel and vacation photos", "people and portraits", "family photos",
        "friends together", "food and meals", "nature and landscapes",
        "animals and pets", "cars and vehicles", "buildings and architecture",
        "documents and scanned pages", "computer screenshots", "events and parties",
        "sports", "art and design", "product photos", "other"
    ]
    results = classifier(str(path), candidate_labels=labels)
    best = results[0]["label"]
    mapping = dict(zip(labels, CATEGORIES))
    return mapping.get(best, "Other")

def classify_image(path, api_key="", use_online=True):
    if use_online and api_key:
        try:
            return _online_classify(path, api_key)
        except Exception:
            pass
    try:
        return _local_clip_classify(path)
    except Exception:
        return filename_fallback(Path(path))

def classify_video(path, api_key="", use_online=True):
    # The core sends a sampled-frame contact sheet through classify_image.
    return filename_fallback(Path(path))
