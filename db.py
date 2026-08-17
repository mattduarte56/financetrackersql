import streamlit as st
from urllib.parse import quote_plus
from sqlalchemy import create_engine

server = "matttestserver.database.windows.net"
database = "FinanceTracker"
username = quote_plus(st.secrets["DB_USERNAME"])
password = quote_plus(st.secrets["DB_PASSWORD"])

connection_string = f"mssql+pymssql://{username}:{password}@{server}/{database}"

engine = create_engine(connection_string)