"""
Enhanced Code Validator - Advanced Safety and Quality Checks
"""
import ast
import re
from typing import Tuple, List, Optional
import logging

logger = logging.getLogger(__name__)


class EnhancedCodeValidator:
    """Enhanced code validation with comprehensive safety checks"""
    
    FORBIDDEN_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'pickle', 'shelve', 'marshal', 'eval', 'exec', 'compile',
        '__import__', 'importlib', 'ctypes', 'multiprocessing'
    }
    
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'compile', '__import__', 'open', 'input',
        'execfile', 'reload', 'vars', 'locals', 'globals', 'dir',
        'getattr', 'setattr', 'delattr', 'hasattr'
    }
    
    ALLOWED_IMPORTS = {
        'pandas', 'numpy', 'scipy', 'matplotlib', 'seaborn', 'plotly',
        'sklearn', 'statsmodels', 'math', 'statistics', 'datetime',
        'collections', 'itertools', 'functools', 'warnings'
    }
    
    @staticmethod
    def validate_and_sanitize(code: str) -> Tuple[str, bool, Optional[str]]:
        """
        Comprehensive validation with multiple security layers
        
        Returns:
            (sanitized_code, is_valid, error_message)
        """
        try:
            # Layer 1: Basic sanitization
            code = EnhancedCodeValidator._sanitize_basic(code)
            
            # Layer 2: Security checks
            is_safe, error = EnhancedCodeValidator._check_security(code)
            if not is_safe:
                return code, False, f"Security violation: {error}"
            
            # Layer 3: Syntax validation
            is_valid_syntax, error = EnhancedCodeValidator._validate_syntax(code)
            if not is_valid_syntax:
                return code, False, f"Syntax error: {error}"
            
            # Layer 4: AST analysis
            is_safe_ast, error = EnhancedCodeValidator._analyze_ast(code)
            if not is_safe_ast:
                return code, False, f"Unsafe operation: {error}"
            
            # Layer 5: Quality checks
            warnings = EnhancedCodeValidator._check_quality(code)
            if warnings:
                logger.warning(f"Code quality warnings: {warnings}")
            
            # Layer 6: Add safety wrapper
            safe_code = EnhancedCodeValidator._add_safety_wrapper(code)
            
            return safe_code, True, None
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return code, False, str(e)
    
    @staticmethod
    def _sanitize_basic(code: str) -> str:
        """Basic sanitization"""
        # Remove markdown code blocks
        code = re.sub(r'```python\n?', '', code)
        code = re.sub(r'```\n?', '', code)
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        # Remove dangerous patterns
        code = re.sub(r'__\w+__', '', code)  # Remove dunder methods
        
        return code
    
    @staticmethod
    def _check_security(code: str) -> Tuple[bool, Optional[str]]:
        """Security checks using pattern matching"""
        
        # Check for forbidden imports
        for forbidden in EnhancedCodeValidator.FORBIDDEN_IMPORTS:
            if re.search(rf'\bimport\s+{forbidden}\b', code):
                return False, f"Forbidden import: {forbidden}"
            if re.search(rf'\bfrom\s+{forbidden}\b', code):
                return False, f"Forbidden import: {forbidden}"
        
        # Check for forbidden functions
        for forbidden in EnhancedCodeValidator.FORBIDDEN_FUNCTIONS:
            if re.search(rf'\b{forbidden}\s*\(', code):
                return False, f"Forbidden function: {forbidden}"
        
        # Check for file operations
        if re.search(r'\bopen\s*\(.*[\'"]w[\'"]', code):
            return False, "File write operations not allowed"
        
        # Check for shell commands
        if re.search(r'os\.system|subprocess\.|shell=True', code):
            return False, "Shell commands not allowed"
        
        # Check for network operations
        if re.search(r'requests\.|urllib\.|socket\.|http\.', code):
            return False, "Network operations not allowed"
        
        return True, None
    
    @staticmethod
    def _validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
        """Validate Python syntax"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _analyze_ast(code: str) -> Tuple[bool, Optional[str]]:
        """Deep AST analysis for unsafe operations"""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Check for dangerous calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in EnhancedCodeValidator.FORBIDDEN_FUNCTIONS:
                            return False, f"Forbidden function call: {node.func.id}"
                
                # Check for attribute access to forbidden modules
                if isinstance(node, ast.Attribute):
                    if isinstance(node.value, ast.Name):
                        if node.value.id in EnhancedCodeValidator.FORBIDDEN_IMPORTS:
                            return False, f"Access to forbidden module: {node.value.id}"
                
                # Check for exec/eval in any form
                if isinstance(node, ast.Expr):
                    if isinstance(node.value, ast.Call):
                        if isinstance(node.value.func, ast.Name):
                            if node.value.func.id in ['eval', 'exec']:
                                return False, "Dynamic code execution not allowed"
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def _check_quality(code: str) -> List[str]:
        """Code quality checks"""
        warnings = []
        
        # Check for common issues
        if 'df = ' in code and 'df[' in code:
            warnings.append("Possible dataframe reassignment detected")
        
        if code.count('for ') > 3:
            warnings.append("Multiple loops detected - consider vectorization")
        
        if 'import *' in code:
            warnings.append("Wildcard imports not recommended")
        
        if len(code.split('\n')) > 200:
            warnings.append("Code is very long - consider breaking into functions")
        
        return warnings
    
    @staticmethod
    def _add_safety_wrapper(code: str) -> str:
        """Add comprehensive error handling"""
        
        wrapper = f"""# Auto-generated safety wrapper
import warnings
warnings.filterwarnings('ignore')

try:
    # Input validation
    if df is None or len(df) == 0:
        raise ValueError("DataFrame is empty or None")
    
    # User code
{EnhancedCodeValidator._indent_code(code, 4)}
    
    # Success marker
    _execution_success = True
    
except Exception as e:
    _execution_success = False
    _error_message = str(e)
    print(f"Execution error: {{_error_message}}")
    import traceback
    traceback.print_exc()
"""
        return wrapper
    
    @staticmethod
    def _indent_code(code: str, spaces: int) -> str:
        """Indent code by specified spaces"""
        indent = ' ' * spaces
        return '\n'.join(indent + line if line.strip() else line 
                        for line in code.split('\n'))
    
    @staticmethod
    def extract_code_blocks(text: str) -> List[str]:
        """Extract code blocks from text"""
        # Try markdown code blocks first
        pattern = r'```(?:python)?\n(.*?)```'
        blocks = re.findall(pattern, text, re.DOTALL)
        
        if blocks:
            return blocks
        
        # If no markdown blocks, return entire text
        return [text]
    
    @staticmethod
    def validate_imports(code: str) -> Tuple[bool, List[str]]:
        """Validate all imports are allowed"""
        try:
            tree = ast.parse(code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split('.')[0])
            
            # Check if all imports are allowed
            forbidden = set(imports) & EnhancedCodeValidator.FORBIDDEN_IMPORTS
            if forbidden:
                return False, list(forbidden)
            
            return True, imports
            
        except Exception as e:
            logger.error(f"Import validation error: {e}")
            return False, []
