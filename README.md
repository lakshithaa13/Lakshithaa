# PocketSmart AI — Your Smart Budget Recommendation Assistant

> **"Plan smarter. Spend better."**  
> A GenAI-powered budgeting and smart recommendation web application built with **FastAPI**, **Google Gemini Flash**, and **SQLite**.

---

## 📌 Project Overview

**PocketSmart AI** helps users make financially smart decisions by automatically partitioning their spending ceiling, allocating contingency reserves, and generating curated shopping recommendations.

The application addresses three high-value personal finance domains:
1. 🛋️ **Home Interior Planning** — Balances seating, lighting, decor, storage, and contingency funds for living rooms, bedrooms, kitchens, and full apartments.
2. 🎉 **Party & Event Planning** — Dynamically calculates per-guest catering budgets, venue allocations, decoration kits, and sound systems for birthdays, weddings, farewells, and college events.
3. 💎 **Jewelry Styling Assistant** — Combines text styling requests with **Gemini Multimodal Vision AI** to analyze uploaded outfit photos (extracting colors, silhouettes, and formality) and curating matching jewelry.

---

## 🚀 Key Features

* **Intelligent Budget Partitioning**: Automatically breaks down total budgets across essential categories while strictly preserving a 5–10% safety buffer.
* **Google Gemini Flash Integration**: Uses Google's official `google-genai` SDK with structured JSON schemas for fast, contextual reasoning.
* **Multimodal Vision Styling**: Upload an outfit image (PNG/JPG/WEBP); Gemini analyzes colors and necklines to match necklace, earring, and bangle pieces without storing personal biometric data.
* **100% Reliable Offline Fallback**: If no API key is provided or if network/quota issues occur, an intelligent local heuristics engine automatically takes over so your project demonstration never fails.
* **Legitimate Search Links**: Generates genuine search queries on Amazon, Flipkart, Pepperfry, Urban Ladder, Tanishq, CaratLane, Zomato, and Swiggy rather than fabricating invalid product URLs.
* **User Authentication & Private History**: Passwords hashed with salted `bcrypt`, session management via secure `JWT` cookies, and SQLite history tracking per user.
* **Modern SaaS Interface**: Clean responsive layout featuring a dark obsidian theme, glassmorphism, Google Fonts (*Outfit* & *Plus Jakarta Sans*), animated loading states, and printable summaries.

---

## 🏗️ Architecture & Project Structure

The project follows a clean **Layered Architecture (Separation of Concerns)** that is easy to explain during college project reviews and viva presentations:

```
PocketSmart-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI application factory & routes
│   │   ├── database.py                 # SQLite engine & session management
│   │   ├── models.py                   # SQLAlchemy ORM models (User, History)
│   │   ├── schemas.py                  # Pydantic validation schemas
│   │   │
│   │   ├── routers/                    # Modular FastAPI routers
│   │   │   ├── auth.py                 # Register, Login, Logout, Session
│   │   │   ├── home.py                 # Home Interior planner & generator
│   │   │   ├── party.py                # Party planner & catering breakdown
│   │   │   ├── jewelry.py              # Jewelry planner & Vision upload
│   │   │   └── history.py              # User recommendation archive & delete
│   │   │
│   │   ├── services/                   # Business logic layer
│   │   │   ├── gemini_service.py       # Google GenAI integration & fallbacks
│   │   │   ├── budget_service.py       # Math allocations & budget limits
│   │   │   └── recommendation_service.py # Orchestrates generation & history
│   │   │
│   │   ├── utils/                      # Helper utilities
│   │   │   ├── auth.py                 # Bcrypt hashing & JWT verification
│   │   │   └── prompts.py              # Structured prompts & search URL generator
│   │   │
│   │   └── templates/                  # Jinja2 HTML responsive templates
│   │       ├── base.html               # Shared layout, navbar, CSS & loading overlay
│   │       ├── index.html              # SaaS landing page with testimonials
│   │       ├── login.html              # User login
│   │       ├── register.html           # User registration
│   │       ├── dashboard.html          # Stats, recent plans & quick actions
│   │       ├── home_planner.html       # Home interior input form
│   │       ├── home_results.html       # Home budget breakdown & product cards
│   │       ├── party_planner.html      # Party planner input form
│   │       ├── party_results.html      # Event budget & catering breakdown
│   │       ├── jewelry_planner.html    # Jewelry input form + image drag-and-drop
│   │       ├── jewelry_results.html    # Jewelry cards + outfit vision analysis
│   │       └── history.html            # User recommendation archive
│   │
│   ├── uploads/                        # Uploaded outfit images (.gitignore applied)
│   ├── test_routes.py                  # End-to-end integration test suite
│   ├── test_image_upload.py            # Image upload verification test
│   ├── .env.example                    # Environment template
│   ├── .env                            # Active environment configuration
│   ├── requirements.txt                # Python package dependencies
│   └── run.py                          # Application startup script
│
├── README.md                           # Documentation
└── .gitignore                          # Git exclusions
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend Framework** | Python 3.10+ / 3.14, FastAPI, Uvicorn (ASGI) |
| **Database & ORM** | SQLite, SQLAlchemy 2.0 |
| **Data Validation** | Pydantic v2, Email-Validator |
| **AI & Multimodal** | Google Gemini Flash (`google-genai` SDK), Pillow (PIL) |
| **Security & Auth** | Bcrypt (salted hashing), PyJWT (HS256 tokens in HTTP-only cookies) |
| **Frontend & UI** | HTML5, CSS3 (Custom Design System), Vanilla JS, Jinja2 Templates |

---

## ⚙️ Quick Start Installation (Windows)

### 1. Open Terminal & Navigate to Project
```powershell
cd c:\Users\sweth\Documents\PocketSmart-AI\backend
```

### 2. Create & Activate Virtual Environment
```powershell
# Create virtual environment
python -m venv venv

