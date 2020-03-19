import asyncio
import json
import os
import threading

import websockets


def get_config_key(key):
    value = os.environ.get(key)
    print("[Agent] get_config_key. Key: '{0}'. Value: '{1}'".format(key, value))
    if value:
        return value
    else:
        return ""


class Agent_Server_Test:

    def __init__(self):
        print("[Agent_Server_Test] Starting Agent '{}'".format(self))

        self.producer_message = ""
        self.producer_flag = threading.Event()

        agent_worker_thread = threading.Thread(target=self.run_worker_websocket)
        agent_worker_thread.start()
        test_loop = threading.Thread(target=self.test_periodic)
        test_loop.start()

    def run_worker_websocket(self):
        agent_url = self.get_agent_url()
        print("[Agent_Server_Test] run_worker_websocket started for agent_url '{}'".format(agent_url))
        agent_worker_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(agent_worker_loop)
        self.agent_websocket = websockets.serve(self.worker_connection_handler, host=agent_url["host"],
                                                port=agent_url["port"])
        agent_worker_loop.run_until_complete(self.agent_websocket)
        agent_worker_loop.run_forever()

    def get_agent_url(self):
        agent_url = {"is_agent_url": True, "host": "0.0.0.0", "port": 8889}
        print("[Agent_Server_Test] Returning agent url '{}'.".format(agent_url))
        return agent_url

    async def worker_connection_handler(self, websocket, path):
        print("[Agent_Server_Test] worker_connection_handler activated.")
        worker_recv_task = asyncio.create_task(self.worker_recv_handler(websocket, path))
        worker_send_task = asyncio.create_task(self.worker_send_handler(websocket, path))
        done, pending = await asyncio.wait([worker_recv_task, worker_send_task], return_when=asyncio.FIRST_COMPLETED, )
        for task in pending:
            task.cancel()

    async def worker_recv_handler(self, websocket, path):
        print("[Agent_Server_Test] worker_recv_handler start.")
        async for message in websocket:
            print("[Agent_Server_Test] worker_recv_handler. Received message from Worker: '{}'".format(message))
            self.producer_message = message
            self.producer_flag = True

    async def worker_send_handler(self, websocket, path):
        print("[Agent_Server_Test] worker_send_handler start.")
        while True:
            message = await self.producer()
            print("[Agent_Server_Test] worker_send_handler. Sending message '{}'".format(message))
            await websocket.send(json.dumps(message))

    async def producer(self):
        print("[Agent_Server_Test] Waiting for producer_flag.")
        self.producer_flag.wait()
        print("[Agent_Server_Test] producer flag set to true. Activating producer.")
        self.producer_flag.clear()
        return self.producer_message[::-1]

    def test_periodic(self):
        print("[Agent_Server_Test] test_periodic started.")
        test_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(test_loop)
        count = 0
        while True:
            test_loop.run_until_complete(asyncio.sleep(30))
            print("[Agent_Server_Test] test_periodic run '{}', every 30sec.".format(count))
            self.producer_message = "Test_Periodic_Message" + str(count)
            self.producer_flag.set()
            count = count + 1


if __name__ == "__main__":
    try:
        # app.run(host="0.0.0.0", port=int("5000"), debug=True)
        agent = Agent_Server_Test()

    except Exception as e:
        print("[Agent_Server_Test] !!!ERROR!!! EXCEPTION OCCURED IN AGENT TOP LEVEL:'{}'. Exit.".format(e))
