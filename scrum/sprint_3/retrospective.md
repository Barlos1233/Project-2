# Sprint 3 Retrospective

**Date/time:** No retrospective meeting date or time is recorded in the
repository.

**Participants:** Not recorded.

## Previous sprint actions

Sprint 2's retrospective listed these follow-ups. Their status is assessed
against the repository evidence available for Sprint 3:

| Sprint 2 action | Status | Evidence |
|---|---|---|
| Reconcile remaining backlog points, team capacity, release scope, and burndown. | Partially completed in this branch. | 38 points are planned; optional US9 (5 points) is excluded from scope. Team capacity and actual burndown still need team confirmation. |
| Record actual planning, daily-scrum, review, and retrospective dates, attendees, decisions, and blockers. | Not fully completed. | Sprint 3 files were blank templates; this evidence-based report does not reconstruct undocumented meetings. |
| Add US7 manual results and complete required regression tests in Docker Compose. | Partially evidenced. | US7 manual results still do not appear in `tests/manual-tests.md`; the earlier broad smoke check confirms app startup but not every US7 acceptance criterion. |
| Replace the board placeholder with a dated screenshot and maintain the board. | Not completed. | Sprint 3 `board.png` remains placeholder text. |

## What went well

- US5 has focused automated tests and manual results recorded as passed on
  2026-11-13.
- US10 implementation and manual results are present; the results were added
  on 2026-11-14.
- The Selenium US2 browser test passed against the Compose app on 2026-11-15.

## What could improve

- US3's implementation sorts by pickup start, while its acceptance criterion
  specifies pickup end; the manual record does not match the implementation.
- Sprint estimates, capacity, release scope, and burndown have not been
  reconciled.
- US7 manual acceptance evidence, actual Sprint 3 event notes, and genuine
  sprint-board screenshots are still missing.
- The manual log says US10 passed, but the 300-character comment limit was not
  tested.

## Actions

| Action | Owner | Due |
|---|---|---|
| Run the documented Selenium US2 test against the Compose stack and record its actual result. | Completed on this branch | 2026-11-15 |
| Keep optional US9 out of the project scope; it is excluded from the README and Sprint 3 plan. | Team | Recorded in the updated plan |
| Reconcile backlog estimates, sprint totals, team capacity, and burndown. | Team; specific owner not recorded | Before final submission |
| Complete missing US7 regression checks, test the US10 comment limit, and correct the US3 sort-order test evidence. | Story owners; not assigned in the repository | Before final submission |
| Record real event dates, attendees, decisions, and replace placeholder board images with actual screenshots. | Scrum Master and team | At the actual events |
