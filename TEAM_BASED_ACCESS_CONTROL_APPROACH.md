# Team-Based Access Control Implementation Approach

## Executive Summary

This document outlines the approach for implementing team-based access control in the AIben application, where users can belong to teams and only teammates can see each other's data. The implementation will transform the current owner-based access model into a team-based access model while maintaining backward compatibility.

**Current State**: Each user can only see their own data (filtered by `owner_id`)  
**Target State**: Users belong to teams and can see all data created by their teammates

## Architecture Overview

### Technology Stack (Confirmed)
- **Backend**: Python FastAPI + SQLModel/SQLAlchemy
- **Frontend**: React + TypeScript
- **Database**: PostgreSQL with Alembic migrations
- **Authentication**: JWT tokens (OAuth2, HTTP-only cookies)

### Affected Data Models
The following models currently use `owner_id` and will need team-based access control:
- ✓ User
- ✓ KnowledgeBase (documents/knowledge bases)
- ✓ Source (individual documents in knowledge bases)
- ✓ Item (generic items)
- ✓ FormConnectForm (form templates)
- ✓ VeraDocChecklist (document verification checklists)
- ✓ ReportGenieOutline (report outlines)
- ✓ LlmInteraction (chat history and interactions)
- ✓ TwinCheckTopicList (comparison topics)
- ✓ EmbeddingModel (optional owner_id - shared resources)
- ✓ LlmModel (optional owner_id - shared resources)

## Database Schema Design

### 1. New Tables

#### Team Table
```python
class Team(SQLModel, table=True):
    __tablename__ = "teams"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, unique=True, index=True)
    description: str | None = Field(default=None, max_length=1000)
    
    # Team ownership and administration
    created_by: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Soft delete support
    is_active: bool = Field(default=True)
    deleted_at: datetime | None = Field(default=None)
    
    # Relationships
    members: list["TeamMembership"] = Relationship(back_populates="team")
```

#### TeamMembership Table (Junction Table)
```python
class TeamRole(str, enum.Enum):
    OWNER = "owner"        # Can manage team, add/remove members, delete team
    ADMIN = "admin"        # Can add/remove members (except owners)
    MEMBER = "member"      # Can view all team data, create data for team
    VIEWER = "viewer"      # Read-only access to team data

class TeamMembership(SQLModel, table=True):
    __tablename__ = "team_memberships"
    __table_args__ = (
        UniqueConstraint("team_id", "user_id", name="uq_team_user"),
    )
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    team_id: uuid.UUID = Field(foreign_key="teams.id", nullable=False, ondelete="CASCADE")
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    
    role: TeamRole = Field(
        default=TeamRole.MEMBER,
        sa_column=Column(
            SQLAlchemyEnum(
                TeamRole,
                native_enum=True,
                values_callable=lambda x: [e.value for e in x],
                name="teamrole",
            ),
            nullable=False,
        ),
    )
    
    # Audit fields
    joined_at: datetime = Field(default_factory=datetime.utcnow)
    added_by: uuid.UUID | None = Field(default=None, foreign_key="user.id")
    
    # Relationships
    team: Team = Relationship(back_populates="members")
    user: User = Relationship()
```

### 2. Modified User Table
```python
# Add to User model:
    # Default team - the team context user is currently working in
    current_team_id: uuid.UUID | None = Field(
        default=None, 
        foreign_key="teams.id"
    )
    
    # Relationships
    team_memberships: list["TeamMembership"] = Relationship(
        back_populates="user",
        cascade_delete=True
    )
```

### 3. Migration Strategy for Existing Data

**Initial Migration Plan:**
1. **Create new tables**: `teams`, `team_memberships`
2. **For each existing user**: 
   - Create a personal team named "{user.full_name}'s Team" or "{user.email}'s Team"
   - Add user as OWNER of their personal team
   - Set `current_team_id` to their personal team
3. **Keep owner_id fields**: Maintain for backward compatibility
4. **Add team_id fields**: Will be populated in phase 2

**Why this approach?**
- Zero downtime deployment
- Existing data remains accessible
- Users can immediately start creating/joining teams
- Gradual migration of queries from owner_id to team_id

## API Changes

### 1. New API Endpoints

