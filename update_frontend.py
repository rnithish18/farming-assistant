import os

frontend_code = """
    <div style="background: #ffffff; max-width: 500px; margin: 20px auto; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); border-top: 5px solid #2e7d32; font-family: sans-serif;">
        <h3 style="margin-top: 0; color: #2e7d32; border-bottom: 2px solid #e8f5e9; padding-bottom: 8px;">📋 Farmer Registration Profile</h3>
        
        <div id="profile-form-step">
            <div style="margin-bottom: 12px;">
                <label style="display:block; font-weight:bold; margin-bottom:5px; color:#333;">Farmer Name / Identity:</label>
                <input type="text" id="reg-username" value="Nithish" style="width:95%; padding:8px; border:1px solid #ccc; border-radius:6px;">
            </div>
            <div style="margin-bottom: 12px;">
                <label style="display:block; font-weight:bold; margin-bottom:5px; color:#333;">Phone Number:</label>
                <input type="text" id="reg-phone" placeholder="Enter 10-digit mobile number" style="width:95%; padding:8px; border:1px solid #ccc; border-radius:6px;">
            </div>
            <div style="margin-bottom: 12px; display: flex; gap: 10px;">
                <div style="flex: 1;">
                    <label style="display:block; font-weight:bold; margin-bottom:5px; color:#333;">Age:</label>
                    <input type="number" id="reg-age" placeholder="Age" style="width:90%; padding:8px; border:1px solid #ccc; border-radius:6px;">
                </div>
                <div style="flex: 1;">
                    <label style="display:block; font-weight:bold; margin-bottom:5px; color:#333;">Gender:</label>
                    <select id="reg-gender" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:6px; background:white;">
                        <option value="Male">Male</option>
                        <option value="Female">Female</option>
                        <option value="Other">Other</option>
                    </select>
                </div>
            </div>
            <button onclick="submitFarmerProfile()" style="width:100%; background:#2e7d32; color:white; border:none; padding:10px; font-weight:bold; border-radius:6px; cursor:pointer; transition: 0.2s;">Send OTP Verification</button>
        </div>

        <div id="otp-form-step" style="display: none; margin-top: 15px; background: #fff3e0; padding: 15px; border-radius: 8px; border-left: 4px solid #ff9800;">
            <p style="margin: 0 0 10px 0; color:#e65100; font-size:14px; font-weight:bold;">✉️ A simulated verification code was issued! Use <strong>1234</strong> to confirm.</p>
            <label style="display:block; font-weight:bold; margin-bottom:5px; color:#333;">Enter Verification OTP:</label>
            <input type="text" id="verification-otp" placeholder="Enter OTP code" style="width:95%; padding:8px; border:1px solid #ccc; border-radius:6px; margin-bottom:10px;">
            <button onclick="verifyFarmerOTP()" style="width:100%; background:#ff9800; color:white; border:none; padding:10px; font-weight:bold; border-radius:6px; cursor:pointer;">Complete Verification & Unlock Logs</button>
        </div>
        
        <p id="registration-status-msg" style="margin-top:12px; font-weight:bold; font-size:14px; text-align:center; color:#d32f2f;"></p>
    </div>

    <script>
    function submitFarmerProfile() {
        const user = document.getElementById('reg-username').value;
        const phone = document.getElementById('reg-phone').value;
        const age = document.getElementById('reg-age').value;
        const gender = document.getElementById('reg-gender').value;
        const msg = document.getElementById('registration-status-msg');

        if(!user || !phone || !age) {
            msg.style.color = '#d32f2f';
            msg.innerText = '❌ Please fill out all profile parameters completely!';
            return;
        }

        fetch('/register-profile', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username: user, phone_number: phone, age: parseInt(age), gender: gender })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                msg.style.color = '#2e7d32';
                msg.innerText = '✅ ' + data.message;
                document.getElementById('otp-form-step').style.display = 'block';
                // Store local reference for verification binding
                window.currentRegisteringUser = user;
            } else {
                msg.style.color = '#d32f2f';
                msg.innerText = '❌ Error: ' + data.message;
            }
        });
    }

    function verifyFarmerOTP() {
        const otpVal = document.getElementById('verification-otp').value;
        const msg = document.getElementById('registration-status-msg');
        const user = window.currentRegisteringUser || document.getElementById('reg-username').value;

        fetch('/verify-otp', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ username: user, otp: otpVal })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                msg.style.color = '#2e7d32';
                msg.innerText = '🎉 Verification Success! Activity tracking is now unlocked.';
                document.getElementById('otp-form-step').style.display = 'none';
                
                // Automatically switch active window session context to user
                if(typeof window.setProfile === 'function') {
                    document.getElementById('farmer-identity-input-box-id').value = user;
                    window.setProfile();
                } else {
                    localStorage.setItem('farmer_username', user);
                }
            } else {
                msg.style.color = '#d32f2f';
                msg.innerText = '❌ ' + data.message;
            }
        });
    }
    </script>
"""

html_path = os.path.join("static", "index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    if "register-profile" not in html_content:
        # Find structural layout placeholder inside header profile selection space
        if 'Set Profile' in html_content:
            html_content = html_content.replace('Set Profile</button>', 'Set Profile</button>\\n' + frontend_code)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Frontend layout injection complete! Profile and verification form mounted.")
        else:
            # Fallback placement injection before main content wrapper
            html_content = html_content.replace('<body>', '<body>\\n' + frontend_code)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print("Frontend fallback complete! Verification container placed inside body wrapper.")
    else:
        print("Verification elements are already mounted in index.html!")
else:
    print("Error: index.html not found in static directory.")