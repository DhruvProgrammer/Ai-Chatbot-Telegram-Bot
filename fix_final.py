with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The issue is in escape_html function - it has """ which breaks the string
# Replace the entire escape_html function
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
    print("Pattern not found exactly")
    # Let's try to find the actual content
    idx = content.find('.replace')
    while idx >= 0:
        if 'def escape_html' in content[max(0,idx-200):idx]:
            print(f"Found at {idx}: {content[idx:idx+100]}")
            break
        idx = content.find('.replace', idx+1)