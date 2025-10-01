"""
Final cleanup of main.py - remove all orphaned code fragments
"""

def final_cleanup():
    """Remove all remaining orphaned code from main.py"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    new_lines = []
    
    # Find the end of get_test_scenarios function
    in_orphaned_section = False
    
    for i, line in enumerate(lines):
        # Start of orphaned section - after get_test_scenarios
        if 'scenarios = db.query(TestScenario).all()' in line:
            # Add this line and the next return line
            new_lines.append(line)
            if i + 1 < len(lines):
                new_lines.append(lines[i + 1])  # return line
            in_orphaned_section = True
            continue
        
        # End of orphaned section - before if __name__
        if 'if __name__ == "__main__"' in line:
            in_orphaned_section = False
            # Add empty line before if __name__
            new_lines.append('')
        
        # Skip orphaned lines
        if in_orphaned_section:
            continue
        
        # Add non-orphaned lines
        if i > 0 and not (i >= 1 and 'scenarios = db.query(TestScenario).all()' in lines[i-1]):
            new_lines.append(line)
    
    # Write cleaned file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines))
    
    print(f"✅ Final cleanup completed")
    print(f"Original lines: {len(lines)}")
    print(f"New lines: {len(new_lines)}")
    print(f"Removed: {len(lines) - len(new_lines)} lines")

if __name__ == "__main__":
    try:
        final_cleanup()
        print("\n✅ main.py is now clean!")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
