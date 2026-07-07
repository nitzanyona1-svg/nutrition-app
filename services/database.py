# services/database.py

class DatabaseService:
    def __init__(self, url, key):
        from supabase import create_client
        self.client = create_client(url, key)

    def _safe_data(self, response):
        if hasattr(response, 'data'):
            return response.data
        if isinstance(response, dict) and 'data' in response:
            return response['data']
        return response

    # --- 👤 פרופיל משתמש ויעדים ---
    def get_profile(self):
        try:
            response = self.client.table("user_profile").select("*").eq("id", 1).execute()
            data = self._safe_data(response)
            if isinstance(data, list) and len(data) > 0:
                return data[0]
            return data
        except Exception:
            return None

    def update_profile(self, profile_data):
        profile_data["id"] = 1
        return self.client.table("user_profile").upsert(profile_data).execute()

    # --- 📁 ניהול קבוצות מזון (הפונקציה שהייתה חסרה!) ---
    def get_categories(self):
        try:
            response = self.client.table("food_categories").select("*").execute()
            return self._safe_data(response)
        except Exception:
            return []

    def add_category(self, name):
        return self.client.table("food_categories").insert({"name": name}).execute()

    def delete_category(self, cat_id):
        return self.client.table("food_categories").delete().eq("id", cat_id).execute()

    # --- 🍏 ניהול מוצרים במזווה ---
    def get_pantry_products(self):
        try:
            response = self.client.table("pantry_products").select("*").execute()
            return self._safe_data(response)
        except Exception:
            return []

    def add_pantry_product(self, product_data):
        return self.client.table("pantry_products").insert(product_data).execute()

    def delete_pantry_product(self, prod_id):
        return self.client.table("pantry_products").delete().eq("id", prod_id).execute()

    # --- 🍴 תשתית יומן תזונה משופרת (מבוססת טווח חודשי) ---
    def get_diary_by_date(self, date_str):
        try:
            response = self.client.table("meal_diary").select("*").eq("date", date_str).execute()
            return self._safe_data(response)
        except Exception:
            return []

    def get_diary_for_month(self, start_date_str, end_date_str):
        """שליפת כל המאכלים של חודש שלם במכה אחת למהירות שיא"""
        try:
            response = self.client.table("meal_diary").select("*").gte("date", start_date_str).lte("date", end_date_str).execute()
            return self._safe_data(response)
        except Exception:
            return []

    def add_diary_entry(self, entry_data):
        return self.client.table("meal_diary").upsert(entry_data).execute()

    def delete_diary_entry(self, entry_id):
        return self.client.table("meal_diary").delete().eq("id", entry_id).execute()