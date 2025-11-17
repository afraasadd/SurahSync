"""
SurahSync backend core logic module
- Fetch & save Quran dataset (JSON)
- Load dataset from disk
- load_surah(surah_num)
- pick_random_ayah(surah_num=None)
- get_ayah_text(surah_num, ayah_num)
- compare_texts(user_text, correct_text, method='difflib'|'levenshtein')
- normalize_arabic(text) to remove diacritics/punctuations/extra spaces
"""

import requests
import json
import csv
import random
import re
from difflib import SequenceMatcher

# Optional: faster Levenshtein ratio if installed
try:
    import Levenshtein  # from python-Levenshtein
    HAVE_LEV = True
except Exception:
    HAVE_LEV = False

# CHANGEABLE: dataset URL (CDN JSON). If it fails, replace with another working JSON source.
DATASET_URL = "https://cdn.jsdelivr.net/npm/quran-json@3.1.2/dist/quran.json"
LOCAL_JSON = "quran.json"
LOCAL_CSV = "quran_flat.csv"

# Arabic diacritics/marks unicode ranges commonly used
_ARABIC_DIACRITICS_PATTERN = re.compile(
    "[" +
    "\u0610-\u061A" +  # Arabic signs
    "\u064B-\u065F" +  # harakat
    "\u06D6-\u06ED" +  # surah decorations
    "]+")


# Basic punctuation to remove (including Arabic punctuation)
_PUNCTUATION_PATTERN = re.compile(r"[^\w\s\u0600-\u06FF]")  # keep Arabic letters+numbers+space


def fetch_and_save_dataset(url: str = DATASET_URL, save_path: str = LOCAL_JSON) -> dict:
    """
    Fetch dataset from `url` and save locally to save_path.
    Returns parsed JSON as Python object on success.
    """
    print(f"Fetching dataset from: {url}")
    resp = requests.get(url, timeout=20)
    resp.raise_for_status()
    data = resp.json()
    # Some JSON formats are array of surahs; some wrap in {data:...}. Normalize:
    if isinstance(data, dict) and "data" in data:
        payload = data["data"]
    else:
        payload = data
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"Saved dataset to {save_path}")
    return payload


