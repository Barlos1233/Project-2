# Sprint 1 Planning

**Planning date:** 2026-10-30 (date of the README change recording the sprint plan)

**Scrum Master:** Carlos Viramontes (as named in the README)

**Other attendees:** Not recorded in the repository.

## Goal

Deliver the first student/vendor workflows for CampusEats: account registration and login, vendor listing creation, student browsing, and dietary/location filtering. The planned order follows the backlog dependencies.

## Sprint commitment

The README's release plan commits to 11 story points and lists 24 points remaining after Sprint 1. Its planned order is:

| Order | Story | Points in backlog estimate | Dependency |
|---|---|---:|---|
| 1 | US1 — Register and log in | 3 | None |
| 2 | US2 — Post a listing | 5 | US1 |
| 3 | US3 — Browse listings | 3 | US2 |
| 4 | US8 — Filter listings | 3 | US3 |
| **Total from estimates** |  | **14** |  |

**Planning discrepancy:** The README release-plan table records 11 points for this scope, but the listed story estimates add up to 14. The team capacity and its justification are also blank in the README. Confirm the intended estimates, sprint commitment, and capacity with the team before using the plan for burndown or velocity reporting.

## Dependencies and completion

The order above satisfies the documented dependencies: US2 follows US1, US3 follows US2, and US8 follows US3. A story should be considered done only after its acceptance criteria pass in the Docker Compose deployment, with the appropriate automated or manual test evidence recorded as described in the README.

## Planning evidence

The README contains this scope and order. The repository does not record the planning meeting's full attendance, capacity rationale, task assignments, or a usable task-board screenshot; those details are not inferred here.
