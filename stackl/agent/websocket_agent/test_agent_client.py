import asyncio
import websockets
import os
import json
import time
import socket
import threading

class Agent_Server_Client:

    agent_server_uri = "ws://localhost:8889"    #local
    #agent_server_uri = "ws://52.210.80.33.:8889"    #remote
    
    def __init__(self):
        asyncio.get_event_loop().run_until_complete(self.test())

    async def test(self):
        print("[Test_Agent_Server_Client] Starting test")
        count = 0
        async with websockets.connect(self.agent_server_uri) as websocket:
            while True:
                count +=1
                print("[Test_Agent_Server_Client] Sending Test Msg {}".format(count))
                await websocket.send(json.dumps({"Test Message " : str(count)}))
                response = await websocket.recv()
                print("[Test_Agent_Server_Client] Received response: {}".format(response))
                await asyncio.sleep(15)

if __name__ == "__main__":
    try:
        #app.run(host="0.0.0.0", port=int("5000"), debug=True)
        agent = Agent_Server_Client()

    except Exception as e:
        print("[Test_Agent_Server_Client] !!!ERROR!!! EXCEPTION OCCURED IN AGENT TOP LEVEL:'{}'. Exit.".format(e))
