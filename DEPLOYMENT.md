# RiskRadar Deployment Guide

This guide provides step-by-step instructions for deploying RiskRadar to Digital Ocean with automated CI/CD using GitHub Actions. This setup supports both production and development environments with automatic deployment.

## Environments

- **Production**: Deploys from `main` branch to your production domain
- **Development**: Deploys from `dev` branch to `riskradar.dev.securitymetricshub.com`

## Prerequisites

1. Domain name with DNS control
2. Digital Ocean account (with two droplets for production and development)
3. GitHub repository with admin access
4. Basic familiarity with command line tools

## 1. DNS Configuration

### 1.1 Purchase/Configure Domain
1. Purchase a domain from any registrar (Namecheap, GoDaddy, etc.)
2. Access your DNS management panel

### 1.2 Create DNS Records
Add these DNS records pointing to your Digital Ocean droplet IPs:

**For Production (your-domain.com):**
```
Type: A
Name: @
Value: YOUR_PRODUCTION_DROPLET_IP
TTL: 300

Type: A  
Name: www
Value: YOUR_PRODUCTION_DROPLET_IP
TTL: 300
```

**For Development (riskradar.dev.securitymetricshub.com):**
```
Type: A
Name: riskradar.dev
Value: YOUR_DEVELOPMENT_DROPLET_IP
TTL: 300
```

Perfect! Your DNS is correctly configured. The API will be accessible at:
- **Development**: `https://riskradar.dev.securitymetricshub.com/api/`
- **Production**: `https://your-domain.com/api/`

## 2. Digital Ocean Setup

### 2.1 Create Droplets
Create two droplets for production and development environments:

**Production Droplet:**
1. Log into Digital Ocean dashboard
2. Click "Create" → "Droplets"
3. Choose configuration:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic plan, $24/month (4GB RAM, 2 CPUs)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH keys (recommended) or password
   - **Hostname**: riskradar-prod

**Development Droplet:**
1. Repeat the process with these settings:
   - **Image**: Ubuntu 22.04 LTS
   - **Size**: Basic plan, $12/month (2GB RAM, 1 CPU) - smaller for dev
   - **Datacenter**: Same as production
   - **Authentication**: Same SSH keys
   - **Hostname**: riskradar-dev

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

# Configure nginx for ACME challenge (nginx is installed automatically)
mkdir -p /var/www/html/.well-known/acme-challenge

# Create nginx config for ACME challenges
tee /etc/nginx/sites-available/default > /dev/null <<EOF
server {
    listen 80;
    server_name riskradar.dev.securitymetricshub.com;  # For dev environment
    # server_name your-domain.com www.your-domain.com;  # For production
    
    root /var/www/html;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
        try_files \$uri =404;
    }
    
    location / {
        return 404;
    }
}
EOF

# Enable the site and reload nginx
ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate using webroot method
# For development:
certbot certonly --webroot -w /var/www/html -d riskradar.dev.securitymetricshub.com

# For production:
# certbot certonly --webroot -w /var/www/html -d your-domain.com -d www.your-domain.com

# Verify certificates location
# For development:
ls -la /etc/letsencrypt/live/riskradar.dev.securitymetricshub.com/

# For production:
# ls -la /etc/letsencrypt/live/your-domain.com/
```

### 2.4 Setup Application Environment
```bash
# Fix directory ownership first
chown -R deploy:deploy /opt/riskradar

# Switch to deploy user
su - deploy
cd /opt/riskradar

# Clone the repository
git clone https://github.com/YOUR_USERNAME/vuln-reporting-demo.git .

# Create environment file (use correct template for each environment)
# For development environment:
cp development.env.template .env

# For production environment:
# cp production.env.template .env

# Edit environment file with your values
nano .env
```

Update `.env` with your specific values:
```bash
# Generate a secret key
SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(50))')
# Copy the output and paste it in .env file

# For development, update these key values:
DEBUG=True
SECRET_KEY=your-generated-secret-key-here
ALLOWED_HOSTS=riskradar.dev.securitymetricshub.com,localhost,127.0.0.1
DATABASE_URL=postgresql://riskradar_dev:your-secure-password@db:5432/riskradar_dev
POSTGRES_PASSWORD=your-secure-password

# For production, update these key values:
# DEBUG=False
# SECRET_KEY=your-generated-secret-key-here
# ALLOWED_HOSTS=your-domain.com,www.your-domain.com
# DATABASE_URL=postgresql://riskradar:your-secure-password@db:5432/riskradar
# POSTGRES_PASSWORD=your-secure-password
```

### 2.5 Setup SSL certificates for Docker
```bash
# Create SSL directory for Docker
mkdir -p /opt/riskradar/ssl

# For development environment:
cp /etc/letsencrypt/live/riskradar.dev.securitymetricshub.com/fullchain.pem /opt/riskradar/ssl/cert.pem
cp /etc/letsencrypt/live/riskradar.dev.securitymetricshub.com/privkey.pem /opt/riskradar/ssl/key.pem

