from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from llm_engine import generate_sql, generate_summary
from database import run_query
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask_fifa(request: QueryRequest):
    # Generate and validate SQL
    sql_query = generate_sql(request.query)
    if sql_query == "INVALID_QUERY":
        raise HTTPException(status_code=400, detail="I am trained to analyze FIFA data. Please ask about players or teams.")
    
    # Execute SQL
    df, error = run_query(sql_query)
    if error:
        raise HTTPException(status_code=500, detail=f"Database error: {error}")
    
    # Handle Empty Results
    if df is None or df.empty:
        return {"sql": sql_query, "summary": "I couldn't find any matching records for that query.", "results": []}
        
    # Generate the Human Summary
    results_dict = df.fillna("N/A").to_dict(orient="records")
    text_summary = generate_summary(request.query, results_dict)
    
    #  Return everything to React
    return {
        "sql": sql_query, 
        "summary": text_summary, 
        "results": results_dict
    }