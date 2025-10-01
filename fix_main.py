"""
Fix main.py by removing leftover code fragments
"""

def fix_main_py():
    """Remove leftover fragments from main.py after cleanup"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_until_next_function = False
    
    for i, line in enumerate(lines):
        # Skip empty docstrings and orphaned code
        if line.strip() in ['"""', "'''"]:
            # Check if this is an orphaned docstring (not part of a function)
            # Look back to see if there's a function definition recently
            is_orphaned = True
            for j in range(max(0, i-10), i):
                if lines[j].strip().startswith('def ') or lines[j].strip().startswith('async def '):
                    is_orphaned = False
                    break
            
            if is_orphaned:
                print(f"Removing orphaned docstring at line {i+1}")
                continue
        
        # Skip orphaned return statements
        if 'return f.read()' in line and not any('def ' in lines[j] for j in range(max(0, i-20), i)):
            print(f"Removing orphaned return at line {i+1}: {line.strip()}")
            continue
        
        new_lines.append(line)
    
    # Write fixed file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Fixed main.py - removed orphaned fragments")
    print(f"Lines: {len(lines)} → {len(new_lines)}")

if __name__ == "__main__":
    try:
        fix_main_py()
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
