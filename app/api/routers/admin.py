from fastapi import APIRouter, Depends

from app.api.deps import RequiresPermission
from app.core import permissions as perms

router = APIRouter()


@router.get(
    "/system-status",
    dependencies=[Depends(RequiresPermission(perms.REPORTS_VIEW))],
)
async def get_system_status():
    """
    Get system status. A placeholder for admin reports.
    """
    return {"status": "ok", "message": "System is running"}
