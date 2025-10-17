"""
Test API endpoints registration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("=" * 60)
print("TESTING API ENDPOINTS")
print("=" * 60)

# Test endpoints
endpoints = [
    # Version Control
    ("GET", "/api/v1/versions/files/1/versions", "Version Control - List Versions"),
    
    # Undo/Redo
    ("GET", "/api/v1/history/operations/history/1", "Undo/Redo - Get History"),
    
    # Export
    ("POST", "/api/v1/export/pdf/1", "Export - PDF"),
    ("POST", "/api/v1/export/excel/1", "Export - Excel"),
    ("POST", "/api/v1/export/png/chart", "Export - PNG Chart"),
    
    # Sharing
    ("POST", "/api/v1/sharing/share", "Sharing - Create Share Link"),
    
    # Scheduled Reports
    ("GET", "/api/v1/reports/schedules", "Scheduled Reports - List"),
    
    # Data Sources
    ("POST", "/api/v1/datasources/test", "Data Sources - Test Connection"),
    
    # Advanced Charts (would be called via viz endpoints)
    ("GET", "/api/v1/viz/charts", "Visualization - Charts"),
]

print("\nChecking endpoint registration...")
print("-" * 60)

# Get all routes
routes = []
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        for method in route.methods:
            routes.append(f"{method} {route.path}")

# Check our endpoints
registered = 0
for method, path, description in endpoints:
    route_key = f"{method} {path}"
    # Check if exact match or pattern match
    is_registered = any(route_key in r or path.split('/')[-2] in r for r in routes)
    
    status = "✅" if is_registered else "⚠️"
    print(f"{status} {description}")
    print(f"   {method} {path}")
    if is_registered:
        registered += 1

print("-" * 60)
print(f"\nRegistered: {registered}/{len(endpoints)} endpoints")

# Show all API routes
print("\n" + "=" * 60)
print("ALL REGISTERED API ROUTES")
print("=" * 60)

api_routes = [r for r in routes if '/api/v1/' in r]
api_routes.sort()

categories = {}
for route in api_routes:
    # Extract category from route
    parts = route.split('/')
    if len(parts) >= 4:
        category = parts[3]  # api/v1/CATEGORY/...
        if category not in categories:
            categories[category] = []
        categories[category].append(route)

for category, routes in sorted(categories.items()):
    print(f"\n{category.upper()}:")
    for route in sorted(set(routes))[:5]:  # Show first 5
        print(f"  {route}")
    if len(routes) > 5:
        print(f"  ... and {len(routes) - 5} more")

print("\n" + "=" * 60)
print("FEATURE STATUS")
print("=" * 60)

features_status = {
    "Version Control": "versions" in str(categories.keys()),
    "Undo/Redo": "history" in str(categories.keys()),
    "Export": "export" in str(categories.keys()),
    "Sharing": "sharing" in str(categories.keys()),
    "Scheduled Reports": "reports" in str(categories.keys()),
    "Data Sources": "datasources" in str(categories.keys()),
    "Visualization": "viz" in str(categories.keys()),
}

for feature, status in features_status.items():
    icon = "✅" if status else "❌"
    print(f"{icon} {feature}: {'Registered' if status else 'Not Found'}")

print("\n" + "=" * 60)
