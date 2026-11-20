import uvicorn
from app.config import HOST, PORT

if __name__ == "__main__":
    print(f"Starting Travel Booking API server on http://{HOST}:{PORT}")
    print(f"Interactive Swagger Docs: http://{HOST}:{PORT}/docs")
    print(f"ReDoc Documentation:    http://{HOST}:{PORT}/redoc")
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=True)
