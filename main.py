from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import math

app = FastAPI()

class ConnectionManager:
    """Manages active browser connections for instant updates."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()
queue = [] # Players waiting: {"id", "name", "skill", "games_played"}
courts = {} # Active games: {"court_1": {"players": [], "start_time": ""}}

def calculate_match_quality(players: List[dict]):
    """Calculates how 'balanced' a 4-some is using Standard Deviation."""
    skills = [p['skill'] for p in players]
    avg = sum(skills) / 4
    variance = sum((s - avg) ** 2 for s in skills) / 4
    return math.sqrt(variance) # Lower is better/more balanced

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "JOIN_QUEUE":
                new_player = {
                    "name": message["name"],
                    "skill": float(message["skill"]),
                    "wait_start": message["time"],
                    "history": [] # IDs of people they've already played with
                }
                queue.append(new_player)
                
            await manager.broadcast({"type": "UPDATE", "queue": queue, "courts": courts})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
