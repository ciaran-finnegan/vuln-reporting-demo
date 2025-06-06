# Docker Logs Access Configuration

## Overview

The RiskRadar application supports real-time Docker container logs access through the admin dashboard. This feature is **disabled by default** for security reasons and should only be enabled in development environments.

## ⚠️ Security Warning

**NEVER enable Docker logs access in production!** Mounting the Docker socket gives the container significant system access and poses security risks.

## Development Setup

### Option 1: Environment Variable Only

1. Set `ENABLE_DOCKER_LOGS=true` in your `.env` file
2. Manually mount Docker socket in your docker-compose file:
   ```yaml
   volumes:
     - /var/run/docker.sock:/var/run/docker.sock
   ```

### Option 2: Using Docker Compose Override (Recommended)

1. Set `ENABLE_DOCKER_LOGS=true` in your `.env` file
2. Use the provided override file:
   ```bash
   docker-compose -f docker-compose.dev.yml -f docker-compose.docker-logs.yml up
   ```

## Usage

Once enabled, you can access Docker logs through:

- **API Endpoint**: `GET /api/v1/logs/docker/{container_name}/`
- **Frontend**: Log Management → Docker Logs section
- **Container Names**: Try `riskradar_web_1`, `riskradar_nginx_1`, etc.

## API Response

```json
{
  "container": "riskradar_web_1",
  "logs": [
    {
      "timestamp": "2025-06-06T00:30:00.000Z",
      "message": "[INFO] Django application started"
    }
  ],
  "total_lines": 100,
  "lines_requested": 100,
  "container_status": "running",
  "docker_logs_enabled": true
}
```

## When Disabled

If `ENABLE_DOCKER_LOGS=false` (default), the API returns an informative message:

```json
{
  "container": "riskradar_web_1",
  "logs": [
    {
      "timestamp": "2025-06-06T00:30:00.000Z",
      "message": "[INFO] Docker logs access is disabled"
    },
    {
      "timestamp": "2025-06-06T00:29:30.000Z",
      "message": "[INFO] Set ENABLE_DOCKER_LOGS=true in environment to enable"
    }
  ],
  "docker_logs_enabled": false,
  "message": "Docker logs disabled via ENABLE_DOCKER_LOGS environment variable"
}
```

## Production Deployment

In production:
- `ENABLE_DOCKER_LOGS` should be `false` or unset
- Docker socket should **never** be mounted
- The feature gracefully falls back to disabled state 