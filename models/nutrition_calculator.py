# models/nutrition_calculator.py
from datetime import date

class NutritionCalculator:
    @staticmethod
    def calculate_targets(weight: float, height: float, target_weight: float, target_date: date) -> tuple:
        days_remaining = (target_date - date.today()).days
        if days_remaining <= 0:
            return 2000, 150 # ברירת מחדל אם התאריך עבר
        
        # חישוב BMR בסיסי
        bmr = (10 * weight) + (6.25 * height) - (5 * 25) + 5
        tdee = bmr * 1.375 # מכפיל פעילות קלה
        
        weight_diff = target_weight - weight
        if weight_diff == 0:
            calories = int(tdee)
        else:
            total_calories_needed = weight_diff * 7700
            daily_change = total_calories_needed / days_remaining
            calories = int(tdee + daily_change)
            
        calories = max(min(calories, 3500), 1200)
        protein = int(weight * 2.2)
        
        return calories, protein