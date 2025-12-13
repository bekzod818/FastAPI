"""
Database models with translatable fields.
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base
from config import settings


class Category(Base):
    """
    Category model with translatable title and description fields.
    
    Stores translations in separate columns: title_en, title_ru, title_uz, etc.
    """
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Translatable fields - one column per language
    title_en = Column(String(255), nullable=False)
    title_ru = Column(String(255), nullable=True)
    title_uz = Column(String(255), nullable=True)
    title_es = Column(String(255), nullable=True)
    title_he = Column(String(255), nullable=True)
    
    description_en = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)
    description_uz = Column(Text, nullable=True)
    description_es = Column(Text, nullable=True)
    description_he = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    articles = relationship("Article", back_populates="category", cascade="all, delete-orphan")
    
    def get_title(self, locale: str = None) -> str:
        """
        Get title in the specified locale, fallback to English if not available.
        
        Args:
            locale: Locale code (e.g., 'en', 'ru', 'uz')
        
        Returns:
            Title in the specified locale or English.
        """
        if locale is None:
            locale = settings.default_locale
        
        attr_name = f"title_{locale}"
        title = getattr(self, attr_name, None)
        
        # Fallback to English if translation not available
        if not title and locale != settings.default_locale:
            title = self.title_en
        
        return title or ""
    
    def get_description(self, locale: str = None) -> str:
        """
        Get description in the specified locale, fallback to English if not available.
        
        Args:
            locale: Locale code (e.g., 'en', 'ru', 'uz')
        
        Returns:
            Description in the specified locale or English.
        """
        if locale is None:
            locale = settings.default_locale
        
        attr_name = f"description_{locale}"
        description = getattr(self, attr_name, None)
        
        # Fallback to English if translation not available
        if not description and locale != settings.default_locale:
            description = self.description_en
        
        return description or ""


class Article(Base):
    """
    Article model with translatable title and description fields.
    
    Stores translations in separate columns: title_en, title_ru, title_uz, etc.
    """
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Translatable fields - one column per language
    title_en = Column(String(255), nullable=False)
    title_ru = Column(String(255), nullable=True)
    title_uz = Column(String(255), nullable=True)
    title_es = Column(String(255), nullable=True)
    title_he = Column(String(255), nullable=True)
    
    description_en = Column(Text, nullable=True)
    description_ru = Column(Text, nullable=True)
    description_uz = Column(Text, nullable=True)
    description_es = Column(Text, nullable=True)
    description_he = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    category = relationship("Category", back_populates="articles")
    
    def get_title(self, locale: str = None) -> str:
        """
        Get title in the specified locale, fallback to English if not available.
        
        Args:
            locale: Locale code (e.g., 'en', 'ru', 'uz')
        
        Returns:
            Title in the specified locale or English.
        """
        if locale is None:
            locale = settings.default_locale
        
        attr_name = f"title_{locale}"
        title = getattr(self, attr_name, None)
        
        # Fallback to English if translation not available
        if not title and locale != settings.default_locale:
            title = self.title_en
        
        return title or ""
    
    def get_description(self, locale: str = None) -> str:
        """
        Get description in the specified locale, fallback to English if not available.
        
        Args:
            locale: Locale code (e.g., 'en', 'ru', 'uz')
        
        Returns:
            Description in the specified locale or English.
        """
        if locale is None:
            locale = settings.default_locale
        
        attr_name = f"description_{locale}"
        description = getattr(self, attr_name, None)
        
        # Fallback to English if translation not available
        if not description and locale != settings.default_locale:
            description = self.description_en
        
        return description or ""

