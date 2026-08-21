from fastapi import APIRouter, HTTPException, status
from ..models.action import ActionPayload, ActionExecutionRequest, ActionExecutionResult
from ..core.executor import executor
from ..core.killswitch import kill_switch

router = APIRouter(prefix="/execute", tags=["Execution"])

@router.post("", response_model=ActionExecutionResult)
async def execute_action(request: ActionExecutionRequest):
    """
    Executes a single allow-listed action with pre-execution logging and killswitch enforcement.
    """
    if kill_switch.is_active and not request.override_killswitch:
        result = executor.execute(request.action, override_killswitch=False)
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail={
                "message": "Execution rejected: CAIOS emergency kill switch is active.",
                "action_type": request.action.action_type,
                "title": request.action.title
            }
        )

    result = executor.execute(request.action, override_killswitch=request.override_killswitch)
    if not result.success and result.details and result.details.get("blocked_by_killswitch"):
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=result.message
        )
        
    return result
