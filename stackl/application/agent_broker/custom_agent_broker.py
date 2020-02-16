import asyncio
import datetime
import json
import logging
import socket

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import websockets

import globals
from agent_broker import AgentBroker

logger = logging.getLogger(__name__)


class CustomAgentBroker(AgentBroker):
    agent_connections = []

    def __init__(self):
        super(CustomAgentBroker, self).__init__()

    def start(self):
        logger.info("[CustomAgentBroker] Starting CustomAgentBroker")
        self.websockets = {}

        self.start_websockets()

    def start_websockets(self):
        logger.info("[CustomAgentBroker] start_websockets.")
        application = tornado.web.Application([
            (r'/ws', self.AgentConnectionHandler, dict(agent_broker=self))
        ])

        asyncio.set_event_loop(asyncio.new_event_loop())
        http_server = tornado.httpserver.HTTPServer(application)
        tornado.options.options.log_file_prefix = '/var/log/tornado.log'
        tornado.options.parse_command_line()
        http_server.listen(8888)
        myIP = socket.gethostbyname(socket.gethostname())
        logger.info("[CustomAgentBroker] Listening for websockets for Agents at {}**".format(myIP))
        io_loop = tornado.ioloop.IOLoop.current()
        io_loop.start()

    def register_agent_connect_info(self, agent_connect_info):
        logger.debug("[CustomAgentBroker] register_agent_connect_info. Registering agent_ws info '{}'".format(
            agent_connect_info))
        reg_agents = globals.get_registered_agents()
        if agent_connect_info in reg_agents:
            logger.debug(
                "[CustomAgentBroker] register_agent_ws. Agent already registered! Registered agents: '{0}'".format(
                    reg_agents))
        else:
            reg_agents.append(agent_connect_info)
            globals.set_registered_agents(reg_agents)
            logger.debug(
                "[CustomAgentBroker] register_agent_ws. New agent added. Registered agents: '{0}'".format(reg_agents))

    def get_agent_for_task(self, task):
        registered_agents = globals.get_registered_agents()
        logger.debug(
            "[CustomAgentBroker] get_agent_for_task. Determining appropriate agent for task '{0}' from  registered_agents '{1}'".format(
                task.__dict__, registered_agents))
        try:
            for agent_info in registered_agents:
                logger.debug(
                    "[CustomAgentBroker] get_agent_for_task. Looking at agent '{0}' for task with requester_auth '{1}".format(
                        agent_info, task.requester_auth))
                if task.requester_auth["tags"] in agent_info["tags"]:  # TODO get the tagging system going
                    logger.debug("[CustomAgentBroker] get_agent_for_task. Found appropriate agent! Returning.")
                return agent_info
        except Exception as e:
            logger.debug(
                "[CustomAgentBroker] get_agent_for_task. Failed. Exception: '{0}'. Returning none.".format(e))
            return None

    async def send_to_agent(self, agent_connect_info, obj):
        try:  # TODO ugly fix for the grpc methodology
            obj_str = json.dumps(obj)
        except:
            obj_str = obj.SerializeToString()
        websocket_uri = agent_connect_info["websocket"]
        logger.debug("[CustomAgentBroker] send_to_agent. Sending to agent with uri '{0}' the obj '{1}'".format(
            agent_connect_info, obj_str))
        try:
            response = ""
            async with websockets.connect(websocket_uri) as websocket:
                await websocket.send(obj_str)
                response_json = await websocket.recv()
                response = json.loads(response_json)
                logger.debug("[CustomAgentBroker] Awaiting response '{0}'".format(response))
                return response
        except websockets.exceptions.ConnectionClosedOK:
            logger.debug("[CustomAgentBroker] ConnectionClosedOK. Received response '{0}'".format(response))
            return response
        except Exception as e:
            logger.debug(
                "[CustomAgentBroker] send_to_agent. Exception occurred: '{0}'. Returning empty response ".format(e))

    def get_websocket_overview(self):
        logger.debug("[CustomAgentBroker] In get_websocket_overview. ")
        return_obj = {}
        if self.websockets:
            logger.debug("[CustomAgentBroker] In get_websocket_overview first check")
            for tag in self.websockets:
                logger.debug("[CustomAgentBroker] Looping websockets")
                if tag == 'all_sockets':
                    continue
                return_obj[tag] = []
                for ws in self.websockets[tag]:
                    logger.debug("[CustomAgentBroker] looping websockets tags get_websocket_overview")
                    return_obj[tag].append({
                        "remote_hostname ": ws.remote_hostname,
                        "serial": ws.certificate['serialNumber']
                    })
        return return_obj

    class AgentConnectionHandler(tornado.websocket.WebSocketHandler):
        def initialize(self, agent_broker):
            self.timeout = None

            self.agent_broker = agent_broker
            logger.info("[AgentConnectionHandler] Initialising AgentConnectionHandler")

        def open(self):
            logger.info("[AgentConnectionHandler] New connection for AgentConnectionHandler")
            try:
                # self.certificate = self.request.get_ssl_certificate()
                # self.remote_ip = self.request.remote_ip

                self.agent_broker.agent_connections.append(self)
                self.write_message(
                    "[AgentConnectionHandler] STACK has received the connection. Waiting for registration.")

            except Exception as e:
                logger.error("[AgentConnectionHandler] Exception occured ... Closing! Exception: {0}".format(e))
                self.close()

        def on_pong(self, message):
            logger.info("[AgentConnectionHandler] received pong: " + str(message))

        def on_message(self, message):
            try:
                msg_obj = json.loads(message)

                if isinstance(msg_obj, str):
                    logger.info(
                        "[AgentConnectionHandler] on_message. Message is str. Message: '{}'".format(message))
                elif isinstance(msg_obj, dict):
                    logger.info(
                        "[AgentConnectionHandler] on_message. Message is dict. Message: '{}'".format(message))
                    if msg_obj.get("is_agent_url", False):
                        logger.info(
                            "[AgentConnectionHandler] on_message. Received agent_url: '{}'. Going to register.".format(
                                msg_obj["is_agent_url"]))
                        agent_connect_info = {"websocket": "ws://{0}:{1}".format(msg_obj["host"], msg_obj["port"]),
                                              "tags": msg_obj["tags"]}
                        self.agent_broker.register_agent_connect_info(agent_connect_info)
                    elif msg_obj.get("keepAlive", False):
                        self.remote_hostname = msg_obj['keepAlive']
                        logger.info("[AgentConnectionHandler] KeepAlive received from: " + str(
                            msg_obj['keepAlive']) + ". Refreshing...")
                        if self.timeout:
                            tornado.ioloop.IOLoop.current().remove_timeout(self.timeout)
                            self.timeout = None
                        self.timeout = tornado.ioloop.IOLoop.current().add_timeout(datetime.timedelta(seconds=65),
                                                                                   self.close_on_timeout)
                        self.write_message({
                            "keepAlive": "ack"
                        })
                else:
                    logger.info("[AgentConnectionHandler] on_message. Message is weird. Ignoring.")
            except Exception as e:
                logger.error("[AgentConnectionHandler] Faulty message. Error: {}".format(str(e)))

        def close_on_timeout(self):
            logger.info("[AgentConnectionHandler] Closing websocket! KeepAlive missed...")
            self.close()

        def check_origin(self, origin):
            return True
