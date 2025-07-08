# file: main.py
from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base

# --- Sabhi controllers ko import karein ---
from controllers import (
    auth_controller, 
    book_controller, 
    category_controller, 
    subcategory_controller,
    upload_controller, 
    language_controller, 
    user_controller, 
    book_copy_controller,
    issue_controller, 
    digital_access_controller, 
    location_controller, 
    request_controller, 
    log_controller, 
    permission_controller,
    book_permission_controller  # Naya controller add kiya
)

# --- Sabhi models ko import karein taaki create_all unhe dekh sake ---
from models import (
    user_model, 
    book_model, 
    language_model, 
    library_management_models,
    request_model, 
    log_model, 
    permission_model,
    book_permission_model  # Naya model add kiya
)

# Database me tables create karein (agar maujood nahi hain)
#Base.metadata.create_all(bind=engine)

# FastAPI application ka instance banayein
app = FastAPI(
    title="Advanced Library Management API",
    version="5.0.0",  # Version update kiya
    description="A comprehensive API with Role-Based Access Control, Logging, Approval System, and Restricted Book Permissions.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware (Cross-Origin Resource Sharing) ko enable karein
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production me ise apne frontend URL se replace karein
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (jaise uploaded images) ko serve karne ke liye
app.mount("/static", StaticFiles(directory="static"), name="static")


# --- Routers ko application me include karna ---

# Authentication route (bina /api prefix ke)
app.include_router(auth_controller.router, tags=["Authentication"])

# Baaki sabhi API routes ke liye ek alag APIRouter banayein
api_router = APIRouter() 

api_router.include_router(user_controller.router, prefix="/users", tags=["Users & Roles Management"])
api_router.include_router(permission_controller.router, prefix="/permissions", tags=["Role & System Permissions"])
api_router.include_router(log_controller.router, prefix="/logs", tags=["Audit Logs"])
api_router.include_router(upload_controller.router, prefix="/upload", tags=["File Uploads"])
api_router.include_router(location_controller.router, prefix="/locations", tags=["Physical Locations"])
api_router.include_router(book_copy_controller.router, prefix="/copies", tags=["Book Copies Management"])
api_router.include_router(issue_controller.router, prefix="/issues", tags=["Book Issuing & Returns"])
api_router.include_router(digital_access_controller.router, prefix="/digital-access", tags=["Digital Book Access"])
api_router.include_router(request_controller.router, prefix="/requests", tags=["Book Upload Requests"])
api_router.include_router(book_controller.router, prefix="/books", tags=["Books Management"])
api_router.include_router(category_controller.router, prefix="/categories", tags=["Categories Management"])
api_router.include_router(subcategory_controller.router, prefix="/subcategories", tags=["Subcategories Management"])
api_router.include_router(language_controller.router, prefix="/languages", tags=["Languages Management"])
# Naya router yahan add karein
api_router.include_router(book_permission_controller.router, prefix="/book-permissions", tags=["Restricted Book Permissions"])

# Sabhi API routes ko /api prefix ke saath main app me include karein
app.include_router(api_router, prefix="/api")


# Root endpoint
@app.get("/", tags=["Root"])
def read_root():
    return {
        "message": "Welcome to the Advanced Library Management API!",
        "api_documentation": "Visit /docs or /redoc to see all endpoints."
    }