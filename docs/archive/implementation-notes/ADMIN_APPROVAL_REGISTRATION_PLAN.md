# Admin Approval Registration System - Implementation Plan

## Overview

This document outlines the implementation plan for converting the current self-service user registration system into an admin-approval system where new account registrations require approval via email confirmation sent to `david@aiben.io`.

## Current Registration Flow

### Frontend (`frontend/src/routes/signup.tsx`)

1. User fills out registration form (full name, email, password)
2. Form submits to `UsersService.registerUser()` API endpoint
3. Upon success, user is redirected to `/login`
4. User can immediately log in

### Backend (`backend/app/api/routes/users.py`)

1. `POST /api/v1/users/signup` endpoint receives registration data
2. Validates email doesn't already exist
3. Creates user account via `crud.create_user()`
4. User account is immediately active (`is_active=True` by default)
5. Returns user data

### Database Model (`backend/app/models.py`)

```python
class User(UserBase, table=True):
    id: uuid.UUID
    email: EmailStr
    hashed_password: str
    is_active: bool = True  # Currently defaults to True
    is_superuser: bool = False
    full_name: str | None
    # ... other fields
```

---

## Proposed Admin Approval System

### High-Level Flow

1. **User Registration Request**

   - User submits registration form
   - Account is created in "pending" state (not active)
   - Registration data is stored temporarily

2. **Admin Notification**

   - Email sent to `david@aiben.io` with:
     - User's registration details (name, email, timestamp)
     - Unique approval link with secure token
     - Decline/reject link (optional)

3. **Admin Action**

   - Admin clicks approval link
   - System validates token and activates account
   - Confirmation email sent to new user
   - User can now log in

4. **User Experience**
   - After registration: "Registration submitted. Awaiting admin approval."
   - After approval: Email with login instructions
   - Login attempt before approval: "Account pending approval"

---

## Implementation Components

### 1. Database Schema Changes

#### Option A: Add Status Field to User Model

```python
class UserStatus(str, enum.Enum):
    PENDING = "pending"      # Awaiting admin approval
    ACTIVE = "active"        # Approved and can log in
    REJECTED = "rejected"    # Admin declined
    SUSPENDED = "suspended"  # Temporarily disabled

class User(UserBase, table=True):
    # ... existing fields
    status: UserStatus = Field(default=UserStatus.PENDING)
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    approved_date: datetime | None = Field(default=None)
    approved_by: uuid.UUID | None = Field(default=None, foreign_key="user.id")
```

**Migration Required**: Alembic migration to add new fields and update existing users to `ACTIVE` status

#### Option B: Separate PendingRegistration Table

```python
class PendingRegistration(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    registration_date: datetime = Field(default_factory=datetime.utcnow)
    approval_token: str = Field(unique=True)
    token_expires: datetime
    status: str = "pending"  # pending, approved, rejected, expired
```

**Recommendation**: Option A is cleaner and maintains data in one place. Option B adds complexity but keeps pending users separate.

### 2. Backend API Changes

#### A. Modify Registration Endpoint (`/api/v1/users/signup`)

**Current:**

```python
@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        raise HTTPException(status_code=400, detail="Email already exists")
    user_create = UserCreate.model_validate(user_in)
    user = crud.create_user(session=session, user_create=user_create)
    return user
```

**Proposed:**

```python
@router.post("/signup", response_model=Message)
def register_user(session: SessionDep, user_in: UserRegister) -> Any:
    # Check if email already exists (active or pending)
    user = crud.get_user_by_email(session=session, email=user_in.email)
    if user:
        if user.status == UserStatus.PENDING:
            raise HTTPException(status_code=400,
                detail="Registration pending approval")
        else:
            raise HTTPException(status_code=400,
                detail="Email already exists")

    # Create user in pending state
    user_create = UserCreate.model_validate(user_in)
    user_create.status = UserStatus.PENDING
    user = crud.create_user(session=session, user_create=user_create)

    # Generate approval token
    approval_token = generate_approval_token(user.email, user.id)

    # Send admin notification email
    if settings.emails_enabled:
        send_admin_approval_email(
            user_email=user.email,
            user_name=user.full_name,
            approval_token=approval_token
        )

    return Message(message="Registration submitted. Awaiting admin approval.")
```

#### B. Add Approval Endpoint

