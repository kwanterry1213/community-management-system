import requests

url = 'http://localhost:8000/api/upload'
files = {'file': ('test.txt', b'hello world', 'text/plain')}

try:
    # Check debug endpoint first
    print("Checking debug endpoint...")
    debug_resp = requests.get('http://localhost:8000/api/debug-upload')
    print(f"Debug Endpoint Status: {debug_resp.status_code}")
    print(f"Debug Endpoint Content-Type: {debug_resp.headers.get('content-type')}")
    print(f"Debug Endpoint Content (first 100 chars): {debug_resp.text[:100]}")
    
    print(f"\nUploading to {url}...")
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 405:
        print("\n\n!!! CRITICAL ERROR: 405 Method Not Allowed !!!")
        print("This means the '/api/upload' endpoint is MISSING from the running server.")
        print("The request is falling through to the SPA catch-all route which only accepts GET.")
        print("SOLUTION: You MUST restart the backend server (close window and run start_server again).")
        
except Exception as e:
    print(f"Error: {e}")
