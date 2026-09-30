import os
import sys
import io
from PIL import Image

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_image_upload_pipeline():
    print("Testing image upload in Jewelry Planner...")
    
    # Register/login user
    reg_data = {
        "name": "ImageTester",
        "email": "img.test@example.com",
        "password": "password123",
        "confirm_password": "password123"
    }
    res = client.post("/register", data=reg_data, follow_redirects=False)
    client.cookies.set("access_token", res.cookies["access_token"])

    # Create dummy in-memory image
    img = Image.new("RGB", (200, 200), color=(180, 40, 60))
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    files = {
        "outfit_image": ("test_outfit.png", img_byte_arr, "image/png")
    }
    data = {
        "budget": 20000,
        "currency": "₹",
        "occasion": "Wedding",
        "style": "Traditional",
        "jewelry_type": "Full Set",
        "preferred_color_material": "Gold & Kundan",
        "outfit_description": "Red silk saree with gold border"
    }

    res = client.post("/generate-jewelry", data=data, files=files)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "Jewelry Collection" in res.text
    assert "/uploads/" in res.text
    print("  -> Jewelry planner with image upload verified successfully!")
    print("  -> Image was saved in uploads directory and thumbnail rendered in results!")

if __name__ == "__main__":
    test_image_upload_pipeline()