# Activate on Windows PowerShell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` or use Command Prompt: `venv\Scripts\activate.bat`)*

### 3. Install Required Dependencies
```powershell
pip install -r requirements.txt
```

---

## 🔑 Where to Paste Your Gemini API Key

You configure your API key in the file **`PocketSmart-AI/backend/.env`**.

1. Open `backend/.env` in any text editor.
2. Replace `your_gemini_api_key_here` with your actual Google Gemini API key:

```env
# backend/.env
GEMINI_API_KEY=AIzaSyYourActualKeyHere1234567890
SECRET_KEY=pocketsmart_ai_super_secret_jwt_key_2025_college_demo_secure
DATABASE_URL=sqlite:///./pocketsmart.db
```

> **Note**: Even if you don't have a Gemini API key ready immediately, the application will automatically run in **High-Quality Demonstration Fallback Mode** with calculated budget partitions and curated recommendations. Once you paste your key, it automatically switches to live Gemini Flash generation!

---

## ▶️ Running the Application

From within the `backend/` directory with the virtual environment activated:

```powershell
python run.py
```
*Alternatively, you can run directly with uvicorn:*
```powershell
uvicorn app.main:app --reload --port 8000
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🧪 Running the Automated Verification Tests

The project includes built-in verification test suites verifying all 11 core routes, authentication, database persistence, and image uploads:

```powershell
cd backend
python test_routes.py
python test_image_upload.py
```

Both tests should display:
```
========================================================
SUCCESS: ALL 11 PIPELINE TESTS PASSED COMPLETELY!
========================================================
```

---

## 📋 API & Web Endpoints

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/` | Polished SaaS Landing Page | No |
| `GET` | `/register` | User Registration Form | No |
| `POST` | `/register` | Creates User, Hashes Password, Sets Session Cookie | No |
| `GET` | `/login` | User Login Form | No |
| `POST` | `/login` | Authenticates User, Sets Session Cookie | No |
| `GET` | `/logout` | Clears Session Cookie & Redirects | No |
| `GET` | `/session-info` | Returns JSON status of current user | No |
| `GET` | `/dashboard` | User Dashboard with Statistics & Recent Plans | **Yes** |
| `GET` | `/home-planner` | Home Interior Planning Form | **Yes** |
| `POST` | `/generate-home` | Runs Budget Partitioning & Gemini Home Recommendations | **Yes** |
| `GET` | `/party-planner` | Party & Event Planning Form | **Yes** |
| `POST` | `/generate-party` | Calculates Dynamic Per-Guest Allocation & Event Kits | **Yes** |
| `GET` | `/jewelry-planner` | Jewelry Form & Multimodal Outfit Upload | **Yes** |
| `POST` | `/generate-jewelry` | Multimodal Vision Outfit Match & Jewelry Recommendations | **Yes** |
| `GET` | `/history` | User's Saved Recommendation Archive | **Yes** |
| `GET` | `/history/{id}` | Inspect Detailed View of a Previously Generated Plan | **Yes** |
| `POST` | `/history/{id}/delete`| Deletes a Saved Plan | **Yes** |

