import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.seed_data import seed_database
from app.routes.auth_routes import router as auth_router
from app.routes.flight_routes import router as flight_router
from app.routes.hotel_routes import router as hotel_router
from app.routes.booking_routes import router as booking_router
from app.routes.payment_routes import router as payment_router

# Initialize FastAPI App
app = FastAPI(
    title="Travel Booking REST API",
    description="Simulated Travel Booking Microservices API for SDET Automation & Quality Engineering",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add latency measurement header to every response for SDET performance assertions."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


@app.on_event("startup")
def startup_event():
    """Ensure database schema is created and initial seed records exist."""
    Base.metadata.create_all(bind=engine)
    seed_database()


# Include Routers
app.include_router(auth_router)
app.include_router(flight_router)
app.include_router(hotel_router)
app.include_router(booking_router)
app.include_router(payment_router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Travel Booking API",
        "status": "ONLINE",
        "documentation": "/docs",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "database": "connected"}
