# Deployment Guide

This guide covers deploying the Tokyo Traffic Data Collection system in various environments, from local development to production cloud deployments.

## Overview

The system can be deployed in several configurations:

- **Local Development**: Single machine setup for development and testing
- **Server Deployment**: Dedicated server for continuous data collection
- **Cloud Deployment**: Scalable cloud infrastructure
- **Containerized Deployment**: Docker-based deployment for consistency

## Prerequisites

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB
- Storage: 50GB available space
- Network: Stable internet connection
- OS: Linux (Ubuntu 20.04+ recommended), macOS, or Windows 10+

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8GB+
- Storage: 200GB+ SSD
- Network: High-speed internet (>10Mbps)
- OS: Ubuntu 22.04 LTS

### Software Dependencies

- **Python**: 3.8 or higher
- **Git**: Version control
- **pip**: Python package manager
- **Optional**: Docker, Docker Compose

## Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/Tatsuru-Kikuchi/MCP-traffic.git
cd MCP-traffic
```

### 2. Python Environment Setup

#### Using venv (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Using conda
```bash
# Create conda environment
conda create -n mcp-traffic python=3.9
conda activate mcp-traffic

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy example configuration
cp config/api_config.example.json config/api_config.json

# Edit configuration with your API key
# The API key is already configured in the repository
```

### 4. Test Installation
```bash
# Test basic functionality
python src/collectors/traffic_collector.py --catalog-only

# Run full collection test
python scripts/collect_all_data.py --dry-run
```

## Server Deployment

### 1. Server Preparation

#### Ubuntu/Debian Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv git

# Create dedicated user
sudo useradd -m -s /bin/bash mcp-traffic
sudo su - mcp-traffic
```

#### CentOS/RHEL Setup
```bash
# Update system
sudo yum update -y

# Install required packages
sudo yum install -y python3 python3-pip git

# Create dedicated user
sudo useradd -m -s /bin/bash mcp-traffic
sudo su - mcp-traffic
```

### 2. Application Setup
```bash
# Clone repository
git clone https://github.com/Tatsuru-Kikuchi/MCP-traffic.git
cd MCP-traffic

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure application
cp config/api_config.example.json config/api_config.json
# Edit config/api_config.json with appropriate settings
```

### 3. System Service Setup

Create systemd service file:

```bash
sudo nano /etc/systemd/system/mcp-traffic.service
```

```ini
[Unit]
Description=Tokyo Traffic Data Collection Service
After=network.target

[Service]
Type=simple
User=mcp-traffic
Group=mcp-traffic
WorkingDirectory=/home/mcp-traffic/MCP-traffic
Environment=PATH=/home/mcp-traffic/MCP-traffic/venv/bin
ExecStart=/home/mcp-traffic/MCP-traffic/venv/bin/python scripts/schedule_collection.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-traffic
sudo systemctl start mcp-traffic
sudo systemctl status mcp-traffic
```

### 4. Log Rotation

Create logrotate configuration:
```bash
sudo nano /etc/logrotate.d/mcp-traffic
```

```
/home/mcp-traffic/MCP-traffic/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 mcp-traffic mcp-traffic
    postrotate
        systemctl reload mcp-traffic
    endscript
}
```

## Docker Deployment

### 1. Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mcp-traffic && \
    chown -R mcp-traffic:mcp-traffic /app
USER mcp-traffic

# Create necessary directories
RUN mkdir -p data/raw data/processed data/archives logs

# Default command
CMD ["python", "scripts/schedule_collection.py"]
```

### 2. Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  mcp-traffic:
    build: .
    container_name: mcp-traffic
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app/src
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('https://ckan.odpt.org')"]
      interval: 30s
      timeout: 10s
      retries: 3
    
  # Optional: Add monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-data:/var/lib/grafana

volumes:
  grafana-data:
```

### 3. Build and Run
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f mcp-traffic

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Deployment

#### 1. EC2 Instance Setup
```bash
# Launch EC2 instance (t3.medium recommended)
# Ubuntu 22.04 LTS AMI
# Configure security groups for SSH access

# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Follow server deployment steps above
```

#### 2. S3 for Data Storage
```python
# Add to config/api_config.json
{
  "storage": {
    "backend": "s3",
    "s3_bucket": "your-mcp-traffic-bucket",
    "s3_region": "us-east-1",
    "local_cache_path": "data/cache/"
  }
}
```

