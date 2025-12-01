import os
import streamlit as st
import requests

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="TaskFlow Board", layout="wide")
st.title("TaskFlow – Board Jira-like")

@st.cache_data
def fetch_tasks():
    resp = requests.get(f"{API_BASE}/api/tasks/")
    resp.raise_for_status()
    return resp.json()

st.write("Chargement des tâches…")

try:
    tasks = fetch_tasks()
    st.success(f"{len(tasks)} tâches chargées.")
except Exception as e:
    st.error(f"Impossible de joindre l'API : {e}")
    st.stop()

# Définition des colonnes du board
STATUS_COLUMNS = [
    ("Backlog", ["À faire"]),
    ("Sélectionné", ["À faire"]),
    ("En cours", ["En cours"]),
    ("Terminé", ["Fait"]),
]

st.subheader("Board Kanban")
cols = st.columns(len(STATUS_COLUMNS))

for col_idx, (col_title, status_values) in enumerate(STATUS_COLUMNS):
    with cols[col_idx]:
        st.markdown(f"### {col_title}")
        column_tasks = [t for t in tasks if t["status"] in status_values]

        if not column_tasks:
            st.caption("Aucune tâche")

        for task in column_tasks:
            with st.container(border=True):
                st.markdown(f"**[{task['task_type']}] {task['title']}**")
                st.caption(f"Projet : {task.get('project')} · Priorité : {task['priority']}")
                st.caption(f"Owner : {task.get('owner') or '—'}")

                desc = (task.get("description") or "")[:120]
                if desc:
                    st.write(desc + ("…" if len(desc) == 120 else ""))