import sqlite3
import datetime
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

def create_db():
    conn = sqlite3.connect("job_search_tracker.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS habit_tracker (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            task TEXT,
            status TEXT,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_entry(category, task, status, notes):
    conn = sqlite3.connect("job_search_tracker.db")
    cursor = conn.cursor()
    date = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO habit_tracker (date, category, task, status, notes) VALUES (?, ?, ?, ?, ?)",
                   (date, category, task, status, notes))
    conn.commit()
    conn.close()

def view_entries():
    conn = sqlite3.connect("job_search_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habit_tracker ORDER BY date DESC")
    entries = cursor.fetchall()
    conn.close()
    return entries

def export_data():
    conn = sqlite3.connect("job_search_tracker.db")
    df = pd.read_sql_query("SELECT * FROM habit_tracker", conn)
    conn.close()
    df.to_csv("job_search_tracker.csv", index=False)
    return df

def plot_progress():
    conn = sqlite3.connect("job_search_tracker.db")
    df = pd.read_sql_query("SELECT date, category FROM habit_tracker", conn)
    conn.close()
    if df.empty:
        st.write("No data to display.")
        return
    df["date"] = pd.to_datetime(df["date"])
    df["count"] = 1
    summary = df.groupby(["date", "category"]).count().reset_index()
    
    plt.figure(figsize=(10,5))
    for category in summary["category"].unique():
        subset = summary[summary["category"] == category]
        plt.plot(subset["date"], subset["count"], marker="o", label=category)
    plt.xlabel("Date")
    plt.ylabel("Entries Logged")
    plt.title("Job Search Progress Over Time")
    plt.legend()
    st.pyplot(plt)

# Streamlit UI
st.title("📌 Job Search Tracker")
create_db()

# Input form
st.subheader("Add a New Entry")
category = st.selectbox("Category", ["Job Application", "Networking", "Skill Development", "Interview Prep", "Freelance Work", "Mental Wellness"])
task = st.text_input("Task")
status = st.selectbox("Status", ["Pending", "Completed", "In Progress"])
notes = st.text_area("Notes (Optional)")
if st.button("Add Entry"):
    add_entry(category, task, status, notes)
    st.success("✅ Entry added successfully!")

# Display existing entries
st.subheader("📌 Previous Entries")
entries = view_entries()
if not entries:
    st.write("No entries found.")
else:
    for entry in entries:
        st.write(f"**[{entry[1]}] {entry[2]}:** {entry[3]} (Status: {entry[4]}) - {entry[5]}")

# Export Data
st.subheader("📁 Export Data")
if st.button("Export to CSV"):
    df = export_data()
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    st.write("✅ Data exported successfully! Download below:")
    st.download_button(label="Download CSV", data=csv_data.encode("utf-8-sig"), file_name="job_search_tracker.csv", mime="text/csv")

# Progress Visualization
st.subheader("📊 Progress Analytics")
plot_progress()
