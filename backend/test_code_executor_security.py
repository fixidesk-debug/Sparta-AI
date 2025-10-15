"""
Security Test Suite for Code Executor

Comprehensive tests to validate security measures and ensure the code executor
properly blocks malicious operations while allowing legitimate data science code.

Author: Sparta AI Team
Date: October 14, 2025
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.code_executor import CodeExecutor
import pandas as pd
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SecurityTestSuite:
    """Comprehensive security test suite for code executor"""
    
    def __init__(self):
        self.executor = CodeExecutor(timeout_seconds=5, max_memory_mb=256)
        self.passed = 0
        self.failed = 0
        self.test_results = []
    
    def run_test(self, name: str, code: str, context: Optional[dict] = None, should_fail: bool = True):
        """Run a single test case"""
        try:
            result = self.executor.execute(code, context or {})
            success = result['success']
            
            if should_fail:
                # Test should fail (security block)
                if success:
                    logger.error(f"❌ {name}: SECURITY BREACH - Code should have been blocked")
                    self.failed += 1
                    self.test_results.append({'name': name, 'status': 'FAILED', 'reason': 'Security breach'})
                    return False
                else:
                    logger.info(f"✅ {name}: Correctly blocked")
                    self.passed += 1
                    self.test_results.append({'name': name, 'status': 'PASSED', 'reason': 'Correctly blocked'})
                    return True
            else:
                # Test should succeed (legitimate code)
                if success:
                    logger.info(f"✅ {name}: Correctly allowed")
                    self.passed += 1
                    self.test_results.append({'name': name, 'status': 'PASSED', 'reason': 'Correctly allowed'})
                    return True
                else:
                    logger.error(f"❌ {name}: INCORRECTLY BLOCKED - {result.get('error')}")
                    self.failed += 1
                    self.test_results.append({'name': name, 'status': 'FAILED', 'reason': f"Incorrectly blocked: {result.get('error')}"})
                    return False
        
        except Exception as e:
            logger.error(f"❌ {name}: Exception - {e}")
            self.failed += 1
            self.test_results.append({'name': name, 'status': 'FAILED', 'reason': str(e)})
            return False
    
    # ========== FILE SYSTEM SECURITY TESTS ==========
    
    def test_block_file_read(self):
        """Test that file reading is blocked"""
        code = """
with open('/etc/passwd', 'r') as f:
    data = f.read()
print(data)
"""
        return self.run_test("Block file read with open()", code)
    
    def test_block_file_write(self):
        """Test that file writing is blocked"""
        code = """
with open('/tmp/malicious.txt', 'w') as f:
    f.write('hacked')
"""
        return self.run_test("Block file write", code)
    
    def test_block_file_delete(self):
        """Test that file operations are blocked"""
        code = """
import os
os.remove('/tmp/important.txt')
"""
        return self.run_test("Block file deletion", code)
    
    # ========== CODE EXECUTION SECURITY TESTS ==========
    
    def test_block_eval(self):
        """Test that eval() is blocked"""
        code = """
result = eval('__import__("os").system("ls")')
print(result)
"""
        return self.run_test("Block eval() function", code)
    
    def test_block_exec(self):
        """Test that exec() is blocked"""
        code = """
exec('import os; os.system("whoami")')
"""
        return self.run_test("Block exec() function", code)
    
    def test_block_compile(self):
        """Test that compile() is blocked"""
        code = """
code_obj = compile('print("hack")', '<string>', 'exec')
eval(code_obj)
"""
        return self.run_test("Block compile() function", code)
    
    def test_block_import_builtin(self):
        """Test that __import__() is blocked"""
        code = """
os = __import__('os')
os.system('ls')
"""
        return self.run_test("Block __import__()", code)
    
    # ========== SYSTEM ACCESS SECURITY TESTS ==========
    
    def test_block_os_import(self):
        """Test that os module import is blocked"""
        code = """
import os
print(os.listdir('.'))
"""
        return self.run_test("Block os module import", code)
    
    def test_block_sys_import(self):
        """Test that sys module import is blocked"""
        code = """
import sys
print(sys.path)
"""
        return self.run_test("Block sys module import", code)
    
    def test_block_subprocess(self):
        """Test that subprocess is blocked"""
        code = """
import subprocess
subprocess.run(['ls', '-la'])
"""
        return self.run_test("Block subprocess import", code)
    
    # ========== NETWORK SECURITY TESTS ==========
    
    def test_block_socket(self):
        """Test that socket module is blocked"""
        code = """
import socket
s = socket.socket()
s.connect(('google.com', 80))
"""
        return self.run_test("Block socket module", code)
    
    def test_block_urllib(self):
        """Test that urllib is blocked"""
        code = """
import urllib.request
response = urllib.request.urlopen('http://example.com')
"""
        return self.run_test("Block urllib", code)
    
    def test_block_requests(self):
        """Test that requests library is blocked"""
        code = """
import requests
r = requests.get('http://example.com')
"""
        return self.run_test("Block requests library", code)
    
    # ========== PRIVATE ATTRIBUTE ACCESS TESTS ==========
    
    def test_block_dict_access(self):
        """Test that private attribute access is blocked"""
        code = """
x = []
print(x.__dict__)
"""
        return self.run_test("Block __dict__ access", code)
    
    def test_block_class_manipulation(self):
        """Test that class manipulation is blocked"""
        code = """
