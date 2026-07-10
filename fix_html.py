import re

with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the escape_html function - it has incorrect replace calls
old = '''def escape_html(text: str) -> str:
    """Escape special characters for Telegram HTML."""
    if not text:
        return ""
    return text.replace("&", "&").replace("<", "<").replace(">", ">").replace('"', """).replace("'", "'")'''

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
    print('Fixed!')
else:
    print('Pattern not found')
    # Search for the function
    for m in __import__('re').finditer(r'def escape_html', content):
        print(f'Found at {m.start()}: {content[m.start():m.start()+300]}')