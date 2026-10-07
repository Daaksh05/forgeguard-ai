from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from backend.app.dependencies import get_forgeguard_service
from backend.app.schemas import TelemetryResponse
from backend.app.services.forgeguard_service import ForgeGuardService

router = APIRouter()
ServiceDependency = Annotated[ForgeGuardService, Depends(get_forgeguard_service)]


@router.get("/machines/{machine_id}/telemetry", response_model=TelemetryResponse)
def get_telemetry(
    machine_id: str,
    service: ServiceDependency,
    limit: Annotated[int, Query(ge=1, le=500)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> dict:
    try:
        return service.get_telemetry(machine_id, limit, offset)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error
