import redis

from job_broker.message_channel.message_channel import MessageChannel
from stackl.utils.general_utils import get_config_key

from stackl.tasks.agent_task import AgentTask


class RedisChannel(MessageChannel):
    def __init__(self):
        self.redis = redis.StrictRedis(host=get_config_key("REDIS_HOST"),
                                       port=6379)

    def register_agent(self, name, selector):
        self.redis.set(f'agents/{name}', selector)

    def unregister_agent(self, agent):
        self.redis.delete(agent)

    def listen_for_jobs(self, agent, callback_function):
        agent_p = self.redis.pubsub()
        agent_p.subscribe(agent)
        for message in agent_p.listen():
            if message["type"] == "subscribe":
                continue
            agent_task = AgentTask.parse_raw(message["data"])
            yield callback_function(agent_task)
