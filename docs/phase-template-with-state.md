# Phase Template with State Tracking

## Phase File Structure
Each phase file should include state tracking sections:

```markdown
# Phase 03: Implementation

## Status: IN_PROGRESS
## Started: 2025-07-21T09:00:00Z  
## Last Updated: 2025-07-21T15:30:00Z
## Completion: 62% (5 of 8 objectives)

## Prerequisites: 
- [x] Phase 02 (Architecture) COMPLETE
- [x] Database schema finalized
- [x] API specifications defined

## Objectives:
<!-- Each objective tracks completion status and timestamp -->
- [x] Database layer implementation 
  - Completed: 2025-07-21T10:15:00Z
  - Notes: Optimized queries, 40% performance improvement
- [x] User authentication system
  - Completed: 2025-07-21T12:45:00Z  
  - Notes: JWT implementation, password hashing with bcrypt
- [x] Core API endpoints (users, auth)
  - Completed: 2025-07-21T14:20:00Z
  - Notes: Full CRUD operations, input validation
- [ ] Business logic API endpoints
  - Progress: 3 of 6 endpoints complete
  - Working on: payment processing endpoint
- [ ] Error handling and validation
  - Status: Pending core endpoints completion
- [ ] API documentation  
  - Status: Partially complete, needs business logic docs
- [ ] Integration tests
  - Status: Test framework set up, writing test cases

## Success Criteria:
- [x] All API endpoints functional (5 of 8 complete)
- [ ] Comprehensive error handling implemented
- [ ] API documentation complete and accurate  
- [ ] Integration test suite passing (>90% coverage)

## Progress Log:
- 2025-07-21T15:30: Payment endpoint implemented, needs testing
- 2025-07-21T14:20: Auth middleware code review completed  
- 2025-07-21T12:45: Database optimization completed
- 2025-07-21T10:15: Core database layer finished

## Next Phase Trigger:
- All objectives marked [x] complete
- Integration tests passing
- Code review completed for all new code
- Documentation updated

## Automation Notes:
- Current focus: Business logic endpoints
- Estimated completion: 1.5 days remaining
- Blocking issues: None currently
- Manual intervention needed: No
```

## State Update Integration Points

1. **Beginning of each automation cycle**: Read state for context
2. **After each work session**: Update progress and notes  
3. **Task completion**: Mark objectives complete with timestamps
4. **Phase transition**: Update master state and advance to next phase
5. **Manual intervention**: Use `/user:project:update` for corrections

The `/user:project:update` command becomes the central hub for maintaining this state synchronization, ensuring that both automated and manual updates keep all files consistent.

This gives Claude reliable state to reference throughout the automation, preventing the "forgets where it is" problem you mentioned.
