import os
import json
import logging
import requests
from tqdm import tqdm
from time import sleep

# === CONFIGURATION ===
MAX_ID = 10000
BASE_URL = "https://www.gutenberg.org/ebooks/{}.epub3.images"
DOWNLOAD_DIR = "downloads"
PROGRESS_FILE = "progress.json"
LOG_FILE = "gutenberg_downloader.log"
USER_AGENT = "Mozilla/5.0 (compatible; ProjectGutenbergDownloader/1.0)"

# === LOGGING ===
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# === UTILITIES ===
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"last_id": 0}

def save_progress(progress):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f)

def ensure_dir():
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

def file_exists(book_id):
    path = os.path.join(DOWNLOAD_DIR, f"{book_id}.epub")
    return os.path.exists(path)

def try_download(book_id):
    url = BASE_URL.format(book_id)
    headers = {"User-Agent": USER_AGENT}
    try:
        response = requests.get(url, headers=headers, allow_redirects=True, timeout=10)
        if response.status_code == 200 and "application/epub+zip" in response.headers.get("Content-Type", ""):
            out_path = os.path.join(DOWNLOAD_DIR, f"{book_id}.epub")
            with open(out_path, "wb") as f:
                f.write(response.content)
            logging.info(f"✅ Downloaded: {book_id} from {url}")
            return True
        else:
            logging.warning(f"❌ Skipped (not found or wrong content type): {book_id} (Status {response.status_code})")
            return False
    except Exception as e:
        logging.error(f"🔥 Error downloading {book_id} from {url}: {e}")
        return False

# === MAIN LOOP ===
def main():
    ensure_dir()
    progress = load_progress()
    start_id = progress.get("last_id", 0) + 1

    logging.info(f"📘 Starting at ID {start_id}")

    for book_id in tqdm(range(start_id, MAX_ID + 1), desc="Downloading books"):
        if file_exists(book_id):
            logging.info(f"⏩ Already exists: {book_id}")
        else:
            try_download(book_id)
            sleep(1)  # polite crawling

        # Save progress every time
        progress["last_id"] = book_id
        save_progress(progress)

    logging.info("🏁 Finished run.")

if __name__ == "__main__":
    main()