#### Team Management (`/api/v1/teams`)
```python
POST   /teams                          # Create new team
GET    /teams                          # List user's teams
GET    /teams/{team_id}                # Get team details
PATCH  /teams/{team_id}                # Update team (name, description)
DELETE /teams/{team_id}                # Delete team (owner only)
POST   /teams/{team_id}/switch         # Switch current team context

# Team membership management
GET    /teams/{team_id}/members        # List team members
POST   /teams/{team_id}/members        # Add member (admin+)
PATCH  /teams/{team_id}/members/{user_id}  # Update member role (admin+)
DELETE /teams/{team_id}/members/{user_id}  # Remove member (admin+)
POST   /teams/{team_id}/invite         # Invite user by email
POST   /teams/{team_id}/leave          # Leave team (members)
```

### 2. Modified Dependency Injection (deps.py)

```python
# New dependency to get user's current team
def get_current_team(
    current_user: CurrentUser,
    session: SessionDep
) -> Team | None:
    """Get the user's currently selected team"""
    if not current_user.current_team_id:
        return None
    
    team = session.get(Team, current_user.current_team_id)
    if not team:
        # Team was deleted, clear current_team_id
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

# Helper function to check team access
def require_team_access(
    current_user: CurrentUser,
    team: CurrentTeam,
    session: SessionDep,
    min_role: TeamRole = TeamRole.MEMBER
) -> Team:
    """Ensure user has team access with minimum role"""
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
```

### 3. Access Control Modifications

**Current pattern (example from knowledgebases.py):**
```python
# OLD: Filter by owner_id
knowledge_bases = session.exec(
    select(KnowledgeBase)
    .where(KnowledgeBase.owner_id == current_user.id)
).all()
```

**New pattern:**
```python
# NEW: Filter by team membership
def get_team_member_ids(session: Session, team_id: uuid.UUID) -> list[uuid.UUID]:
    """Get all user IDs in a team"""
    memberships = session.exec(
        select(TeamMembership.user_id)
        .where(TeamMembership.team_id == team_id)
    ).all()
    return list(memberships)

# In route handlers:
team = require_team_access(current_user, current_team, session)
team_member_ids = get_team_member_ids(session, team.id)

knowledge_bases = session.exec(
    select(KnowledgeBase)
    .where(KnowledgeBase.owner_id.in_(team_member_ids))
).all()
```

**Optimization with helper function:**
```python
def apply_team_filter(
    query: Select,
    session: Session,
    team_id: uuid.UUID,
    owner_id_column
) -> Select:
    """Apply team-based filter to a query"""
    team_member_ids = get_team_member_ids(session, team_id)
    return query.where(owner_id_column.in_(team_member_ids))

# Usage:
query = select(KnowledgeBase)
query = apply_team_filter(query, session, team.id, KnowledgeBase.owner_id)
knowledge_bases = session.exec(query).all()
```

### 4. Route Updates Required

**All routes that filter by owner_id need updates:**
- `/knowledge-bases/*` - All knowledge base endpoints
- `/sources/*` - Source retrieval endpoints  
- `/formconnect/*` - Form templates and history
- `/veradoc/*` - Checklist management and history
- `/reportgenie/*` - Outline management
- `/chatbot/*` - Chat history (LlmInteraction)
- `/twincheck/*` - Topic lists
- `/items/*` - Generic items
- `/llms/*` - User-specific LLM configurations
- `/embedding-models/*` - User-specific embedding models

**Pattern for each route:**
1. Add `current_team: CurrentTeam` dependency
2. Call `require_team_access()` if team is required
3. Replace `owner_id == current_user.id` with team member filter
4. Maintain owner_id for attribution (who created it)

## Frontend Changes

### 1. Team Context Provider

```typescript
// src/contexts/TeamContext.tsx
interface TeamContextType {
  currentTeam: Team | null;
  teams: Team[];
  switchTeam: (teamId: string) => Promise<void>;
  refreshTeams: () => Promise<void>;
  loading: boolean;
}

export const TeamProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [currentTeam, setCurrentTeam] = useState<Team | null>(null);
  const [teams, setTeams] = useState<Team[]>([]);
  const [loading, setLoading] = useState(true);
  
  // Load teams on mount and after login
  // Implement team switching logic
  // ...
};
```

### 2. UI Components to Add

#### Team Selector (Header/Navbar)
```typescript
// src/components/Team/TeamSelector.tsx
// Dropdown showing current team and allowing switching
// Show team members count
// Quick access to team management
```

#### Team Management Page
```typescript
// src/routes/TeamManagement.tsx
// View/edit team details
// Manage team members (add, remove, change roles)
// View team activity/statistics
// Leave team option
// Delete team (owners only)
```

#### Team Member List Component
```typescript
// src/components/Team/TeamMemberList.tsx
// Display team members with roles
// Member management actions (for admins)
```

#### Team Invitation Component
```typescript
// src/components/Team/InviteModal.tsx
// Invite users by email
// Set initial role for new members
```

