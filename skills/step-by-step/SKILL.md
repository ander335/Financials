---
name: step-by-step
description: Must be used when AI agent creates or updates AI-facing files, including AI documentation, Markdown instructions, command guides, agent definitions, prompts, skills, plugins, MCP/tool instructions, or automation instructions. Use whenever work changes files that guide AI behavior or operational commands.
---

# Step By Step
Use this skill as an approval gate for AI-facing edits.

## Workflow
1. Split the target content into logical blocks.
2. A logical block is the smallest meaningful unit the user can review on its own: frontmatter, one section, one rule group, one script function, or one config entry.
3. Keep blocks small; typically 3-5 lines of content, but longer when the idea cannot be split cleanly.
4. Show exactly one logical block and ask for approval before editing it.
5. After editing, propose the next logical block.
6. Repeat until the file is complete or the user stops.

## Approval Requests
Keep each request short and specific:
- Show the exact logical block to add, replace, or delete.
- Ask a clear yes/no approval question.

Do not ask for approval of an outline, plan, full file, or broad editing step.
Do not merge unrelated logical blocks into one approval.

## Scope
Treat these as AI-facing files:

- `*.md` documentation that instructs AI or humans how to operate AI workflows.
- `SKILL.md` files and skill metadata.
- Agent, assistant, prompt, plugin, MCP, command, policy, or instruction files.
- Scripts or config whose main purpose is to direct AI behavior or tool execution.

If unsure whether a file is AI-facing, ask before editing.
