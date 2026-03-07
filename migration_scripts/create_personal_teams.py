#!/usr/bin/env python3
"""
Data migration script to create personal teams for existing users.

This script should be run after the schema migration (add_team_models.py) has been applied.
It creates a personal team for each existing user and sets them as the owner.

Usage:
    python migration_scripts/create_personal_teams.py
"""

import sys
import os
from pathlib import Path

# Add the backend directory to the path so we can import app modules
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

from datetime import datetime
import uuid
from sqlmodel import Session, select

from app.core.db import engine
from app.models import User, Team, TeamMembership, TeamRole


def create_personal_teams():
    """Create personal teams for all users who don't have one."""
    
    with Session(engine) as session:
        # Get all users
        users = session.exec(select(User)).all()
        
        created_count = 0
        updated_count = 0
        error_count = 0
        
        print(f"Found {len(users)} users")
        print("=" * 60)
        
        for user in users:
            try:
                # Check if user already has a team membership
                existing_membership = session.exec(
                    select(TeamMembership)
                    .where(TeamMembership.user_id == user.id)
                ).first()
                
                if existing_membership:
                    print(f"✓ User {user.email} already has team membership")
                    # Make sure they have a current_team_id set
                    if not user.current_team_id:
                        user.current_team_id = existing_membership.team_id
                        session.add(user)
                        updated_count += 1
                        print(f"  → Set current_team_id for {user.email}")
                    continue
                
                # Create a personal team for the user
                team_name = f"{user.full_name}'s Team" if user.full_name else f"{user.email}'s Team"
                
                # Check if team name already exists and make it unique
                base_name = team_name
                counter = 1
                while session.exec(select(Team).where(Team.name == team_name)).first():
                    team_name = f"{base_name} ({counter})"
                    counter += 1
                
                team = Team(
                    id=uuid.uuid4(),
                    name=team_name,
                    description=f"Personal team for {user.full_name or user.email}",
                    created_by=user.id,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    is_active=True
                )
                session.add(team)
                session.flush()  # Get the team ID
                
                # Create team membership with OWNER role
                membership = TeamMembership(
                    id=uuid.uuid4(),
                    team_id=team.id,
                    user_id=user.id,
                    role=TeamRole.OWNER,
                    joined_at=datetime.utcnow(),
                    added_by=user.id  # Self-added
                )
                session.add(membership)
                
                # Set as current team
                user.current_team_id = team.id
                session.add(user)
                
                session.commit()
                
                created_count += 1
                print(f"✓ Created personal team for {user.email}: '{team.name}'")
                
            except Exception as e:
                session.rollback()
                error_count += 1
                print(f"✗ Error creating team for {user.email}: {str(e)}")
                continue
        
        print("=" * 60)
        print(f"\nMigration Summary:")
        print(f"  Teams created: {created_count}")
        print(f"  Users updated: {updated_count}")
        print(f"  Errors: {error_count}")
        print(f"  Total users processed: {len(users)}")
        
        if error_count == 0:
            print("\n✓ Migration completed successfully!")
            return 0
        else:
            print(f"\n⚠ Migration completed with {error_count} errors")
            return 1


def verify_migration():
    """Verify that all users have teams."""
    
    with Session(engine) as session:
        users_without_teams = session.exec(
            select(User)
            .where(User.current_team_id == None)
        ).all()
        
        if users_without_teams:
            print(f"\n⚠ Warning: {len(users_without_teams)} users without teams:")
            for user in users_without_teams:
                print(f"  - {user.email}")
            return False
        else:
            print("\n✓ All users have teams assigned")
            return True


if __name__ == "__main__":
    print("Starting personal team migration...")
    print("=" * 60)
    
    try:
        exit_code = create_personal_teams()
        
        print("\nVerifying migration...")
        print("=" * 60)
        verify_migration()
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n✗ Fatal error during migration: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
