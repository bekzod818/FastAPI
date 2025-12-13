"""
Pydantic schemas for API requests and responses.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoryBase(BaseModel):
    """Base schema for Category."""
    title_en: str
    title_ru: Optional[str] = None
    title_uz: Optional[str] = None
    title_es: Optional[str] = None
    title_he: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    description_uz: Optional[str] = None
    description_es: Optional[str] = None
    description_he: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a Category."""
    pass


class CategoryResponse(BaseModel):
    """Schema for Category response with translated fields."""
    id: int
    title: str
    description: Optional[str] = None
    locale: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Schema for Category list response."""
    id: int
    title: str
    description: Optional[str] = None
    locale: str
    
    class Config:
        from_attributes = True


class ArticleBase(BaseModel):
    """Base schema for Article."""
    category_id: int
    title_en: str
    title_ru: Optional[str] = None
    title_uz: Optional[str] = None
    title_es: Optional[str] = None
    title_he: Optional[str] = None
    description_en: Optional[str] = None
    description_ru: Optional[str] = None
    description_uz: Optional[str] = None
    description_es: Optional[str] = None
    description_he: Optional[str] = None


class ArticleCreate(ArticleBase):
    """Schema for creating an Article."""
    pass


class ArticleResponse(BaseModel):
    """Schema for Article response with translated fields."""
    id: int
    category_id: int
    title: str
    description: Optional[str] = None
    locale: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    """Schema for Article list response."""
    id: int
    category_id: int
    title: str
    description: Optional[str] = None
    locale: str
    
    class Config:
        from_attributes = True


class CategoryWithArticlesResponse(BaseModel):
    """Schema for Category detail with articles."""
    id: int
    title: str
    description: Optional[str] = None
    locale: str
    articles: list[ArticleListResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