```python
@router.post("/approve-registration/{token}")
def approve_registration(token: str, session: SessionDep) -> Any:
    """
    Approve a pending user registration.
    Admin-only endpoint (accessed via email link).
    """
    # Verify and decode token
    user_data = verify_approval_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Get pending user
    user = session.get(User, user_data["user_id"])
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.status != UserStatus.PENDING:
        raise HTTPException(status_code=400,
            detail="User already processed")

    # Activate user
    user.status = UserStatus.ACTIVE
    user.is_active = True
    user.approved_date = datetime.utcnow()
    # Optional: track which admin approved
    # user.approved_by = current_admin_user.id

    session.add(user)
    session.commit()

    # Send welcome email to user
    if settings.emails_enabled:
        send_registration_approved_email(
            email_to=user.email,
            full_name=user.full_name
        )

    # Return success page or redirect
    return {"message": "User approved successfully", "user_email": user.email}
```

#### C. Add Rejection Endpoint (Optional)

```python
@router.post("/reject-registration/{token}")
def reject_registration(token: str, session: SessionDep) -> Any:
    """Reject and delete a pending registration."""
    user_data = verify_approval_token(token)
    if not user_data:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = session.get(User, user_data["user_id"])
    if user and user.status == UserStatus.PENDING:
        session.delete(user)
        session.commit()
        return {"message": "Registration rejected"}

    raise HTTPException(status_code=400, detail="Invalid request")
```

### 3. Email System Enhancements

#### A. Create Admin Approval Email Template

**File:** `backend/app/email-templates/build/admin_approval_request.html`

```html
<!DOCTYPE html>
<html>
  <head>
    <title>New User Registration - Approval Required</title>
  </head>
  <body>
    <h2>{{ project_name }} - New Registration Request</h2>

    <p><strong>A new user has registered and requires your approval:</strong></p>

    <table style="border: 1px solid #ddd; padding: 15px;">
      <tr>
        <td><strong>Name:</strong></td>
        <td>{{ user_name }}</td>
      </tr>
      <tr>
        <td><strong>Email:</strong></td>
        <td>{{ user_email }}</td>
      </tr>
      <tr>
        <td><strong>Registration Date:</strong></td>
        <td>{{ registration_date }}</td>
      </tr>
    </table>

    <p style="margin-top: 30px;">
      <strong>Click below to approve or reject this registration:</strong>
    </p>

    <p>
      <a
        href="{{ approval_link }}"
        style="background-color: #28a745; color: white; padding: 12px 24px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;"
      >
        ✓ Approve Registration
      </a>
    </p>

    <p>
      <a
        href="{{ rejection_link }}"
        style="background-color: #dc3545; color: white; padding: 12px 24px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;"
      >
        ✗ Reject Registration
      </a>
    </p>

    <p style="margin-top: 30px; color: #666; font-size: 12px;">
      This approval link will expire in {{ expiry_hours }} hours.
    </p>
  </body>
</html>
```

#### B. Create User Welcome Email Template

**File:** `backend/app/email-templates/build/registration_approved.html`

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Account Approved - Welcome to {{ project_name }}</title>
  </head>
  <body>
    <h2>Welcome to {{ project_name }}!</h2>

    <p>Hi {{ user_name }},</p>

    <p>Great news! Your account registration has been approved.</p>

    <p><strong>You can now log in with your credentials:</strong></p>

    <ul>
      <li><strong>Email:</strong> {{ user_email }}</li>
      <li><strong>Login URL:</strong> <a href="{{ login_link }}">{{ login_link }}</a></li>
    </ul>

    <p>
      <a
        href="{{ login_link }}"
        style="background-color: #007bff; color: white; padding: 12px 24px; 
                  text-decoration: none; border-radius: 4px; display: inline-block;"
      >
        Go to Login
      </a>
    </p>

    <p>If you have any questions, please contact support.</p>

    <p>Best regards,<br />{{ project_name }} Team</p>
  </body>