x = ''
x.__class__.__bases__[0].__subclasses__()
"""
        return self.run_test("Block __class__ manipulation", code)
    
    # ========== LEGITIMATE CODE TESTS (SHOULD SUCCEED) ==========
    
    def test_allow_pandas(self):
        """Test that legitimate pandas code works"""
        code = """
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
result = df.describe()
print(result)
"""
        return self.run_test("Allow pandas operations", code, should_fail=False)
    
    def test_allow_numpy(self):
        """Test that legitimate numpy code works"""
        code = """
import numpy as np
arr = np.array([1, 2, 3, 4, 5])
mean = np.mean(arr)
print(f'Mean: {mean}')
"""
        return self.run_test("Allow numpy operations", code, should_fail=False)
    
    def test_allow_matplotlib(self):
        """Test that matplotlib plotting works"""
        code = """
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(0, 10, 100)
y = np.sin(x)

plt.figure(figsize=(10, 6))
plt.plot(x, y)
plt.title('Sine Wave')
plt.xlabel('X')
plt.ylabel('Y')
plt.grid(True)
"""
        return self.run_test("Allow matplotlib plotting", code, should_fail=False)
    
    def test_allow_seaborn(self):
        """Test that seaborn visualization works"""
        code = """
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    'x': [1, 2, 3, 4, 5],
    'y': [2, 4, 6, 8, 10]
})

plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x='x', y='y')
plt.title('Scatter Plot')
"""
        return self.run_test("Allow seaborn visualization", code, should_fail=False)
    
    def test_allow_stats(self):
        """Test that statistical analysis works"""
        code = """
from scipy import stats
import numpy as np

data1 = np.random.normal(0, 1, 100)
data2 = np.random.normal(0.5, 1, 100)

t_stat, p_value = stats.ttest_ind(data1, data2)
print(f'T-statistic: {t_stat:.4f}, P-value: {p_value:.4f}')
"""
        return self.run_test("Allow statistical analysis", code, should_fail=False)
    
    def test_allow_sklearn(self):
        """Test that sklearn machine learning works"""
        code = """
from sklearn.linear_model import LinearRegression
import numpy as np

X = np.array([[1], [2], [3], [4], [5]])
y = np.array([2, 4, 6, 8, 10])

model = LinearRegression()
model.fit(X, y)

predictions = model.predict([[6], [7]])
print(f'Predictions: {predictions}')
"""
        return self.run_test("Allow machine learning", code, should_fail=False)
    
    def test_allow_data_manipulation(self):
        """Test that complex data manipulation works"""
        code = """
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'category': ['A', 'B', 'A', 'B', 'A', 'B'],
    'value': [10, 20, 15, 25, 12, 22]
})

result = df.groupby('category')['value'].agg(['mean', 'sum', 'count'])
print(result)
"""
        return self.run_test("Allow data manipulation", code, should_fail=False)
    
    # ========== OUTPUT CAPTURE TESTS ==========
    
    def test_capture_output(self):
        """Test that print output is captured"""
        code = """
print('Hello, World!')
print('Line 2')
for i in range(5):
    print(f'Number: {i}')
"""
        result = self.executor.execute(code)
        if result['success'] and 'Hello, World!' in result['output']:
            return self.run_test("Capture print output", code, should_fail=False)
        return False
    
    def test_capture_variables(self):
        """Test that variables are captured"""
        code = """
x = 42
y = 'test'
z = [1, 2, 3]
"""
        result = self.executor.execute(code)
        if result['success'] and 'x' in result['variables']:
            return self.run_test("Capture variables", code, should_fail=False)
        return False
    
    # ========== DATAFRAME CONTEXT TESTS ==========
    
    def test_dataframe_context(self):
        """Test execution with a dataframe in context"""
        df = pd.DataFrame({
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000]
        })
        
        code = """
result = df[df['age'] > 28]
print(result)
print(f'Average salary: ${df["salary"].mean():.2f}')
"""
        return self.run_test("Execute with dataframe context", code, context={'df': df}, should_fail=False)
    
    def run_all_tests(self):
        """Run all security tests"""
        logger.info("\n" + "=" * 70)
        logger.info("SPARTA AI - Code Executor Security Test Suite")
        logger.info("=" * 70 + "\n")
        
        # Get all test methods
        test_methods = [
            method for method in dir(self)
            if method.startswith('test_') and callable(getattr(self, method))
        ]
        
        logger.info(f"Running {len(test_methods)} security tests...\n")
        
        # Run each test
        for method_name in sorted(test_methods):
            method = getattr(self, method_name)
            method()
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("TEST SUMMARY")
        logger.info("=" * 70)
        logger.info(f"Total Tests: {self.passed + self.failed}")
        logger.info(f"✅ Passed: {self.passed}")
        logger.info(f"❌ Failed: {self.failed}")
        logger.info(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        logger.info("=" * 70 + "\n")
        
        if self.failed > 0:
            logger.error("⚠️  SECURITY ISSUES DETECTED!")
            logger.error("\nFailed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAILED':
                    logger.error(f"  - {result['name']}: {result['reason']}")
            return False
        else:
            logger.info("🎉 All security tests passed! System is secure.")
            return True


def main():
    """Run the security test suite"""
    suite = SecurityTestSuite()
    success = suite.run_all_tests()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
