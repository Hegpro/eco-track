import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

def test_connection():
    load_dotenv()
    uri = os.getenv("MONGO_URI")
    print(f"[Diagnostic] Testing connection to: {uri[:20]}...")
    try:
        import certifi
        client = MongoClient(uri, serverSelectionTimeoutMS=5000, tlsCAFile=certifi.where(), tlsAllowInvalidCertificates=True)
        client.server_info()
        print("[Diagnostic] SUCCESS: Connected to MongoDB Atlas!")
    except Exception as e:
        print(f"[Diagnostic] ERROR: {e}")
        if "dnspython" in str(e).lower():
            print("[Diagnostic] Tip: You need to install 'dnspython'")
        if "selection timeout" in str(e).lower():
            print("[Diagnostic] Tip: Check your Atlas IP Whitelist (Network Access).")

if __name__ == "__main__":
    test_connection()
