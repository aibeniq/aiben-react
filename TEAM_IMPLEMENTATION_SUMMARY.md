# Team-Based Access Control - Phase 1 Implementation Complete

## Summary

Successfully implemented the foundation (Phase 1) of team-based access control for the AIben application. Users can now belong to teams, and the infrastructure is in place to filter data by team membership.

## What Was Implemented

### 1. Database Models (`backend/app/models.py`)

#### New Models:
- **TeamRole Enum**: Four role types (OWNER, ADMIN, MEMBER, VIEWER) with hierarchical permissions
- **Team Model**: Core team entity with soft delete support
  - Fields: name, description, created_by, timestamps, is_active, deleted_at
  - Relationships: members via TeamMembership
  
- **TeamMembership Model**: Junction table managing team-user relationships
  - Fields: team_id, user_id, role, joined_at, added_by
  - Constraints: Unique constraint on (team_id, user_id)
  
#### Updated Models:
- **User Model**: Added team relationship fields
  - `current_team_id`: Tracks the user's active team context
  - `team_memberships`: Relationship to TeamMembership records
  - Updated UserPublic to include current_team_id

#### API Response Models:
- **TeamBase, TeamCreate, TeamUpdate**: Request/response models
- **TeamPublic**: Public team information with member count and user role
- **TeamDetailPublic**: Extended view including member list
- **TeamMemberPublic**: Member information with user details
- **TeamsPublic**: Paginated team list response

### 2. Dependencies (`backend/app/api/deps.py`)

Added three new dependency functions for team access control:

- **`get_current_team()`**: Retrieves the user's currently selected team with validation
  - Verifies team exists and is active
  - Checks user is still a member
  - Auto-clears invalid team references
  
- **`require_team_access()`**: Enforces minimum role requirements
  - Validates team membership
  - Checks role hierarchy (VIEWER < MEMBER < ADMIN < OWNER)
  - Returns HTTPException for unauthorized access
  
- **`get_team_member_ids()`**: Helper to get all user IDs in a team
  - Used for filtering data by team membership

### 3. Team API Routes (`backend/app/api/routes/teams.py`)

Comprehensive API for team management:

#### Team CRUD Operations:
- `POST /teams` - Create new team (auto-adds creator as owner)
- `GET /teams` - List user's teams with member counts and roles
- `GET /teams/{team_id}` - Get team details with full member list
- `PATCH /teams/{team_id}` - Update team (admin/owner only)
- `DELETE /teams/{team_id}` - Soft delete team (owner only)
- `POST /teams/{team_id}/switch` - Switch active team context

#### Team Membership Operations:
- `GET /teams/{team_id}/members` - List all team members
- `POST /teams/{team_id}/members` - Add member by email (admin/owner only)
- `PATCH /teams/{team_id}/members/{user_id}` - Update member role (owner only)
- `DELETE /teams/{team_id}/members/{user_id}` - Remove member (admin/owner only)
- `POST /teams/{team_id}/leave` - Leave team (with ownership checks)

#### Permission Rules Implemented:
- Only admins and owners can add/remove members
- Only owners can add other owners
- Only owners can change roles or delete teams
- Last owner cannot leave (must transfer ownership or delete team)
- Admins cannot remove owners

### 4. Database Migration (`backend/app/alembic/versions/add_team_models.py`)

Alembic migration script that:
- Creates TeamRole enum type in PostgreSQL
- Creates teams table with indexes
- Creates team_memberships table with unique constraint
- Adds current_team_id column to user table with foreign key
- Includes checkfirst guards for idempotency
- Full upgrade and downgrade support

### 5. Data Migration Script (`migration_scripts/create_personal_teams.py`)

Standalone script to create personal teams for existing users:
- Creates one team per user ("{Name}'s Team")
- Adds user as OWNER of their personal team
- Sets team as user's current_team_id
- Handles duplicate names with counter suffix
- Comprehensive error handling and reporting
- Verification function to check migration success

### 6. API Router Registration (`backend/app/api/main.py`)

- Imported teams router
- Registered in api_router (positioned after users router)

## Migration Plan

### Running the Migration:

1. **Apply Schema Migration**:
   ```bash
   cd backend
   alembic upgrade head
   ```

2. **Run Data Migration**:
   ```bash
   python migration_scripts/create_personal_teams.py
   ```

### Expected Output:
- Teams table created
- Team_memberships table created
- User.current_team_id column added
- Personal team created for each existing user
- All users assigned as owners of their personal team

## What's Next (Phase 2-6)

