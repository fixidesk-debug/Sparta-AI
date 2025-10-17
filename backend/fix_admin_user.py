"""Fix admin user email"""
from app.db.session import SessionLocal
from app.db.models import User
from app.core.security import get_password_hash

db = SessionLocal()

# Delete old admin user if exists
old_user = db.query(User).filter(User.email == "admin@spartaai.com").first()
if old_user:
    db.delete(old_user)
    print("Deleted old admin user")

# Check if new admin exists
new_user = db.query(User).filter(User.email == "admin@sparta.ai").first()

if not new_user:
    # Create new admin user
    admin = User(
        email="admin@sparta.ai",
        hashed_password=get_password_hash("admin123"),
        full_name="Admin User"
    )
    db.add(admin)
    db.commit()
    print("✅ Created admin user: admin@sparta.ai / admin123")
else:
    print("✅ Admin user already exists: admin@sparta.ai")

db.close()
