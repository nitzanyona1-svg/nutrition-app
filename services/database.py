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

    # --- פרופיל משתמש ---
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

    # --- יומן תזונה ---
    def get_diary_by_date(self, date_str):
        try:
            response = self.client.table("meal_diary").select("*").eq("date", date_str).execute()
            return self._safe_data(response)
        except Exception:
            return []

    # --- מזווה ---
    def get_pantry_products(self):
        try:
            response = self.client.table("pantry_products").select("*").execute()
            return self._safe_data(response)
        except Exception:
            return []

    # --- קטגוריות ---
    def get_categories(self):
        try:
            response = self.client.table("food_categories").select("*").execute()
            return self._safe_data(response)
        except Exception:
            return []