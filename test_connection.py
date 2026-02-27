#!/usr/bin/env python
"""
Test Snowflake connection and diagnose 404 / connection issues.
Run from project root: python test_connection.py
"""
import os
import sys

# Ensure .env is loaded from script directory (project root when run as python test_connection.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(script_dir, ".env")
if os.path.exists(env_path):
    from dotenv import load_dotenv
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"Warning: No .env at {env_path}")

account = os.getenv("SNOWFLAKE_ACCOUNT")
user = os.getenv("SNOWFLAKE_USER")
password = os.getenv("SNOWFLAKE_PASSWORD")
database = os.getenv("SNOWFLAKE_DATABASE")
warehouse = os.getenv("SNOWFLAKE_WAREHOUSE")

print("\n--- Config (password hidden) ---")
print(f"  SNOWFLAKE_ACCOUNT:   {account or '(not set)'}")
print(f"  SNOWFLAKE_USER:      {user or '(not set)'}")
print(f"  SNOWFLAKE_DATABASE:  {database or '(not set)'}")
print(f"  SNOWFLAKE_WAREHOUSE: {warehouse or '(not set)'}")

if not all([account, user, password]):
    print("\nError: Set SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, and SNOWFLAKE_ACCOUNT in .env")
    sys.exit(1)

# Show the URL the connector will use
url = f"https://{account}.snowflakecomputing.com"
print(f"\n  Login URL (used by connector): {url}")

print("\n--- Connecting ---")
try:
    import snowflake.connector
    conn = snowflake.connector.connect(
        user=user,
        password=password,
        account=account,
        database=database or None,
        warehouse=warehouse or None,
        client_session_keep_alive=True,
        network_timeout=15,
        login_timeout=15,
    )
    with conn.cursor() as cur:
        cur.execute("SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), 1")
        row = cur.fetchone()
        print(f"  Connected. Account: {row[0]}, Region: {row[1]}")
    conn.close()
    print("\nConnection test OK.")
except Exception as e:
    print(f"\nConnection failed: {e}")
    if "404" in str(e):
        print("""
--- 404 Not Found usually means wrong SNOWFLAKE_ACCOUNT ---
1. In Snowflake (Snowsight), open the account selector and note the URL or "Account identifier".
2. Use that exact value for SNOWFLAKE_ACCOUNT (e.g. orgname-accountname or accountlocator.region).
3. Try without region first: e.g. AMPXXYB-BXB87131 instead of AMPXXYB-BXB87131.us-east-1
4. Or use the full account identifier from: Admin > Accounts > your account.
""")
    sys.exit(1)
