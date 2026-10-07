from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_forgeguard_service
from backend.app.schemas import AssessmentRequest, AssessmentResponse
from backend.app.services.forgeguard_service import ForgeGuardService

router = APIRouter()
ServiceDependency = Annotated[ForgeGuardService, Depends(get_forgeguard_service)]


@router.post("/assessment", response_model=AssessmentResponse)
def create_assessment(
    request: AssessmentRequest,
    service: ServiceDependency,
) -> dict:
    try:
        return service.create_assessment(request.machine_id, request.notes)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error


@router.get("/assessment/{machine_id}", response_model=AssessmentResponse)
def get_assessment(machine_id: str, service: ServiceDependency) -> dict:
    try:
        return service.get_assessment(machine_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error
    except LookupError as error:
        raise HTTPException(
            status_code=404,
            detail="No assessment has been generated for this machine",
        ) from error
