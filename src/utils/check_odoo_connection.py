import odoorpc
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Setup path
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.append(str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env")

def diagnose():
    url = os.getenv("ODOO_URL", "http://localhost:8069")
    db = os.getenv("ODOO_DB")
    user = os.getenv("ODOO_USER")
    pwd = os.getenv("ODOO_PASS")

    print(f"--- Odoo Connection Diagnostics ---")
    print(f"URL: {url}")
    print(f"DB: '{db}'")
    print(f"User: '{user}'")
    
    try:
        host = url.split("//")[-1].split(":")[0]
        port = int(url.split(":")[-1])
        odoo = odoorpc.ODOO(host, port=port)
        
        # 1. Check available databases
        dbs = odoo.db.list()
        print(f"Available Databases on Server: {dbs}")
        
        if db not in dbs:
            print(f"❌ ERROR: Database '{db}' not found on server!")
            return

        # 2. Try Login
        try:
            odoo.login(db, user, pwd)
            print("✅ SUCCESS: Login successful!")
        except Exception as login_err:
            print(f"❌ LOGIN FAILED: {login_err}")
            print(f"Tip: Check if password has special characters or trailing spaces in .env")

    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")

if __name__ == "__main__":
    diagnose()
