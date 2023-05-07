import streamlit as st
import pyrebase
import json
import traceback
from datetime import datetime
import pytz


utc_timezone = pytz.timezone('UTC')
indian_timezone = pytz.timezone('Asia/Kolkata')


@st.cache_resource
def get_firebase_db():
    try:
        firebase_config = st.secrets["firebase"]
        firebase = pyrebase.initialize_app(firebase_config)
        db = firebase.database()
        return db
    except:
        traceback.print_exc()
        st.error("Failed to connect to the database. Please check your internet connection.")
        st.stop()

def convert_to_local(utc_dt):
    utc_datetime = datetime.strptime(utc_dt, "%Y-%m-%d %H:%M:%S.%f")
    utc_datetime = utc_timezone.localize(utc_datetime)
    indian_datetime = utc_datetime.astimezone(indian_timezone)
    indian_string = indian_datetime.strftime("%d/%m/%y %H:%M:%S")
    return indian_string