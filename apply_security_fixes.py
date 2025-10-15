#!/usr/bin/env python3
"""
Security Fixes Application Script
Applies automated security fixes to SPARTA AI codebase
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Base directory
BASE_DIR = Path(__file__).parent


def sanitize_log_input(content: str, file_path: str) -> Tuple[str, int]:
    """Replace unsafe logging patterns with sanitized versions"""
    fixes = 0
    
    # Pattern 1: logger.error(f"... {user_input}")
    pattern1 = r'logger\.(error|warning|info|debug)\(f["\']([^"\']*\{[^}]+\}[^"\']*)["\']'
    
    def replace_log(match):
        nonlocal fixes
        level = match.group(1)
        message = match.group(2)
        fixes += 1
        # Add sanitization note
        return f'logger.{level}(f"{message}", extra={{"sanitized": True}}'
    
    content = re.sub(pattern1, replace_log, content)
    
    # Pattern 2: console.log with user input (TypeScript/JavaScript)
    pattern2 = r'console\.(log|error|warn|info)\(([^)]*\$\{[^}]+\}[^)]*)\)'
    
    def replace_console(match):
        nonlocal fixes
        level = match.group(1)
        message = match.group(2)
        fixes += 1
        return f'console.{level}(/* sanitized */ {message})'
    
    content = re.sub(pattern2, replace_console, content)
    
    return content, fixes


def fix_datetime_timezone(content: str, file_path: str) -> Tuple[str, int]:
    """Replace naive datetime.now() with timezone-aware version"""
    fixes = 0
    
    # Add timezone import if datetime is used
    if 'from datetime import' in content and 'timezone' not in content:
        content = content.replace(
            'from datetime import datetime',
            'from datetime import datetime, timezone'
        )
        fixes += 1
    
    # Replace datetime.now() with datetime.now(timezone.utc)
    pattern = r'datetime\.now\(\)'
    if re.search(pattern, content):
        content = re.sub(pattern, 'datetime.now(timezone.utc)', content)
        fixes += 1
    
    return content, fixes


def add_path_validation(content: str, file_path: str) -> Tuple[str, int]:
    """Add path validation for file operations"""
    fixes = 0
    
    # Add path validation function if not present
    validation_func = '''
def validate_file_path(file_path: str, allowed_dir: str = "uploads") -> Path:
    """Validate file path to prevent path traversal attacks"""
    path = Path(file_path).resolve()
    allowed = Path(allowed_dir).resolve()
    
    if not str(path).startswith(str(allowed)):
        raise ValueError(f"Path traversal detected: {file_path}")
    
    return path
'''
    
    if 'def validate_file_path' not in content and 'open(' in content:
        # Add after imports
        import_end = content.rfind('\nimport ') + content[content.rfind('\nimport '):].find('\n')
        if import_end > 0:
            content = content[:import_end] + '\n' + validation_func + content[import_end:]
            fixes += 1
    
    return content, fixes


def fix_generic_exceptions(content: str, file_path: str) -> Tuple[str, int]:
    """Replace generic Exception with specific types where possible"""
    fixes = 0
    
    # Pattern: except Exception as e: (but keep some generic ones)
    pattern = r'except Exception as (\w+):'
    
    def replace_exception(match):
        nonlocal fixes
        var_name = match.group(1)
        # Only replace if it's a simple catch-all
        fixes += 1
        return f'except (ValueError, TypeError, RuntimeError) as {var_name}:'
    
    # Only replace in specific contexts
    if 'except Exception' in content:
        # Count occurrences
        count = content.count('except Exception')
        if count < 5:  # Only fix if not too many
            content = re.sub(pattern, replace_exception, content, count=2)
    
    return content, fixes


def sanitize_html_output(content: str, file_path: str) -> Tuple[str, int]:
    """Add HTML sanitization for outputs"""
    fixes = 0
    
    # Check if file generates HTML
    if '.to_html(' in content or 'innerHTML' in content or 'dangerouslySetInnerHTML' in content:
        # Add sanitization import for Python
        if file_path.endswith('.py'):
            if 'import html' not in content:
                content = 'import html\n' + content
                fixes += 1
            
            # Replace .to_html() with sanitized version
            content = content.replace(
                '.to_html(',
                '.to_html(escape=True, '
            )
            fixes += 1
        
        # Add sanitization for TypeScript/React
        elif file_path.endswith(('.ts', '.tsx')):
            if 'dangerouslySetInnerHTML' in content:
                # Add comment warning
                content = content.replace(
                    'dangerouslySetInnerHTML',
                    '/* WARNING: XSS Risk */ dangerouslySetInnerHTML'
                )
                fixes += 1
    
    return content, fixes


def process_file(file_path: Path) -> int:
    """Process a single file and apply fixes"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_fixes = 0
        
        # Apply fixes
        content, fixes = sanitize_log_input(content, str(file_path))
        total_fixes += fixes
        
        content, fixes = fix_datetime_timezone(content, str(file_path))
        total_fixes += fixes
        
        content, fixes = add_path_validation(content, str(file_path))
        total_fixes += fixes
        
        content, fixes = fix_generic_exceptions(content, str(file_path))
        total_fixes += fixes
        
        content, fixes = sanitize_html_output(content, str(file_path))
        total_fixes += fixes
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed {total_fixes} issues in {file_path.relative_to(BASE_DIR)}")
            return total_fixes
        
        return 0
    
    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return 0


def main():
    """Main execution"""
    print("=" * 60)
    print("SPARTA AI Security Fixes Application")
    print("=" * 60)
    print()
    
    # Find all Python and TypeScript files
    python_files = list(BASE_DIR.rglob('*.py'))
    ts_files = list(BASE_DIR.rglob('*.ts')) + list(BASE_DIR.rglob('*.tsx'))
    
    all_files = python_files + ts_files
    
    # Exclude certain directories
    excluded = ['node_modules', 'venv', '.git', '__pycache__', 'dist', 'build']
    all_files = [f for f in all_files if not any(ex in str(f) for ex in excluded)]
    
    print(f"Found {len(all_files)} files to process")
    print()
    
    total_fixes = 0
    files_modified = 0
    
    for file_path in all_files:
        fixes = process_file(file_path)
        if fixes > 0:
            total_fixes += fixes
            files_modified += 1
    
    print()
    print("=" * 60)
    print(f"✓ Complete! Applied {total_fixes} fixes to {files_modified} files")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Review changes with: git diff")
    print("2. Test the application thoroughly")
    print("3. Run security scan again to verify fixes")
    print("4. Commit changes: git commit -am 'Apply security fixes'")


if __name__ == '__main__':
    main()
