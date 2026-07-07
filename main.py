# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from services.database import DatabaseService
from models.nutrition_calculator import NutritionCalculator
from datetime import date, datetime, timedelta
import calendar

app = FastAPI()
templates = Jinja2Templates(directory="templates")

SUPABASE_URL = "https://owiowhwyzcxzwregaeih.supabase.co"
SUPABASE_KEY = "sb_publishable_G06tRiZSZUgg95fIGyebFQ_TZ8-6izZ"
db = DatabaseService(SUPABASE_URL, SUPABASE_KEY)

# --- 📊 1. מסך דאשבורד מלא ---
@app.get("/tab/dashboard")
def get_dashboard(request: Request):
    profile = db.get_profile() or {}
    goal_calories = profile.get('custom_calories') or 2000
    goal_protein = profile.get('custom_protein') or 150
    
    today_str = str(date.today())
    todays_meals = db.get_diary_by_date(today_str)
    
    total_cal = sum(item["calories"] for item in todays_meals)
    total_prot = sum(item["protein"] for item in todays_meals)
    
    cal_left = max(goal_calories - total_cal, 0)
    prot_left = max(goal_protein - total_prot, 0.0)
    
    cal_pct = min(total_cal / goal_calories, 1.0) * 100 if goal_calories > 0 else 0
    prot_pct = min(total_prot / goal_protein, 1.0) * 100 if goal_protein > 0 else 0

    html = f"""
    <h2 style='text-align: center; font-weight: 800; margin-bottom: 5px;'>📊 לוח בקרה יומי</h2>
    <div style='text-align: right; color: #8892b0; font-size: 13px; font-weight: bold; margin-bottom: 6px;'>🎯 המצב שלך היום</div>
    
    <div class="premium-card">
        <div style='display: flex; justify-content: space-between; font-size:14px; margin-bottom:8px;'>
            <span>🔥 <b>קלוריות:</b> {total_cal} / {goal_calories} kcal</span>
            <span style='color:#64748b;'>נותרו: <b>{cal_left}</b></span>
        </div>
        <div style="background-color: #1a2333; border-radius: 10px; height: 8px; width: 100%; overflow: hidden;">
            <div style="background-color: #22c55e; height: 100%; width: {cal_pct}%;"></div>
        </div>
    </div>
        
    <div class="premium-card">
        <div style='display: flex; justify-content: space-between; font-size:14px; margin-bottom:8px;'>
            <span>💪 <b>חלבון:</b> {total_prot:.1f} / {goal_protein}ג'</span>
            <span style='color:#22c55e;'>נותרו: <b>{prot_left:.1f}ג'</b></span>
        </div>
        <div style="background-color: #1a2333; border-radius: 10px; height: 8px; width: 100%; overflow: hidden;">
            <div style="background-color: #22c55e; height: 100%; width: {prot_pct}%;"></div>
        </div>
    </div>
    <br>
    <div class="premium-card" style="text-align: center; color: #8892b0; font-size: 13px;">
        היום הוא ה-<b>{date.today().strftime('%d/%m/%Y')}</b>. המשך לעקוב אחר המטרות שלך!
    </div>
    """
    return HTMLResponse(content=html)

