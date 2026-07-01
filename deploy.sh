#!/bin/bash

echo "========================================================="
echo "🚀 DEPLOYING SLIDE EXPERT (GE / A2A PERFECT MODE)"
echo "========================================================="

# 1. Cloud Run への直接展開
echo "🤖 Step 1/2: Deploying container to Cloud Run..."
gcloud beta run deploy google-slide-agent \
  --project agentspace-469000 \
  --region us-east1 \
  --source . \
  --memory 4Gi \
  --no-allow-unauthenticated \
  --no-cpu-throttling \
  --min-instances 1 \
  --update-env-vars AGENT_VERSION=0.1.0,APP_URL=https://google-slide-agent-989491130286.us-east1.run.app \
  --labels created-by=adk \
  --quiet

# 2. 登録用トークンの取得
echo "🔑 Fetching access token for registration..."
TOKEN=$(gcloud auth application-default print-access-token 2>/dev/null || gcloud auth print-access-token)

# 3. Discovery Engine API への直接登録
echo "🤖 Step 2/2: Registering agent to Discovery Engine API..."
python3 register_agent.py "$TOKEN"

echo "========================================================="
echo "🎉 Perfect Deployment Complete!"
echo "========================================================="
