"""
Endpoint for CRUD operations on snapshots
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from starlette.background import BackgroundTasks

from core.agent_broker.agent_task_broker import create_job_for_agent
from core.manager.document_manager import DocumentManager
from core.manager.snapshot_manager import SnapshotManager
from core.manager.stackl_manager import get_snapshot_manager, get_redis, get_document_manager
from core.models.history.snapshot_model import Snapshot
from core.models.items.stack_instance_model import StackInstance

router = APIRouter()


@router.get('/{name}', response_model=Snapshot)
def get_snapshot(
        name: str,
        snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Get a snapshot from the store"""
    logger.info(
        f"GET request for snapshot of doc with '{name}'")
    snapshot = snapshot_manager.get_snapshot(name)
    if not snapshot:
        raise HTTPException(status_code=404, detail="Snapshot not found")
    return snapshot


@router.get('/{type_name}/{name}', response_model=List[Snapshot])
def get_snapshots(
        type_name: str,
        name: str,
        snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Returns the snapshots of a specific stackl object"""
    logger.info(
        f"GET request for snapshot of doc with type '{type_name}' and '{name}'"
    )

    snapshots = snapshot_manager.get_snapshots(type_name, name)

    return snapshots


@router.post('/restore/{name}')
def restore_snapshot(
        name: str,
        background_tasks: BackgroundTasks,
        document_manager: DocumentManager = Depends(get_document_manager),
        snapshot_manager: SnapshotManager = Depends(get_snapshot_manager),
        redis=Depends(get_redis)):
    """
    Restore the latest or optionally the given number most recent snapshot
    of the doc with the given type_name and name
    """
    logger.info(
        f"[RestoreSnapshot POST] API POST request for doc with '{name}'")

    snapshot_document = snapshot_manager.restore_snapshot(name)

    if snapshot_document['snapshot']["type"] == "stack_instance":
        stack_instance = StackInstance.parse_obj(snapshot_document["snapshot"])
        background_tasks.add_task(create_job_for_agent, stack_instance,
                                  "update", document_manager, redis)
        return {"result": "stack instance restored, restoring in progress"}

    return {"result": f"snapshot {name} restored"}


@router.post('/restore/{type_name}/{name}')
def restore_latest_snapshot(
        name: str,
        type_name: str,
        snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Restore the latest snapshot with given type and name of document"""
    logger.info(
        f"POST request for doc with '{name}'")

    result = snapshot_manager.restore_latest_snapshot(type_name, name)

    return result


@router.post('/{type_name}/{name}')
def create_snapshot(
        type_name: str,
        name: str,
        snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Create a snapshot for the doc with the given type_name and name """
    logger.info(
        f"POST request for snapshot of doc with type_name '{type_name}' and '{name}'"
    )

    snapshot = snapshot_manager.create_snapshot(type_name, name)
    return snapshot


@router.delete('/{name}')
def delete_snapshot(
        name: str,
        snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """
    Delete the latest or optionally the given number most recent snapshot
    of the doc with the given type_name and name
    """
    logger.info(
        f"[DeleteSnapshot DEL] API DEL request for snapshot of doc with name: '{name}'"
    )

    result = snapshot_manager.delete_snapshot(name)
    return result