# For production environment:
# cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/riskradar/ssl/cert.pem
# cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/riskradar/ssl/key.pem

# Set proper ownership
chown -R deploy:deploy /opt/riskradar/ssl
```

### 2.6 Setup SSL renewal (Optional but Recommended)
```bash
# Note: Certbot automatically sets up SSL renewal via systemd timer when installed
# However, since we copy certificates to Docker, we need a script to update Docker certificates

# Create renewal hook script (optional - only needed if you want automatic Docker certificate updates)
nano /etc/cron.daily/ssl-renewal

# For development environment, add this content:
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/riskradar.dev.securitymetricshub.com/fullchain.pem /opt/riskradar/ssl/cert.pem
cp /etc/letsencrypt/live/riskradar.dev.securitymetricshub.com/privkey.pem /opt/riskradar/ssl/key.pem
chown -R deploy:deploy /opt/riskradar/ssl
cd /opt/riskradar && docker-compose -f docker-compose.dev.yml restart nginx

# For production environment, add this content instead:
#!/bin/bash
certbot renew --quiet
cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /opt/riskradar/ssl/cert.pem
cp /etc/letsencrypt/live/your-domain.com/privkey.pem /opt/riskradar/ssl/key.pem
chown -R deploy:deploy /opt/riskradar/ssl
cd /opt/riskradar && docker-compose restart nginx

# Make executable
chmod +x /etc/cron.daily/ssl-renewal

# Check automatic renewal is working
systemctl status certbot.timer
certbot renew --dry-run
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

**Production Secrets:**
| Secret Name | Value | Description |
|-------------|-------|-------------|
| `PROD_HOST` | `YOUR_PRODUCTION_DROPLET_IP` | Production droplet IP address |
| `PROD_USERNAME` | `deploy` | SSH username for production |
| `PROD_SSH_KEY` | `PRIVATE_KEY_CONTENT` | Private key for production deployment |

**Development Secrets:**
| Secret Name | Value | Description |
|-------------|-------|-------------|
| `DEV_HOST` | `YOUR_DEVELOPMENT_DROPLET_IP` | Development droplet IP address |
| `DEV_USERNAME` | `deploy` | SSH username for development |
| `DEV_SSH_KEY` | `PRIVATE_KEY_CONTENT` | Private key for development deployment |

### 3.4 Final Application Setup
```bash
# On the droplet as deploy user (should already be done in section 2.4)
cd /opt/riskradar

# Verify repository is cloned and files exist
ls -la

# For development environment, no need to update nginx.dev.conf as it's already configured
# For production environment, update nginx.conf with your domain:
# sed -i 's/your-domain.com/YOUR_ACTUAL_DOMAIN/g' nginx.conf

# Verify environment file exists
cat .env | head -5
```

## 4. Initial Deployment and Setup

### 4.1 Start All Services
```bash
# Start all services (web, database, nginx)
# For development environment:
docker-compose -f docker-compose.dev.yml up -d

# For production environment:
# docker-compose up -d

# Check all services are running
# For development:
docker-compose -f docker-compose.dev.yml ps

# For production:
# docker-compose ps

# Wait a moment for database to initialize, then check logs if needed
docker-compose -f docker-compose.dev.yml logs db
```

## 5. Configure Application

### 5.1 Run Database Migrations and Setup
```bash
# Collect static files first
# For development:
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput

# For production:
# docker-compose exec web python manage.py collectstatic --noinput

# Run migrations
# For development:
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# For production:
# docker-compose exec web python manage.py migrate

# Create superuser (you'll be prompted for username, email, password)
# For development:
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# For production:
# docker-compose exec web python manage.py createsuperuser

# Setup initial data
# For development:
docker-compose -f docker-compose.dev.yml exec web python manage.py setup_asset_categories
docker-compose -f docker-compose.dev.yml exec web python manage.py populate_initial_data

# For production:
# docker-compose exec web python manage.py setup_asset_categories
# docker-compose exec web python manage.py populate_initial_data
```

### 5.2 Test Application
Visit your domain:

**For development environment:**
- `https://riskradar.dev.securitymetricshub.com/api/status/` - Should return 200 OK
- `https://riskradar.dev.securitymetricshub.com/admin/` - Django admin login

**For production environment:**
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
# For development:
docker-compose -f docker-compose.dev.yml logs -f web
docker-compose -f docker-compose.dev.yml logs -f nginx

# For production:
# docker-compose logs -f web
# docker-compose logs -f nginx
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

**For Development Environment:**
```bash
# Deploy latest version
cd /opt/riskradar && docker-compose -f docker-compose.dev.yml pull && docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Run Django commands
docker-compose -f docker-compose.dev.yml exec web python manage.py [command]

# Database backup
docker-compose -f docker-compose.dev.yml exec -T db pg_dump -U riskradar_dev riskradar_dev > backup.sql

# Restart services
docker-compose -f docker-compose.dev.yml restart [service_name]
```

**For Production Environment:**
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