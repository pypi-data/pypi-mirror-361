# AGENTS for `uubed` (Project Home)

This repository serves as the central hub for the `uubed` project, coordinating efforts across documentation, Python, and Rust sub-repositories.

## Role of this Repository:
- **Overall Project Management:** Contains the main `PROJECT.md`, `PLAN.md`, and `TODO.md` for the entire `uubed` initiative.
- **Cross-cutting Concerns:** Manages issues, high-level architectural decisions, and overall project progress.
- **Consolidated Documentation:** Provides a holistic view of the project's goals, status, and future direction.

## Key Agents and Their Focus:
- **Project Architect:** Oversees the entire `uubed` ecosystem, ensuring coherence and alignment across all sub-projects.
- **Ideot:** Brainstorms innovative solutions for the core encoding problem and overall project strategy.
- **Critin:** Critiques the project's direction, identifies potential pitfalls, and ensures robust decision-making at the highest level.

If you work with Python, use 'uv pip' instead of 'pip', and use 'uvx hatch test' instead of 'python -m pytest'. 

When I say /report, you must: Read all `./TODO.md` and `./PLAN.md` files and analyze recent changes. Document all changes in `./CHANGELOG.md`. From `./TODO.md` and `./PLAN.md` remove things that are done. Make sure that `./PLAN.md` contains a detailed, clear plan that discusses specifics, while `./TODO.md` is its flat simplified itemized `- [ ]`-prefixed representation. When I say /work, you must work in iterations like so: Read all `./TODO.md` and `./PLAN.md` files and reflect. Work on the tasks. Think, contemplate, research, reflect, refine, revise. Be careful, curious, vigilant, energetic. Verify your changes. Think aloud. Consult, research, reflect. Then update `./PLAN.md` and `./TODO.md` with tasks that will lead to improving the work you’ve just done. Then '/report', and then iterate again.