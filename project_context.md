# תקציר פרויקט: NutriFit Pro

## 🎯 המטרות והחוקים של ה-UI (חסינות מובייל)
1. **אפס שימוש ב-st.columns לרכיבי ניווט או לוחות שנה:** Streamlit מפרק עמודות אלו אנכית במכשירים סלולריים ומעוות את הממשק.
2. **צבעים ופרופורציות אפליקטיביות:** רקע כהה עמוק אחיד (`#090d16`), תיבות ממוסגרות בגוון פחם (`#111827`), שדות קלט כהים (`#1a2333`), ושימוש בירוק זוהר (`#22c55e`) לסימונים אקטיביים והדגשות[cite: 1].
3. **סרגל תחתוני קבוע (Bottom Navigation Bar):** מבוסס HTML/CSS טהור עם פרמטרים מוגנים באנגלית בתוך ה-URL (`?tab=dashboard`, `diary`, `pantry`, `profile`) למניעת היפוכי אותיות בעברית[cite: 1, 8].
4. **לוח שנה פרימיום שטוח (HTML/CSS Grid):** רשת קשיחה של 7 עמודות המונעת קריסה במובייל[cite: 1, 3]. הימים מוצגים כעיגולים קומפקטיים עדינים[cite: 1]. ניווט חודשים (`▶` / `◀`) וסימון יום נבחר מבוצעים דרך פרמטרים ב-URL לסנכרון מיידי וקבוע[cite: 1, 3].
5. **סיכום תפריט יומי מינימליסטי:** תיבה עליונה המציגה את סך הכל היומי (קלוריות וחלבון) ותחתיה רשימה נקייה, שורה אחר שורה, של כל המאכלים והערכים שלהם ללא לחצנים, לחוויית קריאה חלקה.
6. **ניהול פריטים ללא פלוס/מינוס:** שורות הארוחות מציגות רק כפתור עריכת כמות (`🖊️`) הפותח חלונית צפה (`st.dialog`) לעדכון גרמים מדויק, וכפתור מחיקה (`🗑️`)[cite: 3].

## 🗄️ ארכיטקטורת בסיס הנתונים (Supabase SQL)
```sql
-- 1. טבלת פרופיל משתמש ויעדים
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY DEFAULT 1,
    weight_kg FLOAT,
    height_cm FLOAT,
    target_weight_kg FLOAT,
    custom_calories INTEGER,
    custom_protein INTEGER,
    target_date DATE
);

-- 2. טבלת קבוצות מזון
CREATE TABLE IF NOT EXISTS food_categories (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- 3. טבלת מוצרים במזווה
CREATE TABLE IF NOT EXISTS pantry_products (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    category_name TEXT REFERENCES food_categories(name) ON DELETE SET NULL,
    unit_type TEXT NOT NULL, -- 'גרם' או 'יחידה'
    base_amount FLOAT NOT NULL,
    calories INTEGER NOT NULL,
    protein FLOAT NOT NULL
);

-- 4. טבלת יומן תזונה יומי
CREATE TABLE IF NOT EXISTS meal_diary (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    meal_type TEXT NOT NULL, -- 'ארוחת בוקר', 'ארוחת צהריים', 'ארוחת ערב', 'ארוחת ביניים'
    product_id INTEGER REFERENCES pantry_products(id) ON DELETE SET NULL,
    custom_name TEXT, -- להזנה ידנית מותאמת
    amount FLOAT NOT NULL,
    calories INTEGER NOT NULL,
    protein FLOAT NOT NULL
);