# models/nutrition_calculator.py
from datetime import date

class NutritionCalculator:
    @staticmethod
    def calculate_targets(weight: float, height: float, target_weight: float, target_date: date) -> tuple:
        """
        מחשב יעד קלוריות וחלבונים בסיסי על סמך נוסחת גרעון/עודף קלורי להגעה ליעד בזמן מוגדר.
        """
        days_remaining = (target_date - date.today()).days
        if days_remaining <= 0:
            return 2000, 150 # ברירת מחדל אם התאריך עבר
        
        # חישוב BMR בסיסי (נוסחת האריס-בנדיקט מקוצרת)
        bmr = (10 * weight) + (6.25 * height) - (5 * 25) + 5 # הערכה כללית למפתח
        tdee = bmr * 1.375 # מכפיל פעילות קלה
        
        weight_diff = target_weight - weight
        if weight_diff == 0:
            calories = int(tdee)
        else:
            # קילוגרם שומן שווה ערך לכ-7700 קלוריות
            total_calories_needed = weight_diff * 7700
            daily_change = total_calories_needed / days_remaining
            calories = int(tdee + daily_change)
            
        # הגבלת מינימום ומקסימום בריאותי מוגדר
        calories = max(min(calories, 4000), 1200)
        # חלבון מומלץ: כ-1.8 גרם לכל קילו משקל גוף
        protein = int(weight * 1.8)
        
        return calories, protein