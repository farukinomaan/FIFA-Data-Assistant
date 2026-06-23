import streamlit as st
from llm_engine import generate_sql
from database import run_query

st.set_page_config(page_title="FIFA Data Assistant", layout="centered")

st.markdown("""
    <style>
    /* Minimalist Grayscale Theme */
    .stApp {
        background-color: #f4f4f4;
        color: #1a1a1a;
        font-family: 'Courier New', Courier, monospace;
    }
    .stTextInput>div>div>input {
        background-color: #ffffff;
        border: 2px solid #333333;
        border-radius: 0px;
        color: #000000;
        font-family: 'Courier New', Courier, monospace;
    }
    .stButton>button {
        background-color: #1a1a1a;
        color: #ffffff;
        border-radius: 0px;
        border: 2px solid #1a1a1a;
        font-weight: bold;
        text-transform: uppercase;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 2px solid #1a1a1a;
    }
    .stDataFrame {
        border: 1px solid #333333;
    }
    h1, h2, h3 {
        text-transform: uppercase;
        letter-spacing: -1px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("FIFA DATA ASSISTANT")
st.markdown("---")

with st.sidebar:
    st.header("Test Queries")
    st.markdown("Click to copy:")
    st.code("Show me the top 10 players by overall rating.", language="text")
    st.code("Compare Lionel Messi and Cristiano Ronaldo.", language="text")
    st.code("Which teams have the highest average player rating?", language="text")
    st.code("Show me the best strikers with pace above 85.", language="text")
    st.code("What is the average rating of players in Real Madrid?", language="text")

    query = st.text_input("Ask a question about the FIFA database:")

if st.button("Run Query"):
    if query:
        with st.spinner("Compiling logic..."):
            sql_query = generate_sql(query)
            
            if sql_query == "INVALID_QUERY":
                st.error("I am specifically trained to analyze FIFA football data. Please ask me about players, teams, or ratings.")
            else:
                # Display the SQL for transparency (Hiring managers love seeing the engine work)
                with st.expander("View Compiled SQL"):
                    st.code(sql_query, language="sql")
                
                df, error = run_query(sql_query)
                
                if error:
                    st.error(f"Error executing query: {error}")
                elif df is None or df.empty:
                    st.warning("No matching results found in the database. Try adjusting your search terms.")
                else:
                    st.success("Query successful!")
                    st.dataframe(df, use_container_width=True)
    else:
        st.warning("Please enter a query.")