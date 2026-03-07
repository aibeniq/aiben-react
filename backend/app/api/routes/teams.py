"""
API routes for team management.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import select, func, or_
from typing import Any
import uuid
from datetime import datetime

from app.api.deps import (
    CurrentUser,
    SessionDep,
    CurrentTeam,
    get_team_member_ids,
    get_current_active_superuser,
)
from app.models import (
    Team,
    TeamCreate,
    TeamUpdate,
    TeamPublic,
    TeamDetailPublic,
    TeamsPublic,
    TeamMembership,
    TeamMemberPublic,
    TeamRole,
    User,
    Message,
)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.post("/", response_model=TeamPublic, status_code=status.HTTP_201_CREATED)
def create_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_in: TeamCreate,
) -> Any:
    """
    Create a new team.
    """
    # Check if team name already exists
    existing_team = session.exec(
        select(Team).where(Team.name == team_in.name)
    ).first()
    
    if existing_team:
        raise HTTPException(
            status_code=400,
            detail="A team with this name already exists"
        )
    
    # Create the team
    team = Team(
        id=uuid.uuid4(),
        name=team_in.name,
        description=team_in.description,
        created_by=current_user.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        is_active=True
    )
    session.add(team)
    session.flush()
    
    # Add creator as owner
    membership = TeamMembership(
        id=uuid.uuid4(),
        team_id=team.id,
        user_id=current_user.id,
        role=TeamRole.OWNER,
        joined_at=datetime.utcnow(),
        added_by=current_user.id
    )
    session.add(membership)
    
    # Set as current team if user doesn't have one
    if not current_user.current_team_id:
        current_user.current_team_id = team.id
        session.add(current_user)
    
    session.commit()
    session.refresh(team)
    
    return TeamPublic(
        id=team.id,
        name=team.name,
        description=team.description,
        created_by=team.created_by,
        created_at=team.created_at,
        updated_at=team.updated_at,
        is_active=team.is_active,
        member_count=1,
        current_user_role=TeamRole.OWNER
    )


@router.get("/", response_model=TeamsPublic)
def list_teams(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    List all teams the current user is a member of.
    """
    # Get team IDs where user is a member
    memberships = session.exec(
        select(TeamMembership)
        .where(TeamMembership.user_id == current_user.id)
        .offset(skip)
        .limit(limit)
    ).all()
    
    team_ids = [m.team_id for m in memberships]
    
    # Get teams with member counts
    teams_data = []
    for membership in memberships:
        team = session.get(Team, membership.team_id)
        if team and team.is_active:
            # Count members
            member_count = session.exec(
                select(func.count(TeamMembership.id))
                .where(TeamMembership.team_id == team.id)
            ).one()
            
            teams_data.append(TeamPublic(
                id=team.id,
                name=team.name,
                description=team.description,
                created_by=team.created_by,
                created_at=team.created_at,
                updated_at=team.updated_at,
                is_active=team.is_active,
                member_count=member_count,
                current_user_role=membership.role
            ))
    
    return TeamsPublic(data=teams_data, count=len(teams_data))


