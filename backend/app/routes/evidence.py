from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_forgeguard_service
from backend.app.schemas import (
    AnomalyResponse,
    MaintenanceEvidenceResponse,
    VisualEvidenceResponse,
)
from backend.app.services.forgeguard_service import ForgeGuardService

router = APIRouter()
ServiceDependency = Annotated[ForgeGuardService, Depends(get_forgeguard_service)]


@router.get("/machines/{machine_id}/anomalies", response_model=AnomalyResponse)
def get_anomalies(machine_id: str, service: ServiceDependency) -> dict:
    try:
        return service.get_anomalies(machine_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error


@router.get(
    "/machines/{machine_id}/visual-evidence",
    response_model=VisualEvidenceResponse,
)
def get_visual_evidence(machine_id: str, service: ServiceDependency) -> dict:
    try:
        return service.get_visual_evidence(machine_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error


@router.get(
    "/machines/{machine_id}/maintenance",
    response_model=MaintenanceEvidenceResponse,
)
def get_maintenance_evidence(machine_id: str, service: ServiceDependency) -> dict:
    try:
        return service.get_maintenance_evidence(machine_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error
