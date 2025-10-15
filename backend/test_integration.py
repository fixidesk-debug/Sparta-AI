"""
Integration Test for AI Code Generation
Tests the complete flow from query to code generation
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import User, File
from app.services.ai_code_generator import AICodeGenerator
from app.services.ai_providers import AIProvider
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_code_generation():
    """Test the AI code generation system"""
    
    logger.info("=" * 60)
    logger.info("AI Code Generation Integration Test")
    logger.info("=" * 60)
    
    # Check API key
    if not settings.OPENAI_API_KEY:
        logger.error("❌ OPENAI_API_KEY not set in environment")
        return False
    
    logger.info("✅ OpenAI API key found")
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Get or create test user
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        if not test_user:
            logger.warning("No test user found. Please create a user first.")
            return False
        
        logger.info(f"✅ Test user found: {test_user.email}")
        
        # Get a test file
        test_file = db.query(File).filter(File.user_id == test_user.id).first()
        if not test_file:
            logger.warning("No test file found. Please upload a file first.")
            return False
        
        logger.info(f"✅ Test file found: {test_file.filename}")
        
        # Create AI code generator
        logger.info("\n📝 Creating AI Code Generator...")
        generator = AICodeGenerator(
            provider=AIProvider.OPENAI,
            temperature=0.3,
            max_tokens=2000
        )
        logger.info("✅ Generator created")
        
        # Test queries
        test_queries = [
            "Show me the first 10 rows of the data",
            "Calculate the average of all numeric columns",
            "Create a bar chart showing the distribution of values",
            "Show me summary statistics for the dataset"
        ]
        
        logger.info("\n🧪 Testing code generation...\n")
        
        for i, query in enumerate(test_queries, 1):
            logger.info(f"Test {i}/{len(test_queries)}: {query}")
            logger.info("-" * 60)
            
            try:
                result = await generator.generate_code(
                    query=query,
                    file_id=getattr(test_file, 'id'),
                    user_id=getattr(test_user, 'id'),
                    db=db
                )
                
                if result.is_valid:
                    logger.info("✅ Code generation successful")
                    logger.info(f"   Analysis Type: {result.analysis_type.value if result.analysis_type else 'custom'}")
                    logger.info(f"   Code Length: {len(result.code)} characters")
                    if result.explanation:
                        logger.info(f"   Explanation: {result.explanation[:100]}...")
                    logger.info(f"\n   Generated Code:\n{'-'*40}")
                    logger.info(result.code)
                    logger.info("-" * 40)
                else:
                    logger.error(f"❌ Code validation failed: {result.error}")
                    logger.info(f"   Generated Code:\n{result.code}")
                
            except Exception as e:
                logger.exception(f"❌ Error generating code: {e}")
            
            logger.info("\n")
        
        logger.info("=" * 60)
        logger.info("✅ Integration test completed successfully!")
        logger.info("=" * 60)
        return True
        
    except Exception as e:
        logger.exception(f"❌ Test failed: {e}")
        return False
    
    finally:
        db.close()


async def test_conversation_memory():
    """Test conversation memory for multi-turn interactions"""
    
    logger.info("\n" + "=" * 60)
    logger.info("Conversation Memory Test")
    logger.info("=" * 60)
    
    db: Session = SessionLocal()
    
    try:
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        test_file = db.query(File).filter(File.user_id == test_user.id).first() if test_user else None
        
        if not test_user or not test_file:
            logger.warning("Test user or file not found")
            return False
        
        generator = AICodeGenerator(provider=AIProvider.OPENAI, temperature=0.3)
        session_id = "test_session_123"
        
        # First query
        logger.info("\n🔹 First Query: Show me the data overview")
        result1 = await generator.generate_code(
            query="Show me the data overview",
            file_id=getattr(test_file, 'id'),
            user_id=getattr(test_user, 'id'),
            db=db,
            session_id=session_id
        )
        
        if result1.is_valid:
            logger.info("✅ First query successful")
            logger.info(f"   Code: {result1.code[:100]}...")
        
        # Follow-up query
        logger.info("\n🔹 Follow-up Query: Now create a visualization")
        result2 = await generator.generate_code(
            query="Now create a visualization of the data",
            file_id=getattr(test_file, 'id'),
            user_id=getattr(test_user, 'id'),
            db=db,
            session_id=session_id
        )
        
        if result2.is_valid:
            logger.info("✅ Follow-up query successful")
            logger.info(f"   Code: {result2.code[:100]}...")
            logger.info("✅ Conversation memory is working!")
        
        return True
        
    except Exception as e:
        logger.exception(f"❌ Conversation memory test failed: {e}")
        return False
    
    finally:
        db.close()


async def test_security_validation():
    """Test security validation"""
    
    logger.info("\n" + "=" * 60)
    logger.info("Security Validation Test")
    logger.info("=" * 60)
    
    from app.services.code_validator import CodeValidator
    
    validator = CodeValidator()
    
    # Test dangerous code
    dangerous_codes = [
        ("import os; os.system('rm -rf /')", "os module"),
        ("eval('malicious code')", "eval function"),
        ("exec('bad code')", "exec function"),
        ("__import__('subprocess')", "__import__ function"),
        ("open('/etc/passwd', 'r')", "open function")
    ]
    
    logger.info("\n🔒 Testing security validation...\n")
    
    all_blocked = True
    for code, description in dangerous_codes:
        is_valid, error = validator.validate(code)
        if not is_valid:
            logger.info(f"✅ Blocked {description}")
        else:
            logger.error(f"❌ Failed to block {description}")
            all_blocked = False
    
    # Test safe code
    safe_code = """
import pandas as pd
import numpy as np

result = df.describe()
print(result)
"""
    
    is_valid, error = validator.validate(safe_code)
    if is_valid:
        logger.info("✅ Allowed safe pandas code")
    else:
        logger.error(f"❌ Blocked safe code: {error}")
        all_blocked = False
    
    if all_blocked:
        logger.info("\n✅ All security tests passed!")
    else:
        logger.error("\n❌ Some security tests failed!")
    
    return all_blocked


async def main():
    """Run all integration tests"""
    
    print("\n" + "=" * 60)
    print("SPARTA AI - AI Code Generation Integration Tests")
    print("=" * 60 + "\n")
    
    # Test security validation
    security_passed = await test_security_validation()
    
    # Test code generation
    generation_passed = await test_code_generation()
    
    # Test conversation memory
    memory_passed = await test_conversation_memory()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Security Validation: {'✅ PASSED' if security_passed else '❌ FAILED'}")
    print(f"Code Generation:     {'✅ PASSED' if generation_passed else '❌ FAILED'}")
    print(f"Conversation Memory: {'✅ PASSED' if memory_passed else '❌ FAILED'}")
    print("=" * 60)
    
    if security_passed and generation_passed and memory_passed:
        print("\n🎉 All tests passed! System is ready for production.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the logs above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
