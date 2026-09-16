#!/bin/bash
TASKS_FILE="$HOME/.local/share/tasks/tasks.txt"

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "Hello, $USER. Good day today?"

if [ -f "$TASKS_FILE" ]; then
    echo ""
    echo "📋 Here's your TODO list:"
    echo "-----------------"
    display_num=1
    found_task=false
    while IFS= read -r line; do
        if [[ "$line" == \#* ]]; then
            continue  # skip comments
        elif [[ "$line" == \[x\]* ]]; then
            continue  # skip completed tasks
        elif [[ "$line" == \[\ \]* ]]; then
            task_text="${line#\[ \] }"
            echo -e "${display_num}. ${task_text}${NC}"
            found_task=true
            ((display_num++))
        elif [[ -n "$line" ]]; then
            echo "${display_num}. ${line}"
            found_task=true
            ((display_num++))
        fi
    done < "$TASKS_FILE"
    if [ "$found_task" = false ]; then
        echo "No tasks in sight. Good job."
    fi
    echo ""
else
    echo ""
    echo "Task file not found. There should be a file at ~/.local/share/tasks/tasks.txt for details."
    echo ""
fi

echo "Use the command 'taskmaster' to edit your tasks."
read -p "Press Enter to continue."

exec bash
