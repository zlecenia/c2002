"""
Script to remove old inline HTML functions from main.py that have been moved to modules
"""

def cleanup_main_py():
    """Remove old HTML route handlers from main.py"""
    
    with open('main.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Define line ranges to remove (1-indexed, inclusive)
    # Format: (start_line, end_line, function_name)
    ranges_to_remove = [
        (316, 523, "root() - home page"),
        (551, 849, "connect_plus()"),
        (852, 1066, "connect_display()"),
        (1069, 1986, "connect_manager()"),
        (1989, 3391, "fleet_data_manager()"),
        (3394, 5300, "fleet_config_manager()"),
        (5303, 5307, "fleet_software_manager_modular()"),
        (5310, 6550, "fleet_software_manager()"),
        (6553, 6792, "fleet_workshop_manager()"),
    ]
    
    # Sort ranges in reverse order to remove from bottom to top
    ranges_to_remove.sort(reverse=True)
    
    # Remove lines
    new_lines = lines.copy()
    for start, end, name in ranges_to_remove:
        print(f"Removing {name}: lines {start}-{end}")
        # Convert to 0-indexed
        del new_lines[start-1:end]
    
    # Add module routes import and call after line 51 (after fleet_software_router)
    # Find the line with fleet_software_router include
    insert_pos = None
    for i, line in enumerate(new_lines):
        if 'app.include_router(fleet_software_router' in line:
            insert_pos = i + 2  # Add 2 lines after
            break
    
    if insert_pos:
        # Add import and function call
        new_lines.insert(insert_pos, '\n')
        new_lines.insert(insert_pos + 1, '# Import and include module routes\n')
        new_lines.insert(insert_pos + 2, 'from modules.routes import include_module_routes\n')
        new_lines.insert(insert_pos + 3, 'include_module_routes(app)\n')
        print(f"Added module routes configuration at line {insert_pos}")
    
    # Create backup
    with open('main.py.backup', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print("✅ Created backup: main.py.backup")
    
    # Write cleaned file
    with open('main.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("✅ Cleaned main.py written")
    
    # Calculate removed lines
    original_lines = len(lines)
    new_line_count = len(new_lines)
    removed = original_lines - new_line_count
    print(f"\n📊 Statistics:")
    print(f"   Original lines: {original_lines}")
    print(f"   New lines: {new_line_count}")
    print(f"   Removed lines: {removed}")
    print(f"   Reduction: {removed/original_lines*100:.1f}%")

if __name__ == "__main__":
    try:
        cleanup_main_py()
        print("\n✅ Success! Old HTML functions removed from main.py")
        print("💾 Backup saved as main.py.backup")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
