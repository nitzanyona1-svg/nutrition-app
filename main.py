# main.py
import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from services.database import DatabaseService
from services.nutrition_logic import NutritionManager
from datetime import date
from dotenv import load_dotenv

# טעינת משתנים
load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# חיבור
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Missing Supabase credentials!")

db = DatabaseService(SUPABASE_URL, SUPABASE_KEY)
nutrition = NutritionManager(db) # מאתחלים את ה-Manager עם ה-db

@app.get("/tab/dashboard")
def get_dashboard(request: Request):
    today_str = str(date.today())
    summary = nutrition.get_daily_summary(today_str)
    goals = nutrition.get_goals()
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_cal": summary["calories"],
        "total_prot": summary["protein"],
        "cal_left": max(goals["calories"] - summary["calories"], 0),
        "prot_left": max(goals["protein"] - summary["protein"], 0),
        "active_tab": "dashboard"
    })

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("layout.html", {"request": request, "active_tab": "dashboard"})

@app.post("/profile/save")
def save_profile(weight_kg: float = Form(...), height_cm: float = Form(...), 
                 target_weight_kg: float = Form(...), target_date: str = Form(...), 
                 custom_calories: int = Form(...), custom_protein: int = Form(...)):
    
    updated_data = {
        "weight_kg": weight_kg, "height_cm": height_cm, 
        "target_weight_kg": target_weight_kg, "target_date": target_date, 
        "custom_calories": custom_calories, "custom_protein": custom_protein
    }
    db.update_profile(updated_data)
    return {"status": "success"}