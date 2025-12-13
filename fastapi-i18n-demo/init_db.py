"""
Database initialization script with sample data.

Run this script to create the database tables and populate them with sample data.
"""
from database import SessionLocal, init_db
from models import Category, Article
from datetime import datetime


def create_sample_data():
    """Create sample categories and articles with translations."""
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(Category).count() > 0:
            print("Database already contains data. Skipping initialization.")
            return
        
        # Create Categories
        category1 = Category(
            title_en="Technology",
            title_ru="Технологии",
            title_uz="Texnologiya",
            title_es="Tecnología",
            title_he="טכנולוגיה",
            description_en="Articles about technology and innovation",
            description_ru="Статьи о технологиях и инновациях",
            description_uz="Texnologiya va innovatsiya haqidagi maqolalar",
            description_es="Artículos sobre tecnología e innovación",
            description_he="מאמרים על טכנולוגיה וחדשנות"
        )
        
        category2 = Category(
            title_en="Science",
            title_ru="Наука",
            title_uz="Fan",
            title_es="Ciencia",
            title_he="מדע",
            description_en="Scientific articles and research",
            description_ru="Научные статьи и исследования",
            description_uz="Ilmiy maqolalar va tadqiqotlar",
            description_es="Artículos científicos e investigaciones",
            description_he="מאמרים מדעיים ומחקרים"
        )
        
        category3 = Category(
            title_en="Health",
            title_ru="Здоровье",
            title_uz="Salomatlik",
            title_es="Salud",
            title_he="בריאות",
            description_en="Health and wellness articles",
            description_ru="Статьи о здоровье и благополучии",
            description_uz="Salomatlik va farovonlik haqidagi maqolalar",
            description_es="Artículos sobre salud y bienestar",
            description_he="מאמרים על בריאות ורווחה"
        )
        
        db.add(category1)
        db.add(category2)
        db.add(category3)
        db.commit()
        db.refresh(category1)
        db.refresh(category2)
        db.refresh(category3)
        
        # Create Articles for Category 1 (Technology)
        article1 = Article(
            category_id=category1.id,
            title_en="Introduction to Python",
            title_ru="Введение в Python",
            title_uz="Python ga kirish",
            title_es="Introducción a Python",
            title_he="מבוא ל-Python",
            description_en="Learn the basics of Python programming language",
            description_ru="Изучите основы языка программирования Python",
            description_uz="Python dasturlash tilining asoslarini o'rganing",
            description_es="Aprende los conceptos básicos del lenguaje de programación Python",
            description_he="למד את היסודות של שפת התכנות Python"
        )
        
        article2 = Article(
            category_id=category1.id,
            title_en="FastAPI Best Practices",
            title_ru="Лучшие практики FastAPI",
            title_uz="FastAPI eng yaxshi amaliyotlari",
            title_es="Mejores prácticas de FastAPI",
            title_he="שיטות עבודה מומלצות של FastAPI",
            description_en="Best practices for building APIs with FastAPI",
            description_ru="Лучшие практики создания API с FastAPI",
            description_uz="FastAPI bilan API yaratishning eng yaxshi amaliyotlari",
            description_es="Mejores prácticas para crear APIs con FastAPI",
            description_he="שיטות עבודה מומלצות לבניית API עם FastAPI"
        )
        
        # Create Articles for Category 2 (Science)
        article3 = Article(
            category_id=category2.id,
            title_en="Quantum Computing Explained",
            title_ru="Квантовые вычисления объяснены",
            title_uz="Kvant hisoblash tushuntirildi",
            title_es="Computación cuántica explicada",
            title_he="חישוב קוונטי מוסבר",
            description_en="Understanding the principles of quantum computing",
            description_ru="Понимание принципов квантовых вычислений",
            description_uz="Kvant hisoblash tamoyillarini tushunish",
            description_es="Comprender los principios de la computación cuántica",
            description_he="הבנת עקרונות החישוב הקוונטי"
        )
        
        article4 = Article(
            category_id=category2.id,
            title_en="Climate Change Research",
            title_ru="Исследование изменения климата",
            title_uz="Iqlim o'zgarishi tadqiqotlari",
            title_es="Investigación sobre el cambio climático",
            title_he="מחקר שינויי אקלים",
            description_en="Latest research on climate change and its impacts",
            description_ru="Последние исследования изменения климата и его последствий",
            description_uz="Iqlim o'zgarishi va uning ta'siri bo'yicha so'nggi tadqiqotlar",
            description_es="Últimas investigaciones sobre el cambio climático y sus impactos",
            description_he="מחקרים אחרונים על שינויי אקלים והשפעותיהם"
        )
        
        # Create Articles for Category 3 (Health)
        article5 = Article(
            category_id=category3.id,
            title_en="Healthy Eating Habits",
            title_ru="Здоровые привычки питания",
            title_uz="Sog'lom ovqatlanish odatlari",
            title_es="Hábitos alimentarios saludables",
            title_he="הרגלי אכילה בריאים",
            description_en="Tips for maintaining a healthy diet",
            description_ru="Советы по поддержанию здорового питания",
            description_uz="Sog'lom ovqatlanishni saqlash bo'yicha maslahatlar",
            description_es="Consejos para mantener una dieta saludable",
            description_he="טיפים לשמירה על תזונה בריאה"
        )
        
        article6 = Article(
            category_id=category3.id,
            title_en="Exercise and Mental Health",
            title_ru="Упражнения и психическое здоровье",
            title_uz="Jismoniy mashqlar va ruhiy salomatlik",
            title_es="Ejercicio y salud mental",
            title_he="פעילות גופנית ובריאות נפשית",
            description_en="How exercise affects mental well-being",
            description_ru="Как упражнения влияют на психическое благополучие",
            description_uz="Jismoniy mashqlar ruhiy farovonlikka qanday ta'sir qiladi",
            description_es="Cómo el ejercicio afecta el bienestar mental",
            description_he="איך פעילות גופנית משפיעה על רווחה נפשית"
        )
        
        db.add(article1)
        db.add(article2)
        db.add(article3)
        db.add(article4)
        db.add(article5)
        db.add(article6)
        db.commit()
        
        print("✓ Database initialized successfully!")
        print(f"✓ Created {db.query(Category).count()} categories")
        print(f"✓ Created {db.query(Article).count()} articles")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error initializing database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Creating sample data...")
    create_sample_data()
    print("Done!")

