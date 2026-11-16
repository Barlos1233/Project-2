# Sprint 3 Retrospective

**Date/time:** 11-10-26

**Participants:** Team

## Previous sprint actions

Sprint 2's retrospective listed these follow-ups. Their status is assessed
against the repository evidence available for Sprint 3:

| Sprint 2 action | Status | Evidence |
|---|---|---|
| Reconcile remaining backlog points, team capacity, release scope, and burndown. | Partially completed in this branch. | 38 points are planned; optional US9 (5 points) is excluded from scope. Team capacity and actual burndown still need team confirmation. |
| Record actual planning, daily-scrum, review, and retrospective dates, attendees, decisions, and blockers. | Partially completed. | Sprint 3 planning, review, retrospective summaries, and dated daily entries are present. Verify recorded event dates and attendees; the daily entries do not capture a complete discussion/action record. |
| Add US7 manual results and complete required regression tests in Docker Compose. | Partially completed. | US7 manual checks are recorded on 2026-11-12 and 2026-11-15, including successful pickup, rejection cases, pickup-window enforcement, no-show display, and vendor-only access. Ensure any remaining required cases are tested against the deployed app. |
| Replace the board placeholder with a dated screenshot and maintain the board. | Partially completed. | A sprint-tracker screenshot was added to `board.png`; a single snapshot does not show progress throughout the sprint. |

## What went well

- US5 has focused automated tests and manual results recorded as passed on
  2026-11-13.
- US10 implementation and manual results are present; the results were added
  on 2026-11-14.
- The Selenium US2 browser test passed against the Compose app on 2026-11-15.

## What could improve

- Keep US3's sort-order evidence aligned with the implementation: the browse
  route orders listings by pickup-window end, soonest first. Manual-test
  records dated 2026-11-10 and 2026-11-15 report this criterion passed.
- Sprint estimates, capacity, release scope, and burndown have not been
  reconciled.
- US7 manual acceptance evidence and actual Sprint 3 event notes are still
  missing. A single board screenshot does not document progress throughout
  the sprint.
- The manual log says US10 passed, but the 300-character comment limit was not
  tested.

## Actions

| Action | Owner | Due |
|---|---|---|
| Run the documented Selenium US2 test against the Compose stack and record its actual result. | Completed on this branch | 2026-11-15 |
| Keep optional US9 out of the project scope; it is excluded from the README and Sprint 3 plan. | Team | Recorded in the updated plan |
| Reconcile backlog estimates, sprint totals, team capacity, and burndown. | Team; specific owner not recorded | Before final submission |
| Complete missing US7 regression checks and test the US10 comment limit. | team | Before final submission |
| Record real event dates and attendees, and keep the sprint tracker updated at multiple points. | Scrum Master and team | At the actual events |
