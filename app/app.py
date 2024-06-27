from fastapi import FastAPI
from app.config import get_config

app = FastAPI()
cfg = get_config()


@app.get("/")
def read_root():
    return {"Hello": "World"}
