# Database Connection Pool Exhaustion Fix

## Problem Summary

During Full Document Scan operations in TwinCheck (and potentially other features), the system was experiencing:

1. **Connection Pool Exhaustion**: `QueuePool limit of size 5 overflow 10 reached, connection timed out`
2. **AttributeError**: `request.comparison_topics` accessing wrong variable at line 860

## Root Causes

### 1. Small Connection Pool
The default SQLAlchemy connection pool was configured with:
- `pool_size=5` (default)
- `max_overflow=10` (default)
- `pool_timeout=30` (default)

This is insufficient for concurrent Full Document Scan operations which:
- Hold database sessions for extended periods (minutes)
- Run multiple LLM calls while session remains open
- Process multiple concurrent users

### 2. Variable Name Error
Line 860 in `twincheck.py` was accessing `request.comparison_topics` where:
- `request` is a `FastAPIRequest` object (Starlette HTTP request)
- Should be `comparison_topics` (function parameter from Form data)

## Fixes Implemented

### Fix 1: Increased Connection Pool Size
**File**: `backend/app/core/db.py`

**Changes**:
```python
# BEFORE:
engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))

# AFTER:
engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    pool_size=20,  # Increased from default 5
    max_overflow=40,  # Increased from default 10
    pool_timeout=60,  # Increased from default 30
    pool_pre_ping=True,  # Verify connections before use
)
```

**Rationale**:
- `pool_size=20`: Support 20 concurrent long-running operations
- `max_overflow=40`: Allow up to 60 total connections during peak load
- `pool_timeout=60`: Give more time for connections to become available
- `pool_pre_ping=True`: Prevent using stale/broken connections

### Fix 2: Fixed Variable Name Error
**File**: `backend/app/api/routes/twincheck.py`, line 860

**Changes**:
```python
# BEFORE:
{request.comparison_topics}

# AFTER:
{comparison_topics}
```

**Rationale**:
- `comparison_topics` is a function parameter extracted from Form data
- `request` is the HTTP request object, which doesn't have this attribute
- Accessing the correct variable prevents AttributeError

## Session Management Analysis

### Current Architecture
FastAPI uses dependency injection for database sessions:

```python
# backend/app/api/deps.py
def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_db)]
```

### Session Lifecycle in Full Document Scan
1. Request arrives → FastAPI creates session via `get_db()`
2. Session remains open throughout entire request processing
3. Full Document Scan operations may take several minutes
4. Multiple LLM calls made while session is held
5. Session released only when request completes

### Why Pool Exhaustion Occurred
- 5 concurrent users with Full Document Scan = pool exhausted
- Each operation holds connection for 2-5 minutes
- No session leaks detected (context manager properly closes)
- Just insufficient pool size for long-running operations

### No Session Leaks Found
✅ All session access uses dependency injection with context manager
✅ No manual `SessionLocal()` calls without proper cleanup
✅ No background tasks creating orphaned sessions
✅ Sessions properly closed after request completion

## Deployment Impact

### Requires Restart
Yes, the connection pool changes require backend restart:
```bash
docker-compose restart backend
```

### Database Impact
- PostgreSQL will see increased max connections
- Ensure PostgreSQL `max_connections` is set appropriately
- Recommended: `max_connections >= 100` (for pool_size=20, overflow=40, plus other services)

### Monitoring Recommendations
After deployment, monitor:
1. Connection pool metrics (current size, overflow usage)
2. Average session duration for Full Document Scan operations
3. Pool timeout errors (should be eliminated)
4. Database connection count

## Testing Checklist

- [ ] Backend restart successful
- [ ] TwinCheck Full Document Scan completes without AttributeError
- [ ] Multiple concurrent Full Document Scan operations work
- [ ] No connection pool timeout errors in logs
- [ ] Session cleanup still working (no connection leaks)

## Related Files Modified

1. `backend/app/core/db.py` - Connection pool configuration
2. `backend/app/api/routes/twincheck.py` - Fixed variable name error

## Performance Expectations

### Before Fix
- 5-6 concurrent Full Document Scan operations → pool exhaustion
- Connection timeout errors after 30 seconds
- Requests failing with 500 errors

### After Fix
- Up to 20 concurrent operations in normal pool
- Up to 60 concurrent operations with overflow
- 60 second timeout (double the previous)
- More resilient to peak load scenarios

## Alternative Solutions Considered

### Option 1: Session Per Operation (Not Implemented)
Create new session for each chunk processing instead of holding one session:
- **Pros**: Minimal connection hold time
- **Cons**: More complex, breaks transaction semantics, requires significant refactoring

### Option 2: Connection Pooling Proxy (Not Implemented)
Use PgBouncer or similar connection pooler:
- **Pros**: Better connection management, supports 1000+ clients
- **Cons**: Additional infrastructure, deployment complexity

### Option 3: Async Sessions (Future Enhancement)
Use SQLAlchemy async sessions with asyncio-friendly connection pooling:
- **Pros**: Better concurrency, non-blocking I/O
- **Cons**: Major refactoring required, ecosystem support needed

## Conclusion

The immediate fix (increased pool size) addresses the production issue without requiring architectural changes. The pool size increase is conservative and should handle typical production loads while we monitor usage patterns.

For future scaling beyond 60 concurrent long-running operations, consider implementing async sessions or a connection pooling proxy.
