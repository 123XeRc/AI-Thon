from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from src.utils import process_budget_analysis

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/budget_analyse")
async def budget_analyse_api(
    payslip: UploadFile = File(...),
):
    return await process_budget_analysis(payslip)
