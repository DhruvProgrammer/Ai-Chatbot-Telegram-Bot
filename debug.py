with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic line
idx = content.find('.replace(\'"\', """")')
if idx >= 0:
    print(f"Found at {idx}")
    print(repr(content[idx-50:idx+50]))
else:
    print("Not found with that exact search")
    
# Let's look at the escape_html function
idx = content.find('def escape_html')
if idx >= 0:
    print(f"\nFound escape_html at {idx}")
    print(content[idx:idx+500])