### 3. Modified User Context

```typescript
// Add to UserContext:
interface UserContextType {
  user: User | null;
  currentTeam: Team | null;  // ADD
  // ...existing fields
}
```

### 4. UI/UX Considerations

**Team Indicator:**
- Show current team name in header/navbar
- Visual indicator when no team selected
- Warning message for users without teams

**Data Attribution:**
- Show who created each item (maintain owner_id display)
- "Created by John Doe" labels on knowledge bases, forms, etc.

**Team Switching:**
- Smooth team context switching
- Persist last selected team in user preferences
- Reload data after team switch

**Access Control Feedback:**
- Clear error messages for permission issues
- Role indicators (badges) for team members
- Disabled states for actions user can't perform

## Security Considerations

### 1. Authorization Rules

**Team Operations:**
- Create team: Any authenticated user
- View team: Team members only
- Update team: Admins and owners only
- Delete team: Owners only
- Add members: Admins and owners only
- Remove members: Admins and owners only (can't remove owners)
- Change roles: Owners only
- Leave team: Any member (except last owner)

**Data Operations:**
- Create data: Any team member (becomes owner_id)
- View data: Any team member
- Update data: Original creator (owner_id) or team admins
- Delete data: Original creator (owner_id) or team admins

### 2. SQL Injection Prevention
- ✓ Already using SQLModel/SQLAlchemy ORM (parameterized queries)
- ✓ No raw SQL in access control logic
- ✓ Use `.in_()` operator for team member filters

### 3. Data Isolation
- Verify team membership on every request
- No data leakage between teams
- Audit logs for sensitive operations

### 4. Rate Limiting
- Team creation: 5 teams per user max (configurable)
- Member invitations: 10 per hour per team
- Prevent invitation spam

## Migration Plan

### Phase 1: Schema Setup (Week 1)
**Goal**: Add new tables without breaking existing functionality

1. Create Alembic migration for new tables
   - `teams` table
   - `team_memberships` table
   - Add `current_team_id` to `user` table

2. Run data migration script:
   ```python
   # Create personal team for each user
   for user in session.exec(select(User)).all():
       team = Team(
           name=f"{user.full_name or user.email}'s Team",
           created_by=user.id
       )
       session.add(team)
       session.flush()
       
       membership = TeamMembership(
           team_id=team.id,
           user_id=user.id,
           role=TeamRole.OWNER
       )
       session.add(membership)
       
       user.current_team_id = team.id
       session.add(user)
   
   session.commit()
   ```

3. Deploy backend with new tables (no API changes yet)
4. Verify migration success

### Phase 2: Backend API Development (Week 2-3)
**Goal**: Implement team management and access control

1. Implement team CRUD endpoints
2. Implement team membership endpoints
3. Add team context dependencies (`CurrentTeam`, etc.)
4. Create access control helper functions
5. Write comprehensive tests

### Phase 3: Frontend Development (Week 3-4)
**Goal**: Build team management UI

1. Create TeamContext provider
2. Build team selector component
3. Build team management page
4. Build team member management
5. Add team indicators throughout UI
6. Update all data listing pages to show team data

### Phase 4: Route Migration (Week 4-5)
**Goal**: Migrate existing routes to use team-based access

**Strategy**: Migrate one module at a time

1. Knowledge Bases module
2. Form Connect module
3. VeraDoc module
4. ReportGenie module
5. TwinCheck module
6. Chatbot/LLM Interactions
7. Items module

**For each module:**
- Update all GET endpoints (query filters)
- Update all POST/PATCH/DELETE endpoints (ownership checks)
- Add integration tests
- Deploy incrementally
- Monitor for issues

### Phase 5: Testing & Refinement (Week 5-6)
**Goal**: Ensure stability and fix edge cases

1. End-to-end testing
2. Security audit
3. Performance testing (large teams)
4. User acceptance testing
5. Bug fixes and refinements

### Phase 6: Production Rollout (Week 6)
**Goal**: Deploy to production with monitoring

1. Deploy to staging
2. Conduct final QA
3. Prepare rollback plan
4. Deploy to production
5. Monitor logs and metrics
6. Communicate changes to users

## Testing Strategy

### 1. Unit Tests
- Team model validations
- TeamMembership constraints
- Access control helper functions
- Role hierarchy logic

### 2. Integration Tests
```python
def test_team_data_isolation(session, test_users):
    """Ensure users can only see data from their team"""
    user1, user2 = test_users
    
    # User1 creates a knowledge base
    kb1 = KnowledgeBase(owner_id=user1.id, title="Team 1 KB")
    session.add(kb1)
    
    # User2 cannot see it
    result = get_knowledge_bases(session, user2.current_team_id)
    assert kb1.id not in [kb.id for kb in result]
    
    # Add user2 to user1's team
    add_team_member(session, user1.current_team_id, user2.id)
    
    # Now user2 can see it
    result = get_knowledge_bases(session, user2.current_team_id)
    assert kb1.id in [kb.id for kb in result]
```

### 3. API Tests
- Test all team endpoints
- Test permission boundaries
- Test data access across teams
- Test edge cases (no team, deleted team, etc.)

### 4. Frontend Tests
- Team switching functionality
- Permission-based UI rendering
- Error handling for unauthorized actions

### 5. Security Tests
- Attempt to access other team's data
- Attempt unauthorized team operations
- Test SQL injection scenarios
- Test API parameter manipulation

## Rollback Plan

**If critical issues arise:**

1. **Immediate rollback** (< 1 hour):
   - Revert backend deployment
   - Frontend still works with owner_id filters
   - New team features disabled

2. **Data rollback** (not recommended):
   - Team tables can be dropped
   - Remove `current_team_id` from users
   - System returns to single-user mode

3. **Partial rollback** (preferred):
   - Keep team infrastructure
   - Disable team-based filtering temporarily
   - Fix issues and redeploy

## Performance Considerations

### 1. Query Optimization
```python
# AVOID: N+1 query problem
for team in teams:
    members = get_team_members(team.id)  # Bad: N queries

# PREFER: Single query with JOIN
teams_with_members = session.exec(
    select(Team, TeamMembership, User)
    .join(TeamMembership)
    .join(User)
    .where(Team.id.in_(team_ids))
).all()
```

### 2. Caching Strategy
- Cache team member IDs (Redis, 5 min TTL)
- Invalidate on membership changes
- Cache user's team list

### 3. Index Creation
```sql
-- Add indexes for performance
CREATE INDEX idx_team_memberships_user_id ON team_memberships(user_id);
CREATE INDEX idx_team_memberships_team_id ON team_memberships(team_id);
CREATE INDEX idx_users_current_team_id ON users(current_team_id);
```

### 4. Large Team Considerations
- For teams with 100+ members, consider pagination
- Optimize `owner_id.in_(team_member_ids)` queries
- Consider materialized views for very large datasets

## Edge Cases & Considerations

### 1. User Without Team
- Should not happen after migration
- If occurs: Prompt to create/join team
- Fallback: Create personal team automatically

### 2. Last Owner Leaving Team
- Prevent with validation
- Must transfer ownership first
- Or team gets deleted

### 3. Team Deletion
- Soft delete by default
- Hard delete orphans data (need policy)
- Option: Archive team data or transfer to personal teams

### 4. Concurrent Team Switches
- Use optimistic locking
- Refresh on conflict

### 5. Cross-Team Data References
- Knowledge bases can't reference across teams
- Document in API clearly

### 6. Admin Override
- Superusers can view all teams (for support)
- Add audit logging for superuser access

## Documentation Requirements

1. **API Documentation**: Update OpenAPI/Swagger specs
2. **User Guide**: How to create/manage teams
3. **Admin Guide**: Team management best practices
4. **Developer Guide**: How to add team support to new features
5. **Migration Guide**: For existing deployments

## Success Metrics

**Monitor these metrics post-deployment:**
- Team creation rate
- Average team size
- Data access errors (should be near zero)
- API response times (should not degrade)
- User-reported issues

**Success Criteria:**
- ✓ No data leakage between teams
- ✓ All existing features work within team context
- ✓ < 5% increase in API response times
- ✓ Zero critical security issues
- ✓ Positive user feedback

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 1: Schema | 1 week | New tables, data migration |
| Phase 2: Backend API | 2 weeks | Team CRUD, access control |
| Phase 3: Frontend | 2 weeks | Team UI, context management |
| Phase 4: Route Migration | 2 weeks | All routes updated |
| Phase 5: Testing | 1 week | Full test coverage |
| Phase 6: Rollout | 1 week | Production deployment |
| **Total** | **6-8 weeks** | Full team-based access control |

## Next Steps

1. **Review this document** with stakeholders
2. **Approve approach** and timeline
3. **Create detailed tickets** for each phase
4. **Set up development branch**: `feature/team-based-access-control`
5. **Begin Phase 1**: Schema setup and migration

---

**Document Version**: 1.0  
**Created**: 2026-03-07  
**Author**: GitHub Copilot  
**Status**: Pending Review
