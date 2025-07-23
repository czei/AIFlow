---
allowed-tools: Bash(test:*), Bash(git:*), Bash(jq:*), Bash(ls:*)
description: Validate project setup and configuration
---

# Project Doctor - Validate Setup

Validate project setup including git worktree and sprint configuration.

!`echo "🔍 PROJECT VALIDATION"`
!`echo "=================="`
!`[ -f ".project-state.json" ] && echo "✅ State file exists" || echo "❌ State file missing"`
!`[ -d ".git" ] && echo "✅ Git repository" || echo "❌ Not a git repository"`
!`git branch --show-current | grep -q "^feature/" && echo "✅ Feature branch" || echo "⚠️  Not on feature branch"`
!`[ -d "sprints" ] && echo "✅ Sprints directory exists" || echo "❌ Sprints directory missing"`
!`[ -f "CLAUDE.md" ] && echo "✅ CLAUDE.md exists" || echo "❌ CLAUDE.md missing"`
!`[ -f ".claude/settings.json" ] && echo "✅ Claude settings exist" || echo "⚠️  Claude settings missing"`
!`echo ""`
!`jq -r '. | if .project_name then "✅ Valid state structure" else "❌ Invalid state" end' .project-state.json 2>/dev/null || echo "❌ State file invalid"`
!`ls sprints/*.md 2>/dev/null | wc -l | xargs -I {} echo "📁 {} sprint files found"`
!`grep -q "TEMPLATE" sprints/*.md 2>/dev/null && echo "⚠️  Template text found in sprints" || echo "✅ Sprints customized"`

Run `/user:project:start` when ready to begin automated development.