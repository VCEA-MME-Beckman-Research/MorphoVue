# Deployment Guide - MorphoVue

Complete guide for deploying the CT Tick ML Platform to production.

## Prerequisites

- Firebase project (Blaze plan required for Cloud Run)
- Google Cloud Platform account
- Node.js 18+ and npm
- Python 3.10+
- Docker and Docker Compose
- Kamiak HPC account

## Firebase Setup

### 1. Create Firebase Project

1. Go to https://console.firebase.google.com/
2. Click "Add project"
3. Enter project name: "morphovue" (or your choice)
4. Enable Google Analytics (optional)
5. Create project

### 2. Upgrade to Blaze Plan

1. In Firebase Console, click "Upgrade" (bottom left)
2. Select "Blaze" (Pay as you go)
3. Required for Cloud Run deployment

### 3. Enable Services

Enable required services:
- **Authentication**: Email/Password
- **Firestore Database**: Production mode
- **Storage**: Default bucket
- **Hosting**: Enable

### 4. Configure Authentication

1. Go to Authentication → Sign-in method
2. Enable "Email/Password"
3. Add authorized domains (your domain + localhost)

### 5. Create Service Account

1. Go to Project Settings → Service Accounts
2. Click "Generate new private key"
3. Save as `firebase-credentials.json`
4. **NEVER commit this file to git**

### 6. Deploy Firebase Rules

```bash
cd firebase
npm install
firebase login
firebase init  # Select Firestore, Storage, Hosting

# Copy project ID to .firebaserc
cat > .firebaserc << EOF
{
  "projects": {
    "default": "your-project-id"
  }
}
EOF

# Deploy rules
firebase deploy --only firestore:rules
firebase deploy --only storage:rules
```

## Backend Deployment

### Option 1: Cloud Run (Recommended)

#### Build and Deploy

```bash
cd backend

# Build Docker image
docker build -t gcr.io/your-project-id/cttick-backend .

# Push to Google Container Registry
docker push gcr.io/your-project-id/cttick-backend

# Deploy to Cloud Run
gcloud run deploy cttick-backend \
  --image gcr.io/your-project-id/cttick-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars FIREBASE_PROJECT_ID=your-project-id \
  --set-env-vars FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com \
  --set-env-vars FIREBASE_CREDENTIALS_PATH=/app/firebase-credentials.json
```

#### Set Secrets

```bash
# Create secret for Firebase credentials
gcloud secrets create firebase-credentials --data-file=firebase-credentials.json

# Grant Cloud Run access to secret
gcloud secrets add-iam-policy-binding firebase-credentials \
  --member=serviceAccount:your-service-account@your-project-id.iam.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

### Option 2: VM Deployment

#### Setup VM

```bash
# Create VM instance
gcloud compute instances create cttick-backend \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=ubuntu-2004-lts \
  --image-project=ubuntu-os-cloud

# SSH to VM
gcloud compute ssh cttick-backend --zone=us-central1-a
```

#### Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python
sudo apt install python3.10 python3-pip -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y
```

#### Deploy Application

```bash
# Clone repository
git clone https://github.com/your-org/MorphoVue.git
cd MorphoVue

# Copy Firebase credentials
scp firebase-credentials.json user@vm-ip:~/MorphoVue/backend/

# Start services
cd docker
cp .env.example .env
# Edit .env with your values

docker-compose up -d

# Check status
docker-compose ps
docker-compose logs -f
```

## Label Studio Deployment

### Option 1: Cloud Run

```bash
# Deploy Label Studio container
gcloud run deploy cttick-labelstudio \
  --image heartexlabs/label-studio:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars LABEL_STUDIO_HOST=https://your-labelstudio-url.run.app
```

### Option 2: Separate VM

```bash
# Create VM
gcloud compute instances create cttick-labelstudio \
  --zone=us-central1-a \
  --machine-type=e2-small

# SSH and install
gcloud compute ssh cttick-labelstudio

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Run Label Studio
docker run -d -p 8080:8080 \
  -v label-studio-data:/label-studio/data \
  --name label-studio \
  heartexlabs/label-studio:latest

# Configure firewall
gcloud compute firewall-rules create allow-labelstudio \
  --allow tcp:8080 \
  --source-ranges 0.0.0.0/0
```

