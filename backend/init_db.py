"""
Database Initialization Script
Run this to create all database tables
"""
from app.db.session import engine
from app.db.models import Base
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.db.models import User

def init_db():
    """Initialize database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")
    
    # Create a test user if none exists
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == "admin@spartaai.com").first()
        if not existing_user:
            print("Creating default admin user...")
            admin_user = User(
                email="admin@spartaai.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User"
            )
            db.add(admin_user)
            db.commit()
            print("✓ Default admin user created")
            print("  Email: admin@spartaai.com")
            print("  Password: admin123")
        else:
            print("✓ Admin user already exists")
    except Exception as e:
        print(f"✗ Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    try:
        init_db()
        print("\n✓ Database initialization complete!")
    except Exception as e:
        print(f"\n✗ Database initialization failed: {e}")
        print("\nPlease check:")
        print("1. .env file exists with DATABASE_URL")
        print("2. Database server is running")
        print("3. Database credentials are correct")
