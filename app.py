import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import bcrypt
from db import init_db, get_db_connection

init_db()

st.set_page_config(page_title="Maximum Effort Fitness Tracker", layout="centered")

# ---- Title ----
st.title("💪 Maximum Effort Fitness Tracker")
st.write("Track your workouts, see progress, and stay consistent.")

# ---- Registration ----
st.subheader("Register New Account")
new_username = st.text_input("New Username")
new_password = st.text_input("New Password", type="password")
if st.button("Register"):
    if new_username and new_password:
        hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())
        try:
            conn = get_db_connection()
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, hashed_pw))
            conn.commit()
            conn.close()
            st.success("Account created! You can now log in.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.error("Please enter both username and password.")



# ---- Login ----
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"]):
            st.session_state.user = username
            st.success(f"Welcome {username}!")
        else:
            st.error("Invalid login")
    st.stop()
# ---- Logout ----
if st.session_state.user:
    if st.button("Logout"):
        st.session_state.user = None
        st.experimental_rerun()



# ---- Workout Form ----
st.subheader("Add a Workout")
with st.form("workout_form"):
    date = st.date_input("Date")
    exercise = st.text_input("Exercise")
    sets = st.number_input("Sets", min_value=1, max_value=20, step=1)
    reps = st.number_input("Reps", min_value=1, max_value=50, step=1)
    weight = st.number_input("Weight (lbs)", min_value=0, max_value=2000, step=5)
    submitted = st.form_submit_button("Add Workout")

    if submitted:
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO workouts (user, date, exercise, sets, reps, weight) VALUES (?, ?, ?, ?, ?, ?)",
            (st.session_state.user, str(date), exercise, sets, reps, weight),
        )
        conn.commit()
        conn.close()
        st.success("Workout added!")

# ---- Show Log ----
st.subheader("Workout Log")
conn = get_db_connection()
workouts = pd.read_sql_query(
    "SELECT date, exercise, sets, reps, weight FROM workouts WHERE user = ? ORDER BY date DESC",
    conn,
    params=(st.session_state.user,),
)
conn.close()
st.dataframe(workouts)


# ---- Progress Tracking ----
st.subheader("Progress Over Time")
if not workouts.empty:
    workouts["Volume"] = workouts["sets"] * workouts["reps"] * workouts["weight"]

    fig, ax = plt.subplots()
    workouts.groupby("date")["Volume"].sum().plot(ax=ax, marker="o")
    ax.set_ylabel("Total Volume (lbs)")
    ax.set_title(f"Training Volume Over Time – {st.session_state.user}")
    st.pyplot(fig)
else:
    st.info("Log some workouts to see your progress!")

