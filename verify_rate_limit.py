import requests
import asyncio
import websockets
import json
import time

API_URL = "http://127.0.0.1:7860/api/v1/flows"
WS_URL = "ws://127.0.0.1:7860/api/v1/workflow/chat/test_limit"

def test_http_limit():
    print("Testing HTTP Rate Limit (30/min)...")
    start = time.time()
    for i in range(40):
        try:
            res = requests.get(API_URL)
            if res.status_code == 429:
                print(f"HTTP Limit hit at request {i+1}! (Status 429)")
                return
        except Exception as e:
            print(f"Req failed: {e}")
    print("Finished HTTP requests without hitting limit (Potential Issue)")

async def test_ws_limit():
    print(f"\nTesting WebSocket Rate Limit (10 connections/min)...")
    success_count = 0
    blocked_count = 0
    
    for i in range(15):
        try:
            async with websockets.connect(WS_URL) as ws:
                # Init
                await ws.send(json.dumps({"action": "init_data", "data": {}}))
                # Wait a bit
                await asyncio.sleep(0.1)
                success_count += 1
                print(f"Connection {i+1}: Success")
                
        except websockets.exceptions.InvalidStatusCode as e:
            if e.status_code == 403 or e.status_code == 1008: # WS handshake fail often returns 403 or closes with 1008
                 print(f"Connection {i+1}: Blocked ({e.status_code})")
                 blocked_count += 1
        except websockets.exceptions.ConnectionClosed as e:
             if e.code == 1008:
                 print(f"Connection {i+1}: Blocked (Code 1008)")
                 blocked_count += 1
             else:
                 success_count += 1 # Normal close
        except Exception as e:
            print(f"Connection {i+1}: Error {e}")
            
    if blocked_count > 0:
        print("WS Limit Verified! Blocked excess connections.")
    else:
        print("Failed to verify WS Limit (All connected).")

if __name__ == "__main__":
    test_http_limit()
    asyncio.run(test_ws_limit())
