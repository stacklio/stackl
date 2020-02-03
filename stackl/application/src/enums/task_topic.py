from enum import Enum 
import sys


from task import Task
from task.query_task import QueryTask
from task.ping_task import PingTask
from task.result_task import ResultTask
from task.document_task import DocumentTask

class TaskTopic(Enum):
    query =  QueryTask
    ping =  PingTask
    result =  ResultTask
    document =  DocumentTask