@router.get("/{team_id}", response_model=TeamDetailPublic)
def get_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """
    Get team details including members.
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if user is a member
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this team"
        )
    
    # Get all members with user details
    members_data = []
    memberships = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
    ).all()
    
    for member_membership in memberships:
        user = session.get(User, member_membership.user_id)
        if user:
            members_data.append(TeamMemberPublic(
                id=member_membership.id,
                user_id=user.id,
                role=member_membership.role,
                joined_at=member_membership.joined_at,
                full_name=user.full_name,
                email=str(user.email)
            ))
    
    return TeamDetailPublic(
        id=team.id,
        name=team.name,
        description=team.description,
        created_by=team.created_by,
        created_at=team.created_at,
        updated_at=team.updated_at,
        is_active=team.is_active,
        member_count=len(members_data),
        current_user_role=membership.role,
        members=members_data
    )


@router.patch("/{team_id}", response_model=TeamPublic)
def update_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    team_in: TeamUpdate,
) -> Any:
    """
    Update team details (admin or owner only).
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if user has admin or owner role
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership or membership.role not in [TeamRole.ADMIN, TeamRole.OWNER]:
        raise HTTPException(
            status_code=403,
            detail="Only team admins and owners can update team details"
        )
    
    # Check if new name conflicts
    if team_in.name and team_in.name != team.name:
        existing = session.exec(
            select(Team).where(Team.name == team_in.name)
        ).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="A team with this name already exists"
            )
        team.name = team_in.name
    
    if team_in.description is not None:
        team.description = team_in.description
    
    team.updated_at = datetime.utcnow()
    session.add(team)
    session.commit()
    session.refresh(team)
    
    # Get member count
    member_count = session.exec(
        select(func.count(TeamMembership.id))
        .where(TeamMembership.team_id == team.id)
    ).one()
    
    return TeamPublic(
        id=team.id,
        name=team.name,
        description=team.description,
        created_by=team.created_by,
        created_at=team.created_at,
        updated_at=team.updated_at,
        is_active=team.is_active,
        member_count=member_count,
        current_user_role=membership.role
    )


@router.delete("/{team_id}", response_model=Message)
def delete_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """
    Delete a team (owner only). This is a soft delete.
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if user is owner
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership or membership.role != TeamRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="Only team owners can delete the team"
        )
    
    # Soft delete
    team.is_active = False
    team.deleted_at = datetime.utcnow()
    session.add(team)
    
    # Clear current_team_id for all members
    members = session.exec(
        select(User)
        .where(User.current_team_id == team_id)
    ).all()
    
    for member in members:
        member.current_team_id = None
        session.add(member)
    
    session.commit()
    
    return Message(message="Team deleted successfully")


@router.post("/{team_id}/switch", response_model=Message)
def switch_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """
    Switch to a different team context.
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if user is a member
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this team"
        )
    
    # Update current team
    current_user.current_team_id = team_id
    session.add(current_user)
    session.commit()
    
    return Message(message=f"Switched to team: {team.name}")


@router.get("/{team_id}/members", response_model=list[TeamMemberPublic])
def list_team_members(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """
    List all members of a team.
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if user is a member
    user_membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not user_membership:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of this team"
        )
    
    # Get all members
    members_data = []
    memberships = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
    ).all()
    
    for membership in memberships:
        user = session.get(User, membership.user_id)
        if user:
            members_data.append(TeamMemberPublic(
                id=membership.id,
                user_id=user.id,
                role=membership.role,
                joined_at=membership.joined_at,
                full_name=user.full_name,
                email=str(user.email)
            ))
    
    return members_data


@router.post("/{team_id}/members", response_model=TeamMemberPublic, status_code=status.HTTP_201_CREATED)
def add_team_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    user_email: str,
    role: TeamRole = TeamRole.MEMBER,
) -> Any:
    """
    Add a member to the team (admin or owner only).
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if current user has admin or owner role
    current_membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not current_membership or current_membership.role not in [TeamRole.ADMIN, TeamRole.OWNER]:
        raise HTTPException(
            status_code=403,
            detail="Only team admins and owners can add members"
        )
    
    # Only owners can add other owners
    if role == TeamRole.OWNER and current_membership.role != TeamRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="Only team owners can add other owners"
        )
    
    # Find user by email
    user = session.exec(
        select(User).where(User.email == user_email)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if already a member
    existing = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == user.id)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User is already a member of this team"
        )
    
    # Add member
    membership = TeamMembership(
        id=uuid.uuid4(),
        team_id=team_id,
        user_id=user.id,
        role=role,
        joined_at=datetime.utcnow(),
        added_by=current_user.id
    )
    session.add(membership)
    
    # Set as current team if user doesn't have one
    if not user.current_team_id:
        user.current_team_id = team_id
        session.add(user)
    
    session.commit()
    session.refresh(membership)
    
    return TeamMemberPublic(
        id=membership.id,
        user_id=user.id,
        role=membership.role,
        joined_at=membership.joined_at,
        full_name=user.full_name,
        email=str(user.email)
    )


