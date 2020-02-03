#!/usr/local/bin/python

from flask_restplus import reqparse
from flask import Flask, Blueprint
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_cors import CORS
import sys
import threading
import time

from task_broker.task_broker_factory import TaskBrokerFactory
import globals
from logger import Logger

from agent_broker.agent_broker_factory import AgentBrokerFactory
from handler.task_handler import TaskHandler
from manager.manager_factory import ManagerFactory
from utils.general_utils import get_hostname

def stackl_alive_counter():
    while True:
        logger.log("Stackl_App Alive Count (incremented every 30sec): {}".format(globals.get_alive_count()))
        count = globals.get_alive_count() + 1
        globals.set_alive_count(count)
        time.sleep(30)

### Start initialisation of Application Logic
try:
    logger = Logger("STACKL_APP")
    logger.info("@@@@@@@@@@@@@@@@@ STARTING STACKL_APP @@@@@@@@@@@@@@@@@@")

    globals.initialize()


    manager_factory = ManagerFactory()
    task_broker_factory = TaskBrokerFactory()

    agent_broker_factory = AgentBrokerFactory()
    agent_broker = agent_broker_factory.agent_broker
    task_broker = task_broker_factory.get_task_broker()

    agent_broker_thread = threading.Thread(name = "Agent Broker Thread", target=agent_broker.start, args=[])
    agent_broker_thread.daemon = True
    agent_broker_thread.start()
    
    task_broker_thread = threading.Thread(name = "Task Broker Thread", target=task_broker.start_stackl, 
            kwargs= {"subscribe_channels":['all', get_hostname(),'rest'], "agent_broker" : agent_broker})
    task_broker_thread.daemon = True
    task_broker_thread.start()

    alive_count_thread = threading.Thread(name = "Stackl Alive Count Thread", target=stackl_alive_counter, args=[])
    alive_count_thread.daemon = True
    alive_count_thread.start()


except Exception as e:
    logger.error("[STACKL_APP] Exception in loading of application logic: {}".format(e))

### Start initialisation of Interface and API logic
try:
    from api import api
    logger.info("___________________ STARTING STACKL_API ____________________")

    app = Flask(__name__)
    CORS(app)
    bootstrap = Bootstrap()
    moment = Moment()
    blueprint = Blueprint('stackl_api', __name__)
    api.init_app(blueprint)
    bootstrap.init_app(app)
    moment.init_app(app)
    app.config['RESTPLUS_VALIDATE'] = True
    app.register_blueprint(blueprint)
    parser = reqparse.RequestParser()
    parser.add_argument('task')
    
    ######
    # Main function
    ######
    if __name__ == '__main__':
        app.run(debug=True, host='0.0.0.0', port=8080)
        # app.run(debug=False,host='0.0.0.0',port=8080)

except Exception as e:
    logger.error("[STACKL_APP] Exception in loading of Interface and API logic: {}".format(e))
