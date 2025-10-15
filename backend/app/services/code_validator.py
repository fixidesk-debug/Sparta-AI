"""
Code Validation and Sanitization
Ensures generated code is safe and executable
"""
import ast
import re
from typing import List, Tuple, Optional, Set
import logging

logger = logging.getLogger(__name__)


class CodeValidationError(Exception):
    """Raised when code validation fails"""
    pass


class CodeValidator:
    """Validates and sanitizes generated Python code"""
    
    # Dangerous functions and modules that should not be used
    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', '__import__', 'compile', 
        'open', 'input', 'raw_input',
        'globals', 'locals', 'vars', 'dir',
        'getattr', 'setattr', 'delattr', 'hasattr',
        'help', 'reload', 'breakpoint'
    }
    
    FORBIDDEN_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib',
        'requests', 'http', 'ftplib', 'telnetlib',
        'pickle', 'shelve', 'marshal', 'dill',
        'multiprocessing', 'threading', 'asyncio'
    }
    
    # Allowed safe modules for data analysis
    ALLOWED_MODULES = {
        'pandas', 'numpy', 'matplotlib', 'seaborn', 'plotly',
        'scipy', 'sklearn', 'statsmodels',
        'datetime', 'math', 'statistics', 'random',
        'collections', 'itertools', 'functools',
        'typing', 'dataclasses', 'enum'
    }
    
    # Dangerous patterns in code
    DANGEROUS_PATTERNS = [
        r'__\w+__',  # Dunder methods (except common ones)
        r'os\.',
        r'sys\.',
        r'subprocess\.',
        r'import\s+os',
        r'import\s+sys',
        r'from\s+os\s+import',
        r'from\s+sys\s+import'
    ]
    
    # Safe dunder methods that are allowed
    SAFE_DUNDER_METHODS = {
        '__init__', '__str__', '__repr__', '__len__',
        '__getitem__', '__setitem__', '__iter__', '__next__',
        '__eq__', '__ne__', '__lt__', '__le__', '__gt__', '__ge__',
        '__add__', '__sub__', '__mul__', '__truediv__', '__floordiv__',
        '__mod__', '__pow__', '__and__', '__or__', '__xor__'
    }
    
    def __init__(self):
        """Initialize code validator"""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for safety and executability
        
        Args:
            code: Python code string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # 1. Check if code is empty
            if not code or not code.strip():
                return False, "Code is empty"
            
            # 2. Check for dangerous patterns
            is_safe, danger_msg = self._check_dangerous_patterns(code)
            if not is_safe:
                return False, danger_msg
            
            # 3. Parse AST to validate syntax
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return False, f"Syntax error: {str(e)}"
            
            # 4. Check AST for forbidden operations
            is_safe, forbidden_msg = self._check_ast_safety(tree)
            if not is_safe:
                return False, forbidden_msg
            
            # 5. Check for required dataframe variable
            has_df, df_msg = self._check_dataframe_usage(tree)
            if not has_df:
                self.logger.warning(f"No dataframe usage detected: {df_msg}")
            
            return True, None
            
        except Exception as e:
            self.logger.exception(f"Validation error: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _check_dangerous_patterns(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Check for dangerous patterns using regex
        
        Args:
            code: Python code string
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        for pattern in self.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, code)
            if matches:
                # Check if it's a safe dunder method
                if pattern == r'__\w+__':
                    unsafe_matches = [m for m in matches if m not in self.SAFE_DUNDER_METHODS]
                    if unsafe_matches:
                        return False, f"Forbidden dunder method detected: {unsafe_matches[0]}"
                else:
                    return False, f"Dangerous pattern detected: {matches[0]}"
        
        return True, None
    
    def _check_ast_safety(self, tree: ast.AST) -> Tuple[bool, Optional[str]]:
        """
        Check AST for forbidden operations
        
        Args:
            tree: Parsed AST
            
        Returns:
            Tuple of (is_safe, error_message)
        """
        for node in ast.walk(tree):
            # Check for forbidden function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.FORBIDDEN_FUNCTIONS:
                        return False, f"Forbidden function: {func_name}()"
            
            # Check for forbidden imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    if module in self.FORBIDDEN_MODULES:
                        return False, f"Forbidden module import: {module}"
                    if module not in self.ALLOWED_MODULES and module != 'pandas':
                        self.logger.warning(f"Unrecognized module import: {module}")
            
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    module = node.module.split('.')[0]
                    if module in self.FORBIDDEN_MODULES:
                        return False, f"Forbidden module import: {module}"
                    if module not in self.ALLOWED_MODULES:
                        self.logger.warning(f"Unrecognized module import: {module}")
            
            # Check for dangerous attribute access
            if isinstance(node, ast.Attribute):
                if node.attr in self.FORBIDDEN_FUNCTIONS:
                    return False, f"Forbidden attribute access: .{node.attr}"
        
        return True, None
    
    def _check_dataframe_usage(self, tree: ast.AST) -> Tuple[bool, Optional[str]]:
        """
        Check if code uses the dataframe variable
        
        Args:
            tree: Parsed AST
            
        Returns:
            Tuple of (has_df, message)
        """
        has_df = False
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == 'df':
                has_df = True
                break
        
        if not has_df:
            return False, "Code doesn't reference 'df' variable"
        
        return True, None
    
    def sanitize(self, code: str) -> str:
        """
        Sanitize code by removing code fences and extra whitespace
        
        Args:
            code: Raw code string
            
        Returns:
            Sanitized code string
        """
        # Remove markdown code fences
        code = re.sub(r'^```python\s*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'^```\s*\n', '', code, flags=re.MULTILINE)
        code = re.sub(r'\n```\s*$', '', code, flags=re.MULTILINE)
        
        # Remove leading/trailing whitespace
        code = code.strip()
        
        return code
    
    def extract_code_blocks(self, text: str) -> List[str]:
        """
        Extract Python code blocks from text
        
        Args:
            text: Text containing code blocks
            
        Returns:
            List of extracted code blocks
        """
        # Match code blocks with ```python or ``` fences
        pattern = r'```(?:python)?\s*\n(.*?)\n```'
        matches = re.findall(pattern, text, re.DOTALL)
        
        if matches:
            return [self.sanitize(match) for match in matches]
        
        # If no code blocks found, assume entire text is code
        return [self.sanitize(text)]
    
    def validate_and_sanitize(self, code: str) -> Tuple[str, bool, Optional[str]]:
        """
        Sanitize and validate code in one step
        
        Args:
            code: Raw code string
            
        Returns:
            Tuple of (sanitized_code, is_valid, error_message)
        """
        # Extract code blocks
        code_blocks = self.extract_code_blocks(code)
        
        if not code_blocks:
            return "", False, "No code found"
        
        # Use the first (or only) code block
        sanitized = code_blocks[0]
        
        # Validate
        is_valid, error_msg = self.validate(sanitized)
        
        return sanitized, is_valid, error_msg
    
    def get_imports(self, code: str) -> Set[str]:
        """
        Extract all import statements from code
        
        Args:
            code: Python code string
            
        Returns:
            Set of imported module names
        """
        imports = set()
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])
        except SyntaxError:
            self.logger.error("Failed to parse code for imports")
        
        return imports
    
    def add_safety_wrapper(self, code: str) -> str:
        """
        Add safety wrapper around code execution
        
        Args:
            code: Python code string
            
        Returns:
            Wrapped code with error handling
        """
        wrapper = f'''
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Generated code with error handling
try:
{self._indent_code(code, spaces=4)}
except Exception as e:
    print(f"Error executing code: {{type(e).__name__}}: {{str(e)}}")
    raise
'''
        return wrapper.strip()
    
    def _indent_code(self, code: str, spaces: int = 4) -> str:
        """
        Indent code by specified number of spaces
        
        Args:
            code: Code to indent
            spaces: Number of spaces to indent
            
        Returns:
            Indented code
        """
        indent = ' ' * spaces
        lines = code.split('\n')
        return '\n'.join([indent + line if line.strip() else line for line in lines])


# Global validator instance
code_validator = CodeValidator()
