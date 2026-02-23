#!/bin/bash
# Deployment script for Phase 3 Backend to Hugging Face Spaces

echo "=== Deploying Phase 3 Backend to Hugging Face Spaces ==="
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

# Space configuration
SPACE_NAME="${HF_SPACE_NAME:-huz111/backend-chatbot}"

echo "Deploying to Space: $SPACE_NAME"
echo ""

# Navigate to repository root
cd /home/syedhuzaifa/Hackathon-2

# Configure git to use the token
git config credential.helper store
echo "https://huz111:${HF_TOKEN}@huggingface.co" > ~/.git-credentials

# Push to Space (subtree: only Phase-3/backend/ as root)
echo "Pushing Phase-3/backend to Space..."
git remote remove phase3-space 2>/dev/null || true
git remote add phase3-space https://huz111:${HF_TOKEN}@huggingface.co/spaces/${SPACE_NAME}
git push phase3-space $(git subtree split --prefix=Phase-3/backend main):main --force

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Deployment successful!"
    echo ""
    echo "Your Space: https://huggingface.co/spaces/${SPACE_NAME}"
    echo ""
    echo "Next steps:"
    echo "1. Go to: https://huggingface.co/spaces/${SPACE_NAME}/settings"
    echo "2. Add these environment variables:"
    echo "   - DATABASE_URL (Neon PostgreSQL connection string)"
    echo "   - BETTER_AUTH_URL (Your Phase 3 frontend URL)"
    echo "   - GROK_API_KEY (Your Grok API key)"
    echo "   - GROK_BASE_URL (https://api.x.ai/v1)"
    echo "   - GROK_MODEL (grok-3-mini)"
    echo "   - ALLOWED_ORIGINS (Comma-separated frontend URLs)"
    echo "   - PORT (7860 - HF Spaces default)"
    echo "3. Wait for the build to complete"
    echo "4. Test: curl https://huz111-backend-chatbot.hf.space/health/live"
else
    echo ""
    echo "✗ Deployment failed. Check the error above."
    exit 1
fi
