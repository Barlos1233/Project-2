| User story | Acceptance criterion | Tester | Date | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| US4 | 1: Reserve 1 or 2 portions, pickup code shown, remaining portions decrease | ABDALBASET | 11/6/26 | PASSED | Pickup code JQQVAJ (6 characters) shown on the confirmation page. Portions Remaining dropped after reserving. |
| US4 | 2: Request more portions than remain | ABDALBASET | 11/6/26 | PASSED | Asked for 2 portions on a listing with 1 left. Shows "Not enough portions left." and no reservation was created. |
| US4 | 3: Reserve the same listing twice | ABDALBASET | 11/6/26 | PASSED | Second attempt shows "You already have a reservation for this listing." No second reservation created. |
| US4 | 4: Two students reserve the last portion at once | ABDALBASET | 11/6/26 | NOT RUN BY HAND | Cannot be done reliably by hand. The code locks the listing row so only one reservation can take the last portion. |
| US7 | 1: Successful pickup | MASON | 11/12/26 | PASSED | Student name and portions shown; status becomes picked_up; available portions stay correct. |
| US7 | 2: Used code rejected | MASON  | 11/12/26 | PASSED | Reusing a confirmed code is rejected. |
| US7 | 2: Unknown code rejected | MASON  | 11/12/26 | PASSED | 000000 produces a clear error. |
| US7 | 2: Other vendor's code rejected | MASON  | 11/12/26 | PASSED | Wrong vendor cannot confirm the reservation. |
| US7 | 2: Cancelled code rejected | MASON  | 11/12/26 | PASSED | Cancelled reservation cannot be picked up. |
| US7 | 1: Pickup window enforced | MASON  | 11/12/26 | PASSED | Confirmation before the start and after the end is rejected. |
| US7 | 3: No-shows displayed | MASON  | 11/12/26 | PASSED | Both expired active reservations show No Show before any vendor confirmation attempt. |
| US7 | Additional: Vendor-only access | MASON  | 11/12/26 | PASSED | Student cannot open the confirmation page. |
| US8 | 1: Dietary tags | MASON | 11/5/26 | PASSED | Vegan shows A/B/C. Vegan + gluten-free shows A/C. |
| US8 | 2: Location and combined filters | MASON | 11/5/26  | PASSED | Union shows B/C. Vegan + gluten-free + Union shows C. |
| US8 | 3: Clear filters | MASON | 11/5/26  | PASSED | All three listings return and controls reset. |
| US8 | Additional: No matches | MASON | 11/5/26  | PASSED | Halal + Union shows the no-matches message. |
