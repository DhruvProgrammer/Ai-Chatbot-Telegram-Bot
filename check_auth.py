with open('yasir.py', 'r', encoding='utf-8') as f:
    content = f.read()

# The authorize function got mangled. Let me rewrite the entire authorize function properly.
# First, find the exact section to replace.

# Find the start of cmd_authorize
start = content.find('async def cmd_authorize(message: Message):')
if start < 0:
    print("Could not find cmd_authorize")
else:
    # Find the end - it's before cmd_deauthorize
    end = content.find('async def cmd_deauthorize')
    if end < 0:
        end = content.find('async def cmd_settings')
    
    old_function = content[start:end]
    print(f"Found authorize function from {start} to {end}, length {len(old_function)}")
    print("First 500 chars:")
    print(old_function[:500])
    print("---")
    print("Last 500 chars:")
    print(old_function[-500:])