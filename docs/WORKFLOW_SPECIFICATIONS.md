# Sprint-Driven Development Workflow Specifications

This document defines the detailed workflows that Claude Code automation follows during each sprint of development.

## Universal Workflow Pattern

Every development user story follows this story lifecycle regardless of sprint:

### Step 1: Planning
- **Context Review**: Read current user story, acceptance criteria, and dependencies
- **Task Breakdown**: Decompose user story into specific, actionable implementation tasks
- **Risk Assessment**: Identify potential blockers, dependencies, or technical challenges
- **Approach Design**: Plan implementation approach following project architecture
- **Test Strategy**: Define how the user story will be validated and tested
- **Success Definition**: Clarify what "complete" means for this specific user story

### Step 2: Implementation  
- **Code Development**: Write production-quality code following established patterns
- **Architecture Compliance**: Ensure new code aligns with project architecture decisions
- **Error Handling**: Implement comprehensive error handling and edge case management
- **Documentation**: Add inline comments and documentation for complex logic
- **Standards Adherence**: Follow project coding standards, naming conventions, and practices

### Step 3: Validation
- **Compilation Check**: Verify code compiles without errors or warnings
- **Existing Test Suite**: Run full existing test suite to prevent regressions
- **New Unit Tests**: Write comprehensive unit tests for new functionality (>90% coverage)
- **Integration Tests**: Execute relevant integration tests for affected components  
- **Manual Testing**: Perform basic smoke testing and edge case validation
- **Performance Check**: Validate performance meets established benchmarks
- **Security Review**: Check for common security issues and vulnerabilities

### Step 4: Review
- **Self Review**: Conduct thorough self-review of all changes
- **Zen Code Review**: Submit to zen methodology for comprehensive analysis:
  - Logic correctness and algorithm efficiency
  - Edge case handling and error conditions  
  - Code organization, readability, and maintainability
  - Security implications and vulnerability assessment
  - Performance characteristics and optimization opportunities
  - Test coverage adequacy and quality
  - Documentation completeness and accuracy
- **Architectural Review**: Verify changes align with system architecture
- **Standards Compliance**: Confirm adherence to project coding standards

### Step 5: Refinement
- **Issue Resolution**: Address all issues identified during code review
- **Code Quality Improvement**: Implement suggested improvements and optimizations
- **Test Enhancement**: Improve or expand tests based on review feedback
- **Documentation Updates**: Enhance documentation based on review suggestions
- **Regression Testing**: Re-run full test suite after implementing changes
- **Validation Confirmation**: Verify all review issues have been properly addressed

### Step 6: Integration
- **Final Testing**: Execute complete test suite including new and existing tests
- **Documentation Update**: Update project documentation, README, API docs as needed
- **Commit Preparation**: Create clean, descriptive commit with clear message
- **Progress Update**: Update project state and sprint progress tracking
- **Handoff Preparation**: Ensure work is ready for next user story or sprint transition

## Sprint-Specific Workflow Variations

### Planning Sprint Workflow
**Focus**: Project definition, requirements analysis, and approach design

**Planning Step**: 
- Gather and analyze requirements
- Research technical approaches and alternatives
- Define project scope and boundaries

**Implementation Step**:
- Create project specification documents
- Design system architecture diagrams  
- Define development sprints and milestones

**Validation Step**:
- Review specifications for completeness
- Validate architecture against requirements
- Confirm feasibility of planned approach

**Review Step**:
- Stakeholder review of specifications
- Technical review of architecture decisions
- Risk assessment and mitigation planning

**Refinement Step**:
- Address specification gaps or issues
- Refine architecture based on feedback
- Adjust project sprints based on findings

**Integration Step**:
- Finalize project documentation
- Create initial project structure
- Set up development environment

### Architecture Sprint Workflow  
**Focus**: System design, technology selection, and component definitions

**Planning Step**:
- Review requirements and constraints
- Research technology options and patterns
- Plan system component interactions

**Implementation Step**:
- Design system architecture and component interfaces
- Create data models and database schemas
- Define API specifications and contracts
- Set up project structure and build systems

**Validation Step**:
- Validate architecture against requirements
- Verify technology choices are appropriate
- Test build and deployment configurations
- Confirm component interfaces are well-defined

**Review Step**:
- Architectural review for scalability and maintainability
- Technology stack validation
- Security architecture assessment
- Performance and scalability analysis

**Refinement Step**:
- Address architectural issues or gaps
- Refine component interfaces and contracts
- Optimize technology stack decisions
- Improve build and deployment configurations

