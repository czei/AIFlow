---
allowed-tools: Bash(ls:*), Bash(cat:*), Bash(jq:*)
description: Manage project sprints
argument-hint: list | show <sprint>
---

# Project Sprint - Manage Sprints

List sprints or show specific sprint details.

!`if [ "$ARGUMENTS" = "list" ] || [ -z "$ARGUMENTS" ]; then ls -1 sprints/*.md 2>/dev/null | sed 's/sprints\///' | sed 's/\.md//' | sort; elif [[ "$ARGUMENTS" =~ ^show ]]; then sprint=$(echo "$ARGUMENTS" | sed 's/show //'); cat "sprints/${sprint}.md" 2>/dev/null || echo "❌ Sprint not found: $sprint"; else echo "Usage: /user:project:sprint list | show <sprint>"; fi`