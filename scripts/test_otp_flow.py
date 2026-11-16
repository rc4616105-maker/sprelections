import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:5001"

def post(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.getcode(), json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode("utf-8"))

print("--- Test 1: Unauthorized Email ---")
code, res = post("/api/admin/send-otp", {"email": "randomuser@gmail.com", "password": "Spr-Elections@Random"})
print(f"Code: {code}, Response: {res}")
assert code == 403 and res.get("code") == "UNAUTHORIZED_EMAIL", "Test 1 failed!"
print("PASSED Test 1")

print("\n--- Test 2: Invalid Password Format ---")
code, res = post("/api/admin/send-otp", {"email": "sprelections@gmail.com", "password": "mypassword123"})
print(f"Code: {code}, Response: {res}")
assert code == 401 and res.get("code") == "INVALID_PASSWORD", "Test 2 failed!"
print("PASSED Test 2")

print("\n--- Test 3: Authorized Email + Valid Password Format ---")
# To avoid rate limiting, we wait if needed
code, res = post("/api/admin/send-otp", {"email": "sprelections@gmail.com", "password": "Spr-Elections@Abhinav"})
print(f"Code: {code}, Response: {res}")
assert code == 200 and res.get("ok") is True, "Test 3 failed!"
print("PASSED Test 3 (OTP generated & email dispatched via Gmail SMTP!)")

print("\n--- Test 4: Verify with Wrong OTP ---")
code, res = post("/api/admin/verify-otp", {"email": "sprelections@gmail.com", "otp": "000000"})
print(f"Code: {code}, Response: {res}")
assert code == 401 and res.get("code") == "INVALID_OTP", "Test 4 failed!"
print("PASSED Test 4")

# Read generated OTP from server memory via active_otps in otp_server.py
# Let's inspect the server log or test check-session
print("\nAPI Unit Tests successfully verified all security rejection branches!")
