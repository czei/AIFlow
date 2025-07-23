# Hook System Quick Reference

## Workflow Phases At a Glance

| Phase | Can Do | Cannot Do | Complete When |
|-------|--------|-----------|---------------|
| **Planning** | Read code, search, create todos | Write code, execute | Todo list created |
| **Implementation** | Everything | Nothing blocked | Code written |
| **Validation** | Run tests, read, minor edits | Create new files | Tests pass |
| **Review** | Read, analyze, create todos | Write code, execute | Review complete |
| **Refinement** | Edit existing files, test | Create new files | Issues addressed |
| **Integration** | Git ops, final tests | Write new code | Changes committed |

## Emergency Override

Add to any command to bypass workflow rules:
- `EMERGENCY: <command>`
- `HOTFIX: <command>`
- `CRITICAL: <command>`

## Key Commands

```bash
# Check current phase and progress
/user:project:status

# Pause workflow enforcement
/user:project:pause

# Resume workflow enforcement  
/user:project:resume

# Manually advance to next phase
/user:project:advance

# Diagnose issues
/user:project:doctor
```

## Common Scenarios

### "I need to write code but I'm in planning phase"
1. Complete planning by creating a todo list
2. The system will auto-advance to implementation

### "I'm stuck in a phase"
1. Check status to see requirements
2. Complete missing actions
3. Or use `/user:project:advance` to force advancement

### "Production is down!"
Use emergency override:
```bash
EMERGENCY: fix production issue
```

### "Tests are failing in validation"
- You can use Edit to fix issues
- You cannot create new files
- Focus on making existing tests pass

## Hook Responses

When a tool is blocked:
```json
{
  "decision": "block",
  "reason": "Planning phase: Complete requirements analysis",
  "suggestions": ["Read existing code", "Create todo list"]
}
```

## Quality Gates

Automatically tracked:
- ✅ `existing_tests` - Tests run successfully
- ✅ `compilation` - Build succeeds
- ✅ `lint` - Linting passes
- ✅ `review` - Code reviewed

## Troubleshooting

**Hooks not working?**
- Check: `.claude/settings.json` exists
- Run: `/user:project:doctor`

**Wrong phase?**
- Check: `/user:project:status`
- Fix: Complete required actions or advance manually

**Need to disable temporarily?**
- Run: `/user:project:pause`
- Remember to resume later!

## Remember

The workflow is designed to improve code quality through:
1. Thinking before coding (Planning)
2. Focused implementation (Implementation)
3. Thorough testing (Validation)
4. Quality review (Review)
5. Addressing feedback (Refinement)
6. Clean integration (Integration)

Trust the process - it prevents common mistakes and ensures high-quality output!