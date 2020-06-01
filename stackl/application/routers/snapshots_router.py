import logging
from collections.abc import Collection

from fastapi import APIRouter, HTTPException, Request

from enums.stackl_codes import StatusCode
from manager.manager_factory import ManagerFactory
from model.configs.document_model import BaseDocument, CollectionDocument
from model.history.snapshot_model import Snapshot
from task_broker.task_broker_factory import TaskBrokerFactory
from task.snapshot_task import SnapshotTask

logger = logging.getLogger("STACKL_LOGGER")
router = APIRouter()

document_manager = ManagerFactory().get_document_manager()
task_broker = TaskBrokerFactory().get_task_broker()


@router.get('/{type_name}/{name}', response_model=Snapshot)
async def get_snapshot(type_name: str, name: str, snapshot_nb: int = 1):
    """Returns  either the latest or optionally the snapshot_nb most recent snapshot for doc with type_name and name"""
    logger.info(
        f"[GetSnapSHOT GET] API GET request for snapshot of doc with type '{type_name}' and '{name}' and snapshot_nb '{snapshot_nb}'"
    )
    task = SnapshotTask({
        'channel': 'worker',
        'args': (type_name, name, snapshot_nb),
        'subtype': "GET_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    if not isinstance(result, Collection):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result


@router.get('/list/{type_name}/{name}', response_model=CollectionDocument)
async def list_snapshots(type_name: str, name: str):
    """Returns all the snapshots for doc with type_name and name """
    logger.info(
        f"[ListSnapshots GET] API GET request for snapshot of doc with type_name '{type_name}' and '{name}' "
    )
    task = SnapshotTask({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "LIST_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if not isinstance(result, Collection):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")

    document: CollectionDocument = {
        "name": "CollectionDocumentForSnapshot_" + name,
        "description": "Document that contains all the snapshots for " + name,
        "type": "snapshot",
        "documents": result
    }
    return document


@router.post('/{type_name}/{name}')
async def create_snapshot(type_name: str, name: str):
    """Create a snapshot for the doc with the given type_name and name """
    logger.info(
        f"[CreateSnapshot POST] API POST request for snapshot of doc with type_name '{type_name}' and '{name}'"
    )
    task = SnapshotTask({
        'channel': 'worker',
        'args': (type_name, name),
        'subtype': "CREATE_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    if not StatusCode.isSuccessful(result):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result


@router.post('/restore/{type_name}/{name}')
async def restore_snapshot(type_name: str, name: str, snapshot_nb: int = 1):
    """Restore the latest or optionally the given number most recent snapshot of the doc with the given type_name and name """
    logger.info(
        f"[RestoreSnapshot POST] API POST request for doc with type_name '{type_name}' and '{name}' and snapshot_nb '{snapshot_nb}'"
    )
    task = SnapshotTask({
        'channel': 'worker',
        'args': (type_name, name, snapshot_nb),
        'subtype': "RESTORE_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)
    if not StatusCode.isSuccessful(result):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result


@router.delete('/{type_name}/{name}')
async def delete_snapshot(type_name: str, name: str, snapshot_nb: int = 1):
    """Delete the latest or optionally the given number most recent snapshot of the doc with the given type_name and name """
    logger.info(
        f"[DeleteSnapshot DEL] API DEL request for snapshot of doc with type_name '{type_name}' and '{name}' and snapshot_nb '{snapshot_nb}'"
    )
    task = SnapshotTask({
        'channel': 'worker',
        'args': (type_name, name, snapshot_nb),
        'subtype': "DELETE_SNAPSHOT"
    })
    task_broker.give_task(task)
    result = await task_broker.get_task_result(task.id)

    if not StatusCode.isSuccessful(result):
        raise HTTPException(status_code=StatusCode.BAD_REQUEST,
                            detail="NOT OK!")
    return result