def load_dataset(path: str = LOCAL_JSON) -> dict:
    """
    Load dataset from local JSON file.
    Returns the loaded data (list or dict, depending on file shape).
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def flatten_to_csv(data, csv_path: str = LOCAL_CSV):
    """
    Save a flattened CSV with columns:
    surah_number, surah_name, ayah_number, ayah_text
    Works for dataset shapes where data is list-like of surah objects with 'verses' or 'ayahs'.
    """
    rows = []
    # attempt to detect structure
    surahs = data if isinstance(data, list) else (data.get("surahs") or data.get("chapters") or data)
    for s in surahs:
        s_num = s.get("number") or s.get("chapter") or s.get("chapter_number") or None
        s_name = s.get("englishName") or s.get("name") or s.get("chapterName") or ""
        ayahs = s.get("ayahs") or s.get("verses") or s.get("ayah")
        if not ayahs:
            continue
        for a in ayahs:
            a_num = a.get("numberInSurah") or a.get("number") or a.get("verse") or a.get("verse_number")
            a_text = a.get("text") or a.get("verse") or ""
            rows.append((s_num, s_name, a_num, a_text))
    # write CSV
    with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["surah_number", "surah_name", "ayah_number", "ayah_text"])
        writer.writerows(rows)
    print(f"Flattened CSV saved to {csv_path}. Total rows: {len(rows)}")


def _get_surahs_list(data):
    """
    Normalize dataset to return list of surah objects.
    Some datasets are top-level list; others have 'surahs' key; others 'chapters'.
    """
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("surahs", "chapters", "chapters_list", "quran"):
            if key in data:
                return data[key]
        # Fallback: maybe data is mapping of chapters by number
        # try to create list sorted by number
        try:
            items = sorted(data.values(), key=lambda x: int(x.get("number", 0)))
            return items
        except Exception:
            pass
    raise ValueError("Unrecognized dataset structure: cannot find surah list")


def load_surah(data, surah_number: int):
    """
    Return surah object for surah_number (1-based).
    """
    surahs = _get_surahs_list(data)
    # find by number field or by position
    for s in surahs:
        num = s.get("number") or s.get("chapterNumber") or s.get("chapter")
        if num:
            try:
                if int(num) == int(surah_number):
                    return s
            except Exception:
                pass
    # fallback: index-based
    idx = surah_number - 1
    if 0 <= idx < len(surahs):
        return surahs[idx]
    raise IndexError(f"Surah {surah_number} not found")


def get_ayah_text(data, surah_number: int, ayah_number: int) -> str:
    """
    Return the Arabic text for a given surah and ayah (both 1-based).
    """
    s = load_surah(data, surah_number)
    ayahs = s.get("ayahs") or s.get("verses") or s.get("ayah")
    if not ayahs:
        raise ValueError("Surah data does not contain ayahs/verses")
    # many formats store 'number' as global number; some store 'numberInSurah'
    for a in ayahs:
        # try common fields
        for key in ("numberInSurah", "verse", "ayah_number", "verse_number", "number"):
            if key in a:
                try:
                    if int(a[key]) == int(ayah_number):
                        return a.get("text") or next(iter(a.values()))
                except Exception:
                    pass
    # fallback by index
    idx = ayah_number - 1
    if 0 <= idx < len(ayahs):
        return ayahs[idx].get("text") or ""
    raise IndexError(f"Ayah {ayah_number} in Surah {surah_number} not found")


def pick_random_ayah(data, surah_number: int = None):
    """
    Pick a random ayah.
    If surah_number is provided, choose from that surah only.
    Returns tuple: (surah_number, ayah_number, ayah_text)
    """
    surahs = _get_surahs_list(data)
    if surah_number is None:
        s = random.choice(surahs)
    else:
        s = load_surah(data, surah_number)
    s_num = s.get("number") or s.get("chapter") or None
    ayahs = s.get("ayahs") or s.get("verses") or s.get("ayah")
    if not ayahs:
        raise ValueError("No ayahs found in chosen surah")
    a = random.choice(ayahs)
    # determine ayah number in surah
    ayah_num = None
    for key in ("numberInSurah", "verse", "ayah_number", "verse_number", "number"):
        if key in a:
            try:
                ayah_num = int(a[key])
                break
            except Exception:
                pass
    if ayah_num is None:
        # fallback to index
        ayah_num = ayahs.index(a) + 1
    return int(s_num) if s_num else None, ayah_num, a.get("text") or ""


# ------------ Text normalization & comparison helpers ---------------

def normalize_arabic(text: str) -> str:
    """
    Normalize Arabic text for comparison:
    - remove diacritics (tashkeel)
    - remove punctuation
    - collapse whitespace
    """
    if text is None:
        return ""
    text = str(text)
    # remove diacritics
    text = _ARABIC_DIACRITICS_PATTERN.sub("", text)
    # remove punctuation except Arabic letters/numbers/space
    text = _PUNCTUATION_PATTERN.sub("", text)
    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def similarity_difflib(a: str, b: str) -> float:
    """
    Return ratio in [0,1] using difflib.SequenceMatcher
    """
    return SequenceMatcher(None, a, b).ratio()


def similarity_levenshtein(a: str, b: str) -> float:
    """
    Return ratio in [0,1] using python-Levenshtein if available,
    else fallback to difflib.
    """
    if HAVE_LEV:
        # Levenshtein.ratio gives 0..1
        return Levenshtein.ratio(a, b)
    else:
        return similarity_difflib(a, b)


def compare_texts(user_text: str, correct_text: str, method: str = "difflib") -> dict:
    """
    Compare user_text vs correct_text after normalization.
    method: 'difflib' or 'levenshtein' (will fallback to difflib if Levenshtein unavailable)
    Returns dict:
      {
        'normalized_user': ...,
        'normalized_correct': ...,
        'similarity': float (0..1),
        'match_percent': int (0..100)
      }
    """
    u = normalize_arabic(user_text)
    c = normalize_arabic(correct_text)
    if method == "levenshtein":
        sim = similarity_levenshtein(u, c)
    else:
        sim = similarity_difflib(u, c)
    return {
        "normalized_user": u,
        "normalized_correct": c,
        "similarity": sim,
        "match_percent": int(round(sim * 100))
    }


# ------------------ Demo / quick test --------------------
if __name__ == "__main__":
    # 1) Fetch dataset if not present
    try:
        data = load_dataset(LOCAL_JSON)
        print("Loaded local dataset:", LOCAL_JSON)
    except FileNotFoundError:
        print("Local dataset not found, fetching from web...")
        data = fetch_and_save_dataset()

    # 2) Show quick info
    try:
        surahs = _get_surahs_list(data)
        print(f"Total surahs loaded: {len(surahs)}")
    except Exception as e:
        print("Could not detect surahs list:", e)
        raise

    # 3) pick a random ayah
    s_num, a_num, text = pick_random_ayah(data)
    print(f"\nRandom Ayah -> Surah {s_num}, Ayah {a_num}:\n{text}\n")

    # 4) example compare
    user_sample = text  # perfect match test
    res = compare_texts(user_sample, text, method="difflib")
    print("Comparison (perfect):", res)

    # 5) example with slight difference
    user_sample2 = text.replace("اللَّهِ", "الله")  # small change
    res2 = compare_texts(user_sample2, text, method="difflib")
    print("Comparison (small change):", res2)
