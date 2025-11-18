"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal


class FileInfo(BaseModel):
    filename: str
    content_type: Optional[str] = None
    size: int = 0
    # For demo purposes we keep small files inline as base64
    content_base64: Optional[str] = None


class Application(BaseModel):
    """
    Applications collection schema
    Collection name: "application"
    """
    type: Literal["express", "standard"] = Field(..., description="Bewerbungstyp")

    # Basisdaten
    vorname: str = Field(..., description="Vorname")
    nachname: str = Field(..., description="Nachname")
    email: EmailStr = Field(..., description="E-Mail-Adresse")
    telefon: Optional[str] = Field(None, description="Telefonnummer")

    rolle: Optional[str] = Field(None, description="Gewünschte Rolle/Position")
    arbeitszeit: Optional[str] = Field(None, description="Vollzeit/Teilzeit/Mini-Job etc.")

    nachricht: Optional[str] = Field(None, description="Kurze Nachricht/Motivation")

    # Dateien nur bei Standard-Verfahren
    dateien: Optional[List[FileInfo]] = Field(default=None, description="Hochgeladene Dokumente")


# Example schemas kept for reference (not used by the app but available for the viewer)
class User(BaseModel):
    name: str
    email: str
    address: str
    age: Optional[int] = None
    is_active: bool = True


class Product(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    category: str
    in_stock: bool = True
