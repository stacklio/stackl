import ast
import asyncio
import json
import logging
import os
import re
import threading

import websockets

from logger import Logger

logger = Logger("Agent")
websockets_logger = logging.getLogger('websockets.server')
websockets_logger.setLevel(logging.INFO)
websockets_handler = logging.handlers.WatchedFileHandler("ws_agent.log")
websockets_logger.addHandler(websockets_handler)
websockets_handler.setLevel(logging.INFO)
websockets_logger.addHandler(logging.StreamHandler())


def get_config_key(key):
    value = os.environ.get(key)
    logger.log("[Agent] get_config_key. Key: '{0}'. Value: '{1}'".format(key, value))
    if value:
        if re.match(r"\[.*?\]", value):
            # String might contain a python literal
            return ast.literal_eval(value)
        else:
            # String was just a string
            return value
    else:
        return ""


def get_stackl_url():
    host = get_config_key('STACKL_HOST')

    if host is "":
        host = "localhost"
    stackl_url = "ws://{}:8888/ws".format(host)
    logger.log("[Agent] Returning stackl_url '{}'".format(stackl_url))
    return stackl_url


class Agent:

    def __init__(self, stackl_url):
        logger.log("[Agent] Starting Agent '{}'".format(self))
        self.stackl_url = stackl_url

        worker_websocket_thread = threading.Thread(target=self.run_worker_websocket)
        worker_websocket_thread.start()

        stackl_websocket_thread = threading.Thread(target=self.run_stackl_websocket)
        stackl_websocket_thread.start()

        # test_loop = threading.Thread(target=self.test_periodic)
        # test_loop.start()

    def run_worker_websocket(self):
        agent_url = self.get_agent_connect_info()

        logger.log("[Agent] run_worker_websocket. Starting new async loop for agent_url '{}'".format(agent_url))
        worker_websocket_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(worker_websocket_loop)

        self.processor_msg = ""
        self.processor_flag = asyncio.Event()

        self.worker_websocket = websockets.serve(self.worker_connection_handler, host="0.0.0.0", port=agent_url[
            "port"])  # Has to be 0.0.0.0 for containers: see https://serverfault.com/questions/769578/curl-56-recv-failure-connection-reset-by-peer-when-hitting-docker-container
        worker_websocket_loop.run_until_complete(self.worker_websocket)
        worker_websocket_loop.run_forever()

    async def worker_connection_handler(self, websocket, path):
        logger.log("[Agent] worker_connection_handler.")
        loop = asyncio.get_event_loop()
        worker_recv_task = asyncio.ensure_future(self.worker_recv_handler(websocket, path), loop=loop)
        worker_send_task = asyncio.ensure_future(self.worker_send_handler(websocket, path), loop=loop)
        logger.log("[Agent] worker_connection_handler. tasks created.")
        done, pending = await asyncio.wait([worker_recv_task, worker_send_task], return_when=asyncio.FIRST_COMPLETED, )
        if worker_recv_task in done:
            logger.log("[Agent] worker_connection_handler. worker_recv_task {0} in done.".format(worker_recv_task))
        if worker_send_task in done:
            logger.log("[Agent] worker_connection_handler. worker_send_task {0} in done.".format(worker_send_task))
        for task in pending:
            logger.log("[Agent] worker_connection_handler. Task {0} in pending. Cancelling".format(task))
            task.cancel()

    async def worker_recv_handler(self, websocket, path):
        logger.log("[Agent] worker_recv_handler. Starting.")
        while True:  # NOTE: async for message in websocket is Python 3.6+
            message = await websocket.recv()
            logger.log("[Agent] worker_recv_handler. Received message from Worker: '{}'".format(message))

            msg_obj = json.loads(message)
            msg_obj.update({"stack_instance_status": "Stack Instance Received by the Agent!"})

            logger.log("[Agent] Replying to worker with updated msg. Message: '{}'".format(msg_obj))
            msg_json = json.dumps(msg_obj)
            await websocket.send(msg_json)

            self.processor_msg = message
            self.processor_flag.set()

    async def worker_send_handler(self, websocket, path):
        logger.log("[Agent] worker_send_handler. Starting.")
        while True:
            message = await self.processor()
            logger.log("[Agent] worker_send_handler. Sending message: '{}'".format(message))
            await websocket.send(json.dumps(message))

    async def processor(self):
        logger.log("[Agent] Waiting for processor flag.")
        await self.processor_flag.wait()
        self.processor_flag.clear()

        msg_obj = json.loads(self.processor_msg)
        if isinstance(msg_obj, str):
            logger.info("[Agent] processor. Message is str. Message: '{}'".format(msg_obj))
        elif isinstance(msg_obj, dict):
            if msg_obj.get("automation_handler", False):
                logger.log("[Agent]  processor. Handing to automation_handler")
                return "____MSG_AUTOMATION_ECHO____" + msg_obj
            else:
                msg_obj.update({"stack_instance_status": "Stack Instance Received and Processed by the Agent!"})
                logger.log(
                    "[Agent] processor. Message is  dictionary. Updating with success. Message: '{}'".format(msg_obj))
                return msg_obj
        else:
            logger.log("[Agent] Fallback processor, just sleeping 5s and returning the reverse message")
            await asyncio.sleep(5)
            return msg_obj[::-1]

    def run_stackl_websocket(self):
        logger.log("[Agent] run_stackl_websocket. Started.")
        stackl_websocket_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(stackl_websocket_loop)
        while True:
            try:
                stackl_websocket_loop.run_until_complete(self.connect_to_stackl())
                stackl_websocket_loop.run_until_complete(self.stackl_recv_handler(self.ws))
            except Exception as e:
                logger.log(
                    "[Agent] Error! Did the connection die? Exception: '{}'. Restarting STACKL connection.".format(e))

    async def connect_to_stackl(self):
        while True:
            try:
                logger.log("[Agent] connect_to_stackl. Trying to connect to '{}'".format(self.stackl_url))
                self.ws = await websockets.client.connect(self.stackl_url)
                await self.ws.send(
                    json.dumps("-----> Agent '{0}' is connecting to Stackl. The agent_connect_info is:".format(self)))
                await self.ws.send(json.dumps(self.get_agent_connect_info()))  # need to send this seperately, as dict
                logger.log("[Agent] Connection succeeded!")
                break
            except Exception as e:
                logger.log("[Agent] connect_to_stackl. Connecting failed. Error: '{}'".format(e))
                logger.log("[Agent] connect_to_stackl. Trying again in 15 seconds.")
                await asyncio.sleep(15)

    def test_periodic(self):
        logger.log("[Agent] test_periodic started.")
        test_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(test_loop)
        count = 0
        while True:
            test_loop.run_until_complete(asyncio.sleep(30))
            logger.log("[Agent] test_periodic run '{}', every 30sec.".format(count))
            self.processor_msg = "Test_Periodic_Message" + str(count)
            self.processor_flag.set()
            count = count + 1

    async def stackl_recv_handler(self, websocket):
        async for message in websocket:
            logger.log("[Agent] stackl_recv_handler. Received message '{}' ".format(message))
            self.receive_msg(message)

    async def stackl_send_handler(self, websocket):
        while True:
            message = await self.send_msg()
            logger.log("[Agent] stackl_send_handler. Sending message '{}' ".format(message))
            await websocket.send(json.dumps(message))

    def receive_msg(self, rec_msg):
        message = rec_msg  # rec_msg.data.decode("utf-8")
        logger.log("[Agent] received: '{}'".format(message))

    def send_msg(self):
        logger.log("[Agent] Sending a message: '{}'".format("Hi"))
        return "TODO: Implement message"

    def get_agent_connect_info(self):
        agent_url = {"is_agent_url": True, "host": get_config_key("HOST_MACHINE"), "port": 8889,
                     "tags": get_config_key("TAGS")}
        logger.log("[Agent] Returning agent url '{}'.".format(agent_url))
        return agent_url


if __name__ == "__main__":
    try:
        # app.run(host="0.0.0.0", port=int("5000"), debug=True)
        stackl_url = get_stackl_url()
        agent = Agent(stackl_url)

    except Exception as e:
        logger.error("[Agent] Exception occured at top level:'{}'. Exit.".format(e))
