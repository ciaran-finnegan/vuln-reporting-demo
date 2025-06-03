# RiskRadar Deployment Guide

This guide provides step-by-step instructions for deploying RiskRadar to Digital Ocean with automated CI/CD using GitHub Actions.

## Prerequisites

1. Domain name with DNS control
2. Digital Ocean account
3. GitHub repository with admin access
4. Basic familiarity with command line tools

## 1. DNS Configuration

### 1.1 Purchase/Configure Domain
1. Purchase a domain from any registrar (Namecheap, GoDaddy, etc.)
2. Access your DNS management panel

### 1.2 Create DNS Records
Add these DNS records pointing to your Digital Ocean droplet IP:

```
Type: A
Name: @
Value: YOUR_DROPLET_IP
TTL: 300

Type: A  
Name: www
Value: YOUR_DROPLET_IP
TTL: 300

Type: CNAME
Name: api
Value: your-domain.com
TTL: 300
```

## 2. Digital Ocean Setup

### 2.1 Create Droplet
1. Log into Digital Ocean dashboard
2. Click "Create" → "Droplets"
3. Choose configuration:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic plan, $24/month (4GB RAM, 2 CPUs)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH keys (recommended) or password
   - **Hostname**: riskradar-prod

### 2.2 Initial Server Setup
SSH into your droplet:
```bash
ssh root@YOUR_DROPLET_IP
```

#### Update system and install Docker:
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Create deployment directory
mkdir -p /opt/riskradar
cd /opt/riskradar

# Create non-root user for deployment
adduser deploy
usermod -aG docker deploy
usermod -aG sudo deploy
```

#### Configure firewall:
```bash
# Install and configure UFW
ufw allow OpenSSH
ufw allow 80
ufw allow 443
ufw enable
```

### 2.3 Setup SSL with Let's Encrypt
```bash
# Install Certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Verify certificates location
ls -la /etc/letsencrypt/live/your-domain.com/
```

### 2.4 Setup Application Environment
```bash
# Switch to deploy user
su - deploy
cd /opt/riskradar

# Create environment file
cp production.env.template .env

# Edit environment file with your values
nano .env
```

Update `.env` with your specific values:
```bash
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
# Copy the output and paste it in .env file
```

### 2.5 Setup SSL certificates for Docker
```bash
# Create SSL directory for Docker
sudo mkdir -p /opt/riskradar/ssl
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/riskradar/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/riskradar/ssl/key.pem
sudo chown -R deploy:deploy /opt/riskradar/ssl
```

### 2.6 Setup SSL renewal
```bash
# Create renewal script
sudo nano /etc/cron.daily/ssl-renewal

# Add this content:
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/riskradar/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/riskradar/ssl/key.pem
chown -R deploy:deploy /opt/riskradar/ssl
docker-compose -f /opt/riskradar/docker-compose.yml restart nginx

# Make executable
sudo chmod +x /etc/cron.daily/ssl-renewal
```

## 3. GitHub Configuration

### 3.1 Enable GitHub Packages
1. Go to your repository settings
2. Navigate to "Actions" → "General"
3. Ensure "Read and write permissions" is selected
4. Enable "Allow GitHub Actions to create and approve pull requests"

### 3.2 Create Deployment SSH Key
On your local machine:
```bash
# Generate SSH key pair for deployment
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy
```

Add public key to Digital Ocean droplet:
```bash
# On the droplet, as deploy user
mkdir -p ~/.ssh
echo "YOUR_PUBLIC_KEY_CONTENT" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
chmod 700 ~/.ssh
```

### 3.3 Configure GitHub Secrets
Go to your repository → Settings → Secrets and Variables → Actions

Add these repository secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DO_HOST` | `YOUR_DROPLET_IP` | Digital Ocean droplet IP address |
| `DO_USERNAME` | `deploy` | SSH username for deployment |
| `DO_SSH_KEY` | `PRIVATE_KEY_CONTENT` | Content of ~/.ssh/github_deploy (private key) |

### 3.4 Copy Application Files to Server
```bash
# On the droplet as deploy user
cd /opt/riskradar

# Clone your repository or copy necessary files
git clone https://github.com/YOUR_USERNAME/vuln-reporting-demo.git .

# Update nginx.conf with your domain
sed -i 's/your-domain.com/YOUR_ACTUAL_DOMAIN/g' nginx.conf

# Update docker-compose.yml environment file path
nano docker-compose.yml
# Ensure env_file points to your .env file
```

