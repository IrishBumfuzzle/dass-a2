# QuickCart

## 1. Test Cases

**Header Validation:** Ensure that `X-Roll-Number` and `X-User-ID` headers are strictly validated for being present and correctly formatted (integer and non-negative).

**Profile Management:** Ensure name and phone length/format constraints are properly validated.

**Address Management:** Ensure label uniqueness, pincode formats (exactly 6 digits), and default address logic are properly validated.

**Product Catalog:** Ensure search, sorting, category filtering, and price consistency between user and admin APIs are properly validated.

**Cart Operations:** Ensure quantity limits, stock checks, and mathematical accuracy for subtotals and totals are properly validated.

**Coupons:** Ensure PERCENT and FIXED coupon types, capped discounts, and expiry checks are properly validated.

**Checkout & Payments:** Ensure various payment methods, GST (5%) calculations, and stock reduction/cart clearing upon purchase are properly validated.

**Wallet:** Ensure balance addition, payment accuracy, and underflow prevention are properly validated.

**Loyalty Points:** Ensure redemption logic and point tracking are properly validated.

**Order Tracking:** Ensure order tracking, cancellation logic, and stock restoration on cancellation are properly validated.

**Reviews & Ratings:** Ensure 1-5 rating range, comment length bounds, and average rating calculations are properly validated.

**Support Tickets:** Ensure ticket creation and strict state transitions (OPEN -> IN_PROGRESS -> CLOSED) are properly validated.

---

## 2. Detailed Bug Reports

### Wallet Extra Deduction (0.6 Fee)
- **Endpoint:** `POST /api/v1/wallet/pay`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/wallet/pay`
  - **Headers:** `X-Roll-Number: 12345`, `X-User-ID: 1`, `Content-Type: application/json`
  - **Body:** `{"amount": 100}`
- **Expected Result:** Balance reduces by exactly the payment amount (100.0).
- **Actual Result:** Extra amount was deducted beyond the transaction value. Expected balance `166984.99`, got `166984.38999999998` (Difference of 0.6).

### Cart Subtotal Calculation Error
- **Endpoint:** `GET /api/v1/cart`
- **Request Payload:**
  - **Method:** `GET`
  - **URL:** `http://localhost:8080/api/v1/cart`
  - **Headers:** `X-Roll-Number: 12345`, `X-User-ID: 1`
- **Expected Result:** Each item subtotal must equal `quantity * unit_price`.
- **Actual Result:** Adding 3 items of price 120 results in subtotal `104` instead of `360`.

### Cart Total Summation Error
- **Endpoint:** `GET /api/v1/cart`
- **Request Payload:**
  - **Method:** `GET`
  - **URL:** `http://localhost:8080/api/v1/cart`
  - **Headers:** `X-Roll-Number: 12345`, `X-User-ID: 1`
- **Expected Result:** Cart total must be the sum of all item subtotals.
- **Actual Result:** Observed cart total `-16` while sum of subtotals was `-142`.

### Checkout GST & Total Calculation Error
- **Endpoint:** `POST /api/v1/checkout`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/checkout`
  - **Headers:** `X-Roll-Number: 12345`, `X-User-ID: 1`
  - **Body:** `{"payment_method": "COD"}`
- **Expected Result:** Checkout total should match `cart subtotal + 5% GST`.
- **Actual Result:** Response total `126` returned for a calculated expected total of `0.0` (empty or zero-value cart due to subtotal errors).

### Address Management: Valid Address Blocked
- **Endpoint:** `POST /api/v1/addresses`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/addresses`
  - **Headers:** `X-Roll-Number: 12345`, `X-User-ID: 1`
  - **Body:** `{"label": "HOME", "street": "123 Main St", "city": "New York", "pincode": "100001", "is_default": true}`
- **Expected Result:** `201 Created` and returning the full address object.
- **Actual Result:** `400 Bad Request`. Valid address additions were consistently rejected.

### Validation Bypass: Address Pincode Length
- **Endpoint:** `POST /api/v1/addresses`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/addresses`
  - **Body:** `{"label": "HOME", "street": "Pincode Test", "city": "City", "pincode": "10000"}`
- **Expected Result:** `400 Bad Request` (pincode must be exactly 6 digits).
- **Actual Result:** `200 OK`. The server accepts 5-digit and 7-digit pincodes.

### Validation Bypass: Invalid Cart Quantity (Zero)
- **Endpoint:** `POST /api/v1/cart/add`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/cart/add`
  - **Body:** `{"product_id": 1, "quantity": 0}`
- **Expected Result:** `400 Bad Request` (quantity must be at least 1).
- **Actual Result:** `200 OK`.

### Validation Bypass: Invalid Cart Quantity (Negative)
- **Endpoint:** `POST /api/v1/cart/add`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/cart/add`
  - **Body:** `{"product_id": 1, "quantity": -5}`
- **Expected Result:** `400 Bad Request`.
- **Actual Result:** `200 OK`.

### Validation Bypass: Product Review Rating Over Range
- **Endpoint:** `POST /api/v1/products/1/reviews`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/products/1/reviews`
  - **Body:** `{"rating": 6, "comment": "Excellent"}`
- **Expected Result:** `400 Bad Request` (rating limit is 5).
- **Actual Result:** `200 OK`.

### Validation Bypass: Non-Numeric Phone Number
- **Endpoint:** `PUT /api/v1/profile`
- **Request Payload:**
  - **Method:** `PUT`
  - **URL:** `http://localhost:8080/api/v1/profile`
  - **Body:** `{"name": "John Doe", "phone": "987654321a"}`
- **Expected Result:** `400 Bad Request` (phone must be numeric).
- **Actual Result:** `200 OK`.

### Order Lifecycle Violation: Cancel Delivered Order
- **Endpoint:** `POST /api/v1/orders/{id}/cancel`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/orders/1/cancel`
- **Expected Result:** `400 Bad Request` (delivered orders cannot be cancelled).
- **Actual Result:** `200 OK`.

### Data Integrity: Stock Restoration Failure
- **Endpoint:** `POST /api/v1/orders/{id}/cancel`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/orders/{id}/cancel`
- **Expected Result:** Stock increments by the quantity in the cancelled order.
- **Actual Result:** Stock is not restored. Expected `174` units, but observed `173`.

### Data Consistency: Admin vs User Price Mismatch
- **Endpoint:** `GET /api/v1/products/8`
- **Request Payload:**
  - **Method:** `GET`
  - **URL:** `http://localhost:8080/api/v1/products/8`
- **Expected Result:** Price matches between User API and Admin Database.
- **Actual Result:** User API shows `100`, Admin Database shows `95`.

### Loyalty Points Redemption Failure
- **Endpoint:** `POST /api/v1/loyalty/redeem`
- **Request Payload:**
  - **Method:** `POST`
  - **URL:** `http://localhost:8080/api/v1/loyalty/redeem`
  - **Headers:** `X-Roll-Number: 12345`, `X-User-ID: 1`
  - **Body:** `{"amount": 10}`
- **Expected Result:** `200/201 Success` (assuming user has enough points).
- **Actual Result:** `400 Bad Request` for valid redemption requests.

### Logic: Update Non-Existent Cart Item
- **Endpoint:** `PUT /api/v1/cart/items/999`
- **Request Payload:**
  - **Method:** `PUT`
  - **URL:** `http://localhost:8080/api/v1/cart/items/999`
  - **Body:** `{"quantity": 5}`
- **Expected Result:** `400/404 Not Found`.
- **Actual Result:** `200 OK`.
