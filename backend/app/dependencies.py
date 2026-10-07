"""Shared application dependencies."""

from backend.app.services.forgeguard_service import ForgeGuardService

forgeguard_service = ForgeGuardService()


def get_forgeguard_service() -> ForgeGuardService:
    return forgeguard_service
