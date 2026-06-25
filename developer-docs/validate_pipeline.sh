#!/bin/bash
################################################################################
# Pipeline Validation Script
# Runs the pipeline and validates results
################################################################################

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "================================================================================"
echo "PROJECT APE - PIPELINE VALIDATION"
echo "================================================================================"
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != *".project-ape-venv"* ]]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source ~/.project-ape-venv/bin/activate
fi

# Check NotebookLM authentication
echo -e "${BLUE}Checking NotebookLM authentication...${NC}"
notebooklm status 2>&1 | head -3
echo ""

# Clean up old status and logs
echo -e "${BLUE}Cleaning up old status files and logs...${NC}"
rm -rf .multi_process_status/*.json 2>/dev/null || true
rm -rf logs/*.log 2>/dev/null || true
echo "  ✅ Clean slate ready"
echo ""

# Show configuration
echo -e "${BLUE}Current configuration:${NC}"
python3 << 'EOF'
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("config", Path("vars.py"))
config = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config)

print(f"  Clients: {config.clients}")
print(f"  Mode: {config.default_mode}")
print(f"  Persona: {config.persona}")
EOF
echo ""

# Ask for confirmation
read -p "Run pipeline test? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "================================================================================"
echo "STARTING PIPELINE - Expected duration: 24-40 minutes"
echo "================================================================================"
echo ""

# Run the pipeline
START_TIME=$(date +%s)
python3 main.py --mode fast --clients merck_test blue_yonder_test

# Calculate duration
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
MINUTES=$((DURATION / 60))
SECONDS=$((DURATION % 60))

echo ""
echo "================================================================================"
echo "PIPELINE COMPLETE - Duration: ${MINUTES}m ${SECONDS}s"
echo "================================================================================"
echo ""

# Check results
echo -e "${BLUE}Validation Results:${NC}"
echo ""

# Check exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ Exit code: 0 (success)${NC}"
else
    echo -e "${RED}❌ Exit code: $EXIT_CODE (failure)${NC}"
fi
echo ""

# Check status files
echo "Client Status:"
for client in merck_test blue_yonder_test; do
    if [ -f ".multi_process_status/${client}.json" ]; then
        STATUS=$(python3 -c "import json; data=json.load(open('.multi_process_status/${client}.json')); print(data.get('status', 'UNKNOWN'))")
        QUALITY=$(python3 -c "import json; data=json.load(open('.multi_process_status/${client}.json')); print(data.get('quality_score', 'N/A'))")
        NAME=$(python3 -c "import json; data=json.load(open('.multi_process_status/${client}.json')); print(data.get('name', client))")

        if [ "$STATUS" == "COMPLETE" ]; then
            echo -e "  ${GREEN}✅ $NAME: $STATUS (Quality: $QUALITY/10)${NC}"
        else
            echo -e "  ${RED}❌ $NAME: $STATUS${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  ${client}: No status file found${NC}"
    fi
done
echo ""

# Check logs
echo "Log Files:"
for client in merck_test blue_yonder_test; do
    if [ -f "logs/${client}.log" ]; then
        if grep -q "Pipeline completed successfully" "logs/${client}.log"; then
            echo -e "  ${GREEN}✅ logs/${client}.log - Completed successfully${NC}"
        else
            echo -e "  ${YELLOW}⚠️  logs/${client}.log - Check for errors${NC}"
            echo "     Last 5 lines:"
            tail -5 "logs/${client}.log" | sed 's/^/       /'
        fi
    else
        echo -e "  ${RED}❌ logs/${client}.log - Not found${NC}"
    fi
done
echo ""

# Summary
echo "================================================================================"
echo "SUMMARY"
echo "================================================================================"
echo ""
echo "To view detailed logs:"
echo "  tail -f logs/merck_test.log"
echo "  tail -f logs/blue_yonder_test.log"
echo ""
echo "To view status files:"
echo "  cat .multi_process_status/merck_test.json | python3 -m json.tool"
echo "  cat .multi_process_status/blue_yonder_test.json | python3 -m json.tool"
echo ""
echo "Dashboard URL (if enabled):"
echo "  http://localhost:8765"
echo ""

exit $EXIT_CODE