</html>
```

#### C. Add Email Utility Functions

**File:** `backend/app/utils/email_utils.py`

```python
def generate_admin_approval_email(
    user_email: str,
    user_name: str,
    approval_token: str
) -> EmailData:
    """Generate email to admin requesting approval for new registration."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New Registration Requires Approval"

    approval_link = f"{settings.FRONTEND_HOST}/admin/approve-registration?token={approval_token}"
    rejection_link = f"{settings.FRONTEND_HOST}/admin/reject-registration?token={approval_token}"

    html_content = render_email_template(
        template_name="admin_approval_request.html",
        context={
            "project_name": project_name,
            "user_name": user_name,
            "user_email": user_email,
            "registration_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "approval_link": approval_link,
            "rejection_link": rejection_link,
            "expiry_hours": settings.APPROVAL_TOKEN_EXPIRE_HOURS,
        },
    )
    return EmailData(html_content=html_content, subject=subject)

def send_admin_approval_email(
    user_email: str,
    user_name: str,
    approval_token: str
) -> None:
    """Send approval request email to admin."""
    email_data = generate_admin_approval_email(
        user_email=user_email,
        user_name=user_name,
        approval_token=approval_token
    )
    send_email(
        email_to=settings.ADMIN_EMAIL,  # david@aiben.io
        subject=email_data.subject,
        html_content=email_data.html_content,
    )

def generate_registration_approved_email(
    email_to: str,
    full_name: str
) -> EmailData:
    """Generate welcome email after registration approval."""
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Account Approved!"

    html_content = render_email_template(
        template_name="registration_approved.html",
        context={
            "project_name": project_name,
            "user_name": full_name,
            "user_email": email_to,
            "login_link": f"{settings.FRONTEND_HOST}/login",
        },
    )
    return EmailData(html_content=html_content, subject=subject)

def send_registration_approved_email(
    email_to: str,
    full_name: str
) -> None:
    """Send approval notification to user."""
    email_data = generate_registration_approved_email(
        email_to=email_to,
        full_name=full_name
    )
    send_email(
        email_to=email_to,
        subject=email_data.subject,
        html_content=email_data.html_content,
    )
```

#### D. Token Generation/Verification Functions

```python
def generate_approval_token(email: str, user_id: str) -> str:
    """Generate secure approval token with expiration."""
    delta = timedelta(hours=settings.APPROVAL_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()

    encoded_jwt = jwt.encode(
        {
            "exp": exp,
            "nbf": now,
            "sub": email,
            "user_id": str(user_id),
            "type": "registration_approval"
        },
        settings.SECRET_KEY,
        algorithm=security.ALGORITHM,
    )
    return encoded_jwt

def verify_approval_token(token: str) -> dict | None:
    """Verify and decode approval token."""
    try:
        decoded_token = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[security.ALGORITHM]
        )
        if decoded_token.get("type") != "registration_approval":
            return None
        return {
            "email": decoded_token["sub"],
            "user_id": decoded_token["user_id"]
        }
    except InvalidTokenError:
        return None
```

### 4. Configuration Changes

#### Add to `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings

    # Admin approval settings
    ADMIN_EMAIL: EmailStr = "david@aiben.io"
    APPROVAL_TOKEN_EXPIRE_HOURS: int = 72  # 3 days
    REQUIRE_ADMIN_APPROVAL: bool = True  # Feature flag
```

### 5. Frontend Changes

#### A. Update Signup Success Message

**File:** `frontend/src/routes/signup.tsx`

```typescript
// In useAuth hook (frontend/src/hooks/useAuth.ts)
const signUpMutation = useMutation({
  mutationFn: (data: UserRegister) => UsersService.registerUser({ requestBody: data }),

  onSuccess: (data) => {
    // Check if response indicates pending approval
    showToast({
      title: "Registration Submitted",
      description: "Your account is pending admin approval. You'll receive an email when approved.",
      status: "info",
      duration: 8000,
    })
    navigate({ to: "/login" })
  },
  onError: (err: ApiError) => {
    // ... error handling
  },
})
```

#### B. Update Login Error Handling

**File:** `frontend/src/hooks/useAuth.ts`

Handle case where user tries to log in with pending account:

```typescript
const loginMutation = useMutation({
  mutationFn: (data: AccessToken) => LoginService.loginAccessToken({ formData: data }),

  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    navigate({ to: "/" })
  },
  onError: (err: ApiError) => {
    if (err.status === 403 && err.message?.includes("pending")) {
      showToast({
        title: "Account Pending",
        description: "Your account is awaiting admin approval.",
        status: "warning",
      })
    } else {
      // ... other error handling
    }
  },
})
```

#### C. Create Admin Approval Pages (Optional)

**File:** `frontend/src/routes/admin/approve-registration.tsx`

```typescript
import { useQuery } from "@tanstack/react-query"
import { useSearch } from "@tanstack/react-router"

export const Route = createFileRoute("/admin/approve-registration")({
  component: ApproveRegistration,
})

function ApproveRegistration() {
  const { token } = useSearch()

  const { data, isLoading, error } = useQuery({
    queryKey: ["approve-registration", token],
    queryFn: () => UsersService.approveRegistration({ token }),
    enabled: !!token,
  })

  if (isLoading) return <Spinner />

  if (error) {
    return <ErrorDisplay message="Invalid or expired approval link" />
  }

  return (
    <Container>
      <SuccessIcon />
      <Heading>Registration Approved</Heading>
      <Text>User {data.user_email} has been successfully approved.</Text>
      <Text>They will receive a welcome email shortly.</Text>
    </Container>
  )
}
```

### 6. Authentication Logic Updates

#### Update Login Validation

**File:** `backend/app/api/routes/login.py`

```python
@router.post("/access-token")
def login_access_token(
    session: SessionDep, form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    # NEW: Check if user account is pending approval
    if hasattr(user, 'status') and user.status == UserStatus.PENDING:
        raise HTTPException(
            status_code=403,
            detail="Account pending admin approval. Please check your email."
        )

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # ... rest of login logic
```

### 7. Database Migration

#### Alembic Migration Script

**File:** `backend/alembic/versions/xxx_add_user_approval_fields.py`

```python
"""Add user approval fields

