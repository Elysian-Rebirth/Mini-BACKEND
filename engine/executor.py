import asyncio
from typing import Dict, Any, List
from .nodes import get_node_class

class GraphExecutor:
    def __init__(self, flow_data: Dict):
        self.flow_data = flow_data
        self.nodes = flow_data.get("nodes", [])
        self.edges = flow_data.get("edges", [])
        self.node_map = {n["id"]: n for n in self.nodes}
        # Build adjacency list: target_id -> [source_id, ...] needed?
        # Actually we need source -> target for execution flow
        self.adj = {n["id"]: [] for n in self.nodes}
        for edge in self.edges:
            self.adj[edge["source"]].append(edge["target"])

    async def run(self, inputs: Dict[str, Any] = None):
        if inputs is None:
            inputs = {}
            
        # Find start node(s) - nodes with no incoming edges or specific type
        # For simplicity, assume linear flow starts at 'InputNode' or similar
        start_nodes = [n for n in self.nodes if n["type"] == "InputNode" or n.get("data", {}).get("type") == "input"]
        
        # If no explicit input node, just pick the first one (linear assumption)
        if not start_nodes and self.nodes:
            start_nodes = [self.nodes[0]]

        results = {}
        queue = start_nodes
        
        # Simple BFS/Linear execution
        # Note: This doesn't handle complex merges/branches perfectly yet
        visited = set()
        
        final_output = {}

        while queue:
            current_node_data = queue.pop(0)
            node_id = current_node_data["id"]
            if node_id in visited:
                continue
            visited.add(node_id)
            
            node_type = current_node_data["type"] # or data.type?
            NodeClass = get_node_class(node_type)
            node_instance = NodeClass(current_node_data)
            
            # Prepare inputs from previous results
            # Flatten inputs from all incoming edges
            node_inputs = inputs.copy() # Start with global inputs
            
            # Find incoming edges
            incoming_edges = [e for e in self.edges if e["target"] == node_id]
            for edge in incoming_edges:
                source_id = edge["source"]
                if source_id in results:
                    # Merge outputs from source to input
                    # In Bisheng/LangFlow, edges map sourceHandle to targetHandle
                    # We might need to map specific keys. For now, merge dicts.
                    node_inputs.update(results[source_id])

            print(f"Executing {node_type} ({node_id}) with inputs: {node_inputs}")
            try:
                output = await node_instance.run(node_inputs)
                results[node_id] = output
                final_output = output # Update final output to last executed node
            except Exception as e:
                print(f"Error executing {node_id}: {e}")
                results[node_id] = {"error": str(e)}

            # Add neighbors to queue
            for neighbor_id in self.adj[node_id]:
                if neighbor_id not in visited:
                     queue.append(self.node_map[neighbor_id])
        
        return final_output
