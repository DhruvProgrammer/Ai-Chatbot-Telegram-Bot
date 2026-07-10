with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The issue is with the escape_html function - the triple quotes are causing issues
# Let's find and replace it properly using a more robust approach
import re

# Find the escape_html function and replace it entirely
pattern = r'def escape_html\(text: str\) -> str:.*?\.replace\(.+?\)\)'
match = re.search(r'def escape_html\(text: str\) -> str:.*?\.replace\(.+?\)\)', content, re.DOTALL)
if match:
    print("Found at:", match.start())
    print(match.group()[:300])

# Replace the entire function
old_func = '''def escape_html(text: str) -> str:
    """Escape special characters for Telegram HTML."""
    if not text:
        return ""
    return (text
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', """)
        .replace("'", "'"))'''

new_func = '''def escape_html(text: str) -> str:
    """Escape special characters for Telegram HTML."""
    if not text:
        return ""
    return (text
        .replace("&", "&")
        .replace("<", "<")
        .replace(">", ">")
        .replace('"', """)
        .replace("'", "'"))'''

if old_func in content:
    content = content.replace(old_func, new_func)
    with open('yasir.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Fixed!")
else:
    print("Not found with exact match")
    # Try to find the function with regex
    import re
    matches = re.findall(r'def escape_html\(text: str\) -> str:.*?\.replace\("'", content, re.DOTALL)
    if matches:
        print("Found with partial match")
    else:
        print("Not found with partial match")
        # Try to find the exact bytes
        idx = content.find('.replace(\'"\', """)')
        if idx >= 0:
            print(f"Found at index {idx}")
        else:
            print("Not found at all")