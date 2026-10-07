from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from backend.app.dependencies import get_forgeguard_service
from backend.app.schemas import Machine
from backend.app.services.forgeguard_service import ForgeGuardService

router = APIRouter()
ServiceDependency = Annotated[ForgeGuardService, Depends(get_forgeguard_service)]


@router.get("/machines", response_model=list[Machine])
def list_machines(service: ServiceDependency) -> list[dict[str, str]]:
    return service.list_machines()


@router.get("/machines/{machine_id}", response_model=Machine)
def get_machine(machine_id: str, service: ServiceDependency) -> dict:
    try:
        return service.get_machine(machine_id)
    except KeyError as error:
        raise HTTPException(status_code=404, detail="Unknown machine") from error
