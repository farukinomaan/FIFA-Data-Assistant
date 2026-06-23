import os
import re
from google import genai
from dotenv import load_dotenv

load_dotenv()
MODEL_NAME = "gemini-3.1-flash-lite"
_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


SCHEMA_PROMPT = """
You are an expert SQL Data Analyst. Your job is to convert natural language queries into valid SQLite queries.
You are querying a table named 'players'.

Here is the exact schema of the 'players' table:
Name (TEXT) - The short name of the player (e.g., 'L. Messi', 'Cristiano Ronaldo', 'K. Mbappé')
Age (INTEGER) - The age of the player
Nationality (TEXT) - The player's country/nationality
Club (TEXT) - The club team the player plays for
Position (TEXT) - The field positions (e.g., ST, CAM, LW, RW, CB, GK)
Overall (INTEGER) - The current overall rating of the player (out of 100)
Potential (INTEGER) - The maximum potential rating the player can reach
Value (INTEGER) - The player's market value in Euros (€)
Wage (INTEGER) - The player's weekly wage in Euros (€)
Pace (INTEGER) - Speed rating
Shooting (INTEGER) - Shooting accuracy/power rating
Passing (INTEGER) - Passing rating
Dribbling (INTEGER) - Dribbling rating
Defending (INTEGER) - Defensive capabilities rating
Physical (INTEGER) - Physicality/stamina rating

CRITICAL RULES FOR SQL GENERATION:
1. ONLY return the raw SQL query. No markdown formatting, no code blocks, no explanations.
2. PLAYER NAME SEARCHING: The database uses abbreviated short names (like 'C. Ronaldo'). You MUST use the LIKE operator with wildcards targeting their last name.
   - Example: For "Lionel Messi", use `Name LIKE '%Messi%'`
   - Example: For "Cristiano Ronaldo", use `Name LIKE '%Ronaldo%'`
3. ACCENTED NAMES: Many surnames contain accented characters (é, ñ, ü, etc.), e.g. "Mbappé", "Müller".
   You cannot be trusted to type the exact accented character correctly, and a single wrong byte makes
   LIKE match zero rows. To avoid this entirely, ALWAYS build the LIKE pattern from only the ASCII-only
   prefix of the surname — i.e. cut the surname off right before its first accented character. Never put
   an accented character inside a string literal.
   - Example: "Kylian Mbappé" -> Name LIKE '%Mbapp%'   (NOT '%Mbappé%')
   - Example: "Thomas Müller" -> Name LIKE '%M%ller%' is WRONG; use Name LIKE '%ller%' or '%M%' combined
     with another filter — prefer the simplest ASCII-only prefix: Name LIKE '%ller%'
   - Names with no accents are unaffected: "Erling Haaland" -> Name LIKE '%Haaland%'
4. PLAYER COMPARISONS: Surnames are often shared by relatives (e.g. 'Bellingham' matches both Jude and his
   brother Jobe; 'Mbappé' matches both Kylian and his brother Ethan). A plain OR returns all of them, which
   is wrong when the user named two specific famous players. Instead, for any query comparing two (or more)
   named players, build the query as a UNION ALL of per-player subqueries, each ordered by Overall DESC and
   LIMIT 1, so only the single most relevant (highest-rated) match for each name is returned:

   SELECT * FROM (SELECT * FROM players WHERE Name LIKE '%Messi%' ORDER BY Overall DESC LIMIT 1)
   UNION ALL
   SELECT * FROM (SELECT * FROM players WHERE Name LIKE '%Mbapp%' ORDER BY Overall DESC LIMIT 1)

   Do NOT use a plain `WHERE Name LIKE 'A' OR Name LIKE 'B'` for player-vs-player comparisons — only use
   plain OR/LIKE when the user is searching broadly (e.g. "find players named Silva"), not comparing two
   specific named individuals.
5. If the user query is completely unrelated to football, return exactly 'INVALID_QUERY'.
6. TOP-RANKING & AGGREGATION QUERIES: When a user asks for the "highest", "best", "top", or "lowest" groups 
   (e.g., teams, clubs, nationalities) without explicitly specifying a number, ALWAYS apply a strict `LIMIT 5` 
   or `LIMIT 10` to prevent flooding the interface with hundreds of rows.
   - Example: "Which teams have the highest average player rating?" -> 
     `SELECT Club, AVG(Overall) as AvgRating FROM players GROUP BY Club ORDER BY AvgRating DESC LIMIT 5`
"""


def _truncate_before_accent(text: str) -> str:
    """
    Cut a string right before its first non-ASCII character, e.g.
    '%Mbappé%' -> '%Mbapp%'. Unlike stripping/normalizing the accent away,
    this keeps the result a guaranteed substring of the real stored value
    ('K. Mbappé' really does contain the literal text 'Mbapp'), so the
    LIKE match still succeeds even if the original character was wrong,
    missing, or encoded differently.
    """
    for i, ch in enumerate(text):
        if ord(ch) > 127:
            truncated = text[:i]
            return truncated if truncated.endswith("%") else truncated + "%"
    return text


def _sanitize_like_literals(sql: str) -> str:
    """
    Safety net independent of the model's behavior: find every quoted string
    literal in the SQL and truncate it before any accented character, so a
    pattern like '%Mbappé%' (or any mis-typed accent) becomes '%Mbapp%' —
    still a genuine substring of the accented name actually stored in the DB.
    """
    def repl(match):
        quote = match.group(1)
        inner = match.group(2)
        return f"{quote}{_truncate_before_accent(inner)}{quote}"

    return re.sub(r"(['\"])(.*?)\1", repl, sql)


def generate_sql(user_query):
    full_prompt = f"{SCHEMA_PROMPT}\n\nUser Query: {user_query}\nSQL Query:"

    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=full_prompt,
    )
    sql = response.text.strip()

    sql = sql.replace("```sql", "")
    sql = sql.replace("```sqlite", "")
    sql = sql.replace("```", "")

    sql = sql.strip()

    if sql.upper() == "INVALID_QUERY":
        return sql

    sql = _sanitize_like_literals(sql)

    return sql


def generate_summary(user_query, results_dict):
    """Takes the SQL results and generates a natural language summary."""
    if not results_dict:
        return "No data available to summarize."

    data_string = "\n".join([", ".join([f"{k}: {v}" for k, v in row.items()]) for row in results_dict[:5]])

    prompt = f"""
    You are a strict, robotic data-reading script. You know absolutely nothing about the real world, football, or FIFA.

    User Query: "{user_query}"

    Extracted Data:
    {data_string}

    Write a 1-sentence summary answering the query using EXACTLY the numbers from the Extracted Data above.
    Do not invent, adjust, or guess any ratings. If the data says 88, output 88.
    """

    response = _get_client().models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config={"temperature": 0.0},
    )
    return response.text.strip()