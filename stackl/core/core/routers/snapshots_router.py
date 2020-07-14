from typing import List

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from stackl.enums.stackl_codes import StatusCode
from stackl.models.history.snapshot_model import Snapshot
from stackl.tasks.snapshot_task import SnapshotTask

from core.manager.snapshot_manager import SnapshotManager
from core.manager.stackl_manager import get_snapshot_manager

router = APIRouter()


@router.get('/{name}', response_model=Snapshot)
def get_snapshot(
    name: str,
    snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    logger.info(
        f"[GetSnapSHOT GET] API GET request for snapshot of doc with '{name}'")
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
        f"[GetSnapSHOT GET] API GET request for snapshot of doc with type '{type_name}' and '{name}'"
    )

    snapshots = snapshot_manager.get_snapshots(type_name, name)

    return snapshots


@router.post('/restore/{name}')
def restore_snapshot(
    name: str,
    snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Restore the latest or optionally the given number most recent snapshot of the doc with the given type_name and name """
    logger.info(
        f"[RestoreSnapshot POST] API POST request for doc with '{name}'")

    result = snapshot_manager.restore_snapshot(name)

    return result


@router.post('/restore/{type_name}/{name}')
def restore_latest_snapshot(
    name: str,
    type_name: str,
    snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Restore the latest snapshot with given type and name of document"""
    logger.info(
        f"[RestoreSnapshot POST] API POST request for doc with '{name}'")

    result = snapshot_manager.restore_latest_snapshot(type_name, name)

    return result


@router.post('/{type_name}/{name}')
def create_snapshot(
    type_name: str,
    name: str,
    snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Create a snapshot for the doc with the given type_name and name """
    logger.info(
        f"[CreateSnapshot POST] API POST request for snapshot of doc with type_name '{type_name}' and '{name}'"
    )

    snapshot = snapshot_manager.create_snapshot(type_name, name)
    return snapshot


@router.delete('/{name}')
def delete_snapshot(
    name: str,
    snapshot_manager: SnapshotManager = Depends(get_snapshot_manager)):
    """Delete the latest or optionally the given number most recent snapshot of the doc with the given type_name and name """
    logger.info(
        f"[DeleteSnapshot DEL] API DEL request for snapshot of doc with name: '{name}'"
    )

    result = snapshot_manager.delete_snapshot(name)
    return result
