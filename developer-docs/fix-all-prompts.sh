#!/bin/bash
# Fix all consolidated prompts to use plain text formatting instead of markdown

set -e

FORMATTING_HEADER='IMPORTANT FORMATTING INSTRUCTIONS:
- Format your response as clean, readable text suitable for NotebookLM notes
- Use clear section headers (not markdown ## headers)
- Use simple dashes (-) for bullet points, NOT asterisks (*)
- For emphasis, use ALL CAPS or underscores, NOT **bold** markdown
- Use blank lines generously to separate sections
- Number items clearly: 1. 2. 3. etc.
- Keep formatting minimal and professional

═══════════════════════════════════════════════════════════════════════
'

echo "Backing up original prompts..."
for file in chat_prompt_consolidated_*.txt; do
    if [ -f "$file" ]; then
        cp "$file" "$file.backup.$(date +%Y%m%d)"
        echo "  Backed up: $file"
    fi
done

echo
echo "Adding formatting instructions to prompts..."

# Function to add formatting header after first line
add_formatting() {
    local file=$1
    local temp=$(mktemp)

    # Read first line
    head -1 "$file" > "$temp"
    # Add blank line and formatting header
    echo "" >> "$temp"
    echo "$FORMATTING_HEADER" >> "$temp"
    # Add rest of file (skip first line)
    tail -n +2 "$file" >> "$temp"

    # Replace original
    mv "$temp" "$file"
    echo "  Updated: $file"
}

# Update all consolidated prompts
for file in chat_prompt_consolidated_01.txt \
            chat_prompt_consolidated_02.txt \
            chat_prompt_consolidated_03.txt \
            chat_prompt_consolidated_05.txt \
            chat_prompt_consolidated_06.txt; do
    if [ -f "$file" ]; then
        # Check if already updated
        if grep -q "IMPORTANT FORMATTING INSTRUCTIONS" "$file"; then
            echo "  Skipped (already updated): $file"
        else
            add_formatting "$file"
        fi
    fi
done

echo
echo "✅ All prompts updated!"
echo
echo "Prompts with formatting instructions:"
grep -l "IMPORTANT FORMATTING INSTRUCTIONS" chat_prompt_consolidated_*.txt

echo
echo "To revert changes, restore from backups:"
echo "  for f in chat_prompt_consolidated_*.txt.backup.*; do"
echo "    mv \"\$f\" \"\${f%.backup.*}\""
echo "  done"
