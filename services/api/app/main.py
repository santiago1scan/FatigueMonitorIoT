from fastapi import FastAPI

app = FastAPI(
    title="Fatigue Monitor API"
)

@app.get("/")
def root():
    return {
        "status": "running",
        "service": "api"
    }

@app.get("/health")
def health():
    return {
        "healthy": True
    }