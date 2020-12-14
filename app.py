from fastapi import FastAPI

from src.corrector import Corrector, CorrectorResponse

app = FastAPI()
corrector = Corrector()


@app.get("/correct", response_model=CorrectorResponse)
def correct(text: str):
    corrected = corrector.correct(text)
    return corrected
