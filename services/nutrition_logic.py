# services/nutrition_logic.py
from datetime import date

class NutritionManager:
    def __init__(self, db_service):
        self.db = db_service

    def get_daily_summary(self, today_str):
        meals = self.db.get_diary_by_date(today_str)
        total_cal = sum(item["calories"] for item in meals)
        total_prot = sum(item["protein"] for item in meals)
        return {"calories": total_cal, "protein": total_prot}

    def get_goals(self):
        profile = self.db.get_profile() or {}
        return {
            "calories": profile.get('custom_calories', 2000),
            "protein": profile.get('custom_protein', 150)
        }