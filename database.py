import sqlite3
import pandas as pd
import os

DB_NAME= "fifa.db"
CSV_FILE="FC26_20250921.csv"

def init_db(csv_path="players.csv"):
    if os.path.exists(DB_NAME):
        print("Database already exists. Skipping Ingestion")
        return
    
    print("Loading CSV...")

    df= pd.read_csv(CSV_FILE, low_memory=False)

    columns_to_keep= [
        'short_name','age','nationality_name','club_name','player_positions','overall','potential','value_eur','wage_eur','pace','shooting','passing','dribbling','defending','physic'
    ]

    df= df[columns_to_keep]

    df.rename(columns={
        'short_name': 'Name',
        'nationality_name': 'Nationality',
        'club_name': 'Club',
        'player_positions': 'Position',
        'overall': 'Overall',
        'potential': 'Potential',
        'value_eur': 'Value',
        'wage_eur': 'Wage',
        'pace': 'Pace',
        'shooting': 'Shooting',
        'passing': 'Passing',
        'dribbling': 'Dribbling',
        'defending': 'Defending',
        'physic': 'Physical',
        'age': 'Age'
    }, inplace=True)

# SQLite Connection

    conn=sqlite3.connect(DB_NAME)

    print("Writing to SQLite....")
    df.to_sql("players",conn,if_exists="replace",index=False)

    conn.close()
    print("Database ready")

def run_query(query):
        try:
            conn=sqlite3.connect(DB_NAME)
            result= pd.read_sql_query(query,conn)
            conn.close()
            return result, None
        except Exception as e:
            return None, str(e)
        
if __name__=="__main__":
    init_db()