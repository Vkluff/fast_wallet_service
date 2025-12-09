from fastapi import FastAPI
from dotenv import load_dotenv
from routers import auth, keys, wallet, webhook
from core.db import init_db

# Load environment variables from .env file
load_dotenv()




app = FastAPI(
    title="Wallet Service with Paystack, JWT & API Keys",
    description="A backend wallet service implementing deposits via Paystack, JWT/API Key authentication, and fund transfers.",
    version="1.0.0",
)

# Include routers
app.include_router(auth.router)
app.include_router(keys.router)
app.include_router(webhook.router)
app.add_event_handler("startup", init_db) # Initialize DB on startup
app.include_router(wallet.router)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Wallet Service is running!"}

# To run the application, use:
# uvicorn main:app --reload
