from fastapi import FastAPI
from ai_engine.api.predict import router as predict_router
from ai_engine.api.anomaly import router as anomaly_router
from ai_engine.api.nlp_routes import router as nlp_router

app = FastAPI(
    title="Neural Financial Core - AI Engine",
    description="ML microservice: cost/revenue prediction, risk classification, anomaly detection, NLP, RL budget advisor",
    version="2.0.0",
)

app.include_router(predict_router)
app.include_router(anomaly_router)
app.include_router(nlp_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ai-engine", "version": "2.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ai_engine.main:app", host="127.0.0.1", port=8001, reload=True)
