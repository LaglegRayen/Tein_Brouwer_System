"""Decode and verify base64 credentials"""
import base64

# The base64 encoded credentials from config.py
base64_creds = "cmF5ZW4ubGFnbGVnQGFpbWF0aW9uYXRpb24uY29tOjdjODVhMjI1ODYyYWU5MWU="

try:
    # Decode the credentials
    decoded = base64.b64decode(base64_creds).decode('utf-8')
    print("Decoded credentials:", decoded)
    
    # Split into username and password
    if ':' in decoded:
        username, password = decoded.split(':', 1)
        print("\nUsername:", username)
        print("Password:", password)
        print("\nLength checks:")
        print("Username length:", len(username))
        print("Password length:", len(password))
    else:
        print("Invalid format - missing ':' separator")
        
except Exception as e:
    print("Error decoding credentials:", e)
