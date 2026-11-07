Date/Time: 2026-11-06 (date of the latest Sprint 1 story merge visible in the repository; review meeting time is not recorded)

Participants: Not recorded. The README identifies Carlos Viramontes as Scrum Master. No Product Owner or stakeholder attendance/acceptance is documented.

## Sprint goal review

The recorded goal was to deliver registration/login (US1), listing creation (US2), listing browse (US3), and listing filters (US8), in dependency order.

## Evidence-based outcome

| Story / deliverable | Repository evidence | Review status |
|---|---|---|
| US1 — Register and log in | Authentication routes and a basic registration/login test exist; the US1 pull request is recorded as merged. | Implementation is present. The repository does not show evidence that every acceptance criterion was reviewed in the deployed app. |
| US2 — Post a listing | Listing form and route exist, with automated tests for valid/invalid pickup windows and student access denial. | Implementation and focused tests are present; complete acceptance-criteria review is not recorded. |
| US3 — Browse listings | Browse route and page integration exist. | Implementation is present; complete acceptance-criteria review is not recorded. |
| US8 — Filter listings | Filter implementation is merged. The manual-test file records passing checks on 2026-11-05 for tags, location/combined filters, clearing filters, and no matches. | Those recorded manual checks passed; no Product Owner sign-off is recorded. |
| US4 — Reserve portions | Reservation implementation and a manual-test entry were added on 2026-11-06. | Work was pulled forward from the README's Sprint 2 plan. Do not count it as a planned Sprint 1 commitment without updating the release plan. |
| UML design | Class and US4 sequence diagrams are present under `uml/`. | Artifacts are present; review/sign-off is not recorded. |

## Decisions and follow-up

- The repository does not contain review-meeting minutes, a demo record, or Product Owner acceptance; this summary is based on committed artifacts and test records only.
- The Sprint 1 board image is placeholder text rather than a board screenshot, so it does not demonstrate board progress.
- Reconcile the Sprint 1 estimate discrepancy (11 planned versus 14 points from the listed story estimates) and record whether US4 was deliberately pulled into Sprint 1.
- Confirm each story's full acceptance criteria against the Docker Compose deployment and record the results.
