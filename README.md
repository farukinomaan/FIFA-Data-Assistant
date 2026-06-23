# ⚽ FIFA Agentic Data Assistant

A decoupled, deterministic Text-to-SQL AI application built to query, analyze, and summarize the EA FC 26 player dataset from Kaggle.

## 🏗️ Architecture & Stack
* **Frontend:** React (Vite) + Tailwind CSS (Monospace/Brutalist design)
* **Backend API:** FastAPI (Python)
* **Database:** SQLite (Populated via Pandas/Kaggle FC26 Dataset)
* **LLM Engine:** Gemini 3.1 Flash-Lite (Agentic Text-to-SQL routing)

## ✅ Requirements Fulfilled

**1. Data Input**
* Ingested the EA Sports FC 26 Complete Player Dataset (18,000+ rows).
* Cleaned and migrated the CSV into a lightweight, queryable SQLite database.

**2. User Query Interface**
* Built a custom React web application with a conversational chat interface.
* Features real-time loading states, error boundaries, and dynamic data grid rendering.

**3. Structured Output**
* **Two-Step AI Pipeline:** The engine first compiles raw data into a responsive grid, then runs a secondary LLM pass (temperature = 0.0) to generate a concise, human-readable text summary of the exact metrics.
* Includes an expandable "View Compiled SQL" debug panel for transparency.

**4. Complex Logic & Filtering**
* **Top N Ranking:** Handled via programmatic rules injecting `ORDER BY` and `LIMIT` clauses.
* **Player Comparisons:** Handled via complex `UNION ALL` subqueries to prevent duplicate sibling matches (e.g., separating Jude vs. Jobe Bellingham).
* **Team-Level Aggregation:** Supports advanced SQL grouping (e.g., `AVG(Overall) GROUP BY Club`).

**5. Enterprise Error Handling & Guardrails**
* **Hallucination Resistance:** Implemented a Python interceptor (`_sanitize_like_literals`) to strip accented characters via regex before database execution, preventing zero-match errors.
* **Out-of-Bounds Queries:** Queries unrelated to football are trapped and return a strict `INVALID_QUERY` refusal.
* **Data Serialization:** Built-in safeguards to catch and replace `NaN` values to ensure JSON-compliant API responses.
* **Missing Entities:** Graceful textual fallbacks when a requested player is not in the current roster.

## 🚀 How to Run Locally

1. **Backend:**
   ```bash
   pip install -r requirements.txt
   uvicorn api:app --reload

Since I can't trigger a direct file download in this chat window, I have provided the exact raw Markdown code below.

Just click the **Copy code** button at the top right of the block, create a new file in your root folder named exactly `README.md`, and paste this in. GitHub will automatically render it perfectly!

### Dataset used

**EA Sports FC 26 Complete Player Dataset** (via Kaggle). The CSV data was cleaned and migrated into a local SQLite database (`players` table). It includes attributes such as player names, ages, nationalities, clubs, overall ratings, potential, wages, and detailed in-game stats (pace, shooting, passing, etc.).

### Where I used AI / LLMs

**Google Gemini 3.1 Flash-Lite** is utilized as the core logic engine in a two-step orchestration pipeline:

1. **The Logic Compiler:** The LLM receives the user's natural language query alongside a strict database schema prompt and outputs raw SQLite code. (Includes programmatic Python guardrails to sanitize accents and handle sibling surname overlap via `UNION ALL`).
2. **The Analyst Summarizer:** Once the SQL executes, the raw data array is passed *back* to the LLM (at `temperature=0.0`) to generate a strict, factual one-sentence summary of the returned numbers, acting as a human-readable UI layer.

### Known limitations

* **Database Roster Updates:** The app relies on a static snapshot of the FC26 dataset. Players who have recently retired, transferred, or were omitted from this specific Kaggle scrape will gracefully return a "No data available" response rather than live data.
* **Typographical Fragility:** While custom regex intercepts and sanitizes accented characters (e.g., Mbappé to Mbappe) to prevent wildcard failures, heavily misspelled player names in the user prompt may still result in zero database matches.
* **Ambiguous Aggregations:** Broad queries without explicit metrics (e.g., "Who is the best team?") rely on the LLM's assumption to sort by `Overall` rating.


### Example Queries to Try
* "Show me the top 10 players by overall rating."

* "Compare Jude Bellingham and Kylian Mbappé."

* "Which teams have the highest average player rating?"

* "Show me the best strikers with pace above 85."

### 📊 The Interface

**Direct Player Comparison & SQL Compilation:**
![Player Comparison](./assets/3.png)

**Average Player Rating:**
![Average Player Rating](./assets/1.png)

**Best Striker with pace above 85:**
![Best Striker with pace above 85](./assets/2.png)

**Error Handling and Guard Rails:**
![What is the weather in Bengaluru today?](./assets/4.png)

**Short Analysis of the best value player**
![Short Analysis of the best value player](./assets/5.png)