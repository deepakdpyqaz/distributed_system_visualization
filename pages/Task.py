import streamlit as st
from components.authorization import is_authenticated
from components.utilities import get_firebase_db, convert_to_local
import datetime
import pytz
import time
import pandas as pd

st.set_page_config(page_title="Tasks", page_icon="🧊")
is_authenticated()


# Path: pages/Task.py
db = get_firebase_db()
tasks = db.child("tasks").order_by_child("start").limit_to_last(5).get().val()

def create_labels(key):
    if key == "":
        return key
    else:
        return f"{tasks[key]['name']} ({key})"

def get_utilization_report(task):
    clients = db.child("tasks").child(task).child("client").shallow().get().val()
    clients = list(clients)
    utilization = [db.child("heartbeat").child(client).get().val() for client in clients]
    return pd.DataFrame(utilization,index=clients)

keys = [""]+list(tasks.keys())[::-1]
task_selected = st.selectbox("Select a task", keys, format_func=create_labels)
st.divider()
if task_selected != "":
    selected_task = tasks[task_selected]
    st.subheader(f"Task `{selected_task['name']}`")
    col1,col2,col3 = st.columns(3)
    col1.metric("Initiator",selected_task["initiator"])
    col2.metric("Items",selected_task["items"])
    col3.metric("Finished",len(selected_task.get("results",[])))
    col4,col5 = st.columns(2)
    col4.metric("Start", convert_to_local(selected_task["start"]))
    if selected_task.get("end",None):
        col5.metric("End", convert_to_local(selected_task["end"]))
    else:
        col5.metric("End", "Not finished")
    if not selected_task.get("end",None):
        st.divider()
        st.subheader("Performance")
        performance_wrapper = st.empty()
        while True:
            with performance_wrapper.container():
                    utilization = get_utilization_report(task_selected)
                    col1,col2 = st.columns(2)
                    with col1:
                        st.metric("CPU cores", utilization["cpu_cores"].sum())
                        st.metric("Memory (GB)", utilization["memory"].sum())
                        st.metric("Disk (GB)", utilization["disk"].sum())
                        st.metric("GPU (GB)", utilization["gpu_memory"].sum())
                    with col2:
                        st.metric("Core Utilization (%)", round(utilization["cpu_utilization"].mean(),2))
                        st.metric("Memory Utilization (%)", round(utilization["memory_utilization"].mean(),2))
                        st.metric("Disk Utilization (%)", round(utilization["disk_utilization"].mean(),2))
                        st.metric("GPU Utilization (%)", round(utilization["gpu_memory_used"].mean(),2))
                    utilization["timestamp"] = utilization["timestamp"].apply(convert_to_local)
                    st.dataframe(utilization)
                    time.sleep(10)
                    st.info("Data refreshed at {}".format(datetime.datetime.now().strftime("%H:%M:%S")))