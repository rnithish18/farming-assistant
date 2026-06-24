import os

code_payload = """
from pydantic import BaseModel
import sqlite3

class ProfileRequest(BaseModel):
    username: str
    phone_number: str
    age: int
    gender: str

class OTPVerifyRequest(BaseModel):
    username: str
    otp: str

@app.post("/register-profile")
def register_profile(request: ProfileRequest):
    try:
        conn = sqlite3.connect("farming_assistant.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO farmer_profiles (username, phone_number, age, gender, is_otp_verified) VALUES (?, ?, ?, ?, 0)",
            (request.username, request.phone_number, request.age, request.gender)
        )
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Profile saved. Simulated OTP sent.", "mock_otp": "1234"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/verify-otp")
def verify_otp(request: OTPVerifyRequest):
    if request.otp == "1234":
        try:
            conn = sqlite3.connect("farming_assistant.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE farmer_profiles SET is_otp_verified = 1 WHERE username = ?", (request.username,))
            conn.commit()
            conn.close()
            return {"status": "success", "message": "OTP Verified successfully!"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    return {"status": "error", "message": "Invalid OTP code. Try using 1234."}
"""

if os.path.exists("main.py"):
    with open("main.py", "r", encoding="utf-8") as f:
        content = f.read()
    
    if "class ProfileRequest" not in content:
        with open("main.py", "w", encoding="utf-8") as f:
            f.write(content + "\\n" + code_payload)
        print("Backend setup updated successfully! Profile schema and OTP logic added.")
    else:
        print("Profile endpoints are already inside main.py!")
else:
    print("Error: main.py file not found in this directory.")