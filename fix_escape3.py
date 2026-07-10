import re

with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The problematic code has """ in the replace which breaks the string
# Find and fix the escape_html function
idx = content.find('""")')
if idx >= 0:
    print(f"Found problematic at {idx}")
    print(content[idx-200:idx+100])

# Fix the escape_html function - replace the whole function
old = '''def escape_html(text: str) -> str:
    """Escape special characters for Telegram HTML."""
    if not text:
        return ""
    return (text
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', """)
        .replace("'", "'"))'''

new = '''def escape_html(text: str) -> str:
    """Escape special characters for Telegram HTML."""
    if not text:
        return ""
    return (text
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', """)
        .replace("'", "'"))'''

with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

if old in content:
    content = content.replace(old, new)
    with open('yasir.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Old pattern not found")
    # Try to find with regex
    import re
    # Find the escape_html function
    matches = list(re.finditer(r'def escape_html\(text: str\) -> str:.*?\)', content, re.DOTALL))
    for m in matches:
        print(f"Found at {m.start()}: {m.group()[:200]}")
        print("---")