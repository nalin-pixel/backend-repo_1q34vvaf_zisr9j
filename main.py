import os
import base64
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import create_document
from schemas import Application, FileInfo

app = FastAPI(title="Zahnarztpraxis Karriere API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Zahnarztpraxis Karriere API läuft"}


class ExpressApplicationIn(BaseModel):
    vorname: str
    nachname: str
    email: str
    telefon: Optional[str] = None
    rolle: Optional[str] = None
    arbeitszeit: Optional[str] = None
    nachricht: Optional[str] = None


@app.post("/api/bewerbung/express")
def create_express_application(data: ExpressApplicationIn):
    bewerbung = Application(
        type="express",
        vorname=data.vorname,
        nachname=data.nachname,
        email=data.email,
        telefon=data.telefon,
        rolle=data.rolle,
        arbeitszeit=data.arbeitszeit,
        nachricht=data.nachricht,
        dateien=None,
    )
    doc_id = create_document("application", bewerbung)
    return {"ok": True, "id": doc_id}


@app.post("/api/bewerbung/standard")
async def create_standard_application(
    vorname: str = Form(...),
    nachname: str = Form(...),
    email: str = Form(...),
    telefon: Optional[str] = Form(None),
    rolle: Optional[str] = Form(None),
    arbeitszeit: Optional[str] = Form(None),
    nachricht: Optional[str] = Form(None),
    dateien: Optional[List[UploadFile]] = File(None),
):
    files_meta: List[FileInfo] = []

    # inline store small files up to ~1MB for demo purposes
    if dateien:
        for f in dateien:
            content = await f.read()
            # Limit inline encoded content to 1MB
            if len(content) <= 1_000_000:
                b64 = base64.b64encode(content).decode("utf-8")
            else:
                b64 = None
            files_meta.append(
                FileInfo(
                    filename=f.filename,
                    content_type=f.content_type,
                    size=len(content),
                    content_base64=b64,
                )
            )

    bewerbung = Application(
        type="standard",
        vorname=vorname,
        nachname=nachname,
        email=email,
        telefon=telefon,
        rolle=rolle,
        arbeitszeit=arbeitszeit,
        nachricht=nachricht,
        dateien=files_meta if files_meta else None,
    )

    doc_id = create_document("application", bewerbung)
    return {"ok": True, "id": doc_id}


@app.get("/test")
def test_database():
    """Erweiterter Test-Endpunkt für die DB-Verbindung"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os as _os

    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
