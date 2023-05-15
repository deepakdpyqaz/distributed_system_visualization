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

zero_matrix = {
    "cpu_cores":0,
    "cpu_utilization":0,
    "memory":0,
    "memory_utilization":0,
    "disk":0,
    "disk_utilization":0,
    "gpu_memory":0,
    "gpu_memory_used":0,
    "timer": 0,
    "timestamp":datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")
}
def create_labels(key):
    if key == "":
        return key
    else:
        return f"{tasks[key]['name']} ({key})"

def get_zone(row):
    tnow = datetime.datetime.utcnow()
    timestamp = datetime.datetime.strptime(row["timestamp"],"%Y-%m-%d %H:%M:%S.%f")
    timer = row["timer"]
    if (tnow-timestamp).total_seconds() > 3*timer:
        return "red"
    else:
        return "green"

def get_utilization_report(task):
    try:
        clients = db.child("tasks").child(task).child("client").shallow().get().val()
        clients = list(clients)
        utilization = [db.child("heartbeat").child(client).get().val() for client in clients]
        utilization = [zero_matrix if x is None else x for x in utilization]
        utilization = pd.DataFrame(utilization,index=clients)
        utilization["zone"] = utilization.apply(get_zone,axis=1)
        return utilization
    except:
        return pd.DataFrame()

def get_red_zoned(s):
    return ['background-color: red']*len(s) if s.zone=="red" else ['background-color: green']*len(s)

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
                    full_utilization = get_utilization_report(task_selected)
                    utilization = full_utilization[full_utilization["zone"]=="green"]
                    if utilization.empty:
                        st.warning("No client is running this task")
                        time.sleep(10)
                        continue
                    col1,col2 = st.columns(2)
                    with col1:
                        st.metric("CPU cores", round(utilization["cpu_cores"].sum()))
                        st.metric("Memory (GB)", round(utilization["memory"].sum()))
                        st.metric("Disk (GB)", round(utilization["disk"].sum()))
                        st.metric("GPU (GB)", round(utilization["gpu_memory"].sum()))
                    with col2:
                        st.metric("Core Utilization (%)", round(utilization["cpu_utilization"].mean(),2))
                        st.metric("Memory Utilization (%)", round(utilization["memory_utilization"].mean(),2))
                        st.metric("Disk Utilization (%)", round(utilization["disk_utilization"].mean(),2))
                        st.metric("GPU Utilization (%)", round(utilization["gpu_memory_used"].sum()/utilization["gpu_memory"].sum()*100,2))
                    utilization["timestamp"] = utilization["timestamp"].apply(convert_to_local)
                    st.dataframe(full_utilization.style.apply(get_red_zoned,axis=1))
                    time.sleep(10)
                    st.info("Data refreshed at {}".format(datetime.datetime.utcnow().astimezone(pytz.timezone('Asia/Kolkata')).strftime("%H:%M:%S")))