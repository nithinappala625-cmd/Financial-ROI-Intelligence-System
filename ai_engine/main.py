from fastapi import FastAPI
from ai_engine.api.predict import router as predict_router
from ai_engine.api.anomaly import router as anomaly_router

app = FastAPI(title="Neural Financial Core - AI Engine")

app.include_router(predict_router)
app.include_router(anomaly_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ai_engine.main:app", host="127.0.0.1", port=8001, reload=True)
