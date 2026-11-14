| User story | Acceptance criterion | Tester | Date | Result | Notes |

| US8 | 1: Dietary tags | MASON | 11/5/26 | PASSED | Vegan shows A/B/C. Vegan + gluten-free shows A/C. |
| US8 | 2: Location and combined filters | MASON | 11/5/26  | PASSED | Union shows B/C. Vegan + gluten-free + Union shows C. |
| US8 | 3: Clear filters | MASON | 11/5/26  | PASSED | All three listings return and controls reset. |
| US8 | Additional: No matches | MASON | 11/5/26  | PASSED | Halal + Union shows the no-matches message. |

| US4 | 1: Reserve 1 or 2 portions, pickup code shown, remaining portions decrease | ABDALBASET | 11/6/26 | PASSED | Pickup code JQQVAJ (6 characters) shown on the confirmation page. Portions Remaining dropped after reserving. |
| US4 | 2: Request more portions than remain | ABDALBASET | 11/6/26 | PASSED | Asked for 2 portions on a listing with 1 left. Shows "Not enough portions left." and no reservation was created. |
| US4 | 3: Reserve the same listing twice | ABDALBASET | 11/6/26 | PASSED | Second attempt shows "You already have a reservation for this listing." No second reservation created. |
| US4 | 4: Two students reserve the last portion at once | ABDALBASET | 11/6/26 | NOT RUN BY HAND | Cannot be done reliably by hand. The code locks the listing row so only one reservation can take the last portion. |

| US1 | 1: Register as student or vendor and store account | CARLOS | 11/10/26 | PASSED | Registration creates a user in PostgreSQL, stores the selected role, and redirects to the login page. |
| US1 | 2: Duplicate email rejected | CARLOS | 11/10/26 | PASSED | Reusing an existing email shows the duplicate-email error and does not create a second account. |
| US1 | 3: Required fields required | CARLOS | 11/10/26 | PASSED | Empty fields show validation errors and the account is not created. |
| US1 | 4: Password hashed | CARLOS | 11/10/26 | PASSED | The stored password value is a hash rather than plain text in the database. |
| US1 | 5: Login success and invalid password handling | CARLOS | 11/10/26 | PASSED | Correct credentials redirect to the role-based home page; wrong credentials show an error and keep the user logged out. |

| US2 | 1: Vendor can post a valid listing | CARLOS | 11/10/26 | PASSED | Vendor enters title, description, portions, dietary tags, pickup location, and window; listing is saved and linked to the vendor account. |
| US2 | 2: Invalid pickup window rejected | CARLOS | 11/10/26 | PASSED | End time before start or in the past blocks posting and shows the error message. |
| US2 | 3: Student cannot access new-listing page | CARLOS | 11/10/26 | PASSED | Logged-in student receives access denied when trying to open the vendor new-listing page. |

| US3 | 1: Student sees only current available listings | CARLOS | 11/10/26 | PASSED | Listings shown are unended, have at least one portion left, and are not cancelled. |
| US3 | 2: Each listing shows all required information | CARLOS | 11/10/26 | PASSED | Listing cards include title, vendor name, pickup location, dietary tags, portions remaining, and pickup window. |
| US3 | 3: Listings sorted by soonest pickup end | CARLOS | 11/10/26 | PASSED | Listings appear in ascending pickup-window-end order. |
| US3 | 4: No listings available message | CARLOS | 11/10/26 | PASSED | When no valid listings exist, the page displays the no-listings message instead of an empty state. |

| US6 | 1: My Reservations shows all required details and status | CARLOS | 11/10/26 | PASSED | Reservation rows include title, vendor, location, pickup window, portions, pickup code, and status. |
| US6 | 2: Active reservation can be cancelled and portions returned | CARLOS | 11/10/26 | PASSED | Cancelling an active reservation updates its status to cancelled and returns the reserved portions to the listing. |
| US6 | 3: Inactive reservations do not show cancel option | CARLOS | 11/10/26 | PASSED | Reservations no longer active do not display a Cancel button. |

| US5 | 1: My Listings shows each listing's status and reserved/remaining portions | Carlos | 11/13/26 | PASSED | `tests/test_us5_manage_listings.py::test_my_listings_shows_status_and_portion_counts` passed for active, ended, and cancelled status plus portion counts. |
| US5 | 2: Edit a listing with no reservations and validate fields as in US2 | Carlos | 11/13/26 | PASS | `test_edit_listing_updates_fields_and_reuses_listing_validation` passed for saving edits and rejecting an invalid pickup window. |
| US5 | 3: Do not allow portions below the reserved count | Carlos | 11/13/26 | PASSED | `test_edit_cannot_reduce_portions_below_reservations` passed; rejected the edit and kept the stored portions unchanged. |
| US5 | 4: Cancel a listing and cancel its active reservations | Carlos | 11/13/26 | PASSED | `test_cancel_hides_listing_and_cancels_active_reservations` passed; listing was hidden from browsing and its active reservation was cancelled. |
| US5 | 5: Show reserving students and portions; restrict access to the owning vendor | Carlos | 11/13/26 | PASSED | `test_reservations_are_visible_only_to_the_listing_vendor` passed; another vendor received 404 for details, edit, and cancel routes. |