Revision ID: xxx
Revises: yyy
Create Date: 2025-10-24
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

def upgrade() -> None:
    # Add status enum type
    op.execute("""
        CREATE TYPE userstatus AS ENUM ('pending', 'active', 'rejected', 'suspended')
    """)

    # Add new columns
    op.add_column('user', sa.Column('status',
        postgresql.ENUM('pending', 'active', 'rejected', 'suspended',
                       name='userstatus'),
        nullable=True))
    op.add_column('user', sa.Column('registration_date',
        sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('approved_date',
        sa.DateTime(), nullable=True))
    op.add_column('user', sa.Column('approved_by',
        postgresql.UUID(as_uuid=True), nullable=True))

    # Set existing users to 'active' status
    op.execute("UPDATE user SET status = 'active' WHERE status IS NULL")

    # Set registration_date for existing users to current timestamp
    op.execute("UPDATE user SET registration_date = NOW() WHERE registration_date IS NULL")

    # Make status NOT NULL after setting defaults
    op.alter_column('user', 'status', nullable=False)
    op.alter_column('user', 'registration_date', nullable=False)

    # Add foreign key constraint for approved_by
    op.create_foreign_key(
        'fk_user_approved_by', 'user', 'user',
        ['approved_by'], ['id'], ondelete='SET NULL'
    )

def downgrade() -> None:
    op.drop_constraint('fk_user_approved_by', 'user', type_='foreignkey')
    op.drop_column('user', 'approved_by')
    op.drop_column('user', 'approved_date')
    op.drop_column('user', 'registration_date')
    op.drop_column('user', 'status')
    op.execute("DROP TYPE userstatus")
```

### 8. Admin Dashboard (Optional Enhancement)

Create admin panel to view/manage pending registrations:

**Endpoint:** `GET /api/v1/admin/pending-registrations`

```python
@router.get(
    "/admin/pending-registrations",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=list[PendingUserPublic]
)
def get_pending_registrations(session: SessionDep) -> Any:
    """Get all pending user registrations. Admin only."""
    statement = select(User).where(User.status == UserStatus.PENDING)
    pending_users = session.exec(statement).all()
    return pending_users
```

Frontend component showing pending users with approve/reject buttons.

---

## Testing Strategy

### 1. Unit Tests

```python
# backend/app/tests/api/routes/test_registration_approval.py

def test_register_user_creates_pending_account(client: TestClient, db: Session):
    """Test that new registrations create pending accounts."""
    email = "newuser@example.com"
    response = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={
            "email": email,
            "password": "testpass123",
            "full_name": "Test User"
        }
    )
    assert response.status_code == 200

    # Check user is in pending state
    user = db.exec(select(User).where(User.email == email)).first()
    assert user.status == UserStatus.PENDING
    assert not user.is_active

def test_pending_user_cannot_login(client: TestClient, db: Session):
    """Test that pending users cannot log in."""
    # Create pending user
    user = User(
        email="pending@example.com",
        hashed_password=get_password_hash("password"),
        status=UserStatus.PENDING,
        is_active=False
    )
    db.add(user)
    db.commit()

    # Attempt login
    response = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": "pending@example.com", "password": "password"}
    )
    assert response.status_code == 403
    assert "pending" in response.json()["detail"].lower()

