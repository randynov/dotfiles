#!/bin/bash

set -euo pipefail

COWSAY_DIR="/opt/homebrew/Cellar/cowsay-org/3.8.3/share/cowsay/cows"
BOXES_CONFIG="/opt/homebrew/Cellar/boxes/2.3.1/share/boxes-config"
BACKUP_FILE="${BOXES_CONFIG}.bak.$(date +%Y%m%d_%H%M%S)"

echo "📦 Backing up original boxes config to: $BACKUP_FILE"
cp "$BOXES_CONFIG" "$BACKUP_FILE"

cow_files=("$COWSAY_DIR"/*.cow)
demo_cows=("${cow_files[@]:0:3}")

sanitize_box_name() {
    local raw_name="$1"
    echo "$raw_name" | sed 's/[^a-zA-Z0-9_-]/_/g'
}

echo "👀 Adding demo cows:"
for cowfile in "${demo_cows[@]}"; do
    base=$(basename "$cowfile" .cow)
    box_name=$(sanitize_box_name "$base")
    echo " → $base → BOX $box_name"

    # Remove any previous conflicting block
    sed -i '' "/^BOX $box_name$/,/^END $box_name$/d" "$BOXES_CONFIG"

    # Extract only the ASCII art
    art=$(awk '
        BEGIN { keep=0 }
        /^EOC/ { exit }
        /^\$the_cow/ { next }
        /^\$thoughts/ { next }
        /^\$/ { next }
        /^ *$/ { next }
        NR>1 { print "    " $0 }
    ' "$cowfile")

    {
        echo ""
        echo "BOX $box_name"
        echo 'author   "Cowsay.org"'
        echo 'tags     ("artwork", "box", "cowsay")'
        echo "sample"
        echo "$art"
        echo "ends"
        echo 'shapes { w ("|") e ("|") }'
        echo 'elastic (w, e)'
        echo "END $box_name"
    } >> "$BOXES_CONFIG"
done

echo -e "\n🔍 Validating boxes config..."

# Run boxes -l and capture stderr
validation_output=$(boxes -l 2>&1 >/dev/null)

if echo "$validation_output" | grep -qi "error\|syntax\|duplicate"; then
    echo "❌ Config has errors:"
    echo "$validation_output"
    echo "🔄 Restoring original config..."
    cp "$BACKUP_FILE" "$BOXES_CONFIG"
    echo "✅ Original config restored."
    exit 1
fi

echo -e "\n✅ Boxes config appears valid. Demo box names:"
demo_names=$(for f in "${demo_cows[@]}"; do sanitize_box_name "$(basename "$f" .cow)"; done | paste -sd'|' -)
boxes -l | grep -E "$demo_names"

echo -e "\n🎨 Rendering each new box with its own cow art:\n"
for cowfile in "${demo_cows[@]}"; do
    base=$(basename "$cowfile" .cow)
    box_name=$(sanitize_box_name "$base")

    echo "------------------ $box_name ------------------"

    # Extract just the cow ASCII art (not code)
    cow_art=$(awk '
        /^EOC/ { exit }
        /^\$the_cow/ || /^\$thoughts/ || /^\$/ { next }
        /^ *$/ { next }
        NR > 1 { print }
    ' "$cowfile")

    # Feed cow ASCII art into the new box style
    echo "$cow_art" | boxes -d "$box_name" || echo "❌ Failed to render $box_name"
    echo ""
done


echo -e "\n❓ Do you want to continue and add ALL cow files? (y/N)"
read -r answer
if [[ "$answer" != [Yy]* ]]; then
    echo "❌ Cancelled. Restoring original config..."
    cp "$BACKUP_FILE" "$BOXES_CONFIG"
    echo "🔄 Original config restored."
    exit 1
fi

echo "🚀 Adding all remaining cows..."
for cowfile in "${cow_files[@]:3}"; do
    base=$(basename "$cowfile" .cow)
    box_name=$(sanitize_box_name "$base")

    sed -i '' "/^BOX $box_name$/,/^END $box_name$/d" "$BOXES_CONFIG"

    art=$(awk '
        BEGIN { keep=0 }
        /^EOC/ { exit }
        /^\$the_cow/ { next }
        /^\$thoughts/ { next }
        /^\$/ { next }
        /^ *$/ { next }
        NR>1 { print "    " $0 }
    ' "$cowfile")

    {
        echo ""
        echo "BOX $box_name"
        echo 'author   "Cowsay.org"'
        echo 'tags     ("artwork", "box", "cowsay")'
        echo "sample"
        echo "$art"
        echo "ends"
        echo 'shapes { w ("|") e ("|") }'
        echo 'elastic (w, e)'
        echo "END $box_name"
    } >> "$BOXES_CONFIG"
done

echo "🎉 All cows successfully added. You can now use them with the \`boxes\` command!"