@router.patch("/{team_id}/members/{user_id}", response_model=TeamMemberPublic)
def update_member_role(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
    new_role: TeamRole,
) -> Any:
    """
    Update a team member's role (owner only).
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check if current user is owner
    current_membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not current_membership or current_membership.role != TeamRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="Only team owners can change member roles"
        )
    
    # Get target membership
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == user_id)
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this team"
        )
    
    # Can't change own role
    if user_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot change your own role"
        )
    
    membership.role = new_role
    session.add(membership)
    session.commit()
    session.refresh(membership)
    
    user = session.get(User, user_id)
    
    return TeamMemberPublic(
        id=membership.id,
        user_id=user_id,
        role=membership.role,
        joined_at=membership.joined_at,
        full_name=user.full_name if user else None,
        email=str(user.email) if user else None
    )


@router.delete("/{team_id}/members/{user_id}", response_model=Message)
def remove_team_member(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
    user_id: uuid.UUID,
) -> Any:
    """
    Remove a member from the team (admin or owner only).
    Owners cannot be removed by admins.
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Check current user's role
    current_membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not current_membership or current_membership.role not in [TeamRole.ADMIN, TeamRole.OWNER]:
        raise HTTPException(
            status_code=403,
            detail="Only team admins and owners can remove members"
        )
    
    # Get target membership
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == user_id)
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail="User is not a member of this team"
        )
    
    # Admins can't remove owners
    if current_membership.role == TeamRole.ADMIN and membership.role == TeamRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="Admins cannot remove team owners"
        )
    
    # Check if this is the last owner
    if membership.role == TeamRole.OWNER:
        owner_count = session.exec(
            select(func.count(TeamMembership.id))
            .where(TeamMembership.team_id == team_id)
            .where(TeamMembership.role == TeamRole.OWNER)
        ).one()
        
        if owner_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot remove the last owner. Transfer ownership first or delete the team."
            )
    
    # Remove membership
    session.delete(membership)
    
    # Clear current_team_id if this was their current team
    user = session.get(User, user_id)
    if user and user.current_team_id == team_id:
        user.current_team_id = None
        session.add(user)
    
    session.commit()
    
    return Message(message="Member removed successfully")


@router.post("/{team_id}/leave", response_model=Message)
def leave_team(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    team_id: uuid.UUID,
) -> Any:
    """
    Leave a team. Owners must transfer ownership first.
    """
    team = session.get(Team, team_id)
    if not team or not team.is_active:
        raise HTTPException(
            status_code=404,
            detail="Team not found"
        )
    
    # Get user's membership
    membership = session.exec(
        select(TeamMembership)
        .where(TeamMembership.team_id == team_id)
        .where(TeamMembership.user_id == current_user.id)
    ).first()
    
    if not membership:
        raise HTTPException(
            status_code=404,
            detail="You are not a member of this team"
        )
    
    # Owners can't leave if they're the last owner
    if membership.role == TeamRole.OWNER:
        owner_count = session.exec(
            select(func.count(TeamMembership.id))
            .where(TeamMembership.team_id == team_id)
            .where(TeamMembership.role == TeamRole.OWNER)
        ).one()
        
        if owner_count <= 1:
            raise HTTPException(
                status_code=400,
                detail="Cannot leave as the last owner. Transfer ownership first or delete the team."
            )
    
    # Remove membership
    session.delete(membership)
    
    # Clear current_team_id if this was their current team
    if current_user.current_team_id == team_id:
        current_user.current_team_id = None
        session.add(current_user)
    
    session.commit()
    
    return Message(message="You have left the team")
