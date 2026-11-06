#!/usr/bin/env bash
# Automated Deployment Script for DealMind on Firebase & Google Cloud Run
# Run this inside Google Cloud Shell

set -e

PROJECT_ID=$1

if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: Please provide your Firebase/Google Cloud Project ID."
    echo "Usage: bash deploy_firebase.sh <YOUR_PROJECT_ID>"
    exit 1
fi

echo "============================================================"
echo "DEPLOYING DEALMIND TO FIREBASE (PROJECT: $PROJECT_ID)"
echo "============================================================"

echo "Step 1/4: Setting active Google Cloud project..."
gcloud config set project "$PROJECT_ID"

echo "Step 2/4: Enabling required Google Cloud APIs..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# Load keys from .env if present, otherwise prompt
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo "Step 3/4: Building container & deploying to Cloud Run..."
gcloud run deploy dealmind-agent \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars GROQ_API_KEY="$GROQ_API_KEY",HINDSIGHT_API_KEY="$HINDSIGHT_API_KEY",HINDSIGHT_BASE_URL="https://api.hindsight.vectorize.io"

echo "Step 4/4: Deploying Firebase Hosting rewrite..."
firebase use "$PROJECT_ID"
firebase deploy --only hosting

echo ""
echo "============================================================"
echo "🎉 SUCCESS: DealMind is live on Firebase Hosting!"
echo "Visit your site at: https://$PROJECT_ID.web.app"
echo "============================================================"