## 4. Database Setup

### 4.1 Initialize Database
```bash
# Start database service
docker-compose up -d db

# Wait for database to be ready
sleep 30

# Run initial migrations and setup
docker-compose exec db createdb -U riskradar riskradar
```

## 5. Initial Deployment

### 5.1 Test Local Build
```bash
# Build and test locally on the droplet
docker-compose build
docker-compose up -d

# Check all services are running
docker-compose ps

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Setup initial data
docker-compose exec web python manage.py setup_asset_categories
docker-compose exec web python manage.py populate_initial_data
```

### 5.2 Test Application
Visit your domain:
- `https://your-domain.com/api/status/` - Should return 200 OK
- `https://your-domain.com/admin/` - Django admin login

## 6. Automated Deployment

### 6.1 Test GitHub Actions
1. Make a small change to your repository
2. Commit and push to main branch
3. Go to GitHub → Actions tab
4. Verify the deployment workflow runs successfully

### 6.2 Monitor Deployment
```bash
# On the droplet, monitor logs
docker-compose logs -f web
docker-compose logs -f nginx
```

## 7. Post-Deployment Configuration

### 7.1 Setup Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Setup log rotation
sudo nano /etc/logrotate.d/docker-containers
```

Add this content:
```
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    copytruncate
}
```

### 7.2 Backup Configuration
```bash
# Create backup script
nano /home/deploy/backup.sh
```

Add this content:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/deploy/backups"
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T db pg_dump -U riskradar riskradar > $BACKUP_DIR/db_$DATE.sql

# Upload files backup
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /opt/riskradar/temp_uploads

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

```bash
chmod +x /home/deploy/backup.sh

# Add to crontab for daily backups at 2 AM
crontab -e
# Add: 0 2 * * * /home/deploy/backup.sh
```

## 8. Security Hardening

### 8.1 Additional Security Measures
```bash
# Disable root SSH access
sudo nano /etc/ssh/sshd_config
# Set: PermitRootLogin no
# Set: PasswordAuthentication no (if using SSH keys)

sudo systemctl restart ssh

# Install fail2ban
sudo apt install fail2ban -y
sudo systemctl enable fail2ban
```

### 8.2 Setup CloudFlare (Optional)
1. Sign up for CloudFlare
2. Add your domain
3. Update nameservers at your registrar
4. Enable "Full" SSL/TLS encryption mode
5. Enable additional security features

## 9. Troubleshooting

### Common Issues and Solutions

#### SSL Certificate Issues
```bash
# Check certificate validity
openssl x509 -in /opt/riskradar/ssl/cert.pem -text -noout

# Renew certificates manually
sudo certbot renew --force-renewal
```

#### Database Connection Issues
```bash
# Check database logs
docker-compose logs db

# Connect to database directly
docker-compose exec db psql -U riskradar -d riskradar
```

#### Application Logs
```bash
# View application logs
docker-compose logs -f web

# Check nginx logs
docker-compose logs -f nginx
```

#### Performance Issues
```bash
# Monitor system resources
htop
docker stats

# Check disk space
df -h
docker system df
```

## 10. Scaling Considerations

### For Higher Traffic
1. **Load Balancer**: Use Digital Ocean Load Balancer
2. **Database**: Migrate to Digital Ocean Managed PostgreSQL
3. **Static Files**: Use Digital Ocean Spaces (S3-compatible)
4. **Caching**: Add Redis for session/cache storage
5. **Multiple Droplets**: Scale horizontally with container orchestration

### Performance Monitoring
- Set up application monitoring (e.g., Sentry for error tracking)
- Use Digital Ocean monitoring for infrastructure metrics
- Consider APM tools for detailed performance insights

---

## Quick Reference

### Essential Commands
```bash
# Deploy latest version
cd /opt/riskradar && docker-compose pull && docker-compose up -d

# View logs
docker-compose logs -f

# Run Django commands
docker-compose exec web python manage.py [command]

# Database backup
docker-compose exec -T db pg_dump -U riskradar riskradar > backup.sql

# Restart services
docker-compose restart [service_name]
```

### Important File Locations
- Application: `/opt/riskradar/`
- SSL Certificates: `/opt/riskradar/ssl/`
- Logs: `docker-compose logs`
- Environment: `/opt/riskradar/.env`
- Backups: `/home/deploy/backups/` 