---

## 💡 Example Workflows for Demonstration

### 1. Home Interior Demonstration
1. Register or Log in.
2. Click **Home Interior** from the navigation bar or dashboard.
3. Enter Budget: `₹75,000`, Room Type: `Living Room`, Style: `Modern`.
4. Specify quantities: `1 Sofa`, `2 Chairs`, `2 Lamps`, `1 Storage Shelf`.
5. Click **Generate Home Plan with Gemini**.
6. Observe:
   - Dynamic budget allocation bar across Furniture, Lighting, Decor, Storage, and Contingency Reserve.
   - 4–6 curated product cards with realistic prices, style tags, and "Search on Amazon / Pepperfry" links.

### 2. Party & Event Demonstration
1. Click **Party Planner**.
2. Enter Budget: `₹40,000`, Event: `Birthday Party`, Guests: `35`, Location: `Bangalore`.
3. Select `Both (Veg & Non-Veg)`, Decor: `Standard`, Entertainment: `Basic`.
4. Click **Generate Event Budget with Gemini**.
5. Observe:
   - Calculated per-guest catering budget (`~₹450 / guest`).
   - Venue, Decor, Sound, and Contingency splits.
   - Recommended buffet catering, theme balloon kits, and speaker packages with links to Zomato, Swiggy, and Amazon.

### 3. Jewelry & Multimodal Vision Demonstration
1. Click **Jewelry Styling**.
2. Enter Budget: `₹20,000`, Occasion: `Wedding`, Style: `Traditional`.
3. *(Optional)* Drag and drop an outfit image (saree or gown photo) into the upload box.
4. Add description: *"Maroon Banarasi silk saree with gold border"*.
5. Click **Match Jewelry with Gemini**.
6. Observe:
   - Vision AI output detailing dominant colors, formality, and neckline styling advice.
   - Curated choker necklace, earrings, and bangles with direct search links to Tanishq, CaratLane, and Myntra.

---

## 🔒 Security Best Practices Implemented

* **Password Security**: Passwords are never stored in plaintext. They are salted and hashed using `bcrypt` (with automatic PBKDF2 SHA-256 fallback).
* **JWT Cookie Authentication**: JSON Web Tokens are stored in `HttpOnly` and `SameSite=Lax` cookies, mitigating XSS and CSRF exposure.
* **File Upload Protections**: Image uploads are validated for allowed MIME types (`.jpg`, `.jpeg`, `.png`, `.webp`), capped at 5MB, and stored using secure UUID filenames to prevent path traversal.
* **Zero Hardcoded Secrets**: All API keys, secrets, and database paths are loaded strictly via `.env`.
* **Graceful Exception Handling**: Custom HTTP 404/500 handlers ensure users never see raw internal stack traces.

---

## 🎓 College Viva / Demonstration Talking Points

1. **How is the budget enforced?**
   The `budget_service.py` module applies a strict boundary check (`enforce_budget_limit`). It calculates running sums and adjusts or filters candidate recommendations so the total cost never surpasses the user's defined ceiling.
2. **What happens if Gemini is throttled or offline?**
   `gemini_service.py` catches API exceptions or missing keys and triggers dynamic algorithmic fallbacks (`get_home_fallback`, `get_party_fallback`, `get_jewelry_fallback`). The UI clearly labels fallback mode without breaking.
3. **How does multimodal image analysis work?**
   The uploaded file is validated and converted into a `PIL.Image` object, then passed directly into Gemini Flash along with a tailored styling prompt requesting strict JSON.
4. **Why SQLite and FastAPI?**
   FastAPI provides asynchronous request handling, high throughput, and automatic OpenAPI documentation. SQLite provides zero-configuration local persistence that requires no external database servers to be installed.

---

## 📜 License

Created for academic and demonstration purposes. All rights reserved.
