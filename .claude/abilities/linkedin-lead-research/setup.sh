#!/bin/bash
# Setup script for LinkedIn Lead Research Skill
# Makes the skill fully self-contained

set -e

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Setting up LinkedIn Lead Research Skill..."
echo "📁 Skill directory: $SKILL_DIR"

# Check if venv exists
if [ ! -d "$SKILL_DIR/venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv "$SKILL_DIR/venv"
else
    echo "✓ Virtual environment already exists"
fi

# Install dependencies
echo "📥 Installing Python dependencies..."
"$SKILL_DIR/venv/bin/pip" install --upgrade pip -q
"$SKILL_DIR/venv/bin/pip" install -r "$SKILL_DIR/requirements.txt" -q

# Check .env file
if [ ! -f "$SKILL_DIR/.env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Creating template .env file..."
    cat > "$SKILL_DIR/.env" << 'EOF'
# LinkedIn API Configuration
# RapidAPI professional-network-data key
RAPIDAPI_KEY=a45f6d315fmsh9421f84897ba7ddp15659fjsn3eb60906b0db
EOF
    echo "✓ Created .env file with default API key"
else
    echo "✓ .env file exists"
fi

# Make scripts executable
chmod +x "$SKILL_DIR/linkedin_api.py"

# Test the setup
echo ""
echo "🧪 Testing skill setup..."
if "$SKILL_DIR/venv/bin/python3" "$SKILL_DIR/linkedin_api.py" extract-username "https://linkedin.com/in/test" > /dev/null 2>&1; then
    echo "✅ Skill is working correctly!"
else
    echo "❌ Skill test failed. Please check the installation."
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Usage:"
echo "  # Using venv python directly:"
echo "  $SKILL_DIR/venv/bin/python3 $SKILL_DIR/linkedin_api.py <command> [args]"
echo ""
echo "  # Or activate venv first:"
echo "  source $SKILL_DIR/venv/bin/activate"
echo "  python3 linkedin_api.py <command> [args]"
echo ""
echo "Claude will automatically use this skill when you ask LinkedIn-related questions."
