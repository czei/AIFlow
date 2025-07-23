---
allowed-tools: Bash(ls:*), Bash(cat:*), Bash(jq:*)
description: Manage project phases
argument-hint: list | show <phase>
---

# Project Phase - Manage Phases

List phases or show specific phase details.

!`if [ "$ARGUMENTS" = "list" ] || [ -z "$ARGUMENTS" ]; then ls -1 phases/*.md 2>/dev/null | sed 's/phases\///' | sed 's/\.md//' | sort; elif [[ "$ARGUMENTS" =~ ^show ]]; then phase=$(echo "$ARGUMENTS" | sed 's/show //'); cat "phases/${phase}.md" 2>/dev/null || echo "❌ Phase not found: $phase"; else echo "Usage: /user:project:phase list | show <phase>"; fi`