**Integration Step**:
- Finalize architecture documentation
- Set up development environment
- Create project skeleton with chosen technologies
- Prepare for implementation sprint

### Implementation Sprint Workflow
**Focus**: Feature development, coding, and core functionality creation

**Planning Step**:
- Review feature requirements and acceptance criteria
- Plan implementation approach and component interactions
- Identify dependencies and integration points

**Implementation Step**:
- Write production-quality feature code
- Implement business logic and algorithms
- Create user interfaces and API endpoints
- Add error handling and logging

**Validation Step**:
- Compile and build verification  
- Unit test development and execution
- Integration testing with existing components
- Manual feature testing and validation

**Review Step**:
- Code quality and style review
- Logic correctness and algorithm efficiency
- Security vulnerability assessment
- Performance and optimization review

**Refinement Step**:
- Fix identified issues and bugs
- Optimize performance bottlenecks
- Enhance error handling and edge cases
- Improve code clarity and maintainability

**Integration Step**:
- Merge feature code into main codebase
- Update documentation and API specifications
- Create comprehensive commit messages
- Update project progress tracking

### Testing Sprint Workflow
**Focus**: Quality assurance, test coverage, and bug identification/resolution

**Planning Step**:
- Define comprehensive testing strategy
- Identify test scenarios and edge cases
- Plan test automation and manual testing approach

**Implementation Step**:
- Develop comprehensive test suites
- Create automated integration and end-to-end tests
- Implement performance and load testing
- Set up continuous testing infrastructure

**Validation Step**:
- Execute full test suite with coverage analysis
- Perform manual testing of critical user journeys
- Conduct performance and load testing
- Validate security and penetration testing

**Review Step**:
- Test coverage and quality assessment
- Test strategy effectiveness evaluation
- Bug triage and priority assignment
- Quality metrics and acceptance criteria review

**Refinement Step**:
- Fix identified bugs and issues
- Improve test coverage for gaps
- Optimize test execution performance
- Enhance test documentation and maintainability

**Integration Step**:
- Finalize test suite and automation
- Document testing procedures and results
- Create quality assurance reports
- Prepare for deployment or next sprint

### Deployment Sprint Workflow
**Focus**: Production preparation, deployment automation, and release management

**Planning Step**:
- Plan deployment strategy and rollback procedures
- Define production environment requirements
- Identify deployment dependencies and risks

**Implementation Step**:
- Create deployment automation and scripts
- Configure production environments
- Implement monitoring and alerting systems
- Set up backup and disaster recovery procedures

**Validation Step**:
- Test deployment procedures in staging environment
- Validate production environment configuration
- Verify monitoring and alerting functionality
- Confirm backup and recovery procedures work

**Review Step**:
- Deployment readiness assessment
- Security and compliance validation
- Performance and scalability verification
- Documentation and runbook review

**Refinement Step**:
- Address deployment issues and gaps
- Optimize deployment automation
- Enhance monitoring and alerting
- Improve documentation and procedures

**Integration Step**:
- Execute production deployment
- Monitor system health and performance
- Document deployment results and lessons learned
- Transition to maintenance and support sprint

## Acceptance Criteria and Success Criteria

### Universal Acceptance Criteria
Every user story must pass these gates:

1. **Compilation Gate**: All code compiles without errors or warnings
2. **Test Gate**: Full test suite passes with >90% coverage for new code
3. **Review Gate**: Code review completed with all critical issues resolved  
4. **Integration Gate**: Changes integrate cleanly with existing system
5. **Documentation Gate**: All changes properly documented
6. **Performance Gate**: Performance benchmarks met or justified exceptions

### Sprint-Specific Success Criteria

**Planning Sprint**: Requirements complete, architecture designed, project scoped
**Architecture Sprint**: System design finalized, technologies selected, skeleton created
**Implementation Sprint**: Features complete, tested, reviewed, and integrated
**Testing Sprint**: Comprehensive test coverage, bugs identified and resolved
**Deployment Sprint**: Production-ready system deployed and monitored

## Automation Integration

### Stop Hook Integration
The automation system should reference this workflow specification:
- Read current sprint and user story from project state
- Follow appropriate sprint workflow for current user story
- Validate completion against sprint-specific success criteria
- Update progress only when acceptance criteria are satisfied
- Escalate to human intervention when workflows cannot be completed

### State Management Integration
- Track workflow position within each user story (which of the 6 steps)
- Record quality gate passage for audit trail
- Maintain detailed progress notes with validation results
- Enable resumption from any point in the workflow

This comprehensive workflow specification ensures consistent, high-quality development regardless of project type or complexity while providing the detailed guidance Claude Code needs for effective automation.
