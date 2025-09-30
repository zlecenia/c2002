"""
Remove duplicate/broken route handlers from main.py
"""

def remove_broken_routes():
    """Remove broken route handlers that conflict with module routers"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    new_lines = []
    skip_next_lines = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this is a broken route handler
        if '@app.get("/connect-plus"' in line or \
           '@app.get("/connect-manager"' in line or \
           '@app.get("/fleet-data-manager"' in line or \
           '@app.get("/fleet-workshop-manager"' in line or \
           '@app.get("/fleet-config-manager"' in line or \
           '@app.get("/fleet-software-manager"' in line:
            # Skip this decorator and the next function definition
            print(f"Removing broken route at line {i+1}: {line.strip()}")
            i += 1
            # Skip the function definition line
            if i < len(lines) and 'async def' in lines[i]:
                print(f"  Removing function: {lines[i].strip()}")
                i += 1
                # Skip the return line
                if i < len(lines) and 'return' in lines[i]:
                    print(f"  Removing return: {lines[i].strip()}")
                    i += 1
                # Skip empty lines after
                while i < len(lines) and lines[i].strip() == '':
                    i += 1
                # Skip comment line if present
                if i < len(lines) and lines[i].strip().startswith('#'):
                    i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    # Write cleaned file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ Removed broken routes from main.py")
    print(f"Lines: {len(lines)} → {len(new_lines)}")

if __name__ == "__main__":
    try:
        remove_broken_routes()
        print("\n✅ main.py is now clean!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