## Frontend Deployment

### Build React App

```bash
cd frontend

# Install dependencies
npm install

# Create production build
cp .env.example .env
# Edit .env with production values

npm run build

# Build output is in frontend/build/
```

### Deploy to Firebase Hosting

```bash
# From project root
cd firebase

# Update firebase.json to point to frontend build
# (Already configured in provided firebase.json)

# Deploy
firebase deploy --only hosting

# Your app will be available at:
# https://your-project-id.web.app
# or
# https://your-project-id.firebaseapp.com
```

### Custom Domain (Optional)

```bash
# Add custom domain
firebase hosting:channel:deploy production --only=hosting

# Follow instructions to verify domain
# Add DNS records as instructed
```

## Environment Variables

### Backend (.env)

```bash
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
LABEL_STUDIO_URL=https://your-labelstudio-url.run.app
KAMIAK_JOB_TEMPLATE_PATH=../ml-pipeline/job_template.sh
CORS_ORIGINS=https://your-project-id.web.app,https://yourdomain.com
```

### Frontend (.env)

```bash
REACT_APP_API_URL=https://cttick-backend-xxxxx.run.app
REACT_APP_FIREBASE_API_KEY=your-api-key
REACT_APP_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=your-project-id
REACT_APP_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
REACT_APP_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
REACT_APP_FIREBASE_APP_ID=your-app-id
REACT_APP_LABEL_STUDIO_URL=https://your-labelstudio-url.run.app
```

Get Firebase config:
1. Go to Project Settings → General
2. Scroll to "Your apps"
3. Select Web app or create one
4. Copy configuration values

## SSL/TLS Certificates

### Firebase Hosting
- Automatic SSL certificates
- No configuration needed

### Cloud Run
- Automatic SSL certificates
- No configuration needed

### Custom VM
Use Let's Encrypt:

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Install Nginx
sudo apt install nginx -y

# Configure Nginx (see below)

# Get certificate
sudo certbot --nginx -d yourdomain.com
```

Nginx configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }
}
```

## Database Backup

### Firestore Backup

```bash
# Enable Firestore backup
gcloud firestore databases backup-schedules create \
  --database='(default)' \
  --recurrence=daily \
  --retention=7d

# Manual backup
gcloud firestore export gs://your-project-id-backup/$(date +%Y%m%d)
```

### Storage Backup

```bash
# Create backup bucket
gsutil mb gs://your-project-id-backup

# Copy Storage contents
gsutil -m rsync -r gs://your-project-id.appspot.com gs://your-project-id-backup
```

## Monitoring and Logging

### Enable Cloud Monitoring

```bash
# Cloud Run automatically logs to Cloud Logging
# View logs:
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=cttick-backend" --limit 50
```

### Set Up Alerts

1. Go to Cloud Console → Monitoring → Alerting
2. Create alerts for:
   - High error rate
   - High latency
   - Resource exhaustion

### Application Performance

Add monitoring to FastAPI:
```python
# backend/app/main.py
from google.cloud import logging

client = logging.Client()
client.setup_logging()
```

## Scaling

### Cloud Run Auto-scaling

```bash
# Configure auto-scaling
gcloud run services update cttick-backend \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 80
```

### Firestore Scaling
- Firestore automatically scales
- Monitor usage in Firebase Console

### Storage Scaling
- Cloud Storage automatically scales
- Monitor usage and costs

## Cost Optimization

### Estimated Monthly Costs

**Firebase Blaze Plan:**
- Firestore: $0.06 per 100K reads
- Storage: $0.026 per GB/month
- Bandwidth: $0.12 per GB

**Cloud Run:**
- $0.00002400 per vCPU-second
- $0.00000250 per GiB-second
- First 2 million requests free

