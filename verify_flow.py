import asyncio
import websockets
import json

async def verify_flow():
    uri = "ws://127.0.0.1:7860/api/v1/workflow/chat/test_flow_id"
    
    # Mock Flow Data with Input Node and LLM Node
    flow_data = {
        "id": "test_flow_id",
        "nodes": [
            {
                "id": "node_input_1",
                "type": "InputNode",
                "data": {"type": "input", "input_value": ""}
            },
            {
                "id": "node_llm_1",
                "type": "LLMNode",
                "data": {"model_name": "groq/llama3-8b-8192"} 
            }
        ],
        "edges": [
            {"source": "node_input_1", "target": "node_llm_1"}
        ]
    }

    print(f"Connecting to {uri}...")
    async with websockets.connect(uri) as websocket:
        # 1. Send Init Data
        init_msg = {
            "action": "init_data",
            "chat_id": "test_chat_1",
            "data": flow_data
        }
        await websocket.send(json.dumps(init_msg))
        print("Sent init_data")

        while True:
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Received: {data.get('category')} - {data.get('type')}")
            
            if data.get("category") == "input":
                print("Received Input Request. Sending simulated user input...")
                # Simulate User Input
                input_response = {
                    "action": "input",
                    "chat_id": "test_chat_1",
                    "data": {
                        "node_input_1": {
                            "message": "Who is the president of Indonesia?" 
                        }
                    } 
                }
                await websocket.send(json.dumps(input_response))
                
            elif data.get("category") == "stream_msg":
                print(f"\n[STREAM] LLM Output: {data.get('message')}\n")
                
            elif data.get("type") == "close":
                print("Flow execution finished (Close received).")
                break
            
            elif data.get("category") == "error":
                print(f"ERROR: {data}")
                break

if __name__ == "__main__":
    asyncio.run(verify_flow())
