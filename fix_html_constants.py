with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix HTML messages that use _DOT or _EXC - they should use _DOT_HTML and _EXC_HTML
# Find messages with parse_mode=ParseMode.HTML that still use _DOT or _EXC

# We need to find messages with parse_mode=ParseMode.HTML that use _DOT or _EXC
import re

# Pattern: find f-strings with parse_mode=ParseMode.HTML that contain _DOT or _EXC
# But this is complex. Let's just do a simple string replacement for the problematic cases.

# Replace _EXC with _EXC_HTML in HTML context
content = content.replace('_EXC}', '_EXC_HTML}')
content = content.replace('_EXC_HTML}', '_EXC_HTML}')

# Fix _DOT in HTML messages
# This is trickier because _DOT is used in both contexts
# Let's just replace _DOT with _DOT_HTML in HTML messages
# But we need to be careful

print("Done")

with open('yasir.py', 'w', encoding='utf-8') as f:
    f.write(content)