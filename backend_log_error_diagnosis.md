# Docker Backend Log Corruption Diagnosis

## Error Message
```
error from daemon in stream: Error grabbing logs: invalid character 'l' after object key:value pair
```

## Root Cause Analysis

### Actual Problem Found
After investigating the specific backend container logs for `aiben-react-backend-1`, the issue is **missing newline separators between JSON log entries**. 

**Evidence:**
- Container ID: `7473ae7e8987182381aa7cf8d686920778dbfad776b0aeda410bb82fc9c6542a`
- Log file size: 15.7MB (indicating substantial logging activity)
- Log format: Docker's `json-file` logging driver expects one JSON object per line

### Log File Corruption Details
When examining the actual log file with `cat -A`, the entries look like:
```
{"log":"      INFO   127.0.0.1:43950 - \"GET /api/v1/utils/health-check/ HTTP/1.1\" 200\n","stream":"stdout","time":"2025-09-17T03:30:01.01852122Z"}$   {"log":"      INFO   127.0.0.1:40072 - \"GET /api/v1/utils/health-check/ HTTP/1.1\" 200\n","stream":"stdout","time":"2025-09-17T03:30:11.192762829Z"}$
```

**Problem:** JSON objects are concatenated without proper line breaks between them, creating invalid JSON when Docker tries to parse the file line by line.

### Contributing Factors
1. **FastAPI Application Configuration:**
   - Backend runs with `fastapi run --workers 4` (multi-worker setup)
   - No explicit logging configuration in `main.py`
   - Uses default uvicorn logging

2. **Docker Configuration:**
   - Uses default `json-file` logging driver
   - No logging driver options specified in `docker-compose.yml`
   - Environment variable `PYTHONUNBUFFERED=1` is set (good for Docker logs)

3. **High-Volume Logging:**
   - Frequent health check requests (every 10 seconds)
   - Large OpenAI API response logging from `/api/v1/usage/token-usage` endpoint
   - Multiple worker processes writing simultaneously

### Why This Happens
- **Race Conditions:** Multiple uvicorn workers writing to stdout simultaneously can cause log entries to be interleaved
- **Buffering Issues:** Log entries not being properly flushed with newlines
- **Large Payloads:** Very long log lines from OpenAI API responses may be getting truncated or split incorrectly

## Immediate Solutions

### 1. Clear Corrupted Log File
```bash
# Stop the container
docker-compose stop backend

# Clear the log file
sudo truncate -s 0 /var/lib/docker/containers/7473ae7e8987182381aa7cf8d686920778dbfad776b0aeda410bb82fc9c6542a/7473ae7e8987182381aa7cf8d686920778dbfad776b0aeda410bb82fc9c6542a-json.log

# Restart the container
docker-compose up -d backend
```

### 2. Configure Docker Logging Options
Add to `docker-compose.yml` backend service:
```yaml
backend:
  # ... existing config ...
  logging:
    driver: "json-file"
    options:
      max-size: "10m"
      max-file: "3"
```

### 3. Reduce Log Volume
Consider implementing log level filtering or reducing verbosity of the OpenAI API response logging in your application.

## Long-term Prevention

### 1. Implement Proper Logging Configuration
Add structured logging configuration to the FastAPI application to ensure atomic log writes.

### 2. Use Alternative Logging Driver
Consider switching to `local` logging driver:
```yaml
logging:
  driver: "local"
  options:
    max-size: "10m"
    max-file: "3"
```

### 3. Implement Log Rotation
Set up proper log rotation to prevent log files from growing too large.

## System Details
- **Container:** aiben-react-backend-1
- **Image:** backend:latest (FastAPI with uvicorn)
- **Workers:** 4
- **Log Size:** 15.7MB
- **Primary Log Source:** Health checks + OpenAI API usage tracking

## References
- [Docker Logging Drivers](https://docs.docker.com/config/containers/logging/configure/)
- [Uvicorn Logging Configuration](https://www.uvicorn.org/settings/#logging)
- [FastAPI Logging Best Practices](https://fastapi.tiangolo.com/tutorial/logging/)
