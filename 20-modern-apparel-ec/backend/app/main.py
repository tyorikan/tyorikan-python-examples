from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.spanner import init_spanner
from app.api.products import router as product_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # In a real app, we might verify connection here
    init_spanner()
    yield

app = FastAPI(title="Modern Apparel EC API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(product_router, prefix="/api/products", tags=["products"])

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "Modern Apparel EC Backend"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
