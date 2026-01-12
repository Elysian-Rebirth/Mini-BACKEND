from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Any
import json
import logging
from engine.executor import GraphExecutor

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/chat/{flow_id}")
async def websocket_endpoint(websocket: WebSocket, flow_id: str):
    await websocket.accept()
    client_ip = websocket.client.host
    logger.info(f"WebSocket connected for flow {flow_id} from {client_ip}")
    
    # Global Rate Limit for WS (IP based)
    import time
    from collections import defaultdict, deque
    
    # Initialize global state if not exists (hacky for this function scope but works if module level)
    # Better: Use a module-level variable. 
    # But for replace_file, I'll assume I can access a global or declare it here? 
    # No, declare it module level or use an attribute.
    # Let's use a simple pattern: attribute on the function or module level dict.
    
    global ws_request_counts 
    if 'ws_request_counts' not in globals():
        ws_request_counts = defaultdict(list)
        
    WS_RATE_LIMIT = 10
    WS_RATE_WINDOW = 60
    
    try:
        # Check Rate Limit on Connect/Init
        now = time.time()
        # Clean old
        ws_request_counts[client_ip] = [t for t in ws_request_counts[client_ip] if now - t < WS_RATE_WINDOW]
        
        if len(ws_request_counts[client_ip]) >= WS_RATE_LIMIT:
             logger.warning(f"WS Rate Limit exceeded for {client_ip}")
             await websocket.close(code=1008, reason="Rate limit exceeded")
             return
        ws_request_counts[client_ip].append(now)

        # 1. Wait for init_data or check_status
        data = await websocket.receive_json()
        
        logger.info(f"Received initial message: {data.get('action')}")
        
        if data.get("action") == "check_status":
             # Just ack?
             pass
        
        flow_data = data.get("data", {})
        if not flow_data and data.get("action") == "init_data":
             # If data is empty, maybe fetch from DB?
             # For now assume frontend sends it as per ChatPane.tsx logic
             logger.warning("No flow data in init_data")
        
        # 2. Initialize Executor
        executor = GraphExecutor(flow_data)
        
        # 3. Check for Input Node
        # We need to ask for input if we don't present it?
        # Bisheng logic: If flow has Input node, it asks user.
        # Let's see if we can identify Input Node.
        input_nodes = [n for n in executor.nodes if "input" in n["type"].lower() or "start" in n["type"].lower()]
        start_node_id = input_nodes[0]["id"] if input_nodes else None
        
        if start_node_id:
            # 4. Request Input
            # Construct input_schema (mock)
            # This triggers ChatInput to unlock and let user type
            req_msg = {
                "category": "input",
                "message_id": "req_input_1",
                "message": {
                    "node_id": start_node_id,
                    "input_schema": {
                        "tab": "dialog_input", # or form_input
                        # mock value schema
                        "value": [{"key": "dialog_file_accept", "value": "all"}]
                    }
                }
            }
            await websocket.send_json(req_msg)
            
            # 5. Wait for User Input
            input_msg = await websocket.receive_json()
            logger.info(f"Received input: {input_msg.get('action')}")
            
            # Extract user text
            # Structure: data[node_id].message
            user_input_text = ""
            if "data" in input_msg:
                node_inputs = input_msg["data"].get(start_node_id, {})
                user_input_text = node_inputs.get("message", "")
                
            initial_inputs = {"input_value": user_input_text, "text": user_input_text}
        else:
            # No input node, run automatically
            initial_inputs = {}
            
        # 6. Run Executor
        # Send 'start' message
        await websocket.send_json({"type": "begin", "category": "processing"})
        
        # Execute
        # Pass user input to executor
        # We assume the first node takes "input_value" or similar
        
        # Mock Node Runs
        # In a real loop we would send node_run events
        if start_node_id:
            await websocket.send_json({
                "category": "node_run",
                "type": "start",
                "message": {"node_id": start_node_id}
            })
        
        result = await executor.run(initial_inputs)
        
        if start_node_id:
            await websocket.send_json({
                "category": "node_run",
                "type": "end",
                "message": {
                    "node_id": start_node_id, 
                    "input_data": initial_inputs
                }
            })
            
            # 7. Send Response
            # Assume result contains 'result' or 'text'
            final_text = str(result.get("result", result))
            
            # Send stream message (or simple answer)
            await websocket.send_json({
                "category": "stream_msg",
                "message": final_text,
                "node_id": "final_node",
                "receiver": None
            })
            
            # Send Over/Close
            await websocket.send_json({
                "type": "close",
                "category": "processing",
                "chat_id": data.get("chat_id")
            })

    except WebSocketDisconnect:
        logger.info(f"Client disconnected {flow_id}")
    except Exception as e:
        logger.error(f"Error: {e}")
        await websocket.send_json({
            "category": "error",
            "message": {"status_code": 500, "message": str(e)}
        })

