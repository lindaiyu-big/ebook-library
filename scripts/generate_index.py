#!/usr/bin/env python3
import os
import json
import hashlib
from datetime import datetime

REPO_OWNER = "lindaiyu-big"
REPO_NAME = "ebook-library"
BRANCH = "main"
TEXTS_DIR = "texts"

BASE_RAW_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}"


def file_to_url(path):
    path = path.replace("\\", "/")
    return f"{BASE_RAW_URL}/{path}"


def get_summary(md_path, limit=300):
    try:
        with open(md_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read().strip()
            summary = content[:limit].replace("\n", " ").strip()
            if len(content) > limit:
                summary += "..."
            return summary
    except Exception:
        return ""


def get_images_in_dir(directory):
    image_files = []
    for name in sorted(os.listdir(directory)):
        full_path = os.path.join(directory, name)
        if os.path.isfile(full_path) and name.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            rel_path = full_path.replace("\\", "/")
            image_files.append({
                "name": name,
                "url": file_to_url(rel_path)
            })
    return image_files


def scan_library():
    books_map = {}

    for category in sorted(os.listdir(TEXTS_DIR)):
        category_path = os.path.join(TEXTS_DIR, category)
        if not os.path.isdir(category_path):
            continue

        for book_name in sorted(os.listdir(category_path)):
            book_path = os.path.join(category_path, book_name)
            if not os.path.isdir(book_path):
                continue

            book_rel_path = book_path.replace("\\", "/")
            book_id = hashlib.md5(book_rel_path.encode()).hexdigest()[:10]

            chapters = []

            for chapter_name in sorted(os.listdir(book_path)):
                chapter_path = os.path.join(book_path, chapter_name)
                if not os.path.isdir(chapter_path):
                    continue

                md_files = [
                    f for f in sorted(os.listdir(chapter_path))
                    if f.lower().endswith(".md")
                ]

                if not md_files:
                    continue

                # 默认取该章节目录下第一个 md 文件作为章节正文
                md_filename = md_files[0]
                md_path = os.path.join(chapter_path, md_filename)
                stat = os.stat(md_path)

                images = get_images_in_dir(chapter_path)

                chapters.append({
                    "chapter_title": os.path.splitext(md_filename)[0],
                    "chapter_dir": chapter_name,
                    "format": "md",
                    "size_kb": round(stat.st_size / 1024, 1),
                    "url": file_to_url(md_path),
                    "summary": get_summary(md_path),
                    "has_images": len(images) > 0,
                    "image_count": len(images),
                    "images": images
                })

            if not chapters:
                continue

            books_map[book_id] = {
                "id": book_id,
                "title": book_name,
                "category": category,
                "path": book_rel_path,
                "chapter_count": len(chapters),
                "chapters": chapters
            }

    return list(books_map.values())


def main():
    books = scan_library()

    index = {
        "library_name": "AI Ebook Library",
        "description": "AI可直接访问的电子书库，按整本书索引，章节作为子项",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_books": len(books),
        "books": books
    }

    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"Generated index.json with {len(books)} books")


if __name__ == "__main__":
    main()
