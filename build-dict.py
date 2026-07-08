import lzma
import json
import urllib.request
import re

url = "https://raw.githubusercontent.com/g0v/moedict-data/master/dict-revised.json.xz"
print("Downloading dict-revised.json.xz from g0v...")
response = urllib.request.urlopen(url)
compressed_data = response.read()

print("Decompressing xz data...")
data = lzma.decompress(compressed_data)

print("Parsing JSON...")
moedict = json.loads(data)

print("Extracting title and bopomofo...")
out = {}
for entry in moedict:
    title = entry.get('title')
    heteronyms = entry.get('heteronyms', [])
    if title and heteronyms:
        # Take the first heteronym (most common pronunciation)
        bopomofo = heteronyms[0].get('bopomofo')
        if bopomofo:
            # Clean up unwanted characters:
            # 1. Remove zero-width spaces (\u200b)
            bopomofo = bopomofo.replace('\u200b', '')
            
            # 2. Extract from HTML tags if present (e.g. <ruby>...)
            # Moedict sometimes uses HTML for bopomofo structure, sometimes just plain text.
            # Usually 'bopomofo' field is plain string like "ㄆㄧㄥˊ ㄍㄨㄛˇ"
            # But just in case, we will strip tags if any exist (though rare in the plain 'bopomofo' field).
            bopomofo = re.sub(r'<[^>]+>', '', bopomofo)

            # 3. Clean up (變) formatting etc.
            bopomofo = re.sub(r'\(.*?\)', '', bopomofo).strip()
            
            # 4. Remove extra spaces between characters to keep it clean (though moedict has spaces between syllables, which we might want to keep for formatting).
            # Actually, spaces between syllables are useful for splitting. We will keep them.
            
            if bopomofo:
                out[title] = bopomofo

with open('dict-zhuyin.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))

print(f"Done. Extracted {len(out)} entries. Saved to dict-zhuyin.json")
