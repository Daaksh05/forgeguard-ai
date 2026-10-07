from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_forgeguard_service
from backend.app.schemas import ApprovalRequest, ApprovalResponse
from backend.app.services.forgeguard_service import ForgeGuardService

router = APIRouter()
ServiceDependency = Annotated[ForgeGuardService, Depends(get_forgeguard_service)]


@router.post("/approval", response_model=ApprovalResponse)
def record_approval(
    request: ApprovalRequest,
    service: ServiceDependency,
) -> dict:
    try:
        return service.record_approval(request.model_dump())
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error
