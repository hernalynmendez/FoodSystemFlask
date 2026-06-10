# BUG: Checkout rejects valid delivery fields — "Delivery address and city are required."

**Summary**

When a logged-in user fills the Checkout form with valid delivery address and city and confirms the order, the server flashes the error "Delivery address and city are required." and the order is not created.

**Environment**

- Repository: FoodSystem_Flask
- Files/areas affected: templates and checkout flow
- Relevant files: [templates/checkout.html](templates/checkout.html), [app.py](app.py), [static/style.css](static/style.css), [templates/base.html](templates/base.html)

---

**Steps to reproduce**

1. Start the dev server and log in as a normal (non-admin) user.
2. Add an item to the cart from `/menu`.
3. Go to `/cart` and click "Proceed to Checkout".
4. Fill in `Delivery Address` and `City` fields (and optionally `Postal Code`), select a payment method.
5. Click "Confirm Order" and accept the confirmation modal.

**Expected result**

- The server accepts the POST, creates an order (or redirects to mock payment if online), clears the cart (on success), and navigates to the order confirmation page.

**Actual result**

- The checkout POST is rejected server-side and the page flashes: "Delivery address and city are required." The order is not created.

---

**Root cause**

- The delivery fields (`delivery_address`, `city`) were placed outside the `<form method="POST">`, so they were not included in the form submission. Server-side validation therefore received empty values and rejected the request.

Secondary issues discovered during debugging:
- Postal code initially had no numeric-only restrictions, increasing the risk of inconsistent input handling.
- Some UI/text contrast issues around confirmation modals (fixed separately).

---

**Resolution**

Applied fixes (see modified files):

- Moved delivery and payment input elements inside a single `<form method="POST">` so all inputs are submitted together: [templates/checkout.html](templates/checkout.html).
- Added client-side validation and inline error UI (red border + message) for required fields in: [templates/checkout.html](templates/checkout.html) and styles in [static/style.css](static/style.css).
- Enforced digits-only for postal code client-side (`inputmode="numeric"` + `pattern="\d*"`) and server-side (`postal_code.isdigit()`) in: [templates/checkout.html](templates/checkout.html) and [app.py](app.py).
- Preserved user-entered values on validation failure by re-populating form fields using `request.form`.
- Added a logout confirmation modal to improve UX (unrelated to the root cause but part of same change set): [templates/base.html](templates/base.html).

---

**Files changed**

- [templates/checkout.html](templates/checkout.html)
- [app.py](app.py)
- [static/style.css](static/style.css)
- [templates/base.html](templates/base.html)

**How to verify the fix**

1. Start the dev server.
2. Log in as a user, add an item to cart, navigate to `/checkout`.
3. Fill `Delivery Address` and `City` and (optional) `Postal Code` (try a non-digit postal code to test the validation).
4. Click "Confirm Order" and proceed in the modal.
5. Expected: order is created and you are redirected to `/mock-payment/<order_id>` (if online) or `/order/confirmation/<order_id>` (if COD).
6. For invalid postal code (letters), the UI shows an inline error; server will flash a validation message if client-side is bypassed.

---

**Recommendations**

- Convert logout to a POST-based logout endpoint and have the confirmation modal submit that POST (improves CSRF safety).
- Add automated integration tests for checkout (happy path and validation failures).
- Consider persisting user addresses in profiles to improve UX and reduce re-entry.

---

**Reported by**: Development automation (pair-programming session)
**Date**: 2026-06-11

