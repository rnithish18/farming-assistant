import os

interceptor_code = """

def is_profile_verified(username: str) -> bool:
    try:
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute("SELECT is_otp_verified FROM farmer_profiles WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        if row and row[0] == 1:
            return True
    except Exception:
        pass
    return False

def save_verified_log(username: str, feature_type: str, details: str):
    # Only save logs if the user profile has successfully bypassed OTP verification
    if is_profile_verified(username):
        try:
            conn = sqlite3.connect("farming_assistant.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO activity_logs (username, feature_type, query_details) VALUES (?, ?, ?)",
                (username, feature_type, details)
            )
            conn.commit()
            conn.close()
            print(f"Log successfully recorded for verified user: {username}")
        except Exception as e:
            print(f"Logging error: {e}")
    else:
        print(f"Log blocked: User {username} has not verified their profile via OTP yet.")
"""

if os.path.exists("main.py"):
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
        
    if "is_profile_verified" not in content:
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content + "\n" + interceptor_code)
        print("Step 4 Complete: Verification logging guard attached to your backend!")
    else:
        print("Verification logging guard is already installed.")
else:
    print("Error: main.py file not found.")