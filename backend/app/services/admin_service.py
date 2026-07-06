class AdminService:
    """Placeholder for admin validation, apply, change log, and rollback logic."""

    async def preview_change(self, target_type: str, before: dict, after: dict) -> dict:
        return {
            "targetType": target_type,
            "before": before,
            "after": after,
            "warnings": [],
            "allowed": True,
        }
