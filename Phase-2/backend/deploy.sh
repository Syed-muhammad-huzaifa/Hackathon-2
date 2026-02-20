#!/bin/bash
# Simple deployment script for HF Spaces

echo "=== Deploying to Hugging Face Spaces ==="
echo ""

# Check if token is set
if [ -z "$HF_TOKEN" ]; then
    echo "ERROR: HF_TOKEN environment variable not set"
    echo ""
    echo "Please follow these steps:"
    echo ""
    echo "1. Get your token from: https://huggingface.co/settings/tokens"
    echo "   (Create a new token with 'write' access if needed)"
    echo ""
    echo "2. Set the token and run this script:"
    echo "   export HF_TOKEN='your_token_here'"
    echo "   bash deploy.sh"
    echo ""
    exit 1
fi

# Navigate to backend directory
cd /home/syedhuzaifa/Hackathon-2/Phase-2/backend

# Configure git to use the token
git config credential.helper store
echo "https://huz111:${HF_TOKEN}@huggingface.co" > ~/.git-credentials

# Push to Space
echo "Pushing to Space..."
git remote remove space 2>/dev/null || true
git remote add space https://huggingface.co/spaces/huz111/backend-todo
git push space main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Deployment successful!"
    echo ""
    echo "Your Space: https://huggingface.co/spaces/huz111/backend-todo"
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://huggingface.co/spaces/huz111/backend-todo/settings"
    echo "2. Add these environment variables:"
    echo "   - DATABASE_URL"
    echo "   - BETTER_AUTH_SECRET"
    echo "   - BETTER_AUTH_URL"
    echo "   - ALLOWED_ORIGINS"
    echo "3. Wait for the build to complete"
    echo "4. Test: curl https://huz111-backend-todo.hf.space/health/live"
else
    echo ""
    echo "✗ Deployment failed. Check the error above."
    exit 1
fi
