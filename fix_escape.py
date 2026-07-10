with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the escape_html function
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

if old in content:
    content = content.replace(old, new)
    with open('yasir.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Old not found")
    # Try to find it with regex
    import re
    pattern = r'def escape_html\(text: str\) -> str:.*?\.replace\(.+\)\)'
    match = re.search(r'def escape_html\(text: str\) -> str:.*?\.replace\(.+\)\)', content, re.DOTALL)
    if match:
        print("Found with regex")
        print(match.group()[:300])
    else:
        print("Not found with regex either")