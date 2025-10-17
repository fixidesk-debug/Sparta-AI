"""
Quick test script to verify SPARTA AI setup
"""
import os
import sys
from pathlib import Path

def test_setup():
    print("🔍 Testing SPARTA AI Setup...\n")
    
    issues = []
    
    # Test 1: Check .env file
    print("1. Checking .env file...")
    if not Path(".env").exists():
        issues.append("❌ .env file not found")
    else:
        print("   ✅ .env file exists")
        
        # Check for required keys
        with open(".env", "r") as f:
            env_content = f.read()
            
        if "GROQ_API_KEY" not in env_content:
            issues.append("❌ GROQ_API_KEY not in .env")
        elif "gsk_" in env_content:
            print("   ✅ GROQ_API_KEY configured")
        else:
            issues.append("❌ GROQ_API_KEY appears empty")
            
        if "DATABASE_URL" not in env_content:
            issues.append("❌ DATABASE_URL not in .env")
        else:
            print("   ✅ DATABASE_URL configured")
    
    # Test 2: Check uploads directory
    print("\n2. Checking uploads directory...")
    uploads_dir = Path("uploads")
    if not uploads_dir.exists():
        print("   ⚠️  Creating uploads directory...")
        uploads_dir.mkdir(parents=True, exist_ok=True)
        print("   ✅ uploads directory created")
    else:
        print("   ✅ uploads directory exists")
    
    # Test 3: Check database file (SQLite)
    print("\n3. Checking database...")
    if Path("sparta_ai.db").exists():
        print("   ✅ Database file exists")
    else:
        issues.append("⚠️  Database not initialized (run: python init_db.py)")
    
    # Test 4: Check dependencies
    print("\n4. Checking dependencies...")
    try:
        import fastapi
        print("   ✅ FastAPI installed")
    except ImportError:
        issues.append("❌ FastAPI not installed")
    
    try:
        import groq
        print("   ✅ Groq SDK installed")
    except ImportError:
        issues.append("❌ Groq SDK not installed")
    
    try:
        import duckdb
        print("   ✅ DuckDB installed")
    except ImportError:
        issues.append("❌ DuckDB not installed")
    
    try:
        import pandas
        print("   ✅ Pandas installed")
    except ImportError:
        issues.append("❌ Pandas not installed")
    
    # Test 5: Test Groq API
    print("\n5. Testing Groq API connection...")
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            issues.append("❌ GROQ_API_KEY not loaded from .env")
        else:
            from groq import Groq
            client = Groq(api_key=groq_key)
            
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": "Say 'OK'"}],
                max_tokens=10
            )
            
            if response.choices[0].message.content:
                print("   ✅ Groq API working!")
            else:
                issues.append("❌ Groq API returned empty response")
    except Exception as e:
        issues.append(f"❌ Groq API test failed: {str(e)}")
    
    # Summary
    print("\n" + "="*50)
    if not issues:
        print("✅ ALL TESTS PASSED!")
        print("\nYou can now start the backend:")
        print("  python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return 0
    else:
        print("⚠️  ISSUES FOUND:")
        for issue in issues:
            print(f"  {issue}")
        print("\nPlease fix the issues above before starting the backend.")
        return 1

if __name__ == "__main__":
    sys.exit(test_setup())
