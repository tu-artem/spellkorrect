from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.corrector import Corrector, CorrectorResponse

app = FastAPI()

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

corrector = Corrector()


@app.get("/correct", response_model=CorrectorResponse)
def correct(text: str):
    corrected = corrector.correct(text)
    return corrected
