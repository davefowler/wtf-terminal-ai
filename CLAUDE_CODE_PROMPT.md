# Initial Prompt for Claude Code

Copy this and paste it into Claude Code to get started:

---

I need you to implement `wtf` - a terminal AI assistant. All the specs are in this repo.

**Your mission:**
Implement all 32 tasks in `TASKS.md` to build wtf v0.1. Work through them in order, following the workflow instructions at the top of TASKS.md.

**Key files to read first:**
1. `SPEC.md` - Complete technical specification (5300+ lines, comprehensive)
2. `TASKS.md` - Your task list with 32 bite-sized implementation tasks

**How to proceed:**
1. Read SPEC.md to understand the full context of what we're building
2. Start with Milestone 1, Task 1
3. Complete each task according to its acceptance criteria
4. After finishing each MILESTONE, commit with format:
   ```
   feat: [MILESTONE NAME] - brief description
   
   - Task X: what was done
   - Task Y: what was done
   
   Milestone X/11 complete
   ```
5. Test after each milestone before moving to the next
6. Track your progress by saying "✅ Task X complete" after each task

**Git workflow:**
- Work on the `main` branch
- Commit after each completed milestone (not after each task)
- Push after testing each milestone
- Use the commit format specified above

**Important guidelines:**
- ✅ Stick to the spec - don't add features not specified
- ✅ Use type hints and docstrings
- ✅ Use `rich` library for all terminal output
- ✅ Handle errors gracefully
- ✅ Test after each milestone
- ❌ Don't commit broken code
- ❌ Don't skip tasks
- ❌ Don't make assumptions - check SPEC.md

**Expected dependencies:**
```
anthropic>=0.18.0
openai>=1.12.0
google-generativeai>=0.3.0
llm>=0.13.0
rich>=13.7.0
```

**The personality:**
This tool has a Gilfoyle/Marvin personality (dry, sardonic, helpful). Keep this consistent in all user-facing text, error messages, and help output.

**Ready?**
Start by reading SPEC.md to understand what we're building, then begin with Task 1: Initialize Python Project Structure.

Let me know when you've read the spec and you're ready to start Task 1.