#### 3. CloudWatch Monitoring
```bash
# Install CloudWatch agent
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i amazon-cloudwatch-agent.deb

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

### Google Cloud Platform

#### 1. Compute Engine
```bash
# Create VM instance
gcloud compute instances create mcp-traffic-vm \
    --machine-type=e2-standard-2 \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=100GB

# SSH to instance
gcloud compute ssh mcp-traffic-vm
```

#### 2. Cloud Storage
```python
# Add to config/api_config.json
{
  "storage": {
    "backend": "gcs",
    "gcs_bucket": "your-mcp-traffic-bucket",
    "gcs_project": "your-project-id"
  }
}
```

### Azure Deployment

#### 1. Virtual Machine
```bash
# Create resource group
az group create --name mcp-traffic-rg --location eastus

# Create VM
az vm create \
    --resource-group mcp-traffic-rg \
    --name mcp-traffic-vm \
    --image UbuntuLTS \
    --size Standard_B2s \
    --admin-username azureuser \
    --generate-ssh-keys
```

## Monitoring and Logging

### 1. Application Monitoring

Create monitoring script:
```python
#!/usr/bin/env python3
# monitoring/health_check.py

import requests
import json
import time
from datetime import datetime

def check_api_connectivity():
    """Check ODPT API connectivity."""
    try:
        response = requests.get('https://ckan.odpt.org/api/3/action/status_show', timeout=10)
        return response.status_code == 200
    except:
        return False

def check_disk_space():
    """Check available disk space."""
    import shutil
    total, used, free = shutil.disk_usage('.')
    free_percent = (free / total) * 100
    return free_percent > 10  # Alert if less than 10% free

def check_recent_data():
    """Check if data was collected recently."""
    from pathlib import Path
    data_dir = Path('data/raw')
    if not data_dir.exists():
        return False
    
    # Check for files modified in last 2 hours
    cutoff = time.time() - 7200  # 2 hours
    recent_files = [f for f in data_dir.iterdir() 
                   if f.stat().st_mtime > cutoff]
    return len(recent_files) > 0

def main():
    status = {
        'timestamp': datetime.now().isoformat(),
        'api_connectivity': check_api_connectivity(),
        'disk_space_ok': check_disk_space(),
        'recent_data': check_recent_data()
    }
    
    # Log status
    with open('logs/health_check.log', 'a') as f:
        f.write(json.dumps(status) + '\n')
    
    # Print status
    print(json.dumps(status, indent=2))
    
    # Exit with error code if unhealthy
    if not all(status.values()):
        exit(1)

if __name__ == '__main__':
    main()
```

### 2. Log Aggregation

#### ELK Stack Setup
```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.14.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data

  logstash:
    image: docker.elastic.co/logstash/logstash:7.14.0
    volumes:
      - ./logging/logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
    depends_on:
      - elasticsearch

  kibana:
    image: docker.elastic.co/kibana/kibana:7.14.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    depends_on:
      - elasticsearch

volumes:
  elasticsearch-data:
```

### 3. Alerting

Create alerting script:
```python
#!/usr/bin/env python3
# monitoring/alerts.py

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

