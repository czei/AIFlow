Fix Custom Claude Commands for this Project

THe documentation for writing custom / commands for claude code:
https://docs.anthropic.com/en/docs/claude-code/slash-commands



  1. Key Analysis Points

  Technical Reality:
  - Claude Code uses markdown prompts, not executable Python
  - My Python system is sophisticated but architecturally incompatible
  - The .project-state.json approach from Phase 1 works well
  - Existing markdown templates provide a solid foundation

  Implementation Complexity Assessment:
  - Pure markdown enhancement: Lower complexity, immediate compatibility
  - Hybrid approach: Medium complexity, maximum flexibility
  - Python-only approach: High complexity, incompatible with Claude Code

  2. Recommended Approach: Incremental Hybrid Strategy

  Phase 2A: Enhanced Markdown Prompts (Immediate)
  - Improve existing markdown templates with sophisticated instructions
  - Integrate .project-state.json state management into prompts
  - Add detailed workflow guidance and quality gates
  - Enhance existing commands (setup.md, status.md, etc.) with better logic

  Phase 2B: Optional Python Tools (Future)
  - Keep the Python modules as standalone development tools
  - Create optional integration points where prompts can reference Python analysis
  - Provide both approaches for different use cases

  3. Specific Implementation Plan

  Immediate Actions:
  1. Enhance setup.md - Add comprehensive project structure creation logic
  2. Improve status.md - Add rich progress reporting and state analysis
  3. Upgrade lifecycle commands - Better start/pause/resume/stop logic in markdown
  4. Strengthen state management - Better .project-state.json manipulation in prompts

  Future Options:
  - Keep Python tools available for power users or non-Claude Code environments
  - Create documentation showing both approaches
  - Allow gradual migration based on user preferences

  4. Critical Success Factors

      Only Use Acceptable Claude Code Command Syntax

	- Markdown format (.md extension)
	- YAML frontmatter for metadata:
	- allowed-tools: List of tools the command can use
	- description: Brief description of the command
	- argument-hint: The arguments expected for the slash command. Example: argument-hint: add [tagId] | remove [tagId] | list. This hint is shown to the user when auto-completing the slash command.
	- Dynamic content with bash commands (!) and file references (@)
	- Prompt instructions as the main content

  Must Address:
  - Work within Claude Code's prompt-based architecture
  - Only use allowed syntax
  - Leverage the successful .project-state.json foundation from Phase 1
  - Maintain simplicity while adding sophistication
  - Provide clear upgrade path from current system

  Risk Mitigation:
  - Start with proven markdown approach
  - Test each enhancement incrementally
  - Keep fallback to current working system
  - Document both simple and advanced usage patterns

  This approach respects Claude Code's architecture while preserving the valuable work done in the Python implementation for future use.
