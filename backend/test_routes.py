import os
import sys
import uuid

# Ensure stdout handles utf-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi.testclient import TestClient
from app.main import app
from app.database import init_db

init_db()
client = TestClient(app)

def test_full_pipeline():
    print("[1/11] Testing GET / (Landing Page)...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "PocketSmart" in res.text
    print("  -> Landing page OK")

    print("[2/11] Testing GET /login & /register...")
    res = client.get("/login")
    assert res.status_code == 200
    res = client.get("/register")
    assert res.status_code == 200
    print("  -> Auth pages OK")

    print("[3/11] Testing User Registration (POST /register)...")
    random_email = f"user_{uuid.uuid4().hex[:8]}@example.com"
    reg_data = {
        "name": "Swetha",
        "email": random_email,
        "password": "password123",
        "confirm_password": "password123"
    }
    res = client.post("/register", data=reg_data, follow_redirects=False)
    assert res.status_code in (302, 303), f"Expected redirect, got {res.status_code}"
    assert "access_token" in res.cookies
    token_cookie = res.cookies["access_token"]
    print("  -> Registration successful, JWT cookie issued")

    # Set cookie on test client for subsequent requests
    client.cookies.set("access_token", token_cookie)

    print("[4/11] Testing GET /dashboard with auth...")
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert "Swetha" in res.text
    print("  -> Dashboard authenticated successfully")

    print("[5/11] Testing GET /home-planner...")
    res = client.get("/home-planner")
    assert res.status_code == 200
    print("  -> Home planner form page OK")

    print("[6/11] Testing POST /generate-home...")
    home_data = {
        "budget": 50000,
        "currency": "₹",
        "room_type": "Living Room",
        "style": "Modern",
        "sofa_qty": 1,
        "bed_qty": 0,
        "dining_table_qty": 0,
        "chairs_qty": 2,
        "lights_qty": 2,
        "ceiling_fan_qty": 1,
        "curtains_qty": 2,
        "storage_qty": 1,
        "decor_qty": 2,
        "custom_requirements": "Spacious and modern with neutral accents"
    }
    res = client.post("/generate-home", data=home_data)
    assert res.status_code == 200
    assert "Estimated price" in res.text
    assert "Smart Budget Allocation" in res.text
    print("  -> Home recommendations generated and rendered OK")

    print("[7/11] Testing GET /party-planner...")
    res = client.get("/party-planner")
    assert res.status_code == 200
    print("  -> Party planner form page OK")

    print("[8/11] Testing POST /generate-party...")
    party_data = {
        "budget": 35000,
        "currency": "₹",
        "event_type": "Birthday",
        "guest_count": 25,
        "location": "Bangalore",
        "venue_requirement": "Needed",
        "food_preference": "Both",
        "decoration_level": "Standard",
        "entertainment": "Basic",
        "additional_requirements": "Chocolate theme cake needed"
    }
    res = client.post("/generate-party", data=party_data)
    assert res.status_code == 200
    assert "Budget Strategy" in res.text
    print("  -> Party recommendations generated and rendered OK")

    print("[9/11] Testing GET /jewelry-planner...")
    res = client.get("/jewelry-planner")
    assert res.status_code == 200
    print("  -> Jewelry planner form page OK")

    print("[10/11] Testing POST /generate-jewelry (without image)...")
    jewelry_data = {
        "budget": 18000,
        "currency": "₹",
        "occasion": "Wedding",
        "style": "Traditional",
        "jewelry_type": "Full Set",
        "preferred_color_material": "Gold & Pearls",
        "outfit_description": "Emerald green silk saree with gold border"
    }
    res = client.post("/generate-jewelry", data=jewelry_data)
    assert res.status_code == 200
    assert "Jewelry Collection" in res.text
    print("  -> Jewelry recommendations generated and rendered OK")

    print("[11/11] Testing History & Session Endpoints...")
    res = client.get("/history")
    assert res.status_code == 200
    assert "Saved Recommendation History" in res.text
    print("  -> History list retrieved OK")

    res = client.get("/session-info")
    assert res.status_code == 200
    data = res.json()
    assert data["authenticated"] is True
    assert data["user"]["email"] == random_email
    print("  -> Session info endpoint OK")

    res = client.get("/logout", follow_redirects=False)
    assert res.status_code in (302, 303)
    print("  -> Logout OK")

    print("\n========================================================")
    print("SUCCESS: ALL 11 PIPELINE TESTS PASSED COMPLETELY!")
    print("========================================================")

if __name__ == "__main__":
    test_full_pipeline()