def test_approve_registration_activates_user(client: TestClient, db: Session):
    """Test approval endpoint activates pending user."""
    # Create pending user
    user = create_pending_user(db)
    token = generate_approval_token(user.email, str(user.id))

    # Approve registration
    response = client.post(
        f"{settings.API_V1_STR}/users/approve-registration/{token}"
    )
    assert response.status_code == 200

    # Verify user is now active
    db.refresh(user)
    assert user.status == UserStatus.ACTIVE
    assert user.is_active
    assert user.approved_date is not None

def test_expired_approval_token_fails(client: TestClient):
    """Test that expired tokens are rejected."""
    # Create token with past expiration
    expired_token = create_expired_approval_token()

    response = client.post(
        f"{settings.API_V1_STR}/users/approve-registration/{expired_token}"
    )
    assert response.status_code == 400
    assert "expired" in response.json()["detail"].lower()
```

### 2. Integration Tests

- Test full registration → approval → login flow
- Test email sending (use mock SMTP server)
- Test rejection flow
- Test duplicate registration attempts

### 3. E2E Tests (Playwright)

```typescript
// frontend/tests/registration-approval.spec.ts

test("User registration shows pending message", async ({ page }) => {
  await page.goto("/signup")

  await page.getByPlaceholder("Full Name").fill("Test User")
  await page.getByPlaceholder("Email").fill("test@example.com")
  await page.getByPlaceholder("Password", { exact: true }).fill("password123")
  await page.getByPlaceholder("Confirm Password").fill("password123")

  await page.getByRole("button", { name: "Sign Up" }).click()

  // Should show pending approval message
  await expect(page.getByText(/pending.*approval/i)).toBeVisible()
})

test("Pending user cannot login", async ({ page }) => {
  // Assuming we have a pending user in test DB
  await page.goto("/login")

  await page.getByPlaceholder("Email").fill("pending@example.com")
  await page.getByPlaceholder("Password").fill("password123")
  await page.getByRole("button", { name: "Log In" }).click()

  await expect(page.getByText(/pending.*approval/i)).toBeVisible()
})
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] Create and test database migration
- [ ] Update environment variables (ADMIN_EMAIL, APPROVAL_TOKEN_EXPIRE_HOURS)
- [ ] Create email templates
- [ ] Test SMTP configuration
- [ ] Update API client code generation
- [ ] Write comprehensive tests

### Deployment Steps

1. **Backup database**
2. **Deploy backend changes:**
   - Run database migration
   - Deploy new API code
   - Verify SMTP settings
3. **Deploy frontend changes:**
   - Update signup flow
   - Update login error handling
   - Deploy approval pages
4. **Verify:**
   - Test registration creates pending user
   - Test admin email is sent
   - Test approval link activates user
   - Test user can log in after approval

### Post-Deployment

- [ ] Monitor logs for email sending errors
- [ ] Test full flow in production
- [ ] Document admin approval process
- [ ] Create runbook for managing pending users

---

## Alternative/Simplified Approaches

### Option 1: Manual Database Activation (No Email)

- Simplest approach
- Users register normally but accounts are created as inactive
- Admin manually updates database: `UPDATE user SET is_active=true, status='active' WHERE email='user@example.com'`
- Admin manually sends email notification
- **Pros:** Minimal code changes
- **Cons:** Manual process, no audit trail, error-prone

### Option 2: Admin Dashboard Only (No Email Links)

- Users register and get pending status
- Admin logs into dashboard to see pending users
- Admin clicks approve/reject in UI
- System sends approval email to user
- **Pros:** More secure (no token in email), better UX for admin
- **Cons:** Requires admin to log in, more complex frontend

### Option 3: Hybrid Approach

- Email notification to admin (no action links)
- Admin must log into dashboard to approve
- Best of both worlds: notification + secure approval
- **Recommended for production systems**

---

## Security Considerations

1. **Token Security:**

   - Use JWT with short expiration (72 hours recommended)
   - Include user_id and type in token to prevent reuse
   - Verify token hasn't been used before (optional: store used tokens)

2. **Email Validation:**

   - Validate email format on frontend and backend
   - Consider adding email verification (separate from approval)
   - Check for disposable email domains

3. **Rate Limiting:**

   - Limit registration attempts per IP
   - Prevent spam registrations

4. **Audit Trail:**

   - Log all approval/rejection actions
   - Track who approved (if multiple admins)
   - Store timestamp of approval

