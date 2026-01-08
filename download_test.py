# download_test.py
import requests

print("Testing JSON download availability...")
print("="*50)

urls_to_test = [
    ("2025 Edition", "https://en-word.net/downloads/english-wordnet-2025.json"),
    ("2025 Plus", "https://en-word.net/downloads/english-wordnet-2025-plus.json"),
    ("2025 Edition (alt)", "https://en-word.net/static/english-wordnet-2025.json"),
    ("2025 Plus (alt)", "https://en-word.net/static/english-wordnet-2025-plus.json"),
]

for name, url in urls_to_test:
    print(f"\nTesting {name}:")
    print(f"  URL: {url}")
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            print(f"  ✓ Available (200 OK)")
            # Try to get file size
            try:
                size = int(response.headers.get('content-length', 0))
                if size:
                    print(f"  Size: {size:,} bytes ({size/1024/1024:.1f} MB)")
            except:
                pass
        else:
            print(f"  ✗ Not available ({response.status_code})")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n" + "="*50)
print("Summary: Check which URLs actually work.")