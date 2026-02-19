from fastapi import Depends, HTTPException, status
from typing import Callable

from ..dependencies.auth import get_current_user
from .role_matrix import ROLE_ACTION_MATRIX, Action


def require_action(action: Action) -> Callable:
    """
    Dependency factory for enforcing role-based action permissions.
    """

    def permission_checker(current_user: dict = Depends(get_current_user)):
        role = current_user.get("role")

        allowed_actions = ROLE_ACTION_MATRIX.get(role, [])

        if action not in allowed_actions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{role}' not allowed to perform '{action.value}'"
            )

        return current_user

    return permission_checker
