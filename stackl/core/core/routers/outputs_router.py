"""
Endpoint used mainly by the automation handler for adding extra key-value pairs
to an instance
"""

from fastapi import APIRouter, Depends

from core.manager.document_manager import DocumentManager
from core.manager.stack_manager import StackManager, OutputsUpdate
from core.manager.stackl_manager import get_document_manager, get_stack_manager
from core.models.items.stack_instance_model import StackInstance

router = APIRouter()


@router.post('', response_model=StackInstance)
def add_outputs(
        outputs_update: OutputsUpdate,
        document_manager: DocumentManager = Depends(get_document_manager),
        stack_manager: StackManager = Depends(get_stack_manager)):
    """
    Function used to add outputs to a stack instance
    Returns the updated stack_instance
    """
    stack_instance = stack_manager.add_outputs(outputs_update)
    document_manager.write_stack_instance(stack_instance)
    return stack_instance