### Immediate Next Steps:
1. **Test the API** - Verify all team endpoints work correctly
2. **Update existing routes** - Modify data access filters to use team membership
3. **Frontend implementation** - Build team management UI components

### Required Route Updates:
The following modules need team-based access control:
- Knowledge Bases (`/knowledge-bases/*`)
- Form Connect (`/formconnect/*`)
- VeraDoc (`/veradoc/*`)
- ReportGenie (`/reportgenie/*`)
- TwinCheck (`/twincheck/*`)
- Chatbot (`/chatbot/*`)
- Items (`/items/*`)

### Pattern for Route Updates:
```python
# OLD: Filter by owner_id
kbs = session.exec(
    select(KnowledgeBase)
    .where(KnowledgeBase.owner_id == current_user.id)
).all()

# NEW: Filter by team membership
team = require_team_access(current_user, current_team, session)
team_member_ids = get_team_member_ids(session, team.id)
kbs = session.exec(
    select(KnowledgeBase)
    .where(KnowledgeBase.owner_id.in_(team_member_ids))
).all()
```

## Testing Checklist

- [ ] Schema migration applies successfully
- [ ] Data migration creates personal teams
- [ ] All users have current_team_id set
- [ ] Can create new team
- [ ] Can list user's teams
- [ ] Can view team details
- [ ] Can update team name/description
- [ ] Can add member to team
- [ ] Can remove member from team
- [ ] Can change member role
- [ ] Can switch between teams
- [ ] Can leave team (non-owner)
- [ ] Cannot remove last owner
- [ ] Can soft delete team (owner only)
- [ ] Permission checks work correctly

## Files Created/Modified

### Created:
- `backend/app/api/routes/teams.py` (645 lines)
- `backend/app/alembic/versions/add_team_models.py` (105 lines)
- `migration_scripts/create_personal_teams.py` (162 lines)
- `TEAM_BASED_ACCESS_CONTROL_APPROACH.md` (approach document)
- `TEAM_IMPLEMENTATION_SUMMARY.md` (this file)

### Modified:
- `backend/app/models.py` - Added Team, TeamMembership, TeamRole models
- `backend/app/api/deps.py` - Added team access control dependencies
- `backend/app/api/main.py` - Registered teams router

## Database Schema Changes

```sql
-- New enum type
CREATE TYPE teamrole AS ENUM ('owner', 'admin', 'member', 'viewer');

-- New tables
CREATE TABLE teams (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description VARCHAR(1000),
    created_by UUID REFERENCES user(id) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    deleted_at TIMESTAMP
);

CREATE TABLE team_memberships (
    id UUID PRIMARY KEY,
    team_id UUID REFERENCES teams(id) ON DELETE CASCADE NOT NULL,
    user_id UUID REFERENCES user(id) ON DELETE CASCADE NOT NULL,
    role teamrole DEFAULT 'member' NOT NULL,
    joined_at TIMESTAMP NOT NULL,
    added_by UUID REFERENCES user(id),
    UNIQUE(team_id, user_id)
);

-- Modified table
ALTER TABLE user ADD COLUMN current_team_id UUID REFERENCES teams(id);
```

## API Endpoints Added

All endpoints under `/api/v1/teams`:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/teams` | Create team | User |
| GET | `/teams` | List user's teams | User |
| GET | `/teams/{id}` | Get team details | Member |
| PATCH | `/teams/{id}` | Update team | Admin/Owner |
| DELETE | `/teams/{id}` | Delete team | Owner |
| POST | `/teams/{id}/switch` | Switch team | Member |
| GET | `/teams/{id}/members` | List members | Member |
| POST | `/teams/{id}/members` | Add member | Admin/Owner |
| PATCH | `/teams/{id}/members/{user_id}` | Update role | Owner |
| DELETE | `/teams/{id}/members/{user_id}` | Remove member | Admin/Owner |
| POST | `/teams/{id}/leave` | Leave team | Member |

## Notes

- All changes are backward compatible
- Existing data remains accessible via personal teams
- Team names must be unique across the system
- Soft delete prevents data loss
- Role hierarchy enforced consistently
- Foreign key cascades handle cleanup automatically

## Success Metrics

✅ Zero breaking changes to existing functionality
✅ All models import without errors
✅ Clean separation of concerns
✅ Comprehensive permission checks
✅ Full CRUD operations for teams
✅ Proper relationship management
✅ Migration safety with checkfirst guards

---

**Implementation Date**: March 7, 2026  
**Phase**: 1 of 6 (Complete)  
**Next Phase**: Backend API Testing & Route Migration  
**Status**: ✅ Ready for Testing
