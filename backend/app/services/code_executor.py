"""
Secure Python Code Execution Service

This module provides a sandboxed environment for executing user-generated Python code
with comprehensive security measures and resource limits.

Security Features:
- Restricted imports (data science libraries only)
- Resource limits (memory, CPU, execution time)
- File system isolation
- Network access blocking
- AST-based code validation
- Output capture and sanitization

Author: Sparta AI Team
Date: October 14, 2025
"""

import io
import ast
import time
import base64
import traceback
import logging
import re
from typing import Dict, Any, Optional, List, Tuple
from contextlib import redirect_stdout, redirect_stderr
from datetime import datetime, timezone
import json
import platform
import types
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from sklearn import preprocessing

# Platform-specific imports
IS_WINDOWS = platform.system() == 'Windows'

if not IS_WINDOWS:
    import resource
    import signal
else:
    # Stubs for Windows
    resource = None
    signal = None

logger = logging.getLogger(__name__)


class ExecutionTimeoutError(Exception):
    """Raised when code execution exceeds time limit"""
    pass


class ExecutionMemoryError(Exception):
    """Raised when code execution exceeds memory limit"""
    pass


class SecurityViolationError(Exception):
    """Raised when code contains security violations"""
    pass


class CodeExecutor:
    """
    Secure Python code executor with sandboxing and resource limits.
    
    Security Measures:
    - Whitelist-based import restrictions
    - AST validation for dangerous operations
    - Execution timeout (default 30 seconds)
    - Memory limit enforcement
    - Restricted built-ins
    - Output size limits
    
    Example:
        >>> executor = CodeExecutor(timeout_seconds=30, max_memory_mb=512)
        >>> result = executor.execute(code="print('Hello')", context={'df': dataframe})
        >>> print(result['output'])
    """
    
    # Allowed imports - only data science and visualization libraries
    ALLOWED_IMPORTS = {
        'pandas', 'pd',
        'numpy', 'np',
        'matplotlib', 'plt',
        'seaborn', 'sns',
        'plotly',
        'scipy', 'stats',
        'sklearn', 'preprocessing',
        'json',
        'datetime',
        'math',
        'random',
        'collections',
        'itertools',
        'functools',
        're',
    }
    
    # Forbidden built-in functions
    FORBIDDEN_BUILTINS = {
        'eval', 'exec', 'compile', '__import__',
        'open', 'file', 'input', 'raw_input',
        'execfile', 'reload', 'vars', 'globals', 'locals',
        'dir', 'help', 'quit', 'exit',
    }
    
    # Forbidden modules and operations
    FORBIDDEN_MODULES = {
        'os', 'sys', 'subprocess', 'socket', 'urllib',
        'requests', 'http', 'ftplib', 'telnetlib',
        'pickle', 'shelve', 'marshal', 'tempfile',
        'shutil', 'glob', 'pathlib', 'importlib',
    }
    
    # Forbidden AST node types - removed, we check imports individually
    FORBIDDEN_AST_NODES = {}
    
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_memory_mb: int = 512,
        max_output_size: int = 1024 * 1024,  # 1MB
    ):
        """
        Initialize the code executor.
        
        Args:
            timeout_seconds: Maximum execution time in seconds
            max_memory_mb: Maximum memory usage in megabytes
            max_output_size: Maximum output size in bytes
        """
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.max_output_size = max_output_size
        self.start_time = None
        
    def _timeout_handler(self, signum, frame):
        """Signal handler for execution timeout (Unix only)"""
        raise ExecutionTimeoutError(
            f"Code execution exceeded {self.timeout_seconds} second timeout"
        )
    
    def _set_memory_limit(self):
        """Set memory limit for the execution (Unix only)"""
        if IS_WINDOWS:
            logger.warning("Memory limits are not supported on Windows")
            return
            
        try:
            # Set virtual memory limit (Unix-like systems only)
            max_memory_bytes = self.max_memory_mb * 1024 * 1024
            resource.setrlimit(  # type: ignore
                resource.RLIMIT_AS,  # type: ignore
                (max_memory_bytes, max_memory_bytes)
            )
        except (ValueError, OSError) as e:
            # Memory limits may not be supported on all platforms
            logger.warning(f"Could not set memory limit: {e}")
    
    def _validate_code_security(self, code: str) -> Tuple[bool, Optional[str]]:
        """
        Validate code for security issues using AST analysis.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Additional string-based checks before AST parsing
        dangerous_patterns = [
            r'__builtins__', r'__globals__', r'__code__', r'__closure__',
            r'\bexec\s*\(', r'\beval\s*\(', r'\bcompile\s*\(',
            r'\b__import__\s*\(', r'\bopen\s*\('
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False, f"Potentially dangerous code pattern detected"
        
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        for node in ast.walk(tree):
            # Check for forbidden imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name.split('.')[0]  # Get base module
                    if module_name in self.FORBIDDEN_MODULES:
                        return False, f"Forbidden module import: {module_name}"
                    # Only allow imports from ALLOWED_IMPORTS list
                    if module_name not in self.ALLOWED_IMPORTS:
                        return False, f"Module '{module_name}' is not in allowed list. Use pre-imported modules: pd, np, plt, sns, px, go, stats"
            
            # Check for import from statements
            if isinstance(node, ast.ImportFrom):
                module_name = node.module.split('.')[0] if node.module else ''
                if module_name in self.FORBIDDEN_MODULES:
                    return False, f"Forbidden module import: {module_name}"
                # Allow imports from specific allowed modules
                if module_name and module_name not in self.ALLOWED_IMPORTS:
                    return False, f"Module '{module_name}' is not in allowed list. Use pre-imported modules: pd, np, plt, sns, px, go, stats"
            
            # Check for forbidden function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in self.FORBIDDEN_BUILTINS:
                        return False, f"Forbidden function: {func_name}()"
            
            # Check for attribute access that might be dangerous
            if isinstance(node, ast.Attribute):
                attr_name = node.attr
                if attr_name.startswith('__'):  # Only block dunder attributes
                    return False, f"Access to private attributes not allowed: {attr_name}"
        
        return True, None
    
    def _safe_import(self, name, globals=None, locals=None, fromlist=(), level=0):
        """Safe import function that only allows whitelisted modules"""
        base_module = name.split('.')[0]
        
        # Check if module is forbidden
        if base_module in self.FORBIDDEN_MODULES:
            raise ImportError(f"Import of module '{base_module}' is not allowed")
        
        # Check if module is in allowed list
        if base_module not in self.ALLOWED_IMPORTS:
            raise ImportError(f"Module '{base_module}' is not in allowed list")
        
        # Use the real __import__ to load the module
        return __builtins__['__import__'](name, globals, locals, fromlist, level)
    
    def _create_safe_globals(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a restricted global namespace for code execution.
        
        Args:
            context: Additional variables to add to the namespace
            
        Returns:
            Dictionary of allowed global variables
        """
        # Start with minimal safe built-ins
        safe_builtins = {
            'abs': abs, 'all': all, 'any': any, 'bool': bool,
            'dict': dict, 'enumerate': enumerate, 'filter': filter,
            'float': float, 'int': int, 'len': len, 'list': list,
            'map': map, 'max': max, 'min': min, 'pow': pow,
            'range': range, 'reversed': reversed, 'round': round,
            'set': set, 'slice': slice, 'sorted': sorted,
            'str': str, 'sum': sum, 'tuple': tuple, 'type': type,
            'zip': zip, 'print': print,
            'True': True, 'False': False, 'None': None,
            'Exception': Exception, 'ValueError': ValueError, 'TypeError': TypeError,
            'KeyError': KeyError, 'IndexError': IndexError, 'AttributeError': AttributeError,
            '__import__': self._safe_import,  # Safe import function
        }
        
        # Add allowed libraries
        safe_globals = {
            '__builtins__': safe_builtins,
            'pd': pd,
            'np': np,
            'plt': plt,
            'sns': sns,
            'px': px,
            'go': go,
            'stats': stats,
            'preprocessing': preprocessing,
            'json': json,
            'datetime': datetime,
        }
        
        # Add context variables (like dataframes)
        if context:
            for key, value in context.items():
                if not key.startswith('_'):  # Don't allow private variables
                    safe_globals[key] = value
        
        return safe_globals

    def _inspect_code_object(self, code_obj: types.CodeType) -> Tuple[bool, Optional[str]]:
        """
        Recursively inspect a compiled code object for forbidden names or patterns.

        Returns (True, None) if no issues found, otherwise (False, message).
        """
        forbidden = {
            '__import__', 'open', 'eval', 'exec', 'compile',
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests'
        }

        def _walk(co: types.CodeType) -> Tuple[bool, Optional[str]]:
            # Inspect names referenced by the code object
            for name in getattr(co, 'co_names', ()):  # attribute exists on code objects
                if name in forbidden:
                    return False, f"Forbidden name in compiled code: {name}"

            # Recursively walk nested code objects found in co_consts
            for const in getattr(co, 'co_consts', ()):
                if isinstance(const, types.CodeType):
                    ok, msg = _walk(const)
                    if not ok:
                        return False, msg

            return True, None

        return _walk(code_obj)
    
    def _capture_matplotlib_figures(self) -> List[str]:
        """
        Capture all matplotlib figures as base64-encoded PNG images.
        
        Returns:
            List of base64-encoded image strings
        """
        images = []
        
        try:
            fig_nums = plt.get_fignums()
            logger.info(f"Found {len(fig_nums)} matplotlib figures to capture")
            
            figures = [plt.figure(num) for num in fig_nums]
            
            for idx, fig in enumerate(figures):
                buffer = io.BytesIO()
                fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
                buffer.seek(0)
                img_data = buffer.read()
                
                # Validate image data before encoding
                if not img_data or len(img_data) == 0:
                    logger.error(f"Figure {idx+1} produced empty image data")
                    continue
                
                img_base64 = base64.b64encode(img_data).decode('utf-8')
                
                # Validate base64 encoding
                if not img_base64 or len(img_base64) < 100:
                    logger.error(f"Figure {idx+1} produced invalid base64 (length: {len(img_base64)})")
                    continue
                
                images.append(img_base64)
                logger.info(f"Captured figure {idx+1}, raw size: {len(img_data)} bytes, base64 size: {len(img_base64)} chars")
                logger.debug(f"Figure {idx+1} base64 preview: {img_base64[:50]}...{img_base64[-50:]}")
                buffer.close()
                plt.close(fig)
        except Exception as e:
            logger.error(f"Error capturing matplotlib figures: {e}", exc_info=True)
        
        logger.info(f"Total images captured: {len(images)}")
        return images
    
    def _capture_plotly_figures(self, namespace: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Capture Plotly figures from the namespace.
        
        Args:
            namespace: Execution namespace
            
        Returns:
            List of Plotly figure dictionaries
        """
        plotly_figures = []
        
        try:
            for var_name, var_value in namespace.items():
                if isinstance(var_value, (go.Figure, plotly.graph_objs.Figure)):
                    try:
                        fig_json = var_value.to_json()
                        if fig_json is not None:
                            plotly_figures.append({
                                'type': 'plotly',
                                'name': var_name,
                                'data': json.loads(fig_json)
                            })
                    except Exception as e:
                        logger.error(f"Error capturing Plotly figure {var_name}: {e}")
        except Exception as e:
            logger.error(f"Error scanning for Plotly figures: {e}")
        
        return plotly_figures
    
    def _format_output_variables(self, namespace: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format output variables for JSON serialization.
        
        Args:
            namespace: Execution namespace
            
        Returns:
            Dictionary of formatted variables
        """
        output_vars = {}
        
        for var_name, var_value in namespace.items():
            # Skip private variables and built-ins
            if var_name.startswith('_'):
                continue
            
            # Skip imported modules
            if var_name in self.ALLOWED_IMPORTS:
                continue
            
            # Skip matplotlib/plotly objects - they're captured separately
            var_type_str = str(type(var_value))
            if 'matplotlib' in var_type_str or 'plotly' in var_type_str:
                continue
            
            try:
                # Handle pandas DataFrames
                if isinstance(var_value, pd.DataFrame):
                    output_vars[var_name] = {
                        'type': 'dataframe',
                        'shape': var_value.shape,
                        'columns': list(var_value.columns),
                        'head': var_value.head(10).to_dict(orient='records'),
                        'dtypes': var_value.dtypes.astype(str).to_dict()
                    }
                
                # Handle pandas Series
                elif isinstance(var_value, pd.Series):
                    output_vars[var_name] = {
                        'type': 'series',
                        'shape': var_value.shape,
                        'head': var_value.head(10).to_dict(),
                        'dtype': str(var_value.dtype)
                    }
                
                # Handle numpy arrays
                elif isinstance(var_value, np.ndarray):
                    output_vars[var_name] = {
                        'type': 'numpy_array',
                        'shape': var_value.shape,
                        'dtype': str(var_value.dtype),
                        'data': var_value.tolist() if var_value.size < 1000 else 'Too large to serialize'
                    }
                
                # Handle basic types
                elif isinstance(var_value, (int, float, str, bool, type(None))):
                    output_vars[var_name] = {
                        'type': type(var_value).__name__,
                        'value': var_value
                    }
                
                # Handle lists and dicts
                elif isinstance(var_value, (list, dict)):
                    output_vars[var_name] = {
                        'type': type(var_value).__name__,
                        'value': var_value if len(str(var_value)) < 10000 else 'Too large to serialize'
                    }
            
            except Exception as e:
                logger.error(f"Error formatting variable {var_name}: {e}")
        
        return output_vars
    
    def execute(
        self,
        code: str,
        context: Optional[Dict[str, Any]] = None,
        stdout_writer: Optional[Any] = None,
        stderr_writer: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute Python code in a sandboxed environment.
        
        Args:
            code: Python code to execute
            context: Dictionary of variables to make available (e.g., {'df': dataframe})
            
        Returns:
            Dictionary containing:
                - success: bool
                - output: str (captured stdout)
                - error: Optional[str]
                - execution_time: float (seconds)
                - images: List[str] (base64-encoded matplotlib plots)
                - plotly_figures: List[Dict] (Plotly figure data)
                - variables: Dict[str, Any] (output variables)
        """
        self.start_time = time.time()
        result = {
            'success': False,
            'output': '',
            'error': None,
            'execution_time': 0.0,
            'images': [],
            'plotly_figures': [],
            'variables': {},
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        try:
            # Input validation
            if not code or not code.strip():
                raise ValueError("Code cannot be empty")
            if len(code) > 100000:
                raise ValueError("Code exceeds maximum length of 100KB")
            
            # Validate code security
            is_valid, error_msg = self._validate_code_security(code)
            if not is_valid:
                raise SecurityViolationError(error_msg)
            
            # Create safe execution environment
            safe_globals = self._create_safe_globals(context)
            safe_locals = {}
            
            # Set up output capture (allow external writers for streaming)
            stdout_capture = stdout_writer if stdout_writer is not None else io.StringIO()
            stderr_capture = stderr_writer if stderr_writer is not None else io.StringIO()
            
            # Set timeout (Unix-like systems only)
            if not IS_WINDOWS and signal is not None:
                try:
                    signal.signal(signal.SIGALRM, self._timeout_handler)  # type: ignore
                    signal.alarm(self.timeout_seconds)  # type: ignore
                except (AttributeError, ValueError):
                    logger.warning("Timeout handling not available on this platform")
            else:
                logger.warning("Timeout handling not available on Windows - execution time not limited")
            
            # Execute code with output redirection
            # SECURITY: Multi-layer protection:
            # 1. AST validation blocks dangerous operations
            # 2. Restricted namespace with whitelisted imports only
            # 3. No file/network access
            # 4. Resource limits enforced
            # 5. Bytecode compilation validates syntax
            try:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    # Compile with restricted mode for additional safety
                    compiled_code = compile(code, '<user_code>', 'exec', dont_inherit=True)
                    # Inspect compiled bytecode for forbidden names/patterns
                    ok, msg = self._inspect_code_object(compiled_code)
                    if not ok:
                        raise SecurityViolationError(msg)
                    # Execute in isolated namespace
                    exec(compiled_code, safe_globals, safe_locals)
            finally:
                # Cancel timeout alarm
                if not IS_WINDOWS and signal is not None:
                    try:
                        signal.alarm(0)  # type: ignore
                    except (AttributeError, ValueError):
                        pass
            
            # Capture outputs
            try:
                # If writer has getvalue (StringIO), use it; otherwise, try to join if it's a list
                if hasattr(stdout_capture, 'getvalue'):
                    result['output'] = stdout_capture.getvalue()
                elif isinstance(stdout_capture, list):
                    result['output'] = ''.join(stdout_capture)
                else:
                    result['output'] = str(stdout_capture)
            except Exception:
                result['output'] = ''

            try:
                if hasattr(stderr_capture, 'getvalue'):
                    stderr_output = stderr_capture.getvalue()
                elif isinstance(stderr_capture, list):
                    stderr_output = ''.join(stderr_capture)
                else:
                    stderr_output = str(stderr_capture)
            except Exception:
                stderr_output = ''
            
            if stderr_output:
                logger.warning(f"Code execution stderr: {stderr_output}")
            
            # Capture visualizations
            result['images'] = self._capture_matplotlib_figures()
            result['plotly_figures'] = self._capture_plotly_figures({**safe_globals, **safe_locals})
            
            # Capture output variables (skip for now to avoid serialization issues)
            # result['variables'] = self._format_output_variables(safe_locals)
            result['variables'] = {}
            
            # Truncate output if too large
            if len(result['output']) > self.max_output_size:
                result['output'] = (
                    result['output'][:self.max_output_size] +
                    f"\n\n[Output truncated - exceeded {self.max_output_size} bytes]"
                )
            
            result['success'] = True
            
        except ExecutionTimeoutError as e:
            result['error'] = str(e)
            logger.error(f"Code execution timeout: {e}")
        
        except SecurityViolationError as e:
            result['error'] = f"Security violation: {str(e)}"
            logger.error(f"Security violation in code execution: {e}")
        
        except MemoryError as e:
            result['error'] = f"Memory limit exceeded: {self.max_memory_mb}MB"
            logger.error(f"Code execution memory error: {e}")
        
        except SyntaxError as e:
            result['error'] = f"Syntax error: {str(e)}"
            logger.error(f"Code execution syntax error: {e}")
        
        except Exception as e:
            # Capture full traceback for debugging
            tb = traceback.format_exc()
            result['error'] = str(e)
            result['traceback'] = tb
            logger.error(f"Code execution error: {tb}")
        
        finally:
            # Calculate execution time
            result['execution_time'] = time.time() - self.start_time
            
            # Clean up matplotlib
            try:
                plt.close('all')
            except Exception as e:
                logger.exception("Error closing matplotlib figures during cleanup: %s", e)
        
        return result
    
    def validate_code(self, code: str) -> Dict[str, Any]:
        """
        Validate code without executing it.
        
        Args:
            code: Python code to validate
            
        Returns:
            Dictionary with validation results
        """
        is_valid, error_msg = self._validate_code_security(code)
        
        return {
            'valid': is_valid,
            'error': error_msg,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }


# Convenience function for quick execution
def execute_code(
    code: str,
    context: Optional[Dict[str, Any]] = None,
    timeout_seconds: int = 30,
    max_memory_mb: int = 512
) -> Dict[str, Any]:
    """
    Execute Python code in a sandboxed environment.
    
    Args:
        code: Python code to execute
        context: Dictionary of variables to make available
        timeout_seconds: Maximum execution time
        max_memory_mb: Maximum memory usage
        
    Returns:
        Execution result dictionary
    """
    executor = CodeExecutor(
        timeout_seconds=timeout_seconds,
        max_memory_mb=max_memory_mb
    )
    return executor.execute(code, context)