**Typical Usage (100 scans/month):**
- Cloud Run: ~$10-20/month
- Firebase: ~$5-10/month
- Total: ~$15-30/month

### Cost Saving Tips

1. **Clean up old data**:
   ```bash
   # Delete old scans
   firebase firestore:delete --collection scans --where "created_at < timestamp"
   ```

2. **Use Cloud Run min instances carefully**:
   - Set to 0 for development
   - Set to 1+ for production (faster cold starts)

3. **Optimize storage**:
   - Delete processed scans after analysis
   - Use lifecycle policies

## Security

### Firestore Security Rules
Already configured in `firebase/firestore.rules`

### Storage Security Rules
Already configured in `firebase/storage.rules`

### API Security

```bash
# Add API key authentication (optional)
# In backend/app/main.py:
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

@app.get("/api/secure")
async def secure_endpoint(api_key: str = Depends(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    return {"message": "Authorized"}
```

### Secrets Management

```bash
# Store secrets in Google Secret Manager
gcloud secrets create api-key --data-file=-
# Enter secret and press Ctrl+D

# Access in Cloud Run
gcloud run services update cttick-backend \
  --update-secrets API_KEY=api-key:latest
```

## CI/CD Pipeline

### GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v0
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}
      
      - name: Build and Push
        run: |
          cd backend
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/cttick-backend .
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/cttick-backend
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy cttick-backend \
            --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/cttick-backend \
            --platform managed \
            --region us-central1

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Setup Node
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      
      - name: Build
        run: |
          cd frontend
          npm install
          npm run build
      
      - name: Deploy to Firebase
        uses: FirebaseExtended/action-hosting-deploy@v0
        with:
          repoToken: '${{ secrets.GITHUB_TOKEN }}'
          firebaseServiceAccount: '${{ secrets.FIREBASE_SERVICE_ACCOUNT }}'
          channelId: live
          projectId: ${{ secrets.FIREBASE_PROJECT_ID }}
```

## Post-Deployment

### 1. Create First User

```bash
# Using Firebase Console
# Go to Authentication → Users → Add User
# Or use frontend to register
```

### 2. Test Endpoints

```bash
# Health check
curl https://cttick-backend-xxxxx.run.app/api/health

# Frontend
open https://your-project-id.web.app
```

### 3. Configure Label Studio

1. Open Label Studio URL
2. Create account
3. Create project
4. Configure Cloud Storage connector:
   - Type: Google Cloud Storage
   - Bucket: your-project-id.appspot.com
   - Prefix: label-studio/

### 4. Setup Kamiak

Follow [Kamiak Guide](./kamiak-guide.md)

## Rollback

### Cloud Run

```bash
# List revisions
gcloud run revisions list --service cttick-backend

# Rollback to previous revision
gcloud run services update-traffic cttick-backend \
  --to-revisions REVISION_NAME=100
```

### Firebase Hosting

```bash
# List releases
firebase hosting:releases:list

# Rollback
firebase hosting:rollback
```

## Maintenance

### Regular Tasks

**Daily:**
- Check Cloud Run logs
- Monitor error rates

**Weekly:**
- Review Firestore usage
- Check storage costs
- Test backup restoration

**Monthly:**
- Update dependencies
- Review security rules
- Clean up old data
- Check for CVEs

### Update Dependencies

```bash
# Backend
cd backend
pip list --outdated
pip install --upgrade <package>

# Frontend
cd frontend
npm outdated
npm update

# Test after updates
npm test
```

## Troubleshooting

### Cloud Run Issues

```bash
# View logs
gcloud logging tail "resource.type=cloud_run_revision"

# Check service status
gcloud run services describe cttick-backend

# Check recent deployments
gcloud run revisions list --service cttick-backend
```

### Firebase Issues

```bash
# Check indexes
firebase firestore:indexes

# View hosting status
firebase hosting:channel:list
```

## Support

- Firebase Support: https://firebase.google.com/support
- Google Cloud Support: https://cloud.google.com/support
- Project Issues: GitHub Issues