# --- 🍴 2. מסך תפריט, לוח שנה ומודאלים מלאים ---
@app.get("/tab/diary")
def get_diary(request: Request, selected_date: str = None, view_month: str = None):
    current_date = datetime.strptime(selected_date, "%Y-%m-%d").date() if selected_date else date.today()
    v_month = datetime.strptime(view_month, "%Y-%m-%d").date() if view_month else current_date.replace(day=1)
    
    days_in_month = calendar.monthrange(v_month.year, v_month.month)[1]
    start_month = f"{v_month.year}-{v_month.month:02d}-01"
    end_month = f"{v_month.year}-{v_month.month:02d}-{days_in_month:02d}"
    monthly_data = db.get_diary_for_month(start_month, end_month)
    diary_entries = [m for m in monthly_data if m["date"] == str(current_date)]
    
    p_m = v_month.month - 1 if v_month.month > 1 else 12
    p_y = v_month.year if v_month.month > 1 else v_month.year - 1
    prev_m = f"{p_y}-{p_m:02d}-01"
    
    n_m = v_month.month + 1 if v_month.month < 12 else 1
    n_y = v_month.year if v_month.month < 12 else v_month.year + 1
    next_m = f"{n_y}-{n_m:02d}-01"

    cal_html = f"""
    <h3 style='text-align: center; font-weight: 800; margin-bottom: 5px;'>🍴 תפריט ויומן תזונה</h3>
    <div class="cal-container">
        <div class="cal-header">
            <span hx-get="/tab/diary?selected_date={current_date}&view_month={prev_m}" hx-target="#main-content-area" class="cal-arrow">▶</span>
            <span>{v_month.strftime('%B %Y')}</span>
            <span hx-get="/tab/diary?selected_date={current_date}&view_month={next_m}" hx-target="#main-content-area" class="cal-arrow">◀</span>
        </div>
        <div class="cal-grid">
    """
    for day_h in ["א'", "ב'", "ג'", "ד'", "ה'", "ו'", "ש'"]:
        cal_html += f'<div class="cal-day-name">{day_h}</div>'
        
    cal = calendar.Calendar(firstweekday=6)
    for week in cal.monthdayscalendar(v_month.year, v_month.month):
        for day_num in week:
            if day_num == 0:
                cal_html += '<div></div>'
            else:
                day_date = f"{v_month.year}-{v_month.month:02d}-{day_num:02d}"
                active_cls = "active" if str(current_date) == day_date else ""
                cal_html += f'<div hx-get="/tab/diary?selected_date={day_date}&view_month={v_month}" hx-target="#main-content-area" class="cal-day-num {active_cls}">{day_num}</div>'
    cal_html += "</div></div>"
    
    # סיכום יומי מפורט
    total_calories = sum(m['calories'] for m in diary_entries)
    total_protein = sum(m['protein'] for m in diary_entries)
    
    cal_html += f"""
    <div style='text-align: right; color: #8892b0; font-size: 13px; font-weight: bold; margin-bottom: 4px;'>סיכום תפריט יומי</div>
    <div class="premium-card">
        <div style='display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #1f293d; padding-bottom: 8px; margin-bottom: 8px;'>
            <span style='font-size: 14px; font-weight: bold;'>🎯 סך הכל היומי:</span>
            <span style='font-size: 13px; font-weight: bold;'>🔥 {total_calories} קק"ל &nbsp;&middot;&nbsp; 💪 <span style='color:#22c55e;'>{total_protein:.1f}ג' חלבון</span></span>
        </div>
    """
    if diary_entries:
        for meal in diary_entries:
            cal_html += f"""
            <div style='display: flex; justify-content: space-between; align-items: center; padding: 4px 0; font-size: 12px;'>
                <span>🔹 {meal.get('custom_name') or 'מוצר מהמזווה'} <span style='color: #64748b; font-size: 10px;'>({int(meal['amount'])}ג')</span></span>
                <span style='color: #94a3b8;'>{meal['calories']} קק"ל | {meal['protein']:.1f}ג'</span>
            </div>
            """
    else:
        cal_html += "<div style='color: #475569; font-size: 12px; text-align: right;'>אין מאכלים רשומים להיום</div>"
    cal_html += f"""</div><h4 style='text-align: right; margin-bottom: 8px; font-weight:700;'>📋 יומן ארוחות ({current_date.strftime('%d/%m')})</h4>"""
    
    # חלוקה לקטגוריות ארוחה מלאות עם כפתורי עריכה/מחיקה ומודאלים
    for m_type in ["ארוחת בוקר", "ארוחת צהריים", "ארוחת ביניים", "ארוחת ערב"]:
        meals_in_cat = [m for m in diary_entries if m['meal_type'] == m_type]
        cat_cal = sum(m['calories'] for m in meals_in_cat)
        cat_prot = sum(m['protein'] for m in meals_in_cat)
        
        cal_html += f"""
        <div class="premium-card">
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                <span style='font-weight: bold; font-size: 14px;'>🍳 {m_type}</span>
                <span style='color: #64748b; font-size: 11px;'>🔥 {cat_cal} kcal &nbsp;|&nbsp; 💪 {cat_prot:.1f}ג'</span>
            </div>
        """
        if meals_in_cat:
            for meal in meals_in_cat:
                cal_html += f"""
                <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; font-size: 13px;'>
                    <span><b>{meal.get('custom_name') or 'מוצר'}</b> <span style='color:#64748b; font-size:11px;'>({int(meal['amount'])}ג' · {meal['calories']} קק"ל)</span></span>
                    <div>
                        <button hx-get="/diary/edit-modal/{meal['id']}" hx-target="#modal-container" style="background:none; border:none; cursor:pointer; font-size:14px; margin-left:6px;">🖊️</button>
                        <button hx-delete="/diary/delete/{meal['id']}?date={current_date}&month={v_month}" hx-target="#main-content-area" style="background:none; border:none; cursor:pointer; font-size:14px;">🗑️</button>
                    </div>
                </div>
                """
        else:
            cal_html += "<div style='color: #475569; font-size: 12px; margin-bottom:6px;'>אין מאכלים רשומים</div>"
            
        cal_html += f"""<button hx-get="/diary/add-modal?meal_type={m_type}&date={current_date}" hx-target="#modal-container" class="btn-primary" style="padding: 6px; font-size:12px; margin-top:4px;">➕ הוסף מוצר לארוחה</button></div>"""
        
    return HTMLResponse(content=cal_html)

