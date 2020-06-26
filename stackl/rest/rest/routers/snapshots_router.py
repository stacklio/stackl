import logging
from typing import List

from fastapi import APIRouter, HTTPException
from stackl.enums.stackl_codes import StatusCode
from stackl.models.history.snapshot_model import Snapshot
from stackl.task_broker.task_broker_factory import TaskBrokerFactory
from stackl.tasks.snapshot_task import SnapshotTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()
task_broker = TaskBrokerFactory().get_task_broker()


@router.get('/{name}', response_model=Snapshot)
async def get_snapshot(name: str):
    logger.info(
        f"[GetSnapSHOT GET] API GET request for snapshot of doc with '{name}'")
    task = SnapshotTask.parse_obj({
        'channel': 'worker',
        'args': name,
        'subtype': "GET_SNAPSHOT"
    })

    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.get('/{type_name}/{name}', response_model=List[Snapshot])
async def get_snapshots(type_name: str, name: str):
    """Returns the snapshots of a specific stackl object"""
    logger.info(
        f"[GetSnapSHOT GET] API GET request for snapshot of doc with type '{type_name}' and '{name}'"
    )
    task = SnapshotTask.parse_obj({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "GET_SNAPSHOTS"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    return result.return_result


@router.post('/restore/{name}')
async def restore_snapshot(name: str):
    """Restore the latest or optionally the given number most recent snapshot of the doc with the given type_name and name """
    logger.info(
        f"[RestoreSnapshot POST] API POST request for doc with '{name}'")
    task = SnapshotTask.parse_obj({
        'channel': 'worker',
        'args': name,
        'subtype': "RESTORE_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)
    if not StatusCode.is_successful(result.result_code):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result.return_result


@router.post('/{type_name}/{name}')
async def create_snapshot(type_name: str, name: str):
    """Create a snapshot for the doc with the given type_name and name """
    logger.info(
        f"[CreateSnapshot POST] API POST request for snapshot of doc with type_name '{type_name}' and '{name}'"
    )
    task = SnapshotTask.parse_obj({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "CREATE_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)
    if not StatusCode.is_successful(result.result_code):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result.return_result


@router.delete('/{name}')
async def delete_snapshot(name: str):
    """Delete the latest or optionally the given number most recent snapshot of the doc with the given type_name and name """
    logger.info(
        f"[DeleteSnapshot DEL] API DEL request for snapshot of doc with name: '{name}'"
    )
    task = SnapshotTask.parse_obj({
        'channel': 'worker',
        'args': name,
        'subtype': "DELETE_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = task_broker.get_task_result(task.id)

    if not StatusCode.is_successful(result.result_code):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result.return_result
