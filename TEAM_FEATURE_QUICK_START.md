# Team Feature Quick Start Guide

## Overview

The team-based access control feature allows users to collaborate by sharing data within teams. This guide covers how to test and use the new functionality.

## Prerequisites

- Backend running with database access
- Alembic migrations up to date
- User account(s) for testing

## Installation & Setup

### 1. Apply Database Migration

```bash
cd backend
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade ... -> a3b4c5d6e7f8, Add team models and team membership
```

### 2. Run Data Migration (for existing users)

```bash
cd /home/ec2-user/aiben-react
python3 migration_scripts/create_personal_teams.py
```

This will:
- Create a personal team for each existing user
- Set each user as OWNER of their personal team
- Set the personal team as the user's current team

Expected output:
```
✓ Created personal team for user1@example.com: 'John Doe's Team'
✓ Created personal team for user2@example.com: 'Jane Smith's Team'
...
Migration Summary:
  Teams created: 2
  Users updated: 0
  Errors: 0
```

## API Testing

### Authentication
All team endpoints require authentication. Include your JWT token in requests:
```bash
TOKEN="your-jwt-token"
```

### 1. List Your Teams

```bash
curl -X GET "http://localhost:8000/api/v1/teams" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "John Doe's Team",
      "description": "Personal team for John Doe",
      "created_by": "user-uuid",
      "created_at": "2026-03-07T10:00:00",
      "updated_at": "2026-03-07T10:00:00",
      "is_active": true,
      "member_count": 1,
      "current_user_role": "owner"
    }
  ],
  "count": 1
}
```

### 2. Create a New Team

```bash
curl -X POST "http://localhost:8000/api/v1/teams" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Engineering Team",
    "description": "Team for engineering collaboration"
  }'
```

### 3. Get Team Details

```bash
curl -X GET "http://localhost:8000/api/v1/teams/{team_id}" \
  -H "Authorization: Bearer $TOKEN"
```

Response includes members:
```json
{
  "id": "team-uuid",
  "name": "Engineering Team",
  "description": "Team for engineering collaboration",
  "member_count": 2,
  "current_user_role": "owner",
  "members": [
    {
      "id": "membership-uuid",
      "user_id": "user-uuid",
      "role": "owner",
      "joined_at": "2026-03-07T10:00:00",
      "full_name": "John Doe",
      "email": "john@example.com"
    }
  ]
}
```

### 4. Add a Team Member

```bash
curl -X POST "http://localhost:8000/api/v1/teams/{team_id}/members?user_email=jane@example.com&role=member" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Update Member Role

```bash
curl -X PATCH "http://localhost:8000/api/v1/teams/{team_id}/members/{user_id}?new_role=admin" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Switch Team Context

```bash
curl -X POST "http://localhost:8000/api/v1/teams/{team_id}/switch" \
  -H "Authorization: Bearer $TOKEN"
```

### 7. Leave a Team

```bash
curl -X POST "http://localhost:8000/api/v1/teams/{team_id}/leave" \
  -H "Authorization: Bearer $TOKEN"
```

### 8. Remove a Member

```bash
curl -X DELETE "http://localhost:8000/api/v1/teams/{team_id}/members/{user_id}" \
  -H "Authorization: Bearer $TOKEN"
```

### 9. Delete a Team

```bash
curl -X DELETE "http://localhost:8000/api/v1/teams/{team_id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Testing Scenarios

### Scenario 1: Create Team and Collaborate

1. User A creates a team
2. User A invites User B (as member)
3. User A creates a knowledge base
4. User B switches to the team
5. User B should see User A's knowledge base (once Phase 4 is complete)

### Scenario 2: Team Roles and Permissions

1. Owner creates team with Member
2. Member tries to add another member → Should fail (403)
3. Owner promotes Member to Admin
4. Admin adds new member → Should succeed
5. Admin tries to remove Owner → Should fail (403)
6. Owner changes Admin back to Member → Should succeed

### Scenario 3: Leave Team

1. Create team with 2 owners
2. One owner leaves → Should succeed
3. Last owner tries to leave → Should fail (must transfer ownership or delete team)

### Scenario 4: Team Deletion

1. Owner deletes team (soft delete)
2. All members' current_team_id cleared
3. Team no longer appears in lists
4. Team data preserved in database (is_active=false)

## Database Verification

### Check Teams Table

```sql
SELECT id, name, created_by, is_active, member_count 
FROM teams;
```

### Check Team Memberships

```sql
SELECT tm.id, t.name as team, u.email as user, tm.role 
FROM team_memberships tm
JOIN teams t ON tm.team_id = t.id
JOIN "user" u ON tm.user_id = u.id;
```

### Check User's Current Team

```sql
SELECT u.email, u.current_team_id, t.name as current_team
FROM "user" u
LEFT JOIN teams t ON u.current_team_id = t.id;
```

## Common Issues & Solutions

### Issue: Migration fails with "relation already exists"

**Solution**: The migration uses `checkfirst=True`, so this shouldn't happen. If it does:
```bash
# Check which tables exist
psql -d your_db -c "\dt"

# If teams tables exist but migration incomplete, manually run specific parts
```

### Issue: User has no current_team_id after migration

**Solution**: Run the data migration script again:
```bash
python3 migration_scripts/create_personal_teams.py
```

### Issue: Cannot add member - "User not found"

**Solution**: User must exist in the system before they can be added to a team. Check:
```sql
SELECT email FROM "user" WHERE email = 'target@example.com';
```

### Issue: Permission denied errors

**Solution**: Verify the user's role in the team:
```bash
curl -X GET "http://localhost:8000/api/v1/teams/{team_id}" \
  -H "Authorization: Bearer $TOKEN"
```

Check `current_user_role` in the response.

## Role Permission Matrix

| Action | VIEWER | MEMBER | ADMIN | OWNER |
|--------|--------|--------|-------|-------|
| View team data | ✅ | ✅ | ✅ | ✅ |
| Create data | ❌ | ✅ | ✅ | ✅ |
| Update own data | ❌ | ✅ | ✅ | ✅ |
| Delete own data | ❌ | ✅ | ✅ | ✅ |
| View team details | ✅ | ✅ | ✅ | ✅ |
| Add members | ❌ | ❌ | ✅ | ✅ |
| Remove members | ❌ | ❌ | ✅¹ | ✅ |
| Update member roles | ❌ | ❌ | ❌ | ✅ |
| Update team details | ❌ | ❌ | ✅ | ✅ |
| Delete team | ❌ | ❌ | ❌ | ✅ |
| Leave team | ✅ | ✅ | ✅ | ✅² |

¹ Admins cannot remove Owners  
² Last Owner cannot leave (must transfer ownership or delete team)

## Next Steps

After verifying that team management works correctly:

1. **Phase 2**: Update knowledge base routes to use team-based filtering
2. **Phase 3**: Update other data routes (FormConnect, VeraDoc, etc.)
3. **Phase 4**: Build frontend team management UI
4. **Phase 5**: Add team switching in frontend navbar
5. **Phase 6**: Update all data listing pages to show team data

## Support

For issues or questions:
1. Check the implementation documents
2. Review error logs in the backend
3. Verify database state using SQL queries above
4. Check the git commit history for changes

---

**Quick Start Version**: 1.0  
**Last Updated**: March 7, 2026  
**Compatible With**: Phase 1 Implementation