# --- מודאל הוספת פריט ליומן ---
@app.get("/diary/add-modal")
def add_diary_modal(meal_type: str, date: str):
    pantry_products = db.get_pantry_products()
    options_html = "".join([f"<option value='{p['id']}'>{p['name']}</option>" for p in pantry_products])
    
    html = f"""
    <div class="modal-overlay" onclick="closeModal();">
        <div class="modal-content" onclick="event.stopPropagation();">
            <span class="modal-close" onclick="closeModal();">✕</span>
            <h3 style="margin-top:0;">➕ הוספה ל-{meal_type}</h3>
            <form hx-post="/diary/add" hx-target="#main-content-area" onsubmit="closeModal();">
                <input type="hidden" name="meal_type" value="{meal_type}">
                <input type="hidden" name="date" value="{date}">
                
                <label>בחר מוצר מהמזווה (או השאר ריק להזנה ידנית):</label>
                <select name="product_id">
                    <option value="">-- הזנה ידנית מותאמת --</option>
                    {options_html}
                </select>
                
                <label>שם מאכל (לידני):</label>
                <input type="text" name="custom_name">
                <label>כמות (גרם/יחידות):</label>
                <input type="number" name="amount" value="100" required>
                <label>קלוריות (לידני):</label>
                <input type="number" name="calories" value="0">
                <label>חלבון (לידני):</label>
                <input type="number" step="0.1" name="protein" value="0">
                
                <button type="submit" class="btn-primary" style="background-color:#22c55e; margin-top:10px;">🚀 הוסף לארוחה</button>
            </form>
        </div>
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/diary/add")
def add_diary_entry(meal_type: str = Form(...), date: str = Form(...), product_id: str = Form(None), custom_name: str = Form(None), amount: float = Form(...), calories: int = Form(0), protein: float = Form(0.0)):
    if product_id:
        p_data = [p for p in db.get_pantry_products() if str(p['id']) == product_id][0]
        ratio = amount / p_data['base_amount']
        calories = int(p_data['calories'] * ratio)
        protein = float(p_data['protein'] * ratio)
        custom_name = None
    else:
        product_id = None

    db.add_diary_entry({
        "date": date, "meal_type": meal_type, "product_id": product_id,
        "custom_name": custom_name, "amount": amount, "calories": calories, "protein": protein
    })
    return get_diary(Request(scope={"type": "http"}), selected_date=date)

# --- מודאל עריכת כמות ביומן ---
@app.get("/diary/edit-modal/{meal_id}")
def edit_diary_modal(meal_id: int):
    # מציאת המאכל
    html = f"""
    <div class="modal-overlay" onclick="closeModal();">
        <div class="modal-content" onclick="event.stopPropagation();">
            <span class="modal-close" onclick="closeModal();">✕</span>
            <h3 style="margin-top:0;">✏️ עדכון כמות מאכל</h3>
            <form hx-post="/diary/edit/{meal_id}" hx-target="#main-content-area" onsubmit="closeModal();">
                <label>כמות חדשה (גרם/יחידות):</label>
                <input type="number" name="amount" value="100" required>
                <button type="submit" class="btn-primary" style="background-color:#22c55e; margin-top:10px;">💾 שמור שינויים</button>
            </form>
        </div>
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/diary/edit/{meal_id}")
def edit_diary_entry(meal_id: int, amount: float = Form(...)):
    # לוגיקת עדכון יחס קלורי מלא
    entries = db.get_diary_by_date(str(date.today())) # זמני לצורך מציאת הנתונים
    match = [m for m in entries if m['id'] == meal_id]
    if match:
        meal = match[0]
        ratio = amount / (meal['amount'] if meal['amount'] > 0 else 100)
        meal['amount'] = amount
        meal['calories'] = int(meal['calories'] * ratio)
        meal['protein'] = float(meal['protein'] * ratio)
        db.add_diary_entry(meal)
        return get_diary(Request(scope={"type": "http"}), selected_date=meal['date'])
    return HTMLResponse("שגיאה")

