# Deployment Guide - Property Agentic Engine

## Overview

This guide covers deploying the Property Agentic Engine from local development to production.

---

## Prerequisites

### Required Software
- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- Git

### Required API Keys
- Perplexity API Key (from https://www.perplexity.ai/settings/api)

### Recommended Resources
- **Development**: 2 CPU, 4GB RAM
- **Production**: 4 CPU, 8GB RAM, 50GB storage

---

## Quick Start (Local Development)

```bash
# 1. Clone repository
git clone https://github.com/Dhyuthidhar/Data_Ingestion_realestate.git
cd property-agentic-engine

# 2. Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
./scripts/install.sh

# 4. Configure environment
cp .env.example .env
# Edit .env with your credentials

# 5. Initialize database
./scripts/setup-db.sh

# 6. Run tests
./scripts/setup-all.sh

# 7. Start API
python api.py
```

---

## Production Deployment

### Option 1: Single Server Deployment

**Recommended for:** Small to medium workloads (< 1000 requests/day)

#### 1. Server Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv postgresql redis-server nginx

# Create application user
sudo useradd -m -s /bin/bash propertyai
sudo su - propertyai
```

#### 2. Application Setup
```bash
# Clone and setup
git clone https://github.com/Dhyuthidhar/Data_Ingestion_realestate.git
cd property-agentic-engine

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Set production values
```

#### 3. Database Setup
```bash
# Configure PostgreSQL
sudo -u postgres createuser propertyai
sudo -u postgres createdb property_agentic_db -O propertyai

# Initialize schema
psql -U propertyai -d property_agentic_db -f init_db.sql
```

#### 4. System Service

Create `/etc/systemd/system/propertyai.service`:
```ini
[Unit]
Description=Property Agentic Engine API
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=propertyai
WorkingDirectory=/home/propertyai/property-agentic-engine
Environment="PATH=/home/propertyai/property-agentic-engine/venv/bin"
ExecStart=/home/propertyai/property-agentic-engine/venv/bin/gunicorn \
    -w 4 \
    -b 0.0.0.0:5001 \
    --timeout 180 \
    --access-logfile /var/log/propertyai/access.log \
    --error-logfile /var/log/propertyai/error.log \
    api:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable propertyai
sudo systemctl start propertyai
sudo systemctl status propertyai
```

#### 5. Nginx Configuration

Create `/etc/nginx/sites-available/propertyai`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 180s;
        proxy_send_timeout 180s;
        proxy_read_timeout 180s;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/propertyai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

### Option 2: Docker Deployment

Coming soon...

---

### Option 3: Cloud Platforms

#### AWS Deployment

Coming soon...

#### DigitalOcean Deployment

Coming soon...

---

## Environment Configuration

### Required Variables
```bash
# API Keys
PERPLEXITY_API_KEY=your_key_here
PERPLEXITY_MODEL=sonar-pro

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=property_agentic_db
DB_USER=propertyai
DB_PASSWORD=secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Application
ENVIRONMENT=production
DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5001

# Caching
CACHE_TTL=86400
MAX_AGENTS=5
RESEARCH_TIMEOUT=120
```

---

## Monitoring & Maintenance

### Health Checks
```bash
# System health
curl http://localhost:5001/health

# Component status
curl http://localhost:5001/api/status

# Statistics
curl http://localhost:5001/api/stats
```

### Logs
```bash
# Application logs
sudo journalctl -u propertyai -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Database Maintenance
```bash
# Backup database
pg_dump -U propertyai property_agentic_db > backup_$(date +%Y%m%d).sql

# Vacuum and analyze
psql -U propertyai -d property_agentic_db -c "VACUUM ANALYZE;"
```

### Cache Management
```bash
# Redis stats
redis-cli INFO stats

# Clear cache (if needed)
redis-cli FLUSHDB
```

---

## Performance Tuning

### PostgreSQL
```sql
-- Recommended settings for production
ALTER SYSTEM SET shared_buffers = '2GB';
ALTER SYSTEM SET effective_cache_size = '6GB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
```

### Gunicorn
```bash
# Workers: 2-4 x CPU cores
# Timeout: 180s (for long AI research)
gunicorn -w 4 -b 0.0.0.0:5001 --timeout 180 api:app
```

---

## Security Best Practices

1. **API Keys**: Store in environment variables, never commit
2. **Database**: Use strong passwords, restrict access
3. **Firewall**: Only allow necessary ports (80, 443, 5432 from localhost)
4. **SSL/TLS**: Use Let's Encrypt for HTTPS
5. **Rate Limiting**: Implement at nginx level
6. **Updates**: Regular security updates

---

## Troubleshooting

### API Not Starting
```bash
# Check logs
sudo journalctl -u propertyai -n 50

# Test configuration
python scripts/check-env.py
```

### Database Connection Issues
```bash
# Test connection
psql -U propertyai -d property_agentic_db -c "SELECT 1;"

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Redis Connection Issues
```bash
# Test Redis
redis-cli PING

# Check Redis status
sudo systemctl status redis
```

### Slow API Responses
```bash
# Check cache hit rate
curl http://localhost:5001/api/stats | jq '.cache.hit_rate_percent'

# Monitor active requests
ps aux | grep gunicorn
```

---

## Scaling

### Vertical Scaling
- Increase server resources (CPU, RAM)
- Optimize PostgreSQL configuration
- Increase Gunicorn workers

### Horizontal Scaling
- Add more application servers
- Use load balancer (nginx, HAProxy)
- Shared PostgreSQL and Redis instances

### Future Enhancements
- Read replicas for PostgreSQL
- Redis Cluster for distributed caching
- CDN for static assets
- Microservices architecture

---

## Cost Optimization

### API Costs
- **With 80% cache hit rate:**
  - 1000 requests/day = 200 API calls = $5/day
  - 10,000 requests/day = 2000 API calls = $50/day

### Infrastructure Costs
- **Single Server**: $20-50/month
- **Database + Cache**: Included or $10-20/month
- **Total**: ~$30-70/month for small-medium workload

---

## Support & Updates

### Getting Updates
```bash
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart propertyai
```

### Backup Strategy
- Database: Daily backups
- Configuration: Version controlled
- Logs: Rotate and archive

---

## Production Checklist

- [ ] API keys configured
- [ ] Database initialized and backed up
- [ ] Redis running and configured
- [ ] System service enabled
- [ ] Nginx configured with SSL
- [ ] Firewall rules configured
- [ ] Monitoring setup
- [ ] Log rotation configured
- [ ] Backup strategy implemented
- [ ] Health checks passing
- [ ] Performance tested
- [ ] Documentation reviewed

---
