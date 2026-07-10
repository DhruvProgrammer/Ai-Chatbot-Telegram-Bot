import re

with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the escape_html function - look for the problematic replace lines
idx = content.find('.replace(\'"\', """")')
if idx >= 0:
    print(f"Found problematic replace at index {idx}")
    # Show context
    print(content[idx-100:idx+100])
else:
    print("Not found with that search")
    # Try alternative search
    idx = content.find('.replace(\'"\',')
    if idx >= 0:
        print(f"Found at {idx}")
        print(content[idx-50:idx+100])
    else:
        # Try to find the escape_html function
        idx = content.find('def escape_html')
        if idx >= 0:
            print(f"Found escape_html at {idx}")
            print(content[idx:idx+500])
        else:
            print("escape_html not found")