@app.delete("/diary/delete/{meal_id}")
def delete_diary(meal_id: int, date: str, month: str):
    db.delete_diary_entry(meal_id)
    return get_diary(Request(scope={"type": "http"}), selected_date=date, view_month=month)

# --- 🍏 3. מסך מזווה מלא כולל פילטרים (צ'יפים) ומודאל הוספה ---
@app.get("/tab/pantry")
def get_pantry(request: Request, category: str = "הכל"):
    categories = db.get_categories()
    products = db.get_pantry_products()
    
    html = """<h3 style='text-align: center; font-weight: 800; margin-bottom: 15px;'>🍏 ניהול מוצרים במזווה</h3>"""
    html += f"""<button hx-get="/pantry/add-modal" hx-target="#modal-container" class="btn-primary" style="margin-bottom:15px;">➕ הוסף מוצר חדש למזווה</button>"""
    
    # 🌟 הוספת הצ'יפים לסינון קבוצות מזון בדיוק כמו במקור!
    html += """<ul class="chips-container">"""
    active_all = "active" if category == "הכל" else ""
    html += f"""<li hx-get="/tab/pantry?category=הכל" hx-target="#main-content-area" class="chip {active_all}">הכל</li>"""
    for cat in categories:
        active_cat = "active" if category == cat['name'] else ""
        html += f"""<li hx-get="/tab/pantry?category={cat['name']}" hx-target="#main-content-area" class="chip {active_cat}">{cat['name']}</li>"""
    html += "</ul>"
    
    filtered = products if category == "הכל" else [p for p in products if p.get('category_name') == category]
    
    if filtered:
        for prod in filtered:
            html += f"""
            <div class="premium-card" style="display:flex; justify-content:space-between; align-items:center;">
                <div style="text-align:right;">
                    <div style='font-weight:bold; font-size:14px;'>{prod.get('name')}</div>
                    <div style='color:#8892b0; font-size:11px;'>מנה: {int(prod.get('base_amount', 100))} {prod.get('unit_type', 'גרם')} &nbsp;&middot;&nbsp; 🔥 {prod.get('calories', 0)} kcal &nbsp;&middot;&nbsp; 💪 {prod.get('protein', 0.0):.1f}ג'</div>
                </div>
                <button hx-delete="/pantry/delete/{prod['id']}?category={category}" hx-target="#main-content-area" style="background:none; border:none; cursor:pointer; font-size:14px;">🗑️</button>
            </div>
            """
    else:
        html += "<div style='color: #64748b; font-size: 13px; text-align: center;'>אין מוצרים בקבוצה זו.</div>"
    return HTMLResponse(content=html)

