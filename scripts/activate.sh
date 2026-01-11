#!/bin/bash
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "Python: $(python --version)"
echo "Pip: $(pip --version)"
echo ""
echo "💡 To deactivate: type 'deactivate'"
