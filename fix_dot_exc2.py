with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix HTML messages that use _DOT/_EXC - they should use _DOT_HTML and _EXC_HTML
# This is a targeted fix for the patterns we know are problematic

replacements = [
    # Fix authorize/deauthorize messages that use _DOT with HTML parse_mode
    ('{_DOT}", parse_mode=ParseMode.HTML', '{_DOT_HTML}", parse_mode=ParseMode.HTML'),
    ('{_EXC}", parse_mode=ParseMode.HTML', '{_EXC_HTML}", parse_mode=ParseMode.HTML'),
    ('{_DOT}", parse_mode=ParseMode.HTML', '{_DOT_HTML}", parse_mode=ParseMode.HTML'),
    ('{_EXC}", parse_mode=ParseMode.HTML', '{_EXC_HTML}", parse_mode=ParseMode.HTML'),
]

fixed = 0
for old, new in replacements:
    count = content.count(old)
    if count > 0:
        content = content.replace(old, new)
        fixed += count
        print(f"Fixed {count}: {old} -> {new}")

with open('yasir.py', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Fixed {fixed} occurrences")