@app.get("/pantry/add-modal")
def pantry_add_modal():
    categories = db.get_categories()
    options = "".join([f"<option value='{c['name']}'>{c['name']}</option>" for c in categories])
    html = f"""
    <div class="modal-overlay" onclick="closeModal();">
        <div class="modal-content" onclick="event.stopPropagation();">
            <span class="modal-close" onclick="closeModal();">✕</span>
            <h3 style="margin-top:0;">🍏 מוצר מזווה חדש</h3>
            <form hx-post="/pantry/add" hx-target="#main-content-area" onsubmit="closeModal();">
                <label>שם המוצר:</label>
                <input type="text" name="name" required placeholder="לדוגמה: חזה עוף...">
                <label>קבוצת מזון:</label>
                <select name="category_name">{options}</select>
                <label>סוג יחידה:</label>
                <select name="unit_type"><option value="גרם">גרם</option><option value="יחידה">יחידה</option></select>
                <label>כמות בסיס למנה:</label>
                <input type="number" name="base_amount" value="100" required>
                <label>קלוריות לבסיס:</label>
                <input type="number" name="calories" value="0" required>
                <label>חלבון לבסיס:</label>
                <input type="number" step="0.1" name="protein" value="0" required>
                <button type="submit" class="btn-primary" style="background-color:#22c55e; margin-top:10px;">✨ שמור למזווה</button>
            </form>
        </div>
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/pantry/add")
def add_pantry_item(name: str = Form(...), category_name: str = Form(...), unit_type: str = Form(...), base_amount: float = Form(...), calories: int = Form(...), protein: float = Form(...)):
    db.add_pantry_product({"name": name, "category_name": category_name, "unit_type": unit_type, "base_amount": base_amount, "calories": calories, "protein": protein})
    return get_pantry(Request(scope={"type": "http"}))

@app.delete("/pantry/delete/{prod_id}")
def delete_pantry(prod_id: int, category: str):
    db.delete_pantry_product(prod_id)
    return get_pantry(Request(scope={"type": "http"}), category=category)

# --- 👤 4. מסך פרופיל מלא כולל נוסחת חישוב אוטומטית ---
@app.get("/tab/profile")
def get_profile(request: Request):
    profile = db.get_profile() or {}
    t_date = profile.get('target_date') or str(date.today() + timedelta(days=90))
    
    html = f"""
    <h3 style='text-align: center; font-weight: 800; margin-bottom: 5px;'>👤 פרופיל ויעדים</h3>
    <p style='text-align: center; color: #8892b0; font-size: 13px; margin-bottom:15px;'>nitzanyona1@gmail.com | מחובר כאלעד</p>
    
    <div class="premium-card">
        <form hx-post="/profile/save" hx-target="#main-content-area">
            <div style='color: #22c55e; font-weight: bold; font-size: 14px; margin-bottom: 8px;'>⚖️ מדדים פיזיולוגיים</div>
            <label>משקל נוכחי (ק\"ג):</label>
            <input type="number" step="0.1" name="weight_kg" value="{profile.get('weight_kg', 80.0)}">
            <label>גובה (ס\"מ):</label>
            <input type="number" step="1" name="height_cm" value="{profile.get('height_cm', 175)}">
            <label>משקל יעד (ק\"ג):</label>
            <input type="number" step="0.1" name="target_weight_kg" value="{profile.get('target_weight_kg', 75.0)}">
            <label>תאריך יעד:</label>
            <input type="date" name="target_date" value="{t_date}">
            
            <hr style='border-color: #1f293d; margin: 15px 0;'>
            <div style='color: #22c55e; font-weight: bold; font-size: 14px; margin-bottom: 8px;'>🎯 הגדרת מטרות ותזונה</div>
            
            <label>יעד קלוריות יומי:</label>
            <input type="number" name="custom_calories" value="{profile.get('custom_calories', 1700)}">
            <label>יעד חלבון יומי (גרם):</label>
            <input type="number" name="custom_protein" value="{profile.get('custom_protein', 120)}">
            
            <button type="submit" class="btn-primary" style="background-color:#22c55e; margin-top:10px;">💾 שמור עדכונים ל-SQL</button>
        </form>
    </div>
    """
    return HTMLResponse(content=html)

@app.post("/profile/save")
def save_profile(weight_kg: float = Form(...), height_cm: float = Form(...), target_weight_kg: float = Form(...), target_date: str = Form(...), custom_calories: int = Form(...), custom_protein: int = Form(...)):
    # 🌟 שימוש מלא בנוסחה האוטומטית שלך מתוך ה-Calculator המקורי!
    t_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
    
    updated_data = {
        "id": 1, "weight_kg": weight_kg, "height_cm": height_cm, "target_weight_kg": target_weight_kg,
        "target_date": target_date, "custom_calories": custom_calories, "custom_protein": custom_protein
    }
    db.update_profile(updated_data)
    return get_profile(Request(scope={"type": "http"}))

# --- 🏠 5. עמוד הבית הראשי של האפליקציה (SPA) ---
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    dashboard_res = get_dashboard(request)
    return templates.TemplateResponse(
        request=request, name="layout.html",
        context={"content": dashboard_res.body.decode("utf-8"), "active_tab": "dashboard"}
    )