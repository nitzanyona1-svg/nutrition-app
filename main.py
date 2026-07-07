# main.py
import os
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from services.database import DatabaseService
from services.nutrition_logic import NutritionManager
from datetime import date
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

app = FastAPI()
templates = Jinja2Templates(directory="templates")

if SUPABASE_URL and SUPABASE_KEY:
    db = DatabaseService(SUPABASE_URL, SUPABASE_KEY)
    nutrition = NutritionManager(db)
else:
    print("CRITICAL WARNING: Supabase credentials are missing!")
    db = None
    nutrition = None

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse(request=request, name="layout.html", context={"active_tab": "dashboard"})

@app.get("/tab/dashboard")
def get_dashboard(request: Request):
    if not nutrition:
        return HTMLResponse("שגיאה: מסד הנתונים לא מחובר.")
        
    today_str = str(date.today())
    summary = nutrition.get_daily_summary(today_str)
    goals = nutrition.get_goals()
    
    cal_left = max(goals["calories"] - summary["calories"], 0)
    prot_left = max(goals["protein"] - summary["protein"], 0)
    
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "total_cal": summary["calories"],
        "total_prot": summary["protein"],
        "cal_left": cal_left,
        "prot_left": prot_left,
        "active_tab": "dashboard"
    })

@app.get("/tab/diary")
def get_diary(request: Request, selected_date: str = str(date.today())):
    if not nutrition:
        return HTMLResponse("שגיאה: מסד הנתונים לא מחובר.")
        
    summary = nutrition.get_daily_summary(selected_date)
    return templates.TemplateResponse(request=request, name="diary.html", context={
        "meals": summary["meals"],
        "selected_date": selected_date,
        "active_tab": "diary"
    })

# --- הפונקציה החדשה שקולטת ארוחה מהטופס ---
@app.post("/diary/add")
def add_meal_to_diary(request: Request, 
                      food_name: str = Form(...), 
                      calories: int = Form(...), 
                      protein: float = Form(...), 
                      selected_date: str = Form(...)):
    if not db:
        return HTMLResponse("שגיאה: מסד הנתונים לא מחובר.")
        
    meal_data = {
        "date": selected_date,
        "food_name": food_name,
        "calories": calories,
        "protein": protein
    }
    db.add_meal_to_diary(meal_data)
    
    # מיד אחרי השמירה, טוענים מחדש את יומן התזונה המעודכן
    summary = nutrition.get_daily_summary(selected_date)
    return templates.TemplateResponse(request=request, name="diary.html", context={
        "meals": summary["meals"],
        "selected_date": selected_date,
        "active_tab": "diary"
    })

@app.get("/tab/pantry")
def get_pantry(request: Request):
    if not db:
        return HTMLResponse("שגיאה: מסד הנתונים לא מחובר.")
        
    products = db.get_pantry_products()
    return templates.TemplateResponse(request=request, name="pantry.html", context={
        "products": products,
        "active_tab": "pantry"
    })

@app.get("/tab/profile")
def get_profile(request: Request):
    if not db:
        return HTMLResponse("שגיאה: מסד הנתונים לא מחובר.")
        
    profile = db.get_profile() or {}
    return templates.TemplateResponse(request=request, name="profile.html", context={
        "profile": profile,
        "active_tab": "profile"
    })

@app.post("/profile/save")
def save_profile(weight_kg: float = Form(...), height_cm: float = Form(...), 
                 target_weight_kg: float = Form(...), target_date: str = Form(...), 
                 custom_calories: int = Form(...), custom_protein: int = Form(...)):
    
    if not db:
        return {"status": "error", "message": "No DB connection"}

    updated_data = {
        "weight_kg": weight_kg, "height_cm": height_cm, 
        "target_weight_kg": target_weight_kg, "target_date": target_date, 
        "custom_calories": custom_calories, "custom_protein": custom_protein
    }
    db.update_profile(updated_data)
    return {"status": "success"}