5. **HTTPS Only:**
   - Ensure approval links only work over HTTPS in production
   - Use secure cookies for admin sessions

---

## Configuration Reference

### Environment Variables Required

```bash
# .env file additions
ADMIN_EMAIL=david@aiben.io
APPROVAL_TOKEN_EXPIRE_HOURS=72
REQUIRE_ADMIN_APPROVAL=true

# Existing email settings must be configured
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_TLS=true
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAILS_FROM_EMAIL=noreply@aiben.io
EMAILS_FROM_NAME="aibenIQ System"
```

---

## Timeline Estimate

| Task                                  | Estimated Time  |
| ------------------------------------- | --------------- |
| Database schema design & migration    | 2-3 hours       |
| Backend API changes (endpoints, CRUD) | 4-6 hours       |
| Email templates creation              | 2-3 hours       |
| Token generation/verification         | 1-2 hours       |
| Frontend changes (signup, login)      | 3-4 hours       |
| Admin approval pages                  | 2-3 hours       |
| Unit tests                            | 4-5 hours       |
| Integration/E2E tests                 | 3-4 hours       |
| Documentation                         | 1-2 hours       |
| Testing & debugging                   | 4-6 hours       |
| **Total**                             | **26-38 hours** |

---

## Risks & Mitigation

| Risk                                 | Impact                                | Mitigation                                                         |
| ------------------------------------ | ------------------------------------- | ------------------------------------------------------------------ |
| Email delivery failure               | High - approvals won't be sent        | Implement retry logic, log failures, add admin dashboard fallback  |
| Token expiration                     | Medium - admin misses approval window | Set longer expiration (72h), add reminder emails, allow re-request |
| Existing users affected by migration | High - active users become pending    | Migration script sets existing users to ACTIVE                     |
| SMTP misconfiguration                | High - no emails sent                 | Validate SMTP settings on startup, add health check endpoint       |
| User frustration from wait time      | Medium - poor UX                      | Set expectations in signup message, send status emails             |

---

## Future Enhancements

1. **Email verification before admin approval**

   - User verifies email first
   - Then admin approves
   - Two-step verification

2. **Bulk approval interface**

   - Approve multiple users at once
   - Export pending users to CSV

3. **Automatic approval rules**

   - Whitelist certain email domains
   - Auto-approve after manual review period

4. **Notification system**

   - Webhook when new user registers
   - Slack/Teams integration
   - Daily digest of pending users

5. **Self-service re-request**
   - User can re-send approval request if expired
   - Track number of requests

---

## Recommended Implementation Order

1. **Phase 1: Core Backend** (Start here)

   - Database migration
   - Update User model
   - Modify registration endpoint to create pending users

2. **Phase 2: Email System**

   - Create email templates
   - Add token generation/verification
   - Implement admin notification email

3. **Phase 3: Approval Mechanism**

   - Create approval/rejection endpoints
   - Add user welcome email
   - Test approval flow

4. **Phase 4: Frontend Updates**

   - Update signup success message
   - Update login error handling
   - Create approval result pages

5. **Phase 5: Testing & Polish**
   - Write comprehensive tests
   - Add admin dashboard (optional)
   - Documentation and deployment

---

## Questions to Answer Before Implementation

1. **Should rejected users be able to re-register?**

   - Delete user record entirely, or mark as rejected?
   - Allow same email to register again?

2. **Multiple admin approvers?**

   - Just david@aiben.io, or support multiple admins?
   - Track which admin approved?

3. **Notification preferences?**

   - Email only, or also in-app notifications?
   - Daily digest vs. immediate notification?

4. **User communication?**

   - Send rejection email or just silence?
   - Provide reason for rejection?

5. **Token expiration handling?**

   - Auto-delete expired pending users?
   - Allow re-requesting approval?

6. **Existing pending state?**
   - Any existing "pending" mechanisms to preserve?
   - Compatibility with current is_active flag?

---

## Conclusion

This implementation plan provides a comprehensive approach to converting self-service registration into an admin-approval system. The recommended approach is **Option A (User Status Field)** with email-based approval links for simplicity and maintainability.

**Next Steps:**

1. Review and approve this plan
2. Clarify any questions listed above
3. Begin with Phase 1 (Core Backend) implementation
4. Iteratively test and deploy each phase

**Estimated Total Implementation Time: 26-38 hours**

This approach balances security, user experience, and maintainability while providing a clear audit trail of all registrations and approvals.