class AlertManager:
    def __init__(self, smtp_server, smtp_port, email, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.email = email
        self.password = password
        
    def send_alert(self, subject, message, recipients):
        """Send email alert."""
        msg = MIMEMultipart()
        msg['From'] = self.email
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            text = msg.as_string()
            server.sendmail(self.email, recipients, text)
            server.quit()
            return True
        except Exception as e:
            print(f"Failed to send alert: {e}")
            return False
            
    def check_and_alert(self):
        """Check system health and send alerts if needed."""
        # Run health check
        import subprocess
        result = subprocess.run(['python', 'monitoring/health_check.py'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            # System is unhealthy, send alert
            status = json.loads(result.stdout)
            
            alert_message = f"""
Tokyo Traffic Data Collection System Alert

Timestamp: {status['timestamp']}
API Connectivity: {status['api_connectivity']}
Disk Space OK: {status['disk_space_ok']}
Recent Data: {status['recent_data']}

Please check the system immediately.
"""
            
            self.send_alert(
                "MCP-Traffic System Alert",
                alert_message,
                ['admin@example.com']  # Replace with actual admin email
            )

# Usage
if __name__ == '__main__':
    alerter = AlertManager(
        'smtp.gmail.com', 587,
        'your-email@gmail.com',
        'your-app-password'
    )
    alerter.check_and_alert()
```

## Security Considerations

### 1. API Key Security
```bash
# Use environment variables for sensitive data
export ODPT_API_KEY="your-api-key-here"

# Or use a secrets management system
# AWS Secrets Manager, HashiCorp Vault, etc.
```

### 2. Network Security
```bash
# Configure firewall (UFW on Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow from 10.0.0.0/8 to any port 22  # Restrict SSH to private networks

# For Docker deployments
sudo ufw allow from 172.16.0.0/12 to any port 3000  # Grafana
sudo ufw allow from 172.16.0.0/12 to any port 9090  # Prometheus
```

### 3. SSL/TLS Configuration
```bash
# Use Let's Encrypt for SSL certificates
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# Configure nginx as reverse proxy
sudo apt install nginx
```

Nginx configuration:
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    location / {
        proxy_pass http://localhost:3000;  # Grafana
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### 1. Data Backup
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backup/mcp-traffic"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup data
tar -czf $BACKUP_DIR/data_backup_$DATE.tar.gz data/

# Backup configuration
cp -r config/ $BACKUP_DIR/config_backup_$DATE/

# Backup database if using one
# pg_dump mcp_traffic > $BACKUP_DIR/db_backup_$DATE.sql

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*backup*" -mtime +30 -delete

echo "Backup completed: $DATE"
```

### 2. Automated Backup
```bash
# Add to crontab
crontab -e

# Backup daily at 3 AM
0 3 * * * /home/mcp-traffic/MCP-traffic/scripts/backup.sh
```

### 3. Recovery Procedure
```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE=$1

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# Stop service
sudo systemctl stop mcp-traffic

# Restore data
tar -xzf $BACKUP_FILE -C /

# Restart service
sudo systemctl start mcp-traffic

echo "Restore completed from: $BACKUP_FILE"
```

## Performance Tuning

### 1. System Optimization
```bash
# Increase file descriptor limits
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# Optimize network settings
echo "net.core.rmem_max = 16777216" >> /etc/sysctl.conf
echo "net.core.wmem_max = 16777216" >> /etc/sysctl.conf
sudo sysctl -p
```

### 2. Python Optimization
```python
# Add to config/api_config.json
{
  "performance": {
    "worker_threads": 4,
    "connection_pool_size": 20,
    "request_timeout": 30,
    "retry_attempts": 3,
    "batch_size": 100
  }
}
```

### 3. Database Optimization (if using)
```sql
-- PostgreSQL optimizations
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
SELECT pg_reload_conf();
```

## Troubleshooting

### Common Issues

1. **API Rate Limiting**
   - Implement exponential backoff
   - Monitor request frequency
   - Use caching to reduce API calls

2. **Disk Space Issues**
   - Implement log rotation
   - Archive old data
   - Monitor disk usage

3. **Memory Issues**
   - Process data in chunks
   - Optimize data structures
   - Monitor memory usage

4. **Network Connectivity**
   - Implement retry logic
   - Use connection pooling
   - Monitor network status

### Debugging Commands
```bash
# Check service status
sudo systemctl status mcp-traffic

# View logs
sudo journalctl -u mcp-traffic -f

# Check resource usage
top -p $(pgrep -f mcp-traffic)

# Monitor network connections
sudo netstat -tulpn | grep python

# Check disk usage
df -h
du -sh data/
```

## Maintenance

### Regular Tasks

1. **Daily**
   - Check system health
   - Monitor disk space
   - Review error logs

2. **Weekly**
   - Update system packages
   - Clean up old logs
   - Verify backups

3. **Monthly**
   - Security updates
   - Performance review
   - Capacity planning

### Update Procedure
```bash
#!/bin/bash
# scripts/update.sh

# Stop service
sudo systemctl stop mcp-traffic

# Backup current version
cp -r MCP-traffic MCP-traffic.backup.$(date +%Y%m%d)

# Update code
cd MCP-traffic
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run tests
python -m pytest tests/ || { echo "Tests failed"; exit 1; }

# Restart service
sudo systemctl start mcp-traffic

# Verify deployment
sleep 10
sudo systemctl is-active mcp-traffic

echo "Update completed successfully"
```

This comprehensive deployment guide covers all aspects of deploying and maintaining the Tokyo Traffic Data Collection system in various environments. Choose the deployment method that best fits your requirements and infrastructure.