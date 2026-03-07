from collections.abc import Generator
from typing import Annotated
import uuid

import jwt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import TokenPayload, User, Team, TeamMembership, TeamRole

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    auto_error=False,  # Don't auto-error, we'll handle cookies
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_token_from_cookie_or_header(
    request: Request, token: str = Depends(reusable_oauth2)
) -> str:
    """
    Get token from HTTP-only cookie first, fallback to Authorization header for backward compatibility
    """
    # Try to get token from HTTP-only cookie first
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        return cookie_token

    # Fallback to Authorization header (for API clients or during migration)
    if token:
        return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )


TokenDep = Annotated[str, Depends(get_token_from_cookie_or_header)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


# Team-related dependencies
def get_current_team(
    current_user: CurrentUser,
    session: SessionDep
) -> Team | None:
    """Get the user's currently selected team."""
    if not current_user.current_team_id:
        return None
    
    team = session.get(Team, current_user.current_team_id)
    if not team or not team.is_active:
        # Team was deleted or deactivated, clear current_team_id
        current_user.current_team_id = None
        session.add(current_user)
        session.commit()
        return None
    
    # Verify user is still a member
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team.id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership:
        # User no longer in team, clear current_team_id
        current_user.current_team_id = None
        session.add(current_user)
        session.commit()
        return None
    
    return team


CurrentTeam = Annotated[Team | None, Depends(get_current_team)]


def require_team_access(
    current_user: CurrentUser,
    team: CurrentTeam,
    session: SessionDep,
    min_role: TeamRole = TeamRole.MEMBER
) -> Team:
    """Ensure user has team access with minimum role."""
    if not team:
        raise HTTPException(
            status_code=400,
            detail="No team selected. Please select a team first."
        )
    
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team.id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this team"
        )
    
    # Check role hierarchy
    role_hierarchy = {
        TeamRole.VIEWER: 0,
        TeamRole.MEMBER: 1,
        TeamRole.ADMIN: 2,
        TeamRole.OWNER: 3
    }
    
    if role_hierarchy[membership.role] < role_hierarchy[min_role]:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Requires {min_role.value} role."
        )
    
    return team


def get_team_member_ids(session: Session, team_id: uuid.UUID) -> list[uuid.UUID]:
    """Get all user IDs in a team."""
    memberships = session.exec(
        select(TeamMembership.user_id)
        .where(TeamMembership.team_id == team_id)
    ).all()
    return list(memberships)
