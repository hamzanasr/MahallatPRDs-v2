# Mahallat Platform Specification — Version 4.11

29 October 2026 · Revision 2026-10-29 · 240 requirements · 93 pages. The requirements are the reference.

## Order states by type

Every state an order passes through on each path: when it enters the state, who performs the transition, and where the money is.

### Menu or Mart order with delivery

| # | Internal state | What the customer sees | Entered when | Actor | Money | Reference |
|---|---|---|---|---|---|---|
| 1 | Paid: cancellation window | Looking for a driver | Payment hold succeeds | System | Held | ORD-002 PAY-001 |
| 2 | Searching for a driver | Looking for a driver | 60 seconds elapse | System | Held | DSP-001 |
| 3 | At the merchant | Being prepared | A driver accepts the order | System | Held | ORD-003 ORD-006 |
| 4 | Ready | Being prepared | Merchant presses "Ready" | Merchant | Held | ORD-001 ORD-003 |
| 5 | Picked up by the driver | Out for delivery | Merchant enters the driver code within the arrival distance (100 meters) | Merchant | Held | ORD-005 |
| 6 | Driver arrived | Out for delivery | Driver presses "Arrived" within the arrival distance (100 meters) of the customer | Driver | Held | ORD-008 |
| 7 | Delivered (final) | Delivered | Driver confirms with evidence within the arrival distance | Driver | Captured | ORD-005 PAY-001 |

### Write-in or pharmacy order

| # | Internal state | What the customer sees | Entered when | Actor | Money | Reference |
|---|---|---|---|---|---|---|
| 1 | Delivery paid: cancellation window | Looking for a driver | First payment hold succeeds | System | Delivery held | ORD-013 ORD-002 |
| 2 | Searching for a driver | Looking for a driver | 60 seconds elapse | System | Held | DSP-001 |
| 3 | At the merchant: review | Being prepared | A driver accepts the order | System | Held | ORD-003 PHR-012 |
| 4 | Awaiting payment | Being prepared, with a payment request | Merchant uploads the products invoice photo and amount | Merchant | 10-minute window for the second payment | ORD-013 |
| 5 | Paid: preparing | Being prepared | Customer pays | Customer | Both payments held | ORD-013 |
| 6–9 | Ready ← Picked up by the driver ← Arrived ← Delivered | Same as menu | Same as menu | Same as menu | Captured on delivery | ORD-005 |

### Self-pickup (menu, outside Mart)

| # | Internal state | What the customer sees | Entered when | Actor | Money | Reference |
|---|---|---|---|---|---|---|
| 1 | Paid: cancellation window | Being prepared | Payment hold succeeds | System | Held | EXT-006 ORD-002 |
| 2 | At the merchant | Being prepared | 60 seconds elapse (no driver task) | System | Held | EXT-006 ORD-006 |
| 3 | Ready for pickup | Ready page with directions | Merchant presses "Ready" | Merchant | Held | EXT-006 |
| 4 | Picked up (final) | Delivered | Merchant confirms with the order number | Merchant | Captured | ORD-005 EXT-006 |

### Non-final state: Awaiting support decision

The order enters it from any stage whenever its amounts are a staff decision, and stays in it until the support agent records what is captured and what is refunded for each party; then it is closed. Nothing is captured or refunded in it before the decision, except the full refund for an out-of-stock item, and the automatic capture when 24 hours have passed since the hold (PAY-001), after which the decision is executed as a refund. Anything not resolved within 18 hours of the hold is escalated to the support supervisor.

| Reason for entry | When | Actor | Reference |
|---|---|---|---|
| Out-of-stock item | The customer chose "Cancel the order" in advance, or all items were removed; the amount is refunded in full | System, then the support decision on the loss charge or penalty | MER-032 |
| Unpaid | 10 minutes elapse or the customer rejects the products invoice in a write-in order | System, then the support decision on the amount | ORD-013 |
| Rejected before the products invoice | Merchant rejects a write-in order, including a pharmacy order without a prescription | Merchant, then the support decision | ORD-004 PHR-012 |
| No-show | Self-pickup whose owner did not come by the end of working hours | System, then the support decision | EXT-006 |

### Final states without delivery

The order is closed without delivery with one of these states. Cancellation is a closing in which all or part of the amount is refunded, and termination is a closing in which it is captured. What is captured and what is refunded in each case is covered in "Closing an order without delivery".

| Internal state | When | Actor | Reference |
|---|---|---|---|
| Cancelled within the window | Before the 60 seconds elapse | Customer | ORD-002 |
| Cancelled with no driver | After 15 minutes without a driver, with the customer choosing a refund or making no choice within 5 minutes | Customer or system | ORD-004 |
| Cancelled by support | After the window, with a written reason and a named liable party, or "No loss charge" | Support agent | ORD-004 ADM-043 |
| Closed by support decision | After "Awaiting support decision": cancellation or termination according to what the agent decided | Support agent | ORD-001 ORD-004 |
| Converted to self-pickup | After 15 minutes without a driver, with customer acceptance within 5 minutes; the order continues as self-pickup | Customer | EXT-006 ORD-004 |
| Ended for non-responsiveness | After reviewing the evidence | Support agent | ORD-008 |
| Returning to the pharmacy ← Returned | Medicine not delivered, then the return stop, with the return code entered or an operations decision | Driver and pharmacy | PHR-010 |

> Internal status names are approved for development. What the customer sees of the four ORD-001 statuses, and the final statuses, are shown to them as written. Rejection, out-of-stock, non-payment and no-show are reasons, not statuses. Every transition executes once on the server and records the executor and time (ORD-001).

## Dispatch algorithm

How the system picks the driver. Approved by the owner on 5 October.

The timeline for a single order per DSP-001. The rules, weights, and the priority index example are in the requirement itself, and the values are in "Configurable values"; this appendix adds no rule.

### Timeline

| Time | What happens |
|---|---|
| 0:00 | Cancellation window ends. The 15-minute window starts. |
| 0:00 to 0:30 | The preferred captain alone, if set. If none, the first attempt starts immediately. |
| 0:30 to 1:00 | Attempt 1: task-offer radius 5 km, top 3 by priority index. |
| 1:10 to 1:40 | Attempt 2: task-offer radius 6 km, top 6. |
| 1:50 to 2:20 | Attempt 3: task-offer radius 7 km, all eligible drivers. |
| From 2:30 | Cycles: +1 km each attempt up to 10 km, all eligible drivers. |
| 5:00 | Alert to support. |
| 15:00 | Automatic task offers stop. For non-Mart: self-pickup within 5 minutes or a full refund. For Mart: manual assignment or cancellation. |

## Closing an order without delivery

What happens to the money in every case that does not end in delivery.

When the held amount is captured, when it is refunded, and who gets what, when the order does not end in delivery. The general rule: the amount stays held until the order is closed (PAY-001).

> The tip always follows the delivery fee: if delivery is paid out to the driver, the tip is paid out with it, and if it is refunded to the customer, the tip is refunded in full (CUS-010).

| Case | Who decides | Customer | Driver (delivery and tip) | Merchant | Reference |
|---|---|---|---|---|---|
| Customer cancels within 60 seconds | Customer | The hold is fully released | Nothing | Nothing | ORD-002 PAY-001 |
| No driver after 15 minutes, and the customer chose self-pickup | Customer | Delivery and tip are refunded, and the rest is captured at pickup | Nothing | Completes the order | EXT-006 ORD-004 |
| No driver after 15 minutes, and the customer chose a refund or did not choose within 5 minutes | Customer or system | The hold is fully released | Nothing | Nothing | ORD-004 PAY-001 |
| No driver in Mart | Support | Manual assignment, or cancellation with a full refund | Whoever is assigned | — | ORD-004 |
| Cancellation by support after the window | Support agent | The amount is refunded | What support decides, if the driver had picked up the order | A loss charge to the extent of the loss, or a penalty, if support decides them; the platform may be the liable party | ORD-004 PAY-025 |
| Out-of-stock item and "Cancel the order" chosen | System, then support | The amount is refunded | What support decides | A loss charge or penalty if support decides them | MER-032 |
| Customer non-responsiveness | Support agent | No refund, and the amount is captured | The fee and the tip | Their due as usual | ORD-008 DRV-005 |
| Write-in order not paid within 10 minutes | System, then support | Bears the part of delivery that support decides, and the rest is refunded | What support decides, and the tip follows delivery | Nothing | ORD-013 |
| Pharmacy order without a prescription | Support agent | The part of delivery that support decides | What support decides | Nothing | PHR-012 |
| Medicine not delivered because of no response | Support or Operations | Delivery is not refunded; the medicine price and the service fee are refunded after the pharmacy confirms it is intact; if the refund is rejected, the pharmacy keeps it for 7 days for a new delivery order, then it is destroyed | Fee and tip | You restore the medicine | PHR-010 |
| Self-pickup not collected by its owner | Support agent | What support decides | — | What support decides | EXT-006 |

Every support decision in these cases is logged with the actor, the written reason, and the liable party, and the order stays "Awaiting support decision" and is not closed before it. "What support decides" means the cancellation screen asks the agent for the amount for each party or "nothing".

## Roles and permissions

The built-in admin dashboard roles and their default distribution.

This table is the reference for the default distribution of permissions across the built-in roles (ADM-043), and the admin edits it from the settings page (A22).

### Default distribution for the built-in roles

| Permission | Admin | Support supervisor | Support agent | Operations | Finance | Sales | Reference |
|---|---|---|---|---|---|---|---|
| Operations room and orders | ✓ | ✓ | ✓ | ✓ | Read only | — | ADM-003 |
| Assignment and reassignment | ✓ | ✓ | ✓ | ✓ | — | — | DSP-002 ORD-004 |
| Cancel an order after the window and refund | ✓ | ✓ | ✓ | — | — | — | ORD-004 |
| Loss charge and penalty | ✓ | ✓ | ✓ | — | — | — | PAY-025 |
| Refund of an undelivered medicine (within the role limit) | ✓ | ✓ | ✓ | ✓ | — | — | PHR-010 |
| Compensation and repeat-order credit | ✓ | ✓ | ✓ | — | — | — | SUP-002 MKT-002 |
| Reverse a financial decision with a reversing entry | ✓ | ✓ | — | — | ✓ | — | PAY-025 PAY-005 |
| Tickets and chats | ✓ | ✓ | ✓ | Read only | — | — | SUP-001 |
| Drivers: approve, disable, and ban | ✓ | ✓ | — | ✓ | — | — | DRV-001 DRV-023 |
| Merchants: onboarding and contracts | ✓ | — | — | — | Read only | ✓ | MER-013 PAY-009 |
| Offers, ads, and campaigns | ✓ | — | — | — | — | ✓ | MKT-003 MKT-008 |
| Accounts, entries, and closing | ✓ | — | — | — | ✓ | — | ADM-036 |
| Approve payouts | ✓ | — | — | — | ✓ | — | PAY-006 |
| Financial reports | ✓ | — | — | — | ✓ | — | ADM-006 |
| Other reports (within the role's scope) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ADM-006 |
| Settings, cities, and fees | ✓ | — | — | — | — | — | ADM-034 DSP-002 |
| Roles, permissions, and audit log | ✓ | — | — | — | — | — | ADM-001 ADM-002 |
| Disable a city or payment method | ✓ | — | — | — | — | — | ADM-004 |
| Disable a branch | ✓ | ✓ | — | ✓ | — | — | ADM-004 |
| Disable an ad | ✓ | — | — | — | — | ✓ | ADM-004 |
| Preferred captain and instant incentive | ✓ | — | — | ✓ | — | — | MER-038 ADM-044 |
| Catalogs, price review, and enabling integrations | ✓ | — | — | — | — | ✓ | MER-010 MER-002 MER-041 |
| Ban customers | ✓ | ✓ | — | — | — | — | ADM-013 |
| Ban merchants | ✓ | — | — | — | — | — | ADM-004 |
| Second approval for freezing a wallet | ✓ | ✓ | — | — | — | — | ADM-013 |
| Add points to a customer | ✓ | — | — | — | — | — | MKT-010 |
| Viewing the prescription photo (for the pharmacist in the merchant app only) | — | — | — | — | — | — | PHR-012 ADM-001 |
| View the customer address | ✓ | ✓ | ✓ | ✓ | — | — | ADM-001 |

**Account manager** is a seventh role in the admin dashboard (MER-014): admin assigns them a group of merchants; they see their merchants and those merchants' chats and reports, and have no financial permissions. The merchant's chats reach them and are visible to the support supervisor.

"Read only": can see but takes no action.

The general permission rules (role scope by city, two-step verification, financial limits, audit log, and session expiry) are in ADM-001, ADM-043, and ADM-002.

## Admin page details

The content of the Accounts and driver performance pages, and the placement of the reports list and indicators.

Some admin dashboard requirements referred their details to sections that are not in the file. This appendix writes those details from the existing requirements and ties each part to its reference.

### Accounts page: the nine tabs

Reference ADM-036, page A18.

| Tab | What it shows | Actions | Reference |
|---|---|---|---|
| Overview | Captured and held amounts for the period, unpaid dues, open discrepancies, and negative driver dues accounts | Open any number into its list | PAY-001 PAY-006 PAY-026 |
| Collection and reconciliation | Every payment with its status, and the daily reconciliation against the Moyasar report: captured minus the actual Moyasar fee equals the bank deposit, with the difference visible | Suspend a discrepancy, retry a failed transaction | INT-001 PAY-027 ADM-036 |
| Dues and payouts | The statement of each merchant and freelance driver (and companies later), the list of due payouts, and the status and bank reference of each transfer | Approve one account, or select several accounts and approve them together | PAY-006 FLT-002 PAY-018 |
| Liabilities | The platform's liability items and their total, matched against wallet and points balances | Export | PAY-031 |
| Invoices | Platform invoices for customers, and monthly fees invoices and ad invoices for merchants | Issue, export | PAY-007 PAY-022 |
| Tax | 15% tax on platform fees shown separately, and the VAT included in tips per CUS-010, with the rate's effective date | Export | PAY-022 PAY-029 SYS-012 |
| Refunds | Every refund with its type, source, actor, reason, and the liable party | Open the order, reversing entry | PAY-003 PAY-028 SUP-002 |
| Financial reports | The "Finance" reports in the admin reports list | As in each report | ADM-006 |
| Closing and controls | The status of each month (open or closed), the financial audit log, and the financial limits for the roles | Close a month, for the holder of the closing permission (Finance by default) | ADM-036 ADM-002 PAY-005 |

### Driver performance and incentives: the four tabs

Reference ADM-035, page A11.

| Tab | What it shows | Reference |
|---|---|---|
| Performance | Each driver's score over the last 30 days, the breakdown of indicators with their weights, the tier, and review alerts | DRV-017 DRV-015 ADM-009 |
| Driver profile | Account, vehicle, city, equipment, bank, insurance, bans, payouts, and the action log | DRV-001 PAY-024 DRV-023 |
| Incentives | The four incentives and the instant incentive, the cost of each incentive and what it brought in, and the budget | DRV-006 ADM-044 |
| System settings | Score weights, tier thresholds and benefits per city, and the weights of the priority index in dispatch | DRV-015 DRV-017 DSP-001 |

### Reports center and page analytics

- The full admin reports list is in the "Reports" section of this document (ADM-006).
- Each page's indicators are the elements listed under it in the "Admin dashboard" section, and the definition of each number is in "Indicator definitions" (ADM-030).

## Indicator definitions

A unified definition for every number in the dashboards and reports.

One definition for each number, used on all pages and reports, so the same number appears with the same value wherever it is shown (ADM-030, ADM-006). The period is in Riyadh time (REP-001), and an order is attributed to its closing date. Amounts come from the ledger, not from the customer-facing UI.

> These definitions are approved by the owner (29 October 2026) to standardize the calculation.

### Orders and money

| Indicator | Definition | Reference |
|---|---|---|
| Delivered orders | Orders closed by delivery or by self-pickup in the period | ORD-001 |
| Gross sales | What customers paid on delivered orders (products, delivery, service, and tip) after discounts, minus refunds | ADM-006 |
| Platform revenue | Service fees, contract fees or the Mart and pharmacy percentage, the payment fee, the platform's share of delivery, ads and cashier, and penalties that went to the platform; minus the platform's funding of offers and compensation. Before tax | ADM-006 PAY-031 |
| Average order value | Gross sales ÷ delivered orders | ADM-006 |
| Cancellation rate by cause | Cancelled orders ÷ all paid orders, split by the recorded cause (customer, merchant, driver, no driver, out-of-stock, non-payment) | ADM-014 ORD-004 |
| Report rate | Orders with a report (missing, damaged, did not arrive) ÷ delivered orders | ADM-014 SUP-002 |
| Orders without a driver | Orders that reached 15 minutes without a driver accepting | DSP-001 |
| Late rate | Orders delivered after the initial arrival time shown to the customer ÷ delivered orders | ORD-011 ADM-014 |

### Timings

| Indicator | From | To | Reference |
|---|---|---|---|
| Acceptance time | Start of dispatch (after the 60-second window) | Driver accepts | DSP-001 ADM-014 |
| Preparation time | Start of preparation (ORD-003) | Press of "Ready" | ORD-003 ORD-007 |
| Driver wait at the branch | Driver enters the arrival distance of the branch | Pickup code entered | ORD-005 ADM-014 |
| Delivery time | Pickup from the branch | Delivery | ADM-014 |
| Total order time | Payment | Delivery | ORD-011 |

### Drivers

| Indicator | Definition | Reference |
|---|---|---|
| Acceptance rate | Task offers the driver accepted ÷ task offers that reached the driver. A task offer withdrawn because someone else accepted is not counted | DRV-017 DSP-001 |
| Completion rate | Delivered tasks ÷ accepted tasks, excluding merchant delays, customer cancellation, and technical failure | DRV-017 |
| Rating | Average customer ratings in the period. No rating is not zero | DRV-017 |
| Orders versus drivers | Open orders ÷ available drivers in the city and service | ADM-014 |

### Customers

| Indicator | Definition | Reference |
|---|---|---|
| Active customers | Customers with at least one delivered order in the period | ADM-006 |
| New customers | Customers whose first delivered order falls in the period | ADM-006 |
| Retention | Share of the previous period's customers who ordered again in the current period | ADM-006 |

## Settings (configurable default values)

| Setting | Value | Limits and effect |
|---|---|---|
| Payment fee | 2.5% of the product value after discount + 1 SAR | Fixed on restaurant and Shops merchants whatever the payment method; not Mart or pharmacy |
| Mart and pharmacy merchant percentage | 5% | Global, then per-merchant; base is the original price |
| Markup rate | Mart 5%; restaurants and Shops per each merchant's contract | Inside the sale price; independent of the merchant percentage |
| Menu and Mart service | 2.5% | Total after discounts, excluding the tip and before the service fee |
| Write-in and pharmacy service | 5% | Products only, as a separate line item |
| Per-customer fee per branch | 2 / 5; threshold 25; cap 30; 365-day cycle | For the fee contract only; independent counter per customer and branch; the threshold applies to the selling price |
| Order preparation time | Longest product time; cap 40 minutes | Store-level time for write-in; one edit within 3 minutes |
| Busy mode | Increase ≤15 minutes for a duration ≤1 hour | Does not raise preparation above 40 and does not change an existing order |
| Driver dispatch | 5 km then +1 km per attempt up to 10 km; 3 attempts (top 3, then top 6, then all); 30 s to accept; 10 s gap; priority index weights 50 score / 30 delivery / 20 proximity | System-wide, with an optional per-city exception; cycles repeat up to 15 minutes |
| No driver available | Alert at 5 minutes; intervention at 15 minutes | Mart has no self-pickup; others get a 5-minute conversion window |
| Order batching | 3 orders; 3 km pickup; 3 km delivery; 10 additional minutes | Adjustable per city |
| Arrival distance | 100 meters | Configurable; saved on the task |
| Driver location update | 20 seconds by default | Configurable; a stale location of 120 seconds is excluded from task offers |
| Branch zone | The boundaries of the city where the branch is | Platform staff can draw a manual zone for the branch within its city |
| Write-in invoice payment window | 10 minutes | Service 5% of products; no merchant rejection after the products invoice is uploaded |
| Out-of-stock item | 3-minute reply window from pressing "Out of stock" | After the window the item is removed (MER-032) |
| Customer non-responsiveness | Alert at 5 minutes; support at 30 minutes | No operations code or auto-ending |
| Report / objection window | 1 hour for a report from delivery, in all sections; 7 days for an objection | A report is not accepted after the window; the objection is for the merchant and the driver, from the decision notification; target objection reply 48 hours |
| Driver deposit | 100 SAR | Held and separate from the dues account; refunded at closing after settlement |
| Reward and wallet | Claim within 24 hours; compensation and promotional 14 days | Refund does not expire and does not require claiming a reward |
| Hour Deal | 30% or more | Recurring schedule, a single end time, and inventory |
| Tier score | Last 30 days | Filters of 10 and 30 orders, 30 days, and custom |
| Driver platform percentage | 10% | The city, then the region, then tier benefits, then global; a company driver uses their company's contract percentage |
| Delivery fee | Restaurants and Shops: 9 SAR including 3 km + 1.5 per km, bounds 9–25; Mart and pharmacies: 12 SAR including 3 km + 1.5 per km, bounds 12–30 | System-wide, with an optional setting per region and per city |
| Delivery distance measurement | Air distance (straight line) | Or road distance through Google Maps; each region and each city has its own method, and when road distance is unavailable: air distance × road factor |
| Driver negative balance limit | −50 SAR | When reached, the driver enters "balance lockout" and receives no new tasks until payment |
| Payment splitting for merchants | Always on through Moyasar | Each order's share is split into its branch wallet at capture; and no wallet balance is transferred to the bank without the accountant's approval (PAY-006) |
| Road factor | 1.3 | System-wide, and per region or city; used when road distance is unavailable: air distance × the factor |
| Idle period | 30 days | System-wide; defines the "Idle" segment in coupons and campaigns |
| Pharmacy retention of a medicine whose refund was declined | 7 days | Then destroyed without a refund |
| Maximum hold duration | 24 hours | System-wide; after that, the full amount is captured and whatever support decides is executed as a refund; and an unresolved case is escalated to the support supervisor at 18 hours |

### Default values added in 4.11

Values that had no default, approved by the owner (29 October 2026), and remain adjustable from settings.

| # | Setting | Proposed assumption | Allowed range | Reason | Reference |
|---|---|---|---|---|---|
| 1 | Small refund limit | 25 SAR per decision | 0–50 SAR | Stays under the support agent limit (50 SAR), so a small refund does not need a second approval. "assumption" in usage: it classifies the report as a "small claim" in the queue and reports only, and does not mean an automatic refund | CFG-01 L319; SUP-004 L5265 |
| 2 | Financial limit — Support agent | **50 SAR** per decision (owner decision, mandatory) | Fixed by owner decision | Owner decision | Corrects ADM-043 L5193 (which has 200) |
| 3 | Financial limit — Support supervisor | **200 SAR** per decision (owner decision, mandatory) | Fixed by owner decision | Owner decision | Corrects ADM-043 L5193 (which has 1,000) |
| 4 | Financial limit — Admin | No limit, and every decision is logged | — | Last step in the approval ladder: "anything above goes to admin" | ADM-043 L5193 |
| 5 | Financial limit — Operations | 0 SAR | 0 only as long as the permission is not granted | The role has no cancellation, refund, loss charge, or penalty | L123–L125; ADM-043 L5198 |
| 6 | Financial limit — Finance | 200 SAR for the reversal entry and accepting the objection "assumption" | 0–1,000 SAR | Equal to the support supervisor limit, because the two roles reverse each other's decisions (L126, L2097), and anything above it goes to admin. Finance does not originate loss charges or penalties | L124, L126; L2097 |
| 7 | Financial limit — Sales | 0 SAR | 0 only | Has no financial permissions on orders | L123–L126 |
| 8 | Financial limit — New custom role | 0 SAR until admin sets it | 0–200 SAR | The new role starts safe, and does not exceed the supervisor's limit without an explicit decision | A22 L2591; ADM-001 "least necessary permission" |
| 9 | Single penalty cap (independent of the role limit) | No separate cap; the role limit is the effective cap "assumption" | — | The loss charge is limited to the proven loss (SUP-002 L5245), and the penalty is a manual decision subject to the executor's limit. This makes an additional figure unnecessary | CFG-01 L319; PAY-025 |
| 10 | Target time to rule on the objection | **48 hours** everywhere (owner decision) | 24–72 hours | Owner decision. The number is written into SUP-006 L5289 ("target period" without a number) to match L260 and L4631 | SUP-006 L5289 |
| 11 | Escalating an unanswered objection | At 48 hours it is automatically escalated to the support supervisor ("assumption" on the party) | Follows item 10 | Owner decision: an unanswered objection is escalated. We propose the support supervisor because they hold the authority to accept the objection (L2517) | SUP-006 |
| 12 | Objection submission window | **7 days** from the decision notification (owner decision) | 3–14 days | Exists. Mentioned here for confirmation | L260; SUP-006 L5288 |
| 13 | Escalating the "Awaiting support decision" status | **18 hours** from the hold, escalated to the support supervisor (owner decision) | 12–22 hours | 6 hours remain before automatic capture at 24 hours, and capture happens on time without change | L273; PAY-003 L3306; L109 |
| 14 | Location distance from address warning | **300 meters**, and the actual distance is shown (owner decision) | 100–1,000 m | Owner decision. Format: in meters below 1 km ("350 m away"), and in kilometers above it ("1.4 km away") | CUS-002 L2819; C13 L627 |
| 15 | Customer chat remaining after the order is closed | **24 hours**, a configurable setting (owner decision) | 0–72 hours | Owner decision. Note: MER-022 L4060 and M13 L980 close the **merchant**'s conversation with the customer when the order is closed. "Assumption": the setting applies only to the customer–driver conversation (CUS-008), and the merchant conversation remains as is. Needs owner confirmation | CUS-008 L2905, L2907 |
| 16 | Marketing message limits | **No limit of any kind** (owner decision) | — | Owner decision. The existing limits are removed (see table C) | CFG-01 L319 |
| 17 | Busy mode with a preparation cap | Stays +15 minutes for an hour, and the resulting time does not exceed 40 minutes (owner's decision) | Increase 5–15 min; duration 15–60 min | Owner decision. Available extension = 40 − longest preparation time. Example: if the time is 35 minutes, only +5 is shown | L250; MER-018 L4010; M09 L1167 |
| 18 | Loyalty points to SAR conversion rate | **100 points = 1 SAR**, a setting per city or period (the value is an assumption) | 50–200 points per riyal | The minimum redemption is 500 points, so the first redemption is 5 SAR, a tangible amount without a large burden on the platform net | MKT-010 L5427, L5430 |
| 19 | Points earning rate | 10 points per 1 SAR of platform net on the order "assumption" | 1–20 points per riyal | Without an earning rate, the conversion rate is meaningless. With item 18, the loyalty cost is about 10% of the platform net | MKT-010 L5425, L5427 |
| 20 | Store customer campaign price per city | 0 SAR (free) at launch "assumption" | 0 or more | MKT-005 acknowledges that a zero price makes it free, and does not mention an assumption | MKT-005 |
| 21 | Merchant campaign budget limit ("Higher than the platform limit for you") | No limit "assumption" | 0 = no limit | Consistent with the owner's decision to remove message limits. If a financial limit rather than a message limit is meant, it needs a separate decision | MD05 L1411; MKT-005 |
| 22 | Repeated exceeding of the refund limit before restriction | Exceeding the limit (20%) in two consecutive reviews 30 days apart: a notice, then restriction on the third "assumption" | 2–4 times | SUP-007 says "if repeated" without a number | SUP-007 L5301 |

## Financial transaction examples

| Inputs | Customer account | Merchant or driver account |
|---|---|---|
| Mart: store price 100, markup rate 5%, delivery 12 | Products 105 + service 2.93 + delivery 12 =119.93 | 5% percentage on 100 =5; product dues 95 before platform-fee tax |
| Pharmacy: invoice 100, delivery 12 | First payment 12; second payment 100 + service 5 =105 | 5% percentage =5 before platform-fee tax; no payment fee |
| Restaurant, 10% percentage contract: selling price 105, delivery 12 | Products 105 + service 2.93 + delivery 12 =119.93 | 10% of the selling price =10.50; payment fee 3.63; values before platform-fee tax |
| Restaurant: discount 20, merchant 8 and platform 12 | Products 85 + delivery 12 + service 2.43 =99.43 | Percentage base 97; commission 10% =9.70; platform funding does not reduce the base |
| Exempt restaurant link, products 105 | Customer price and service as in a normal order | Contract fee 0; payment fee 3.63 remains; customer service is not exempted |
| Mart: same 100, merchant percentage 4% | Sale price does not change with a change in the merchant percentage alone | Merchant commission 4; markup rate 5 is independent |
| Driver: full delivery 12, illustrative platform percentage 10% | The customer's discount does not change the driver pay base | Net delivery without tax 10.43; platform percentage 1.04; due 9.39; tip is independent |
| Fee-contract restaurant: new customer at the branch, two orders at selling price 20 then 40 | Customer pays the selling price | Fee 2 then 5; continues until the customer's total at the branch reaches 30; no percentage |
| Restaurant not registered for VAT, 10% contract percentage: products at selling price 115 | Customer pays 115 including VAT and the merchant's share enters its branch's Moyasar wallet<br/>The merchant issues the products invoice, and the platform issues its invoice for delivery and service only | Commission 11.50 + its VAT 1.73 are deducted; merchant receives 101.77 before the payment fee; product VAT 15 stays with them |

> In restaurants, the commission is calculated on the selling price or as a per-customer fee according to the contract. If there is a markup on the menu, the contract determines where it goes, not the platform's rules.

## Integrations

- **Moyasar** — hold, capture, and refund, plus merchant payouts by payment splitting into each branch's wallet with weekly payouts (Launch-critical)
- **STC Pay** — payout of driver dues after approval (Later; bank transfer at launch)
- **4jawaly** — verification code SMS messages (Launch-critical)
- **OpenLoyalty** — points, referral, and reward rules (Launch-critical)
- **Adjust** — source, links, and referral (Launch-critical)
- **OneSignal** — order and marketing notifications (Launch-critical)
- **PostHog** — visits, conversion, and product events (Launch-critical)
- **Odoo** — ledger, reconciliation and settlements, and automatic issuing of all invoices on command from the system (Launch-critical)
- **Google Maps** — route duration from the store to the customer (Launch-critical)
- **MCP** — role-scoped reports; financial reports with approval inside the dashboard (Launch-critical)
- **Cashier and partner interfaces** — sending the order and importing the product and the products invoice, optional or in write-in orders (per the first integration batch)
- **Call center** — calls, their recording, and distribution (Later; not Launch-critical and does not block launch)

## Quality and operations

- Four interfaces with permissions and city and branch scope; staff cannot exceed their role or their merchant's permissions.
- Arabic RTL first, full English, central texts, named and keyboard-accessible buttons, and clear contrast.
- Every page has loading, empty, error, and weak-network states; money and states are not updated from the customer UI alone.
- Riyadh time, amounts in whole halalas, round half up once per fee; tax and commercial calculations remain without separate compliance requirements.
- Prevent duplicate payment, acceptance, refund, reward, and entries; a durable scheduler for timeouts that survives a server restart.
- Finance is shown only to authorized users; a log of who did what, when, and before and after; manual payouts are approved by a different person.
- Home, sections, placements, values, and keys come from the server; exception order is branch, then city, then region, then global, per the value's setting.
- Three separate environments; daily backups and a restore drill; measurable performance targets; monitoring of payment, the scheduler, and integrations.
- The release is an update to the same store apps with the new platform's rules. Accounts and contracts are not migrated from the current app; balances are transferred manually as opening balances (TRN-001), and reference data is used through a one-time export with consent (TRN-002).
- Acceptance tests for every requirement, financial examples in halalas, and tests of photo paths, permissions, loss charge and penalty, and customer non-responsiveness.

## Before go-live

- **CFG-01 Specific operating values before launch**: The default platform percentage for drivers and tier benefits, delivery fees per city, limits for small refunds, loss charges, penalties, and negative balance (their defaults are in "Default values added in 4.11"). They are filled in Settings; not hard-coded.
- **INT-SEL Providers and the first integration batch**: connect 4jawaly for verification code messages, the payment methods actually tested with Moyasar, the first cashier systems, and the call center provider when it starts.
- **INT-PAY Payment splitting and driver payouts**: Written confirmation from Moyasar of the payment splitting terms (when the share is split, its fees, and recovery after a split), and confirmation of the STC Pay integration details (later) for payouts after approval: the payout interface available to businesses, amount and count limits, its fees, and how the wallet holder's name is verified. The STC Pay outcome decides the driver payout limits.

## Open questions

What remains unresolved. For each question: what it is waiting on, who resolves it, and what is blocked until it is resolved. Nothing that depends on an open question is coded before it is resolved; a requirement that refers here states the question number.

| Number | Question | Resolved by | Blocked until resolved | Requirements |
|---|---|---|---|---|
| **Q-01** | Written confirmation from Moyasar of the wallet model: a wallet per branch at capture, payout to the bank only on the platform's instruction after approval, deduction from the wallet before payout, holding a wallet until a new bank account is approved, and a daily reconciliation report | Owner with Moyasar | The actual Moyasar integration (the logic is built now) | PAY-006, INT-001 |
| **Q-02** | Reporting to the Transport General Authority (TGA): the required data, its format and timing, and whether connecting to the delivery platforms system at the Communications Authority is required | Owner with Legal | REG-007 | REG-007, DRV-001 |
| **Q-04** | Final terms of HRDF (Hadaf), and the list of controlled medicines or medicines prohibited from delivery. ("Wasfaty" is deferred: PHR-003 later) | Owner with Legal | Enabling pharmacies in production | REG-006, DRV-022, EXT-004, PHR-012 |
| **Q-06** | Approval of the data retention policy, especially sharing the entrance photo without consent | Legal | Automatic deletion and archive | CUS-001, DRV-028, TRN-004 |
| **Q-07** | Whether 4jawaly can send the code via WhatsApp, and the default channel | Owner with 4jawaly | WhatsApp channel (SMS works) | CUS-001 |

### Resolved

| Number | Decision | Dated |
|---|---|---|
| **Q-03** | Driver payouts at launch are by bank transfer after approval; STC Pay integration (INT-014) later | 29 October 2026, the owner |
| **Q-01 (hold)** | mada, Visa, Mastercard, Apple Pay, and Google Pay all support hold then capture (PAY-001) | 29 October 2026, the owner |
| **Q-05** | The chart of accounts, entries and fee basis table are approved (Appendix PAY-005) | 29 October 2026, the owner |
| **Q-08** | The merchant's opening balance is paid from the platform's bank in the first approval cycle, and does not pass through the Moyasar wallet (TRN-001) | 29 October 2026 |
| **Q-09** | The payout cycle is weekly by default, and it is a setting | 29 October 2026 |
| **Q-10** | In prescription disputes, support relies on the pharmacist's description; it does not see the prescription photo | 29 October 2026 |
| **Q-11** | The Mart markup is a fee on the merchant with 15% VAT in the fees invoice; the merchant invoices the customer at the full selling price | 29 October 2026 |
| **Q-12** | Branch wallets at Moyasar on the balance sheet as a restricted asset with an offsetting liability | 29 October 2026 |
| **Q-13** | Existing driver deposit: 50 SAR from each of the first two weeks, and the rest from the following weeks, without suspension | 29 October 2026 |
| **Q-14** | The notifications button on the home screen opens a pop-up list of notifications from the last 30 days, and each notification opens its destination | 29 October 2026 |

**The question is closed** by amending the relevant requirement and moving it to "Resolved" with the date and who resolved it.

## Pages

### Customer app

#### C01 — Home

Access to the sections and stores available for the customer's address.

- Elements: Delivery address: the address name, its district, and its city in the header, not just "My address", Notifications bell: in the header, Unified search: a search field for all sections (CUS-004), Current order: a card at the top of the page with the store name, status badge, arrival time in minutes and arrival clock time (ORD-011), and the four status steps (looking for a driver, being prepared, out for delivery, delivered); with more than one current order, a single card "You have N current orders", Restaurants, Mart, Shops, and Pharmacies: the four sections with their visibility and order by the customer's city (CUS-009), City banners: carrying a visible "Ad" tag, as does any paid row (CUS-003), Featured stores: a row of stores, Discounted products: a row of products with a discount, Suggestions: a "Suggestions for you" row with a reason line beneath: an item the customer ordered before or their dietary preference (CUS-003); for a new user, a fallback row "Most ordered in your city", Store card in the rows: rating, arrival time as a single number, delivery fee, and the Quality badge (MKT-014); each merchant has a single store, the nearest open branch whose zone covers the address (CUS-003)
- Actions and what happens:
  - **Change address**: opens Addresses (C13). After another address is chosen, the sections, stores, and fees refresh immediately (CUS-003) with a transient notice "We updated the stores for your address". An address outside coverage goes to C24. If the new address is outside the zone of the cart's branch, the cart stays with its branch and payment in it is disabled, and "Open branch ..." appears with a new cart if another branch of the merchant covers the address (CRT-001).
  - **Search**: opens Search (C02) with the cursor in the field and the keyboard visible, with recent searches.
  - **Open a section**: opens the section page: Restaurants C03, Mart C04, Shops C05, Pharmacies C06, for the current address's city.
  - **Open a store**: opens C07; a write-in Shops store and a pharmacy open C17 (CUS-009).
  - **Open the current order**: opens Tracking (C11); for a self-pickup order C16; for an order awaiting the customer's reply on an out-of-stock item C12. With more than one current order it opens "My orders" (C10).
  - **Open an ad banner**: opens the linked store or offer; the offer terms appear before adding to the cart.
  - **See all**: opens the list of the section the row belongs to, in the same order as Home.
  - **Open a discounted product**: opens C08 inside its store, with the pre-discount price struck through.
  - **Open notifications**: Opens the customer's notifications list (a pop-up list of notifications from the last 30 days, and each notification opens its destination).
- UX decisions:
  - The current-order card sits above the sections because it is the first thing someone returning to the app during an open order looks for, and the status is a badge and steps, not text alone.
  - The full address in the header explains why these stores appear, and changing it takes one tap.
  - The store card numbers allow comparison without opening the store.
  - The suggestion reason line builds trust and explains the ordering.
- Requirements: CUS-003 CUS-004 CUS-009 MKT-014 ORD-011
- Navigates to: C02 C03 C04 C05 C07 C10 C13 C11 C16 C12 C24 C08 C17 C26
- Special states: New user with no orders: "Suggestions for you" is replaced by "Most ordered in your city" and the in-progress order card does not appear; the page is never empty.; Address outside coverage: the page moves to C24 (no driver or coverage) with a change-address button.; Section disabled in the city: it disappears from the sections grid and the remaining sections move up in the city's order.; A store closed now: appears with a "Closed · opens 4:00 PM" tag at the end of the row and is not shown as available.; A store outside the customer's city: does not appear in any row, nor in "Suggestions for you".; Pharmacy order in progress: the in-progress order card says "Your order from the pharmacy" without any medicine name.; No offers or discounted products in the city: the whole row is hidden instead of being shown empty.

#### C02 — Search and results

Search across sections with alternatives when nothing matches.

- Elements: Search term: a field, and before typing the recent searches appear; the spelling correction is visible, such as "Showing results for burger · Search for burgir as typed", Results by section: chips All, Restaurants, Mart, Shops, Pharmacies, with the result count on each chip, Filters: category, offers, delivery fee, self-pickup, rating (CUS-004), Sort: a chip with the current sort name (CUS-004), Store card: rating, arrival time as a single number, delivery fee, offer tag if any, and the Quality badge (MKT-014), Mart product result: the grocery name and the product's price there, A "Can't find your store? Suggest a store" card: below all results, Suggestion form: store name, and the district or a note (optional)
- Actions and what happens:
  - **Filter**: a bottom sheet with the filters and a button "Show N results" whose count updates with each choice. On apply the results update and the active filters appear as chips above the list with "Clear all".
  - **Open a store**: opens C07, or C17 for a write-in store or a pharmacy. On return the term and filters remain.
  - **Suggest a store**: opens the suggestion form inside the page with the store name pre-filled from the search term. On submit it is logged with the city and the search term (ADM-039), a transient notice "Your suggestion was received, thank you" appears, and the alternatives stay visible.
  - **Sort**: a single-choice list (CUS-004); the order refreshes immediately and its name appears on the chip.
  - **Select a section**: the chip limits the results to the section; "All" returns them grouped under section headings.
  - **Clear the search**: the × button empties the field and shows recent searches.
  - **Search as typed**: cancels the correction and repeats the search with the original term.
  - **Open a product**: opens C08 inside its grocery or store.
  - **Submit the suggestion**: as in "Suggest a store"; the button is disabled while sending, then becomes "Suggestion sent" and both fields are cleared.
- Validation and error messages:
  - Search term: search starts from two characters.
  - Store name is required: when submitted empty, "Enter the store name" appears below it in red.
  - District or note: 120 characters maximum with a counter.
- UX decisions:
  - The field border takes the brand color while typing, and the × clears with one tap.
  - The spelling correction is visible with an option to undo, so what the customer typed is not lost.
  - The result count on the section chips shows where the results are before tapping.
  - The "Suggest a store" card is always present because the results may not include the store the customer wants.
  - In the no-result state, the alternatives come before the suggestion form so the customer still has something to order now.
- Requirements: CUS-004 ADM-039 MKT-014
- Navigates to: C07 C21 C08 C17
- Special states: No result: the message "No ... delivers to your address", then close alternatives from the same category, then the suggestion form; the term is logged as a search with no result (ADM-039).; A result not available for the address does not appear (CUS-004) and is not counted in the chip counts.; A store closed now: at the end of the list with the tag "Closed · opens ...".; Filters emptied the results: "No results with these filters" with a "Clear filters" button, and the alternatives and suggestion form are visible.; A duplicate suggestion from the same customer for the same store: "You suggested this store before, we received your suggestion" without a new record.; A merchant with several branches: a single store appears for it, the nearest open branch whose zone covers the address; if all its branches are closed, the nearest one appears with the tag "Closed · opens ..." (CUS-004).

#### C03 — Restaurants

Browse restaurants with an active menu.

- Elements: Restaurant count: in the header, the number of restaurants that deliver to the address, Categories: category chips, including "All", Current sort chip: visible and highlighted, Filters: categories, self-pickup, offers, rating, distance, arrival time, Restaurant card: the Quality badge on the image (MKT-014), the delivery fee as a number, and the arrival time as a single number, not a range (ORD-011), Card tags: "Closes in N min" in red near closing (CUS-005); an offer tag (discount or free delivery) if the offer applies to it (CUS-005); "Self-pickup" for restaurants that offer it
- Actions and what happens:
  - **Open a restaurant**: opens C07 on the active period's menu (CUS-005). With the self-pickup filter it opens in the pickup path (C15).
  - **Sort**: a single-choice list: nearest, fastest, highest rated, lowest delivery; the order refreshes immediately.
  - **Filter**: a bottom sheet with the filters; the button "Show N restaurants" applies and closes, and the active filters are removable chips.
  - **Select a category**: the chip limits the list to the category, and "All" removes the restriction.
  - **Enable self-pickup**: limits the list to restaurants that offer it, the time becomes "Ready in", and the delivery fee disappears from the cards.
- UX decisions:
  - The arrival time as a single number matches what the customer sees in the cart and tracking, so there is no surprise difference.
  - The delivery fee as a number, not a generic phrase, because it is part of the choice decision.
  - The red near-closing tag protects the customer from a cart that will not complete.
  - Shorter images (92 pixels) show three restaurants above the fold instead of two.
- Requirements: CUS-005 CUS-009 MKT-014 ORD-011
- Navigates to: C07 C15
- Special states: No restaurants with an active menu now: "Restaurants are closed now" with the nearest opening time and a "Browse Mart" button.; A restaurant with no active menu at this hour: does not appear in the list.; Self-pickup filter with no results: "No restaurants offer pickup near your address" with a "Cancel filter" button.; A merchant with several branches: a single store appears for it, the nearest open branch whose zone covers the address; if all its branches are closed, the nearest one appears with the tag "Closed · opens ..." (CUS-003).

#### C04 — Mart and groceries

Choose a known grocery, then its products.

- Elements: Fixed message above the list: the cart is from one grocery, the order is prepared from it only, with no self-pickup (DSP-005), Available groceries: a card for each grocery with the Quality badge (MKT-014), closing time, and distance, Arrival time and delivery fee: two numbers on each grocery card, Offers: the grocery's offer tag as written, Sections inside the grocery: shortcuts inside its card to enter the section directly
- Actions and what happens:
  - **Open a grocery**: opens C07 in Mart mode: the grocery's sections and its enabled products and local prices only (MER-010).
  - **Search for a product**: opens C02 limited to Mart; every product result shows its grocery name and its price there, and opening it enters that grocery.
  - **Open a section inside a grocery**: the section chip in the grocery card opens C07 scrolled to that section.
  - **Sort and filter**: selection chips: nearest, open now, offers, lowest delivery; applied immediately.
- UX decisions:
  - The single-grocery message at the top of the list prevents the expectation of a "unified order" from several groceries.
  - The section shortcut inside the card saves a step for someone who knows what they want.
  - Showing the grocery and the price together in product search lets the customer choose while seeing the difference.
- Requirements: MER-010 DSP-005 MKT-014
- Navigates to: C07 C08 C09 C02
- Special states: No grocery open now: groceries carry the tag "Closed · opens ..." and adding to the cart is disabled.; A product the platform disabled centrally or a new merchant product not approved: does not appear (MER-010).; Adding a product from another grocery while the cart has a grocery: the "Start a new cart?" dialog as in C07.; A Mart merchant with several groceries: a single grocery appears for it, the nearest open grocery whose zone covers the address; if all are closed, the nearest one appears with the tag "Closed · opens ..." (CUS-003).

#### C05 — Shops

Manual categories at the top of the page and the stores below them.

- Elements: Categories: a grid of manual categories with icons at the top of the page (CUS-009), the selected one highlighted, Stores: a list under the grid, titled with the selected category's name and the store count, Order type: products or write-in: a tag on each store "Order from products" or "Write your order", "Write your order" explanation: a short line: delivery now, then the products invoice, Time and fees: arrival time as a single number and the delivery fee as a number for each store, Quality badge: on the store (MKT-014)
- Actions and what happens:
  - **Select a category**: highlights the category and limits the list to it, and its title becomes "[Category] · N stores".
  - **Open a store**: a products store opens C07; a write-in store opens C17 (CUS-009).
- UX decisions:
  - Categories are an icon grid, not horizontal chips, so all appear without side scrolling.
  - The order-type tag in two different colors clarifies the difference between the two paths before tapping.
  - The "Write your order" explanation line prevents the surprise of two-stage payment.
- Requirements: CUS-009 MER-053 MKT-014
- Navigates to: C07 C17
- Special states: A store converted from write-in to menu: its tag becomes "Order from products" and it opens the menu; as long as the conversion is not published it stays "Write your order" (MER-053).; A category with no stores in the customer's city: does not appear in the grid.; A closed store: dimmed with the tag "Closed · opens ..." at the end of the list.; A merchant with several branches: a single store appears for it, the nearest open branch whose zone covers the address; if all its branches are closed, the nearest one appears with the tag "Closed · opens ..." (CUS-003).

#### C06 — Pharmacies

Choose a pharmacy, then write the order.

- Elements: Privacy message at the top of the page: the prescription is seen only by the pharmacist, not the driver, and the notifications read "Your order from the pharmacy" with no medicine name (PHR-012, PHR-008), Pharmacies that deliver to the address: each pharmacy has its status (open, or closed with the opening time) and the Quality badge (MKT-014), and a "Write your order" button on open ones, Arrival time and delivery fee: for each pharmacy, "My prescription" tag when available: with the explanation "Medicine at no cost, delivery only" (PHR-003), A "How your order works" card: four steps: write and attach the prescription, pay for delivery, pharmacist reviews and sends the products invoice, pay within 10 minutes and then the driver picks up (PHR-012), Prescription message: if the medicine needs a prescription and none is attached, the order is cancelled (PHR-012)
- Actions and what happens:
  - **Open a pharmacy**: opens C17 for this pharmacy; there is no menu for pharmacies (EXT-004).
  - **Write an order**: the "Write your order" button opens C17 directly with the cursor in the order text field.
  - **Search for a pharmacy**: opens C02 limited to pharmacies that deliver to the address.
- UX decisions:
  - The privacy message is the first thing the customer sees because the prescription is sensitive information.
  - A "Write your order" button on every open pharmacy makes the main action one tap.
  - The four steps set expectations for two-stage payment and the window before starting.
  - A closed pharmacy stays visible instead of disappearing, so the customer knows when it opens.
- Requirements: PHR-003 PHR-012 EXT-004 PHR-008 MKT-014
- Navigates to: C17 C02
- Special states: A closed pharmacy: dimmed at the bottom with the tag "Closed · opens ..." and no write button.; No pharmacy delivers to the address: "No pharmacy delivers to your address now" with a change-address button.; No self-pickup for pharmacy orders at launch: the pickup option does not appear in this section.; A merchant with several pharmacies: a single pharmacy appears for it, the nearest open pharmacy whose zone covers the address; if all are closed, the nearest one appears with the tag "Closed · opens ..." (CUS-003).

#### C07 — Store page

Show the store's details and its products, or its write-in path.

- Elements: Name, rating, and favorite: the store header (CUS-005), next to the logo the Quality badge (MKT-014) and the active menu period tag such as "Evening menu", Preparation time: in the header, Offers under the preparation time: a card directly under the preparation time, containing approved platform offers and merchant offers together (CUS-005), Delivery and minimum: three numbers with their units: minimum in SAR, arrival in minutes as a single number (ORD-011), delivery fee in SAR, Near-closing sticker: a countdown and the closing time (CUS-005), Search: inside the store menu, Active menu or grocery sections: the active period's menu (MER-005); in grocery mode its sections instead of menu categories, with its enabled products and local prices (MER-010), Price and options: on each product's line (CUS-005); a bundled meal carries the tag "Bundled meal" and a description of its components, Cart bar: item count and amount, and the remainder to the minimum or to free delivery with a progress bar (CRT-002), and the cart expiry time (CRT-004), "Start a new cart?" dialog: when adding while the cart belongs to another store (CRT-001), naming the store and the number of items that will be deleted
- Actions and what happens:
  - **Favorite**: adds the store to favorites immediately and the heart fills red, with a transient notice "Added to favorites"; a second tap removes it.
  - **Share**: opens the phone's share sheet with the store's link and name.
  - **Search**: shows this store's matching products on the same page; × restores the full menu.
  - **Open a product**: opens C08.
  - **Add to cart**: the + button on a product with no required options adds it once per tap and the bar updates immediately; a product with required options (including the bundled meal) opens C08. If the cart belongs to another store: the "Start a new cart?" dialog before any change.
  - **View cart**: opens C09. The bar does not appear while the cart is empty.
  - **Start a new cart**: deletes the other store's items and adds the chosen item; it cannot be undone, so the button is red and names the store whose cart will be deleted.
  - **Keep my current cart**: closes the dialog with no change.
  - **Select a menu section**: scrolls the list to the section, and the sections bar stays fixed at the top of the screen while scrolling.
- UX decisions:
  - The near-closing sticker sits above the offers because it determines whether ordering is possible now.
  - The offers card has a distinct color.
  - The free-delivery progress bar above the cart button encourages adding without pressure.
  - The bottom navigation bar is hidden here so the cart button stays the main action within thumb reach.
- Requirements: CUS-005 MER-005 MER-010 MKT-014 CRT-002 CRT-004 MER-024 CRT-001 ORD-011
- Navigates to: C08 C09 C17
- Special states: Near closing: the sticker is orange; at closing it becomes "Store closed · opens ...", adding is disabled, and the cart expires (CRT-004).; Store closed: the page is browse-only, the buttons are disabled, and the opening time is visible.; A product outside its availability time or the active menu period, or an offer outside the branch zone: does not appear (CUS-005, MER-005).; A product unavailable now (a meal whose component is out of stock with no substitute, MER-024): dimmed with no add button and the tag "Not available now".; A store not participating in a free-delivery offer: no free-delivery bar (CRT-002), and only the remainder to the minimum appears if it is not met.; Minimum not met: the bar reads "Add N SAR to reach the minimum".; Customer returns after the cart expired (CRT-004): the message "Your previous cart expired" and the app re-validates the items or starts a new cart.; A write-in Shops store or a pharmacy: opens C17 instead of this page.

#### C08 — Product details

Choose the size, extras, and quantity at the displayed price.

- Elements: Image: the product image, Name and description: the product name and description; for a bundled meal the tag "Bundled meal" and a description of its components, Price: with the pre-discount price struck through when there is a discount, Sizes and extras: each extra's price next to it; in a bundled meal each component with its options and a tag "Required" or "Optional" (MER-024), and an out-of-stock option is dimmed with the phrase "Out today" and cannot be chosen, Availability: the availability time such as "Available until [time]", Quantity: + and − buttons, Add button: shows the total after options and quantity, such as "Add to cart · N SAR"
- Actions and what happens:
  - **Edit options**: choosing an option in a required component (single choice) or an optional extra (multiple) updates the price on the button immediately.
  - **Add to cart**: validates the required components, then adds the item with its options and returns to the store page with a notice "Added to cart" and an updated cart bar. If the cart belongs to another store: the "Start a new cart?" dialog (CRT-001).
  - **Change quantity**: + and − change the quantity by one per tap and the amount on the button updates; − is disabled at 1.
  - **Close**: × returns to the store page without adding.
  - **Open a similar meal**: in the unavailable state: opens the similar meal's details.
- Validation and error messages:
  - Required component with no choice on add: the page scrolls to it and "Choose the drink type" appears below it in red, and the item is not added.
- UX decisions:
  - Each component sits in its own card with a "Required" tag so the customer knows what remains before adding.
  - Single-choice options are large, easy-to-tap cards instead of small radio buttons.
  - An out-of-stock option stays visible and dimmed so the customer does not look for it.
- Requirements: CUS-005 CRT-001 MER-024
- Navigates to: C09 C07
- Special states: Bundled meal unavailable (MER-024): an "Not available now" badge and a written reason, the add button disabled, and similar available meals shown.; An option in a component is out of stock and has a substitute: the option is dimmed and the meal stays available.; The product's availability time ended while the page is open: "No longer available now" and adding is disabled.; Page opened from the cart for editing: the saved options are selected, and the button "Save changes" replaces the item instead of adding it.; Price changed while the page is open: the price updates with a short message "Price changed".

#### C09 — Cart and checkout

Review the amount, address, and out-of-stock policy before confirming payment.

- Elements: Arrival time: in the header as a single number (ORD-011), Free-delivery bar: the remainder in SAR and a progress bar (CRT-002), Items: the cart items with their quantities and options, "Usually ordered with": suggestions from the same store with an add button (CRT-003), Non-binding note: the note field with a tag "Not binding on the store" next to it (CRT-001), Out-of-stock choice: three cards: remove it and don't charge for it, call me, cancel the order; with "Call me" the registered number or "Another number" (MER-032), Address: the delivery address, Tip: amount chips, with an explanation: it includes 15% VAT and the rest reaches the driver (example: of 10 SAR the driver gets 8.70), Coupon: a code field and an "Apply" button, Wallet: a toggle to use the balance, Products, delivery, and service: the payment summary with its lines (CRT-005), and the service with its percentage (PAY-021), Card and total: the chosen payment method, and a button with a verb and an amount "Pay N SAR" with the hold line above it "We hold the amount and capture only what is due when the order is closed", Cart expiry time: shown when it approaches (CRT-004)
- Actions and what happens:
  - **Edit quantity**: + increases by one per tap; − at 1 asks "Remove [item] from the cart?". Every change recalculates the bar, the service, and the total immediately (CRT-002).
  - **Choose out-of-stock handling**: one choice from three cards. "Call me" shows the registered number partially masked and an "Another number" link opens a mobile field. The choice is saved on the order (MER-032).
  - **Choose payment**: opens the payment methods sheet: enabled methods only (PAY-001), and Tabby and Tamara when the installment limit is reached (PAY-015). The choice is saved for future orders.
  - **Confirm payment**: the server re-validates price, availability, minimum, whether the address is within the branch zone, and store status (CRT-001); if anything changed, a differences review appears and nothing is held. Then the amount is held (PAY-001). Success creates the order and goes to C11 with the cancel button with a counter (ORD-002). Failure does not create an order and keeps the cart.
  - **Add a suggestion**: adds it once per tap (CRT-003), the button temporarily becomes a checkmark, and the summary and bar update.
  - **Edit options**: opens C08 in edit mode with the saved options selected.
  - **Change address**: opens C13; after the choice the delivery fee, eligibility, and arrival time are recalculated, and an address outside the branch zone disables payment (CRT-001).
  - **Choose a tip**: one chip from none/3/5/10 SAR; added as a line in the summary and does not change the service fee (PAY-004).
  - **Add a coupon**: opens the field; a valid code adds a "Discounts" line and recalculates the service (PAY-021).
  - **Use the wallet**: the toggle draws from the balance up to the amount due and a "From wallet" line appears; the rest is held on the payment method (PAY-004).
  - **Write a note**: saved with the order and shown to the merchant (CRT-001); it does not change the price.
- Validation and error messages:
  - Invalid or expired coupon: below the field in red "The code is invalid or has expired".
  - A coupon that does not apply to this store or has a minimum: "This coupon does not apply to your order" with its condition.
  - The other number for "Call me": a Saudi mobile of 10 digits starting with 05, otherwise "Enter a valid mobile number starting with 05".
  - Note: 200 characters maximum with a counter.
  - The out-of-stock choice is preselected with the customer's last choice, or "Remove it" if none exists (MER-032).
- UX decisions:
  - The hold line above the pay button reassures that the amount is not captured before closing.
  - The free-delivery bar is at the top of the cart because it changes the add decision.
  - The out-of-stock choice uses visible cards instead of a dropdown that hides the alternatives.
  - The arrival time before payment is the same one that appears in tracking.
- Requirements: CRT-001 CRT-005 PAY-004 PAY-021 ORD-002 CRT-002 CRT-003 CRT-004 ORD-011 PAY-001 PAY-015 MER-032
- Navigates to: C10 C12 C13 C08 C11
- Special states: Empty cart (last item removed): return to the store page.; Disconnection after payment: the app queries the order without repeating it.; Cart expired (CRT-004): when opened "Your cart expired" and the app re-validates the items or starts a new cart.; Minimum not met: the pay button is disabled with the text "Add N SAR to reach the minimum".; Eligible for free delivery: the bar turns green "Delivery is free for this order" and the delivery line is 0.00.; The saved payment method was disabled by the platform (PAY-001): it disappears from the sheet, and another method must be chosen before payment.; Address outside the branch zone: the cart stays with its branch and does not move; a red message above the summary and the pay button is disabled, and "Open branch ..." appears with a new cart if another branch of the merchant covers the address (CRT-001).; Self-pickup order: no address, no delivery, no tip, and no free-delivery bar (PAY-021).; Hold in progress: the button is disabled with an indicator and the text "Holding…" so the request is not repeated, and the page is not closed by going back.; A delivery offer and a discount offer on products combine in the order; two discount offers on products do not combine, so only the one with the higher saving applies (MKT-007).

#### C10 — My Orders

Current and past orders with status, source, and fulfillment method.

- Elements: current orders: "Current" tab with the order count, past orders: "Past" tab, and a "Cancelled" tab showing the final statuses verbatim, status and arrival time: a color-coded badge per status (Looking for a driver, Preparing, On the way, Delivered, Ready for pickup), and the arrival time as a single number for the active order (ORD-011), money status per order: "Amount held" for active, "Paid" for delivered, "Hold released" or "Refunded" for cancelled, and "Awaiting support decision" until support decides the amounts, message while waiting for the customer's reply inside the card: out-of-stock item with a countdown (MER-032), or a products invoice to pay with a 10-minute countdown, fulfillment method: delivery, or "Pick it up yourself" with closing time, search and filters: in "Past", purchase order and products invoice if available: "Purchase order" and "Products invoice" links, with the products invoice only if the merchant uploaded it (PAY-007), reorder dialog: price differences and unavailable items (CUS-006)
- Actions and what happens:
  - **Track**: opens C11 for delivery; for a self-pickup order the button becomes "Directions" and opens C16.
  - **Reorder**: creates a cart from the same store (CUS-006) and shows the differences dialog: "Price changed" with both prices, "Same as before", "Unavailable today · will not be added". "Review cart" opens C09. If a cart for another store exists: the customer is asked before replacing it. Store closed: "Store is closed now · opens ..." and no cart is created.
  - **Support**: opens C21 with the order linked to the ticket.
  - **Open details**: opens C19: purchase order, products invoice, and rating.
  - **Choose now**: on an order waiting for a reply about an out-of-stock item: opens C12.
  - **Pay the products invoice**: on a write-in order awaiting payment: opens C18.
  - **Open purchase order**: shows the purchase order with its line items and payment source (PAY-007).
  - **Open products invoice**: shows the products invoice image uploaded by the merchant (PAY-007).
  - **Search and filters**: search by store name or order number, with a type filter (delivery, self-pickup, write-in, pharmacy) and a period filter.
  - **Switching tabs**: Current, Past, Cancelled; scroll position is kept per tab.
- UX decisions:
  - "Choose now" is a primary button with a countdown because the deadline is running.
  - Money status is visible on every card so the customer does not think they paid twice.
  - The reorder dialog shows the differences before payment so the customer is not surprised by a different price.
- Requirements: CUS-006 ORD-001 PAY-007 ORD-011 PAY-001 MER-032
- Navigates to: C11 C16 C19 C21 C12 C18 C09 C01
- Special states: no current orders: "No current orders right now" and a "Start an order" button to the home page.; order closed without delivery: in "Cancelled" with its final status ("Cancelled" or "Ended") and the closing reason (cancellation within the grace period, support decision, out-of-stock item, non-payment, rejection before the products invoice) and the amount status.; order awaiting a support decision: an "Awaiting support decision" badge with no final amounts until it is closed.; old order from a Mahallat store that switched from write-in to menu: stays with its two payments and its products invoice.; reorder where none of the items are available: "None of the items in this order are available today" and no cart is created.; order awaiting a reply about an out-of-stock item: the message is orange, and the "Choose now" button is the primary button on the card.

#### C11 — Track Order

A map, status, and an overall arrival time with no code.

- Elements: map: top of the page (CUS-007), remaining time: a single arrival time in minutes and the arrival clock time, without breaking down the components (CUS-007, ORD-011), status line: the four customer-facing status steps, driver: first name, transport type, and a "Hidden number" tag, call and chat: two buttons directly next to the driver, address instructions: the address card and its instructions, fix location: a button in the address card, leave at the door: an "Leave it at the door" switch with an explanation of the photo (ORD-010), and after dropping off, a photo of the order in place, cancel order card: with a countdown, within the grace period only (ORD-002), showing its effect "The full N SAR hold is released"
- Actions and what happens:
  - **Call**: a call through a proxy number (CUS-008). Disabled after the contact period ends.
  - **Chat**: opens C25. Disabled before a driver accepts, with the text "Chat is available when a driver accepts".
  - **Fix location**: opens the map to move the pin (C13), then "Confirm location". Same fees: the location updates immediately and the driver is notified. Farther location: a "Delivery fee difference X SAR" dialog with two buttons "Pay the difference" and "Continue to the first location", and the location does not change before payment. Rejection and out-of-zone follow (ORD-009); for out-of-zone the message "Your request reached support and they will contact you" is shown.
  - **Ticket**: opens C21 with a ticket linked to the order.
  - **Leave it at the door**: the switch saves the choice immediately (ORD-010) with a transient notice "The driver will leave your order at the door and photograph it". It can be turned off before the driver arrives.
  - **Cancel the order**: within the grace period only (ORD-002). Confirmation "Cancel the order? The full N SAR hold is released" with two buttons "Yes, cancel the order" and "Go back". Confirming turns the page into "Order cancelled". When the countdown ends the button disappears with no explanation, and "Ticket" remains.
  - **View drop-off photo**: opens the photo taken by the driver at full size.
- Validation and error messages:
  - Fix location without moving the pin: the confirm button is disabled with the text "Move the pin to the correct location".
- UX decisions:
  - The duration number is large with the arrival clock time, and it is the first piece of information after the map.
  - Cancellation is a visible countdown on the card instead of an explanatory sentence, and the confirmation states the financial effect.
  - The "Hidden number" tag next to the call button reassures the customer.
  - A slightly shorter map so the four important cards appear above the fold.
- Requirements: CUS-007 ORD-009 ORD-010 CUS-008 ORD-011 PAY-001 PHR-008 ORD-002
- Navigates to: C21 C13 C19 C25 C16 C24 C12 C10
- Special states: no driver after 15 minutes: the page moves to C24.; driver approaching: a "Your driver is approaching" notification and the map updates (CUS-007).; preparation change, reassignment, or order batching: the number updates (ORD-011), and the driver card changes with a notification.; order awaiting a reply about an out-of-stock item: an orange top bar "Item out of stock · your reply is needed" with a countdown that opens C12.; awaiting payment of the location-fix difference: an "Awaiting payment of the difference" badge, and the driver heads to the first location.; delivered: the drop-off photo is shown if present, then the customer moves to C19.; self-pickup order: opens C16 instead of this page.; pharmacy order: notifications follow (PHR-008).

#### C25 — Chat with Driver (new)

Chat and call with the driver within the order using hidden numbers, closed a set time after the order closes.

- Elements: header: the driver's first name, order number and its status, and a call button using a hidden proxy number, fixed message at the top of the chat: numbers are hidden, and the chat closes 24 hours after the order ends (CUS-008), messages: with the time of each message and its status (sending, delivered, not sent), system messages: when a number is hidden "We hid a phone number from your message, and it did not reach the driver", and when "Leave it at the door" is enabled from the chat, quick replies: leave it at the door, I'm at the door, call me on arrival, input field and send button, message removal request dialog: the message and an optional reason
- Actions and what happens:
  - **Send message**: sends the text; any phone number is replaced with "[hidden number]" (CUS-008) and the sender sees a system message. The message appears immediately as "Sending" then "Delivered".
  - **Call**: a call through a proxy number (CUS-008); disabled after contact is closed.
  - **Quick reply**: sends the text with one tap. "Leave it at the door" actually enables the same option in C11, not only as text (ORD-010), with a system message confirming it.
  - **Message removal request**: a long press on a message written by the customer opens the "Request removal of this message" dialog. Submitting sends it to platform staff and a "Removal requested" tag appears under the message until a decision; the message is deleted only by a platform staff decision.
  - **Back**: returns to C11 and the draft stays in the field.
- Validation and error messages:
  - Empty message: the send button is disabled.
  - Message length: 500 characters maximum with a counter when approaching it.
- UX decisions:
  - The hidden-numbers message at the top of the chat answers the privacy question before it is asked.
  - The system message when a number is hidden explains to the sender why their message changed.
  - Quick replies sit above the field.
  - The call button is in the header, and send is a large button within thumb reach.
- Requirements: CUS-008 ORD-010
- Navigates to: C11 C21
- Special states: new chat with no messages: "Start the chat with your driver" and the quick replies are visible.; before a driver accepts: no chat; its button in C11 is disabled.; driver changed (reassignment): a new chat with the new driver, and the old one is read-only.; after the order closes: the chat stays open until the end of the period (CUS-008), then read-only and the call button is disabled.; network loss: the message is in the "Not sent · Retry" state and its text is not lost.

#### C12 — Out-of-Stock Item and Substitute

Customer approval, or applying their pre-selected choice after 3 minutes.

- Elements: reply countdown: a large circular countdown at the top of the screen that starts the moment the merchant taps "Out of stock" (MER-032), the out-of-stock item: by name, pre-selected choice: the customer's pre-selected choice, and the number the store will call, partially masked, substitute and its price: the substitute proposed by the store with its name and price, price and service difference: the item price difference and the service fee difference, then the amount added to the hold, deadline line: with no reply before it ends, the item is removed and its price is not charged (MER-032), auto-cancellation result screen: the reason "Out-of-stock item" and the amount whose hold was released
- Actions and what happens:
  - **Accept the substitute**: for a pricier substitute: the button "Accept the substitute and pay N SAR" holds the difference on the same payment method (PAY-028); success locks in the substitute and moves to tracking with an "Item replaced" notification, and failure removes the item and the customer is informed with a message (MER-032). For a cheaper or equal-priced substitute: "Accept the substitute" with no payment (PAY-028).
  - **Remove**: the "Remove the item" button asks "Remove [item] from your order? The amount drops by N SAR". Confirming removes the item (PAY-028). If it is the last item: auto-cancellation and the result screen.
  - **Call me**: confirms to the store to wait for a call with the customer before acting, and shows the chosen number with "Another number" to change it for this item. It does not extend the deadline.
  - **Cancel per choice**: the "Cancel the order" button asks "Cancel the whole order? The N SAR hold is released". Confirming cancels the order automatically (MER-032); nothing is charged to the customer. The result screen is shown.
  - **Order from another grocery**: on the cancellation screen: opens C04.
  - **Contact support**: opens C21 linked to the order.
- Validation and error messages:
  - Another number for "Call me": a Saudi mobile number of 10 digits starting with 05.
  - After the deadline passes: all buttons are disabled with the text "Time is up".
- UX decisions:
  - The countdown is at the top because time is the most important thing on the screen.
  - The cancel button is red and goes through a confirmation.
  - The result screen after auto-cancellation has a next step (another grocery) instead of a dead end.
- Requirements: MER-032 PAY-028 PAY-001 ORD-004
- Navigates to: C09 C11 C04 C21 C10
- Special states: the store has not proposed a substitute yet: "Awaiting the store's suggestion", and the accept-substitute button is hidden while remove and cancel remain.; the deadline passed without a reply: the screen shows "We removed the item · new amount N SAR" with a "Continue your order" button.; the merchant recorded the customer's reply after a call (replace, remove, cancel): the screen updates immediately with the result and the buttons are locked.; all items removed, or the pre-selected choice is "Cancel the order": auto-cancellation (MER-032) and the result screen is shown.; the pre-selected choice is "Remove it": this screen does not appear; a notification "We removed the item and will not charge for it" arrives.; cheaper substitute: a line "The amount drops by X SAR" instead of payment.; several out-of-stock items: a card per item with its own countdown.; pharmacy order: the out-of-stock notification uses the phrase "Your order from the pharmacy" without the medicine name.

#### C13 — Addresses

Managing locations, entry instructions, and no-answer handling.

- Elements: Saved locations: the address list with an edit for each address, the default with a badge, and a "Driver adjusted entrance location · saved" badge on the address whose entrance the driver corrected, "Use my current location" button: in the address picker list, Distance warning: "Your current location is [distance] from the chosen address" when choosing the address if it is 300 meters or more away (in meters under 1 km and in kilometers above) (CUS-002), Add steps: set location ← details ← save, Location confirmation: "Location confirmed" badge on the map (CUS-002), Short national address (optional): when entered, the pin moves to its location, and the customer still has to confirm it, Address name: Home / Work / Other (free text), Building, floor and apartment: three separate fields, Instructions: entry instructions, Entrance photo: an optional photo, Leave it at the door: under "What should the driver do if I don't answer": "Call me and wait" or "Leave it at the door"
- Actions and what happens:
  - **Add**: opens "New address" with the map on the device location. On save the address is added and becomes the selected one for the current order if the customer came from C09, with the message "Address saved".
  - **Edit**: opens the same form with the address values. Moving the pin cancels the confirmation and requires a new confirmation before saving. Editing does not change the address of an existing paid order.
  - **Confirm location**: fixes the current pin as the address location, shows the district and street name under the map, and enables the save button. "Edit location" returns the map to moving mode and cancels the confirmation.
  - **Choose an address**: makes the address the delivery address for the current order and returns to the cart. If the device location is far away, the distance warning appears first with a "Deliver to (address name)" button to continue, without blocking.
  - **Use my current location**: new: asks for location permission, then opens a new-address form with the pin on the current location, and it needs confirmation and saving like any address.
  - **Entrance photo**: new: opens the camera or gallery and attaches one photo that appears to the driver during delivery only. It can be deleted or replaced.
  - **Delete address**: new (from the edit dialog): confirmation "Delete the Home address? No existing order will be affected". The default address cannot be deleted until another default is chosen.
- Validation and error messages:
  - Building is required: "Enter the building number or name".
  - Short National Address in an incorrect format: "Check the code, example RRRD2929".
  - The National Address does not match a location: "We couldn't find this address, mark your location on the map".
  - Entry instructions: maximum length with a counter under the field.
  - The "Other" name is required when selected, and no two addresses share a name.
- UX decisions:
  - The map comes first and then the fields, because confirming the location is the save requirement that prevents mistakes.
  - Building, floor, and apartment in one row of three short fields instead of a combined field.
  - The no-answer option is a single visible choice rather than a checkbox, so the driver clearly knows what to do.
  - The driver's entrance correction appears as a badge so the customer understands why the pin changed.
- Requirements: CUS-002 ORD-008
- Navigates to: C01 C09 C24
- Special states: location not confirmed: the save button is disabled with "Confirm the location on the map to save the address" under it.; address outside coverage: on confirmation "We don't deliver to this location yet" with a "Notify me" button (C24), and the address can still be saved.; driver corrected the entrance: the entrance location in the saved address updates (CUS-002) and the blue badge appears.; location permission denied: the map opens on the city with the message "Enable location or move the map manually".; no saved addresses: "Add your first address" with an add button.

#### C14 — My Account

Access to balance, cards, addresses, tip, language, and support.

- Elements: account details: name and masked mobile number, wallet and cards: a balance card with a "Reward awaiting collection" line if one exists, and the default card abbreviated to its last digits, addresses: their count and the default address, auto tip: the amount and what reaches the driver after its included 15% VAT (CUS-010), with an on/off switch, points and invitation: the number of available points, notifications: notification settings, language: Arabic / English buttons directly in the row instead of a sub-page, help: "Support" with two options "Help with an order" or "Help with the app" (SUP-001), visitor card: "Browse freely, sign in when you order" and a sign-in button
- Actions and what happens:
  - **Edit**: Opens the name edit window. The mobile number cannot be edited from here; it is changed with a code sent to the new number (CUS-001). Saving updates the name immediately with "Your details were saved".
  - **Open wallet**: goes to C20, with the awaiting reward, if any, at the top of the page.
  - **Support**: a bottom sheet: "Help with an order" (latest orders, then C21 with the order context) and "Help with the app" (C21 with no order number).
  - **Sign out**: confirmation: "Sign out of this device? Your cart and addresses stay saved in your account". Afterwards the page shows in visitor state and browsing continues without a verification code.
  - **Auto tip (switch)**: new: turning it off is immediate with no confirmation and shows "We turned off the auto tip", so it is not added to later orders. Turning it on opens the amount or percentage selection (CUS-010).
  - **Language**: new: switches the app language and direction immediately without signing in again, and saves the choice in the account.
  - **Notifications**: new: turning off stops promotional notifications only, after a confirmation explaining that order status and reward notifications remain because they concern your orders and their deadlines (24 hours for the reward).
  - **Sign in**: new (for a visitor): mobile number, then the verification code by SMS (CUS-001).
- Validation and error messages:
  - Empty name: "Enter your name".
  - Mobile number in a non-Saudi format: "Enter a mobile number of 9 digits starting with 5".
  - Auto tip amount of zero or negative: "Choose an amount or turn off the auto tip".
- Permissions:
  - Visitor: any action that needs an account opens the sign-in dialog (CUS-001), then returns to the same action.
- UX decisions:
  - The balance card opens the wallet and shows the pending reward before it lapses.
  - Every row shows its current value under its name so the customer does not need to open it to know.
  - Sign out is in the danger color at the end of the list with a confirmation.
- Requirements: CUS-001 CUS-010 PAY-023 SUP-001
- Navigates to: C13 C20 C21 C22 C23
- Special states: visitor: a welcome card and a sign-in button, and wallet, addresses, and points are hidden.; wrong or expired verification code: a message under the field with "Resend" after a countdown.; auto tip turned off: the line shows "Off" with no amount.

#### C26 — Notifications (new)

All of the customer's notifications about their orders and offers for the last 30 days in one place.

- Elements: tabs: All, Orders, Offers (ADM-007), grouping: Today, This week, Older, the notification: type icon, title, details line, time, unread marker, and a status tag if any, notification for adding the store the customer suggested (ADM-039), retention period line (INT-004) and a link to notification settings in "My Account"
- Actions and what happens:
  - **Open a notification**: marks it as read and opens its destination: an order opens C11 or, after delivery, C19; a reward opens C20; an offer opens C22 or the store.
  - **Mark all as read**: the unread markers disappear and the bell counter on the home page becomes zero.
  - **Switch tab**: shows one type without reloading the page.
  - **Back**: returns to the previous page.
- UX decisions:
  - The unread counter on the home bell opens this page.
  - Unread is a colored dot next to the time, cleared by viewing.
  - Every notification opens its destination directly; no notification is without a destination.
- Requirements: INT-004 ADM-039 ADM-007
- Navigates to: C11 C19 C20 C22
- Special states: no notifications: "No notifications in the last 30 days" with a "Browse stores" button.; notifications turned off on the phone: a bar at the top of the page "Turn on notifications to get your order status" with a button to settings.

#### C15 — Pick It Up Yourself

Stores eligible for self-pickup; Mart is excluded.

- Elements: list and map: a single segmented control to switch between them, reference location for distance: "Near: Home" with the ability to change it, sort: Nearest / Fastest ready / Has pickup discount, distance: per store, ready time: per store, pickup discount: if any (EXT-006), working hours: a branch status badge next to the name: Open / Closes in X minutes / Closed, opens at X, directions button: per store, explanation line under the list: you pay, then the order reaches the store and you pick it up yourself; it does not include Mart, pharmacies, or write-in orders (EXT-006)
- Actions and what happens:
  - **Choose a store**: opens C07 in "Pick it up yourself" mode: no delivery fee and no tip, and the pickup discount, if any, is in the cart. A closed store does not open for ordering and shows its opening time.
  - **Open directions**: opens the maps app at the branch location without leaving or changing the order.
  - **Map**: new: switches the view to a map with pins for the eligible stores; tapping a pin shows the same store card.
  - **Sort**: new: reorders the list immediately per the selection.
- Validation and error messages:
  - Entering from a Mart store or pharmacy link: no pickup option, and the message "Self-pickup is not available for this store".
- UX decisions:
  - The list is the default view because it is faster for comparison.
  - The branch status is a colored badge next to the name so the customer does not order from a branch that is closing.
  - The directions button is separate from opening the store to avoid mis-taps.
- Requirements: EXT-006 ORD-002
- Navigates to: C07 C16 C13
- Special states: no eligible stores near you: "No pickup stores near this address" with a change-address button.; store closing soon: a warning badge; and an order whose ready time falls after closing is not accepted (EXT-006).; store closed: the card is faded with "Opens at X".; no location permission: the distance is from the default address, and this is shown under the address.

#### C16 — Your Order Is Ready for Pickup

A persistent page with no code, with directions and pickup notifications.

- Elements: store and branch: the store name, and the branch address and distance, order number: in large type with "No code needed · the employee confirms pickup by order number" (EXT-006), ready status: a "Ready for X minutes" badge, and steps: Paid -> Being prepared -> Ready -> Picked up, held amount: captured on pickup, reminder, delay, and end of working hours: the line "We will remind you if you don't pick up within 60 minutes, and if you don't come by end of working hours the order becomes 'Awaiting support decision'" (EXT-006), directions: the primary button in the sticky bar, with support as secondary next to it, line for an order converted from delivery: "You converted your order to pickup · delivery fee and tip refunded"
- Actions and what happens:
  - **Open directions**: opens the maps app at the branch location. The page is kept in "My Orders" and opens from the notification until pickup (EXT-006).
  - **Contact support**: opens C21 with the order context and number automatically.
  - **Confirm pickup (by the merchant)**: new, no customer button: when the merchant enters the order number the page becomes "Picked up" and the amount is captured, then the rating screen C19 appears.
- UX decisions:
  - The order number is the largest element because the customer reads it to the employee at the counter.
  - The held amount is visible with the time it will be captured so the customer does not worry about an early capture.
  - The end-of-working-hours rule is written in advance so the customer is not surprised by the closure.
- Requirements: EXT-006 ORD-004
- Navigates to: C21 C19 C10
- Special states: being prepared: before "Ready" the "Being prepared" step and the expected time appear, with no large number.; during the cancellation grace period (EXT-006): a "Cancel the order" button with a countdown, then it disappears.; more than 60 minutes since ready (EXT-006): a reminder notification and a yellow bar at the top of the page.; the customer did not come by end of working hours (EXT-006): the order is "Awaiting support decision", and the amount is held and not captured before the decision (the second preview).; picked up: a green badge and the pickup time, then the rating.

#### C17 — Write the Order and Pay Delivery

A text order with photos or a prescription, then the delivery payment.

- Elements: store: its name, order steps: write and pay delivery -> the pharmacist reviews -> pay the products invoice -> delivery, order text: a field with a character counter, photos or prescription: horizontal thumbnails of attachments with a "Prescription" tag and a delete on each attachment; and the text "Voice recording is not accepted" with no voice button (ORD-013), pharmacy message before payment: "A medicine that needs a prescription is cancelled if you don't attach one. The prescription is seen only by the pharmacist, not by the driver" (PHR-012), delivery fee, and an explanation that the products invoice will arrive for payment: delivery now, then the products and service invoice is paid within the deadline (ORD-013), payment method: the default card first with "Change" (PAY-023), pay button: "Pay delivery · N SAR"; and after payment a countdown on the cancel button only, with no explanation (ORD-002)
- Actions and what happens:
  - **Attach**: opens the camera or gallery (images only). Each image appears as a thumbnail and can be tagged "Prescription". An upload failure keeps the text and shows "Retry" on the thumbnail.
  - **Pay delivery**: at a pharmacy with no prescription attached, a "You didn't attach a prescription" dialog appears first (the second preview). After payment only the delivery is held and the order page appears with a "Cancel" button with a countdown, then searching for a driver and sending to the store (ORD-013). When the products invoice arrives a notification opens C18.
  - **Attach the prescription now**: new (in the prescription dialog): closes the dialog and opens the camera to attach the prescription.
  - **My order doesn't need a prescription**: new (in the prescription dialog): continues to payment; if the medicine does need a prescription, rejection and cancellation follow (PHR-012).
  - **Cancel within 60 seconds**: new: releases the hold in full and the order does not reach the store; after the deadline the button disappears and cancellation is through support only (ORD-002).
- Validation and error messages:
  - Order text is empty and there are no attachments: "Write your order or attach a photo".
  - Maximum character limit exceeded: input stops and the counter turns red.
  - A non-image file or one that is too large: "Attach an image in JPG or PNG format".
- Permissions:
  - Visitor: sees the page in a "Sign in" state, and any action that needs an account opens the mobile-number sign-in dialog (CUS-001), then returns to the same action.
- UX decisions:
  - The steps bar explains the two-part payment before the customer pays.
  - The prescription message is visible before payment, and repeats as a dialog only when nothing is attached at a pharmacy.
  - Prescription privacy is stated explicitly to reassure the customer.
- Requirements: ORD-013 PHR-012 PAY-023 ORD-002
- Navigates to: C18 C10 C21
- Special states: a write-in store that is not a pharmacy: no prescription message, and the attachment button reads "Attach photos".; store closed or outside coverage: payment is disabled with the reason.; pharmacist rejects for no prescription (PHR-012): the order page shows "The pharmacist rejected the order for no prescription · Awaiting support decision".; payment failed: the text and attachments remain, with the message "Payment did not go through, try another card".

#### C18 — Pay the Products Invoice

Shows the products invoice as the merchant uploaded it, with the 5% service shown separately.

- Elements: total due: the amount due now in large type at the top of the screen, 10-minute countdown: a circular countdown for the deadline next to the amount (ORD-013), mandatory products invoice image: a thumbnail with its upload time and the ability to zoom (ORD-013), products: the products invoice amount line, 5% service: a line separate from the products (PAY-012), prepaid delivery: outside the total with the line "Delivery was prepaid · not added to this amount", default payment method: with "No payment fee on pharmacy" (PAY-012), pay button: "Pay · N SAR", "Reject the products invoice" button: in the danger color
- Actions and what happens:
  - **Pay**: holds the products + service (PAY-012) on the selected card. Success stops the countdown, preparation begins, and returns the customer to C11. Failure keeps the countdown with "Payment did not go through, try again or change the card".
  - **Reject**: a confirmation dialog states the effect: rejection with no undo, the products invoice amount is not captured, and the delivery fee and tip are decided by support (ORD-013, CUS-010). After confirmation the order page becomes "Awaiting support decision".
  - **Support**: opens C21 with the order context and number, and the countdown continues, visible at the top of the chat.
  - **Zoom the products invoice**: new: shows the full products invoice image with pinch-to-zoom.
- Validation and error messages:
  - Products invoice image or amount missing (ORD-013): "The products invoice is incomplete, we are contacting the store".
- Permissions:
  - Visitor: sees the page in a "Sign in" state, and any action that needs an account opens the mobile-number sign-in dialog (CUS-001), then returns to the same action.
- UX decisions:
  - The amount and the countdown come first on the screen because they are what the customer needs to decide.
- Requirements: ORD-013 PAY-012 CUS-010 ORD-004 PHR-012
- Navigates to: C11 C21 C10
- Special states: under 2 minutes: the countdown is red with "Less than 2 minutes left".; deadline passed (ORD-013): "Payment deadline passed · the order is awaiting support decision", and the pay button disappears.; paid: both payments are held and are captured on delivery.; products invoice has not arrived yet: the page does not open, and tracking shows "The pharmacist is reviewing your order".

#### C19 — After Delivery

A separate rating, help, tip, and purchase order.

- Elements: delivery confirmation: the delivery time, and "This order's points are pending until the report window ends" (MKT-010), store rating and delivery rating: food rating (store) and delivery rating (driver) are separate, with quick reasons (CUS-006), tip: preset amounts or "Other", with what reaches the driver after its included 15% VAT (CUS-010), tip repeat: an "Use the same tip on my upcoming orders" option (CUS-010), submit button: fixed, sends the rating and tip together and states the tip amount if one is selected, report window: a report-window countdown (1 hour from delivery in all sections) and its end time (SUP-005), and the buttons "Report missing item" and "I didn't receive it", and for Mart "Damaged or expired item" with a photo, driver chat button (C25): while the chat is open, purchase order: a link, products invoice if available: the products invoice uploaded by the merchant, or "Not available" when absent
- Actions and what happens:
  - **Submit rating**: saves both ratings linked to the order (CUS-006) and pays the selected tip if any, then "Thank you for your rating". One rating is enough.
  - **Tip**: choose a preset amount or "Other"; it is captured from the default card on submit. "Use the same tip" makes it automatic (CUS-010), and the customer turns it off from C14.
  - **Report missing item**: opens C21 on "Missing or wrong item" with this order's items, with a photo from the app camera (SUP-002). It disappears after the window ends (SUP-005).
  - **I didn't receive it**: opens C21 on "I didn't receive it" with no photo, and the evidence file is attached automatically for support (SUP-002). It disappears after the window ends (SUP-005).
  - **Damaged or expired item**: new (Mart): opens C21 with the type "Damaged or expired" with a mandatory photo; within 1 hour of delivery like other reports, and the reply comes after support review, not automatically (SUP-009).
  - **Driver chat**: new: opens C25 for the same order.
  - **Purchase order**: new: shows the purchase order PDF with download and share.
- Validation and error messages:
  - "Other" tip amount: a positive number with two decimal places, otherwise "Enter a valid amount".
  - Comment: a maximum character limit with a counter.
- UX decisions:
  - Rating first, then tip, then the problem, in the order most customers act.
  - The net tip is visible so the customer trusts the amount.
  - The report window is a visible countdown so the customer is not surprised when it ends.
- Requirements: CUS-006 CUS-010 SUP-005 SUP-009 MKT-010 SUP-002
- Navigates to: C21 C25 C14
- Special states: after the one-hour window (SUP-005): all report buttons disappear, including the Mart report, and no report is accepted after it.; already rated: the stars are read-only with "Thank you for your rating".; self-pickup order: the delivery rating, the tip, and "I didn't receive it" are hidden.; tip payment failed: the rating is saved and "The tip was not paid, try again" is shown.

#### C20 — Wallet, Cards, and Reward

Balances clear by type and expiry, and reward actions.

- Elements: available balance: the total, with "We spend the soonest-expiring first, and refund credit last", and under the title "No top-up and no withdrawal" (PAY-002), 24-hour reward: the pending reward with its amount, reason, and a collection countdown, above the balances (PAY-002), refund, compensation, and promotional: the balances by type, ordered by soonest expiry, and each balance shows its source and expiry date on one line, card refund in progress: the amount, order, status, and arrival time (PAY-003), with "Move it to the wallet now", cards: "Saved with Moyasar and we do not store your full card number" (PAY-023), and "Default" and "Delete" buttons inside each card's row, default: a badge on the default card, balance activity: every addition, spend, and return, including a return of promotional credit from a cancelled order, reward page (from the notification): the amount, type, validity, and reason, and a large "Collect the reward" button that states the amount
- Actions and what happens:
  - **Collect the reward**: immediately adds the amount as compensation credit with its expiry date (PAY-002), the reward card disappears, a line appears in the activity, and the message "We added N SAR to your wallet". After the deadline the button is disabled and "The reward lapsed" appears.
  - **Add a card**: opens the secure Moyasar form to enter the card and verify. Success adds it with its last 4 digits and asks "Make it the default?". Failure shows Moyasar's reason in simple language.
  - **Delete a card**: confirmation "Delete the [type] •• [last 4 digits] card? It will not appear at payment". Existing orders held on it are not affected. Deleting the default asks to pick another if one exists.
  - **Change the default**: makes the card the default immediately with a short message (PAY-023).
  - **Move it to the wallet now**: new: confirmation "Move N SAR to your wallet instead of the card? It becomes refund credit that does not expire and does not return to the card"; afterwards it is added immediately (PAY-003).
  - **Open an activity entry**: new: shows the type, reason, reference (order number or ticket), date, and expiry date.
- Validation and error messages:
  - Moyasar rejects the card: "We couldn't add the card, check its details or try another card".
  - Collecting an expired reward: the button is disabled and the request is rejected on the server.
- Permissions:
  - Visitor: sees the page in a "Sign in" state, and any action that needs an account opens the mobile-number sign-in dialog (CUS-001), then returns to the same action.
- UX decisions:
  - The pending reward sits above the balances because it is the only thing lost if the customer does not act.
  - Deleting a card is in the danger color with a confirmation.
- Requirements: PAY-002 PAY-003 PAY-023 MKT-002
- Navigates to: C09 C14 C21 C23
- Special states: reward lapsed: it appears in the activity in gray "Not collected within 24 hours".; balance expiring within 3 days: a warning badge next to it.; cancelled order that used promotional credit: the balance is returned (PAY-003, MKT-002) and "Returned from order #..." is shown.; support decision amended: a reversing entry in the activity linked to the original "Ticket #... decision amended".; no cards: "Add a card to pay quickly" with an add button.; wallet is zero: an empty state explaining the balance sources (refund, compensation, referral prize, points).

#### C21 — Support and Tickets

Help with an order or with the app, with context and evidence.

- Elements: the order: a card with the number, store, status, and amount, and "The order number is attached automatically" (SUP-001), report-window countdown: 1 hour from delivery in all sections including Mart, next to the order (SUP-005), problem type: a grid of large cards with icons that change with the order status (SUP-001): before delivery "Where is my order" and "I want to cancel", after it "Missing or wrong item", "Damaged item", "I didn't receive it", and "Payment or amount", and for Mart "Damaged or expired item", items: choosing the affected items from the order's items, camera photo for damage: from the app camera only and the button says so explicitly (SUP-002), chat: the ticket chat, status: ticket steps Received -> Under review -> Resolved, and a "My tickets" list with the status of each ticket, resolution and satisfaction: a support decision card (the resolution, the amount and its destination: refund to the wallet or the card, and compensation as a reward collected within 24 hours in C20 (PAY-002); the reason, the executor, and the time), then "Was your problem solved?" Yes / No, and "Open a general ticket", which does not reopen the decision (SUP-003), "Help with the app" entry: with no order number
- Actions and what happens:
  - **Open a ticket**: sends the report with its type, items, photo, and order number, and opens the chat with the message "We received your report". Sending is disabled until the conditions are met (SUP-002). The ticket appears in "My tickets" with the status "Under review".
  - **Attach**: opens the app camera directly for an item report (no gallery), and accepts additional photos in the chat.
  - **Reply**: sends the message in the ticket chat with the status "Sent". After the ticket is closed it becomes "Open a new ticket".
  - **Rate the resolution**: "Yes" closes the ticket with a satisfaction rating. "No, I need help" records the dissatisfaction and shows "Open a general ticket"; the support decision is final for the customer (SUP-003).
  - **Where is my order**: new (before delivery): shows the status and expected time from C11 without opening a ticket, with "Not resolved? Talk to support".
  - **I want to cancel**: new: within the grace period cancels the order directly with a confirmation. After it, "After 60 seconds cancellation is through support only" appears and a chat is opened with a cancellation request in the order context (ORD-004).
  - **Payment or amount**: new: opens a report about this order's amount, with the payment summary attached.
  - **Open a general ticket**: new: after the support decision, opens a general ticket with the order context that appears in "My tickets"; the support decision is final for the customer, the ticket does not reopen it, and the customer has no objection to it. If support amends the decision on its own, the reversing entry appears in C20 (SUP-003).
- Validation and error messages:
  - Item report with no item selected: "Choose the affected item".
  - Item report with no photo: the send button is disabled with "Take the photo to enable sending" under it.
  - Duplicate report for the same item: "You already have an open report for this item" with a link to open it.
- Permissions:
  - Visitor: sees the page in a "Sign in" state, and any action that needs an account opens the mobile-number sign-in dialog (CUS-001), then returns to the same action. App help is available to a visitor.
- UX decisions:
  - Problem buttons come before any form.
  - The support decision is a clear card, not a message lost in the chat.
  - The general ticket is a secondary link, and satisfaction is two large buttons.
- Requirements: SUP-001 SUP-002 SUP-003 SUP-007 SUP-009 SUP-005 ORD-004
- Navigates to: C10 C20 C11
- Special states: every report is reviewed by an agent and there is no automatic reply (SUP-004): "The support team is reviewing your report and we will reply".; repeated overuse: a message at the top of the page (SUP-007).; restricted customer (SUP-007): the self-report buttons disappear and "Talk to support" remains.; after the one-hour window (SUP-005): the report buttons disappear in all sections including Mart, and no report is accepted after it; "Talk to support" remains for a general ticket.; damaged or expired Mart report: "The item price is refunded after support review" (SUP-009).; decision escalated to a higher level (SUP-002): "Your order is with the support supervisor".; smart reply enabled later: messages carry an "Automated assistant" tag with a "Talk to an agent" button.

#### C22 — Offers and Hour Deal

Offers from stores that deliver to the customer's address; a countdown to the end of the schedule.

- Elements: the address used for offers: in the header with "Change" (CUS-015), categories: All / Hour Deal / Free delivery / Restaurants / Mart, sort "Most savings first" (CUS-015), active offers: for each offer the discount and prices (amount saved), the duration, and the offer conditions (minimum and others), with a primary "Add product" button and a secondary "Open store", Hour Deal stock and recurring schedule: one prominent card: the product and the price before and after with the discount percentage, and a countdown to the end of the period such as "Ends [time] for everyone", the actual stock "X of Y left", and the schedule such as "Daily [from] – [to]" (MKT-017)
- Actions and what happens:
  - **Open a store**: opens C07 with the offer prominent at the top of the page and its conditions visible.
  - **Add a product**: adds the product at the offer price and shows an "Added to cart · View cart" bar. If the offer stock runs out or the period ends before the add, "Offer ended" appears and it is added at the regular price only after the customer agrees.
  - **Add to cart (Hour Deal)**: new: like Add a product, and the discounted price holds until the end of the scheduled period (MKT-017); after that the regular price returns in the cart with a message.
  - **Change the address**: new: opens C13, then the offers eligible for the new address are reloaded.
- Permissions:
  - A visitor sees the offers after setting their location, adding to cart is available, and payment requires sign-in.
- UX decisions:
  - Hour Deal is a prominent card because the countdown and the stock drive the purchase decision.
  - "For everyone" next to the end time clarifies that the countdown does not start when the customer enters.
  - The address in the header so the customer understands why they see these offers.
- Requirements: CUS-015 MKT-017
- Navigates to: C07 C08 C13 C09
- Special states: Hour Deal stock ran out or its period ended: it disappears immediately (CUS-015).; upcoming Hour Deal (recurring): "Starts tomorrow [time]" with no add button.; no offers for your address: "No offers reach your address right now" with change address.; no address set (visitor): location is requested first (CUS-015).; a delivery offer and a discount offer on products combine in the order; two discount offers on products do not combine, so only the one with the higher saving applies (MKT-007).

#### C23 — My Points and Invite a Friend

Loyalty and referral through OpenLoyalty and Adjust links.

- Elements: pending and available points: the available count with its SAR value under it (MKT-010), and the pending ones with "Available after the report window", redemption value: a "Redeem" button and a confirmation dialog stating what you get, the credit type and its validity, the points after redemption, and that it cannot be reversed, expiry: the nearest points expiry by count and date, invitation link: with the explanation "You both get a referral prize after their first completed order" (MKT-013), completed invitations: a list of invitations with masked numbers and a colored badge for each invitation's status: awaiting an order / pending until the window ends / completed / cancelled due to refund, referral prize: its type and value (MKT-013)
- Actions and what happens:
  - **Redeem**: opens the confirmation dialog (the second preview). After confirmation the points become promotional credit (PAY-002) that appears in C20, and the available points become zero.
  - **Share link**: opens the device share sheet with the customer's own link. Copying shows "Link copied".
  - **Open an invitation**: new: shows the invitation status and the reason the prize is pending or cancelled.
- Validation and error messages:
  - Redeeming below the city's minimum is rejected on the server with the same message (MKT-010).
- Permissions:
  - Visitor: sees the page in a "Sign in" state, and any action that needs an account opens the mobile-number sign-in dialog (CUS-001), then returns to the same action.
- UX decisions:
  - Invitees' numbers are masked to protect friends.
- Requirements: MKT-010 MKT-013 PAY-002
- Navigates to: C20 C14
- Special states: points withdrawn (MKT-010): shown in the log as "Withdrawn due to a refund on order #...".; referral prize cancelled (MKT-013): "Not eligible".; points below the redemption threshold: the button is disabled with "You need X more points".; no invitations: an empty state explaining the referral prize with a share button.; points sync delayed: "We are updating your points" with no placeholder numbers.

#### C24 — No Driver or No Coverage

A clear action for the problem without showing an unavailable store.

- Elements: reason for the state: a timeline of what happened: search started, support notified, waiting for the choice (ORD-004), after 15 minutes: eligible pickup within 5 minutes or a refund: two visible options "I'll pick it up myself from the branch" (distance, ready time, and "Your delivery fee is refunded") and "Cancel the order and get a full refund" (the amount and where it goes), with a red choice-deadline countdown above the fold (ORD-004), Mart: support and refund: "The support team is handling your order: assigning a driver or cancelling with a full refund" (ORD-004), location: a map with the customer's location when out of coverage, coverage interest: a one-step "Notify me when covered" button (ADM-033)
- Actions and what happens:
  - **Notify me**: sends the pin's location as a coverage request (ADM-033) and shows "We received your request, we'll notify you when the service arrives". The button becomes "Your interest is recorded" and is not repeated for the same location.
  - **Self-pickup for non-Mart**: converts the order once (EXT-006, CUS-010), and C16 opens in the "Being prepared" state. Does not appear in Mart.
  - **Refund**: confirmation "Cancel the order and refund the full N SAR to your card?". Afterwards the hold is released (PAY-001) and the order appears as "Cancelled · full refund" in C10.
  - **Support**: opens C21 with the order context. In Mart it is the primary action.
- Validation and error messages:
  - Converting to pickup after the deadline has passed or after a driver accepted: "This option is no longer available".
- UX decisions:
  - One choice of two with their financial consequences, and a primary button that follows the choice.
  - The timeline prevents the customer from feeling the order was neglected.
- Requirements: ADM-033 ORD-004 EXT-006 CUS-010 PAY-001
- Navigates to: C15 C21 C16 C13 C10
- Special states: before 15 minutes: "Looking for a driver" with the elapsed time, no options.; Mart after 15 minutes: "Support is following up on your order" with the support button only.; a driver accepts while the options are shown: the screen disappears and the order returns to tracking with "We found a driver".; out of coverage: the second preview, with no unavailable store shown.; interest recorded earlier: "We recorded your interest in this location" with edit location.

### Merchant App

#### M01 — Orders

A working screen for the merchant according to their type and branches.

- Elements: new, preparing, and ready: tabs with the order count in each (MER-006), bell: the ringing line on the new card "Ringing on … devices until one of you opens it", then after interaction "Opened by … · … · …" (device, staff member, and time) on all devices (MER-030), 3-minute timer: a circular timer for the duration-adjustment window, with the default duration and a −/+ control (ORD-003, MER-040), products and notes: the order items, and the customer's note on a yellow background, customer identifier: its ID number only (MER-006), delay alert with no deduction: in the preparing tab a countdown of the remaining time that turns red and negative on overrun with "Support was notified of the times, and there is no automatic deduction from your dues" and a "View order times" link (ORD-007), branch status badge: top of the screen (Open / Busy +… until … / Temporarily paused) with "Visible to customers" or "Not visible", not-visible bar: red "Your branch is not visible to customers" with the reason as text (MER-028), driver arrival bar: green at the top of the list in all tabs "Driver arrived … for order #… · waiting since …" with a "Hand over the order" button (MER-020, MER-019), order type badge: delivery · menu, or Mart, or write-in, or self-pickup, or "Converted to self-pickup", out-of-stock badge: "Out of stock" and the deadline timer on the order awaiting the customer's reply, with a "Record the customer's reply" button (MER-032), write-in badge: "Awaiting products invoice" or "Awaiting customer payment …" instead of a ready button, printer bar: when disconnected "Printer not connected — … awaiting printing and will print when it returns" (MER-042), order of preparing cards: overdue first, then closest to the end of its duration
- Actions and what happens:
  - **Confirm duration**: the "Confirm … minutes" button confirms the displayed duration with no confirmation prompt: ringing stops on all devices and the device and staff member appear on them, the order moves to "Preparing", and the −/+ control disappears (ORD-003)
  - **Details**: opens M02 for the order; preparation starts if it has not started (ORD-003) and ringing stops on all devices
  - **Ready**: one tap with no confirmation: the order moves to "Ready" and notifies the driver, or the customer in self-pickup, with a transient notice "Order #… is ready" (MER-006). For write-in it is disabled with the text "Available after the customer pays" (ORD-013)
  - **Out of stock**: opens a list of the order's items to choose the out-of-stock item, then the out-of-stock dialog itself in M02 (M02_2) (MER-032)
  - **Hand over the order**: from the driver arrival bar: opens M03 for the order with the code field ready for typing
  - **−/+ preparation time**: changes the suggested duration in 5-minute steps before confirmation; nothing is saved until "Confirm duration"
  - **View order times**: opens M02 on the "Order times" section (ORD-007)
  - **Record the customer's reply**: opens the active out-of-stock dialog (M02_2) with the number and the remaining timer
  - **Branch status badge**: opens M09 to change the status or busy mode
  - **Not-visible bar**: opens the place to fix it according to the reason: M09 for status and hours, M05 for out-of-stock, M12 for messaging the platform when the city is disabled
  - **Printer bar**: opens M15
- Validation and error messages:
  - Duration: the − button is disabled at 1 minute and the + button at the maximum (ORD-003), and no value outside them can be entered
  - Confirmation from another device after confirmation is rejected with the message "Another device confirmed the duration … minutes"
- Permissions:
  - The screen and ringing: the "Orders" permission at the branch (merchant manager, branch manager, authorized merchant staff, preparation account)
  - The "Hand over the order" button: the "Handover" permission only
  - No reject button in Menu and Mart orders for any role (MER-006); a write-in order is rejected before the invoice is uploaded (ORD-004); and no monetary amounts on the cards
- UX decisions:
  - The confirm button carries the duration and takes two-thirds of the width, and "Details" is a secondary button.
  - The circular timer is next to the −/+ control instead of a numeric keypad, for kitchen speed.
  - The branch status badge is always visible because not being visible stops orders.
- Requirements: MER-006 ORD-003 MER-020 MER-028 MER-030 MER-042 ORD-007 MER-032 MER-019 EXT-006 ORD-013 MER-040
- Navigates to: M02 M03 M04 M09 M15 M08
- Special states: new order ringing: the card has an orange border until a device interacts (MER-030); adjustment window ended without confirmation: the adjustment control disappears and the order moves to "Preparing" with the default duration (ORD-003); overdue: the card has a red border and a negative timer (ORD-007); out-of-stock awaiting: the card has an orange border and a timer; when it ends its text becomes "Item removed automatically" (MER-032); driver arrived: the green bar stays until the code is entered; converted to self-pickup: the order badge changes and the driver disappears, and handover is by order number (EXT-006); cancelled during preparation by support, or entered "Awaiting support decision" for an out-of-stock item or non-payment of write-in: a gray card "Stop preparing" and an "Acknowledged" button that removes it; branch not visible: the red bar is fixed at the top of the screen until visibility returns; device offline: a bar "No internet connection — orders reach the branch's other devices and print on the reception device, and will appear here when it returns" (MER-042); Mart account: the default duration is confirmed automatically with one optional adjustment (ORD-003), and "Details" opens M08 (MER-031)

#### M02 — Order Details

Preparation, driver, events, and products invoice by type.

- Elements: preparation: status steps at the top of the page (Arrived -> Preparing -> Ready -> Picked up) with a large countdown of the remaining time, items and options: each item with its options and an "Out of stock" button beside it, and the components of the bundled meal and the customer's choice for each component under its name (MER-024), customer's choice on out-of-stock: at the head of the items list (remove it / call me / cancel the order), with no numbers (MER-032), item status after out-of-stock: struck through "Removed · out of stock", or "Substitute: … · awaiting customer approval / approved", driver by identifier: its ID number and status (on the way · arrives in … / arrived since …) and their waiting time (MER-019), order times: arrival time, preparation start and its reason, confirmed duration, expected readiness, actual "Ready" time, driver arrival, pickup (ORD-007, ORD-003), products invoice optional, or mandatory for write-in: its status (no invoice / attached from the cashier / uploaded manually) with the archive link (MER-036), amounts: the value of the products, and the merchant's net per the contract, customer chat button: in the top bar with the unread message count (MER-022), order log: every action with the staff member, device, and time (MER-037, MER-030), loss charge and penalty line on delay or cancellation: "Any loss charge or penalty is a manual support decision with a written reason, and it appears in your statement" (ORD-007)
- Actions and what happens:
  - **Print**: sends the order ticket (MER-021) with the duration, without the customer's name and number, and shows "Sent to print". With no printer: "No printer connected" and a button that opens M15
  - **Substitute**: for an item recorded as "Replace": opens the branch's available products to choose the substitute and its quantity with the price difference. "Send the substitute to the customer" sends it to C12, and the item shows "Awaiting customer approval" then "Approved" or "Rejected" (MER-032)
  - **Products invoice**: in menu and Mart: photographing or uploading a file that is saved in the archive with the order number. In write-in and pharmacy it opens M04 (MER-036)
  - **Ready**: as in M01, then returns to M01 with a transient notice. Disabled in write-in before payment, and disabled with the text "Record the customer's reply on the out-of-stock item first" if an item is awaiting a reply
  - **Ticket**: opens M12 with a new ticket linked to the order number
  - **Out of stock (per item)**: opens the "Out of stock" dialog per the customer's choice (MER-032): "Remove it": confirmation "The item will be removed and the collected amount reduced by … SAR" then it is removed and the customer sees the update; "Call me": the number the customer chose for this item, the deadline timer, a "Call the customer" button, and "Replace / Remove / Cancel" buttons; "Cancel the order": confirmation "The order enters "Awaiting support decision" due to an out-of-stock item and the customer is refunded in full, and support sets any loss charge or penalty. This cannot be undone"
  - **Replace / Remove / Cancel (in the out-of-stock dialog)**: "Replace" opens the "Substitute" action; "Remove" removes the item and updates the amount; "Cancel" asks for a confirmation stating the effect and then puts the order into "Awaiting support decision" (MER-032). After any button, or when the deadline ends, the number disappears and the timer closes
  - **Call the customer**: opens the phone call to the number; the number is not copied anywhere else
  - **Customer chat**: opens M13 for the order
  - **Share PDF**: from the print menu: generates the order file or its products invoice and opens the phone's share sheet (MER-021)
- Validation and error messages:
  - Products invoice upload: image or PDF only; anything else is rejected with "Upload an image or a PDF file"
  - Substitute: is not sent without a product and quantity; the message "Choose the substitute product"
- Permissions:
  - Viewing the order, printing, out-of-stock, and ready: the "Orders" permission
  - Merchant net and amounts per the contract: the "Finance" permission only; others see only the value of the products
  - Order log: branch manager and merchant manager
- UX decisions:
  - The steps and the countdown are at the top because they are what the kitchen needs most.
  - "Ready" alone is the primary button in the fixed bar, and the other four actions are a secondary row.
  - The out-of-stock dialog is a bottom sheet within thumb reach: the number is large, then the call button, then three buttons in different colors, and cancel is red with a confirmation.
- Requirements: MER-036 MER-019 MER-032 MER-022 MER-024 ORD-007 MER-021 MER-030 MER-037 ORD-003 MER-006
- Navigates to: M03 M04 M12 M13 M15
- Special states: overdue: a red bar "You exceeded the preparation time by … min. Support was notified of the times, and there is no automatic deduction from your dues" and the times section is open (ORD-007); item awaiting a customer reply: an orange bar with the timer that reopens the out-of-stock dialog; item removed: the amounts update; substitute rejected: the item is removed; order cancelled or awaiting support decision: all buttons disappear and a bar with the reason appears (cancellation by support, out-of-stock item, non-payment) and "Do not complete preparation"; closed order: the page is read-only and the chat is closed; self-pickup: the driver card is replaced by "The customer picks it up themselves · match the order number"; driver changed after reassignment: the new identifier and a line "Driver changed …"

#### M13 — Customer Chat (new)

Text chat between the merchant and the customer of an active order using hidden numbers, such as getting their approval to remove an out-of-stock item or its substitute, and it closes when the order closes.

- Elements: chat header: the customer by ID number, the order number and its status, and an "Open order" button, fixed note in the header: "A chat for this order only. Numbers are hidden for both parties, and it closes when the order closes", messages: with time, and the name of the sending staff member is visible to the merchant only, system lines: what was recorded on the order, such as "… recorded 'Replace' for item … · …", quick replies: "An item is out of stock, shall we remove it?", "Do you accept a substitute?", "Your order will be ready soon", fixed composer bar at the bottom of the screen: a text field, a photo button, and a send button
- Actions and what happens:
  - **Send**: the message appears immediately with the time, and reaches the customer as a notification in their app
  - **Quick reply**: puts the text in the field for the staff member to edit and then send
  - **Photo**: opens the camera or gallery to send a photo (such as the proposed substitute)
  - **Open order**: returns to M02 or M04
- Validation and error messages:
  - Empty message: the send button is disabled
  - Sending after the order is closed is rejected on the server with the same message
- Permissions:
  - The "Orders" permission at the order's branch; the chat appears to all the branch's authorized devices
- UX decisions:
  - The privacy note in the header so the staff member does not ask for the customer's number.
  - Quick replies cover the common out-of-stock cases in one tap.
  - System lines link what was said in the chat to what was recorded on the order.
- Requirements: MER-022
- Navigates to: M02
- Special states: empty chat: "Start the chat with the customer about this order" with the quick replies; new message from the customer: a count badge on the chat button in M02 and M04 and a short sound alert; order closed (delivered or cancelled): messages are read-only and the composer field is hidden with the text "The order is closed; messages cannot be sent" (MER-022); send failed: the message has a red mark and "Resend" without losing the text

#### M03 — Order Handover

Driver pickup by code; customer self-pickup by order number.

- Elements: Driver and driver ID: arrival alert at the top of the page "Driver arrived … · within the arrival distance · waiting since …" (MER-020, MER-019), arrival distance badge: within it or outside it (ORD-005), driver code: a single large digit field with spaced digits and a direct numeric keypad (ORD-005), write-in payment status: for write-in orders (ORD-013), photo: "Order photo at handover" button, saved with the order (ORD-005), pickup type: part of a pre-handover checklist with the order number, item count, and bag count (and the cooler in Mart), self-pickup match: the order number shown large and a "Number shown by the customer" field with a "Match" or "No match" badge (EXT-006), self-pickup payment: "Paid online · collected on confirmation", ready time, and end of shift, link "Driver doesn't have the code? Open a ticket"
- Actions and what happens:
  - **Enter driver code**: the field is enabled when the driver is within the arrival distance of the branch, and the server validates the code and the distance (ORD-005)
  - **Confirm handover**: with a driver: sends the code; on success the order becomes "Picked up by driver", the photo is saved, and the customer sees "Delivery in progress", then a short success page and a return to M01 with a notification "Order #… handed over". For self-pickup: after the match, a confirmation "Hand over order #… to the customer? The amount is collected and this cannot be undone", then the order is closed as "Received" (EXT-006)
  - **Order photo at handover**: opens the camera and attaches the photo to the order
  - **Open a ticket**: opens M12 with a ticket linked to the order and the subject "Handover"
- Validation and error messages:
  - Wrong code: the field turns red "Incorrect code. Ask the driver for it again"
  - Driver outside the arrival distance at submission: "The driver is outside the arrival distance of the branch, handover is not possible now"
  - Self-pickup number does not match: "The number does not match #…. Check that this is the correct order" and the button is disabled
- Permissions:
  - The page and its actions: "Handover" permission at the branch
- UX decisions:
  - One primary button at the bottom with a clear verb "Confirm handover to driver" or "Hand over order #… to customer".
  - Self-pickup is a separate blue screen so it is not confused with handover to a driver.
- Requirements: ORD-005 EXT-006 MER-020 MER-019 ORD-013 MER-030
- Navigates to: M01 M12
- Special states: driver on the way: the field is disabled with the text "Available when the driver arrives · arrives in …"; driver outside the arrival distance: red badge and the button is disabled "Ask the driver to come closer to the branch"; unpaid write-in order: the button is disabled "No handover before the customer pays" (ORD-013); self-pickup waiting for the customer: alert "If the customer does not show up by the end of the shift, the order enters "Awaiting support decision" due to "No-show""; after that, read-only with the status "Awaiting support decision · No-show" (EXT-006)

#### M04 — Write-in Orders and Products Invoice

Accept for processing or reject before the products invoice, then submit it for payment.

- Elements: write-in order steps: review ← products invoice ← payment ← preparation ← ready, text and images: what the customer wrote and attached, prescription for the store only: with the note "The prescription is for the store only and does not appear in any report", products invoice and its amount: its image and products amount; the submitted image is kept in the archive under the order number (MER-036), preview of what the customer pays: products and service fee shown separately and the total, delivery is prepaid and not included; updates as the amount is typed (ORD-013), payment status: and who sent the products invoice, from which device, and when, 10-minute counter: after sending, the screen switches to a large circular timer instead of the form (ORD-013), customer chat button: in the top bar to clarify items (MER-022)
- Actions and what happens:
  - **Reject before products invoice**: only before the products invoice is uploaded (ORD-004): a dialog to choose the reason (not available with us / no prescription / invalid prescription / other reason with text), then a confirmation "The order enters "Awaiting support decision" for support to decide what is refunded to the customer. This cannot be undone". After that the customer and driver are notified and the order disappears from the list (PHR-012)
  - **Upload and send**: validates the image and the amount, then a confirmation "After sending, you cannot reject the order. The customer will be asked to pay … SAR within 10 minutes". After that the products invoice is saved, the payment request reaches the customer (C18), the timer starts, and the reject button disappears (ORD-013, MER-036)
  - **Ticket**: opens M12 with a ticket linked to the order
  - **Customer chat**: opens M13 for the order
  - **Ready**: works as in M01 after payment (ORD-013)
- Validation and error messages:
  - No image: "Attach the products invoice image before sending" and the button is disabled
  - No amount or zero amount: "Enter the products amount as on the products invoice"
  - Amount with at most two decimal places: "Write the amount like 100.00"
  - Rejection with reason "Other" and no text: "Write the rejection reason"
- Permissions:
  - Rejecting and uploading the products invoice: "Orders" permission (MER-030)
- UX decisions:
  - The primary button carries the amount "Upload and send · … SAR", and rejecting is a secondary red button.
  - A warning "No rejection after sending" sits directly above the button.
- Requirements: ORD-013 MER-036 MER-030 MER-022 ORD-004
- Navigates to: M03 M13
- Special states: awaiting customer payment: "Ready" is disabled with the text "Available after the customer pays", no rejection after the products invoice is uploaded, and it can be corrected once before payment (ORD-013); customer paid: notification and a short ring "Customer paid order #… — start preparing", and the step becomes "Preparation"; customer declined or timeout expired: "Awaiting support decision: Unpaid — do not prepare" and the page is read-only (ORD-013); rejected before the products invoice: "Awaiting support decision", read-only with the chosen reason; pharmacy: the preview shows the service fee only (ORD-013)

#### M05 — Menu and Availability

Manage the restaurant or Shops menu according to permissions.

- Elements: menu period: the menu active now and the time of the next one ("Morning · active now", "Evening · from …") (MER-005), search and filters: search by name, and filters All, Not visible, Awaiting review, Paused, with counts, products: for each product the preparation time in minutes, and a "Combo meal" badge with the number of its components (MER-040, MER-024), store price and sale price: store price ← sale price on one line, product availability time: the time or "Follows menu period" (MER-005), availability: visibility badge with the reason written under the product: visible, outside availability time, paused until a time, awaiting review, unavailable due to an out-of-stock component (MER-028, MER-024), review: the product is awaiting price review (MER-002), sizes and add-ons: shared option groups, cashier sync: the status and last sync time (MER-024)
- Actions and what happens:
  - **Add**: opens M06 with a new product (or a combo meal) in the selected menu
  - **Edit**: tapping the product opens M06
  - **Enable**: toggle switch: turning it on makes the product visible if the other conditions are met (MER-005), otherwise the badge shows the reason. Turning it off hides it immediately until it is turned on manually, with no confirmation, with a notification "… paused" and an "Undo" button
  - **Pause**: bottom sheet: one or more products, and the duration (one hour, two hours, until end of day, until a specific time). After "Pause until …" a badge "Paused until … · returns automatically" appears (MER-004)
  - **Sizes and add-ons**: opens the shared option groups for editing
  - **Switch menu**: the menu chip shows the products of the Morning or Evening menu; a menu that is not enabled does not appear (MER-005)
- Validation and error messages:
  - Pause until a time in the past: "Choose a time after now"
- Permissions:
  - Viewing the menu, enabling, and pausing: "Products" permission
  - Editing the price: "Prices" permission; others see the price as text only
  - The branch manager edits only their branch's store prices and product availability; the menu is shared by all of the merchant's branches (MER-002)
- UX decisions:
  - The "Not visible" filter gathers everything that needs action in one tap.
  - Pausing with ready-made durations and a clear return time instead of a permanent pause the employee forgets.
- Requirements: MER-002 MER-005 MER-024 MER-040 MER-004 MER-028
- Navigates to: M06 M07
- Special states: menu not active now: banner "The Evening menu starts …; its products do not appear to customers before then"; product returned automatically: the badge disappears and "Returned automatically …" is logged (MER-004); combo meal unavailable: red badge with the out-of-stock component, and it becomes available again automatically when the component is back or a substitute is added (MER-024); product awaiting price review: the proposed price is shown (MER-002); cashier sync failure: banner "Sync failed … — the menu is running on the last version" with "Retry"; Mart merchant: the screen does not appear, and the Products tab opens M07 (MER-005)

#### M06 — Product and Price Edit

A clear preview of the store price, sale price, and the approved price limits.

- Elements: name, description, and image: product fields, edit limit: badge for the store price edit mode granted to the merchant (not allowed, needs review, within a percentage with the percentage, full) (MER-002), approved price: the last price approved by the platform, and the price limits without review in numbers ("from … to …"), proposed price: the store price the merchant writes, and the review status if any "Your proposal … awaiting review since …", sale price: now and after approval together, with the line "Sale price = store price × (1 + markup rate …%) per your branch's contract" (MER-002), preparation time: in minutes (MER-040), availability time: with the period of the menu the product belongs to for comparison ("Within the Morning menu period …") (MER-005), options: product options; for a combo meal the component list, each component with its options and the availability of each option, and the meal status (available / unavailable) (MER-024), cashier: product linking and sync status (MER-024)
- Actions and what happens:
  - **Allowed save**: available when the price is within the price limits, the mode is "full", or no price change was made: saves immediately without confirmation and updates the sale price, and returns to M05 with a notification "Saved". Disabled when the edit needs review, or the mode is "not allowed" (MER-002)
  - **Submit for review**: appears as the primary action when the price falls outside the price limits or the mode is "needs review": confirmation "The sale price … remains for customers until the platform approves …". After that a badge "Awaiting review" appears in M05, the request reaches the platform (A08), and non-price edits are saved immediately (MER-002)
  - **Preview**: the product card as the customer sees it: image, name, current sale price, preparation time, and options
  - **Pause**: choose the return time; the product disappears until that time (MER-004)
  - **Add component**: for a combo meal: choose a product from the menu as a component and set its substitute options
  - **Product image**: opens the camera or gallery; the new image is saved with the product
- Validation and error messages:
  - Preparation time above the limit: "Maximum preparation time is 40 minutes" and it is not saved (MER-040)
  - Preparation time empty or zero: "Enter the preparation time in minutes"
  - Price outside the price limits: the field turns red "Outside the price limits; it will be sent for review, and … remains for customers until approval" (MER-002)
  - Availability end before its start: "Availability end must be after its start"
  - Availability time outside the menu period: "The time is outside the Morning menu period (…)"
  - Meal component with no option: "Add at least one option for each component"
- Permissions:
  - Name, description, image, availability, and preparation time: "Products" permission
  - Price field: the "Prices" permission within the merchant's cap; and the store price is for this branch only (MER-002)
- UX decisions:
  - The primary button switches automatically between "Allowed save" and "Submit for review" depending on the price entered.
  - The price limits are shown in numbers rather than a percentage alone, so the merchant knows in advance whether it will be reviewed.
- Requirements: MER-002 MER-005 MER-040 MER-024 MER-004
- Navigates to: M05 M12
- Special states: mode "not allowed": the price field is locked with the text "Price editing is not available to you. To change it, message the platform" and a button that opens M12; awaiting review: the price field shows the proposal, and under it "The customer sees … until approval"; proposal rejected: banner "The platform rejected …: reason…" and the field returns to the approved price; meal unavailable: red banner in the page header with the name of the out-of-stock component (MER-024); product synced from the cashier: the fields coming from it are shown with "From cashier"

#### M07 — Mart Catalogs and Products

Choose a whole collection, then customize it locally.

- Elements: primary, secondary, and general: the catalogs (MER-010), catalog subscriptions: for each catalog the catalog subscription status and the product count, and the number of later additions this week and how many of them await enabling (MER-010), enable additions automatically: a toggle per subscribed catalog, off by default; turning it on brings later additions in enabled, and a product the grocery proposed stays enabled for it (MER-010), products: search by name and a barcode search button, and filters: All, Central, Locally edited, Centrally paused, Drafts, central and local: a source badge for each product and its status: central, locally edited, centrally paused (locked), draft awaiting the platform, rejected with the reason, availability: toggle for the product in your grocery, store price and sale price: the reference store price from the catalog, your local price for this grocery if you edited it, and the sale price, on one line (MER-010), new product for review: an "Add product" button, and drafts in the "Drafts" filter (MER-010)
- Actions and what happens:
  - **Subscribe to a catalog**: enabling it shows a confirmation "The catalog's current products … (…) will be added enabled, and what is added to it later comes in disabled unless "Enable additions automatically" is on". Cancelling shows "Its products will disappear from your grocery, and the sales history is not deleted" (CAT-001)
  - **Enable a product**: toggle in your grocery. The toggle of a centrally paused product is locked, and touching it shows "The platform paused it for all groceries, and it cannot be enabled locally" (CAT-001)
  - **Edit price**: opens M06 in Mart mode: the local store price for this grocery versus the reference price, and the sale price (MER-010)
  - **Add product**: form (name, barcode, image, section, price) then "Submit for approval": saved as a draft and sent to the platform for approval in the general catalog (MER-010)
  - **Barcode search**: opens the camera and goes to the matching product, or shows "Not found in your catalogs" with "Add it for review"
- Validation and error messages:
  - New product with no name, image, or price: a message under the missing field
  - Barcode already exists: "This barcode belongs to an existing product: …"
- Permissions:
  - Subscription, enabling, and adding a product: "Products" permission
  - Local price: "Prices" permission
  - Mart account limits (MER-030)
- UX decisions:
  - The source badge is color-coded so the merchant is not surprised by a central pause.
  - The barcode is next to search because the grocery works by scanning.
- Requirements: MER-010 CAT-001 MER-030
- Navigates to: M06 M08
- Special states: centrally paused: locked and hidden from customers (CAT-001); locally edited after a central update: line "The platform updated the reference price to …; your local price stays …" (MER-010); no subscriptions yet: "Choose a catalog to start your grocery with ready-made products"

#### M08 — Mart Preparation

A list of barcode, section, and progress, then review and packing.

- Elements: products and quantities: grouped by section with the quantity for each product, barcode: for each product, scanned to mark it, cooler: a badge on cooler products and their count in the header, preparation progress: "Prepared … of …" with a bar, and the number remaining, out-of-stock and substitute: the customer's choice on out-of-stock for this order, and the status of the unavailable product "Removed per customer choice · −…" or "Awaiting customer reply …" or "Substitute awaiting approval" (MER-032), bags: their count in the final review, final total: final review with the order total, items removed for being out of stock, substitutes and their differences, and the final total, optional products invoice: photo or upload (MER-036), driver: ID and expected arrival time (MER-019), line "No rejecting the order and no transferring to another grocery" (MER-031)
- Actions and what happens:
  - **Scan**: opens the camera: the matching product is marked "Prepared" and progress increases with a confirmation sound; scanning is repeated by the quantity
  - **Prepare**: manual marking for a product without a barcode
  - **Unavailable**: opens the same out-of-stock dialog as in M02 according to the customer's choice (MER-032)
  - **Ready**: after all products are processed: opens the final review and the bag count, then "Ready · … SAR" moves the order to "Ready" and notifies the driver (MER-031, MER-036)
  - **Products invoice**: photo or upload, saved in the archive under the order number
- Validation and error messages:
  - Barcode of another product: vibration and the message "This is the barcode of "…", not "…""
  - Scanning more than the quantity: "The quantity of this product is complete (…)"
  - Bag count: an integer of 1 or more "Enter the number of bags"
- Permissions:
  - Preparation, product out-of-stock, and ready: "Orders" permission, including the preparation account within its limits (MER-030)
- UX decisions:
  - Scan is the primary button in the fixed bar, and "Ready" is enabled on completion.
  - Sections in aisle order reduce walking inside the grocery.
  - The cooler badge is blue.
  - The final total updates immediately after each removal or substitute.
- Requirements: MER-031 MER-032 MER-030 MER-019 MER-020 MER-036
- Navigates to: M02 M03
- Special states: remaining products: "Ready" is disabled with the text "… products remain: prepare them or tap Unavailable"; product awaiting customer reply: a timer beside it, and when it ends the product is removed and the total updates (MER-032); all products unavailable: the order enters "Awaiting support decision" due to an out-of-stock item and the screen closes (MER-032); driver arrived during preparation: green banner "Driver arrived … · waiting since …" (MER-020)

#### M09 — Branch Status and Hours

Open, busy, or temporarily paused, and special hours.

- Elements: branch visibility to customers now: visible / not visible, and the number of visible products and the active menu (MER-028), reason for not being visible: as text, with the list of monitored reasons and their status: branch status, working hours, menu and products, city (MER-028), status: open, busy, or temporarily paused, busy duration up to 15 minutes: ready increments (+5 / +10 / +15 min) (MER-018), busy period up to one hour: 15 min / 30 min / 45 min / one hour (MER-018), preview of what the customer sees before ordering: "Preparation … min instead of … min", and the automatic end time, temporary pause for a period: from a time to a time with the return time (MER-004), hours: daily and weekly hours and special days (MER-005), menu periods: for display (MER-005), product time (MER-005)
- Actions and what happens:
  - **Change status**: "Open" is immediate. "Busy" opens the busy setup, then "Enable busy +… min until …" with no additional confirmation (MER-018). "Temporarily paused" asks for the return time, then a confirmation "You will not receive new orders until …. Current orders will be completed" (MER-004)
  - **Temporary pause duration**: set the start and end of the temporary pause or the busy duration, and the return time is shown (MER-004)
  - **Edit hours per permission**: opens the weekly schedule and special days, then "Save hours" with a summary of the change; menu periods are display-only (MER-005)
  - **End busy now**: restores the original duration for new orders immediately
  - **Open now**: ends the temporary pause before its scheduled time after a simple confirmation
  - **Message the platform**: when not visible for a reason on the platform side (city disabling or branch disabling): opens M12
- Validation and error messages:
  - Increment above the ceiling: not offered, and any larger value is rejected "Maximum increase is 15 minutes" (MER-018)
  - Busy duration above the ceiling: "Maximum busy duration is one hour"
  - Closure end before its start or in the past: "Choose a return time after now"
  - Overlapping hours on the same day: "The two periods overlap"
- Permissions:
  - Changing status, busy, and temporary pause: merchant manager, branch manager, and anyone with the "Orders" permission as granted by the merchant manager (MER-004)
  - Editing hours: merchant manager, and branch manager for their branch only, within what the platform allows
- UX decisions:
  - Visibility is in the first card because the merchant's first question is: do customers see me?
  - Busy uses ready options that do not exceed the ceiling, so there are no error messages in normal use.
  - All times are labeled as Riyadh time.
- Requirements: MER-004 MER-018 MER-005 MER-028
- Navigates to: M01 M05 M12
- Special states: busy: badge "Busy +… min until …" in M01 and a countdown timer (MER-018); temporarily paused: counter until return, and the reason for not being visible "Temporary pause"; outside working hours: "Closed now · opens …" and the status cannot be changed to open outside hours; city or branch disabled by the platform: red alert with the reason and the status buttons are disabled (MER-028); all active menu products out of stock: "Not visible: no products available" with a link to M05

#### M10 — Today's Performance

Sales and operations summary with custom range and links to reports.

- Elements: period: the one selected in the filter, with each number compared to the previous period (vs yesterday / vs last week), branch: the one selected in the filter, orders and sales: the period's numbers, preparation: the period's numbers, delays: the number of late orders and their share of delivered orders, rating: the rating and number of ratings, next payout: its amount and date, with a share-statement-PDF button beside it (MER-021), store quality: a compact card with the number of indicators better and worse than the section average in the city and the names of the worst ones, with details in "Store Quality" (MD14) in the merchant dashboard (MER-026)
- Actions and what happens:
  - **Filter**: bottom sheet: period (today, last 7 days, last 30 days, custom), branch, and comparison; "Show" updates the numbers immediately
  - **Full report**: opens the full reports (MD06) with the same period and branch (MER-035)
  - **Store quality**: opens "Store Quality" MD14 in the merchant dashboard
  - **Share statement PDF**: generates the period's account statement as a PDF file and opens sharing on the phone (MER-021)
- Validation and error messages:
  - Custom period: "Choose an end date after the start"
- Permissions:
  - The page: "Reports" permission, and sales according to it; a branch manager sees only their branch in the filter (MER-035)
  - Next payout and statement sharing: "Finance" permission only, and they do not appear for others (MER-037)
- UX decisions:
  - Four main numbers in a grid with the direction of change in green or red.
  - Delays in red with their percentage because the number alone is not enough to judge.
  - Store quality is a prominent link with the number of items needing improvement instead of a separate hidden report.
- Requirements: MER-035 MER-026 MER-021 MER-037
- Navigates to: MD01 MD06 MD14
- Special states: no orders in the period: numbers are zero with the text "No delivered orders in this period" and no comparison

#### M11 — More and Team

The tools allowed for the user according to their role.

- Elements: user card: store name, employee name, role, and branch, branch status and hours (M09): with the visibility status, store quality (MD14 in the merchant dashboard): the number of indicators that need improvement (MER-026), devices and printers (M15): device count, and a red badge for any disconnection (MER-030, MER-042), support (M12): badge for new platform replies, finance: MD07, marketing: MD04, ratings (MD08): badge for new ratings, team: MD10, printer and sound: test print, notifications: notification toggles for this device, preferred captain: ID and the text "Your order is offered to them first if available, and the order is not delayed if they are not", display only (MER-038), log out from this device
- Actions and what happens:
  - **Open a tool**: opens the chosen tool at its destination in the elements; tools not allowed for the role do not appear at all
  - **Printer**: sends a test ticket to the connected printer; if not connected, opens M15
  - **Manage an employee**: opens branch staff (MD10): edit their branches and permissions, or suspend them with a confirmation "They will be logged out of all devices immediately, and the branch keeps running" (MER-037)
  - **Notifications**: a toggle for driver arrival, delay, and platform reply notifications on this device; the new order ring cannot be turned off from here
  - **Log out from this device**: confirmation "This device will not ring for new orders after logging out", then the login screen
- Permissions:
  - Finance: "Finance" permission. Marketing: "Offers" and "Campaigns". Ratings: as granted by the merchant manager. Team: "Employees". Devices: merchant manager and branch manager
  - A branch manager manages only their branch's employees (MER-037)
- UX decisions:
  - Tools are ordered with daily operations first (status, quality, devices, support), then administrative ones.
  - Each row carries its short status or a count badge, so the merchant does not need to open it to know.
- Requirements: MER-037 MER-021 MER-030 MER-038 MER-042 MER-026
- Navigates to: MD04 MD05 MD07 MD10 M12 MD14 M15 M09
- Special states: limited role (such as the preparation account): only orders, devices, and support appear (MER-030); no preferred captain: the row does not appear

#### M15 — Devices and Printers (New)

Manage the branch's devices (phones, tablets, and order-receiving devices) and printers, and make sure the order rings and prints and is not lost when a device disconnects.

- Elements: disconnection alert: the device or printer name, the disconnection time, the number of orders awaiting printing, and that orders reach the remaining devices (MER-042), branch devices: name, type (Android, iPhone, tablet, receiving device), the account signed in on it, whether it rings, connection status and last seen (MER-030), printers: name, the device it is linked to, status, and the number of orders awaiting printing, auto-print: a toggle "Auto-print every new order" with the ticket content without customer data (MER-021), sound: bell volume, and that it repeats until interaction (MER-030)
- Actions and what happens:
  - **Link a device or printer**: linking methods: a new device (the employee signs in with their account and it appears here), or a Bluetooth or network printer, or an order-receiving device; after linking it appears in the list as "Connected"
  - **Test print**: prints a test ticket; "Printed" or "Printing failed: check that the printer is connected" appears
  - **Test bell**: the bell rings once on this device
  - **Auto-print**: turning it on prints every new order when it arrives (MER-042); turning it off asks for confirmation "Orders will not be printed automatically on this printer"
  - **Log out a device**: from the device menu: confirmation "This device will not ring or receive orders until it is signed in again"
  - **Remove a printer**: confirmation, then it is deleted from the list; orders awaiting printing are moved to another printer if one exists
- Validation and error messages:
  - No printer during linking: "We could not find a printer. Check that it is on and nearby"
- Permissions:
  - Merchant manager for all branches, and branch manager for their branch
  - Other employees see device status only and can run the test print
- UX decisions:
  - The disconnection alert comes first with explicit reassurance that orders are not lost.
  - Each device shows who uses it and whether it rings, so the branch manager knows who will hear the order.
  - Test print and test bell next to the setup itself.
  - One primary link button at the bottom.
- Requirements: MER-030 MER-042
- Special states: disconnected device: red badge "Disconnected …", and orders appear on it when it returns; disconnected printer: orders are saved and printed automatically in order when it returns (MER-042); no connected device that rings in the branch: red alert "No connected device to receive orders"; no devices yet: "Link your first device or printer to receive and print orders automatically"

#### M12 — Support and Call Me

Support tickets and the number the customer chose when an item is out of stock.

- Elements: call-me number for this order: a card at the top of the page with the order number, the out-of-stock item, the number the customer chose, and the buttons "Substitute / Remove / Cancel order" (MER-032), 3-minute timeout: a timer on the card (MER-032), two tabs: tickets, and the ongoing platform chat (MER-012), ticket list: number, topic, title, linked order, and status (open, awaiting your reply, closed), topic accounts, menu, contract, or support: in the new ticket form with the order number (optional), problem description, and attachments, messages and attachments: inside the ticket and the chat (MER-012)
- Actions and what happens:
  - **Ticket**: "New ticket" opens the form; "Send" creates a ticket with a number and the status "Open" that reaches platform support (A19), with a notification "Your ticket was sent"
  - **Reply**: sends the message and attachments in the open ticket; they appear immediately with their time, and the status changes to "Awaiting support"
  - **Call on out-of-stock**: opens the phone dialer with the number the customer chose for this order (MER-032)
  - **Substitute / Remove / Cancel**: as in the out-of-stock dialog in M02; after any button the card and the number disappear
  - **Attach**: a photo or file is added to the reply before sending
- Validation and error messages:
  - Ticket with no topic: "Choose the topic"
  - Ticket with no description: "Write the problem description"
  - Order number not in your branch: "No order with this number in your branch"
- Permissions:
  - Tickets and platform chat: "Tickets" permission; accounts tickets also appear for anyone with "Finance"
  - "Call me" card: "Orders" permission and for the relevant order only
- UX decisions:
  - The "Call me" card is above everything in orange, because its timeout is short.
  - The reply is in the fixed bottom bar within thumb reach, with the new-ticket button below it.
  - Each ticket's status is a color badge, with "Awaiting your reply" first.
- Requirements: MER-012 MER-032
- Navigates to: M02
- Special states: no active out-of-stock: the card does not appear; timeout expired: the card and the number disappear with a notification "Item automatically removed from order #…" (MER-032); closed ticket: read-only with an "Open a linked ticket" button; new support reply: badge on the tab and on "Support" in M11

### Merchant Dashboard

#### MD01 — Overview

Branch comparison, totals, and operations.

- Elements: period and custom: shortcuts (today, last 7 days, last 30 days, this week) and a custom option with start and end dates (REP-001), branch: a switcher "All branches" or a single branch, whose selection persists while navigating between dashboard pages (MER-017), sales and orders: cards for sales, delivered orders, average basket, new customers, repeat customers, cancellation rate, with the difference from the previous period; customer indicators are counts only (MER-029), best and slowest branch: a branch comparison table (sales, orders, average preparation, share exceeding the time, rating) with Best and Slowest tags, peak times: for the selected branch, in place of the comparison table, alerts: what needs action, sorted by severity, each alert with a "View" button, visibility to customers now: a bar for each branch: visible, visible with busy mode, not visible with the reason (temporary pause or disabling, out of stock, outside hours, disabled city) and the return time if any, store quality: the quality badge status and the indicator it is missing (MER-026, MKT-014), next payout: amount, status, and period
- Actions and what happens:
  - **Filter**: applies the branch and period to all cards, the table, and the chart together without reloading and without confirmation, and the choice is saved (REP-001).
  - **Open a report**: opens reports (MD06) on "Sales Summary" with the same branch and period and the same numbers.
  - **Switch branch**: choosing a branch from the switcher or "Open" in the branch row shows only its data here and on every following page until returning to "All branches".
  - **View (in an alert)**: opens the relevant page filtered by branch and item: Branches for visibility, Products for out-of-stock, Store Quality for exceeding the time, Ratings for a pending reply. The alert disappears when its cause is gone.
  - **Open store quality**: opens store quality (MD14) on the selected branch and period.
  - **Open the statement**: opens the statement and payouts (MD07) on the live statement for the current period.
  - **Manage branches**: opens Branches (MD09).
- Validation and error messages:
  - Start after end in custom: the filter is not applied, and under the field "Start date is after end date" (REP-001)
  - End in the future: clipped to today, and under the field "Data is shown up to today"
- Permissions:
  - Merchant manager: all branches and all cards
  - Branch manager: their branch only, with no switcher and no branch comparison (MER-017)
  - "Reports" permission: indicators within their branches; without it, only alerts and visibility status
  - "Finance" permission: the next payout card; it disappears entirely for others and does not appear locked (MER-037)
- UX decisions:
  - Visibility status is seen first because a non-visible branch loses orders now, then sales.
  - The branch and period switcher is in a fixed place at the top of all dashboard pages.
  - Branch comparison is a table with adjacent numbers, easy to scan, instead of separate bars.
  - The actual range in dates under the title so "last 30 days" is not confused with the calendar month.
- Requirements: MER-017 MER-035 MER-029 MER-026 MKT-014 REP-001
- Navigates to: MD06 MD07 MD09 MD03 MD08 MD14 MD15
- Special states: single-branch merchant: the branch switcher and comparison table disappear; branch not visible during its working hours: the visibility bar becomes a red alert at the top of the page with the reason and return time; period with no orders: cards are 0 and the chart is empty with "No delivered orders in this period" and a button to change the period

#### MD02 — Order Log

Order search, its details, and its net.

- Elements: order number: search by it, with filters for status, method, source, and payment status, and the branch and period from the top of the dashboard, status: using the order lifecycle names: with merchant, ready, ready for pickup, picked up by driver, delivered, received, and "Awaiting support decision" with its reason (out-of-stock item, Unpaid, No-show), and closing without delivery: cancelled or terminated with the closing reason, payment status: a separate column: held, collected, hold released, partially refunded, refunded (ORD-001), method: a column and a filter, source: app, menu link (exempt or non-exempt), cashier, with the offer tag if applied, timeline: a timeline for each transition with the time and who performed it from the merchant's team (ORD-001), amounts: the order net line by line with the name of each fee and how it is calculated: products, actual contract fee or the exemption value, payment fee, platform fee tax 15% shown separately, the net (PAY-010, PAY-011), Mart and pharmacy: a "Store percentage" line instead of the contract fee, with no payment fee line (PAY-011), products invoice if any: an icon in the table, and its absence is not colored as an error, branch: a column when "All branches" is selected, details panel: beside the table: branch, method, source, items, and timeline, closing without delivery: the written closing reason, the recorded liable party, and the loss charge and penalty if support set them
- Actions and what happens:
  - **Open**: opens details in the side panel (and clicking the row does the same) and the row stays highlighted. The link is shareable within the merchant's team.
  - **Print**: the print dialog with the order receipt: items, options, notes, and order number, without customer data.
  - **Report**: a report form with the topic "Support" and the order number pre-filled, a required reason and text, and an optional attachment. Sending creates it in platform communication (MD12) assigned to the account manager, with a notification "Report sent" and its link.
  - **Products invoice**: downloads the products invoice if one exists; otherwise "Upload products invoice" appears, and the file is linked to the order and appears in the archive (ORD-001).
  - **Open in statement**: opens the statement (MD07) filtered to the order: its line, the payout it went into, and the products invoice.
  - **Search**: filters the table while typing; a full order number opens its details.
- Validation and error messages:
  - Search with a non-numeric character: the character is ignored
  - Report with no text: it is not sent, and under the field "Write what happened with the order"
  - Products invoice in an unsupported format: "Upload an image or a PDF file"
- Permissions:
  - "Orders" permission: the log, details, and printing within their branches
  - "Finance" permission: the net, the fee breakdown, and the "Open in statement" button; without it, only the products value
  - "Tickets" permission: the "Report" button
  - Branch manager: their branch's orders only, with no branch column
- UX decisions:
  - Details in a side panel so the employee reviews consecutive orders without losing their place.
  - Order status and payment status are two separate colored badges, so "Delivered" is not understood as "Amount transferred".
  - The net breakdown explains where the number comes from without opening the statement.
- Requirements: MER-008 ORD-001 PAY-010 PAY-011
- Navigates to: MD07 MD12
- Special states: open order (with merchant, ready): payment is "Held" and the net is "Estimated until delivery"; awaiting support decision or closed without delivery: amounts are 0.00 or what the support decision set; the loss charge or penalty if any with its status and an "Object" button that opens the statement; item removed before collection: only the reduced collected amount with the tag "Edited before collection", with no reversal entry; refunded after collection: a refund line linked to the original (PAY-010); write-in order: both payments appear, delivery then products (ORD-001); no search result: "No order with this number in your branches" and a button to clear filters

#### MD03 — Products, Menu, and Catalog

A management tool depending on the merchant's operating type.

- Elements: products: for each product the menu period, availability toggle, availability time (MER-005), store price, sale price, completeness, and the customer-facing status in its own text (visible, outside menu period now, paused until a time, centrally paused, price awaiting review, new product for review), menu periods or catalogs: a "Menu periods" tab for restaurants and Shops with a menu, and "Catalogs" instead of it for Mart only (MER-005, MER-010), availability: a toggle for each product, and bulk selection: pause until a time, enable, set availability hours, store price and sale price: two columns; and the pending price next to the approved one with an arrow and "The customer sees the approved price until accepted", review requests: a tab of new products sent for review, price mode: a bar at the top of the page with the granted store price edit mode and its percentage, and that the sale price = store price × (1 + markup rate) per the branch's contract, and the menu is shared by all branches while each branch has its own store price and availability (MER-002), menu completeness: the overall percentage and its breakdown and a percentage per product with small bars (MER-047), improvement assistant: a draft image or description beside the current one with a "Draft" tag until the user chooses to use it (MER-047), linking and sync: a tab with the link status, last sync and its result, the imported count, incoming prices awaiting review, and items hidden for being out of stock in the merchant's system (MER-041), Mart: the catalogs subscribed to and the "Enable additions automatically" option for each, a "Local price" tag for a product whose price was edited in this grocery, a centrally paused product cannot be enabled locally, and a sale price preview (MER-010)
- Actions and what happens:
  - **Add**: product form: name, image, description, price, options, menu period, availability time. Saving creates it with the status "New product for review" in "Review requests" (MER-002, MER-010).
  - **Edit**: product edit dialog with a preview of the store price and sale price before saving; the price is applied or sent for review depending on the mode (MER-002).
  - **Subscribe to a catalog**: for Mart only (disabled for others with a hint). A list of catalogs; choosing one shows a confirmation: "Its current products enter your grocery enabled at the reference store prices, and its later additions are not enabled unless "Enable additions automatically" is on; you can edit the price, availability, and image of each product". After that the products appear in the table.
  - **Improve with the assistant**: generates a draft image or description for the selected product or for incomplete ones; nothing is published until "Use draft" (MER-047).
  - **Availability toggle**: pauses or enables the product in the selected branch immediately. Pausing asks "Until when?" (until I enable it, or until a specific time) (MER-004). The toggle of a centrally paused product is disabled with the reason.
  - **Bulk actions**: apply pause, enable, or availability hours to the selection at once, with a message of how many changed and how many did not and why.
  - **Sync now**: in the linking tab: requests the latest prices and stock from the merchant's system (MER-041).
- Validation and error messages:
  - Empty or zero price: "Enter a price greater than zero"
  - Price outside the price limits: not blocking; under the field "Outside the price limits (min – max) · will be sent for review" and the save button becomes "Send price for review"
  - Availability time ending before its start or outside the menu period: "Availability time must fall within the menu period"
  - Empty name: "Write the product name"
- Permissions:
  - "Products" permission: adding and editing name, image, description, and availability
  - "Prices" permission: editing the price within the merchant's mode limits (MER-002)
  - Branch manager: availability and its hours in their branch
  - Menu periods are display-only here; they are operated from the merchant page in the admin dashboard (MER-005)
- UX decisions:
  - The customer-facing status in the last column answers: does the customer see the product now? And if not, why?
  - One assistant button turns missing completeness into an action.
- Requirements: MER-002 MER-010 MER-005 MER-047 MER-041 MER-004
- Special states: mode "not allowed": the price field is locked with "Price editing is not available to you; contact the platform"; price awaiting review: no second price edit for the product until decided, with "Awaiting review since…"; price or product rejected: a "Rejected" badge with the reason, and the approved one remains; link failure or sync delay: yellow alert with the last successful sync and a "Sync now" button, and the products stay in their last known state; menu with no active menu period now: alert "Customers see no product now because the menu is outside its period"

#### MD04 — Offers

Direct offer subscription to a platform offer, a merchant offer for review, and a recurring Hour Deal.

- Elements: tabs: available, offer subscriptions, merchant offer, Hour Deal, results (MER-034), available: a card for each platform offer: the discount, minimum, duration, eligible branches, funding share for each party, and whether it combines with others (MKT-007), offer subscriptions: each branch's subscription to each platform offer with its status (active, paused until you approve a new share, ended), and scheduled Hour Deals with their status (MKT-007), funding: an explicit funding share "The platform funds … · you fund …" as an amount or a percentage before the subscribe button, and your share is fixed when your branch subscribes; and a note on the discount's effect on fees (MKT-007), merchant offer: fully funded by the merchant; a form with cities, branches, products, duration, stock, minimum, budget, combining rule; and its status (under review, approved, rejected with reason) (MKT-007), 30% hour schedule: the branch's subscription to the Hour Deal (a platform offer): product, discount percentage, deal stock, once or recurring days, start and end hour, and a preview of what the customer sees and the price after the discount (MKT-017), current Hour Deal: product, price before and after, remaining stock, and a timer until the period ends (MKT-017), results: one table for each subscription: orders, discount value, your share, platform share, end date; it matches the offers line in the statement (MER-034)
- Actions and what happens:
  - **Subscribe**: on a platform offer: choosing the branch, or "All branches" for the merchant manager, then a confirmation with your share and the duration: "The offer starts immediately after subscribing, and your share … of each discount is fixed". After that it becomes "Active" in offer subscriptions (MKT-007).
  - **Create**: opens the merchant offer form or the Hour Deal form depending on the tab. A merchant offer is sent with the status "Under review" until the platform approves it; the Hour Deal subscription (a platform offer) is published automatically at its time without review (MKT-007, MKT-017).
  - **End an offer subscription**: a red button with a confirmation: "The offer stops immediately for new orders in the selected branches". After that the status is "Ended" and its results remain in Results.
  - **Follow up**: opens the submitted merchant offer: its status (under review, approved, rejected), the rejection reason, and an "Edit and resubmit" button for a rejected one.
  - **Stop an Hour Deal**: confirmation: "The usual price returns immediately, and the next recurrence stops". After that the status is "Paused".
  - **Publish an Hour Deal**: saves the deal and schedules it; it appears in offer subscriptions as "Scheduled" then "Running now" at its time. Disabled while the form has an error.
  - **Approve the new share**: on an offer subscription paused because the platform raised your share: shows the previous and the new share, and a confirmation "Your branch's subscription becomes active again with the new share on new orders". Without approval the subscription stays paused and nothing is deducted from you at the new share (MKT-007).
- Validation and error messages:
  - Hour Deal discount below 30%: "Discount is below 30% · the Hour Deal is not published" and publishing is disabled
  - End before start: "End time must be after the start"
  - Zero or empty stock: "Enter stock for the deal"
  - Recurring days with no day: "Choose at least one day"
  - Merchant offer with no products or branches: "Choose the branches and products the offer covers"
- Permissions:
  - "Offers" permission: subscribing, creating, and ending within their branches; anyone without it does not see the page
  - Branch manager: their branch's offers and results only
- UX decisions:
  - The current Hour Deal is at the top of the page because it is the only one that changes now.
  - The discount error is directly under its field.
- Requirements: MKT-007 MKT-017 MER-034
- Navigates to: MD07 MD05
- Special states: Hour Deal stock ran out: "Deal stock ended" (MKT-017); merchant offer budget ran out: it stops with a "Budget ended" badge; merchant offer rejected: red badge with the platform's reason; no offers available: "No platform offers are available for your branches now, create a merchant offer" and a "Create" button; offer that does not combine with others: a sentence saying so on the card (MKT-007); the platform raised your share in an existing offer: the branch subscription is "Paused until you approve" with both shares and an "Approve the new share" button; lowering the share takes effect immediately without approval (MKT-007)

#### MD05 — Ads and Campaigns

An ad is a banner or pin at the city price, and a campaign is a message to your past customers.

- Elements: tabs: ads (banner or pin), campaigns (messages to your past customers), results (MER-034), placement: a card for each placement available in the branch's city: its location, price for the day, remaining capacity, ad form: placement, city, duration (from and to), image at the placement's size; no keywords (MKT-003), price: a cost summary beside the form: price × days, tax 15%, total, and under it "No deduction before approval, and the ad invoice is issued after it" in a reassuring color (MKT-003), stop policy: its link for this placement shown before sending (MKT-003), approval status: awaiting approval, active, rejected with reason, paused, disabled by the platform, ended (MKT-008), results: one table with the status: spend, impressions, clicks, orders, new customers, return on spend; and spend matches the statement (MER-034, MKT-015), campaigns: segments (new, repeat, idle), city, branches and zone, template, attached offer, send time, and the expected audience count in a large font with a privacy explanation beside it (MKT-005), campaign results: audience, who opened, who ordered, sales; aggregated (MKT-005)
- Actions and what happens:
  - **Cost preview**: calculates the cost summary immediately beside the form. It does not hold or deduct.
  - **Send**: confirmation with the amount: "… SAR will be deducted from your dues only after platform approval, and the ad invoice will be issued to you". After that the ad is "Awaiting approval" with a notification "Ad sent for approval" (MKT-008).
  - **Follow up**: ad details: its status and the date of each change, the rejection reason, its daily results, and the ad invoice.
  - **Stop an ad**: a confirmation showing the placement's stop policy and what is refunded and what is not (MKT-003). After that "Paused" and it disappears from the app.
  - **Repeat an ad**: copies the settings of an ended ad into a new form with empty dates.
  - **Send a campaign to your customers**: sends the campaign for review (MKT-005). Disabled while the form has an error.
- Validation and error messages:
  - Image at a non-matching size: under the upload area "Image size does not match this placement"
  - End before start or start in the past: "Choose a duration that starts tomorrow or later"
  - Campaign budget above the platform limit: "Above the platform's limit for you" and sending is disabled
  - No segment: "Choose at least one segment"
- Permissions:
  - "Campaigns" permission: creating, sending, and stopping
  - "Finance" or "Campaigns" permission: seeing spend and return
  - Branch manager: their branch's ads and campaigns only
- UX decisions:
  - Errors are under the field itself.
- Requirements: MKT-003 MKT-008 MER-034 MKT-005
- Navigates to: MD04 MD07
- Special states: rejected ad: red badge with the platform's reason (MKT-008); disabled by the platform: badge "Disabled by the platform", and the refund line in the statement with a credit note linked to the ad invoice (MKT-003); placement full: the card is disabled with "Capacity is full in this period"; ended ad with no orders: results are zeros and the return is "—" not zero; campaign with zero audience: sending is disabled with "No past customers served in these segments and branches"

#### MD06 — Reports

A reports center with flexible periods and comparison.

- Elements: groups: a fixed report list on the left divided into groups, with the open one highlighted (MER-035), custom: period shortcuts and a custom option (REP-001), branch: the branch selected for the report (MER-035), comparison: with the previous period, and the title writes the actual range and its comparison, chart and table: each report starts with four numbers, then the chart, then the table, export: Excel and PDF, sending: the current schedule line below the report: day, reports sent, recipients from the merchant's team, "Your Customers" report: new, repeat, idle, average basket, retention; for each period and each week (MER-029), "Per-customer fee" report: the number of customers in each branch by their cycle total (have not reached the cap, reached it) and the total contract fees (PAY-010), privacy note: "No names, phone numbers, or addresses", finance reports: "Fees invoice" and "Penalties and loss charges" instead of "Monthly commission invoice" and "Late penalties" (PAY-025)
- Actions and what happens:
  - **View**: shows the report with the chosen period, branch, and comparison, and saves the last choice (REP-001).
  - **Excel**: downloads Excel with the same numbers as the screen (REP-001), and the file name carries the report name and range.
  - **PDF**: downloads a PDF matching the screen with the chart and table.
  - **Schedule**: dialog: reports, weekly send day, recipients (only those with the Reports permission). After saving, a "Sent weekly" line appears and reports arrive by email for the weekly period that just ended.
  - **Choose a report**: shows the report in the main area without changing the period or branch.
- Validation and error messages:
  - Start after end: "Start date is after end date" and it is not displayed (REP-001)
  - Schedule with no recipient: "Choose at least one recipient"
- Permissions:
  - "Reports" permission: non-financial reports within their branches
  - "Finance" permission: the "Finance" group; it does not appear in the list for others
  - Branch manager: their branch's reports only (MER-035)
  - "Employees" permission: employee performance and the action log
- Requirements: MER-035 MER-029 REP-001 PAY-010
- Navigates to: MD01 MD07
- Special states: a report specific to an operating type (Mart only, write-in orders): hidden for other types; long-period export: prepared in the background with "We are preparing the file, you will be notified when it is ready"; no data for the period: an empty state and a "Try a longer period" button

#### MD07 — Statement and Payouts

Breakdown of dues, exemption, penalties, and loss charges.

- Elements: tabs: live statement, payouts, fees invoice, archive (MER-045), the selected branch's dues account at the top of the page, and "All branches" with their total for the merchant manager: three separate balances: "Pending capture" for orders not yet closed (amount held), "Due" for what was captured and entered the branch's Moyasar wallet but has not reached you, and "Paid out to you" for the period; below them the next weekly payout date (MER-008, PAY-006), net: the period summary on the first line: sales, platform fees and their tax, offers, refunds, loss charges, and penalties, net so far, next payout status, sales: a waterfall under the summary explaining how sales go down to the net, an item for each type, and the tax as a separate item (MER-008, PAY-022), contract fee and payment fee in each order's breakdown: source, products, the actual contract fee with the reason for its value written ("Exempt" with the exemption value, or "Cap reached"), payment fee, offers, tax, net (PAY-010, PAY-011, MER-007), Mart and pharmacy: a "Store percentage" column instead of the contract fee, with no payment fee column (PAY-011), merchant not registered for VAT: no product VAT is deducted from them, and they issue the products invoice themselves (PAY-029), offers (merchant share) and refunds: two items in the waterfall, manual and its reason: the loss charge and the penalty are two separate lines, for each line the type (loss charge or penalty), amount, order or source, reason, status as a colored badge, last date to object (7 days from the decision notification), and an "Object" button beside it (MER-008, SUP-006), payouts per branch to its bank account: reference, period, amount, method (weekly from the branch's Moyasar wallet), status, bank reference, date (PAY-006), fees invoice: monthly, the total of each fee type and the loss charges and penalties, tax separate, the total, and an indicator of whether the month's lines match it; ad fees are not included, as they have the ad invoice (PAY-022), archive: the order result is one card with the products invoice, the statement line, and the linked payout, and the ad invoices (MER-045)
- Actions and what happens:
  - **Order search**: filters the order breakdown to the order and opens its card with the statement line, the payout, and the products invoice.
  - **Statement**: downloads the statement for the period and branch (Excel or PDF) with the same numbers as the screen (MER-008).
  - **Object**: a dialog with the amount, the original reason, and the last date, and a required "Reason for your objection" field, and an optional attachment. After sending, the status is "Under objection" and it appears in Ratings and Reports (Objections); then "Accepted" with a reversal entry or "Rejected" with the reason (MER-008).
  - **Download fees invoice**: downloads the fees invoice for the month as a PDF.
  - **Open a payout**: the transfer details: the orders and charges that went into it, the status, the bank reference, the date, and who approved it and when.
  - **Archive search**: searches by order number or a date range and document type, and groups results by order or month.
- Validation and error messages:
  - Objection with no reason: "Write the reason for your objection"
  - Second objection on a charge under objection: the button is unavailable with "Your objection is under review"
  - Order number not in the user's branches: "No order with this number in your branches"
  - Start after end: "Start date is after end date"
- Permissions:
  - The page is for the "Finance" permission only, and does not appear in the list for others (MER-037, MER-043)
  - Branch manager with the Finance permission: their branch's finance only
  - Platform staff see the same archive from the merchant page in the admin dashboard (MER-045)
- Requirements: MER-008 PAY-006 PAY-025 PAY-010 PAY-011 PAY-022 MER-045 MER-043
- Navigates to: MD02 MD08 MD12
- Special states: failed transfer: red badge "Failed · not paid" with the reason if it came from the bank (PAY-006); next weekly payout: the amount is an estimate and changes until the payout date; objection period expired: the button is disabled with "Objection period ended on …" (SUP-006); "Potential" loss charge: in a different color, and not counted in the net until it becomes "Charged"; month not finished: "This month's fees invoice is issued after it ends"; split share failed: red badge "Failed · not paid", and the amount stays in "Due" until Finance retries it (PAY-006); the branch's new bank account is awaiting Finance approval: the branch's share stays in "Due" with "Arrives after the account is approved" (MER-001)

#### MD08 — Ratings and Reports

Reply, support decision, and objection.

- Elements: ratings: a summary at the top of the page: average rating, count, unreplied, open reports, and the weekly rating trend for the last 8 weeks as a small line beside the numbers (MER-027), list: unified for ratings, reports, objections, and hide requests, with a status tag on each item, and what needs action first with a colored tag, rating: the text, order, branch, and time, without the customer name, reply: its status (unreplied, awaiting platform review, published, rejected with reason) and its three steps (write, platform review, visible to customers), reports: the customer's report and evidence, the support decision, the loss charge or penalty and its status (potential, charged, under objection, accepted, rejected), and the payout it went into, reasons: a hide request with its reason (not related to the order, abusive) and its status and the reason for the platform's decision (MER-027), objections: the last date as an explicit date before sending, and the decision status (SUP-006)
- Actions and what happens:
  - **Reply for review**: sends the reply to the platform; the status becomes "Your reply is awaiting review" and the reply field is locked (MER-027).
  - **Object**: on a loss charge or penalty in a report: a dialog with the last date (7 days from the decision notification) and the amount, a required reason, and an optional attachment. After that it is "Under objection" here and in the statement; acceptance shows a reversal entry, and rejection shows its reason.
  - **Request to hide a violating review**: a dialog with a choice of reason and an optional explanation. The review stays visible with the status "Hide request · awaiting platform decision" then the decision and its reason (MER-027).
  - **Open an item**: shows the item on the other side without leaving the page.
  - **Filter**: type filters (rating, report, objection), stars, and status (unreplied first) filter the list.
- Validation and error messages:
  - Empty reply: "Write your reply before sending"
  - Objection with no reason: "Write the reason for your objection"
  - Objection after the deadline: the system rejects it with the message "Objection period ended on …" (SUP-006)
  - Hide request with no reason: "Choose the hide reason"
- Permissions:
  - "Tickets" permission: replying, requesting hide, and viewing reports
  - "Finance" permission: objecting to loss charges and penalties and seeing their amounts
  - Branch manager: their branch's ratings and reports only
- Requirements: MER-027 SUP-006
- Navigates to: MD07 MD14
- Special states: published reply: appears as customers see it, with no reply field; rejected reply: "Reply rejected" badge with the reason; "Potential" loss charge or penalty: no object button until it becomes "Charged"; objection period expired: the button is disabled with the end date; no unreplied ratings: "You have replied to all ratings"

#### MD14 — Store Quality (new)

Shows the merchant their store's quality indicators compared with the average of stores in their category in the city, the status of the Quality badge, and what is missing.

- Elements: Branch and period: at the top of the page. Quality badge: met or not met, with its conditions per branch and their thresholds, and the status of each condition (within threshold, above/below threshold) (MKT-014). Indicators: a table of the five indicators, each with the store value, the category average in the city, a "Better/Worse" badge, and the change from the previous period (MER-026). Indicators by branch: when "All branches" is selected. What raises your quality now: the two worst indicators, each with an understandable cause and a button to the page where you fix it. Indicator definitions: a link to the definition of each indicator
- Actions and what happens:
  - **View affecting orders**: opens the orders log (MD02) filtered to the orders that affected the selected indicator for the same branch and period.
  - **Indicator definitions**: a dialog that explains each indicator in one sentence: when measurement starts and ends, and what is and is not included.
  - **Products / Branches (in the improvement card)**: opens Products (MD03) or Branches (MD09) on the branch with the problem.
  - **Switch branch**: shows the indicators of that branch alone compared with the average of its category in its city, and the branches table is hidden (MER-026).
- Validation and error messages:
  - Start after end: "Start date is after end date"
- Permissions:
  - Merchant manager with the "Reports" permission: all branches
  - Branch manager: own branch only
- UX decisions:
  - The badge status and the missing condition come first on the page because they are what the customer sees.
  - The branches table reveals which branch pulls the average down.
- Requirements: MER-026 MKT-014
- Navigates to: MD02 MD03 MD09
- Special states: Badge met: a green card "The Quality badge is visible to your customers" with the indicator closest to the threshold; badge lost: an alert "The Quality badge was lost in … because of…" here and in the overview; new store with few orders: "We need more orders to calculate your indicators" instead of numbers; not enough stores in the category and city to compare: the average column is hidden with a sentence giving the reason; no ratings: "No ratings yet", not zero

#### MD09 — Branches

Branches, their status, devices, and permissions.

- Elements: Location and branch data: city, preparation time, minimum order, the payout bank account (defaults to the merchant's account), and cashier integration, for display (MER-001, MER-011). Status: the first column after the name, with a status badge: Open now, Busy (busy mode) until a time, Temporarily paused until a time, Outside hours, Awaiting platform approval. Hours: weekly hours and special days per branch (MER-004). Delivery: the branch zone within the limits of its city (MER-046). Devices: type, connection status, and last connection (MER-042). Team: number of staff, the branch manager, and a link to manage them. Branch link and QR (INT-009). Editing: hours, special days, and temporary pause directly; name, location, and city by request to the platform
- Actions and what happens:
  - **Request new branch**: a form: name, location on the map, city, hours, preparation time, minimum order. After submission the branch shows as "Awaiting platform approval" and is not visible to customers, and a notification arrives with the approval or with a request to complete it and its reason.
  - **Allowed edit**: hours and special days are saved immediately and appear to customers; platform fields are locked, with "Request a change" next to them, which creates a conversation in Communication with the Platform.
  - **Temporary pause**: a dialog with options: for a duration, or until a specific time, or until the end of the day, and an optional reason. The confirm button writes the return time: "The branch will not be visible to customers until …". Afterward it shows "Temporarily paused until…" (MER-004).
  - **Copy link**: copies the branch link with a "Link copied" notification.
  - **Download QR**: downloads a print-ready QR image for the branch link.
  - **Manage**: opens Staff and Permissions (MD10) filtered to the branch.
- Validation and error messages:
  - Closing before opening on the same day without crossing midnight: "Closing time is before opening time"
  - New branch location outside the selected city: "The location is outside the city of …"
  - Return time in the past: "Choose a time after now"
- Permissions:
  - Merchant manager: all branches and requesting a new branch
  - Branch manager: own branch only (MER-017); edits their hours and special days and pauses it temporarily (MER-004)
  - Other staff: view the status of their branches only
- Requirements: MER-017 MER-037 INT-009 MER-004 MER-042
- Navigates to: MD10 MD12
- Special states: device not connected: a reassuring yellow alert at the top of the page with the disconnection time, instead of a scary red one (MER-042); awaiting approval or completion required: a blue badge; with a completion request, the written reason and a "Complete" button; deleted branch: its old link opens an alternative with the merchant's other branches (INT-009); disabled city: a "Not visible · City disabled" badge and it cannot be opened from here

#### MD10 — Staff and Permissions

The merchant manager distributes access and branches.

- Elements: Staff: for each staff member, the account status: active, suspended, not signed in yet (MER-043). Role: branch manager or merchant staff, with a ready-made permissions template that can be edited. Branches: one branch, several, or all branches for each staff member. Independent permissions: a permissions matrix with two columns, "Granted to the merchant" and what the staff member has; permissions not granted to the merchant are locked, and the column explains the reason for the lock without an error message (MER-037). Performance: orders, average preparation time, and lateness rate, next to the staff member themselves (MER-037). Action log: cannot be deleted: staff member, action, branch, time
- Actions and what happens:
  - **Add**: a form: name, mobile, role, branches, permissions. After saving, the staff member gets their login immediately and receives a notification, and shows as "Not signed in yet" until first login (MER-043).
  - **Edit permissions**: enables the matrix checkboxes for the staff member; "Save permissions" applies them immediately in the UI and the server, so revoked buttons and pages disappear, and the change is logged with who made it and the values before and after.
  - **Suspend**: a red button with confirmation: the staff member cannot sign in immediately, and the branches operate as usual (MER-037). Afterward it shows "Suspended" and a "Reactivate" button.
  - **Reactivate**: a simple confirmation returns them to "Active" with their previous permissions.
  - **Open staff member**: clicking the row shows their permissions, branches, performance, and log in the other pane.
- Validation and error messages:
  - Invalid mobile: "Enter a Saudi mobile number that starts with 05 and has 10 digits"
  - Number registered to another staff member: "This number is registered to one of your staff members"
  - No branch: "Choose at least one branch"
  - No permission: "Choose at least one permission"
- Permissions:
  - "Staff" permission: add, edit, and suspend within its branches
  - Merchant manager: all staff and branches
  - Branch manager: their branch's staff within the limits of their permissions (MER-037, MER-002)
- Requirements: MER-037 MER-043
- Navigates to: MD09 MD06
- Special states: not signed in yet: no performance or log yet, and their permissions can be edited at any time; the platform revoked a permission from the merchant: it is revoked from all staff and shows locked with "Revoked by the platform from your account"; suspending yourself: the button is unavailable for your own account

#### MD11 — Files

Optional operational attachments.

- Elements: Files: a table of files, and who uploaded each file and when. File owner: the merchant, a specific branch, a staff member, or the platform. Optional date: the expiry date, with the number of days remaining in the badge. Status: valid, expires within (number of days), expired, no date. Alert: at the top of the page for a file that is close to expiry or expired, with the explicit text "Reminder only; it does not stop orders" (MER-044). Permanent note: no mandatory documents (MER-044)
- Actions and what happens:
  - **Upload**: choose a file, then a dialog: name, owner (the merchant or a branch), optional expiry date. It appears at the top of the table with its status, and the reminder is automatic if a date is entered (MER-044).
  - **Download**: downloads the file as uploaded; the button in the top bar downloads the selected files.
  - **Replace**: uploads a new version with an optional date; the previous one is kept in the file's history, the status updates, and the reminder stops.
- Validation and error messages:
  - Unsupported format: "Upload a PDF, image, or Excel file"
  - Past expiry date at upload: accepted and shows "Expired" with "The expiry date has passed"
- Permissions:
  - Merchant manager: all files of the merchant and its branches
  - Branch manager: their branch's files
  - Staff member: sees and uploads only their own
- Requirements: MER-044
- Navigates to: MD09
- Special states: nearing expiry: a yellow badge, no stop (MER-044); expired: a red "Expired" badge and a prominent "Replace" button next to it, so renewal is one click; uploaded by the platform: view and download only, no replace; no files: "No files yet. Upload what you need for operations; none of them is mandatory"

#### MD12 — Communication with the Platform

Topic, owner, attachments, and tickets.

- Elements: Topics: a filter: Accounts, Menu, Contract, Support. Account manager: their name and avatar in the page header and in every conversation they handle (MER-014). Messages: for each conversation the topic, owner, status (open, new reply, closed), and the last message and its time; attachments are inside the messages. Linking: to an order, loss charge, penalty, or invoice, with a button that opens it, so the order number is not copied into every message. Save note: conversations are saved and linked to the merchant (MER-012)
- Actions and what happens:
  - **Start**: a dialog: topic (required), branch, optional order, loss charge, or penalty number, message, optional attachment. After sending, the conversation appears at the top of the list as "Open", assigned to the account manager (MER-014).
  - **Reply**: sends the message, which appears immediately in the thread with its time, and a notification goes to the owner.
  - **Attach**: adds a file or image to the message as a box with its name that can be deleted before sending.
  - **Open in statement**: opens the linked loss charge, penalty, or order in the statement or the orders log.
- Validation and error messages:
  - Empty message: the reply button is disabled
  - Start without a topic: "Choose the conversation topic"
  - Attachment in an unsupported format: "Upload an image or PDF file"
- Permissions:
  - "Tickets" permission: start, reply, and attach
  - "Accounts" conversations also appear to the "Finance" permission
  - Branch manager: their branch's conversations and those they started
- UX decisions:
  - The input field is fixed at the bottom of the thread, and Reply is the primary button.
- Requirements: MER-012 MER-014
- Navigates to: MD07 MD02
- Special states: new reply: a "New reply" tag on the conversation and a counter on the page name; closed conversation: read-only, and writing in it reopens it; no account manager assigned: assigned to the support team and "Mahallat Team" shows instead of a name; no conversations: "No conversations yet. Start a conversation with your account manager" and a "Start" button

#### MD13 — Settings and My Contract

What the merchant edits and what is display-only.

- Elements: Name and cover pending review: a card titled "Pending review", Special hours and days, Sound and printer, QR, store link and branch links (INT-009), Cashier: integration status, the systems available to you, and a "My system is not listed" button (MER-011), Contract for display: a "Display only" card with clear values and examples: contract type, order fee and cap (PAY-010), payment fee (PAY-011), menu link order exemption (on or off) (MER-007), platform fee tax (PAY-022), and VAT registration: the VAT number, or "Not registered: you issue the products invoice yourself and its tax remains your responsibility" (PAY-029), Operating type: display-only with "Set by the platform and determines the fee model", and the section and category "Display placement only" (MER-009), The price editing mode granted for the store price, and the markup rate in each branch's contract (MER-002, PAY-009), Systems connected through the partner API: system name, what it can access, branches (INT-012), API product integration: status, last sync, and a link to the integration tab in products (MER-041)
- Actions and what happens:
  - **Allowed edit**: enables the allowed fields. Name and cover are sent for review with "Awaiting review" and the old ones remain for customers until accepted; sound and printer are saved immediately.
  - **QR**: downloads a print-ready QR for the store link or the selected branch.
  - **Link cashier**: a dialog with the available systems and branch selection; "Request linking" creates a request whose status appears in the card (awaiting the platform, linked, linking failed) (MER-011).
  - **My system is not listed**: a system name field and a note; submitting creates a linking request that appears in Communication with the Platform (MER-011).
  - **Copy link**: copies the store link with a "Link copied" notification.
- Validation and error messages:
  - Empty name: "Enter the store name"
  - Cover with an unsuitable size or format: "Upload a landscape image in JPG or PNG format"
  - System request without a name: "Enter the cashier system name"
- Permissions:
  - Merchant manager: all settings and requesting linking
  - "Finance" permission: sees the contract card; hidden from others
  - Branch manager: their branch's link, QR, sound, and printer
  - Contract, operation type, and category are display-only for everyone
- UX decisions:
  - The cashier card reassures that orders work without linking, and "My system is not listed" turns a dead end into a request.
- Requirements: MER-011 MER-007 MER-002 MER-009 PAY-010 PAY-011 INT-009 INT-012 MER-041
- Navigates to: MD03 MD07 MD09 MD12
- Special states: percentage contract: the agreed "contract percentage" and its base (sale price minus the merchant's share of the discount) instead of the order fee and cap; Mart or pharmacy: "Store percentage" 5% and its base, with no payment fee and no contract-fee exemption (PAY-011, MER-007); exemption disabled: "Menu-link orders are treated like any order under your contract"; cashier linking failed: a red badge with the reason and a "Retry" button, and orders continue; no systems available: "No systems are enabled for you right now" with a request-a-system button

#### MD15 — Merchant Registration and Application Tracking (new)

The merchant starts registering their store themselves, uploads their documents, and tracks the status of their application and the reason for any completion request until platform approval.

- Elements: Progress steps: business data, branches, documents and bank account, platform review, approval and login details. Application status: a badge at the top: draft, under review, completion required, approved. Completion reason: the text written by platform staff, with their name and date (MER-013). Business data: trade name, store name, business type (MER-009), city, the responsible person and their mobile. Branches: location on the map and branch data (MER-001), and the status of each branch (complete, needs editing). Documents: logo, commercial register, menu, and others, each with an "Optional" tag and its status (MER-044). Bank account: partially masked IBAN. Application log: submission, completion requests, approval, with dates. Visibility note: the store is not visible to customers before approval (MER-013)
- Actions and what happens:
  - **Next (in every step)**: saves the step and moves to the next; the merchant can go back to any completed step.
  - **Submit for review / Resubmit for review**: one primary button at the bottom of the page; it submits the application, the status becomes "Under review", and the fields are locked. After resubmission the completion alert disappears and a line is added to the application log.
  - **Save and complete later**: saves the draft; the merchant returns to it with their mobile and verification code.
  - **Edit location / Replace**: opens the required field directly, and "Needs editing" changes to "Edited" after saving.
  - **Upload**: uploads an optional document, which appears with its name and the status "Uploaded".
- Validation and error messages:
  - Invalid mobile: "Enter a Saudi mobile number that starts with 05 and has 10 digits"
  - Branch location outside the selected city: "The location is outside the selected city of …"
  - Invalid IBAN: "The IBAN starts with SA and has 24 characters"
  - Empty store name: "Enter the store name"
  - File in an unsupported format: "Upload an image or PDF file"
- Permissions:
  - Only the application owner (with their registered mobile) sees and edits their application
  - Platform staff (sales or admin) decide on the application from the Merchants and Onboarding page (MER-013)
- UX decisions:
  - The progress steps and the status badge tell the merchant where their application stands without calling anyone.
- Requirements: MER-013 MER-001 MER-009 MER-044
- Navigates to: MD01
- Special states: draft: incomplete steps are gray and "Submit for review" is disabled until the basic data is complete; under review: fields are locked with "Your application has been under review since…"; completion required: a yellow alert with the reason, and the required elements are tagged "Needs editing" in place; approved: "Your store has been approved" with a step to receive login details and go to the merchant dashboard

### Driver App

#### D01 — Home and Map

Start work and view current status and earnings.

- Elements: Available or unavailable: a status card at the top of the screen ("You are available now" or "Unavailable") with an availability switch and the line "Your location is sent only while you work". Today's earnings. Tasks: the number of tasks available now on the primary "Orders" button. City. Level. Account status. "Verified" badge: next to the name if the platform granted it (DRV-007). Dues account: shown when negative, with the balance lockout threshold (−50) and the reason for each deduction (PAY-026). Demand map: neighborhoods that have orders now, with a color gradient (high/medium) (DRV-030). Best earning hours: hourly bars in the driver's city with the highest highlighted. Restriction reason bar: appears in any state that prevents tasks (see states)
- Actions and what happens:
  - **Start work**: changes the status to "Available", starts sending the location (DRV-003) and enters dispatch (DSP-001); the card changes to "You are available now" and the "Orders" button appears. If there is a blocker, the reason bar and the next step appear instead of activation.
  - **Stop availability**: changes the status to "Unavailable" immediately, and location sending and new task offers stop. With a task in progress, a confirmation appears: "You will not receive new task offers; complete your current task", and the task is not canceled.
  - **Orders**: opens D02 on "Task offer" if there is a task offer directed to them, otherwise on "Task list".
  - **Pay balance**: appears only when the balance lockout threshold is reached (PAY-026): opens payment for the full negative amount; after success the balance lockout is lifted and a "You can receive tasks again" notification appears.
  - **Open demand map**: tapping a colored neighborhood shows only its name and demand level (high/medium), with no customer data (DRV-030).
- Validation and error messages:
  - "Start work" without location permission: the message "Enable location to receive tasks" and a button that opens the phone settings
- Permissions:
  - A driver who is not approved or has not passed onboarding does not see the "Orders" button and cannot become available (DRV-001, DRV-012)
- UX decisions:
  - Status is the first card and large because the driver needs it at a glance while driving
  - One primary action in the bottom bar instead of two adjacent buttons
  - When tasks stop, the reason, the amount, and the next step appear in a single red bar instead of a generic message
  - The demand map shows colored neighborhoods, not points, so it does not reveal customer locations
  - Best hours are below the fold because they are for planning, not for the moment
- Requirements: DRV-001 DRV-003 DRV-030 PAY-026 DRV-027 DRV-007 DRV-023 DRV-012
- Navigates to: D02 D07 D08 D03 D11 D13
- Special states: account awaiting approval: the switch is disabled, and a "Your application is under review" bar with a link to D13 (DRV-001); onboarding not passed: a bar "Complete onboarding to receive your first task" with a link to D13 (DRV-012); negative dues account before the balance lockout threshold: work is normal with a yellow bar showing the balance; at −50: the "balance lockout" state and a "Task reception stopped" bar until payment (PAY-026) (second preview); suspected fake location or impossible jumps: "Your tasks are suspended pending review" with the reason, and the switch is disabled until support lifts the suspension (DRV-027); modified phone (root/jailbreak): "You cannot work from this phone" with the reason (DRV-027); ban from the penalty ladder (24 hours or permanent): the bar states the step, the reason, the end time, and a link to the objection in D11 (DRV-023); expired document: a yellow reminder only (DRV-006); task in progress: a "Current task" card at the top of the screen opens D03 instead of the "Orders" button; city or service disabled by the platform: "The service is temporarily disabled in your city"; network outage while working: a bar "No network: your events are saved and sent when you are back"

#### D02 — Available Tasks

A task offer sent directly to nearby drivers; the first to accept wins.

- Elements: Service tag: with a "Chilled" tag for an order that needs a cooler bag. Net earnings: with the line "After tax and platform percentage · + tip if any" (DRV-002). Store and customer, distances, duration, accept countdown, current capacity. "Task offer" / "Task list" toggle: the task offer directed to you with its countdown, and tasks that no one has accepted (DSP-001, DRV-018). Batching line: in an extra task offer while on a task, the current order number and the expected extra delay to deliver it (DSP-003). Eligibility line under the list: "Only tasks suited to your vehicle, equipment, services, and city appear"
- Actions and what happens:
  - **Accept**: sends the acceptance to the server (DSP-001). If first: the card is withdrawn from the others, a pickup code is created, and D03 opens. If someone else was first: "Another driver accepted this task" and the card disappears. If eligibility no longer holds at acceptance (DRV-011): "This task no longer suits you". The level benefit is fixed on the task (DRV-015). Acceptance is a final commitment: no declining after it, and an emergency goes through an emergency report from "Help" (ORD-014).
  - **Reject**: hides the task offer immediately without confirmation and counts toward the acceptance indicator; the effect of rejection and ignoring on later task offers follows (DSP-001).
  - **Open route**: shows a route preview (store then customer) on the map without accepting; the countdown continues in the background.
  - **Accept from the list**: an "Accept" button on every card in the list with the same behavior, and the card disappears from everyone's lists as soon as it is accepted (DRV-018).
- Validation and error messages:
  - Task offer whose countdown ended or was withdrawn: "This task offer is no longer available"
- Permissions:
  - Shown only to an approved, available driver (DRV-001, DRV-002)
- UX decisions:
  - Net earnings and the countdown are on one line in large type because the decision is made in seconds
  - A wide "Accept" button carries the amount, and a small "Reject" next to it reduces accidental presses
  - The task list is in a separate tab so it does not compete with the task offer, which has a deadline
  - Under the card: "If you reject it, it will not be shown to you again" so the driver knows the effect of rejecting
- Requirements: DSP-001 DRV-002 DRV-018 DRV-011 DSP-003 DRV-013 DRV-015
- Navigates to: D03 D01
- Special states: no offers now: "No nearby tasks right now · Stay available" with a link to the demand map in D01; countdown ended with no response (ignored): the card fades with "Task offer time ended"; task withdrawn because someone else accepted: a transient notification and the card disappears (second preview); capacity full: no new task offers appear and "Complete your current tasks to receive offers" shows (DRV-015); service or city disabled by the platform: its tasks do not appear (DRV-002)

#### D03 — Current Task and Route

Stops of batched orders, ordered, with expected time.

- Elements: Orders up to 3: the orders of the batched task (DSP-003). Stop order: a next-stop card (its type, the store or neighborhood, order numbers, distance, expected time) then the remaining stops. Pickup and delivery: a bar of the five task stages (DRV-004). Time: an "On time" or "Late" badge (ORD-012). Instructions. Help button: a dialog with ready-made reasons, including "An emergency prevents me from completing" for the emergency report (DRV-020, ORD-014). "Emergency" button: fixed red on the map
- Actions and what happens:
  - **Navigate**: opens the current stop's location in the preferred navigation app set in D10 (DRV-021); if none is set, it asks once and saves the choice.
  - **Arrived at store**: enabled only within the arrival distance of the store (DRV-004); records the time and location, notifies the merchant "The driver arrived" (MER-020), starts the wait counter, and opens D04.
  - **Help**: opens the reasons dialog; "Send report" opens a report linked to the order, stage, and location (DRV-020) and it appears in D11 with the status "Open". The reason "Customer not answering" opens D06. The reason "An emergency prevents me from completing" (breakdown or accident) opens an emergency report that reaches operations with priority (ORD-014); the task stays with you, and support decides whether to assign a replacement or something else.
  - **Emergency**: calls the unified number and sends the location and order to the operations room (DRV-024); no confirmation before the call so it is not delayed.
  - **Open stop**: shows the stop's instructions and its orders; the order is set by the system and the driver does not change it (DSP-003).
- Validation and error messages:
  - The emergency report requires describing the problem: "Write what happened"
  - Help report: the button is disabled until a reason is chosen
- UX decisions:
  - The next stop is in large type, with the remaining stops smaller beneath it
  - "Emergency" is separate from "Help" so they are not confused
  - The primary action changes with the stage (arrived at store, on the way, arrived) in the same place at the bottom of the screen
  - No decline button after acceptance: an emergency goes through "Help" with an emergency report
- Requirements: DSP-003 ORD-014 DRV-004 DRV-020 DRV-021 DRV-024 ORD-012 MER-020 DRV-003
- Navigates to: D04 D05 D06 D11 D15
- Special states: outside the arrival distance of the store: the "Arrived at store" button is disabled with "Get closer to the store (… m away)"; late against the reference time (ORD-012): a "Late" badge and the line "No money is deducted from you, and it appears in the performance report"; batched order added: a notification "Order [number] added · new stop order" and the arrival estimate is recalculated; network outage: a "No network" bar at the top of the screen; events are saved and sent in order (DRV-004); emergency report sent: a bar "Your emergency report reached support · wait for its decision", and the task stays with you until support assigns a replacement or decides otherwise (ORD-014); pharmacy order "returns to the pharmacy": the next stop becomes the return stop to the pharmacy and D15 opens (PHR-010)

#### D04 — Pickup from the Store

The driver's code to the merchant and pickup proof, with no products-invoice requirement in menu orders.

- Elements: Pickup code: with its status "Waiting for the merchant to enter the code" then a green "Verified" badge. Order number. Arrival distance 100 m: a badge "Within 100 m of the store". Pickup photo. Products invoice if present: a badge by order type, "Not required" or "Attached by the pharmacy/store" (MER-036). Contents. "Your wait" counter at the store: with a sentence that it is not counted against the driver (DRV-019, ORD-012)
- Actions and what happens:
  - **Show code**: enlarges the code to full screen and raises brightness so the merchant can read it easily (ORD-005).
  - **Photo**: opens the camera directly, not the photo gallery; the photo is saved with its time and location as pickup proof.
  - **Picked up**: enabled after the code is verified and the pickup photo is taken. On tap: the wait counter stops (DRV-019), the task moves to "On the way", and D03 opens on the next delivery stop or D05.
  - **Report: order does not match**: a small link that opens the help dialog (D03) on the reason "Order does not match", tied to the pickup stage.
- Validation and error messages:
  - "Picked up" without a photo: "Photograph the order first"
- UX decisions:
  - The code is in the largest type on the screen because it is what the merchant needs
  - The primary button is disabled with its activation condition written beneath it instead of an error message after tapping
  - The wait counter is visible so the driver feels their time is recorded
- Requirements: ORD-005 MER-036 DRV-004 DRV-019 MER-020 ORD-012
- Navigates to: D05 D03
- Special states: outside the arrival distance: the code is hidden and "Get closer to the store to show the code" shows; merchant entered a wrong code: nothing changes for the driver; the message is at the merchant; order not ready yet: "The store is preparing your order" with the wait counter, and a "Store is late" report can be opened; batched orders from the same store: a code for each order and a tab for each order number; code canceled after a replacement assignment: "This code is no longer valid" (ORD-014)

#### D05 — Arrival and Delivery

Delivery within 100 m without entering a customer code.

- Elements: Arrived: stage bar and the current stage "Arrived at customer". Location. Entry instructions: with the entrance photo and the corrected pin if present (DRV-028). Call and chat. Leave at the door with permission: a "Leaving at the door allowed" badge when permission exists (ORD-010, DRV-004). Photo. Task status. Line "Do not ask the customer for any code". Bar "No network: the delivery will be saved and sent when you are back". Link "Customer not answering?" to D06
- Actions and what happens:
  - **Arrived**: enabled only within the arrival distance of the customer (DRV-004); records the time and location, the order status changes to "Driver arrived" and the customer receives a notification, route measurement stops (ORD-012), and the no-response counter starts (D06).
  - **Call**: a call from inside the app; it is logged with its time as evidence of non-response (ORD-008).
  - **Chat**: opens D14.
  - **Photo**: opens the camera; the photo is delivery proof with its time and location, and the entrance photo is saved for the address (DRV-028).
  - **Delivered**: enabled within the arrival distance after proof (ORD-005); the order is closed as "Delivered", the amount is collected and the fee is added to the driver's dues account, and the driver returns to D01 or to the next stop in batched tasks. With no network it is saved and sent when back (DRV-004).
  - **Leave at the door**: appears only with permission (ORD-010); opens a dialog that asks for a photo of the order in place, then "Delivered at the door" saves the photo on the order and sends it to the customer.
- Validation and error messages:
  - Leaving without a photo: "Cannot leave without a photo"
  - "Delivered" outside the arrival distance: "Get closer to the customer's location to confirm delivery"
- UX decisions:
  - One large line, "Hand the order to the customer in person", reminds of the default
  - The entrance photo is beside the instructions because it is faster than reading an address description
  - Call and chat are two equal large buttons within thumb reach
- Requirements: ORD-005 ORD-010 DRV-004 DRV-028 DRV-021 DRV-029 DRV-003
- Navigates to: D06 D01 D14
- Special states: before arriving: "Arrived" is disabled with the distance; leaving not allowed: the option does not appear at all; customer asked for leaving in chat: the option appears automatically with a "Requested in chat" marker and its time; no previous entrance photo: the card shows address instructions only; delivery saved with no network: a "Awaiting send" badge on the order until it syncs; pharmacy order: no leaving at the door except with support permission

#### D14 — Customer Chat (new)

An automatically translated chat between driver and customer with ready replies that are logged as evidence.

- Elements: Messages: translated into the recipient's language (DRV-029). "Translated from…" line: under the message with "View original". Ready replies: I arrived at the door, I'm on my way, I'm at the store, I can't find the address. Leave-at-door request notice: when the customer requests it. Call button. Input field and send button
- Actions and what happens:
  - **Send**: sends the message translated into the customer's language (DRV-029), and it is saved with its original, translation, and time as evidence.
  - **Ready reply**: sends the text immediately with one tap, translated into the customer's language.
  - **View original**: toggles the message between the translation and the original text.
  - **Call**: a call from the app to the customer, and it is logged.
- Validation and error messages:
  - An empty message is not sent
- UX decisions:
  - Ready replies are above the input field so they can be sent with a tap while driving
  - The leave-at-door request is a prominent notice, not an ordinary message
  - The language of each message is stated so the driver trusts the translation
- Requirements: DRV-029 ORD-010 ORD-008
- Navigates to: D05
- Special states: no messages yet: ready replies only; translation failed: the message is sent in its original with "Translation unavailable"; order ended: the chat is read-only; no network: the message is "Awaiting send"

#### D06 — No Response and Help

Steps at 5 minutes and 30 minutes, then a support decision with no operations code.

- Elements: Call and message. Time since arrival. Documented conditions: a timeline with step times: arrived, called, sent a message, customer notification, support alert (ORD-008). Customer notification. Support chat. Returning the medicine if needed: a return stop in the same task (PHR-010). The sentence "Do not leave or end the order yourself; support decides". Note on the fee when ended for non-response (DRV-005). Support decision card: with its outcome (ORD-008)
- Actions and what happens:
  - **Notify customer**: enabled after the timeout if a call and a message are documented (ORD-008); sends the customer a prominent notification, and is logged in the timeline.
  - **Open report**: opens a "Customer not answering" report in the operations room linked to the order with the recorded evidence (location, time on site, calls, messages), and it appears in D11.
  - **Read support decision**: opens the decision dialog: the outcome, the amounts due to the driver, the name of who executed it and the time, and the next step: leave, or D05 to retry or leave with proof, or D15 to return the medicine.
- UX decisions:
  - The large counter and the timeline answer the driver's question "How much is left and when does support step in?"
  - Each step is documented with a check mark so the driver is reassured that their fee is protected
  - The decision is in a clear dialog with the amounts instead of a text message in the chat
- Requirements: ORD-008 PHR-010 DRV-005 DRV-004
- Navigates to: D05 D11 D15
- Special states: before the customer-notification timeout: the button is disabled with a countdown "Available after …"; at the support timeout: "Support alert sent" automatically, and the order is not closed automatically (ORD-008); ended-for-non-response decision (second preview): the fee and tip (DRV-005) and leaving is allowed; driver left the arrival distance before the decision: a notification "Stay near the customer until support decides" and the exit is logged

#### D15 — Return Medicine to Pharmacy (new)

Return stop within the same task: returning an undelivered medicine to the pharmacy with a return code that the pharmacy enters.

- Elements: Return stop within the same task: status "Returning to pharmacy" (PHR-010). Return code (ORD-005, PHR-010). Return deadline (PHR-010). Steps: support decision, on the way, pharmacy enters the code. Note: the fee and tip are protected (ORD-008)
- Actions and what happens:
  - **Navigate**: opens the pharmacy location in the preferred navigation app (DRV-021).
  - **Arrived at pharmacy**: enabled within the arrival distance; records the arrival, notifies the pharmacy, and shows the return code.
  - **Pharmacy closed? Report to operations**: opens a report linked to the order in the operations room; the order stays "Returning to pharmacy" until operations decides (PHR-010).
- UX decisions:
  - The screen resembles the pickup screen (D04) so the driver knows what to do without learning anything new
  - The code is in the largest type with an "Independent of the pickup code" badge to prevent confusion
- Requirements: PHR-010 ORD-005 ORD-008
- Navigates to: D06 D11
- Special states: outside the arrival distance: the code is hidden; deadline ended: "An alert was sent to operations to decide" and the order is not closed (PHR-010); code entered: "Returned", the order is closed, and the driver returns to D01

#### D07 — Earnings and Payouts

Net, incentives, loss charges and penalties, and their reasons.

- Elements: Delivery and tip after tax: two separate lines, delivery after tax and platform percentage, and the tip after excluding its VAT: a tip of 10 yields 8.70 (PAY-014). Platform percentage. Incentives. Loss charge and penalty: two separate lines with the type of each, and each amount with its reason and order number beside it (PAY-025). Net. Payout date. Payout account: the STC Pay wallet with its last 4 digits and status (approved, or awaiting Finance approval), with a line "Your earnings are paid out automatically on [day] without approval" (INT-014). Payments log: each payout with its status and reference (STC Pay transaction number) (PAY-006, INT-014), including "In progress". Dues account balance: excludes the deposit, with the held deposit line shown separately (PAY-024). Task list: with the badges "Late tip" and "Ended for non-response · full fee". Negative-balance deduction from the next payout: a visible line (PAY-026)
- Actions and what happens:
  - **Open task**: opens the task statement (second preview): delivery fee, tax, platform percentage, fee, tip and the time it was added if it was late, wait time at the store, and any delivery offer (PAY-014).
  - **Statement**: opens the live statement for the selected period with all movements (fees, tips, incentives, loss charges, penalties, reversal entries, payouts) with a PDF export button.
  - **Objection**: opens D11_2 filled with the selected loss charge or penalty; the window is 7 days from the decision notification, after which "Objection period ended" shows (DRV-023).
  - **Switch period**: Day/Week/Month changes only the numbers and the list, not the balance.
- UX decisions:
  - One large number (the balance) on top, with its breakdown beneath as a sum equal to the number
  - The deposit is visually separated from the balance so the driver does not think it is withdrawable money
  - Payout status is a clear word and color, and a failed one is red and not confused with paid
- Requirements: PAY-014 PAY-025 PAY-006 INT-014 DRV-005 PAY-026 PAY-024
- Navigates to: D11 D10
- Special states: late tip: a notification "The customer added a tip of [amount] to order [number]" and it appears in the same task's statement (DRV-005); negative balance: the number is red with "Deducted from your next payout", and at the balance lockout threshold (−50) a "Task reception stopped" bar and a payment link (PAY-026); payout failed: "Failed · not paid" with a link to update the STC Pay account in D10 (PAY-006, INT-014); deduction not yet approved: does not appear in the balance (PAY-026); reversal entry after an objection is accepted: a green line "Refunded: your objection on [number] was accepted"; task whose driver was replaced: per (PAY-014), and any compensation to the first driver is a manual line with its reason; STC Pay wallet not yet approved: "Your payout arrives after Finance approves your number", and nothing is sent before then (INT-014)

#### D08 — My Performance

One page with filters for 10 orders, 30 orders, 30 days, and custom.

- Elements: Score, level, display period: with a note that filters other than "Last 30 days" are for display only (DRV-017). Indicators: the seven, with each indicator's weight beside its name (DRV-017). Notes: lateness (ORD-012) and emergency reports (ORD-014). Tip. Level score over 30 days. Exceptions line: what is not counted in the score (DRV-017). Last daily update date
- Actions and what happens:
  - **Change period**: switches the numbers between periods (DRV-017), and custom opens a two-date picker; the displayed score changes, while the level and its badge do not change and "Your level is from the last 30 days" is written beneath them.
  - **Indicator details**: opens the indicator dialog: the value, the target, the score from the weight, and the orders that affected it with a link to each order.
  - **Objection**: from a specific note opens D11_2 linked to the order and the note.
- Validation and error messages:
  - Custom period: start before end, and not later than today
- UX decisions:
  - Score and level in one ring at the top of the screen
  - The weakest indicator in a different color with a related tip
  - Showing the weights explains to the driver why one indicator matters more than another
- Requirements: DRV-017 ORD-012 ORD-014 DRV-015
- Navigates to: D09 D11
- Special states: new driver: "Your level is new · your score is calculated after 30 orders" and the indicators are for diagnosis only; no ratings in the period: "No ratings yet" and the indicator is excluded (DRV-017); custom period with no orders: "No orders in this period"; score under watch: a "Under watch" badge with the tip (DRV-015, DRV-017)

#### D09 — Level and Incentives

Targets, benefits, progress, budget, and duration.

- Elements: Target. Progress. Peak incentive. Level benefits: in the driver's city, in numbers, with "Fixed on the task the moment you accept it" (DRV-015). City incentive. Expiry. The five-level ladder with its thresholds (DRV-015). Score remaining to the next level. The four incentive types: for the driver's city only (DRV-006). Each incentive's card: days and hours, incentive amount, status (active, ending, budget exhausted)
- Actions and what happens:
  - **Details**: opens the incentive with its settings (DRV-006), how your progress is calculated, and the tasks that were counted.
  - **Object to a note**: opens D11_2 linked to the incentive or note (for example a task that was not counted).
  - **Invite a driver**: in the referral incentive: shares an invitation link; invitees and their status appear.
- UX decisions:
  - The level ladder is horizontal with the current level highlighted so the driver knows where they are and what comes next
  - Each incentive has one progress card and a colored status badge
- Requirements: DRV-006 DRV-015 DRV-017
- Navigates to: D08
- Special states: incentive reached its budget: "Incentive stopped because its budget was reached" (DRV-006); ended incentive: moves to "Past incentives" with what you earned; level not eligible for an incentive: the card is gray with "For levels: …"; no incentives in your city: "No active incentives in [city] right now"; level changed in the daily check: a notification "You became [level]" or "Your level dropped to [level]" with the reason

#### D10 — My Account, Vehicle, and Equipment

Operating data, bank, deposit, equipment, and services.

- Elements: Driver type, Vehicle and its photos: type, allowed services and maximum distance, display only (DRV-011), Equipment: with the effect of lacking a cooling bag (DRV-013), Bank and STC Pay: the IBAN for the earnings payout after the accountant's approval, for the deposit refund, and for account-closure settlement, and the STC Pay wallet (last 4 digits) when INT-014 is enabled later, and the status of each: approved or under review (INT-014), Deposit: the amount and status (paid and held, or refund pending), separate from the dues account (PAY-024), Regular services, Optional files: to request a "Verified" badge, "Verified" badge and its explanation (DRV-007), Document expiry reminder: a single yellow card that states explicitly that it does not stop tasks (DRV-006), Preferred navigation app, Conversation language (Arabic, English, Urdu)
- Actions and what happens:
  - **Edit**: opens the item for editing. Changing the vehicle, equipment, bank, or STC Pay number is sent for review and the old one stays active until approval; changing navigation and language is immediate.
  - **Upload file**: opens the camera or files; the optional file is sent for verification review, and its status shows (under review, accepted, rejected with the reason).
  - **Request closure via support**: opens a dialog (second preview) showing the settlement: the dues account balance, the deposit, and the net that is refunded. Confirming opens a closure ticket in D11 and stops task reception immediately (PAY-026).
  - **Hadaf deliveries**: opens D12 (DRV-022).
- Validation and error messages:
  - IBAN: 24 characters starting with SA; the message "Check the IBAN number"
  - STC Pay number: a Saudi mobile of 10 digits starting with 05; message "Check the STC Pay number"
  - File: image or PDF only; the message "File type is not supported"
- Permissions:
  - The driver edits their own data; changing the type (Saudi freelancer/resident) is through support only
- UX decisions:
  - Status (active, verified) in the page header as badges
  - The closure button is red at the bottom
- Requirements: DRV-001 DRV-013 PAY-024 INT-014 DRV-007 DRV-011 PAY-026 DRV-021 DRV-029 DRV-006
- Navigates to: D11 D12
- Special states: edit under review: an "Under review" badge on the item; verification rejected: the reason and an "Upload another file" button; closure request open: a "Closure request is being settled" bar and the closure button is disabled; resident driver: the "Hadaf deliveries" link does not appear; first STC Pay number under review: "Your payout will arrive after Finance approves your number"; changing an approved number keeps the old one active until the new one is approved (INT-014)

#### D11 — My Tickets and Objections

A ticket linked to a task, or an objection of a loss charge, penalty, or penalty step.

- Elements: Task, reason, evidence, amount if any, messages. Objection decision: accepted (reversal entry) or rejected with the reason (PAY-025). Tabs: All, My objections, Actions (penalty ladder: warning, then priority lowered for a week, then a 24-hour ban, then operations review, then a permanent ban). Penalty-ladder step notice: the reason, the next step, and the last date to object to: 7 days from the notice (DRV-023). Objection response counter (DRV-023). Help reports: linked to the order and stage, including the emergency report (DRV-020, ORD-014)
- Actions and what happens:
  - **Ticket**: opens a new ticket form: topic (help with a task, financial inquiry, object to a loss charge or penalty, object to a penalty step, closure request), task, description, attachments; after sending it appears in the list with the status "Open".
  - **Reply**: sends a message in the ticket; it is saved with no network and sent when back.
  - **Attach**: attaches an image or document to the ticket or objection.
  - **Objection**: opens D11_2 for the selected loss charge, penalty, or penalty step, within 7 days of the decision notification (DRV-023); if accepted on a deduction it appears as a reversal entry in D07.
- Validation and error messages:
  - Objection reason at least 10 characters: "Write your objection reason in at least 10 characters"
  - The topic is required
- UX decisions:
  - Penalty-ladder actions are at the top of the screen because they directly affect the driver's work
  - Each item shows its status as a colored badge and the time remaining to respond
  - The objection form shows the amount, the reason, and the deadline before the input field
- Requirements: DRV-020 DRV-023 PAY-025 DRV-004
- Navigates to: D07
- Special states: permanent ban by a staff decision without the gradual steps (fraud, location spoofing, account sharing, abuse of a customer): a red card with the reason and an objection link (DRV-023); objection period ended: the button is disabled with "Objection period ended"; response deadline passed with no response: a "Response late" badge; no tickets: "No messages · If you face a problem on a task, use the Help button"

#### D11_2 — Objection Form

A sub-screen of D11 opened from the "Object" button on a loss charge, penalty, penalty step, or performance note.

- Elements: What is being objected to (the task or the note), Amount if any, Decision reason, Deadline for objection (7 days from the notice), Objection reason field, Attachments
- Actions and what happens:
  - **Send**: The objection is created with the status "Open" and appears in D11 with the response counter (48 hours)
- Validation and error messages:
  - Objection reason at least 10 characters: "Write the reason for your objection in at least 10 characters"
- Requirements: DRV-023 SUP-006 PAY-025

#### D12 — Hadaf Deliveries

Monthly delivery count for the Saudi driver.

- Elements: Month or custom range: the current month is shown as "to date". Count: with a "Matches the completed tasks log" badge and the line "Canceled and undelivered orders are not counted". Verified orders. Report: name, driver type, period (DRV-022)
- Actions and what happens:
  - **Export**: generates a PDF report (DRV-022) with the count and the list of completed orders (number and date), and saves it on the phone.
  - **Share**: opens the phone's share sheet with the same report file.
  - **Change month**: switches the count and the list; custom opens a two-date picker.
- Validation and error messages:
  - Custom range: start before end and not later than today
- Permissions:
  - Saudi driver only (DRV-022); for a resident the page is unavailable and its link does not appear
- UX decisions:
  - The count is in the largest type with the match badge
  - Export is the primary action and Share is secondary beside it
- Requirements: REG-006 DRV-022
- Special states: month with no deliveries: "No completed deliveries this month" and export is disabled; order closed after the end of the month: attributed to its closing date

#### D13 — Registration and Onboarding

Registration, then approval and operational onboarding before the first task.

- Elements: Contact. Vehicle: type car or motorcycle (DRV-011). Photos. Bank. City. Deposit: paid before activation (PAY-024). Short onboarding: lessons then a test (DRV-012). Application status. The six registration steps: contact, vehicle, bank, deposit, review, onboarding. Driver type: Saudi freelancer or resident freelancer (DRV-001). Equipment (DRV-013). Optional files: to request the "Verified" mark (DRV-007)
- Actions and what happens:
  - **Submit**: after the steps are complete and the deposit is paid, sends the application to the platform; the status becomes "Under review" and a notification arrives with the decision.
  - **Continue**: saves the current step and moves to the next; the driver can leave and return without losing inputs.
  - **Pass onboarding**: submits the test answers; on success (DRV-012) D01 opens with "You can now receive your first task". On failure the wrong questions show with explanations and a "Retake test" button.
  - **Pay the 100 SAR deposit**: opens payment; after success it shows "The deposit is held, separate from your dues account, and refunded when the account is closed after settlement" (PAY-024).
- Validation and error messages:
  - Mobile number Saudi 05xxxxxxxx: "Enter a valid mobile number"
  - The three vehicle photos are required: "Add the rear photo"
  - IBAN 24 characters starting with SA
- UX decisions:
  - Short steps with a progress bar at the top of the screen instead of a long form
  - Type and vehicle options as large cards instead of a dropdown
  - The test is one question per screen with large answers
- Requirements: DRV-001 DRV-012 PAY-024 DRV-011 DRV-013 DRV-007 DRV-004
- Navigates to: D01
- Special states: under review: "We are reviewing your application" with what was submitted; rejected or incomplete: the reason and the item that must be edited; approved but onboarding not passed: second preview; test failed: the lessons related to the wrong questions are repeated

### Admin Dashboard

#### A01 — Home

Growth, problems, and what needs intervention.

- Elements: Period and custom: the period filter, and "Custom" shows two date fields and an "Apply" button. City and category: two filters in the title bar that apply with the period to the whole page. Orders and revenue: unified indicators (ADM-030): delivered orders, total sales, platform revenue, average order value, lateness rate, cancellation rate; each with the change from the previous period and a tooltip defining each number. Demand map. Top stores: a table with a "Lateness" column. Alerts: an "Needs intervention now" bar at the top of the page with four cards: orders with no driver for more than 15 minutes, unreceived operational alerts, open anomalies, merchant onboarding requests. Last updated: a stamp in Riyadh time under the title. Anomalies (ADM-012): the type of the spike, its level and its source, the current value versus the usual in one sentence instead of a chart, the detection time, and an "Open source" button. Announced-time accuracy (ADM-011): the average difference per city, the most deviating store, and a "Report for every store" link. Cancellation by cause: customer, no driver, out-of-stock item, merchant, driver, non-payment; and their sum equals the cancellation rate
- Actions and what happens:
  - **Open an indicator**: opens the list from which the number was calculated with the same filters (ADM-030): orders -> A03, merchants and onboarding requests -> A05, alerts and orders with no driver -> A02, anomalies -> the spike's source. No confirmation.
  - **Filter**: applies the period, city, and category to the whole page and saves them for the session. While recalculating, the old numbers stay faded until the new ones arrive.
  - **Open source (anomaly)**: opens the list of operations that produced the spike filtered by its source and time. It changes nothing.
  - **Mark anomaly as reviewed**: a dialog with a required note (what was found and what action was taken). On save the anomaly disappears from the intervention bar and stays in the alerts log with the staff member's name and time, and it returns if a new spike is detected from the same source.
  - **Report for every store (time accuracy)**: opens the announced-time accuracy report (A21) filtered by city and period (ADM-011).
  - **Open a store row**: a row in "Top stores" opens the merchant page (A06).
- Validation and error messages:
  - Custom range: end before start -> "End date must be after start date" and "Apply" stays disabled.
  - Date in the future -> "Choose a date up to today".
- Permissions:
  - The page is for all roles within their cities: admin, support supervisor, support agent, operations, finance, sales.
  - Total sales and platform revenue: admin and finance only.
  - Intervention bar: the store onboarding requests card for admin and sales, and the rest for admin, support supervisor, support agent, and operations.
  - "Mark anomaly as reviewed": admin, finance, and support supervisor.
- UX decisions:
  - The intervention bar is the first thing seen, before the growth numbers, and its cards are colored by severity.
- Requirements: ADM-030 ADM-011 ADM-012
- Navigates to: A02 A03 A05 A06 A21
- Special states: nothing needs intervention: the bar cards show zero in a neutral color with the text "Nothing needs your intervention right now".; incomplete "Today" period: a "Partial until [time]" badge beside every number, and the comparison is with the same period of the previous day.; staff member with limited role scope: the numbers and the city list are for their cities only, and under the title "Your cities: [cities]".; role without financial reports permission: "Total sales" and "Platform revenue" are hidden, and the remaining cards expand.; no previous period (new city): "—" instead of the change percentage with the tooltip "No previous period".

#### A02 — Operations Room

Order, alert, its owner, and the parties map.

- Elements: Services without Taxi: service filter: restaurants, Mart, pharmacies, Shops, write-in, self-pickup; City: filter; Status: filter; Map: parties of the selected order and its route; Nearby drivers: table for the unassigned order: name and number, distance (DSP-001), score, 30-day deliveries, priority index and its breakdown, tier, status (free, has a stackable task, rejected this order, preferred captain); Stage times: for the selected order, preparation vs. the stated duration and route vs. the reference (ORD-012); Alerts: for each alert a timer showing its age, type, order, owner ("Unclaimed" or the staff member's name, also shown on the order), priority by color, next deadline (e.g. "Intervene at [time]"), and a handling guide and the required action; Room tabs (ADM-003): dashboard, orders, order file, penalties and loss charges, cities and incentives, drivers and branches now, alert and shift rules; Shift badge in the title bar: pickup time, the staff member's cities and services, count of items under their name, and a "Hand over shift" button; Indicators bar for the selected city and service (ADM-014); "Alert and shift rules" tab (second preview): rules list, rule editor (ADM-005) with handling guide, and an "On shift now" table; "Instant disable" window (ADM-004): type, item, written reason, and impact summary
- Actions and what happens:
  - **Claim alert**: reserves the alert under the staff member's name immediately with a single server operation, so their name appears on the alert and the order for everyone and the "Mine" button disappears for others; opens the order, its evidence, and the handling guide. If a colleague got there at the same moment: "[Name] claimed it moments ago" and nothing changes. No confirmation.
  - **Assign**: window: a driver from the eligible table or by number, and a written reason (DSP-002). The confirmation "Assign order #[number] to [driver]" delivers the order to the driver as assigned, which is binding like acceptance (DSP-002), withdraws the task offer from the others, records the actor, reason, and time in the order events, and closes the "no driver" alert. If another driver accepted before saving: "The order was just accepted by [driver]" and the manual assignment is canceled.
  - **Transfer staff member**: window: a staff member who is on shift now and covers the order's city, and a mandatory note. Confirming moves the alert and the order under their name, records the transfer with both parties' names and its time, and the new staff member receives an alert (ADM-042).
  - **Call**: list: customer, merchant, driver. The call starts from the dashboard and is logged in the order events as "Call from [staff member] to [party] [time]" with its duration. Call center is Later (ADM-003).
  - **Escalate**: window with a mandatory note; raises the alert to the support supervisor (or whoever the rule specifies) and shows it with an "Escalated" badge at the top of the list; its owner keeps it until the supervisor decides to transfer it. The escalator and time are recorded.
  - **Mine**: the short name for "Claim alert" inside the alert row; same result.
  - **Take over shift**: opens the previous handover notes for everything that will become theirs; "Read and taken over" starts the shift, records the time, and the items move to them (ADM-042).
  - **Hand over shift**: window listing every open order and alert under their name, each with a mandatory note (ADM-042). "Hand over and end my shift" is disabled until all notes are complete. Confirming moves the items to the next shift's staff member (or to automatic distribution) and records the handover (ADM-042).
  - **Redistribute**: for the supervisor: window to distribute cities and services among those present, and to move one staff member's alerts to another in one batch. Every transfer is logged.
  - **Offer self-pickup or refund**: appears for a non-Mart order that reached the intervention deadline (ORD-004). A confirmation states the impact, then the customer receives the two options (ORD-004, EXT-006). The alert follows the customer's choice and is closed by it.
  - **Cancel and refund (Mart after 15 minutes)**: opens the cancellation window in the order file (A03), with the cause "no driver" and the reason pre-suggested (ORD-004).
  - **Instant disable**: shows the impact before confirming, such as "[Branch] will not receive any new orders; ongoing orders complete". The confirm button is red "Disable now". Takes effect immediately without an app update (ADM-004), and the item shows a "Disabled" badge with the reason and actor, and is resumed with a "Resume" button and a written reason.
  - **Message**: opens a chat with the customer, merchant, or driver linked to the order (ADM-010).
  - **New rule / Save and apply now**: saving takes effect immediately on new events (ADM-005) and records the editor and the values before and after. "Stop rule" with a confirmation stating that new alerts of this type will not appear.
- Validation and error messages:
  - Assign with a non-existent number → "No driver with this number".
  - Ineligible driver → the specific reason: "Outside the order's city", "Excluded from this branch", "Has no cooler bag", "Has a private zone that does not include the branch", "Stopped from tasks: balance −50", "Suspended for review".
  - Empty reason for assign, escalate, transfer, or disable → "Write the reason".
  - Incomplete handover → "Write a note for each open item ([count] remaining)" and the button is disabled.
  - Transfer: a staff member who is off shift or whose cities do not match does not appear in the list.
  - Rule editor: "Intervene after" is not greater than "Alert after" → "The intervention time must be after the alert time".
- Permissions:
  - View the room: admin, support supervisor, support agent, operations; finance read-only; sales cannot see it.
  - Assign, reassign, call, escalate, and claim alert: admin, support supervisor, support agent, operations, within their cities.
  - Cancel, refund, and offer refund to the customer: admin, support supervisor, support agent; not shown to operations.
  - Redistribute and transfer others' alerts: support supervisor and admin.
  - Alert rules: admin edits; the rest read only.
  - Instant disable: city and payment method for admin; branch for admin, support supervisor, and operations; ad for admin and sales.
- UX decisions:
  - Alerts are sorted by severity, then age.
  - The selected row opens the map and the nearby-drivers table for that same order without leaving the room.
- Requirements: ADM-003 ADM-042 ADM-004 ADM-005 ADM-014 DSP-001 ORD-004 ORD-007 ORD-012 ORD-008 DRV-027 EXT-006 MER-038
- Leads to: A03 A04 A09 A10 A20
- Special states: Alert claimed by a colleague: the row shows their name, "Mine" is hidden, and the order actions are disabled with the hint "[Name] is working on it · ask the supervisor for a transfer".; Shift not started: the room is read-only with a "Start your shift" bar, and all buttons are disabled except "Take over shift".; Order reached the intervention deadline (ORD-004): automatic task offering stops, the row is red with an "Intervene now" badge, and intervention options appear by type.; No eligible driver: the nearby-drivers table is empty with the text "No eligible driver within 10 km" and a "Assign by driver number" field.; Driver suspended for location spoofing (DRV-027): does not appear in the nearby list, and their alert has a "Spoofing" badge.; Emergency report from a driver after acceptance (ORD-014): a high-priority alert on the order, and the staff member decides to assign a replacement manually or handle it otherwise; the order returns to automatic dispatch only by their decision.; Real-time update delayed: a yellow badge "Last updated [count] seconds ago" next to the title until the connection returns.; Rule with no configured duration: "Stopped" with a "Duration not configured" badge and it does not run until configured.

#### A03 — Orders and Order File

A full reference for the order, events, money, and evidence.

- Elements: Status: four independent statuses in cards at the top of the file (ORD-001): internal order status and what the customer sees, payment (held, collected, hold released, refunded) and its amount, driver task, products invoice; with order progress steps by type and the current step highlighted; Source: in the file header with the order number, city, and the staff member working on it; Service: route type in the file header (menu, Mart, write-in, pharmacy, self-pickup); Events: with actor and time, including the dispatch attempt number, its task-offer radius, and the acceptance or assignment time; and times vs. the reference: preparation (ORD-007), route, and driver wait (ORD-012); Amounts per party: what the customer paid and its status, the tip and its net to the driver after excluding its 15% VAT (CUS-010), the merchant's due after the contract percentage and online payment fee (2.5% + 1 on products after discount), the invoices by type: the products invoice (its photo and amount, mandatory for write-in and pharmacy), and the platform invoice for delivery and service, and the payment timer (ORD-013); Photos: evidence: pickup and delivery photo, driver route, "arrived" location, call and message log; and the pharmacy prescription; Chats: with customer, merchant, and driver tabs and a send field, linked to the order (ADM-010); "All orders" tab: search by order number, customer, store, or driver, and filters for city, service, status, period, and causing party; columns: number, store, service, status, payment, age, owner staff member; "Awaiting support decision" tab with a count, by reason for entry: out-of-stock item, unpaid (write-in), rejected before the products invoice (including pharmacy without prescription), no-show (self-pickup), unresponsive customer; Intervention bar at the top of the file: its reason (ticket, delay, no response) and what needs to be done; Support decisions log (SUP-003): reason, responsible party, evidence, actor, time, values before and after, and the loss charge and penalty as two separate lines, objection, and the reversal entry if any; "Cancel because of" window (second preview): the causing party, reason, the liable party for the loss charge (merchant, driver, platform, or "No loss charge") and its amount (ORD-004), and an optional separate penalty with its amount and destination, evidence, refund to the customer, what is paid to the driver and their tip, impact summary per party, and role limit
- Actions and what happens:
  - **Refund**: available after collection; before it, disabled with the hint "The amount is still held". Window: items or an amount, the reason, the liable party (merchant, driver, or platform), evidence. The confirm button is "Refund [amount] SAR to the customer" and states the impact on the liable party. It is refunded to the same payment method, and the entry is recorded (ADM-043) and appears as a loss charge in the liable party's statement with the right to object within 7 days, or as an expense on the platform (PAY-025). Above the role limit it goes to "Awaiting approval" in A04.
  - **Compensation**: window: the compensation amount, the reason, the source (platform or a penalty on a party) (PAY-025). The confirm button is "Give the customer a reward of [amount] SAR". The customer receives a notification of the reward to collect within 24 hours, otherwise it lapses with a reversal entry (PAY-002); and the entry is recorded. Subject to the role limit.
  - **Cancel because of**: appears only after the customer's grace period and only for those with permission, and opens the cancellation window; save conditions (ORD-004). The confirm button is red "Cancel the order and refund [amount] SAR". After it: status "Canceled by support", the full amount hold is released, the task is withdrawn from the driver, the customer, merchant, and driver are notified, the loss charge and penalty, if any, are recorded in A04 as effective (or awaiting approval above the role limit) with the right to object, and the causing party is counted in the cancellation rate.
  - **Reassign**: Dialog: a table of eligible drivers with priority index or a driver number, and a mandatory reason; this is how an emergency report after acceptance is handled (ORD-014). Confirmation pulls the task from the current driver and notifies them of the reason, sends it to the new one as an assignment binding like acceptance, and logs the event. After the driver has picked up the order, a warning "The order is with the current driver" appears, and reassignment at that point is for the support agent and support supervisor only, with a mandatory reason.
  - **Message / Send**: sends to the party selected in the chat tab; it appears for them in the app linked to the order, and is saved in the file with the staff member's name and time.
  - **No-response decision**: appears after the support deadline from "arrived" (ORD-008). A window shows the evidence (staying near the customer and for how long, calls, messages) and the three decision options with a written reason; the impact of each option per ORD-008.
  - **Amounts decision (out-of-stock item or unpaid)**: for an order "Awaiting support decision" because of an out-of-stock item (MER-032) or unpaid (ORD-004): a window with fields for how much of the delivery the customer bears, what is refunded to them, what is paid to the driver, the loss charge or penalty on the merchant for the out-of-stock item if any, and a written reason (ORD-013). The order is closed only after saving.
  - **Decision on rejection before the products invoice**: for a write-in or pharmacy order rejected before the products invoice, including medicine without a prescription: fields for how much of the delivery fee is refunded, what is paid to the driver, and a written reason (ORD-013, PHR-012). Saving sends the customer the cancellation notification and its reason and closes the order.
  - **"No-show" decision (self-pickup)**: fields for what is collected from the customer and what is refunded, the merchant's share, and a written reason (EXT-006); the order stays "Awaiting support decision" until saving, then it is closed.
  - **Offer self-pickup or refund**: as in Operations Room A02 (ORD-004).
  - **Loss charge or penalty**: opens "Manual add" in A04 with the order pre-filled (PAY-025).
- Validation and error messages:
  - Empty cancellation reason → "Write the cancellation reason" under the field, and the confirm button is disabled.
  - Liable party not selected → "Choose who is liable for the loss or "No loss charge"".
  - Merchant or driver without an amount → "Write the loss charge amount"; zero or negative → "The amount must be greater than zero".
  - Driver picked up the order and what is paid to them was not specified → "Specify what is paid to the driver or write 0".
  - Refund greater than the collected, unrefunded amount → "Maximum [amount] SAR".
  - Amount above the role limit → yellow notice "Exceeds your limit ([limit] SAR); it will be sent for approval" and the button becomes "Send for approval".
  - Reassign to an ineligible driver → the specific reason as in A02.
- Permissions:
  - View the file and list: admin, support supervisor, support agent, operations (within their cities); finance read-only.
  - Cancel because of, refund, compensation, and closing decisions: admin, support supervisor, support agent; not shown to operations or finance.
  - Reassign: admin, support supervisor, support agent, operations.
  - Reverse a previous support decision (from A04): support supervisor, finance, and admin.
  - Prescription photo: admin, support supervisor, and support agent only.
  - Amount limit per role (ADM-043).
- Requirements: ORD-001 ADM-043 ORD-004 ORD-006 ORD-007 ORD-012 ORD-008 ORD-013 PHR-012 EXT-006 SUP-003 ADM-010 PAY-025
- Leads to: A02 A04 A06 A10 A19
- Special states: Within the customer's grace period: "Cancel because of" is hidden, and a bar "The customer can cancel on their own until [timer]".; Awaiting support decision: an orange bar states the reason for entry (such as "Unpaid within 10 minutes") and the appropriate decision button; nothing is captured, refunded, or closed before the decision (ORD-001).; Write-in awaiting payment: the payment timer next to the payment status, and the first payment (delivery) is held.; Final order (delivered or closed): only refund, compensation, and messaging are available.; Another staff member is working on it: actions are disabled with "[Name] is working on it · ask for a transfer".; Mart order: no self-pickup option in any window (ORD-004).; Canceled by the customer during the grace period: status "Canceled during grace period", the payment hold is released, and it never reached the merchant.; Support decision under objection: an "Objection open" badge in the support decisions log with a link to A04.; Compensation reward not collected within 24 hours: a "Compensation lapsed" line with its reversal entry in the support decisions log; "Compensation" grants a new reward and the lapsed one is not reactivated (PAY-002).; Medicine whose refund was declined: "Kept at the pharmacy until [date]" for 7 days, and redelivered with a new order for the delivery fee only; after that "Destroyed" with no refund (PHR-010).

#### A04 — Penalties and Loss Charges

Imposing, reviewing, and objecting, by authorized decision only.

- Elements: Order: order number or report, Liable party: merchant or driver, or the platform for a loss charge (platform expense), Type: loss charge (to the extent of an actual loss) or penalty (a sanction beyond the loss); each is a separate line in the statement (PAY-025), Reason: written, Amount and its destination (PAY-025): for a loss charge, refunding what the customer paid or covering the loss, and for a penalty, the platform or customer compensation, Evidence, Actor: with the date and execution time for each entry, Approval: the actor's role limit and the text "Within your limit, so it is executed without approval" or "Above your limit, so it is sent for approval"; and what awaits approval in a separate card beside the form with "Approve" and "Reject" buttons in the same row, Objection: its status in the log, and its window is 7 days from the decision notification (SUP-006), summary at the top of the page: awaiting approval (count and amount), open objections, effective this month, reversal entries; each number opens its list, filters: period, city, party, approval status, objection status, Impact before saving: for a driver, their dues account balance after the deduction, the balance lockout threshold (−50), and that the deposit is not touched (PAY-026); for a merchant, that the amount is deducted from their dues and appears in their statement, Reversal entry in the log under its original, linked to it (↳) with its reason and actor, Entry details when opened: evidence, objection text and support's reply, values before and after (SUP-003)
- Actions and what happens:
  - **Manual add**: Form: the order or report, the type (loss charge or penalty), the responsible party, the amount, the outcome, the reason, the evidence. The save button "Save and deduct [amount] SAR" is disabled until the reason and evidence are complete. Within the role limit it is recorded as effective immediately, deducted, and the party receives a notification (PAY-025); above it, it is recorded as "Awaiting approval" (ADM-043). A loss charge on the platform is recorded as an expense without deduction. If the deduction brings the driver to the lockout limit (PAY-026), this is stated in the confirmation.
  - **Approve**: for the higher role only, and the actor cannot approve their own entry. Confirmation "[Amount] SAR will be deducted from [party]'s dues". After it the entry becomes effective, the approver and time are recorded, and the party is notified.
  - **Reverse**: window with a mandatory reason and confirmation "Reverse [amount] SAR to [party]". Creates a reversal entry of the same amount linked to the original without deleting it; the amount returns to the party and they are notified. If the original's month is closed, the reversal is recorded in the open month.
  - **Compensate**: directs the amount of an effective penalty (all or part) as compensation to the same order's customer, who receives it as a reward (PAY-002); a confirmation states the amount and the customer. The destination becomes "Customer compensation" and the entry is recorded (PAY-025).
  - **Reject**: for the approver: rejects an entry awaiting approval with a mandatory reason; it touches no balance, and the actor is notified of the reason.
  - **Accept objection**: opens "Reverse" pre-filled with the reason "Objection accepted", and notifies the party of the acceptance.
  - **Reject objection**: a mandatory written reply reaches the party; the entry stays effective and the objection status is "Rejected".
  - **Open order**: the order number opens its file in A03.
- Validation and error messages:
  - Order or report is mandatory and within the staff member's cities → "No order with this number in your cities".
  - Amount greater than zero with two decimal places → "Write a valid amount".
  - Empty reason → "Write the reason"; missing evidence → "Attach at least one piece of evidence; a loss charge or penalty is not saved without evidence".
  - Liable party is merchant or driver; and "the platform" for a loss charge only, with a written reason (PAY-025).
  - A loss charge does not exceed the proven loss → "Anything beyond the loss is a penalty; choose "Penalty"" (SUP-002).
  - Reason for rejection, reversal, and objection reply is mandatory.
- Permissions:
  - Manual add: admin, support supervisor, support agent.
  - Approve above the role limit: the higher role (ADM-043).
  - Reverse with a reversal entry and accept objection: admin, support supervisor, finance.
  - Compensate: admin, support supervisor, support agent.
  - Operations and sales do not see the page; whoever lacks the loss charge and penalty permission does not see the add button and the server does not execute it.
- Requirements: PAY-025 ADM-043 SUP-003 PAY-026 ORD-007
- Leads to: A03 A10 A18
- Special states: Awaiting approval: yellow badge, and the actor sees "Awaiting approval by [name]".; Reversed entry: the original has a "Reversed" badge.; Open objection: the entry is effective with the status "Under objection" and "Accept objection" and "Reject objection" buttons for those with permission.; Month closed: hint "The original is in a closed month; the reversal will be recorded in [open month]".; Nothing awaiting approval: "No entries awaiting your approval".

#### A05 — Merchants and Onboarding

Merchants, branches, contracts, and onboarding requests.

- Elements: City: filter, Type: column "Type · Ordering method" (MER-046), Status: colored badge and counters: active, awaiting approval (including those with incomplete data), disabled, draft; and under the disabled one its reason, actor, and time, Onboarding requests: tab: merchant, type, city, request date, account manager, what is missing, Account manager: column and filter, Branches, Contract: its type: percentage, or per-customer fee and branch, Data completeness (X/9) and exactly what is missing: location, city, hours, duration, minimum, bank account (approved by finance), contract, users, menu, or a catalog subscription for Mart, with priced products (MER-001), search by merchant or branch name, bulk selection with an actions bar: assign account manager, export
- Actions and what happens:
  - **Add**: window: merchant name, operational type, city, first branch, account manager. Saving creates the merchant as a "draft" and its first branch with its city's zone (MER-046) and opens its page (A06) to complete the data.
  - **Import**: upload an Excel file using the template, then a check: the number of valid rows, and errors with row number and reason. The button "Add [count] merchants as drafts · skip [count]" adds only the valid ones; no merchant is approved by import.
  - **Approve**: window with the completeness list; the button is disabled if an operational item is missing, with a hint about what is missing (MER-001). The confirmation "Approve [merchant]" makes it active and receiving orders, notifies the merchant, and records the approver and time.
  - **Open file**: opens the merchant page (A06) on the "Overview" tab.
  - **Instant disable**: from the merchant page or the actions menu: the branch, a mandatory reason, and confirmation "[Branch] will not receive any new orders; ongoing orders complete". Takes effect immediately (ADM-004) and shows "Disabled" with the reason.
  - **Resume**: for a disabled branch: a written reason, then it receives orders immediately and the actor is recorded.
  - **Reject onboarding request**: a mandatory reason reaches the applicant, and the request moves to "Rejected" without deletion.
  - **Assign account manager**: for the bulk selection: choose a sales staff member then confirm with the number of merchants; the change is recorded.
  - **Export**: downloads an Excel file of the current list and its filters.
- Validation and error messages:
  - Name, type, and city are mandatory in "Add" → "Choose the city".
  - Duplicate name in the same city → "A merchant with this name exists in [city]; open it instead of creating a new one?".
  - Import rows: "Row [number]: unknown city", "Row [number]: type must be restaurants, Mart, pharmacy, or Shops".
  - Reason for disabling, resume, and rejection is mandatory.
- Permissions:
  - Add, import, approve, and reject: admin and sales.
  - Finance: read-only.
  - Instant disable and resume of a branch: admin, support supervisor, operations.
  - Each staff member sees only the merchants and branches within their role scope.
- UX decisions:
  - The row's primary action changes by its status: open file, approve, or resume.
- Requirements: MER-001 MER-046 ADM-004 ADM-032
- Leads to: A06 A09
- Special states: Incomplete data: "Data completeness" is red with what is missing.; Disabled: red badge, and "Resume" instead of "Open file".; No merchants in the selected city: "No merchants in [city] yet" and "Add" and "Import" buttons.; Import with errors only: nothing is added, and the errors file is offered for download.

#### A06 — Merchant Page

A unified file containing all the settings of the merchant and its branches without scattering.

- Elements: Overview, Operations and zone: each branch's zone on a map: its city boundaries or a manual zone inside them (MER-046), and the hours, preparation time, and minimum, Products: store-price edit permission mode (MER-002) and percentage, and for each product in each branch the store price with the sale price beside it, calculated with the markup rate in the branch's contract; platform staff do not enter the sale price by hand, Contract: its type (PAY-009), value, markup rate, and effective date, any branch-specific contract percentage or markup rate, and the exempt menu link, and tax registration: registered with its VAT number or not registered (PAY-029), Offers, ads, and campaigns, Dues, Team, Support and log: platform chats with the merchant (ADM-010), the edit log with actor and values before and after, and bank account changes, a fixed header visible in all tabs: name, type and ordering method, city, number of branches, account manager, status (active, disabled), and the "Message merchant" and "Instant disable" buttons, Preferred captain (MER-038): preferred drivers with their live status (online, offline), tier, and equipment, and a field to add by driver number, Self-pickup: enabled or not, its discount, its distance for each branch, and who funds the discount (EXT-006), Shops conversion: menu readiness (number of valid products)
- Actions and what happens:
  - **Edit setting**: makes the current tab's fields editable. "Save" shows a before/after difference summary and asks for confirmation; it applies to new orders only and is recorded in "Support and log".
  - **Shops conversion**: a window that checks menu readiness; with no valid products the button stays disabled "Cannot publish: 0 valid products". The confirmation "Convert to a menu for new orders" (MER-053).
  - **Menu permissions**: window: choose the mode, and the percentage for "Within a percentage" (MER-002).
  - **Percentage**: window: contract type (a percentage agreed with the merchant, or a fee per new customer at each branch), its value, the markup rate by which the sale price is calculated from the store price, and effective date, with an optional per-branch customization of the percentage or markup rate while the merchant's contract stays for the other branches. The confirmation gives an example: "Selling price 110 and percentage 10% = 11 to the platform" (PAY-009). No confirmed order changes.
  - **Branch zone**: for each branch: choose "City boundaries" or "Manual zone" and draw on the map; anything outside the branch's city boundaries is clipped while drawing (DSP-002). Saving applies it to new orders, offers, and campaigns (MER-046); a customer outside the branch's city cannot order from it.
  - **Link**: creates an exempt menu link and copies it, and it can be stopped. What is deducted from its orders (PAY-009).
  - **Add preferred captain**: the number of an approved driver in the branch's city; added to the list, and the branch's order is offered to them first as a task offer for 30 seconds (MER-038).
  - **Remove**: removes the driver from the preferred list with a simple confirmation; applies to new orders.
  - **Message merchant**: opens a chat with the merchant linked to the merchant or the branch (or to an order if one is chosen), appearing in their dashboard and app.
  - **Instant disable**: the branch, a written reason, and the confirmation "[Branch] will not receive any new orders; ongoing orders complete"; takes effect immediately and the button becomes "Resume".
  - **Enable self-pickup**: a switch in "Ordering and pickup method"; disabled for Mart with the hint "Mart has no self-pickup".
- Validation and error messages:
  - Preferred captain: number not found → "No driver with this number"; from another city → "The driver is not in [branch city]"; not approved → "The driver is not approved".
  - A manual zone is a closed polygon → "Close the boundary before saving".
  - Percentages between 0 and 100 → "The percentage is between 0 and 100".
  - The effective date cannot be in the past.
  - Registered for VAT without a 15-digit number → "Enter the VAT number (15 digits)".
- Permissions:
  - Contract, percentage, link, conversion, and menu permissions: admin and sales; finance read-only.
  - Branch zone: admin; preferred captain: admin, operations; instant branch disable: admin, support supervisor, operations.
  - Message merchant: admin, support supervisor, support agent, sales.
  - A staff member sees only the merchants and branches within their role scope.
- UX decisions:
  - Settings not available for the merchant type remain visible but disabled with a hint giving the reason.
- Requirements: MER-046 MER-053 MER-002 PAY-009 MER-038 ADM-004 ADM-010 MER-001 EXT-006
- Leads to: A05 A07 A08 A10
- Special states: Mart merchant: ordering method "Catalog" and self-pickup is disabled.; Write-in Shops: "Shops conversion" is active; otherwise disabled with the hint "Available for Shops merchants only".; Offline preferred captain: badge "Offline · does not delay the order".; Disabled: a red bar at the top of the page with the branch, reason, actor, and time.; Edit with an upcoming effective date: badge "Scheduled from [date]" next to the value.

#### A07 — Mart Catalogs

Primary, secondary, and public, and merchant product review.

- Elements: Catalogs: for each catalog its type (primary: common grocery products, secondary: specialized categories, general: merchant suggestions after approval), its status and the number of groceries subscribed to it; the catalog is for Mart only, Central products: search by name or barcode and a catalog and status filter, Reference store prices: with a "Selling price + the branch's set markup rate" column next to them, Catalog subscriptions: for each grocery its catalogs, and the status of the "Auto-enable additions" option (off by default), Local customization: a column with the number of groceries that edited the price, availability, or image, and it opens their detail, Products for review: beside the table, for each product the image, the sending grocery, the proposed store price, the request age, and approve and reject buttons in the row, Tabs: central products, products for review (with count), catalog subscriptions, import log, Import log: result of the last Excel check: valid, errors, Bulk selection for central suspension
- Actions and what happens:
  - **Add**: window: a new catalog (primary, secondary, public) or a central product (name, category, reference store price, image, catalog). The product enters the subscribed grocery stores disabled, except for those that turned on "Enable additions automatically" (MER-010).
  - **Excel and check**: upload the file, then a report: new rows, update rows, errors with row number. "Apply [count] rows" after confirmation. It does not touch a modified local price (MER-010).
  - **Central stop**: a red confirmation stating the impact and number of grocery stores: "[Product] will disappear from [count] grocery stores and new purchase of it is blocked; confirmed orders keep their copy". Takes effect immediately (CAT-001).
  - **Approve product**: adds it to the public catalog so it stays enabled in the submitting grocery store, and enters the grocery stores subscribed to the public one disabled unless the "Enable additions automatically" option is on (MER-010), and the merchant receives a notification. A transient message with an "Undo" button for a few seconds.
  - **Reject with reason**: a written or selected reason reaches the merchant; the product stays a draft (MER-010).
  - **Central reactivation**: for a centrally stopped product: confirmation, then it returns to where it was locally enabled.
  - **Open customization details**: a list of the grocery stores that customized the product: local price, availability, and image for each store; view only.
- Validation and error messages:
  - Store price greater than zero → "Write a valid price".
  - File errors: "Row [number]: store price is empty", "Row [number]: catalog not found", "Row [number]: duplicate product".
  - Rejection reason is mandatory.
- Permissions:
  - Catalog management, central stop, and product approval: admin and sales by default (catalogs, price review, and enabling the link), and the admin grants them to any role from the role editor.
  - Other roles: read-only if granted.
- Requirements: MER-010 CAT-001
- Leads to: A06 A08
- Special states: Centrally stopped: red badge, and the customization column shows the affected grocery stores.; No products for review: "No products awaiting review".; Import in progress: a progress bar, and the list remains usable.; Cancelling a grocery store's catalog subscription: its products disappear from it and their sales history remains (CAT-001).

#### A08 — Merchant Reviews

Only the required review according to permission and request type.

- Elements: Before and after: in two colors, with the sale price in both cases, the reason for the request, Sale price: for a store-price edit the approved price and the percentage change from it are shown, the merchant's permission mode and price limits, the store price and sale price, and what the customer sees until the decision (MER-002), Merchant offers: offer terms, and the merchant funds it in full (MKT-007), Ads: placement, city, duration, price, and remaining capacity (MKT-003), New product: a review type opened in A07, Review-type chips with their counters: prices, merchant offers, ads, new products; and the city filter and sort (oldest first by default), the age of each request in the list, Rejection reason with ready templates and free text, Decision log: reviewer, time, and reason
- Actions and what happens:
  - **Approve**: the button states the result by type: price "Sale price becomes [price]" takes effect on new orders immediately; a merchant offer is published with its terms; an ad is published, its amount is deducted, and the ad invoice is issued (MKT-003). The merchant is notified, the decision is recorded, and the list moves to the next item.
  - **Reject with reason**: the reason is mandatory (template or text); the previous approved price stays and nothing is deducted (MER-002, MKT-003), and the merchant receives the reason. Moves to the next item.
  - **Open merchant page**: opens the merchant page (A06) on the related tab (products, or offers, ads, and campaigns).
  - **Open new product**: opens the review in Mart catalogs (A07).
- Validation and error messages:
  - Rejecting without a reason → "Choose a reason or write one".
  - A merchant offer is funded in full by the merchant; if platform participation in its funding is requested → it is not approved as is, and the platform creates it as a platform offer on its behalf (A14, MKT-007).
- Permissions:
  - Merchant offers and ads: admin and sales.
  - Price edits: admin and sales by default (catalogs, price review, and enabling the link).
  - Only the required reviews according to the staff member's permission and request type are shown.
- UX decisions:
  - The list is on the right and the details on the left, and the decision does not require going back to the list.
- Requirements: MER-002 MKT-007 MKT-003
- Leads to: A06 A07 A16
- Special states: Merchant withdrew their request before the decision: the item is gray "Withdrawn by merchant" with no buttons.; Placement capacity filled before approval: "Approve" is disabled with the hint "No capacity in this placement for the requested duration".; Two requests on the same product: only the latest appears with the note "Replaces an earlier request".; Nothing to review: "No requests awaiting review".

#### A09 — Cities and Zones

Boundaries, coverage, fees, and exceptions.

- Elements: Boundaries: city boundaries on the map (the city zone, which is the default zone for its branches, and no branch zone exceeds it), with the drivers' private zones (DSP-002) and out-of-boundary coverage requests, Sections: those enabled in the city, Stores and drivers: city page numbers (ADM-032): stores (by section), drivers (and those online now), active customers, delivered orders; each number opens its list filtered by the city, Delivery fees (PAY-013): base fee and its kilometers, extra kilometer price, minimum and maximum, restaurants and Shops fee and Mart and pharmacies fee, distance measurement method (air or road distance) and road factor, effective date, and rule priority: branch, then city, then region, then global, Driver percentage: in the "Fees and driver percentage" tab, Stacking: a per-city setting, Coverage requests: on the map outside the boundaries and in the readiness indicator, Cities list beside the city page: name, region, status (open, candidate, disabled), readiness for a candidate (X/6 with a bar), and whether it has a specific setting, City tabs: overview and boundaries, fees and driver percentage, distribution and driver cap, seasons, readiness and launch, Source of each setting: "Follows global", "Follows region" or "City-specific" with an "Exception" badge and a revert button, a "Global setting / [Region] / [City]" switch in the header showing which level is being edited; and the order: branch, then city, then region, then global (ADM-034), Distribution settings (DSP-001) with the global value and the city value: task-offer radius at start, increment, maximum, who they are offered to, acceptance duration, interval, preferred captain, support alert, search timeout, new-driver score, prioritizing those who stayed online an hour without an order (within the task-offer radius only); and priority-index weights with a live calculation preview using the three examples that updates as the weights change, Driver cap and waiting-list count (DSP-004); empty = no cap, Seasons (ADM-015): name, cities, from and to, and what is linked to it, Readiness and launch (ADM-037): candidate city indicator, checklist, and the number of those who registered interest, an "Instant disable" button for the city and an active-season badge
- Actions and what happens:
  - **Draw boundaries**: placing a drawing on the map with polygon points. "Save boundaries" shows the impact before confirming "[count] branches without a manual zone will take the new boundaries · [count] customer addresses became outside the city zone". Applies to new orders.
  - **Pricing**: window: "Follows the region setting" (or "Follows the global setting" for a region) or "Specific setting" with the PAY-013 fields, including the measurement method: air or road distance, and an effective date, with a fee preview for an example distance using the chosen method. A region has the same window, and its cities inherit it.
  - **City setting**: opens the settings tab (distribution, driver percentage, stacking, cap, enabled sections); each item is "Follows global" or a specific value with an "Exception" badge. "Save [city] settings" applies to orders whose distribution starts after it, and records the editor and the values before and after.
  - **Open city**: for a candidate city: shows the checklist and the button is disabled until it is complete (ADM-037). The confirmation states the impact "[City] will be opened for ordering and [count] registered users will receive a notification with the launch coupon". It becomes "Open" and the notification is sent once.
  - **Global setting**: switches the editor to the global setting (distribution, fees, and cap). The save confirmation states the number of cities that follow global and will be affected.
  - **Exception / Customize**: converts an item from "Follows global" to a city-specific value with an "Exception" badge.
  - **Revert to global**: deletes the city's value for the item so it follows global again; a simple confirmation states the value that will apply.
  - **Instant disable**: a written reason and the confirmation "Customers in [city] will not be able to order until resumed". Takes effect immediately, ongoing orders complete, the city appears "Disabled" in the list, and the button becomes "Resume".
  - **Add season**: window with the season fields (ADM-015).
  - **Private driver zone**: choose a driver and draw a zone inside the city (DSP-002). Removed with a "Remove zone" button.
  - **Open list**: the city page numbers and coverage requests open their lists filtered by the city (ADM-032): merchants A05, drivers A10, customers A13.
  - **Add candidate city**: name and region (country → region → city); created as "candidate" with readiness 0/6.
- Validation and error messages:
  - Boundaries: unclosed or self-intersecting polygon → "Close the boundary without intersections".
  - Fees: minimum greater than maximum → "The minimum must not exceed the maximum"; negative value → "The value cannot be negative"; past effective date → "Choose a date from today onward".
  - Distribution: starting radius greater than maximum → "The task-offer radius at start must not exceed the maximum"; weights do not equal 100 → "The weights total [total]; it must be 100".
  - The cap is a positive integer or empty.
  - Season: end before start → "The end date must be after the start".
- Permissions:
  - City page and its numbers: all roles within their cities (view).
  - Drawing boundaries, pricing, settings, global setting, seasons, opening a city, and disabling it instantly: admin.
- Requirements: DSP-002 PAY-013 ADM-037 ADM-032 DSP-001 DSP-004 ADM-015 ADM-004
- Leads to: A05 A10 A11 A13 A14
- Special states: City fully following global: all items "Follows global" with no exception badge.; Scheduled fee rule: badge "Scheduled from [date]" with the current value beside it.; Candidate city: the default tab is "Readiness and launch".; Disabled city: a red bar with the reason, actor, time, and a "Resume" button.; Active season: a badge in the city header, and values changed by the season carry the season icon.; Driver cap reached: "Waiting list now: [count]" in a warning color.

#### A10 — Drivers

Accounts, activation, restrictions, and equipment.

- Elements: Account: status chips with counters: awaiting approval, active, stopped from tasks (PAY-026), suspended for review, disabled for a reason, banned, Vehicle: driver type and vehicle under the name (DRV-001), City and zone: city boundaries or private zone (DSP-002), Performance: link to A11, Bank and deposit: dues account and deposit are two columns and two separate cards (PAY-024, PAY-026): dues account balance is yellow near the balance lockout threshold (−50) and red at it, and the deposit is held or "Not paid" with a dotted frame and a lock, Equipment: thermal bag, cooler bag, uniform (DRV-013), Ban and exclusion: the ban with its duration or permanent, the branches and customers they are excluded from, and the current penalty-ladder step (DRV-023), Payouts: link, search by name, ID, or mobile, and a filter for type and equipment, selected driver panel beside the table: restriction status bar (disabling, ban, or balance lockout) and its reason with a sentence explaining when it returns, the dues account and deposit cards, and the latest dues account movements, documents and their expiry dates (reminder only), spoofing detection (DRV-027): type, time, evidence
- Actions and what happens:
  - **Approve**: a checklist window (DRV-001) and the deposit is paid. The button is disabled if the deposit has not been paid, with the hint "Deposit not paid". Confirming activates the account, notifies the driver, and records the approver.
  - **Disable with reason**: window: a mandatory reason and the duration (until manual lift or until a date). Confirmation "[Driver] will not receive new tasks". Takes effect immediately, the driver receives a notification with the reason, and "Disabled for a reason" and a "Lift disabling" button appear (PAY-026).
  - **Ban or exclusion**: window: the type: ban (24 hours, until a date, or permanent) or exclusion from a specific branch or a specific customer, and a reason. A red confirmation states the impact. Exclusion removes them only from the branch's or the customer's task offers; a ban prevents entering tasks for its duration, and closing the account goes through support (DRV-001). All penalty-ladder steps are manual (DRV-023).
  - **Edit city**: the new city and a reason; confirmation "[Driver] will receive only [city] orders, and their private zone is canceled". Applies to new task offers and is recorded.
  - **Lift disabling**: a written reason; they resume receiving tasks immediately unless stopped due to balance (PAY-026) or suspended for review.
  - **Review spoofing detection**: an evidence window (route, jumps, device type) and two options with a mandatory note: "Lift suspension" (false detection) or "Permanent ban" for proven spoofing (DRV-027, DRV-023).
  - **Edit equipment**: the three equipment switches; the change is recorded and applies to dispatch immediately (DRV-013).
  - **Set private zone**: draw a zone inside the city (DSP-002).
  - **Message**: opens a chat with the driver linked to their account or to an order the staff member chooses (ADM-010).
  - **Performance**: opens the "Driver file" tab in A11.
  - **Close account**: through support: a settlement window showing the dues account balance and deposit (PAY-024, PAY-026). The button "Close the account and refund [amount] SAR" does not work before settlement. The account becomes "Closed" and the final payout is sent for payout approval.
- Validation and error messages:
  - A written reason is mandatory for disabling, ban, exclusion, city edit, and lifting the disabling.
  - City edit during an ongoing task → "The driver has an ongoing task; the change takes effect after it ends".
  - Disabling or ban end in the past → "Choose a later date".
  - Closing the account with an ongoing task or pending payout → "End the ongoing task and the pending payout first".
- Permissions:
  - Approve, disable, ban, exclude, city edit, equipment, and spoofing review: admin, support supervisor, operations (within their cities).
  - Dues account and deposit: everyone sees the status; movement details for admin, finance, and support.
  - Closing and settling the account: admin, support supervisor, support agent; the final payout is approved by whoever holds payout approval (admin, finance).
  - Messaging: admin, support supervisor, support agent, operations.
- Requirements: DRV-001 DRV-013 PAY-024 PAY-026 DRV-027 ADM-010 DSP-002
- Leads to: A11 A04 A18 A09
- Special states: Near the balance lockout threshold: active with a yellow "Near limit" badge.; At the balance lockout threshold (PAY-026): red "Stopped".; Deposit not paid: "Not paid" in the deposit column.; Suspended for review (spoofing): "Suspended" and a "Review spoofing detection" button (DRV-027).; Expired or soon-to-expire document: a "Reminder only" badge and no stop.; Closed account: read-only with the closing date and settlement amount.

#### A11 — Driver Performance and Incentives

Indicators, tiers, filters, and incentives.

- Elements: Period and custom: performance filters (DRV-017), and "Last 30 days" is tagged "Tier score", 30-day score: performance table with indicator columns and each indicator's weight in its column header (DRV-017); "—" for an indicator without data, Indicator details: driver analytics (ADM-009), Tiers: with their names and default thresholds in the chart (DRV-015), and beside them review alerts (ADM-009), each alert with a "Review" button and the phrase "No automatic deduction or sanction", Incentives: tab, for each incentive the type (DRV-006 types or instant), city, days, hours, tiers, incentive amount, budget, end, cost, extra orders, and status, Budget: in the incentives card with the amount spent and its percentage and the extra orders it brought, Percentage: ranking of the driver platform percentage (city, then region, then tier benefits, then global) in the incentives card, The four tabs (ADM-035), a "Daily update" stamp and the last update time, Targeted instant incentive window (second preview): ADM-044 fields and the count of matches, System settings tab: score weights and conversion of indicator to points (DRV-017), tier thresholds and benefits per city and period (DRV-015), report alert percentage (ADM-009), and dispatch priority-index weights (DSP-001), Driver file tab: their score and pinned tier, indicator details, previous reviews and penalty-ladder steps, incentives they received
- Actions and what happens:
  - **Settings**: opens "System settings". Saving shows the confirmation "Scores will be recalculated in the next daily update; the benefit pinned on accepted tasks does not change". The editor and the values before and after are recorded.
  - **Incentive**: a creation window: one of the four types with DRV-006 fields and a cost preview, or "Instant", which opens the targeted-incentive window. Its appearance and stopping follow DRV-006 and ADM-044.
  - **Warning**: the first step of the penalty ladder (DRV-023): a written message with its reason reaches the driver as a notification about their performance; no financial or operational impact. Recorded in their file.
  - **Review**: opens a review: the relevant reports, orders, and ratings. The decision: close with no action, or the next step of the penalty ladder (warning, then lowered priority for a week, then a 24-hour ban, then operations review, then a permanent ban; fraud goes directly to a permanent ban), or refer for a loss charge or penalty (A04), with a mandatory note (ADM-009, DRV-023). The driver moves a step only by a staff decision.
  - **Launch the incentive**: a confirmation stating the count and the limit "Launch the incentive for [count] drivers · limit [amount] SAR". It appears immediately for those in the group and stops at its limit or end of its duration (ADM-044).
  - **Save group with its conditions**: saves the group under a name platform staff type so it appears in "Saved group"; its members are computed from the conditions at each use.
  - **Stop incentive**: a confirmation stating that the incentive disappears from drivers immediately, and what was earned before the stop is paid out.
  - **Copy incentive**: creates a copy for another city or another month without affecting the original.
  - **Performance filters**: change the displayed numbers only; the tier score does not change (DRV-017).
- Validation and error messages:
  - Score weights do not equal 100 → "The weights total [total]; it must be 100".
  - Tier thresholds overlap or have a gap → "Tier thresholds must connect without overlap".
  - Incentive: budget or cap is zero → "Write a limit greater than zero"; end before start → "The end date must be after the start"; amount greater than the cap → "The amount must not exceed the cap".
  - The review decision note is mandatory.
- Permissions:
  - Performance and driver file: admin, support supervisor, operations (within their cities).
  - Warning and review: admin, support supervisor, operations.
  - Incentives and system settings: admin; finance sees the budget and cost.
  - Launching the instant incentive: admin, operations (preferred captain and instant incentive).
- Requirements: DRV-017 DRV-006 DRV-015 ADM-035 ADM-044 ADM-009 DSP-001
- Leads to: A10 A04 A09
- Special states: New driver: tier "New" and no score appears for them in the table (DRV-015, DSP-001).; Indicator without data: "—" (DRV-017).; Driver at the "Lowered priority" step: a badge with its end date (one week) in the table and their file, and their priority index is computed lowered until it ends (DRV-023).; Incentive reached its budget: gray "Stopped: budget reached".; Incentive whose date ended: "Ended".; Group with no matches: "No one matches now" and the launch button is disabled.; Filter other than "Last 30 days": a bar "For display only · the tier does not change".

#### A12 — Delivery Companies

Company drivers, their cities, performance, and dues.

- Elements: Company, Cities: the cities allowed for the company, and a part of a city added or excluded (FLT-001), Drivers, Shifts, Percentage (FLT-002), Statement, a "Later section" bar at the top of the page, and an empty state at launch explaining what will happen upon contracting, The illustrative table is titled "Illustrative data" to separate it from the actual state
- Actions and what happens:
  - **Add**: disabled at launch. Later: creates a company with its contract, percentage, and cities, and it appears in the list as "Awaiting activation".
  - **Cities and zone**: Later: sets the allowed cities and draws or excludes a part of a city (FLT-001).
  - **Statement**: Later: opens the company's live statement; payout to them is through manual approval in A18 (FLT-002).
- Permissions:
  - At build: the admin creates and sets the cities and zone; approving a company payout is for whoever holds "payout approval" (admin, finance).
- Requirements: FLT-001 FLT-002
- Leads to: A18
- Special states: At launch: no companies, the empty state is visible, and "Add" is disabled.

#### A13 — Customers and Segments

Retention, targeting, and the customer file.

- Elements: Tabs: customers, ban and exclusion lists, Segments: ready-made: all, new, repeat, idle (by the idle period, 30 days by default), high spenders, exceeded the trust limit (SUP-007), Segment summary: customer count, average spend, median last order, percentage with notifications enabled, Customers table: city, orders, spend, last order, rating, refund rate; and sorting by last order, orders, spend, rating, and city, Customer file: status, registration date, address (by permission), refund rate and a trust-limit-exceeded badge, tickets and their satisfaction, notifications, bans and exclusions on them (drivers excluded from their orders), Wallet: credit types and expiry date of each type, and the pending reward and its 24-hour claim window (PAY-002), and freeze status: "Awaiting second approval" then "Frozen" with the requester and approver names, Ban and exclusion lists: banning customers, merchants, and drivers, and excluding a driver from a branch or from a customer; for each restriction: the party, type, reason, duration (until a date or permanent), actor, date
- Actions and what happens:
  - **Coupon**: opens coupon creation (A14) restricted to the customer or segment, with an eligibility preview before saving
  - **Notification**: opens a scheduled notification (A17) with the customer or segment as audience, with the audience count and template preview before sending; it respects the frequency limit
  - **Compensation**: window: amount, reason, linked order if any; after confirmation the compensation arrives as a reward the customer claims within 24 hours, otherwise it lapses with a reversal entry (PAY-002), and it is recorded. Above the role limit it is raised to a higher role (ADM-043)
  - **Ban with reason**: window: reason, duration (until a date or permanent), note; a confirmation states that the customer will not be able to order, then the account is banned and appears in the ban and exclusion lists and is recorded
  - **Repeat-order credit**: an amount and reason window; added as promotional credit directly, without a reward awaiting claim (MKT-002)
  - **Exclude driver from a customer**: choose a driver, the reason, and the duration (ADM-013)
  - **Exclude driver from a branch**: from the ban and exclusion lists: choose a driver, a branch, the reason, and the duration (ADM-013)
  - **Freeze wallet**: asks for a reason then is sent to a second staff member for approval (ADM-013); it is not frozen before that. Unfreezing uses the same dual approval, and the requester and approver are recorded
  - **Lift ban**: lifts the ban or exclusion from their lists, with a reason, and recorded
  - **Send to segment**: moves the current segment with its filters and count to A17 as the audience for a new notification
- Validation and error messages:
  - Ban and exclusion: reason and duration are mandatory "Choose the duration or "Permanent""; lifting a ban: the reason is mandatory
  - Freezing the wallet: the approver is not the requester "Another staff member approves"
  - Compensation and repeat-order credit: an amount greater than zero and a mandatory reason
- Permissions:
  - View customers: support and operations roles within their cities; the address for whoever holds the customer address permission (ADM-001)
  - Compensation, repeat-order credit, banning customers, and the second approval on freezing: (ADM-043)
  - Coupon and marketing notification: admin, sales
  - Excluding a driver from a branch or customer: the "Drivers: approve, disable, and ban" permission (admin, support supervisor, operations)
- UX decisions:
  - Restrictive actions (ban, exclusion, freeze) are separated by a line and in red from the retention actions
  - The wallet is detailed by its types because support is asked about it often
- Requirements: ADM-008 ADM-013 MKT-002 SUP-007 ADM-002 PAY-002 ADM-043
- Leads to: A14 A17 A19 A26
- Special states: Address hidden: a lock and the text "Visible to those with permission" appear instead (ADM-008); Awaiting freeze approval: badge "Awaiting second approval" and the requester's name; Frozen wallet: the balance is visible with a red badge and cannot be spent; Customer exceeded the trust limit (SUP-007): red badge and the refund rate on their reports; Ban expired: moves automatically to "Expired" in the ban and exclusion lists

#### A14 — Offers and Coupons

Cities and branches, a funding share, a budget, and a stacking rule.

- Elements: Tabs: all, platform offers, merchant offers (with a badge of the count awaiting review), coupons, Hour Deals, Budget or stock: a "Used / Total" column, and an "Budget nearly exhausted" badge, Platform offer fields (MKT-007): cities and branches, products, duration, stock, minimum order, budget, funding share as a percentage or amount per party, stacking (a delivery offer with one discount offer on products), Coupon fields (MKT-001): cities and branches, categories, customers or customer segment relative to the branch (new, repeat, idle), period, usage limit, budget, funding per party, stacking, Offer subscriptions: each branch's subscription to a platform offer, and the merchant's share is fixed when it subscribes; raising it pauses its subscription until the merchant agrees, and lowering it takes effect immediately (MKT-007), restricting the coupon to an issuing bank: choosing the bank and the funder (MKT-001), "First order" line: a fixed line in the form showing the rule (MKT-001), Stacking setting with wallet credit: read-only under the stacking field (MKT-001), Hour table (Hour Deal): product, discount, stock, schedule (once or recurring days, start and end hour), and the unified counter until the end of the period (MKT-017), Eligibility preview: inside the form before saving: the number of eligible customers and stores, and the excluded and their reasons (outside the branch zone, not idle, device previously used), Merchant offers awaiting review (funded in full by the merchant): a list with approve and reject buttons
- Actions and what happens:
  - **Create**: validates the fields then saves: "Scheduled" if its date is upcoming, otherwise "Active" immediately; a platform offer without review when the branch subscribes (MKT-007). Recorded in the audit log
  - **Extend**: a new end date field, and optionally increasing the budget or stock; after confirmation the offer continues without interruption
  - **Stop**: a confirmation stating the number of ongoing orders with the offer and that they keep their discount; then it becomes "Stopped" and is not applied to new orders
  - **Eligibility preview**: computes with the current conditions without saving and shows the result in the form
  - **Approve merchant offer**: publishes the offer immediately or on its date, and the merchant receives a notification
  - **Reject merchant offer**: asks for a reason that reaches the merchant (MKT-007), and the offer stays unpublished
  - **Create on behalf of a merchant**: from "Merchant offers": creates a platform offer on behalf of the merchant when the platform participates in its funding (MKT-007), and the actor is recorded
- Validation and error messages:
  - Funding share: "Total [N]%; it must not exceed the offer cost (100%)" under the field with the actual total, and the create button is disabled until corrected (MKT-007)
  - Hour Deal discount: "The minimum Hour Deal discount is 30%" (MKT-017)
  - End date after start, and budget greater than zero
  - Merchant offer rejection: the reason is mandatory
  - Cities or branches outside the staff member's role scope cannot be chosen
- Permissions:
  - Creating, extending, and stopping offers and coupons and reviewing merchant offers: admin, sales
  - The other roles do not see the page; support sees the coupon's effect in the order file
- Requirements: MKT-001 MKT-007 MKT-017 MKT-005 PAY-002
- Leads to: A13 A21 A18
- Special states: Budget exhausted: the offer stops automatically with the status "Budget ended" (MKT-001); Hour Deal whose stock ran out or whose period ended: (MKT-017); Merchant offer "Under review": does not appear to customers; Offer outside the branch zone: does not appear (MKT-007), and the preview lists the excluded branches; raising the merchant's share in an existing offer: its branches' subscription is "Paused until approval", and nothing is deducted at the new share before it (MKT-007)

#### A15 — Loyalty and Referral

OpenLoyalty rules, referral prizes, and cost measurement.

- Elements: Tabs: points, referral, sync, Summary: points granted, pending, redeemed, points liability in SAR (link to liabilities in A18), completed invites, pending referral prizes in SAR, Rules: for each rule: city and period, points value, the funder (the platform, or the merchant for boosted points they buy), cap, redemption and expiry (MKT-010), status, Points basis card: short sentences under the rules table explaining the basis, the hold, and the withdrawal (MKT-010), and rounding down, Referral: the referral prize for each city, its period, type (promotional credit, coupon, or free delivery; by default 15 SAR promotional credit for each party), and cost (MKT-013), Invites: a count funnel: awaiting first order, pending, withdrawn, rejected for first-order abuse, Sync: OpenLoyalty status and last sync, and events not sent, Links: Adjust links awaiting matching, "Add with reason" window: customer, points or credit, reason, funder
- Actions and what happens:
  - **Edit**: opens the rule for editing (value, limit, expiry, cap, city, period); saving creates a version that applies to new events only, and is recorded
  - **Stop**: a confirmation stating that granted points remain and the rule no longer grants; it becomes "Stopped"
  - **Add with reason**: adds points or credit to the customer; recorded with the actor and appears in liabilities (PAY-031)
  - **Review sync**: shows unsent events with their identifiers; "Resend" sends them again without duplicating the points or prize (MKT-010)
- Validation and error messages:
  - "Add with reason": the reason is mandatory, and points greater than zero
  - Cap and expiry are positive numbers, and the start of the rule's period is before its end
- Permissions:
  - Rules, referral, and stopping them: admin, sales (offers, ads, and campaigns)
  - "Add with reason": points for admin (add points to a customer), and credit for whoever holds compensation and credit (admin, support supervisor, support agent)
  - Sync review: admin
- UX decisions:
  - Points liability in SAR is in the summary because the program's cost is the platform's first question
- Requirements: MKT-010 MKT-013 PAY-031 PAY-027 PAY-002
- Leads to: A18 A13 A22
- Special states: OpenLoyalty down: badge "Down · orders work", and events are saved for re-sync (MKT-010); sync errors state explicitly that orders were not affected; Pending points: shown to the customer as "Pending" (MKT-010); Referral prize withdrawn by an order refund: appears in the count and has an entry (MKT-013); Boosted-points rule funded by a merchant: badge "Funded by merchant"

#### A16 — Ads and Placements

Banners and pinning per city with price and capacity.

- Elements: Placements: cards: name, location in the app, city, price per day, capacity used out of total, stop policy at the merchant's request, Ads table: merchant and city, placement, duration, total amount (price × days), status (awaiting approval, active, ended, rejected with reason, disabled or stopped), Results: for each ad: impressions, clicks, orders, new customers, amount deducted and the ad invoice number; matching the merchant's statement and spend page (MKT-015), Pricing window: placement, city, price per day, capacity, stop policy at the merchant's request, fixed text: deduction, disabling, and stop rules (MKT-003) so that nothing is approved without understanding its impact
- Actions and what happens:
  - **Pricing**: saves a placement's price, capacity, and stop policy for a city; applies to new ads only (MKT-003)
  - **Approve**: a confirmation stating the amount that will be deducted from the merchant's dues with its 15% tax; after it the ad is published on schedule, the ad invoice is issued, and the deduction is recorded in their statement with its number (MKT-003), and the merchant receives a notification
  - **Reject**: asks for a reason that reaches the merchant; no deduction and no publishing (MKT-008)
  - **Stop**: asks for the reason: "Disabling for a platform reason", which refunds the unexecuted part, or "Stop at the merchant's request" per the placement policy (MKT-003); and shows the refunded amount and its credit note before confirming
- Validation and error messages:
  - Price and capacity are positive numbers
  - Rejection and stop: the reason is mandatory
  - No approval for an ad that exceeds the placement capacity in the period: "Capacity is full in [period]"
- Permissions:
  - Pricing, approval, rejection, and stopping: admin, sales
  - Finance sees the deduction's effect in the merchant's statement (A18)
- UX decisions:
  - The ad awaiting approval is the first row, with its buttons inside the row
  - Results are beside the queue to see placement performance before approving a new ad
- Requirements: MKT-003 MKT-015 MKT-008 PAY-022
- Leads to: A18 A06
- Special states: Capacity full in the period: the placement has a "Full" badge; Rejected ad: the reason is visible in the table and to the merchant; Disabled or stopped ad: the refunded amount, if any, is visible beside it

#### A17 — Notifications

Order templates, scheduling, and targeting via OneSignal.

- Elements: Tabs: order events, scheduled notifications, automatic messages, merchant campaigns, templates and languages, Event (order events): for each event: its identifier, the template in each language, channels, order link, status (INT-004), New notification: type (operational or marketing), audience (segment and INT-004 options), city, branch (restricts the audience to its zone), time in Riyadh time, template, Arabic and English templates: a side-by-side preview of each enabled language, Audience preview: adjacent to the form: the final count, and the excluded with their reasons (outside the branch zone, reached the frequency limit (ADM-007), disabled notifications), AI suggestion: a "Review suggestion" card for the text and audience (INT-004), Automatic messages: a short list of ADM-040 rules, for each rule: event, delay, template, daily limit, status; with text stating they work without AI, Merchant campaigns: frequency limits, budget, and the templates available to the merchant, and their segments (new, repeat, idle by the idle period), and their aggregate results (MKT-005), Templates and languages: each template with its key and translations; adding a language as a data row (SYS-013), Results: sent, opened, resulting orders per notification and for the period
- Actions and what happens:
  - **Schedule**: a confirmation shows the final audience count, then it is saved as "Scheduled" for its time; it can be edited or canceled before its time
  - **Send**: a confirmation "The notification will reach [count] customers now", then sending via OneSignal (ADM-007), and results appear progressively
  - **Template**: opens the template editor: text in each language, allowed variables, the link
  - **Enable event**: enables or stops an order event notification or an automatic message rule (ADM-040)
  - **Approve AI suggestion**: shows the suggested text and audience for editing; it does not enter scheduling until "Approve" (INT-004), and the approver is recorded
  - **Set merchant campaign limits**: sets the frequency limit, budget, and templates available to merchants; applies to new campaigns
- Validation and error messages:
  - Scheduling time in the future: "Choose a time after now"
  - Branch audience: anyone outside its zone is excluded automatically and the excluded count is shown (ADM-007)
  - The text of each enabled language is mandatory, and the template is not saved without it
  - The delay and daily limit of automatic messages are positive numbers
- Permissions:
  - Marketing notifications, automatic messages, and merchant campaigns: admin, sales
  - Order event templates and enabling them: admin
  - Approving AI suggestions: admin
- UX decisions:
  - The instant send button is secondary and scheduling is primary to reduce wrong sends
- Requirements: INT-004 ADM-007 ADM-040 MKT-005 SYS-013
- Leads to: A13 A22 A19
- Special states: Audience zero after exclusion: the send button is disabled "No one in the audience after exclusion"; OneSignal down: scheduled notifications wait and an alert appears; orders are not affected; AI tool down: the suggestion card is hidden (ADM-040); Template missing an enabled language: badge "Translation incomplete"

#### A18 — Accounting

Reconciliation, settlements, liabilities, and closing.

- Elements: The nine tabs (ADM-036): each tab has a number for what awaits action (open differences, accounts awaiting approval), Months status bar: the current is open, the previous awaiting closing, and the oldest closed; and the daily entry balance check result (PAY-005), "Needs your attention" first in the overview: accounts awaiting approval, failed transfers, reconciliation differences, entries not sent to Odoo, a month ready for closing; each item has a button that opens its place, Overview: collected and held (with the count of open orders), undisbursed dues (with the count of accounts), payments sent, open differences with count and amount, drivers' negative balances and those stopped from tasks (PAY-026), liabilities and those expiring this month, and held driver deposits separated from their dues accounts; each number opens its list, Collection and reconciliation: each payment operation with its status (held, collected, hold released, refunded, failed), its method, Moyasar reference, and actual fee (PAY-027), Daily reconciliation (INT-001): a line equation: collected − actual Moyasar fee = expected in bank, against what was actually deposited; the difference in red with a flag button; and the payment fee taken from merchants is a separate revenue line (PAY-027), Dues and payouts: the live statement and the dues list (PAY-006) with columns: select, account and its type, due, deductions (commission, fees, ad, loss charge, penalty), net, statement, status, bank reference, transfer date, transfer statuses: "Awaiting approval" then PAY-006 statuses, and "Failed" with the Moyasar reason, payout method in the dues list: a column showing for each account "Automatic by splitting" (merchants: weekly payout from the branch's Moyasar wallet) or "Manual approval" (delivery companies and deposit refunds) or "Automatic STC Pay"; automatic ones appear with their status and reference, with no checkbox and no approve button (PAY-006, INT-014), Bulk selection: a checkbox for each row and "Select all" in the header; and when selected, a fixed dark bar above the table: the number of accounts, their net total, and an "Approve N payouts" button (not "Confirm"), Rows that cannot be approved: shown with a disabled checkbox and a written reason: negative balance (PAY-026), or a payout prepared by the current user (ADM-002), Driver deposit refund: a row in the payouts list that goes through the same approval (PAY-024), Liabilities: the single table with its items and columns (PAY-031), and a total-reconciliation line with wallet and points balances in the ledger, Invoices: the platform invoice and customer purchase orders, and each branch's statement and monthly fees invoice with its lines (PAY-022, PAY-007), and ad invoices (MKT-003), Tax: platform fee tax separately (PAY-022), the tax included in tips (15%), and the percentage's effective date, Refunds: each refund with its type (full, partial) and source (card, wallet), and each compensation with its reward status (claimed, lapsed), its actor, reason, and liable party, and the order link and the reversal entry, Financial reports: the "Finance" reports from the reports center (net revenue by components, order profitability, collection and reconciliation, dues and payouts, liabilities, refunds, expected balance) with the same filters, Closing and controls: each month's status and who closed it and when, a link to the financial audit log (A26), and the roles' financial limits for reading (edited in A22), Entries: a table of the latest entries: entry number, time, description, debit, credit, reference; and the reversal entry with a "Reversal" badge and a link to its original instead of editing the row, Odoo: last successful send, the count of entries waiting, and a resend button
- Actions and what happens:
  - **Approve payouts individually or in bulk**: "Approve" on the row for one account, or the "Approve N payouts" bar for the selection. Both open a confirmation: each account with its masked IBAN and amount, the total, that sending via Moyasar cannot be stopped after approval, and the excluded rows and their reason. After approval (PAY-006) rows become "In progress" then "Sent" with the bank reference or "Failed" with the reason, and a message "N payouts sent for execution" appears
  - **Retry failed**: on a "Failed" payout: a confirmation shows the Moyasar or STC Pay reason and the current account details (the new IBAN if edited). It resends the payout with the same amount without a new approval, unless the IBAN changed, in which case it needs a new approval
  - **Reversal entry**: window: the original entry read-only, the amount, the reason. After confirmation the entry is created in the open month linked to its original (PAY-005), and appears in the audit log (ADM-002). If the original is in a closed month the window states that the correction will be recorded in the open month
  - **Close**: for a month "awaiting closing": a confirmation shows the month summary (total entries, open differences, incomplete transfers) and asks to type the month's name because it cannot be reversed. After it the month becomes "Closed" with the actor's name and time (ADM-036)
  - **Export**: exports the current tab with the same period and filters to Excel or PDF with numbers matching the screen, and is recorded in the audit log
  - **Open a number to its list**: clicking a number in the overview opens the relevant tab filtered by what it was computed from
  - **Open dues account statement**: a side panel with the live statement of the branch or driver (PAY-006) with loss charges and penalties each on its own line, the previous carried-forward balance, and the net; and an "Approve" button if the account is due
  - **Select all / Clear selection**: "Select all" selects only the approvable rows in the filtered page; "Clear selection" hides the bulk bar
  - **Flag a difference**: in daily reconciliation: a note and classification of the difference (late deposit, different fee, missing operation); the difference stays "Open" until resolved by an entry, and the flag is recorded with the staff member's name
  - **Retry failed payment operation**: for a collection or hold-release operation that failed at Moyasar: resubmits the same request with its identifier to prevent duplication, and the status updates when Moyasar responds
  - **Resend entries**: sends the waiting entries to Odoo in order and shows how many succeeded and failed
  - **Issue fees invoice**: for each branch after month end: a preview of the lines (including loss charges and penalties, excluding ad fees), tax, and total; after confirmation it is issued and appears in the branch's statement and cannot be edited; correction (PAY-007)
  - **Open order**: from the refunds tab opens the order file in A03
- Validation and error messages:
  - The approve button in the window is disabled until "I reviewed each account's statement" is checked
  - A row with a negative or zero balance cannot be selected, nor a payout prepared by the same user; the reason appears on hovering the checkbox
  - An account's due changed after it was selected (new order, loss charge, or penalty): "[Account]'s amount changed from [old] to [new]; review before approving", and the new one is approved after confirming it
  - Reversal entry: the reason is mandatory, and the amount is greater than zero and does not exceed the original: "The amount is greater than the original entry ([amount])"
  - Closing: the button is disabled until the month's name is typed exactly
  - Flagging a difference: the note is mandatory
- Permissions:
  - The page, approving payouts, and financial reports: admin and finance, and the support supervisor has the reversing entry only; whoever lacks approval sees the list without checkboxes or approve buttons
  - The creator of a manual payout (driver deposit refund, early withdrawal) does not approve it even if admin (ADM-002)
  - Reversal entry: the "Reverse a financial decision with a reversal entry" permission (admin, support supervisor, finance)
  - Closing: the closing permission holder (finance by default) and admin
  - No direct edit of any party's balance (PAY-005)
- Requirements: PAY-005 PAY-006 PAY-031 INT-014 TRN-001 ADM-036 PAY-022 PAY-027 PAY-029 INT-001 INT-010 PAY-024 ADM-002 PAY-018 PAY-026 PAY-007 PAY-003 FLT-002
- Leads to: A03 A26 A22 A21 A10
- Special states: Closed month: its entries are read-only (ADM-036); Open reconciliation difference: a red row in daily reconciliation and a number on the collection and reconciliation tab until resolved; Daily balance check failed (PAY-005): a red alert at the top of the page with the date and difference; Odoo down: a yellow bar "Entries are saved in the ledger and waiting to be sent (N)", and orders and payouts work; Failed payout: stays "Failed" and is not counted in payments sent (PAY-006); Bulk approval partially succeeded: a message "N sent and M failed", and the failed are visible with a "Retry failed" button; Account with a negative balance: it is not paid (PAY-026); and the driver in balance lockout has a "Stopped from tasks" badge; Payout prepared by the current user: its checkbox is disabled with the badge "Approved by someone else"; No dues on schedule: "No accounts due in this period" with the next payout date; Companies: hidden at launch, and a "Companies" filter appears when enabled later; automatic payout failed (splitting or STC Pay): "Failed" badge and a retry button for whoever has "Approve payouts" (PAY-006, INT-014)

#### A19 — Support and Tickets

Context, evidence, decision, satisfaction, and object to.

- Elements: Tickets: a list with the tabs "Mine" and "Unassigned" first, then "All"; by type: not delivered, missing and damaged, Mart damage, objections, financial; each ticket shows: type, order number, customer or party, age, assigned agent, and a red badge for exceeding the trust limit, Ticket header: type, order number (SUP-001), report time since delivery (accepted within one hour only, SUP-005), assigned agent, open-order button, call button, three cards above the ticket before the decision: evidence, trust, financial authority, Trust: refund rate, number of orders and refunds, badge for exceeding the trust limit, and no automatic refund (SUP-004, SUP-007), and the count of notifications or restriction, Evidence file: its content (SUP-002) and the delivery photo, Damage (reported items): item, quantity, price, reason, Financial authority: the agent's role, what they can execute without approval, their role's amount limit, and that anything above it is escalated (ADM-043), Reply: the ticket conversation, each message with its time and the agent's name, Support decisions log on the ticket: reason, liable party, evidence, amounts per party, executor and time, objection status, Objection: the text of the objection by the charged merchant or driver (within 7 days of the decision notification) and its attachments, and the supervisor's decision; the customer has no objection, Satisfaction: the customer's rating of the resolution after closing, Support decision window: refunded items, reason, refunded to (the original payment method or refund credit in the wallet), "Who is liable for the loss?" with three cards (merchant, driver, the platform), loss charge amount, evidence, result of the role-limit check; and a confirm button that writes the full effect, such as "Refund [amount] to the customer and charge it to the merchant", Repeat-order credit window: amount and reason (MKT-002), Calling: masked-call buttons and call recording after the call center is connected (INT-013)
- Actions and what happens:
  - **Reply**: sends the message immediately in the ticket conversation, and the party receives a notification that opens the ticket
  - **Transfer**: a list of agents or teams (support supervisor, finance, operations) with a mandatory note; ownership moves and the recipient's name appears on the ticket, and the transfer is logged
  - **Refund within authority**: opens the support decision window. On confirm, the customer is refunded and the amount is charged to the liable party with a linked loss-charge entry (or recorded as a platform expense), and the party receives a notification with the reason and sees it in their statement with an objection button within 7 days (SUP-003, PAY-025). Above the role limit the button becomes "Escalate for approval" and is sent to a higher role without executing (ADM-043)
  - **Manual penalty**: opens the penalty window (A04): party, amount, reason, evidence, destination of the amount (PAY-025); a decision independent of loss allocation, and it is logged (ADM-043)
  - **Close**: a confirmation showing a summary of what was executed; a request to rate the resolution is sent to the customer; the support decision is final for the customer, and the charged merchant or driver may object to it within 7 days of the decision notification (SUP-003)
  - **Take ticket**: the "Mine" button assigns the unassigned ticket to the current agent and shows their name to others; if another agent got there first, "[Name] took it moments ago" is shown
  - **Open order**: opens the order file in A03; from there, the cancellation window after the grace period (reason, liable party, amounts per party) for whoever has the permission
  - **Repeat-order credit**: opens its window; on confirm, promotional credit is added to the customer directly and logged (MKT-002)
  - **Masked call**: calls the party without revealing their number, and the call and its recording are logged against the order and the agent (INT-013). Before the connection, the button is disabled with the tooltip "Call center not connected"
  - **Accept objection / Reject objection**: accepting amends the decision with a reversal entry for the charged amount; rejecting requires a reason. Both notify the party and are logged in the audit log
  - **Reverse decision**: reverses a previous support decision with a reversal entry linked to its original, after a reason is written
- Validation and error messages:
  - Reason and liable party are mandatory; the confirm button is disabled until both are complete
  - The charged amount must not exceed the proven damage (SUP-002): "Must not exceed the proven damage ([amount]). For a penalty, use 'Manual penalty'"
  - The refunded amount must not exceed the amount collected (PAY-003): "Greater than the amount collected ([amount])"
  - Report photo according to its type (SUP-002)
  - Repeat-order credit: amount greater than zero and reason mandatory
  - Transfer always requires a note; closing requires a note when a decision is pending
- Permissions:
  - Tickets and conversations: admin, support supervisor, support agent; operations is read-only, without cancel and refund buttons
  - Refund, compensation, assigning the liable party, repeat-order credit, loss charge, and penalty: (ADM-043)
  - Reverse decision, accept or reject objection, and ticket assignment: support supervisor and admin, and finance for reversing a decision
- UX decisions:
  - One primary button "Refund within authority"; the penalty has a different color and is placed away from it; close is at the other end
- Requirements: SUP-002 SUP-004 ADM-043 SUP-003 SUP-007 SUP-009 MKT-002 INT-013 PAY-025 PAY-003 ADM-042 SUP-001
- Navigates to: A03 A04 A13 A26
- Special states: ticket being worked on by another agent: their name is visible, it opens read-only, and a "Request transfer" button replaces the decision buttons (ADM-042); customer exceeded the trust limit (SUP-007): red badge "Exceeded trust limit · Support supervisor decision"; repeated exceedance: badge "Customer notified" then "Restricted" (SUP-007); order delivered more than an hour ago: no new report on it in all sections including the Mart (SUP-005, SUP-009); and the customer's general ticket does not reopen the support decision (SUP-003); amount above the role limit: "Awaiting support supervisor approval" and not executed before approval; open objection on a support decision: badge "Objection" in the list and the ticket header; "Not delivered" report: shows delivery evidence instead of the photo (SUP-002)

#### A20 — Team and Shifts

Takeover, handover, and notes without overlap.

- Elements: Tabs: current shift, team performance, city and service distribution, handover log, "Your shift" card at the top of the page: start time, whom you took over from and the number of acknowledged notes, number of open items under your name, handover time and to whom, Shift summary: on shift, open alerts, unowned, average pickup time, pending handover notes, Team-now table: agent, role, cities and services, current load, resolved today, status (on shift, handed over, starts later), "Unowned" list: short, unassigned alerts and tickets with a prominent "Mine" button, and text explaining automatic distribution (ADM-042), Takeover window: the previous shift's notes item by item with a confirm-read button, Notes (handover window): the receiving agent, and every open item under your name with a note field with a three-question prompt text: what did you do, what is pending, what is needed next, Performance (team performance): each agent's metrics and their comparison over the same period (ADM-041), Agent profile: their action log (from the audit log) and their shifts, City and service distribution: an agent × cities and services table editable by the supervisor, and a redistribute-open-alerts button, Handover log: recorded handovers (ADM-042)
- Actions and what happens:
  - **Take over**: opens the takeover window; after confirming the notes were read, the handed-over items move to the agent and the takeover is logged (ADM-042), and alerts start reaching them
  - **Hand over**: opens the handover window; the button "Hand over N items to [recipient]" is disabled until all notes are written. On confirm, the items and their notes move and the handover is logged (ADM-042), the shift ends, and alerts stop reaching the agent
  - **Transfer**: moves an order, alert, or ticket to another agent; the recipient's name appears on the item immediately, and the transfer is logged (ADM-003)
  - **Edit cities and services**: changes the agent's cities and services; new alerts are assigned accordingly, and open ones stay with their owner until the supervisor redistributes them
  - **Mine**: assigns the unassigned alert or ticket to the current agent and shows their name on it; if someone else got there first, "[Name] took it moments ago" is shown
  - **Redistribute alerts**: shows the proposed distribution across available agents by city and load, and applies it after confirmation
  - **Open performance figure**: opens the list of orders or alerts that the figure represents (ADM-041)
- Validation and error messages:
  - A note for every open item: "Write a note for this item before handover"
  - The recipient is mandatory and cannot be the agent themselves
  - Transfer requires a note
  - "Mine" does not work outside the agent's cities: "This alert is outside your cities"
- Permissions:
  - Every dashboard agent takes over and hands over their own shift and transfers their own items
  - Editing cities and services, redistribution, and transferring an item owned by someone else: the supervisor (support supervisor for the support team, and admin)
  - Team performance and agent profiles: admin, and support supervisor for their team
- Requirements: ADM-041 ADM-042 ADM-003 ADM-002 INT-013
- Navigates to: A02 A19 A22 A26
- Special states: agent has not taken over yet: no alerts reach them, and "Take over" is the only action; incomplete handover: the handover button is disabled with the count of items without a note; item being worked on by another agent: their name is visible, action buttons are hidden, and a "Request transfer" button appears; no agent available in the alert's city: it goes to the supervisor; no recipient in the next shift: handover goes to the supervisor

#### A21 — Reports

Every report with a custom period, comparison, export, and scheduling.

- Elements: Groups: a grouped list of reports (orders, cities and coverage, drivers, merchants and branches, customers, marketing and loyalty, finance, support, operations and system), and the selected report is highlighted, Filters: period with ready shortcuts (today, last 7 days, last 30 days) and "Custom", and city and section, Custom: start and end date (REP-001), and a single line above the report stating the applied period in plain language: "Includes the whole end day · Riyadh time", Comparison: against the previous equivalent period, or the same period last month, or no comparison; with the comparison period's dates, Platform revenue: a waterfall of components (service fees, contract fees and the Mart and pharmacy percentage, payment fee, platform percentage of delivery, ads and cashier, penalties that went to the platform, minus platform funding of offers and compensations) then the actual Moyasar fee and platform net (PAY-027), next to gross sales shown separately (ADM-006), Saved view: its name, the period and filters saved with it, and the roles it is shared with, Export: Excel and PDF buttons with schedule and save in one row under the report, Sending (scheduling): report, frequency, recipients by email, format (Excel or PDF); and a list of schedules, MCP: a quiet card below the report with a plain-language question field, and text explaining that it is read-only and that a financial change needs approval inside the dashboard (INT-011)
- Actions and what happens:
  - **View**: computes the report with the current period, filters, and comparison and shows the figures, chart, and table (ADM-030)
  - **Save**: asks for a name and saves the period, filters, and comparison; it appears in "My saved views" and opens in the same state
  - **Share with role**: picks one or more roles to see the view; each agent sees only the figures of their own cities and permissions, and financial reports are not shared with a role that does not have them
  - **Schedule**: a window: frequency (ADM-006), recipients, format; it is sent with the chosen rolling period, and appears in the schedules list with a pause button
  - **Excel**: downloads the report with the same period and filters (REP-001)
  - **PDF**: downloads a print-ready copy with the period, filters, and comparison
  - **Apply custom range**: validates the two dates then applies the period (REP-001)
  - **Open figure**: opens the list from which the figure was computed: orders or ledger entries (ADM-030)
  - **Ask the assistant**: shows an answer or table via MCP (INT-011); an unauthorized user is rejected with the message "You do not have permission for this data"; a financial change appears as a suggestion with an approve button inside the dashboard
- Validation and error messages:
  - Start after end is not executed (REP-001): "Start date is after end date"
  - Saved view name is mandatory and not duplicated
  - Scheduling: at least one recipient and a valid email "Invalid email"
- Permissions:
  - Financial reports: admin, finance
  - Other reports: all roles within the role's scope and cities
  - Assistant: read for anyone who has reports; and financial suggestions (INT-011)
- Requirements: ADM-006 INT-011 REP-001 PAY-027 ADM-030
- Navigates to: A18 A26
- Special states: driver level indicator: last 30 days (REP-001) with a note saying so; financial report for an agent without permission: does not appear in the list; schedule whose sending failed: a badge in the schedules list with a retry button; assistant down: the card shows "Assistant unavailable right now" and the reports keep working

#### A22 — Settings and Integrations

Configurable values, permissions, keys, and connection status.

- Elements: Connection status bar at the top of all tabs: Moyasar, STC Pay, Odoo, OneSignal, OpenLoyalty, PostHog, Adjust, Google Maps (usage percentage of the cap), call center; each badge opens the Integrations tab, Tabs: fees, windows, dispatch, batching, home, roles, feature flags, integrations, security, quality and trust, languages, calculation basis, settings log (ADM-034): for each value: name, type (percentage, amount, duration, count, list), unit, allowed limits, the global value and the selected level's value side by side, version, effective date, the scheduled version if any, last editor, Level selector: global ← region ← city, and "a specific branch" where the setting supports it; and the priority: branch, then city, then region, then global (ADM-034); the inherited value is gray "Inherits global/region" and the overridden one carries an "Override" badge, Currency and time: SAR next to every amount, and the city's time zone next to every effective date (SYS-012), Setting edit panel: the global value (read-only), the source of the current value, allowed limits, new value, "Effective immediately / on date", reason, and below it the setting's versions (scheduled, effective, and previous), Approved rules (ADM-034): locked "Approved rule · read-only under the contract" without an edit button, Dispatch: the twelve dispatch algorithm settings (DSP-001) with their global values and a city-override column, Roles: the list of roles with the number of agents in each role (the six built-in roles and a custom role); a permission × role matrix with values execute/read-only/no access, highlighting the column of the role being edited and the modified cell in a different color until saved; and the role editor: name, role scope (cities and branches), amount limit for financial actions, permissions, Security: two-step verification read-only with no off switch, and idle time before the session expires (ADM-001), Feature flags: a feature × city table with its stages (SYS-006), and the city's pilot group of merchants and drivers (SYS-019), and the minimum allowed version per app and platform, Quality and trust: the "Quality" badge thresholds (MKT-014), and the customer refund-rate threshold and what happens when it recurs (SUP-007), and no automatic refund (SUP-004), and the report window of one hour from delivery in all sections including the Mart (SUP-005, SUP-009), Languages: data rows (SYS-013), and each text with its key and translations, and the count of missing texts per language; notification templates are in A17, Calculation basis (read-only): a table of basis, tax, and invoice (products, platform, fees, or ad invoice) per amount type, and the rounding rules (PAY-029), Integrations: for each integration: status, environment (test/live for Moyasar), last successful operation, number of errors today, test button; for Moyasar "Payment splitting for merchants" is always on with no switch to turn it off, with the status of the last split and the last weekly payout (PAY-006); for STC Pay the last successful payout and the number of failed ones (INT-014); and for Google Maps: the two caps and the cost so far (SYS-021); and for PostHog and Adjust: the list of events sent (INT-008); and MCP: read by default, Call center: a "Later · not connected" card in Integrations (INT-013)
- Actions and what happens:
  - **Edit**: opens the edit panel at the selected level. "Immediately" creates a version effective now, and "On date" a scheduled version with a "Scheduled" badge (ADM-034). A message "Version [number] scheduled to take effect [date]" appears
  - **Test connection**: sends a probe request and shows the result within seconds: "Working · response time" or "Failed" with the provider's message, and updates the status badge; it creates no financial operation and no notification to a customer
  - **Permission**: ticking or unticking a permission for a role shows an "Unsaved change" bar with the impact in numbers "Takes effect immediately for [N] agents". "Save and apply now" applies it immediately in the interface and the server (ADM-001), and the buttons disappear in open sessions
  - **Financial limit**: sets for a role a maximum amount per financial action (refund, compensation, loss charge, penalty) (ADM-043); the limit is shown read-only in A18 and in the decision window for the role's agent
  - **View log**: opens the audit log (A26) filtered by the current tab, setting, or role
  - **Cancel scheduled version**: after confirmation, deletes the scheduled version before it takes effect, and the current one remains; the cancellation is logged
  - **Revert to a previous version**: creates a new version with the previous value without erasing history, immediately or on a date
  - **Remove city override**: a confirmation stating the value the city will inherit; then the city inherits from the region or global from the chosen effective date
  - **Create custom role**: an empty role editor: name, role scope, permissions from the matrix, financial limit; "Create role" adds it to the list and makes it available when assigning agents in A20
  - **Duplicate role**: creates a custom role with the current role's permissions to edit, named "Copy of …"
  - **Delete custom role**: only for a role with no agents; otherwise "Move the role's agents first ([count])"
  - **Change feature flag stage**: moves a feature in a city between stages after a confirmation stating who will be affected; without a new release (SYS-006)
  - **Edit minimum allowed version**: sets the minimum version per app and platform; older versions are asked to update on open
  - **Add language**: added as a row and its missing texts appear for translation; it is not enabled until the admin chooses "Enable language"
  - **Switch Moyasar environment**: between test and live after a written confirmation, and logged in the audit log
- Validation and error messages:
  - The value must have the correct type and unit and be within the allowed limits, such as "The task-offer radius at start must not exceed its maximum ([value])"
  - Priority index weights sum to 100: "Total is [N]; must be 100"
  - Effective date is not in the past: "Choose a time after now"
  - A reason is mandatory for every edit: "Write the reason for the edit"
  - Role name is not duplicated, and a custom role contains at least one permission
  - A change that leaves the system with no agent holding "Roles and permissions" is not saved
  - Minimum allowed version is not lower than the minimum supported version (SYS-006)
- Permissions:
  - The page is for admin only (settings, cities and fees, roles and permissions, and audit log); other roles do not see it, and finance sees the financial limits read-only in A18
- Requirements: SYS-002 ADM-001 INT-008 INT-014 INT-001 REG-007 ADM-034 ADM-002 SYS-006 SYS-012 SYS-013 SYS-019 SYS-021 PAY-029 MKT-014 SUP-007 SUP-004 SUP-009 INT-010 INT-013 ADM-043 DSP-001
- Navigates to: A26 A20 A17 A18 A09
- Special states: scheduled version: "Scheduled" badge and its effective date, then "Effective" automatically at its time; inherited value: shown with its source; editing it creates an override for the selected level; integration down: red badge and last success, and text beside it that PostHog, Adjust, OpenLoyalty, or Odoo being down does not stop orders or payment; Maps cap reached: badge "Saved estimates in use" (SYS-021); call center not connected: masked-call buttons are hidden (INT-013); unsaved permission change: an alert bar, and leaving the tab asks "Save or discard"; language with missing translations: the count of missing texts beside it and it is not enabled

#### A26 — Audit Log (new)

A single non-deletable log for every financial change or change to roles, permissions, or settings, with its executor, time, and before and after values.

- Elements: Period: shortcuts and custom in Riyadh time, Event type: financial, roles and permissions, settings, payouts, AI assistant (MCP), Executor and executor role: two filters, Search: by order number, ledger entry, account, or agent, Summary: today's events by type, and the number of rejected attempts, Table: time, executor and their role, action and entity, before ← after in one short column, source with a badge (dashboard or MCP), Event details in a side panel: before and after side by side, executor, time to the second, role scope (cities), impact, reason, reference, and the second approver if any, Rejected attempts: what the system rejected (a payout creator trying to approve it, an MCP request outside permissions, a disallowed city), Permanent notice: the log cannot be deleted or edited from the interface
- Actions and what happens:
  - **Filter**: filters and tabs update the table and summary immediately, and are saved in the URL for sharing with an authorized agent
  - **Open event**: clicking a row shows its details in the side panel without leaving the page
  - **Open entity**: navigates to the related order, ledger entry, role, or setting (A03, A18, A22)
  - **Filter by executor**: shows all events of the same agent in the period
  - **Export**: exports the filtered results to Excel or PDF; the export itself is logged as an event
- Validation and error messages:
  - Period: start cannot be after end "Start date is after end date"
- Permissions:
  - Admin sees all events
  - Finance sees financial events only, from the "Closing and controls" tab in A18
  - No one deletes or edits an event, and there is no button for it (ADM-002)
- UX decisions:
  - Search by order number or ledger entry shortens tracing from a report to a decision
- Requirements: ADM-002 ADM-001 ADM-034 ADM-043 INT-011 PAY-005 PAY-006 ADM-013
- Navigates to: A22 A18 A03
- Special states: no results for the filter: "No events match these conditions" with a clear-filters button; MCP event: "MCP" badge and the original request text, and a financial change appears with the agent's approval inside the dashboard; event approved by two people (such as a wallet freeze): the requester and approver and the time of each; rejected event: a light red row and the rejection reason

Shared states for all pages: clear loading without fake numbers; an empty state that explains the next step; an error with retry; network loss preserves inputs; an unavailable permission hides the action

## Reports

### Merchant Reports

**Sales**
- Sales summary: the dashboard shows sales, orders, and average order value daily, weekly, and monthly, with comparison to the previous period
- By hour and day: peak times for each branch
- By order method: for each of delivery, self-pickup, menu link, the dashboard shows the count, amount, and average order value
- By branch: the dashboard compares branches across all indicators
- By district and city: where orders come from

**Products**
- Product performance: for each item the dashboard shows quantity, sales, its share, and its rating, with the best and worst sellers
- Add-ons and sizes: the most chosen and their revenue
- Out-of-stock products: when each item went out of stock and for how many hours, and the affected orders
- Ordered together: the dashboard shows items that recur in a single order, to build meals

**Operations**
- Acceptance and preparation: the dashboard compares actual acceptance and preparation time against the confirmed duration, per hour, per branch, and per item
- Delays and compensations: late orders, delay duration, and compensation amount
- Cancellations: cancelled orders by reason and who cancelled them
- Driver waiting at your store: how long the driver waits for your order after arriving
- Late penalties: penalties and loss charges, their reasons, objections, and decisions; no automatic financial calculation
- Availability and working hours: actual opening hours, temporary closure, busy mode, and auto-accept

**Customers**
- Your customers: count, new versus returning, and order frequency
- Loyalty: customers who ordered twice, three times, or more, and the average days between their orders
- Customers by district: shows the distribution across districts without showing names or numbers

**Ratings and Reports**
- Ratings: overall rating and its trend, each item's rating, and comments
- Reports: by reason: missing, wrong, quality, delay
- Objections: your objections and their outcome

**Marketing**
- Offer performance: the dashboard shows for each offer: orders, sales, your cost, new customers, and average order value
- Ad and campaign performance: impressions, clicks, orders, sales, spend, and return
- Cashback: amounts returned to customer wallets and orders

**Finance**
- Weekly statement: the calculation from sales to net, with the payout date
- Per-order breakdown: sales, percentage or customer fee, gateway, your share of offers, compensation, refund, net
- Per-customer fee: for a Type 1 contract the dashboard shows: the amount deducted in the period, the number of customers paid for, and who reached the 30 SAR cap, without personal data
- Payouts: the dashboard shows every payout with its date, amount, and status
- Monthly commission invoice: the platform's invoice includes its commission with 15% tax, and itemizes each order
- Product invoice archive: every invoice the merchant issued or uploaded, linked to its order, plus orders whose products invoice is late; the products invoice is required for write-in orders only, and optional for the rest

**Mart Only**
- Picking accuracy: the percentage of items removed from each order with customer approval
- Picking speed: average order picking time per employee
- Low and out-of-stock inventory: items close to running out and those most often out of stock

**Staff**
- Staff performance: the orders each employee handled, average acceptance and preparation time, and delays
- Action log: the employee who accepted the order, who issued the products invoice, and who handed the order to the driver

**Write-in Orders and Pharmacies**
- Write-in orders: number of orders, products invoice upload time, payment rate after it, and average amount
- Returns: orders returned to the pharmacy and what was refunded

### Admin Reports

**Orders**
- Detailed order log: the report shows every order with the times of each stage, its amounts, its parties, and its status.
- Stage times: average driver acceptance, preparation, waiting, travel, and handover, per city and hour
- Cancellations: count, percentage, reason, who caused them, and their cost
- Orders without a driver: waiting time, handling after support intervention, and those converted to self-pickup
- Late orders: preparation and delivery delays, who caused them, and penalties
- Customer non-response: count, support alerts at 30 minutes and their decisions, and handling with support permission
- Write-in orders: products invoice upload time, payment time, and unpaid ones
- Self-pickup: count, pickup time, no-show, and the self-pickup discount and its funder
- Orders by hour and day: heat map, per service
- Location correction: count, the farthest, outside the zone, and payment rejection
- Out-of-stock and substitutes: out-of-stock products, substitutes, and customers' pre-selected choices

**Cities and Coverage**
- City performance: orders, growth, delivery, cancellation, and revenue per city
- Orders versus drivers: orders per driver per hour per city
- Contracting targets: stores customers requested that were not added, coming from: searches with no result, "Suggest a store", and coverage requests
- Coverage requests: the map shows the locations of customers, merchants, and drivers that fall outside the service area.
- Branch zones: branches whose zone covers a specific district versus the governorate

**Drivers**
- Driver performance: score, level, and every indicator per driver
- Levels over time: the number of drivers in each level weekly
- Shifts and login hours: those logged in in the morning, evening, and night, and each driver's hours
- Driver earnings: delivery, tip, incentives, penalties, and net
- Incentives and their impact: the cost of each incentive, extra orders, and cost per extra order
- Penalties and sanctions: penalties and loss charges, their reasons, objections, and decisions; no automatic financial calculation
- Delivery companies: each company's performance and dues
- Deposits: paid, refunded, and deducted

**Merchants and Stores**
- Store performance: sales, orders, rating, and delays per store and branch
- Preparation and readiness: stated versus actual duration, and the time "Ready" was pressed
- Invoices: products invoice upload time, late ones, and missing ones; the products invoice is required for write-in orders only, and optional for the rest
- Menu and price review: requests, approved, and rejected, and edits within the allowed percentage
- Contract types: platform revenue from each contract type and each store
- Menu link: orders from links, and the value of the waiver
- Cashier integration: stores connected per system, integration failures, and "Another system" requests
- Pauses and closures: temporary pause, and closure during working hours
- Merchant penalties: penalties and loss charges, their reasons, objections, and decisions; no automatic financial calculation

**Customers**
- New, active, and lapsed customers: per city and period
- Retention: monthly cohorts showing how many return from each month.
- Customer value: average order value, frequency, and spend
- Ratings and reports: by reason, store, and driver
- Wallets: balances by type, expiry, and spend

**Marketing and Loyalty**
- Coupons and offers: usage, cost per party, and return
- Hour Deal: participants, orders, and cost
- Ads: spend, impressions, and orders
- Loyalty: points earned, redeemed, and expired, and their cost from platform net
- Refer a friend: invitations, completed ones, and cost per new customer
- Notifications: sent, opened, and orders afterwards, per category

**Finance**
- Net revenue by components: the report shows every income source after the platform's funding of offers and compensations.
- Profitability per order: per city, section, and contract type
- Collection and reconciliation: Moyasar, the bank, and discrepancies
- Dues and payouts: merchants, drivers, and companies, and failed ones
- Liabilities: wallets, deposits, and manual penalties
- Refunds: by reason and who bore them
- Expected balance: shows what will come in and go out each day for the next week.

**Support**
- Tickets: count, first-response time, resolution time, satisfaction, and what was resolved by self-service
- Agent performance: the report shows tickets and refunds per agent, and the operations team's performance in detail is on a separate page.
- Calls: inbound and outbound, wait time, per order and agent
- "Not delivered" reports: count and the outcome of the evidence file

**Operations and System**
- Operations alerts: count, response time, resolved, and escalated
- Operations interventions: instant incentives, manual assignment, and disabling and ban
- Audit log: the report shows every edit with who executed it and the value before and after.
- Pharmacies: orders, rejected prescriptions, and those returned to the pharmacy

## Requirements

### Compliance: HRDF (Hadaf) Program (REG)

#### REG-006 — HRDF (Hadaf) Program Adoption [Launch-critical]

Rules:
- Adopting the HRDF (Hadaf) program is a core part of the launch scope.
- The system shows the number of deliveries by the Saudi driver and provides an exportable report without adding other compliance items.

Acceptance criteria:
- The service, the counter, and the report appear in the launch acceptance list.

Pages: D12

#### REG-007 — Reporting to the Transport General Authority (TGA) [Launch-critical]

Rules:
- The system sends the Transport General Authority (TGA) driver, vehicle, and order data in the format and at the timing the Authority specifies.
- The integration details and required data are in "Open questions" (Q-02), and the integration is not coded before they are resolved.

Acceptance criteria:
- The data of every active driver and every delivered order is sent in the approved format, and each submission is logged with its result.

Pages: A22

### Customer App (CUS)

#### CUS-001 — Account and Language [Launch-critical]

Rules:
- Registration and login with a phone number and a verification code by SMS; no Google or Apple sign-in.
- Browsing is available before sign-up, and login is requested at an action that needs an account.
- Arabic and English in the apps and both dashboards.
- The customer changes their phone number from the app with a code sent to the new number.
- "Delete my account" is available inside the app with a warning that promotional credit and points are forfeited; refund credit is returned to the customer's card via support before deletion.
- The verification code arrives through the 4jawaly gateway by WhatsApp or by SMS according to what the gateway supports, and is sent by SMS when WhatsApp is unavailable.

Acceptance criteria:
- Browsing does not ask for a verification code.
- Login does not create two accounts for the same number.

Pages: C14

#### CUS-002 — Addresses and Location Accuracy [Launch-critical]

Rules:
- The customer saves multiple addresses: map location, building, floor, apartment, and entry instructions.
- The customer confirms the address location before saving it, and an optional entrance photo can be attached.
- The address supports the Saudi short national address for locating, and instructions for no-answer and leave-at-door.
- The app warns if the customer's current location is far from the selected address.
- A driver's entrance correction is saved for subsequent deliveries.
- The warning "Your location is far from the address" appears at 300 meters or more, and shows the actual distance.

Acceptance criteria:
- The address is not saved without confirming the location.
- The map and address instructions are shown in understandable wording before saving.

Pages: C13

#### CUS-003 — Home and Ranking [Important]

Rules:
- The system ranks stores by the customer's city, time, and previous orders.
- The system does not show a store outside the customer's city as available.
- Ad placements are visually distinguished
- The system builds the "Suggestions for you" row from items the customer ordered and their recorded dietary preferences.

Acceptance criteria:
- When the customer changes the address, the system re-renders the eligible stores and fees.
- A new user does not see an empty page.
- The "Suggestions for you" row does not show a store outside the customer's city.

Pages: C01

#### CUS-004 — Search and Filters [Launch-critical]

Rules:
- Unified Arabic and English search covering the four sections and respecting the branch zone.
- Search tolerates spelling variations and typos.
- Filters: section, category, offers, fees, self-pickup, and rating; sort: nearest, fastest, highest rated, and lowest delivery fee.
- When there is no result, alternatives are shown along with a suggest-a-store option that feeds the contracting targets.

Acceptance criteria:
- No result that is unavailable for the customer's address is shown.
- Alternatives remain visible when there is no match.

Pages: C01 C02

#### CUS-005 — Store and Product Page [Launch-critical]

Rules:
- Store header: name, logo, category, rating, share, favorite, minimum order, time, and delivery fee.
- Platform offers the branch has joined and approved merchant offers appear under the preparation time.
- The product list shows description, image, price, sizes, and add-ons; no mandatory nutrition data.
- The menu is shown in the active menu period, with products within their availability time.
- A near-closing label appears in the last 30 minutes with a counter; the bottom bar shows the cart and the remainder to the minimum order or the delivery offer.
- The customer sees one branch of each merchant on the home page, in the sections, and in search: the nearest open branch whose zone covers the customer's address; if all its branches are closed, the nearest one appears with the tag "Closed · opens ...".

Acceptance criteria:
- A product outside its availability time is not shown.
- An offer outside the branch zone is not shown.
- Joined platform offers and approved merchant offers are in the same position.
- A merchant with two branches covering the address, the nearer one closed and the farther one open: only the farther open branch appears.

Pages: C03 C07 C08

#### CUS-006 — Reorder, Favorites, and Rating [Launch-critical]

Rules:
- On reorder, the system creates a cart with today's prices and availability, and shows the differences.
- The customer rates the food separately from delivery, and it is tied to an actual order.

Acceptance criteria:
- An out-of-stock item from the old order is shown with a warning.

Pages: C10 C19

#### CUS-007 — Tracking and Order Arrival Time [Launch-critical]

Rules:
- The map shows the order status and a single arrival time: preparation + Google Maps route from store to customer + 5 minutes.
- The route starts after pickup, and the estimate updates on a material change or at a configured interval.
- When the driver gets within one kilometer, the customer receives a notification.
- No delivery code for the customer, and no saving of or asking for this code on any screen.
- The customer sees the driver's first name.

Acceptance criteria:
- No delivery code and no field to enter it appears for the customer or the driver.
- The overall time matches the formula and does not show a breakdown of components.

Pages: C11

#### CUS-008 — Chat and Calling [Launch-critical]

Rules:
- Chat and calling with masked numbers within the order.
- Phone numbers typed in the chat are removed automatically.
- Contact expires a configurable period after the order is closed, with an assumed default of 24 hours; the conversation owner can ask the platform to remove part of it.
- Phone numbers, links, and external accounts are removed from the chat.
- Communication stays available after the order is closed for the configured period (24 hours by default).

Acceptance criteria:
- The other party does not receive a typed number.
- The chat closes after the specified window.

Pages: C11 C25

#### CUS-009 — Customer Sections and Navigation [Launch-critical]

Rules:
- Sections: restaurants, Mart, Shops, pharmacies; each city manages the section's status and order.
- Restaurants have a menu; Mart is independent grocery stores; pharmacies are write-in; Shops are menu or write-in.
- Inside Shops, manual categories appear first and the stores below them.
- Bottom navigation: Home, Orders, Offers, My Account.
- No Taxi launch button at launch.

Acceptance criteria:
- Entering a grocery store shows only that grocery store's products.
- A write-in Shops store opens a write-in form, not an empty menu.

Pages: C01 C03 C05

#### CUS-010 — Tip [Important]

Rules:
- When ordering, the customer chooses a preset percentage or sets an amount themselves.
- After delivery: with the rating
- The option "Use the same tip in my future orders" adds the tip automatically to subsequent orders, and the customer can turn it off from settings
- The tip's included 15% VAT is excluded, like everything else the customer pays (tip ÷ 1.15), and the rest reaches the driver in full with no platform percentage.
- The tip follows the delivery fee: if the delivery fee is paid out to the driver, the tip is paid out with it, and if the delivery fee is refunded to the customer, the tip is refunded in full.
- In write-in and pharmacy orders, the tip is shown at delivery payment in fixed amounts only, and the automatic percentage tip is not applied.
- The after-delivery tip option always appears, even for someone who paid a tip with the order.

Acceptance criteria:
- The automatic tip appears in the cart, and the customer can change it before payment
- From a 10 SAR tip, 8.70 reaches the driver.
- When an order is ended due to customer non-response (ORD-008), the tip is paid to the driver because the delivery fee was paid to them.
- On a cancellation where delivery is refunded to the customer, the system refunds the tip in full.

Pages: C14 C18 C19 C24

#### CUS-013 — Language Extensibility [Later]

Rules:
- Texts are designed so that a new language can be added without rebuilding the app, such as Urdu for the expatriate workforce service.

Acceptance criteria:
- When a new language is added, the app is not rebuilt.

#### CUS-015 — Offers Page [Important]

Rules:
- Gathers active offers eligible for the customer's address, sorted by savings with each offer's duration and conditions.
- The city alone is not enough; an offer from a store whose zone does not cover the customer's address is excluded from the page, the banner, and the notification.
- Hour Deal shows the expiry and actual stock, and disappears when sold out or expired.

Acceptance criteria:
- The customer does not see an offer from a restaurant that does not deliver to them.
- The end time is the same for all customers.

Pages: C22

#### CUS-020 — Item Ratings [Later]

Rules:
- The customer rates each item they ordered with a like or dislike.
- The system shows a satisfaction indicator for an item once its number of ratings reaches the minimum set by the platform.

Acceptance criteria:
- A customer cannot rate an item they did not order.
- The satisfaction indicator does not appear before the minimum number of ratings is reached.

#### CUS-023 — "My Purchases" in Mart [Later]

Rules:
- The customer re-orders previously purchased items with one tap.
- The customer saves lists such as "Weekly groceries".

Acceptance criteria:
- The system adds the saved list to the cart in full.

#### CUS-024 — Send the Order to Someone Else [Later]

Rules:
- Recipient name, number, and instructions; the recipient receives an order tracking link by message.
- The recipient is fixed on the order, and hands over to the driver without a customer code.

Acceptance criteria:
- The link reaches the correct recipient without exposing another order's data.

#### CUS-025 — Pickup from the Car [Later]

Rules:
- For stores that support self-pickup, the customer sends "I have arrived" with the car type and color.
- The merchant sees the order number and car description and confirms handover, without a customer code.
- The service is not available for Mart.

Acceptance criteria:
- The arrival alert includes the car description and order number.

### Cart and Payment (CRT)

#### CRT-001 — Cart and Notes [Important]

Rules:
- The cart is for one branch, which is the store as the customer sees it.
- The merchant sees the sizes, add-ons, and customer notes.
- The customer sees a small notice stating that notes are not binding on the merchant.
- The system recalculates price and availability before payment.
- A note per item, in addition to a general order note.
- The cart does not move between the merchant's branches; if the customer changes their address to one outside the branch zone, payment is disabled, and an "Open branch ..." button appears if another branch of the merchant covers the address, starting a new cart.

Acceptance criteria:
- The notice appears next to the notes field.
- Changing the address to one covered only by another branch of the merchant does not move the items to it.

Pages: C07 C08 C09

#### CRT-002 — Free Delivery Bar [Launch-critical]

Rules:
- The system shows what remains for the customer to qualify for a free delivery offer that is active in the store's city.

Acceptance criteria:
- Removing an item immediately reduces qualification
- The system does not advertise free delivery for a branch that does not participate in the offer.

Pages: C07 C09

#### CRT-003 — Suggested Add-ons [Launch-critical]

Rules:
- The system shows suggestions from the same store and does not add them automatically.

Acceptance criteria:
- Each tap on the add button modifies the cart only once.

Pages: C09

#### CRT-004 — Cart Expiry [Launch-critical]

Rules:
- It expires at the end of the branch's working hours, and after 24 hours for branches that operate all day
- The cart does not reserve stock or price.
- If the customer returns after the cart has expired, the items remain, and their price and availability are re-validated with a notification.

Acceptance criteria:
- If the customer returns after the cart has expired, the items remain and the app re-validates them.

Pages: C07 C09

#### CRT-005 — Payment Summary Breakdown [Launch-critical]

Rules:
- It shows the products, delivery, service fee, discounts, tip, wallet usage, and the amount due.
- The service percentage depends on the order type per PAY-021: 2.5% for menu and Mart on products after discounts + delivery, excluding the tip and before the service fee itself; or 5% on write-in and pharmacy products only.
- Before paying the products invoice in a write-in order, it distinguishes the previously paid delivery from the amount due now.

Acceptance criteria:
- The sum of the line items equals the held amount or the amount due for the second payment.

Pages: C09

### Order Lifecycle (ORD)

#### ORD-001 — Order Statuses [Launch-critical]

Rules:
- Order status, payment, the driver's task, and the products invoice are independent fields; issuing the products invoice is not a condition for completing a menu order.
- Customer statuses: Looking for a driver, Preparing, Delivering, Delivered; it stays Preparing until the driver picks up.
- Each transition is executed on the server once and records the actor and time; racing transitions do not repeat the event.
- Mart follows the menu lifecycle; write-in has two payments and a mandatory products invoice; Taxi is a deferred foundation.
- The "Awaiting support decision" state is non-final: the order enters it whenever its amounts are a staff decision (no-show in self-pickup, unpaid in write-in, rejection before the products invoice, out-of-stock item), and it is closed only when the decision is recorded.
- Closing is reaching a final state, at which the hold is captured or voided: cancellation is a closing without delivery in which all or part of the amount is refunded, and termination is a closing without delivery in which it is captured; rejection, out-of-stock, non-payment, and no-show are closing reasons, not states.

Acceptance criteria:
- Pressing Ready does not change the customer status to Delivering.
- Two acceptances do not link the order to two drivers.
- An "Awaiting support decision" order is not captured, refunded or closed before the decision is recorded under the name of the person who made it, except for the automatic capture at 24 hours from the hold (PAY-001); after that, the decision is executed as a refund.

Pages: C10 MD02 A03

#### ORD-002 — Customer Cancellation Window [Launch-critical]

Rules:
- The rule that the customer may cancel within 60 seconds of payment remains.
- After the window, the order is sent to dispatch and the app does not offer the usual customer cancellation.
- During the window, next to the countdown: "You can cancel your order free of charge within {s} seconds".
- Support actions and the special cancellation option after no driver is found remain, per ORD-004.
- After the window, the cancel button is replaced, with a support button: "Your order is now in progress. To cancel, contact support".

Acceptance criteria:
- Cancelling at second 59 cancels the hold once.
- After the window, the usual cancel action is not allowed; the support path appears without the two phrases.

Pages: C09 C11 C15 C17

#### ORD-003 — Order Dispatch and Preparation [Launch-critical]

Rules:
- In menu, Mart, and write-in, the driver accepts first, then the order reaches the merchant, deliberately: no order is prepared without a driver; and the announced arrival time includes the time to find the driver, then preparation (ORD-011).
- The default order duration is the longest preparation time among the products; write-in takes the branch's default duration.
- The merchant may adjust the duration once within 3 minutes of the order's arrival; after that the default applies, with a limit of 40 minutes.
- The customer sees "Being prepared", and the delay is measured from the driver accepting the order; the merchant's preparation time is counted from when they open the order in the app or 3 minutes after it arrives, whichever comes first (ORD-007).
- The Ready button is an explicit decision; the products invoice is optional in menu and Mart and mandatory in write-in.
- "Open order" means the merchant opens the order details. The only duration adjustment allows increasing or decreasing within the 40-minute limit.
- Mart is like the restaurant: its default duration is applied automatically, and it has one optional adjustment.

Acceptance criteria:
- Products of 10, 20, and 30 minutes give 30 minutes.
- Ready works without an invoice in a menu order.
- Opening the order in the first minute starts preparation immediately.

Pages: M01 M02

#### ORD-004 — Cancellation and Alternative Pickup [Launch-critical]

Rules:
- The customer may cancel normally within 60 seconds (ORD-002).
- After the window, the order is cancelled only through support: the support agent refunds the customer, determines the party liable for the loss for the loss charge (merchant, driver, or platform) and any penalty, and writes the reason (PAY-025).
- If the driver has already picked up the order from the store, the support agent also decides what is paid to the driver and what each party bears.
- Two cases put the order automatically into "Awaiting support decision": an out-of-stock item for which the customer previously chose "Cancel the order" (MER-032), and a write-in order not paid within 10 minutes (ORD-013). After them, support decides the loss charge, the penalty, or the amount, then the order is closed.
- No cancellation by the merchant in menu and Mart; the merchant rejects write-in only before uploading the products invoice, and the order enters "Awaiting support decision".
- At 5 minutes without a driver, an alert reaches support; at 15 minutes support intervenes and offers the non-Mart customer self-pickup within 5 minutes or a full refund.
- Pharmacy and write-in orders after 15 minutes without a driver: the delivery hold is released and the order is canceled by support decision.
- Mart has no self-pickup; after 15 minutes support handles assignment or cancellation and refund, without transferring to another grocery.
- If the customer does not choose within 5 minutes (non-Mart), the order is escalated to a support agent to decide; no automatic cancellation.
- The liable party in the cancellation window: the merchant, the driver, the platform, or "No loss charge"; the penalty is a separate, optional decision.

Acceptance criteria:
- No reject button in a menu or Mart order.
- No self-pickup option for Mart.
- The system does not deduct a loss charge or a penalty merely because of cancellation.
- A cancellation after the window is not saved without an executor and a written reason, and without specifying the liable party or "No loss charge".

Pages: C12 C16 C18 C21 C24 M04 A02 A03

#### ORD-005 — Driver Pickup and Customer Handover [Launch-critical]

Rules:
- The pickup code is shown to the driver and entered by the merchant within 100 meters of the store; the pickup photo is saved.
- The customer receives without a code; the driver confirms "delivered" within 100 meters with proof of delivery.
- Customer self-pickup is without a code; the merchant confirms handover after matching the order number.
- No operations code, and no Taxi start code; the pharmacy medicine return code is independent of the customer code.
- For hand-to-hand handover, the driver's confirmation within 100 meters with the confirmation time is sufficient; a photo is mandatory only when leaving at the door (ORD-010).

Acceptance criteria:
- The driver's pickup code works only at the merchant.
- There are no customer code fields in the apps or dashboards.

Pages: D04 D05 D15 M03

#### ORD-006 — Task Offer Order [Launch-critical]

Rules:
- Every order delivered from a specific branch is first offered to the active drivers near it.
- After the driver accepts, the order is sent to the merchant; the grocery does not accept or decline in order to pass it to a next grocery.
- Self-pickup is sent to the merchant without a driver task, and is not available for Mart.

Acceptance criteria:
- No order is moved from one grocery to another.
- Mart follows the same menu ordering.

Pages: A03

#### ORD-007 — Merchant Delay Monitoring [Launch-critical]

Rules:
- The system detects when the preparation time is exceeded and sends a warning and an alert to support.
- The monitoring role stops at collecting time and evidence; no automatic deduction.
- A support agent can add a loss charge or penalty manually per PAY-025.

Acceptance criteria:
- Delay alone does not change the merchant's dues account.
- The alert opens the order and its timestamps.

Pages: M01 M02 A02 A03 A04

#### ORD-008 — Customer Unresponsiveness [Launch-critical]

Rules:
- The driver presses "I have arrived" while within 100 meters of the customer's location, then calls the customer and sends them a message from the app.
- After 5 minutes without a reply, a "Notify customer" button appears for the driver; after 30 minutes, an alert reaches support.
- No automatic completion and no operations code; support reviews the location, dwell time, communication, and evidence.
- The support agent decides: end the order for unresponsiveness, retry, or leave at the door with evidence.
- If the unresponsiveness conditions are met and the order is ended, the driver is entitled to their fee and the tip (CUS-010) and the customer is not refunded; if they are not met, support decides on refund or handling.
- The driver does not end the order themselves and does not leave without permission; the pharmacy order is returned per PHR-010.

Acceptance criteria:
- The system does not issue an operations code.
- The passing of 30 minutes does not close the order automatically.

Pages: C13 D14 D06 D15 A02 A03

#### ORD-009 — Location Correction [Important]

Rules:
- The customer corrects their location even after the driver has picked up the order.
- If the new location is farther, the system adds the fee and sends the customer a payment request.
- If the new location is outside the zone, a direct alert reaches support to resolve the issue.
- If the customer refuses to pay the difference, an alert reaches the operations room and a notification reaches the driver. The driver continues to the original location with no extra fee, and the order is not cancelled. The refusal is recorded on the order, and no penalty is imposed on the customer
- The payment window for the location-correction difference is 3 minutes, and its expiry counts as a refusal.

Acceptance criteria:
- The location does not change before the customer pays the difference.
- If the location is outside the zone, an alert is created for support.
- If the customer refuses to pay the difference, the order is not cancelled, and the driver continues to the original location.

Pages: C11

#### ORD-010 — Leave at the Door [Launch-critical]

Rules:
- By default, the driver hands the order to the customer hand to hand.
- A clear "Leave it at the door" option exists in the address instructions and on the tracking screen during the order
- The leave option appears to the driver when the customer enables this option. It is also sufficient for the customer to ask for leaving in the chat
- When leaving the order, the driver photographs the order in place. The system saves the photo on the order and sends it to the customer.

Acceptance criteria:
- The leave option appears to the driver if the customer enabled it or requested it in the chat, or support authorized it (ORD-008).
- Leaving without a photo is not possible
- If the customer writes "Leave it at the door" instructions in the address, the option appears to the driver automatically.

Pages: C11 C25 D05 D14

#### ORD-011 — Displayed Arrival Time [Launch-critical]

Rules:
- Initial arrival time = expected time to find a driver + longest preparation + travel time from the store to the customer + 5 minutes (ORD-003).
- It is shown as a single duration; at pickup the elapsed preparation time is removed and the remaining arrival time is shown.
- Adjusting preparation, reassignment, or order batching recalculates the estimate without counting elapsed time twice.

Acceptance criteria:
- 20 preparation and 15 travel give 40 minutes initially.
- After pickup, preparation is not added a second time.

Pages: C01 C03 C07 C09 C10 C11

#### ORD-012 — Driver Delay Monitoring [Launch-critical]

Rules:
- The reference travel time is recorded from Google Maps and 5 minutes are added as an operational allowance.
- Arrival-for-pickup delay is measured from Ready; the driver's waiting within 100 meters of the store is not counted against them.
- Travel measurement stops upon entering 100 meters of the customer; for batched orders, the planned route is used.
- Delay sends an alert and affects the report; no automatic penalty calculation or per-minute deduction percentage.

Acceptance criteria:
- No financial entry is created from the delay counter.
- Merchant delay does not reduce the driver's score.

Pages: D03 D04 D08 A02 A03

#### ORD-013 — Write-in Orders [Launch-critical]

Rules:
- In write-in and pharmacy orders, driver dispatch does not start until the customer pays the products invoice.
- Text and photos or a prescription; no voice recording for the order.
- The customer pays delivery first, then a 60-second window, then driver acceptance and dispatch to the merchant.
- The merchant uploads the products invoice photo and its amount; the products invoice is mandatory and the merchant cannot reject after it.
- A separate service fee of 5% of the products; no hidden markup rate on the products invoice in pharmacy or write-in and no second 2.5% service fee.
- The customer pays within 10 minutes; their refusal or expiry of the window puts the order into "Awaiting support decision" with the reason "Unpaid" (ORD-001).
- The support agent decides exactly: what delivery fees the customer bears, what is refunded to them, and what is paid to the driver; then the order is closed. There is no automatic rule for these amounts, and the tip follows the delivery fee (CUS-010).
- No pickup before payment; the merchant's percentage follows their contract, and the pharmacy has a configurable percentage with no online payment fee.
- The merchant corrects the products invoice amount or photo once before payment, and the 10-minute window restarts.
- Rejecting a write-in order before the products invoice requires a reason: not available, requires a prescription, outside the store's activity, or other with text; and the order enters "Awaiting support decision".

Acceptance criteria:
- A products invoice of 100 shows products 100 and a separate service fee of 5.
- No payment request is sent without a photo and amount.
- No voice recording.
- Expiry of the 10-minute window puts the order into "Awaiting support decision" once and opens a report for support, and it is not closed before the decision.

Pages: C17 C18 M01 M03 M04 A03

#### ORD-014 — Emergency Report After Acceptance [Launch-critical]

Rules:
- The driver does not apologize for a task after accepting it: acceptance is an irrevocable commitment on their side, and there is no apology button in the app.
- If a breakdown, an accident, or a circumstance arises that prevents them from completing it, they contact support with an emergency report from the Help button (DRV-020) and explain the problem.
- Platform staff decide what is needed: assigning a substitute who picks up the order from the store, or from the first driver's location if they had already picked it up, or another resolution; the order returns to automatic dispatch only by their decision.
- The emergency report is recorded in the driver's performance, and is counted as a violation only by a platform staff decision (DRV-023); no automatic penalty.
- When a substitute is assigned, the first driver's pickup code is cancelled; the fee and tip go to whoever delivered, and any compensation to the first driver is a manual decision.

Acceptance criteria:
- The driver sees no apology button after acceptance, and the first driver's code does not work after a substitute is assigned.
- The time before their assignment is not counted against the substitute.

Pages: D03 D08

### Payment, Fees, and Settlements (PAY)

#### PAY-001 — Payment and Hold [Launch-critical]

Rules:
- An order awaiting support decision that is not resolved 18 hours after the hold is automatically escalated to the support supervisor with an alert, and appears at the top of their list with the time remaining until capture.
- If pre-launch testing shows that a payment method does not support holds, its amount is captured directly at order time, and all cancellation and edit decisions on it are executed as refunds.
- Online payment via Moyasar
- The amount stays held on the customer's payment method until the order is closed, then the system captures what is due and releases the hold on the remainder.
- The order is closed in one of these cases: delivery, ending the order due to unresponsiveness (ORD-008), returning the medicine to the pharmacy (PHR-010), or a support decision on a cancellation or in the "Awaiting support decision" state. In a support decision, only what support specified is captured.
- The system releases the hold in full if the customer cancels within the window, or if no driver is found and the customer chooses a refund.
- Payment methods are mada, Visa, Mastercard, Apple Pay, and Google Pay through Moyasar, all supporting hold then capture; no STC Pay for the customer, no installments at launch (PAY-015), and no cash on delivery.
- Platform staff disable any payment method from settings without an app update.
- An amount stays on hold for at most 24 hours from the hold: if the order is not closed within that time, the system captures the full held amount and the order stays open, and whatever support decides afterwards is carried out as a refund (PAY-003).

Acceptance criteria:
- The system does not capture the amount before the order is closed in one of the listed ways, or before the hold reaches 24 hours.
- If the payment notification is repeated, the system does not repeat the capture.
- Neither STC Pay nor installments appear among the customer's payment methods.
- An order "Awaiting support decision" whose hold has reached 24 hours: the full amount is captured, and a later support decision to return part of it is carried out as a refund, not a hold release.

Pages: C09 C10 C11 C12 C24

#### PAY-002 — Wallet and Rewards [Launch-critical]

Rules:
- Credit has three types: refund (does not expire), compensation (14 days), and promotional (14 days).
- Promotional credit comes from the referral prize, the loyalty program, gifts and cashback. For each promotional credit it is set who funds it: the platform or the branch
- The customer does not top up their wallet and does not withdraw from it.
- Any compensation reaches the customer as a reward with a notification. The customer taps the notification and the reward page opens with a "Claim reward" button. When pressed, the amount reaches their wallet immediately
- The reward lapses if not claimed within 24 hours of the notification's arrival.
- The system spends the credit that expires first before the others, and spends refund credit last.
- The wallet shows each credit with its type and expiry date.
- Wallet credit is allowed in both write-in order payments: delivery and the products invoice.
- Promotional credit funded by a branch is spent only on orders from that branch, and is deducted from it only when actually used; if it expires unused, the branch pays nothing.
- A reward not claimed within 24 hours returns to the platform with a reversal entry, and "Compensation lapsed" appears in the order file; support can grant a new compensation, and the lapsed reward is not reactivated.

Acceptance criteria:
- The system does not spend promotional credit that is 15 days old.
- Spending starts with the credit nearest to expiry
- A reward not claimed within 24 hours lapses.
- A lapsed reward cannot be claimed, and its reversal entry appears in the ledger.
- Promotional credit funded by the Olaya branch is not spent on an order from the same merchant's Al Malqa branch.

Pages: C20 C23 A13 A14 A15

#### PAY-003 — Refund [Launch-critical]

Rules:
- The card portion returns to its method and the wallet portion returns to its type and expiry date; refund credit does not expire.
- If the customer chooses to convert a card refund to the wallet, it becomes permanent refund credit and is added directly; no reward-claim window.
- Every compensation granted by support arrives as a reward with a 24-hour claim window (PAY-002); a refund does not go through the reward.
- The reason, reference, and authorizer are recorded, and the time it takes to arrive and its status are shown.

Acceptance criteria:
- A refund does not lapse after 24 hours.
- No amount exceeding what was captured is refunded, and a cancelled hold is not re-issued as a capture.

Pages: C20 A18 A19

#### PAY-004 — Price and Fee Rule [Launch-critical]

Rules:
- The menu sale price = store price × (1 + the markup rate agreed with the merchant) (MER-002).
- Mart: store price × (1 + markup rate), default 5%.
- The restaurant percentage applies to the sale price minus the merchant's share of the discount; the discount funded by the platform does not reduce the merchant commission base.
- The customer service fee is calculated per PAY-021.
- The wallet is a payment method and does not reduce the fee base; a copy of the contract and settings is saved on the order.

Acceptance criteria:
- Wallet credit is not spent twice.
- No service fee is calculated on itself or on a tip.

Pages: C09

#### PAY-005 — Financial Record [Launch-critical]

Rules:
- The double-entry ledger is the only reference for money, and is built before any financial screen
- Every movement is recorded as a balanced two-sided entry. An entry is not edited; it is corrected with a reversing entry
- Before development, a chart of accounts and an entry template for each financial event are written. An explicit ruling is written for each lapse case: an unclaimed reward, expired cashback, and merchant-funded promotional credit
- The system checks daily that the sum of entries is zero
- Odoo receives what the system exports from the ledger
- Lapse ruling: what the platform funded (a reward not claimed within 24 hours, expired promotional credit, expired points) returns to it as revenue under the name "Lapsed amounts".

Acceptance criteria:
- An admin dashboard user cannot directly edit any party's balance
- The sum of entries for any day is zero
- When a reward lapses, an entry is recorded that specifies its destination

Pages: A18 A26

#### PAY-006 — Settlements and Payouts by Payment Splitting [Launch-critical]

Rules:
- The system shows a real-time statement for each branch, freelance driver and company; the merchant manager sees their branches' statements and their total.
- Split payment through Moyasar is the only method for merchant payouts: when an order is captured, the branch share is split into its wallet at Moyasar, and branch wallet balances appear in the admin dashboard; the platform does not hold merchant dues or pay them out itself; the platform instructs Moyasar to transfer the wallet to the bank only after the accountant's approval.
- There is no automatic payout. On the payout cycle date (a setting, weekly by default) the system shows whoever holds the "Payout approval" permission a list of all branch wallets, freelance driver dues, delivery companies, and deposit refunds, each at its net after deductions. For each line: approve the payout or reject it with a written reason. An approved line sends an order to Moyasar (branch wallet to its bank account) or a bank transfer to the driver's verified IBAN (STC Pay later, INT-014), and a rejected line remains a visible balance for the next cycle. The merchant and the driver see the status "Awaiting approval" before "In progress".
- Approved driver payouts are exported by the system as a bulk transfer file for the platform's bank, and Finance records the bank reference for each transfer so it becomes "Sent", or "Failed" with its reason so it returns as due.
- The holder of the "Approve payouts" permission approves after reviewing the account statement: one account, or selects several accounts and approves them together.
- Delivery companies' dues are paid to the company only
- Each transfer appears with its status, bank reference, and date. Statuses: in progress, sent, or failed
- The wallet balance of a branch whose new bank account is awaiting Finance approval is not paid out (MER-001).
- The branch's share is split when the order is captured after closing (not at hold), and equals its net in the statement: products minus the commission or contract fee, the payment fee, the tax on platform fees, and its share of offers; the product VAT inside its share is borne by the merchant and is not deducted by the platform (PAY-029).
- The share of a branch whose new bank account is awaiting Finance approval (MER-001) stays in its Moyasar wallet as "Due", is not paid out, and reaches it on the first payout date after approval.
- Penalties, loss charges, compensations, and refunds that occur after the order is split are recorded on its branch's dues account and deducted from its Moyasar wallet through the admin dashboard integration before the payout is approved; whatever the wallet balance does not cover is carried forward on the branch and deducted from its next shares, and it never touches the dues of another branch of the merchant.
- Each split is recorded in the ledger (PAY-005, PAY-005 appendix) with its gateway reference, and shows in the merchant's dues account as "In progress", then "Sent" or "Failed"; a failed one returns to being due, visible to Finance in A18, and is not counted as paid.
- Each branch has its own dues account and Moyasar wallet: each order's share is split into its branch's wallet, and the branch's deductions, penalties, and order refunds are deducted from its wallet alone.

Acceptance criteria:
- A failed transfer does not appear as paid
- No payout (branch, driver, company, or deposit refund) is sent without a recorded approval with the approver's name and time.
- A rejected line in the approval list is not sent, and appears in the next cycle with the rejection reason.
- Selecting 10 accounts and approving them sends 10 payouts and records an approval for each account.
- The statement shows all deductions, compensations, and offers
- A delivered order's branch share enters its wallet at Moyasar at capture, appears in the approval list in the next cycle, and does not reach its bank account before it is approved.
- Unregistered merchant, products at selling price 115, 10% contract percentage: 101.77 is split to them before the payment fee, and no product VAT is deducted from them (PAY-029).
- A merchant with two branches: a penalty on the Olaya branch is deducted from Olaya's dues and does not touch Al Malqa's dues.
- A 200 penalty on a branch whose wallet balance is 50 before the payout: 50 is deducted, and 150 is carried forward on the branch and deducted from its next shares.

Pages: D07 MD07 A18 A26

#### PAY-007 — Invoices and Purchase Orders [Launch-critical]

Rules:
- The products invoice is optional for menu and Mart, and mandatory for write-in orders.
- The purchase order shows the customer the products, delivery, service, tip, discounts, and payment source.
- Uploaded products invoices are saved linked to the order; the absence of an optional products invoice does not block Ready or delivery.
- The merchant statement and the monthly fees invoice are linked to orders, and a refund is corrected with a reversing entry and a linked credit note.

Acceptance criteria:
- The absence of a products invoice in a menu order is not an operations error or a delay alert.
- Write-in does not bypass the products invoice requirement.

Pages: C10 A18

#### PAY-009 — Restaurant and Shops Contracts [Launch-critical]

Rules:
- The two contract types: a per-new-customer fee at each branch (PAY-010), or a percentage agreed by the platform with the merchant.
- The contract percentage is always calculated on the selling price minus only the merchant's share of the discount.
- From an exempt menu link, the contract percentage or the per-customer contract fee is not deducted; the payment fee and the customer service fee remain.
- These two contracts are for restaurants and Shops with a menu; Mart and pharmacies use their own percentages (PAY-012).
- The restaurant or Shops contract stores the markup rate agreed with the merchant. The merchant's contract is the default for all its branches, and platform staff can customize the contract percentage or markup rate for a specific branch; each order saves its branch's contract.

Acceptance criteria:
- The contract type is one of percentage or per-customer-and-branch fee.
- An item with a selling price of 110 and a contract percentage of 10%: the platform deducts 11.
- Fee contract: no percentage is deducted from the merchant; only the customer fee is deducted (PAY-010).
- Changing a merchant's or a branch's markup rate changes sale prices for new orders only.
- A branch given a markup rate of 8% while its merchant's contract says 10%: its sale price = its store price × 1.08, and the other branches stay at 10%.

Pages: A06

#### PAY-010 — Contract Fee per Customer and Branch — Deducted from the Merchant [Launch-critical]

Rules:
- This is a fee on the merchant according to their contract type, independent of the customer service fee shown in the payment summary.
- The amount due is 2 SAR for an order whose total selling prices is below 25, and 5 SAR for 25 or more.
- Each customer and branch has an independent 365-day cycle from the first order; the cycle cap is 30 SAR.
- Actual = min(due, max(0, 30 − cycle total)).
- A new cycle starts at the first order after 365 days have elapsed, not by an automatic daily reset without an order.
- The fee is fixed at capture with a counter lock; a refund reverses only the actual fee.
- An exempt-link order carries no fee and does not increase the counter.
- The fee is deducted from the merchant on each order of the new customer until its total reaches 30 SAR at the branch, then nothing is deducted until its cycle ends.

Acceptance criteria:
- A total of 26 and a due amount of 5 gives 4.
- At 30 the fee is zero.
- Two concurrent orders do not exceed the cap of 30.
- A new customer at the branch orders at selling price 20, then 40, then 60: 2, then 5, then 5 are deducted.

Pages: MD02 MD06 MD07 MD13

#### PAY-011 — Payment Fee [Launch-critical]

Rules:
- A fixed fee deducted from restaurant and Shops merchants on every menu order: 2.5% of the product value after discount + 1 SAR; it does not include delivery, service fees, or the tip.
- It remains with the menu link exemption.
- Mart and pharmacies do not bear this fee; the actual Moyasar fee is recorded as a separate platform expense.
- The fixed 1 SAR is once per order when its products are captured; payment provider fees on the two write-in payments are recorded as a separate expense, without repeating the merchant's fixed fee.
- The fee is deducted whatever the payment method, even if the whole order was paid from the wallet; it is a fixed commercial fee, not a pass-through of the Moyasar cost.

Acceptance criteria:
- Products of 100 and delivery of 20 give a merchant fee of 3.50.
- Products of 105 and a discount of 20 give a merchant fee of 3.13 (2.5% of 85 + 1).
- Mart and pharmacy do not show the payment fee.
- A menu order with products of 105 paid entirely from the wallet: merchant fee 3.63.

Pages: MD02 MD07 MD13

#### PAY-012 — Mart and pharmacy percentages [Launch-critical]

Rules:
- The merchant commission percentage is configurable per Mart and pharmacy; the default is 5%, and 4% or other values can be set.
- The Mart basis is the store price, not the sale price after the markup rate.
- The Mart adds a 5% markup rate (default) inside the sale price, plus the general service fee per PAY-021.
- The pharmacy shows the original products invoice and a 5% service fee on products as separate items; the merchant percentage applies to the value of the products invoice.
- No payment fee applies to Mart or pharmacy.

Acceptance criteria:
- Store price 100, sale price 105, and merchant percentage 4%: the merchant commission is 4.
- A pharmacy products invoice of 100 with a customer service fee of 5 does not become a products invoice of 105.

Pages: C18

#### PAY-013 — Delivery fee [Launch-critical]

Rules:
- The delivery fee is a system-wide setting: a base fee that includes a set number of kilometers, a price per additional kilometer, a minimum, and a maximum.
- Distance from the store to the customer is measured by a method platform staff choose in the pricing setting: air distance (straight line) or road distance through Google Maps. The global setting is air distance by default, and each region and each city can choose its own method along with its prices.
- The distance and the measurement method are stored on the order when it is confirmed.
- An optional setting can be added for any region and any city (SYS-012): measurement method, base fee and its kilometers, extra kilometer price, the two limits, and the road factor. A city with no setting inherits its region's setting, and a region with no setting inherits the global setting.
- There is one fee for restaurants and Shops, and another fee for Mart and pharmacies.
- Pricing rules have a level, a priority, and an effective date: a specific branch first, then city, then region, then the global setting.
- The driver's pay has rules independent of the delivery fees charged to the customer, so delivery offers do not reduce it (PAY-014).
- Default values of the global setting: restaurants and Shops 9 SAR including 3 km, 1.5 SAR per additional kilometer, minimum 9 and maximum 25. Mart and pharmacies 12 SAR including 3 km, 1.5 SAR per additional kilometer, minimum 12 and maximum 30.
- A partial additional kilometer is rounded up: 2.3 km is counted as 3 km.
- If the measurement method is road distance and Google Maps cannot be called (outage, or the SYS-021 cap is reached) and there is no saved estimate for the route, the air distance multiplied by the road factor of the applicable setting (1.3 by default) is used, and the order records its method as "air × factor".

Acceptance criteria:
- When a city's fees change, no confirmed order changes.
- If the calculated fee exceeds the maximum, the system applies the maximum.
- The system does not apply a rule whose effective date is in the future before that date.
- A city with no specific setting takes the global setting.
- A restaurant 4.2 km away: 9 SAR for the first three kilometers + 2 × 1.5 = 12 SAR.
- A region set to road distance, and a city in it with no setting of its own: the city's orders are priced by road distance and the region's prices.
- A city set to air distance inside a region set to road distance: its orders are priced by air distance and the city's prices.
- Road method with Google Maps down, a restaurant 4 km away by air with a factor of 1.3: distance 5.2 km, so the fee is 9 + 3 × 1.5 = 13.50 SAR, and the saved method is "air × factor".

Pages: A09

#### PAY-014 — Driver earnings [Launch-critical]

Rules:
- The driver's pay comes from the full delivery fee before delivery offers, after excluding its tax and then the platform percentage.
- The platform percentage has a default, with a per-city and per-region exception and tier benefits; the order is: city, then region, then tier benefits, then the global setting.
- A delivery-company driver is outside this order: their earnings are calculated for their company using the platform percentage in the company's contract (FLT-002).
- Tip: its included 15% VAT is excluded and the remainder arrives in full with no platform percentage (CUS-010).
- The funder of a delivery offer bears the difference and does not reduce the driver's pay.
- When a driver is replaced, the pay and the tip go to the driver who delivered; any compensation to the first driver is a documented manual decision with no automatic deduction.
- The default platform percentage of the driver's pay is 10%.
- Driver pay is calculated from the delivery fee using the distance and measurement method saved on the order (PAY-013), so it follows the method of the order's region or city.

Acceptance criteria:
- An offer does not change the driver's base pay.
- A city exception overrides the tier percentage.
- Tier benefits in the percentage do not apply to a company driver.

Pages: D07

#### PAY-015 — Installments and pay later [Later]

Rules:
- The customer pays by installments or deferral through an approved provider (Tabby or Tamara) when available via Moyasar.
- The system shows the installment or deferral option only if the order amount reaches a minimum set by the platform.
- The installment minimum is 100 SAR.

Acceptance criteria:
- If the order is below the minimum, the system does not show the installment option.

Pages: C09

#### PAY-018 — Withdrawal before the payout date [Later]

Rules:
- A freelance driver can request to withdraw their due balance before the weekly payout date, limited to one request per day.
- With a fee set by the platform.
- The withdrawal requires approval by two people.

Acceptance criteria:
- The system rejects a second withdrawal request submitted on the same day.
- A driver who belongs to a company does not see the withdrawal option.

Pages: A18

#### PAY-019 — Commission packages [Later]

Rules:
- Defined commission packages exist, each package being a percentage in exchange for visibility benefits.
- A merchant is linked to a package instead of entering the percentage manually.
- Per-merchant customization remains available.

Acceptance criteria:
- When a merchant's package changes, no confirmed order changes.

#### PAY-020 — Fees based on driver availability [Later]

Rules:
- Platform staff temporarily enable a fee multiplier per city when drivers are short.
- The delivery fee after applying the multiplier does not exceed the city maximum defined in PAY-013.
- The customer is notified of it before ordering.

Acceptance criteria:
- Fees after applying the multiplier do not exceed the city maximum.
- The customer sees the fee increase before paying.

#### PAY-021 — Customer service fee [Launch-critical]

Rules:
- For menu and Mart: the default is 2.5% on products after discounts + delivery after the delivery offer (what the customer actually pays), before the service fee, excluding the tip.
- For write-in and pharmacy: 5% of products only; no additional general service fee on the delivery that is paid first.
- The fee appears as a separate line item; its basis in self-pickup has no delivery.
- Settings support values, city level, and exceptions; a new rollout does not change confirmed orders.
- For a medicine returned to the pharmacy, the 5% service fee is refunded along with its price (PHR-010).

Acceptance criteria:
- Products total 100, delivery 20, and tip 10 give a general service fee of 3.
- Write-in 100 and delivery 20 give a service fee of 5 only.
- Products 100 and delivery 12 with a free-delivery offer give a service fee of 2.50.

Pages: C09

#### PAY-022 — Branch statement and its monthly fees invoice [Launch-critical]

Rules:
- The monthly fees invoice is issued for each branch separately in the merchant's name with the branch details, and aggregates contract fees or the Mart and pharmacy percentage, payment fees, cashier fees, loss charges and penalties, with the details and source of each order; ad fees are not included, as they have the ad invoice when deducted (MKT-003).
- Exemptions and merchant type are applied to each order before aggregation.
- The default accounting tax is 15% on platform fees; it is shown separately and the sum of the lines matches the statement.
- Refund and reversal are entries linked to the original; accounting integration is through Odoo.

Acceptance criteria:
- An exempt linked order carries no contract fee.
- Mart and pharmacy carry no payment fees.
- The total of the month's lines equals the branch statement.
- Platform fees of 100 SAR in the month appear on the fees invoice as 100 + 15 tax = 115.
- An ad approved during the month does not appear on the fees invoice, and its deduction appears in the statement with the ad invoice number.

Pages: MD07 A16 A18

#### PAY-023 — Customer cards [Launch-critical]

Rules:
- The customer can save more than one card in settings, and choose one of them as the default.
- Cards are saved through Moyasar, and the system does not store their full numbers on the platform's servers.
- The customer deletes any card, or changes the default card.

Acceptance criteria:
- The default card appears first at payment.

Pages: C14 C17 C20

#### PAY-024 — Driver deposit [Launch-critical]

Rules:
- Each driver pays a 100 SAR deposit before their account is activated (a setting).
- Drivers who worked on the previous platform are activated without an upfront payment, and a 50 SAR deposit is deducted from the net of each of the first two weeks; whatever earnings do not cover is deducted from the following weeks until 100 SAR is complete, without suspending the driver.
- The deposit is a held amount separate from the dues account: it does not enter its balance, cannot be withdrawn, and penalties are not deducted from it during work.
- The driver gets the deposit back when the account is closed, after deducting any amounts owed by them.
- The driver pays the deposit electronically from the app through Moyasar.

Acceptance criteria:
- A driver who has not paid the deposit does not get their account activated.
- The dues account balance shown to the driver does not include the deposit.

Pages: D07 D10 D13 A10 A18

#### PAY-025 — Manual loss charges and penalties [Launch-critical]

Rules:
- There is no automatic loss charge or penalty; lateness, cancellation, or a warning does not create a deduction entry.
- A support agent decides manually, after reviewing the evidence, two separate things: the loss charge, which is a deduction equal to an actual loss from the party liable for it (merchant or driver), or recording it as an expense on the platform; and the penalty, which is a punishment in addition to any loss, on a merchant or driver.
- Every loss charge or penalty requires a linked order or report, a written reason, an amount, an actor, a date and evidence. Anything above the staff role's mandatory limit needs a second approval (ADM-043).
- The affected party receives a notification of the decision and the reason appears in their statement, and they can object within 7 days of the notification (SUP-006); reversing the decision is done with a reversal entry.
- The destination of the loss charge: refunding what the customer actually paid, or covering the loss; the destination of the penalty: the platform or compensation to the customer. Compensation is not a refund of an amount the customer paid.
- "Platform" is a possible liable party in a loss charge with a written reason, and is recorded as an expense on the platform.
- The loss charge and the penalty appear as two separate lines in the statement, each with its type; and "compensation" is added to the customer as a reward (PAY-002).
- The deduction remains in effect during the objection with the status "Under objection", and is reversed with a reversal entry if the objection is accepted.

Acceptance criteria:
- No financial entry is created merely because of a 10-minute delay.
- An agent whose role does not have loss charge and penalty permission cannot execute a deduction.
- The deduction is visible, explained, and traceable, and the loss charge is separate from the penalty.

Pages: D07 D11 MD07 A03 A04 A19

#### PAY-026 — Negative balance and driver deposit [Launch-critical]

Rules:
- Approved penalties and loss charges may produce a negative balance in the driver's dues account, which is deducted from their next payout.
- If the driver's dues account reaches −50 SAR or less (a setting), they enter "balance lockout" and receive no new tasks until they pay; there is no automatic ban because of lateness.
- The negative balance is not settled from the deposit during work; it is settled from it only when the account is closed, and the deposit is not returned before settlement.
- The driver pays the negative balance electronically from the app through Moyasar, and returns to receiving tasks immediately upon payment.

Acceptance criteria:
- A balance of −49 does not stop tasks, and a balance of −50 stops them.
- An unapproved deduction does not affect the balance.
- Account closure does not bypass balance settlement.

Pages: D01 D07 D10 A04 A10 A18

#### PAY-027 — Actual Moyasar fee [Launch-critical]

Rules:
- The system records the actual Moyasar fee of each payment operation as a separate expense in the ledger.
- The system subtracts the fee from the platform net and from the loyalty points basis.
- The system records the payment fee charged to the merchant (2.5% + 1) as platform revenue.
- A write-in order includes two payment operations, so the system records the fee of each operation.

Acceptance criteria:
- Reports show the platform net after subtracting the Moyasar fee.
- The daily reconciliation matches the recorded fee with the Moyasar statement.

Pages: A15 A18 A21

#### PAY-028 — Recalculation and partial refund [Launch-critical]

Rules:
- A single financial function recalculates the remaining items, the service fee, the contract, the payment fee, and the tax on the original order copy.
- A modification before collection (deleting an item or a substitute) reduces only the amount collected, with no reversal entries.
- A modification after collection refunds only the difference in the fee paid; a capped contract is recalculated using the counter locked when the order was collected (PAY-010), not a current counter changed by later orders.
- A reversal entry for the difference and for each party after collection; the refunded customer fee is returned to the counter of its original cycle and does not reduce the counter of a new cycle.
- A deleted item, a cheaper substitute, and a returned medicine all enter processing; an increase requires the customer's acceptance and payment of the difference before it is finalized.
- The fixed part of the payment fee applies once per order when product collection exists; it is refunded in a full cancellation per the refund decision, while the provider's actual cost remains an expense.

Acceptance criteria:
- Products lower by 25 give an amount due of 2 before the cap limit.
- The new fee does not increase the contract fee paid in a partial refund.
- Replaying the event does not repeat the refund.
- Deleting an item before collection does not create a reversal entry.

Pages: C12

#### PAY-029 — Calculation basis, tax, and rounding [Launch-critical]

Rules:
- A single table is prepared defining the basis on which each fee is calculated, reviewed with the accountant before coding, and then the examples are corrected accordingly.
- For each amount type it is determined whether tax is inside it or added on top of it, and on which invoice it appears.
- Amounts are calculated in halalas as integers, a half is rounded up, and each fee is rounded once.
- The tax of the monthly fees invoice equals the sum of the taxes of its lines.
- Points are rounded down.
- Everything the customer pays (products, delivery, and service fees) includes 15% tax: a delivery of 12 SAR, of which 10.43 is before tax.
- Platform fees on the merchant (contract fee or percentage, and payment fee) have 15% tax added on the fees invoice; advertising fees have 15% added on the ad invoice when deducted (MKT-003).
- The accountant approves the table before coding, and then the examples are declared final.
- Each merchant has an option platform staff set when adding it: registered for VAT or not registered; a registered merchant must have its VAT number (15 digits) entered. The option covers all merchants: restaurants, Shops, Mart and pharmacies.
- The merchant always issues its products invoice (the tax invoice under its VAT number if registered) at the full selling price, and the platform issues the platform invoice for the delivery fee and service fee.
- The markup percentage that goes to the platform (Mart, or a restaurant if the contract provides for it) is a fee on the merchant, with 15% added to it in the monthly fees invoice.
- The basis of each fee, its tax treatment and its entries are in the "PAY-005 appendix: chart of accounts, entries, and fee basis", which is approved.
- Changing the registration status or VAT number applies to new orders only; it is saved on each order and recorded in the audit log.
- All invoices the platform issues are issued automatically through Odoo on command from the system (INT-010), except the products invoice of a registered merchant, which the merchant issues itself.
- VAT on delivery fees, service fees, and the tip is on the platform in every case: it issues its invoice for them and remits it, and it is not deducted from the merchant, registered or not. Product VAT is always on the merchant, and the platform does not remit it on their behalf.
- Payment splitting is the only model (PAY-006): the product value reaches the branch's Moyasar wallet and never passes through the platform's account; so the platform issues the platform invoice for delivery fees, service fees, and the tip, and the fee invoice to the merchant only, while the merchant issues the products invoice and its VAT stays with them, registered or not.

Acceptance criteria:
- 1.525 becomes 1.53.
- Each row in "Financial operation examples" matches the calculation output in halalas.
- Registered merchant, same order: no product VAT is deducted; only the commission 11.50 and its VAT 1.73, so the merchant receives 101.77 before the payment fee.
- A "Registered" merchant cannot be saved without a 15-digit VAT number.
- Order with a 12 SAR delivery fee: its VAT of 1.57 appears on the platform invoice and is not deducted from the merchant's balance.
- Unregistered merchant, splitting active, products at selling price 115, 10% contract percentage: the platform issues no invoice for the products and does not deduct their VAT; it deducts only the commission 11.50 and its VAT 1.73, so the merchant receives 101.77 before the payment fee and bears the product VAT of 15 themselves.
- Unregistered merchant, splitting active: the merchant issues the products invoice, and the platform issues none for it.

Pages: A18 A22

#### PAY-031 — Liabilities (debts) in accounts [Launch-critical]

Rules:
- Every amount the platform has promised and not yet paid out is considered a liability on it. These liabilities appear ordered in a single table in "Accounts → Liabilities".
- The items: loyalty points at their value in SAR, promotional credit (referral prize, gifts, and cashback), pending referral prizes, compensation credit, rewards not yet received, refund credit, cancellation compensations due to the merchant, and the platform's share of ongoing offers.
- For each item it is shown: the balance, who funds it (the platform or the merchant), what is expected to be paid out, and what expires this month.
- When an item expires or lapses, the system records an entry that determines where the amount went.
- A weekly report of liability changes is issued.

Acceptance criteria:
- The total of liabilities matches the wallet and points balances in the ledger.
- Expired points leave the liabilities with an entry.
- A promotional credit funded by a merchant that expired unused leaves the liabilities with no deduction from the merchant.

Pages: A15 A18

### Appendix PAY-005: Chart of accounts, entries and fee basis

| Item | Value |
|---|---|
| Status | **Approved for development** by owner decision after the last review (29 October 2026). Meets the PAY-005 condition "chart of accounts before development" |
| Note | It is advisable for the business's accountant to review section 5 before the first VAT return, because the regulatory responsibility before ZATCA lies with the business |
| Date | 29 October 2026 |
| Reference | PRD 4.11. Section 5 records the approved accounting treatment decisions, and they take precedence over any earlier assumption in this file |

**General rules governing everything below:**
- The double-entry ledger is the single source of truth for money; every movement is a balanced entry, and no entry is edited but corrected with a reversing entry; and the sum of each day's entries is zero (PAY-005).
- Amounts are in halalas as integers, half is rounded up, and each fee is rounded once; points are rounded down (PAY-029).
- Everything the customer pays includes 15% VAT; and 15% is added to the platform fees on the merchant (PAY-029).
- All platform invoices and credit notes are issued automatically through Odoo connected to the Fatoora system (INT-010). The merchant always issues the invoice for its products, and the platform issues invoices for its fees only (owner decision, PAY-029).
- No payout to any party (branch or driver) except with the accountant's approval (owner decision).

---

#### 1. Chart of accounts

##### 1-A Assets

| Account number | Name | Type | Description |
|---|---|---|---|
| 1100 | Bank — the platform's current account | Asset | Receives Moyasar settlements for the platform's share, and funds the STC Pay business account. |
| 1110 | Moyasar — platform balance (clearing account) | Asset | The platform's share of each capture after the split, until settled to 1100. Reconciled daily with the Moyasar statement (PAY-027). |
| 1120 | Moyasar — branch wallet funds (restricted) | Asset | The contra account for account 2100: what Moyasar split into branch wallets and has not yet been transferred to their banks. It is not used for any platform purpose. **See the treatment in 1-F.** |
| 1130 | STC Pay — business account balance | Asset | Activated with the STC Pay integration (INT-014, later). At launch drivers are paid from 1100. |
| 1140 | Accounts receivable — branches (carried-forward balance) | Asset | Any penalty, loss charge, or refund not covered by the branch wallet balance, deducted from its next shares (PAY-006). A sub-account per branch. |
| 1150 | Accounts receivable — drivers (negative balance) | Asset | Reclassification of the debit balance in 2110 when preparing the statements (PAY-026). |
| 1160 | Input VAT | Asset | VAT on supplier invoices (including Moyasar fees if invoiced with VAT). |

##### 1-B Liabilities

| Account number | Name | Type | Description |
|---|---|---|---|
| 2100 | Branch dues (Moyasar wallets) | Liability | Each branch's share of its orders after deductions (PAY-006). A sub-account per branch; no branch affects another branch. |
| 2105 | Merchant dues — opening balances from the previous platform | Liability | The migrated merchant balance (TRN-001). Paid from the platform's bank (1100) in the first approval cycle, and does not pass through the Moyasar wallet. |
| 2110 | Driver dues | Liability | Delivery fee and tips minus penalties and loss charges (PAY-014, CUS-010, PAY-025). May become a debtor (negative balance, PAY-026). |
| 2115 | Delivery company dues | Liability | Later (FLT-002). |
| 2120 | Driver deposits held | Liability | 100 SAR per driver, separate from 2110; it is not withdrawn and no penalties are deducted from it while working (PAY-024). |
| 2130 | Customer wallet — refund balance | Liability | Does not expire (PAY-002, PAY-003). |
| 2131 | Customer wallet — compensation balance | Liability | Expires after 14 days (PAY-002). |
| 2132 | Customer wallet — platform-funded promotional credit | Liability | The referral prize, gifts, cashback and redeemed points; 14 days (PAY-002, PAY-031). |
| 2133 | Granted rewards not yet claimed | Liability | Compensation awaiting a press on "Claim reward" within 24 hours (PAY-002, PAY-031). |
| 2134 | Pending referral prizes | Liability | On hold until the report window ends (MKT-013, PAY-031). |
| 2140 | Loyalty points liability | Liability | The SAR value of points at the conversion rate in effect for the city or period (MKT-010, PAY-031). |
| 2150 | VAT — output tax payable | Liability | VAT on what the platform has actually invoiced. |
| 2151 | Output VAT — merchant fees not yet invoiced | Liability | A tracking-only sub-account of 2150: VAT on merchant fees deducted at split. It is remitted in the return for the period in which it was deducted (the deduction is a payment, and payment is a tax point), and is moved to 2150 when the monthly fees invoice is issued (PAY-022; Section 5, item 6). |
| 2160 | Customer refunds in progress | Liability | A post-capture refund that was ordered and not yet confirmed by Moyasar (PAY-003). |
| 2170 | Payouts in progress | Liability (intermediary) | Approved payouts sent to Moyasar or STC Pay whose confirmation has not arrived; closed on "Sent" or reversed on "Failed" (PAY-006). |
| 2180 | Ad and campaign revenue received in advance | Liability | The unperformed portion of an ad period that extends past the end of the month; recognized as revenue by days (MKT-003; section 5 item 19). |
| 2190 | Amounts captured on open orders | Liability | The platform's net share of an order auto-captured at 24 hours while still open; it becomes revenue at closing or is refunded by support decision (Section 5, item 10). |

##### 1-C Equity

| Account number | Name | Type | Description |
|---|---|---|---|
| 3100 | Capital | Equity | — |
| 3200 | Retained earnings | Equity | — |
| 3900 | Migrating opening balances from the old platform | Equity (intermediate) | The contra account for wallet balances transferred manually; the accountant settles it against cash or receivables transferred from the old platform's books, and it must reach zero (owner's decision). |

##### 1-D Revenue (all net of tax)

| Account number | Name | Type | Description |
|---|---|---|---|
| 4100 | Customer service fee | Revenue | 2.5% menu and Mart, 5% write-in and pharmacy (PAY-021). |
| 4110 | Delivery fee | Revenue | The amount before tax (12 → 10.43). Recorded gross, and the driver fee is an expense in 5100 (section 5 item 8). |
| 4115 | Tip | Revenue | Net tip before VAT (10 → 8.70). The platform invoices it, so it is its revenue, and its counter-entry is 5105 (Section 5, item 9). |
| 4190 | Discounts on platform services | Contra revenue (negative) | Platform discount on its own fees (free delivery, service fee discount): reduces revenue and is not treated as an expense (Section 5, item 5). |
| 4120 | Contract percentage commission — restaurants and Shops | Revenue | A percentage of the selling price minus the merchant's share of the discount (PAY-009, owner decision). |
| 4121 | Contract fee per customer and branch | Revenue | 2 or 5 SAR, capped at 30 per 365-day cycle (PAY-010). |
| 4122 | Mart and pharmacy commission | Revenue | 5% by default (PAY-012). |
| 4130 | Payment fee borne by the merchant | Revenue | 2.5% of products after discount + 1 SAR (PAY-011, PAY-027). |
| 4140 | Markup rate fee — Mart | Revenue | The markup is a fee on the merchant, with 15% added on top, in the monthly fee invoice (section 5 item 2). |
| 4141 | Markup rate fee — restaurants with a contract stating it belongs to the platform | Revenue | The same treatment, only when the contract states it (section 5 item 3). |
| 4150 | Ads and paid placements | Revenue | MKT-003. |
| 4151 | Store customer campaigns | Revenue | MKT-005. |
| 4152 | Double points bought by the merchant | Revenue | MKT-010; the price is a setting not specified in the file. |
| 4153 | Cashier fee | Revenue | Listed in the fees invoice (PAY-022); the price is not specified in the file. |
| 4160 | Penalties that go to the platform | Revenue | PAY-025. |
| 4170 | Forfeited amounts | Revenue | An unclaimed reward, expired promotional credit, or expired points funded by the platform (PAY-005). |

##### 1-E Expenses

| Account number | Name | Type | Description |
|---|---|---|---|
| 5100 | Driver fees | Expense | Full delivery fee before offers, excluding VAT, minus the platform's 10% share (PAY-014). |
| 5105 | Driver tips | Expense | The net tip due to the driver, against 4115. |
| 5110 | Actual Moyasar fees | Expense | Per payment transaction; two transactions in write-in and pharmacy (PAY-027). |
| 5120 | Platform-funded discounts and offers | Expense | The platform's share of product offers, delivery offers and coupons (MKT-007, PAY-004). |
| 5130 | Customer compensations | Expense | Compensation rewards funded by the platform (PAY-002, PAY-025). |
| 5140 | Platform-funded promotional credits | Expense | Referral prizes, gifts and cashback (PAY-002, MKT-013). |
| 5150 | Loyalty points expense | Expense | MKT-010. |
| 5160 | Loss charges and losses on the platform | Expense | When the responsible party is "Platform" for a written reason (PAY-025). |
| 5170 | STC Pay transfer fees | Expense | If any; not specified in the file. |

##### 1-F Memorandum accounts (memo — off balance sheet)

| Account number | Name | Type | Description |
|---|---|---|---|
| 9100 / 9101 | Customer card holds / counter-entry | Memo | An amount held on the customer's card that has not been captured; not platform money (PAY-001). |
| 9200 / 9201 | Branch-funded promotional credit / counter-entry | Memo | Deducted from the branch only when it is used, and nothing is charged to it if it expires (PAY-002, PAY-031). |

**Treatment of branch wallets at Moyasar (1120 / 2100) — approved:**
- **Approved:** recognize them on the balance sheet: a restricted asset (1120) offset by a liability (2100). Reason: the platform controls money leaving the wallet (no payout without its accountant's approval, owner decision), and deducts penalties and refunds from it (PAY-006); this brings it close to "control", and enables full daily reconciliation with Moyasar and the zero-balance entries check (PAY-005).
- **Reconsidered only** if the Moyasar contract explicitly states that the wallet is the merchant's legal property and that the platform is only an agent (PAY-006: "The platform does not hold merchants' dues"). In that case 1120/2100 are replaced by two memo accounts, and 1140 remains for the migrated balances.
- In both cases: the product value is not platform revenue; the platform is an agent for the products (PAY-029).

---

#### 2. Entry templates for each financial event

##### 2-A Reference numeric example (used in the entries below)

A restaurant on a 10% percentage contract, VAT-registered or not (the VAT on products is its responsibility in both cases, PAY-029). Selling price 105, delivery 12, service 2.5%, tip 10, paid entirely by card.

| Item | Account | Amount |
|---|---|---|
| Customer pays | 105 + service 2.93 + delivery 12 + tip 10 | **129.93** |
| 10% commission of 105 | + its 15% tax | 10.50 + 1.58 |
| Payment fee 2.5%×105 + 1 | + its 15% tax | 3.63 + 0.54 |
| **Branch share to its wallet** | 105 − 10.50 − 1.58 − 3.63 − 0.54 | **88.75** |
| Delivery 12 | Net + VAT | 10.43 + 1.57 |
| Service 2.93 | Net + VAT | 2.55 + 0.38 |
| Tip 10 | For the driver + VAT | 8.70 + 1.30 (CUS-010) |
| **Platform share at Moyasar** | 129.93 − 88.75 | **41.18** |
| Driver fee | 10.43 − 10% (1.04) | 9.39 (file example L285) |
| Driver tip | Net tip | 8.70 (received in full, CUS-010) |
| **What remains for the platform** | 41.18 − tax 5.37 − driver 18.09 | **17.72** before the actual Moyasar fee |

##### 2-B Entries table

| # | Event | Debtor | Creditor | Note |
|---|---|---|---|---|
| 1 | Amount hold at order | 9100 Holds (129.93) | 9101 Holds contra (129.93) | Memo only; no financial entry (PAY-001). |
| 2 | Full hold release (cancellation within the window / no driver) | 9101 | 9100 | No financial entry (PAY-001, PAY-003). |
| 3 | Edit before capture (delete an item, cheaper substitute, partial refund before capture) | 9101 for the difference | 9100 for the difference | Reduces only the captured amount, with no reversing entries (PAY-028). |
| 4 | Capture and splitting when the order closes | 1110 Moyasar—Platform 41.18; 1120 Branch wallets 88.75; 9101 (129.93) | 2100 Branch 88.75; 4120 Commission 10.50; 4130 Payment fee 3.63; 2151 Tax on merchant fees 2.12; 4110 Delivery 10.43; 4100 Service 2.55; 2150 Tax (1.57+0.38+1.30) 3.25; 4115 Tip 8.70; 9100 (129.93) | The platform's simplified invoice for the order (delivery, service, and tip) is issued at capture (INT-010). The merchant issues its products invoice. Fees contract: 4121 instead of 4120. Mart: 4122 + 4140 with their tax in 2151, and no 4130 (PAY-012). |
| 5 | Automatic capture after 24 hours with the order still open | Same as entry 4, for the full held amount | Same as entry 4, except that platform revenues (4100, 4110, 4115, 4120…) are recorded in 2190 until closing; VAT goes to 2150 immediately | At closing: debit 2190, credit the revenue accounts. A support decision after that is executed as a refund (entry 8) from 2190 (Section 5, item 10). |
| 6 | Escalating the status to the supervisor at hour 18 | — | — | No entry; audit log only (owner decision). |
| 7 | Actual Moyasar fee | 5110 Moyasar fees; 1160 Input tax (if any) | 1110 Moyasar—Platform | Per transaction; reconciled daily against the Moyasar statement (PAY-027). |
| 8 | Partial or full refund after capture | The revenue and tax affected by the difference (4100, 4110, 4120/4121/4122, 4130, 2150, 2151); 2110 for the refunded tip; 2100 for the refunded branch share, or 5160 if the platform is responsible | 2160 Refunds in progress | A single function recalculates on the original order snapshot; the locked contract fee counter (PAY-028, PAY-010). A linked credit note is issued (PAY-007, INT-010). If delivery is refunded, the tip is refunded in full (CUS-010). Role limit: support agent 50, supervisor 200 (owner decision). |
| 8a | Moyasar refund confirmation | 2160 | 1110 Moyasar—Platform; 1120 Branch wallets (with the branch share) | The branch share is deducted from its wallet (PAY-006). |
| 8b | Refund to the customer's wallet instead of the card | 2160 | 2130 Refund credit | At the customer's choice; does not expire and has no claim window (PAY-003). |
| 9 | Platform-funded discount on products (file example: discount 20, platform 12, merchant 8) | 5120 Platform discounts 12 | (part of the capture entry: what the customer paid decreases by 12 and the branch share remains calculated on 97) | Does not reduce the commission base (PAY-004, PAY-009, example L282). The merchant invoices the customer for 97 (what the customer paid + what the platform paid on their behalf), and its VAT is on 97 (section 5, item 4). |
| 9a | Platform discount on its own fees (free delivery, service discount) | 4190 Discounts on platform services | (what the customer paid decreases) | The platform invoice shows the full fee and the discount line, with VAT on the net (Section 5, item 5). The driver fee is not affected (PAY-014). |
| 10 | Coupon or offer funded by the merchant | — (no expense on the platform) | 2100 is recorded at its share after the discount | Reduces the commission base by the merchant's share (PAY-009). |
| 10a | Using branch-funded promotional credit | 2100 Branch (for the amount used); 9201 | 9200; (offset by the reduction in the amount collected from the customer) | Deducted from it only on use; expiry has no effect on it (PAY-002, PAY-031). |
| 11 | Payment from the customer's wallet (platform-funded) | 2130 / 2131 / 2132 by type | Replaces part of 1110 in the capture entry | The wallet is a payment method that does not reduce the fee base; nearest to expiry first and refund last (PAY-002, PAY-004, PAY-011). |
| 12 | Tip: driver accrual | 5105 Driver tips 8.70 | 2110 Driver 8.70 | The revenue and tax in the capture entry (4115, 2150). The platform issues the invoice and remits the tax (CUS-010, PAY-029). A post-delivery tip: a separate payment with a separate simplified invoice and the same two entries + the Moyasar fee. |
| 13 | Driver fee accrual at closing | 5100 Driver wages 9.39 | 2110 Driver 9.39 | Of the full delivery fee before offers (PAY-014). |
| 14 | Approve a driver payout and send it | 2110 Driver | 2170 Payouts in progress | **With the accountant's approval** (PAY-006). At launch, a bank transfer to the driver's approved IBAN, and STC Pay later (INT-014). No payout for a zero or negative net. |
| 14a | Record the transfer's bank reference | 2170 | 1100 Bank (and 1130 after STC Pay is enabled) | The bank reference or the STC Pay transaction number is stored. |
| 14b | Funding the STC Pay account (after it is activated) | 1130 | 1100 Bank | — |
| 15 | Approve a branch wallet payout and send it to Moyasar | 2100 Branch | 2170 Payouts in progress | **With the accountant's approval**, then the instruction is sent to Moyasar (owner decision, differs from PAY-006). No payout to a new, unapproved bank account (MER-001). |
| 15a | Moyasar payout confirmation | 2170 | 1120 Branch wallets | — |
| 16 | Accountant rejects the payout | — | — | No entry; the balance remains due in 2100/2110 with the rejection reason in the audit log. |
| 17 | Payout failure after sending | 2170 | 2100 or 2110 | A failed transfer is not counted as paid and returns as a visible due amount for Finance (PAY-006, INT-014). |
| 18 | Settling the platform's share from Moyasar to the bank | 1100 Bank | 1110 Moyasar—Platform | — |
| 19 | Loss charge on a merchant (actual loss) | 2100 Branch (or 1140 for what the wallet balance does not cover) | 2160 if the outcome is a refund to the customer; or 5160 if it covers a loss borne by the platform | Manual, with a reason and evidence, and linked to an order (PAY-025). Compensation, not consideration for a supply: outside the scope of VAT (section 5, item 7). |
| 20 | Penalty on a merchant | 2100 Branch (or 1140) | 4160 Penalties (platform outcome); or 2133 compensation reward for the customer | Out of VAT scope; shown in the branch statement and as a non-taxable line in the monthly fees invoice (PAY-022). |
| 21 | Penalty or loss charge on a driver | 2110 Driver (may become negative) | 4160; or 2133 compensation for the customer; or 5160/2160 for the loss charge | At −50 the driver is stopped (PAY-026). Not settled from the deposit while working. |
| 22 | Accepting the objection | Reverse the original entry with the same accounts and amounts | — | A reversing entry linked to the original; the deduction remains in effect during the objection (PAY-025). |
| 23 | Platform compensation to a customer (grant a reward) | 5130 Compensation | 2133 Unclaimed rewards | Subject to the role limit (PAY-025). |
| 23a | Claiming the reward within 24 hours | 2133 | 2131 Compensation credit | PAY-002. |
| 23b | Reward forfeiture / expiry of platform-funded promotional credit | 2133 or 2131 or 2132 | 4170 Forfeited amounts | The forfeiture rule is in PAY-005. |
| 24 | New driver deposit through Moyasar | 1110 Moyasar—Platform | 2120 Held deposit | Before activation (PAY-024). |
| 24a | Existing driver deposit in installments | 2110 Driver | 2120 Held deposit | 50 SAR from the net of each of the first two weeks; whatever earnings do not cover is deducted from the following weeks until 100 is reached, and the driver keeps working (Section 5, item 17). |
| 24b | Driver pays off their negative balance through Moyasar | 1110 | 2110 | PAY-026. |
| 24c | Account closure and deposit refund | 2120 Deposit | 2110 Driver | The negative balance is settled first, then the net is paid out via entry 14 with approval (PAY-024, PAY-026). |
| 25 | Campaign or ad invoice at approval | 2100 Branch (or 1140) for the amount + tax | 4151 Campaigns or 4150 Ads; 2150 tax 15% | A separate tax invoice immediately through Odoo, outside the fees invoice (MKT-003, MKT-005). File example: 100 + 15 = 115. |
| 25a | Refund of the unserved portion of an ad | 4150; 2150 | 2100 Branch | A credit note linked to the ad invoice (MKT-003). |
| 26 | Earning loyalty points (when the report window ends) | 5150 Points expense | 2140 Points liability | From the platform net after the offer funder, the coupon, and the Moyasar fee; a base ≤ 0 gives no points (MKT-010). Valued at the payout rate in effect on the entry date (section 5, item 11). |
| 26a | Points withdrawal on refund | 2140 | 5150 | MKT-010. |
| 26b | Redeem points | 2140 | 2132 Promotional credit | Redemption converts to promotional credit used as a payment method (entry 11). From 500 points. |
| 26c | Points expiry (12 months) | 2140 | 4170 Forfeited amounts | PAY-005, PAY-031. |
| 27 | Referral prize | 5140 | 2134 Pending → when the report window ends: 2134 to 2132 | Withdrawn on order refund by reversing the entry (MKT-013). |
| 28 | Branch monthly fees invoice | 2151 | 2150 | Transfer of the month's fees VAT when the invoice is issued; invoice VAT = the sum of its line VAT amounts (PAY-022, PAY-029). |
| 29 | Opening balance entry from the old platform | 3900 Balance migration | 2130 (customer); 2110 (driver); 2105 (merchant) | Entered manually by the finance team from an approved statement with a second approver (TRN-001). |
| 29a | Transfer of the corresponding cash from the previous platform's account | 1100 Bank | 3900 Balance migration | At the total of the transferred balances; 3900 reaches zero. Any difference is investigated and is closed only by an approved entry (section 5 item 12). |
| 29b | Paying the merchant's opening balance | 2105 | 2170 → then 1100 on confirmation | In the first approval cycle, a bank transfer from the platform's account (not through the Moyasar wallet). |

---

#### 3. Entry test figures (from the file examples L279–L287)

| Example | Expected result in the ledger |
|---|---|
| Mart: store price 100, markup 5%, delivery 12 | Customer 119.93; 4122 = 5; 4140 = 5; 2151 = 1.50; 2100 = 93.50 (95 before platform fee tax, as in L279). The merchant invoices the customer at 105 |
| Restaurant 10%, selling price 105 | 4120 = 10.50; 4130 = 3.63 |
| Restaurant discount 20 (merchant 8, platform 12) | Commission base 97; 4120 = 9.70; 5120 = 12; 4130 = 3.13 |
| Unregistered restaurant, selling price 115, 10% | 4120 = 11.50; 2151 = 1.73; 2100 = 101.77 before the payment fee |
| Driver, delivery 12 | 4110 = 10.43; 5100 = 9.39 |
| Tip 10 | 4115 = 8.70; 2150 = 1.30; 5105 = 8.70; 2110 = 8.70 |

---

#### 4. Fee basis table (G-A2)

| Fee | What it is calculated on | Tax inclusive or exclusive | Who issues the invoice | In any invoice | Reference |
|---|---|---|---|---|---|
| Product price | Selling price after discount | Included, and always borne by the merchant | Merchant | Products invoice from the merchant | PAY-029, owner decision |
| Delivery fee | Distance: restaurants 9 SAR covers 3 km + 1.5/km (9–25); Mart and pharmacy 12 SAR covers 3 km + 1.5/km (12–30) | Included (12 → 10.43 + 1.57) | Platform | Platform invoice for the order at capture | PAY-013, PAY-029, INT-010 |
| Customer service fee — menu and Mart | 2.5% of products after discounts + the delivery actually paid, excluding the tip and before service | Included | Platform | Platform invoice for the order | PAY-021, PAY-029 |
| Customer service fee — write-in and pharmacy | 5% of products only | Included | Platform | Platform invoice for the order (second payment) | PAY-021, PAY-012 |
| Tip | The amount the customer chooses | Included (÷ 1.15) | Platform | Platform invoice for the order; the tip after delivery with a separate simplified invoice | CUS-010, PAY-029 |
| Contract percentage commission — restaurants and Shops | The agreed percentage × (selling price − the merchant's share of the discount); the platform's share does not reduce it | 15% VAT applies | Platform | Branch monthly fees invoice (deducted at split) | PAY-009, PAY-022, PAY-029, owner decision |
| Contract fee per customer and branch | 2 SAR if the total of selling prices is < 25, and 5 SAR from 25; cap of 30 per 365-day cycle | 15% VAT applies | Platform | Monthly fee invoice | PAY-010, PAY-022 |
| Mart commission | 5% by default of the store price (not the selling price) | 15% VAT applies | Platform | Monthly fee invoice | PAY-012, PAY-022 |
| Pharmacy commission | 5% by default of the products invoice value | 15% VAT applies | Platform | Monthly fee invoice | PAY-012, PAY-022 |
| Payment fee | 2.5% of products after discount + 1 SAR per menu order; no delivery, service or tip; no Mart or pharmacy; whatever the payment method | 15% VAT applies | Platform | Monthly fee invoice | PAY-011, PAY-022, PAY-029 |
| Markup rate fee — Mart | 5% by default of the store price | 15% VAT applies (fee on the merchant). The full selling price to the customer is in the merchant's invoice with its VAT | Platform (the fee); merchant (the selling price) | Monthly fee invoice | PAY-004, PAY-012 |
| Markup rate fee — restaurants | Per the contract | If it belongs to the platform: like Mart (a fee with 15% on top). If it belongs to the merchant: no fee | The platform, if it belongs to it | Monthly fee invoice | PAY-009 |
| Ads and placements | Placement, city and duration price | 15% VAT applies | Platform | A separate ad invoice at approval and deduction | MKT-003 |
| Store customer campaigns | Zone or city price (zero is free) | 15% VAT applies | Platform | A separate invoice, like an ad, after approval | MKT-005 |
| Double points are bought by the merchant | The price is a setting (ADM) | 15% VAT applies | Platform | Monthly fee invoice | MKT-010 |
| Cashier fee | Not specified in the file | 15% VAT applies (like platform fees) | Platform | Monthly fee invoice | PAY-022 |
| Loss charge on a merchant | Amount of the actual loss | Out of VAT scope (compensation) | No tax invoice | Non-taxable line in the branch statement and the fees invoice | PAY-025, PAY-022 |
| Penalty on a merchant | The amount support decides | Out of VAT scope (contractual penalty) | No tax invoice | Non-taxable line in the branch statement and the fees invoice | PAY-025, PAY-022 |
| Loss charge and penalty on a driver | The loss or the decided amount | Out of VAT scope | No invoice | Driver statement | PAY-025 |
| Platform percentage of the driver's fee | 10% of the full delivery before offers, excluding tax | No VAT: a method of calculating the fee, not a charge | No invoice | Driver statement | PAY-014 |
| Driver deposit | 100 SAR fixed | Out of VAT scope (assumption: refundable deposit) | No invoice; a receipt | — | PAY-024 |
| Actual Moyasar fee | Per the Moyasar contract | Input VAT if Moyasar invoices it | Moyasar | Moyasar's invoice to the platform | PAY-027 |
| Transfer fees (Moyasar to bank, STC Pay) | Per the two contracts | Input VAT if invoiced | Provider | Provider's invoice to the platform | Borne by the platform (5110, 5170) unless the merchant's contract states otherwise |

---

#### 5. Approved accounting treatment decisions (29 October 2026)

All open questions in the draft were resolved in the latest review. Reference: the VAT Law and its Implementing Regulations, and financial reporting standards (principal versus agent, and revenue recognition on satisfaction of the performance obligation).

| # | Issue | Approved decision | Reason |
|---|---|---|---|
| 1 | Branch wallets at Moyasar | Within the budget: restricted asset 1120 against liability 2100, disclosed as restricted | The platform controls money leaving (no payout without its accountant's approval) and deducts from it, so it is under its control; full daily reconciliation with Moyasar achieves this |
| 2 | Markup percentage in Mart | The merchant is the principal in selling the products and invoices the customer at the full selling price (105) with its tax. The markup is a fee on the merchant (4140) with 15% added on top in the monthly fee invoice together with the commission | The invoicing chain stays the same: the merchant sells, and the platform invoices its services to the merchant. Matches the L279 example: 95 before platform fee tax |
| 3 | Markup in restaurants when the contract gives it to the platform | Same as item 2 (4141). When it belongs to the merchant there is no platform entry | Consistency |
| 4 | Platform-funded discount on products | The merchant invoices the full consideration (what the customer paid + what the platform paid on their behalf = 97 in the example) with its tax on it. The platform's share is a marketing expense 5120 with no input tax | What a third party pays on the customer's behalf is part of the consideration for the supply |
| 5 | Platform discount on its own fees (free delivery, service discount) | A revenue reduction (4190), not an expense. The invoice shows the full fee and the discount line, and tax is on the net | A discount on the platform's own supply reduces the consideration |
| 6 | VAT point for merchant fees | At deduction (treated as payment), so it is remitted in the return for the deduction period. A consolidated monthly tax invoice per branch is issued during the following month, and 2151 is a tracking sub-account of 2150 | Accrual at the earliest of supply, invoice, or payment |
| 7 | Loss charges and penalties | Out of VAT scope (compensation for damage or a contractual penalty, not consideration for a supply). Shown as non-taxable lines in the statement and the fees invoice, and no invoice for the driver | No supply corresponds to it |
| 8 | Delivery | Gross: the platform is the principal in the delivery service (invoices it in its own name, 4110), and the driver fee is an expense (5100). The 10% rate is a way of calculating the fee, not a fee or an invoice | The platform sets the price and bears responsibility for the service toward the customer |
| 9 | Tip | Gross, like delivery: revenue 4115 at its net, and expense 5105 at the same amount for the driver. A post-delivery tip gets a separate simplified invoice | As long as the platform invoices it with its VAT, it is the platform's supply; the net effect on profit is zero |
| 10 | Automatic capture at 24 hours with the order still open | Tax is due immediately (payment). Platform revenue is deferred in 2190 until closing or a support decision. The branch share is split at capture as in PAY-006 | Revenue is not recognized before the service is fulfilled |
| 11 | Loyalty points | Liability when the report window ends (when the points become due) at the conversion rate in effect that day. Redemption converts to promotional credit 2132, and expiry to 4170 | Before the window ends, points may be withdrawn by an order refund |
| 12 | Opening balances | Recorded against 3900, and the corresponding cash is moved from the previous platform's account to 1100 against 3900 until it reaches zero. The merchant's opening balance in 2105 is paid from the platform's bank in the first approval cycle and does not pass through the Moyasar wallet | The Moyasar wallet is funded from captures only |
| 13 | Payment fee (2.5% + 1) on full refund after capture | Refunded to the merchant with a credit note, and the actual Moyasar fee remains an expense on the platform (5110) | A fee against an order whose supply was cancelled |
| 14 | Two-payment write-in and pharmacy orders | A simplified platform invoice for each captured payment | Accrual at each payment |
| 15 | Moyasar-to-bank transfer fees and STC Pay fees | Borne by the platform (5110, 5170) unless the merchant's contract states otherwise | No provision charges it to the merchant or the driver |
| 16 | Rejected payout | Remains due in 2100 or 2110 and appears in the next cycle with the rejection reason; no entry | Rejection does not change the liability |
| 17 | Installment payment of former drivers' deposits | 50 SAR from the net of each of the first two weeks. Whatever earnings do not cover is deducted from the following weeks until 100 is reached, and the driver keeps working | Accommodation without suspension, with the deposit completed |
| 18 | Cashier fee and double points price | Two settings in the admin dashboard, with 15% on top, in the monthly fee invoice | A platform fee like the others |
| 19 | Prepaid ads | Invoice and deduction at approval; revenue is recognized by day, and whatever extends past month-end is deferred in 2180 | Recognizing revenue over the service period |

**Accounting operating controls (binding for development):**
- Daily balance check: total debits for each day = total credits, and any difference is a red alert in A18 (PAY-005).
- Daily reconciliation: 1110 and 1120 against the Moyasar statement, and 1130 against the STC Pay statement; every difference stays open until it is resolved with an entry.
- 3900 must reach zero before the first month after launch is closed.
- A month is not closed while 2170 has payouts older than 7 days without a comment.
- Every manual entry (opening, loss charge, penalty, reversing) with a reason, a reference, and a second approver above the role limit (ADM-002, ADM-043).

### Mart catalog (CAT)

#### CAT-001 — Mart product inheritance [Launch-critical]

Rules:
- The hub copy and the grocery customization values are stored separately; the customization takes priority as long as the central product is active.
- When the central product is deactivated, it stops in all groceries even if it is enabled locally.
- The shared catalog adds its later products to the grocery disabled, unless the "Enable additions automatically" option is on (MER-010); removing the catalog subscription does not delete the product's sales record.
- Central deactivation prevents display, adding, and new purchase; a confirmed order keeps its copy and handles out-of-stock items per the customer's choice.

Acceptance criteria:
- The customization is not erased when the hub is updated.
- A local activation cannot bypass a central deactivation.

Pages: M07 A07

### Merchant and branches (MER)

#### MER-001 — Merchant and its branches [Launch-critical]

Rules:
- The system saves the merchant, its branches, contracts, bank accounts and users; each branch is run as if it were an independent store in operations and money.
- Each branch has its location, city, hours, preparation time, minimum and zone, a payout bank account (defaults to the merchant's account), and its own cashier integration and devices.
- Changing the bank account requires validation and a log; activation is by platform decision based on completeness of the operational data.
- No mandatory compliance requirements or licenses in this PRD except HRDF (Hadaf) and reporting to the Transport General Authority (TGA) (REG-007).
- A finance staff member approves the new bank account of the merchant or a branch after matching its holder's name with the business name; the affected branch's payouts stop until approval, and a notification of the change reaches the merchant manager's mobile.
- Merchant activation requires: branches with their locations and hours, the contract, the bank account, and a menu or catalog with products that have prices.
- Business data includes VAT registration: registered with its VAT number, or not registered (PAY-029).

Acceptance criteria:
- A branch manager does not see another branch's finances.
- The bank change is visible in the audit log.
- A new unapproved bank account stops the payout of the branch it belongs to, and no money is sent to it.

Pages: MD15 A05 A06

#### MER-002 — Menu, prices, and permissions [Launch-critical]

Rules:
- Each product in each branch has a store price entered by the merchant and a sale price set by the platform: either manually per product, or by a markup rate on the merchant's or branch's whole menu, so the sale price = store price × (1 + markup rate) in the branch's contract (PAY-009); a manual price takes precedence over the rate. The customer sees only the sale price and never sees the store price, the store price is used in reports and analytics, the merchant sees both prices, and all calculations are on the sale price.
- Modes for the merchant's edits to the store price: prohibited, needs review, within a percentage, full; price limits are measured against the approved price (the last price approved by the platform), not against the merchant's last edit.
- The price limits are an absolute percentage for raising or lowering; an edit outside it goes to review, and prohibited does not allow a price edit.
- The approved price remains for the customer until an edit that needs review is accepted; the preview shows the store price and the sale price together.
- The merchant's permission is set by the platform, then the merchant manager distributes permissions to merchant staff within its limits.
- A new product for restaurants and Shops follows the price permission mode: it appears immediately in "full" and "within a percentage", and goes to review in "needs review".
- The menu is shared by the merchant and inherited by each branch, and each branch has its own store price, availability and hours, as with groceries (MER-010); changing a price in one branch does not change it in another.

Acceptance criteria:
- Two edits do not each accumulate a 5% raise beyond the price limits.
- An employee does not exceed the merchant's permission ceiling.
- A product with a store price of 30 and its branch's markup rate of 10%: its sale price is 33; the customer sees 33 and does not see 30, and fees and the percentage are calculated on 33.
- The merchant sees the store price and the sale price of each product in their app and dashboard, and the store price is not shown to the customer on any page.
- Raising a product's store price in the Olaya branch does not change its price in the Al Malqa branch, and the product stays in both branches' menu.
- A menu with a 10% markup, and a product with a store price of 30 for which a platform employee entered a manual sale price of 35: the customer sees 35, and the other products are at store price × 1.10.

Pages: M05 M06 MD03 MD13 A06 A08

#### MER-004 — Temporary suspension [Important]

Rules:
- The merchant temporarily pauses their branch for a set period from a time to a time, then the branch returns automatically.
- The merchant suspends a product for a set duration, then the product returns automatically.
- Regular and exceptional hours are in Riyadh time.
- Temporary pause is for the branch manager and anyone with the "Orders" permission.

Acceptance criteria:
- The branch returns automatically at the set time.
- The product returns automatically at the set time.

Pages: M05 M06 M09 MD03 MD09

#### MER-005 — Menu periods and product availability [Launch-critical]

Rules:
- From the merchant's page in the admin dashboard, a morning menu period, an evening one, or both can be enabled, or a single menu with no periods.
- Each menu has an active period; two menu periods of a branch do not overlap, and the hours of special days can be set.
- The merchant can edit the availability hours of a specific product per their permissions.
- Visibility requires an open branch, an active menu, an enabled product, and a time within the product's availability.
- If a product's period is not set, it follows the full period of the menu; Mart is excluded from managing a restaurant menu and uses the catalog.
- The merchant sets the hours of special days (Ramadan and holidays) from their app, and they appear to the platform, which can edit them.

Acceptance criteria:
- A 7–11 product does not appear at 12.
- The evening menu period does not appear in the morning.
- Enabling a single menu does not require two periods.

Pages: C07 M05 M06 M09 MD03

#### MER-006 — Merchant orders screen [Launch-critical]

Rules:
- A repeating bell until interaction; lists for new, preparing, and ready.
- Preparation time is set once within 3 minutes; the default is applied after that.
- Ready does not require the products invoice in menu and Mart; write-in requires uploading the products invoice and the customer's payment before delivery.
- No rejection for menu or Mart; write-in rejection is before the products invoice.
- The merchant sees the customer and driver by an ID number only; the customer's number is excepted in the "Call me" case for an out-of-stock item per MER-032.

Acceptance criteria:
- No automatic discount offer or automatic penalty.
- A ready menu order is not blocked because of a missing products invoice.

Pages: M01 M02

#### MER-007 — Merchant menu link [Launch-critical]

Rules:
- A link extension for each merchant with a QR code and links that open the app or the app store.
- Platform staff set whether the order coming from the link is exempt from the contract fee only.
- The source is fixed on the cart created in the link session, and is not generalized to later orders from the app.
- The payment fee and the customer service fee remain; Mart and pharmacy have no payment fee to begin with.
- An exempt order does not increase the per-customer fee counter for each branch.

Acceptance criteria:
- The exemption option turned off means the usual contract is applied.
- The order statement shows its source and the exemption value.

Pages: MD13

#### MER-008 — Financial statement per branch [Important]

Rules:
- A live page per branch (PAY-006) showing for each order: products value, the commission or contract fee or the Mart and pharmacy percentage, the payment fee (not shown for Mart and pharmacy), the branch's share of offer discounts, ad and cashier fees, loss charges and penalties, compensations, refunds, tax on platform fees separately, and the net.
- Each branch's monthly fees invoice is independent of this page (PAY-022).
- Statement export.
- Every loss charge or penalty on the branch in its statement carries a visible type and status; the statuses are: Potential, Charged, Under objection, Accepted, Rejected
- An objection button for each loss charge or penalty.
- The page opens with the branch's dues account in three separate balances: "Pending capture" (orders not yet closed, amount held), "Due" (captured and in the branch's Moyasar wallet, not yet paid out), and "Paid out to you" for the period; below it the next weekly payout date (PAY-006). The merchant manager also has "All branches" with their total.

Acceptance criteria:
- Each line is linked to its order or its source (ad, cashier integration, report).
- When an objection is accepted, the status changes and the system issues a reversal entry.
- The total of "Pending capture", "Due", and "Paid out to you" for the period matches the net of its orders in the statement.
- A loss charge on one branch does not appear in another branch's statement and is not deducted from its dues.

Pages: MD02 MD07

#### MER-009 — Operation type and section [Launch-critical]

Rules:
- Operation type: restaurants · Shops · Mart · pharmacies. The operation type determines the fee model.
- The section and category determine only where it appears.
- The merchant does not change the operation type themselves.
- The merchant suggests the operation type at registration, and the platform approves or changes it.

Acceptance criteria:
- When the category changes, the fees do not change.

Pages: MD13 MD15

#### MER-010 — Mart catalogs [Launch-critical]

Rules:
- The catalog is for Mart only. The platform creates three types at reference store prices: the primary (common grocery products), the secondary (specialized categories the grocery chooses, such as organic or imported), and the general (what Mart merchants suggest after platform approval).
- When the merchant type is set to Mart, Mart mode is activated automatically, and the merchant chooses whole catalogs then edits products individually.
- The catalog subscription inherits its current products enabled, and later additions enter the grocery disabled unless the merchant turns on the "Enable additions automatically" option; a local edit of price, availability, and image is not replaced by a central update.
- A new merchant product is sent to the platform for approval into the general catalog; before approval it is a draft not shown to the customer, and after it, it stays enabled at the grocery that suggested it.
- Deactivating a central product deactivates it in all groceries; a local activation does not override the central deactivation.
- Each grocery has an independent page, enabled products, and local prices with a +5% preview.
- The "Enable additions automatically" option is per grocery and catalog, and is off by default.

Acceptance criteria:
- Updating the central product does not touch an edited local price.
- A new product in a shared catalog enters the shared grocery disabled, unless the "Enable additions automatically" option is on.
- Central deactivation hides the product from everyone.

Pages: C04 C07 M07 MD03 A07

#### MER-011 — Cashier system integration [Launch-critical]

Rules:
- The platform chooses the first batch of systems after verifying their interfaces, and only the available systems are shown to the merchant.
- The evaluation list: Foodics, Marn, Sapaad, Touché, NCR Aloha, Oracle Simphony, iiko, berryPOS, and Odoo POS for restaurants; Rewaa, Qoyod, Snad, Loyverse, Geidea, and EZPOS for Shops and Mart.
- The order is sent to the linked system, and items and the products invoice are imported when integration is available; it is not assumed that all systems are supported at launch.
- Another program creates an integration request to the platform; the fee is set per branch according to the system and size.
- The manual products invoice is an alternative to integration, optional for menu and Mart and mandatory for write-in.
- At launch, cashier integration is built only for the systems the platform approves, and the platform decides per branch whether it is connected; each branch has its own system and integration.

Acceptance criteria:
- Another program creates a request in its own name.
- The absence of integration or of a products invoice in a menu order does not block order fulfillment.
- Two branches of one merchant with different cashier systems are each connected to their own system.

Pages: MD13

#### MER-012 — Communication with the platform [Launch-critical]

Rules:
- There is an in-app chat between the platform and the merchant, and each party can write in it.

Acceptance criteria:
- Chats are saved and linked to the merchant.

Pages: M12 MD12

#### MER-013 — Merchant self-registration [Important]

Rules:
- The merchant starts their registration by themselves, uploads their documents, and follows the status of their request.
- The platform approves the request or asks for it to be completed, with a written reason.
- The platform has "final rejection" with a written reason, in addition to approval and requesting completion.

Acceptance criteria:
- The request for completion appears to the merchant with its reason.
- An unapproved store does not appear to customers.

Pages: MD15

#### MER-014 — Account manager [Important]

Rules:
- Account manager is a separate role in the admin dashboard; the admin assigns each employee with this role a group of merchants, and each merchant has one account manager
- Their name appears to the merchant in the communication channel (MER-012), the merchant's chats are assigned to them, and the support supervisor sees them

Acceptance criteria:
- A new chat from the merchant reaches their account manager.

Pages: MD12

#### MER-015 — Menu from an image or file [Later]

Rules:
- The system converts the image or file uploaded for the menu into a draft of items, and the merchant reviews it.
- After that, the platform approves the draft (MER-002).

Acceptance criteria:
- Draft items are not published before the platform approves them.

#### MER-016 — Founding partner badge [Later]

Rules:
- The "Founding partner" badge gives the merchant promotional terms for a set duration, by platform decision.
- The badge appears in the merchant's statement.

Acceptance criteria:
- When the duration ends, the merchant's regular terms return.

#### MER-017 — Branches in the merchant dashboard [Important]

Rules:
- The merchant switches between their branches with one click from the top of the dashboard.
- The "All branches" option shows total sales and a comparison between branches.
- Each page shows the data of the selected branch or the data of all branches.

Acceptance criteria:
- A branch manager sees only their branch.

Pages: MD01 MD09

#### MER-018 — Busy mode [Important]

Rules:
- The merchant increases the preparation time for new orders only, by up to 15 minutes, for a maximum of one hour, and the total preparation time does not exceed a cap of 40 minutes. These values are configurable, edited from settings
- The customer sees the new time before ordering
- The mode does not change the time of an existing order

Acceptance criteria:
- An increase above the cap is rejected
- This mode ends automatically after one hour

Pages: M09

#### MER-019 — Driver data for the merchant [Launch-critical]

Rules:
- The merchant sees the driver's ID number, expected arrival time, and waiting time
- The merchant does not see the driver's name or phone number

Acceptance criteria:
- The driver's name and phone number are not shown to the merchant

Pages: M01 M02 M03 M08

#### MER-020 — Driver arrival at the store [Important]

Rules:
- The merchant is notified of the driver's arrival
- Handover uses the driver code ( ORD-005 )

Acceptance criteria:
- The order is not handed over without the code

Pages: D03 D04 M01 M03 M08

#### MER-021 — Printing and sharing [Important]

Rules:
- Print the order ticket from the merchant app on a connected printer, including the order items, their add-ons, and notes
- The order, its products invoice, or the statement can be shared as a file (PDF) through mobile apps
- In the restaurants and Shops app

Acceptance criteria:
- The printed ticket carries the order number and its items
- The shared file does not carry the customer's name or number

Pages: M02 M10 M11

#### MER-022 — Merchant chat with the customer [Important]

Rules:
- Chat limited to the active order only, for example to get the customer's approval to remove an out-of-stock item
- With hidden numbers; the customer appears by their ID number
- Closed when the order is closed
- The customer or the merchant can start the chat as long as the order is active; links and external accounts are removed just as phone numbers are removed.

Acceptance criteria:
- After the order is closed, the chat cannot be opened

Pages: M02 M13 M04

#### MER-024 — Bundled meals [Important]

Rules:
- A bundled meal consists of items, and each component has options
- The system syncs the meal with the cashier system
- Out-of-stock status of its components is counted

Acceptance criteria:
- If a component is out of stock and has no substitute among its options, the meal becomes unavailable

Pages: C07 C08 M02 M05 M06

#### MER-026 — Store quality [Launch-critical]

Rules:
- The "Store quality" page shows the following indicators: driver waiting time after the preparation time ends, the rate of exceeding the time, temporary pauses during working hours, and the report rate and rating
- The page compares the indicators with the average of stores in the same category in the city

Acceptance criteria:
- The system shows each indicator together with the average of stores in the same category in the city

Pages: M10 M11 MD01 MD14

#### MER-027 — Ratings and replying to them [Important]

Rules:
- The merchant reads their store's ratings and writes one public reply per rating, and the platform reviews the reply
- The merchant sees the trend of their rating each week
- The merchant requests to hide a violating rating (unrelated to the order, or abusive), and the platform decides on the request and records the reason for its decision
- If the merchant's reply to a rating is rejected, the merchant sees the reason, then edits and resubmits; the "one reply per rating" rule applies to the published reply.

Acceptance criteria:
- A second reply to the same rating is not allowed.
- The reply is not shown to customers until the platform has reviewed it.

Pages: MD08

#### MER-028 — Store disappearance alert [Important]

Rules:
- The system alerts the merchant when their store stops appearing to customers during its working hours.
- The system states the reason for the disappearance in the alert: temporary pause or disabling, out-of-stock, outside hours, or city disabled.

Acceptance criteria:
- When the store's city is disabled, the system sends the merchant an alert stating the reason.

Pages: M01 M05 M09

#### MER-029 — Customer indicators for the merchant [Important]

Rules:
- The system shows the merchant, for each period, the number of new customers, the number of repeat customers, and the average basket.
- The system does not show the merchant any personal data of customers.

Acceptance criteria:
- The merchant does not see the name or number of any customer.

Pages: MD01 MD06

#### MER-030 — Merchant app and devices [Launch-critical]

Rules:
- Android, iPhone, and tablet, with multiple devices per branch and independent permissions for each employee.
- The order rings until an authorized device responds; the response is shown on the other devices.
- Mart sees the catalogs, prices, stock, and preparation of its grocery orders; there is no accepting or rejecting of a menu or Mart order.
- Write-in screens allow rejection before the products invoice, and attaching it is mandatory.

Acceptance criteria:
- An action by one employee is reflected on all of the branch's devices.
- A preparation account does not open the dues or edit prices without permission.

Pages: M01 M02 M03 M04 M07 M08 M11 M15

#### MER-031 — Mart order preparation [Launch-critical]

Rules:
- The grocery receives the order after the driver accepts and does not reject it.
- A preparation list by sections, barcode, and quantities, with marking of what is prepared and the completion rate.
- Unavailable opens removal or a substitute according to the customer's choice; a cooler and the number of bags are shown.
- Final review of the total and substitutes; the products invoice is optional, then ready.
- Product management includes catalogs, local products, and the sale price.

Acceptance criteria:
- The order does not move to another grocery.
- Preparation can be finished without a products invoice.

Pages: M08

#### MER-032 — Substitute for an unavailable product [Launch-critical]

Rules:
- At payment, the customer chooses in advance what the merchant does if a product is out of stock: remove it, call me, or cancel the order.
- If the customer chooses "call me", they specify the number the merchant calls: their registered number or another number.
- If the merchant presses "Out of stock" on an item and the customer has chosen "call me", the merchant sees the number the customer chose in order to call it. This is an exception to the rule of hiding customer data, and applies to this order only
- A 3-minute window starts the moment the merchant presses "Out of stock". After the call, the merchant records the customer's response with one button: "Replace", "Remove", or "Cancel".
- If the merchant does not record a response within 3 minutes, the system applies the "remove it" option.
- The merchant proposes removal or a substitute, and the customer approves and pays the price difference if the substitute costs more
- If all items of the order are removed, or the customer had chosen "cancel the order", the order enters "Awaiting support decision" for the reason "item out of stock", and the amount is refunded to the customer in full.
- The support agent decides whether the merchant bears a loss charge to the extent of the loss, or a penalty, for the out-of-stock item, writing the reason (PAY-025), then the order is closed.
- The system hides the customer's number from the merchant when the customer responds, or when "remove it" is applied after the 3-minute window ends, or when the order is closed.
- If the customer accepts a more expensive substitute and holding the difference fails, the item is removed and the customer is notified.
- "Out of stock" is not available after "Ready" is pressed; any problem after that is escalated to support.
- The default option on out-of-stock is "remove it", and the customer's last choice is saved.

Acceptance criteria:
- The number is not shown to the merchant unless they press "Out of stock" and the customer has chosen "call me".
- If no response is recorded within 3 minutes of pressing "Out of stock", the item is removed
- The "Cancel" button cancels the order as in the automatic cancellation due to out-of-stock.
- The number does not appear in the order list, the order details, or the merchant's reports. It appears only for the item the merchant pressed "Out of stock" on, in an order where the customer chose "call me"
- After the customer responds, the 3-minute window ends, or the order is closed, the number is no longer shown to the merchant.
- Cancellation due to out-of-stock does not create a loss charge or a penalty automatically; both are a manual decision by support.

Pages: C09 C10 C12 M01 M02 M08 M12

#### MER-034 — Marketing in the merchant dashboard [Important]

Rules:
- The "Marketing" menu contains two separate pages: "Offers" and "Ads and campaigns".
- The Offers page shows: available offers, offer subscriptions, and the results of each offer.
- The "Ads and campaigns" page allows creating an ad (a paid placement) and a campaign (a message to the store's customers), and viewing the status and results of each; and for the ad, the return on spend.

Acceptance criteria:
- Offer results match the merchant's statement.

Pages: MD04 MD05

#### MER-035 — Merchant reports [Important]

Rules:
- All reports are gathered in the "Merchant reports" section within this page.
- Reports support filtering by period and branch, comparison, export to Excel and PDF, and weekly sending
- Reports do not include customers' phone numbers or addresses.

Acceptance criteria:
- A branch manager does not see the reports of any other branch.

Pages: M10 MD01 MD06

#### MER-036 — Products invoice and its archive [Launch-critical]

Rules:
- For restaurants, Shops with a menu, and Mart: issuing or uploading a products invoice is optional, and no alert requires it.
- For write-in and pharmacy: the products invoice image and its amount are mandatory before sending the payment request; no merchant rejection after that.
- A linked cashier may attach it automatically or the merchant uploads it manually.
- The archive keeps what exists and links it to the order number, and the absence of an optional one is not treated as a delay.

Acceptance criteria:
- An optional products invoice does not block Ready or pickup.
- Write-in does not create a payment request without an image.

Pages: D04 M02 M04 M08

#### MER-037 — Employees and permissions [Launch-critical]

Rules:
- The merchant manager creates employees and sets the branches and permissions: orders, handover, products, prices, offers, campaigns, reports, finance, tickets, ratings, employees.
- The default permissions of each role are in the "MER-037 appendix: merchant staff permissions matrix"; where a screen differs from it, the matrix prevails.
- A branch manager works within their branch only, and permissions do not exceed what the platform granted to the merchant.
- Every important action records the employee and the time; finance is hidden from anyone not authorized.
- Employee performance shows orders, preparation, delays, and the action log.
- A separate permission named "Ratings" to read and reply to ratings.

Acceptance criteria:
- A products employee does not see the dues statement without permission.
- An employee can be suspended without suspending the store.

Pages: M02 M10 M11 MD09 MD10

#### MER-038 — Preferred captain [Launch-critical]

Rules:
- Optional setting: platform staff assign one or more preferred drivers to the branch.
- The system shows the branch's orders to them first if they are available.

Acceptance criteria:
- An unavailable preferred driver does not delay the order.

Pages: M11 A02 A06

#### MER-039 — Learning center [Later]

Rules:
- The merchant portal includes a "Learn" section containing short Arabic articles.
- A log of new updates

Acceptance criteria:
- When a new update is added, it appears in the log with its date.

#### MER-040 — Product preparation time [Launch-critical]

Rules:
- The merchant sets a preparation time for each product, not exceeding 40 minutes.
- The default order time is the longest preparation time among its products, per ORD-003.

Acceptance criteria:
- A product time above 40 is rejected

Pages: M01 M05 M06

#### MER-041 — Product integration via API [Important]

Rules:
- Restaurants, Shops with a menu, and Mart can import their products directly from their system; there is no product integration for pharmacies because they work by write-in.
- The system syncs prices and stock automatically.
- A price change received through the integration is subject to review ( MER-002 ).
- Not a launch requirement: built after the cashier integration, and the platform decides per branch whether to link it.

Acceptance criteria:
- When a product is out of stock in the merchant's system, the system hides it in the app.

Pages: MD03 MD13

#### MER-042 — Order-receiving devices [Launch-critical]

Rules:
- The system connects to order-receiving devices and printers at branches.
- The order reaches the device and is printed without merchant intervention.

Acceptance criteria:
- A device disconnection does not lose the order

Pages: M01 M11 M15 MD09

#### MER-043 — Merchant and employee accounts [Launch-critical]

Rules:
- The platform creates the merchant manager account when the merchant is approved (it is the same registration account), and the merchant manager adds their employees, who get their login immediately within the permissions the platform granted, and this is logged.
- Each account has its permissions and branches set.

Acceptance criteria:
- An employee does not see the statement if they do not have the finance permission.

Pages: MD07 MD10

#### MER-044 — Files and attachments [Launch-critical]

Rules:
- A files page for the merchant and the driver to upload operational files and optional dates.
- There is no mandatory license list or compliance check that blocks activation; official documents do not automatically become a requirement.
- When a document's expiry date (ID or license) approaches or arrives, a reminder reaches the merchant or driver and the platform, and this does not stop orders or tasks.
- The document reminder starts 30 days before it expires, then on the expiry day.

Acceptance criteria:
- The absence of an optional file does not stop orders.
- An expired document does not prevent the driver from receiving tasks.

Pages: MD11 MD15

#### MER-045 — Payouts and invoices archive [Launch-critical]

Rules:
- On this page the merchant finds their payouts, the fees and ad invoices issued to them, and the invoices of their products.
- The user searches by order number or by date.
- Platform staff view the same archive for each merchant.

Acceptance criteria:
- When searching by order number, the products invoice and payout linked to that order appear.

Pages: MD07

#### MER-046 — Merchant type and its admin page [Launch-critical]

Rules:
- All merchants are under contract; the operating type is restaurants, Mart, pharmacies, Shops.
- Restaurants are menu, Mart is catalog, pharmacy is write-in, Shops is menu or write-in with conversion from the admin page.
- The branch zone defaults to the limits of the city it is in (DSP-002), and platform staff can draw a manual zone for the branch within its city; offers and campaigns follow the branch zone.
- The merchant page brings together the business, branches, operations, products, contract, marketing, finance, permissions, and support; and the merchant's contract is the default for all its branches and can be customized for a branch (PAY-009).

Acceptance criteria:
- Converting a Shops merchant to menu keeps the history and old orders.
- Mart does not allow turning on self-pickup.
- A new branch without a manual zone takes its city's limits.

Pages: A05 A06

#### MER-047 — Menu completeness and image assistant [Important]

Rules:
- Shows the completeness percentage of name, image, description, price, and options.
- The image and description improvement tool produces a draft, and publishing it depends on the merchant's permission.
- No completeness percentage is based on mandatory nutrition data.

Acceptance criteria:
- A missing calorie count does not prevent a product from being complete.

Pages: MD03

#### MER-048 — Preparation time suggestion from actuals [Later]

Rules:
- The system calculates the average actual preparation time for each item and each hour.
- A one-click suggestion to adjust the time

Acceptance criteria:
- The suggestion does not change the preparation time without the merchant's approval.

#### MER-049 — Smart ratings summary [Later]

Rules:
- Each week the system shows the merchant what customers praise and what they complain about, with one suggested action

Acceptance criteria:
- The summary relies on the week's ratings only.

#### MER-050 — Unmet request in your branch's zone [Later]

Rules:
- The system shows the merchant what customers searched for in the merchant's category and did not find.

Acceptance criteria:
- No customer data appears

#### MER-051 — Quiet-hours offers [Later]

Rules:
- The system provides an "Hours of the day" option in the offer.
- The system suggests an offer for weak hours only.

Acceptance criteria:
- The offer does not appear outside its hours

#### MER-053 — Conversion between write-in and menu [Launch-critical]

Rules:
- Platform staff can convert a Shops merchant from write-in to menu after its products are prepared; restaurants are menu, pharmacies are write-in, and Mart is catalog.
- The conversion applies to new orders and preserves the mechanism and accounting of previous orders.
- If the menu is not ready, the conversion is not published until valid product data is available.

Acceptance criteria:
- An old write-in order remains with two payments and its products invoice after the merchant is converted.

Pages: C05 A06

### Appendix MER-037: Merchant staff permissions matrix

Approved by the owner (29 October 2026).

#### Glossary

- **Merchant owner** = "merchant manager" in MER-037 (L4223) and MER-043 (L4293). It is the registration account itself, and sees all branches.
- **Branch manager**: works in their own branch only (MER-037 L4224, MER-017 L4003). Created from MD10 with a ready-made permissions template (L1545). ✓ in the branch manager column means the permission is **included in the default template and for their branch only**.
- **Staff member (with granted permissions)**: has nothing by default. The owner (or the branch manager within their limits) grants them permissions from the MER-037 list: Orders, Handover, Products, Prices, Offers, Campaigns, Reports, Finance, Tickets, Staff, **Reviews** (L4223, L4227).
- **Prep account**: a shared device or kitchen account. It works with the "Orders" permission within its limits (M01 L936, M08 L1144). It does not open dues or edit prices (MER-030 L4137). In M11 it sees only orders, devices and support (L1224).

Cell symbols: ✓ allowed | ✗ not allowed and not grantable | "By grant" not allowed by default, and enabled by granting the permission named in parentheses.

#### Matrix

| # | Action | Merchant owner | Branch manager | Staff member | Prep account | Reference and note |
|---|---|---|---|---|---|---|
| 1 | Accepting the order (interacting with the ringing and opening it) | ✓ | ✓ | "By grant" (Orders) | ✓ | M01 L921–922, L936; MER-030 L4131. There is no accept or reject decision for a menu or Mart order (MER-030 L4132), and "accept" here means stopping the ringing and starting preparation |
| 2 | Set the preparation time (the only edit within 3 minutes) | ✓ | ✓ | "By grant" (Orders) | ✓ | M01 L921, L926; ORD-003 L3110 |
| 3 | Ready announcement ("Ready") | ✓ | ✓ | "By grant" (Orders) | ✓ | M01 L923; M02 L967; M08 L1144 |
| 3a | Delivery by the driver or the customer (code entry) | ✓ | ✓ | "By grant" (Handover) | ✓ | M01 L937; M03 L1016. "Assumption": the prep account has "Handover" because it is usually the device at the counter |
| 4 | Out-of-stock handling (remove / call / replace / cancel according to the customer's choice) | ✓ | ✓ | "By grant" (Orders) | ✓ | M02 L967; M08 L1144; M12 L1268 |
| 5 | Rejecting a write-in order (only before the products invoice is uploaded) | ✓ | ✓ | "By grant" (Orders) | ✗ "assumption" | Owner decision: rejection applies to the write-in order only, and only before the invoice (ORD-004 L3130, MER-006 L3853). There is no reject button in menu and Mart for any role. Blocking it for the prep account is an "assumption": rejection cannot be undone, the order enters "Awaiting support decision", and the shared account does not identify who made the decision (MER-037 L4225) |
| 6 | Uploading the invoice (products invoice) | ✓ | ✓ | "By grant" (Orders) | ✓ | M02 L955; M04 L1041; M08 L1138. In write-in, the upload sends the payment request to the customer (M04 L1031) |
| 7 | Temporarily pause the branch | ✓ | ✓ | "By grant" (Orders) | ✗ "assumption" | M09 L1172; MER-004 L3822. Pausing hides the branch from customers, so it is not left to a shared account |
| 8 | Busy mode | ✓ | ✓ | "By grant" (Orders) | ✓ "assumption" | M09 L1172; MER-018 L4010. The kitchen knows best how busy it is. Busy mode does not raise any time above 40 minutes (owner decision) |
| 8a | Edit working hours and special days | ✓ | ✓ | ✗ | ✗ | M09 L1173; MD09 L1535 |
| 9a | Edit the menu (add a product, name, image and description, options, preparation time) | ✓ | ✗ (the menu is shared across all branches) | "By grant" (Products) | ✗ | M05 L1064–1066; M06 L1094; MD03 L1357. The branch manager changes only the **availability** of their branch's products and their temporary pause (M05 L1066, MD03 L1359) |
| 9b | Edit prices (store price) | ✓ | ✓ for their branch | "By grant" (Prices) | ✗ | M05 L1065–1066; M06 L1095; MER-030 L4137. Editing is within the merchant's pattern, and anything beyond it goes to platform review (MER-002) |
| 10 | Devices and printers (link, remove, sign a device out, auto-print) | ✓ | ✓ for their branch | ✗ (status view only) | ✗ (status view only) | M15 L1241–1242; MD13 L1627 |
| 11 | Test print and bell test | ✓ | ✓ | ✓ | ✓ | M15 L1242. It needs no grant because it changes nothing |
| 12 | Staff management (add, permissions, suspend) | ✓ | ✓ for their branch's employees and within their permissions | "By grant" (Staff) | ✗ | MD10 L1558–1560; M11 L1213, L1218; MER-037 L4224 |
| 13 | Ratings, replying to them, and requesting hiding | ✓ | ✓ for their branch | "By grant" (Reviews) | ✗ | MER-037 L4227 makes it a separate permission, and MD08 L1488 contradicts it by tying it to "Tickets" |
| 13a | Objecting to a loss charge or penalty | ✓ | "By grant" (Finance) | "By grant" (Finance) | ✗ | MD08 L1489; MD07 L1454, L1464–1465; SUP-006 |
| 14 | Tickets and platform chat | ✓ | ✓ for their branch | "By grant" (Tickets) | ✓ for order tickets only "assumption" | M12 L1267; MD12 L1600–1602; M11 L1224. The "Accounts" subject also requires "Finance" (M12 L1267). **Destination (owner decision):** the account manager assigned to the merchant, which is a role in the admin dashboard, together with the supervisor |
| 15 | Viewing the contract card | ✓ | "By grant" (Finance) | "By grant" (Finance) | ✗ | MD13 L1626. Line L1628 says "view only for everyone", which contradicts L1626 |
| 16 | Statements and wallet (statement, payouts, fees invoice, archive) | ✓ | "By grant" (Finance) for their branch | "By grant" (Finance) | ✗ | MD07 L1464–1465; M10 L1196; MER-043 L4297; MER-030 L4137 |
| 17a | Payout request | ✗ | ✗ | ✗ | ✗ | The merchant does not request a payout: the branch wallet balance appears to the accountant in every cycle, who approves or rejects its payout (owner decision, 29 October; PAY-006 in 4.11). The owner and the branch manager see the status "Awaiting approval" in the statement |
| 17b | Change bank details (request to change the bank account) | ✓ | ✗ | ✗ (not granted even with "Finance") | ✗ | "Assumption". MER-001 L3782–3784 requires verification and finance approval, and the notification goes to the merchant manager's mobile. MD09 L1521 shows the account as view-only and does not specify where the request is made; we propose it be submitted from MD12 under the "Accounts" subject |
| 18 | Paid campaigns and ads (create, send, stop) | ✓ | "By grant" (Campaigns) for their branch | "By grant" (Campaigns) | ✗ | MD05 L1414–1416. Spend and return are visible to whoever has "Finance" or "Campaigns" (L1415). The amount is deducted from the branch's dues after approval (MKT-003, MKT-005) |

#### General matrix rules

1. No employee's permissions exceed what the platform granted the merchant. What the platform has withdrawn appears locked for all roles (MER-037 L4224, MD10 L1563).
2. A branch manager does not grant an employee a permission they do not hold themselves (MD10 L1560).
3. Every action from the prep account is logged under the device name together with the last employee who signed in on it, if any ("assumption"). The reason is that MER-037 L4225 requires logging the employee.
4. Ringing continues until a device with the "Orders" permission interacts (MER-030 L4131).

### Driver (DRV)

#### DRV-001 — Driver account and activation [Launch-critical]

Rules:
- The driver registers by themselves as a Saudi freelancer or a resident freelancer. The "Company-affiliated" type is activated later with the first delivery company (FLT-001).
- The account includes contact, bank, vehicle and its photos, city, and equipment; activation is approved by platform staff.
- No Taxi operation at launch; no mandatory compliance list other than HRDF (Hadaf) and reporting to the Transport General Authority (TGA) (REG-007).
- Account closure goes through support to settle dues and insurance.

Acceptance criteria:
- An unapproved driver does not receive a task.
- No active Taxi service screen.
- The "Company-affiliated" option does not appear in registration before companies are activated.

Pages: D01 D10 D13 A10

#### DRV-002 — Orders and services [Launch-critical]

Rules:
- One page for restaurant, Mart, pharmacy, and Shops orders, with clear tags.
- Regular orders are open to the approved driver; platform staff disable a service or city when needed.
- The task offer shows: the expected earnings after tax and the percentage, the pickup and drop-off locations, and the countdown.
- Taxi is not operated; only an internal service extension is prepared for it.
- In the task offer, the paid tip appears as a separate line after excluding its 15% tax, next to the net delivery.
- When there is a clear blocker (offline, outside their zone, balance lockout on the dues account reaching −50, ban from the penalty ladder), a general reason is shown to the driver, without revealing the priority index calculation.

Acceptance criteria:
- No Taxi task is shown.
- Accepting the task locks it to the first acceptance only.

Pages: D02

#### DRV-003 — Location while working [Launch-critical]

Rules:
- The driver's location is sent only while working.

Acceptance criteria:
- When the network returns, events are sent in the order they occurred.

Pages: D01 D03 D05

#### DRV-004 — Driver task stages [Launch-critical]

Rules:
- Arrived at store, then pickup with the driver code and a photo, then on the way, then arrived at customer, then delivered within 100 m with proof.
- The products invoice depends on the order type; the driver does not ask the customer for a code.
- No declining after acceptance; an emergency report is referred to support to decide the assignment (ORD-014), and waiting time is saved separately.
- Leaving at the door needs the customer's instructions or support permission and proof.
- Mobile events, their time, and their location are saved and synced in order when the network returns.

Acceptance criteria:
- Handover does not ask for a code.
- A saved delivery event is not lost on network disconnection and does not duplicate the fee.

Pages: D03 D04 D05 D06 D11 D13

#### DRV-005 — Earnings [Important]

Rules:
- The driver is entitled to the delivery fee after excluding its tax and then the platform percentage, and to the tip after excluding its 15% tax with no platform percentage (PAY-014).
- When an order is ended because the customer is unresponsive, the driver is entitled to the full fee and the tip
- A notification reaches the driver when any tip is added after delivery
- A tip paid later appears in the statement of the same task.

Acceptance criteria:
- The reason for any deduction is shown
- When a later tip is paid, it appears in the original task's statement and is not recorded as a new task.

Pages: D06 D07

#### DRV-006 — Incentives [Launch-critical]

Rules:
- Platform staff control configurable incentives, which are: weekly target, peak incentive, top 10 in the city, and driver referral.
- Each incentive specifies: the city, the days and hours, the incentive value, the eligible levels, the maximum budget, and the end date.
- Platform staff can change the incentive scheme within a specific city, or for a specific month, without affecting others
- An incentive stops automatically when it reaches the budget or the end date.
- The incentives page shows the cost of each incentive and the extra orders it brought.
- An expired document only sends a reminder and does not block tasks (MER-044).

Acceptance criteria:
- A Jeddah incentive does not appear to a Riyadh driver.
- When an incentive reaches its budget, it stops.
- Editing a rule today does not change any previously completed task.

Pages: D09 D10 A11

#### DRV-007 — Optional verification badge [Launch-critical]

Rules:
- Platform staff can grant a verified badge after reviewing optional files.
- The badge is a configurable eligibility or ranking factor; not a mandatory compliance list.

Acceptance criteria:
- The absence of optional verification does not block regular services.

Pages: D01 D10 D13

#### DRV-011 — Vehicle Type [Important]

Rules:
- The vehicle type is car or bicycle; platform staff configure the maximum distance and permitted services for each type.
- Eligibility is checked at the task offer and at acceptance; Taxi is deferred for everyone.
- Default: bicycle up to 5 km for restaurants, Shops, and pharmacies, excluding Mart; car up to 15 km and all services.

Acceptance criteria:
- A driver does not receive a task beyond the vehicle's limit or the permitted service.

Pages: D02 D10 D13

#### DRV-012 — Onboarding Before the First Task [Important]

Rules:
- Before the first task, the driver goes through a short mandatory onboarding in the app, covering: task stages, non-responsiveness, safety, and uniform.
- A simple quiz whose pass is recorded
- The onboarding quiz has 10 questions and the pass mark is 80%; attempts are unlimited, with a one-hour wait after 3 failed attempts.

Acceptance criteria:
- If the driver does not pass the quiz, they do not receive a first task.

Pages: D01 D13

#### DRV-013 — Equipment Record [Launch-critical]

Rules:
- An equipment record is kept for each driver: thermal bag, cooling bag, and uniform.
- The record is used in dispatching and assignment

Acceptance criteria:
- The system does not offer a chilled order to a driver who has no cooling bag.

Pages: D02 D10 D13 A10

#### DRV-015 — Driver Levels [Launch-critical]

Rules:
- By default: New for the first 30 orders, Under Watch below 70, Silver 70–79, Gold 80–89, Diamond 90 and above.
- The level determines task-offer priority, capacity, and percentage benefits; by itself it does not prevent a regular delivery service.
- Levels, their thresholds, and their benefits are configurable per city and period.
- The level score is based on the last 30 days; it is checked daily, and the benefit is locked onto the task when it is accepted.
- Default benefits: Diamond has higher priority, 3 orders together, and a 2-point reduction in the platform percentage; Gold has priority, 3 orders, and a 1-point reduction; Silver has 2 orders together; New and Under Watch have 1 order. The benefits are shown to the driver as numbers.

Acceptance criteria:
- A score of 85 gives Gold under the default configuration.
- Switching the performance filter does not change the level.

Pages: D02 D08 D09 A11

#### DRV-017 — Driver Performance Page [Launch-critical]

Rules:
- A single page with filters: last 10 orders, last 30 orders, last 30 days, and custom; updated daily.
- The official level score is the last 30 days; the other filters are for display and diagnosis.
- Default weights: completion 20, delivery 20, pickup 15, acceptance 15, rating 15, confirmed reports 10, commitment 5; configurable.
- Scores exclude merchant delays, customer cancellations, and technical failures.
- The platform configures the conversion of indicators into scores; the default is linear from zero to the target, capped at the indicator's weight; an indicator with no data is excluded and the remaining weights are normalized to 100.
- The first 30 orders are level New; there is no automatic financial penalty from a lower score.
- Default targets: completion 98%, on-time delivery 90%, on-time pickup 90%, acceptance 80%, rating 4.8, confirmed reports zero, and commitment 95%.

Acceptance criteria:
- The level score does not change merely by switching the display filter.
- Absence of ratings is not treated as zero satisfaction.

Pages: D08 D09 A11

#### DRV-018 — Available Tasks List [Important]

Rules:
- The list shows available tasks that no one has accepted.
- Nearby drivers choose from it.
- The existing task enters 3 minutes after dispatch starts, and it is seen by the same drivers that dispatch offers to in that minute (DSP-001), and not by anyone who explicitly rejected it.

Acceptance criteria:
- When a driver accepts a task, the task disappears from the list immediately.

Pages: D02

#### DRV-019 — Driver Waiting at the Branch [Important]

Rules:
- The system does not pay the driver for waiting at the branch, and does not charge the merchant or the customer any additional amount.
- The system records the driver's waiting time at the branch for each order, and shows it in merchant reports and the admin dashboard.

Acceptance criteria:
- The driver's waiting does not change any amount in the order.
- The waiting time appears in the "Driver waiting at your location" report.

Pages: D04

#### DRV-020 — Help Button [Important]

Rules:
- At every stage, the driver sees a help button with ready-made reasons: store is late, order does not match, wrong address, customer not responding, accident.
- When the driver presses the button, the system opens a ticket linked to the order in the operations room.
- The reason "Emergency preventing me from completing" opens an emergency report (ORD-014), and it reaches operations with priority.

Acceptance criteria:
- When the ticket is opened, it appears in the operations room linked to the order and the stage.

Pages: D03 D11

#### DRV-021 — Navigation Handoff [Important]

Rules:
- The app provides a button that opens the pickup or delivery location in the driver's preferred navigation app.

Acceptance criteria:
- When the button is pressed, the location of the current stage opens.

Pages: D03 D05 D10

#### DRV-022 — HRDF (Hadaf) Delivery Counter [Important]

Rules:
- The system shows a monthly delivery counter for the Saudi driver.
- The system provides an exportable or shareable report that proves the number of deliveries for the purpose of HRDF (Hadaf) support.
- The HRDF (Hadaf) deliveries report is a PDF carrying the platform's name, its digital stamp, and a QR code for verification; the HRDF (Hadaf) terms are reviewed before launch.

Acceptance criteria:
- The count in the report matches the number of completed deliveries in the month.

Pages: D12

#### DRV-023 — Penalty Ladder and Objection [Launch-critical]

Rules:
- Five consecutive steps are applied to the driver: warning, then priority reduction for a week, then a 24-hour ban, then operations review, then a permanent ban.
- In fraud, location spoofing, account sharing, and abuse of a customer, platform staff jump directly to a permanent ban without progression, after a review; the system does not ban anyone automatically.
- The driver receives a notification of the reason for each step.
- The driver objects within 7 days of the decision notification, and gets the response within 48 hours; anything not answered within that time is escalated to the support supervisor
- Ladder steps are carried out manually by an operations employee or support supervisor after review, not automatically by the system.
- Violations that move the driver one step: a confirmed report, or leaving without permission, or an emergency report that platform staff deemed a violation (ORD-014).
- The driver returns to the start of the ladder after 90 days with no violation.

Acceptance criteria:
- No driver is banned without the reason being shown to them.
- The system does not move the driver a step on its own; every step is a logged staff decision.

Pages: D01 D11

#### DRV-024 — Emergency Button [Important]

Rules:
- The app provides an emergency button that calls the unified emergency number.
- When the button is pressed, the system immediately sends the driver's location and current order to the operations room.

Acceptance criteria:
- When the button is pressed, an immediate alert with the location and order appears in the operations room.

Pages: D03

#### DRV-027 — Location Spoofing Detection [Launch-critical]

Rules:
- The system detects mock locations and impossible jumps in the driver's location.
- The system detects modified phones (rooted or jailbroken).
- An immediate alert reaches the operations team with the evidence, and it appears in the driver's file; the driver is not disabled automatically (DRV-023)

Acceptance criteria:
- If a driver is detected with a fake location, an alert reaches Operations within a minute, and the driver stays active until a staff member decides.

Pages: D01 A02 A10

#### DRV-028 — Entrance Memory with Photo [Launch-critical]

Rules:
- The system saves the first successful delivery photo together with the address's corrected pin.
- The entrance photo is shared with subsequent drivers to the same address without asking for the customer's consent; this is stated in the privacy policy, and the customer can delete it from the addresses page; the retention period follows the data retention policy (Q-06).
- It is shown to every driver delivering to the same address.

Acceptance criteria:
- The photo is shown to the driver on the next order to the same address.

Pages: D05

#### DRV-029 — Chat Translation and Quick Replies [Launch-critical]

Rules:
- The system translates the chat between Arabic, English, and Urdu.
- The app provides ready-made buttons such as "I've arrived at the door" and "I'm on my way".

Acceptance criteria:
- The message appears in the recipient's language

Pages: D05 D14 D10

#### DRV-030 — Demand Map and Best Times [Important]

Rules:
- The app shows the driver the neighborhoods with demand right now.
- The app shows the driver the best earning hours in their city.

Acceptance criteria:
- The map does not show any customer data.

Pages: D01

### Dispatch and Cities (DSP)

#### DSP-001 — Dispatching the Task Offer to Drivers [Launch-critical]

Rules:
- Filtering: online and active, service and city permitted, not excluded by the branch or the customer, recent location, suitable equipment, and available capacity.
- Dispatch starts after the customer's 60-second cancellation window ends (ORD-002), and the 15-minute window is counted from that point.
- Each eligible driver gets a "priority index" out of 100: the driver score (DRV-017, which includes rating) 50%, delivery volume in the last 30 days relative to the city's top driver 30%, and proximity to the branch 20%.
- A preferred captain gets a single exclusive task offer for 30 seconds first if platform staff have configured it; if they do not respond, the order returns to the sequence without changing the 15-minute window.
- First attempt: task-offer radius 5 km and the top 3 by priority index. Second: 6 km and the top 6. Third: 7 km and all eligible drivers. Each attempt allows 30 seconds to accept, with 10 seconds between attempts.
- Subsequent rounds: the task-offer radius expands by 1 km each attempt up to 10 km and then holds, and the order is shown to all eligible drivers; this repeats up to 15 minutes.
- The first atomic acceptance wins, and the task offer is withdrawn from the rest. The order is not linked to two drivers.
- A driver who explicitly declined the task offer is not shown the same order again; a driver who ignored it until the timeout is shown it in the next round.
- Distance is a straight line from the driver's current location to the branch. A driver who already has a task is included if the batching conditions are met (DSP-003).
- A new driver (first 30 orders) is scored as 70 in the calculation.
- Support alert at 5 minutes; at 15 support intervenes and the ORD-004 handling is executed.
- All values are global system settings and can be overridden per city; they are not hard-coded constants.
- If the branch has more than one available preferred captain, the order is shown to them together for 30 seconds, the first to accept takes it, and then the order returns to the normal sequence.
- A driver who has stayed online for an hour without an order takes first place in the first order for which they are within the task-offer radius, so the task offer is shown to them along with the top two others; then the normal rule resumes.

Acceptance criteria:
- The proximity component of the priority index = (1 − distance ÷ the attempt's task-offer radius) × 100.
- Khaled (score 78, 260 deliveries, 1 km) = 85 on the priority index; Ahmed (92, 180, 3 km) = 75; Salem, the new driver (70, 12, 0.5 km) = 54; when the top driver has 260 and the task-offer radius is 5 km.
- With 5 eligible drivers within 5 km, in the first attempt the task offer is shown only to the top 3 by priority index.
- The order is not linked to two drivers.
- Leaving the task-offer radius or exclusion withdraws the task offer.
- City configuration overrides the global configuration.
- A driver online for an hour without an order, 4.9 km away, with a priority index of 40: the task offer is shown to them in the first attempt along with the top two, and not to the third.

Pages: D02 A02 A09 A11 A22

#### DSP-002 — Cities [Launch-critical]

Rules:
- Platform staff draw each city's boundaries, and these boundaries are the city zone.
- When a branch is added and its city is set, the city zone is applied to the branch automatically, and platform staff can draw a separate manual zone for the branch that does not exceed its city's limits; whatever falls outside them is clipped when drawing.
- Optionally: a zone within the city can be set for a specific driver, and orders from outside it do not reach them
- Platform staff assign an order manually by driver number with a reason stated.
- A manual assignment reaches the driver as directly assigned with the reason, and it is binding like acceptance: no rejection and no declining; if the driver cannot carry it out, it is through an emergency report (ORD-014), and it is recorded in their performance.
- If the assigned driver does not open the task within two minutes (setting), an alert reaches the assigning staff member to reassign it; it does not return to automatic dispatch.

Acceptance criteria:
- A customer outside the branch's city cannot order from it.
- If a driver has a defined zone, they are not shown an order outside that zone.
- A manual zone drawn beyond the limits of the branch's city is saved clipped at those limits.

Pages: A09 A10

#### DSP-003 — Order Batching [Launch-critical]

Rules:
- Global settings with a per-city exception: enable batching, capacity, pickup and delivery proximity, maximum additional time.
- Default: 3 orders, 3 km between pickups, 3 km between deliveries, 10 minutes of additional delay for any order.
- An additional order can be added at any stage if the route shows the conditions are compatible and it does not block an existing appointment or preparation.
- The system determines the order of stops; the customer's arrival estimate is recalculated, and the driver's full fee does not change because of a customer's offer.
- The batching setting and its route are saved on the task.

Acceptance criteria:
- Distance proximity without passing the time limit is not sufficient.
- Changing a city's setting does not change a locked route except through a recorded re-plan.

Pages: D02 D03

#### DSP-004 — City Driver Cap [Important]

Rules:
- Platform staff set a cap on the number of free online drivers in each city and in each hour
- A driver who exceeds the cap enters a waiting queue that informs them of the less crowded times
- There is no default cap until platform staff set one, and the waiting queue is oldest first.

Acceptance criteria:
- When the cap is reached, the next driver is placed in the waiting queue.

Pages: A09

#### DSP-005 — Mart Is an Independent Store [Launch-critical]

Rules:
- The customer chooses a specific grocery and its products, then pays, and the order is dispatched to drivers.
- No sequential distribution across groceries, no hiding the grocery's name, and no unified order with an anonymous store.
- No self-pickup for Mart; an out-of-stock product is handled within the chosen grocery.

Acceptance criteria:
- The order does not move to a grocery other than the one the customer chose.

Pages: C04

### Delivery Companies (FLT)

#### FLT-001 — Company Portal [Later]

Rules:
- A portal for each delivery company that shows: the company's drivers, their vehicles, and their performance
- Platform staff set the cities allowed for the company, and can restrict it to part of a city or exclude part of it.
- The company's and its drivers' permissions apply only within its cities.
- Note for the developer: there is no contracting with delivery companies at launch. The entire companies section (FLT-001 to FLT-004) is built later, and driver data and payouts are designed so that a company can be added without a rebuild.
- When contracted: the platform contracts with the company and pays out to it, and the company manages its drivers and pays them out.

Acceptance criteria:
- A company does not see any other company's data.
- A company driver does not receive an order outside their company's cities.

Pages: A12

#### FLT-002 — Company Dues [Later]

Rules:
- The platform contracts with the delivery company and pays out its drivers' dues to the company only, and the company pays its drivers and manages them.
- The platform percentage follows the company's contract, and driver level benefits are not applied to it.
- Payout to the company follows the manual approval in PAY-006.

Acceptance criteria:
- The company report matches the payout
- A company driver does not see a payout or a withdrawal in their app.

Pages: A12 A18

#### FLT-003 — Shift Booking [Later]

Rules:
- The delivery company books shifts for its drivers in its cities
- The system shows platform staff the expected number of drivers for each city and hour.

Acceptance criteria:
- The company cannot book a shift in a city not allowed for it.

#### FLT-004 — Company Scorecard [Later]

Rules:
- The system issues a monthly scorecard for each company containing: completion, lateness, reports, and cancellation.
- The company sees its drivers' indicators from the scorecard.
- The system uses the scorecard when distributing cities.

Acceptance criteria:
- A company does not see any other company's scorecard.

### Administration (ADM)

#### ADM-001 — Roles, Permissions, and Security [Launch-critical]

Rules:
- Permissions are granular, and a role is a bundle of these permissions, and the role scope is one or more cities.
- Ready-made roles at launch: Admin, support supervisor, support agent, operations, finance, and sales (ADM-043).
- The Admin edits the permissions of any role, or creates a custom role and chooses its permissions, and the change applies immediately to the role's employees.
- Least privilege
- The system enforces two-step verification on all admin dashboard and finance users.
- Penetration test before launch
- The prescription photo is not visible to any role in the admin dashboard; only the pharmacist sees it (PHR-012), and the customer's address is seen only by support and operations.
- Session expires after 30 minutes of inactivity.

Acceptance criteria:
- Access to the admin dashboard is rejected without completing the second verification step
- The default operations role does not have refund or compensation.
- Removing a permission from a role immediately prevents its employees from performing it, and its buttons disappear.
- Every change to roles and permissions is recorded in the audit log (ADM-002).

Pages: A22 A26

#### ADM-002 — Audit Log and Dual Approval [Launch-critical]

Rules:
- The system records every financial, permission, or settings change with the values before and after the change.
- The creator of a payout does not approve it
- Every payout, to a merchant, a driver, or a company, and every deposit refund, needs a recorded approval with the approver's name and time; there is no payout without approval.

Acceptance criteria:
- A financial record cannot be deleted from the interface.

Pages: A13 A18 A20 A22 A26

#### ADM-003 — Unified Operations Room [Launch-critical]

Rules:
- A shared screen for restaurants, Shops, Mart, write-in orders, pharmacies, and self-pickup, with service, status, and city filters.
- Opening an alert or order shows its parties, its path, and the nearby drivers if it is not linked to a driver.
- Tabs: dashboard, orders, order file, penalties and loss charges, cities and incentives, drivers and branches now, alert and shift rules.
- One alert is owned by one employee, and is transferred by a recorded action.
- Calling and chat are available from the dashboard, and the call center is an important later integration; financial actions are for authorized users per ADM-043.

Acceptance criteria:
- Another employee does not receive a reserved alert.
- An order not linked to a driver shows the nearest eligible drivers.

Pages: A02 A20

#### ADM-004 — Immediate Disabling [Launch-critical]

Rules:
- Platform staff can disable a branch, city, payment method, or ad.
- On disabling, in-progress orders complete through delivery, and disabling blocks new orders only.
- Exception: a driver banned for fraud or location spoofing has the task withdrawn immediately and it is re-dispatched (DRV-027).

Acceptance criteria:
- A disabled branch does not receive an order
- Disabling a branch does not cancel an in-progress order in it.

Pages: A02 A05 A06 A09

#### ADM-005 — Operational Alerts [Launch-critical]

Rules:
- Platform staff configure the event, duration, service, city, escalation, sound, and priority.
- No driver: alert at 5 minutes and intervention at 15 minutes; no automatic closure or penalty.
- Preparation or driver delay, write-in without products invoice or payment, no response for 30 minutes, emergency report from a driver, medicine not returned: alerts that have a handling playbook and an owner employee.
- A missing products invoice in menu or Mart orders does not create an alert to enforce it.
- A "write-in without products invoice" alert fires 15 minutes after the order reaches the merchant; any alert that no one has picked up within two minutes is escalated.

Acceptance criteria:
- A new rule works without updating the app.
- The alert opens the order, its evidence, and the required action.

Pages: A02

#### ADM-006 — Reports Center [Launch-critical]

Rules:
- The "Reports" page in the admin dashboard gathers all reports in one place.
- The full list is in the "Reports" section of this document (admin reports), and the definitions of their numbers are in the "Metric Definitions" appendix.
- Each report provides: period, city, and department filters, comparison, Excel and PDF export, and scheduled email delivery.
- The system separates total sales from platform revenue.
- Email delivery frequency: daily, weekly, and monthly. A finance report to an external email (such as the accountant) is added by the Admin only.

Acceptance criteria:
- Report numbers match the orders and ledger entries.
- When the same number is shown in a report and a page, the value is the same

Pages: A21

#### ADM-007 — Notifications Center [Launch-critical]

Rules:
- Create and schedule an operational or marketing notification within a city, audience, and time.
- Segments, cities, and stores are targeted; a store offer is not sent outside its branch zone.
- The audience preview, its size, and the language template appear before sending.

Acceptance criteria:
- A store offer does not reach an address it does not serve.
- A customer who turned off marketing notifications in their settings does not receive marketing notifications.

Pages: C26 A17

#### ADM-008 — Customer Analytics [Launch-critical]

Rules:
- Sorting by city, orders, spend, and rating

Acceptance criteria:
- An unauthorized employee does not see the customer's address.

Pages: A13

#### ADM-009 — Driver Analytics [Important]

Rules:
- Acceptance, rejection, arrival times, cancellation, ratings, and earnings
- An alert is issued when shortage or damage reports on a driver exceed a percentage set by platform staff
- When the alert is issued, a review is opened, and nothing is deducted automatically
- A driver review is opened when reports exceed 5% of their deliveries in 30 days (with a minimum of 20 deliveries), or on a rating of 2 stars or lower.

Acceptance criteria:
- When a poor rating exists, a review is opened and nothing is deducted automatically
- When the percentage is exceeded, a review is opened with no deduction from the driver

Pages: A11

#### ADM-010 — Communication Channel [Launch-critical]

Rules:
- Platform staff communicate by chat with merchants, drivers, and customers inside the app.

Acceptance criteria:
- Every chat is linked to its owner or to its order.

Pages: A03 A06 A10

#### ADM-011 — Announced Time Accuracy [Important]

Rules:
- A report that measures the accuracy of the time announced to the customer by comparing it with the actual time, per city and per branch
- The displayed times are tuned based on the report (CUS-005).

Acceptance criteria:
- The report shows, for each branch, the difference between the announced time and the actual time.

Pages: A01

#### ADM-012 — Anomaly Detection [Important]

Rules:
- The system alerts automatically when there is an unusual spike in refunds, coupons, or payment failures.
- The spike is detected at the city, branch, or bank level.
- Unusual spike: 50% above the average of the last 4 weeks for the same hour, with a minimum of 10 operations; the Admin, finance, and support supervisor are notified.

Acceptance criteria:
- The alert identifies the type of spike and its source.

Pages: A01

#### ADM-013 — Ban and Exclusion [Important]

Rules:
- Ban lists for customers, merchants, and drivers; a ban is a penalty with a recorded reason and a duration, or it is permanent.
- Exclude a driver from a specific branch.
- Exclude a driver from a specific customer.
- A freeze temporarily prevents spending from the customer's wallet, with two-person approval.

Acceptance criteria:
- A driver excluded from a branch is not shown that branch's orders.
- A driver excluded from a customer is not shown that customer's orders

Pages: A13 A26

#### ADM-014 — Operations Room Indicators [Launch-critical]

Rules:
- Indicators are calculated per city and per service.
- Movement indicators include: open orders vs. available drivers, average time to find a driver, driver wait at the branch, and delivery time.
- Quality indicators include: late rate, report rate, and cancellation rate by cause.

Acceptance criteria:
- When a city and service are selected, only their indicators are shown.

Pages: A02

#### ADM-015 — Peak Seasons [Important]

Rules:
- Platform staff define seasons, such as Ramadan, Eids, Hajj, and city seasons.
- A season can be linked to special branch hours, driver incentives, alerts, and delivery fees when needed.

Acceptance criteria:
- When the season ends, hours and fees return to their normal values

Pages: A09

#### ADM-016 — Controlled Experiments [Later]

Rules:
- A setting can be enabled for a percentage of cities or customers over a time period.
- Compare results before rolling out

Acceptance criteria:
- Customers outside the experiment are not affected by the setting.

#### ADM-030 — Analytics for Every Page in the Admin Dashboard [Important]

Rules:
- Every page shows the indicators, charts, tables, and alerts listed in its elements, in the "Admin Dashboard" section, using the definitions in the "Indicator Definitions" appendix.
- Unified indicator definitions are used across all pages.

Acceptance criteria:
- Tapping any number opens the list it was calculated from
- When the same number is shown on two pages for the same period, the value is the same

Pages: A01 A21

#### ADM-032 — City Page [Launch-critical]

Rules:
- Each city in the admin dashboard has a page showing: its branches, its drivers, its customers, and its numbers
- From this page, the list for each category opens with filters

Acceptance criteria:
- A city's branch list does not show any branch from another city.

Pages: A05 A09

#### ADM-033 — In-App Registration and Coverage Requests [Launch-critical]

Rules:
- Drivers and merchants register their accounts directly from our app.
- If the service is not available at the customer's, driver's, or merchant's location, a field appears where they register their interest
- For the customer it is one step: they set their location and submit, and it reaches the admin dashboard automatically

Acceptance criteria:
- Coverage requests appear on the map in the admin dashboard.

Pages: C24

#### ADM-034 — Settings Log [Launch-critical]

Rules:
- Every configurable value has a type, unit, allowed limits, version, and effective date, and a future version can be scheduled or rolled back.
- Commercial and operational configurable values are not hard-coded; the online payment fee 2.5%+1 is an approved rule and is shown read-only within the contract.
- An order stores the contract version, fees, and time limits used; changing a setting does not change the constraints of a previous order.
- Priority: branch, then city, then region, then global, where the setting supports it; and the driver percentage: city, then region, then level benefits, then global.
- Editing settings and roles does not require a second approval at launch; it is recorded in the audit log, and a notification reaches all admins when fees or roles are edited.

Acceptance criteria:
- A scheduled version takes effect at its time.
- A previous order keeps its calculation after the percentage is edited.

Pages: A22 A26

#### ADM-035 — Driver Performance and Incentives [Launch-critical]

Rules:
- A page is shown inside "Drivers" with four tabs: Performance, Driver Profile, Incentives, and System Settings.
- The content and requirements of each tab are in the "Admin Pages Details" appendix.

Acceptance criteria:
- When the weights change, scores are recalculated in the next update

Pages: A11

#### ADM-036 — Accounts Page [Launch-critical]

Rules:
- Nine tabs: Overview, Collection and Reconciliation, Dues and Payouts, Liabilities, Invoices, Tax, Refunds, Financial Reports, and Closing and Controls.
- The system records every riyal with a two-sided entry. An entry is not edited after it is recorded; it is corrected with a reversing entry.
- The content and requirements of each tab are in the "Admin Pages Details" appendix.
- Closing the month is blocked if there is a failed transfer or a reconciliation difference without a written comment; it is allowed if every difference has a comment explaining it.

Acceptance criteria:
- A closed month does not change
- Collected minus the actual Moyasar fee equals the amount deposited in the bank; otherwise the difference is shown
- A reconciliation difference without a comment blocks closing.

Pages: A18

#### ADM-037 — City Readiness and Waitlist [Launch-critical]

Rules:
- The system shows an indicator for each candidate city: coverage requests, contracted stores in each section, and registered drivers.
- A checklist is run before opening any city, including: boundaries, fees, settings, and the minimum number of stores and drivers.
- When the city opens, those who registered their interest receive a notification with a coupon
- Minimum to open a city: 20 restaurants, 3 Marts, 2 pharmacies, and 30 drivers. Opening coupon: 15 SAR on the first order with a minimum of 40 SAR, valid for 14 days, funded by the platform.

Acceptance criteria:
- A city is not opened before the checklist is complete

Pages: A09

#### ADM-039 — Contracting Targets List [Launch-critical]

Rules:
- Shows the stores that people ask for and that have not been added yet, ranked by: search terms with no results, "Suggest a Store" suggestions, and coverage requests.
- The merchants team uses this list to contract first with what people actually ask for.
- The customer is notified when the store they suggested is added in their city.

Acceptance criteria:
- Every suggestion made through "Suggest a Store" appears in the list

Pages: C02 C26

#### ADM-040 — Automated Marketing Messages [Important]

Rules:
- Rules: a cart left for an hour without payment, a registered user who has not ordered, a customer who dropped off; the event, timeout and template are settings.
- A low rating alerts support; a high rating suggests referral.
- Choosing timing and wording with AI is a later improvement; the rules work without it.
- An idle customer at a branch: has not ordered from it for the idle period (the single setting in MKT-001, 30 days by default). "Registered, never ordered" after 24 hours, and "Customer lapsed" after 30 days.

Acceptance criteria:
- Changing the timeout applies to new cases.
- An outage of the AI tool does not stop rule-based messages.

Pages: A17

#### ADM-041 — Operations Team Performance [Important]

Rules:
- On this page platform staff see the performance of every operations and support staff member in detail.
- The system shows for each staff member: alerts received and resolved, receipt time, resolution time, escalated, orders saved, calls, tickets and customer satisfaction, refunds requested, quality of handover notes, and shift hours.
- The page compares staff over the same period, and shows each staff member a profile with a log of their actions.
- Customer satisfaction after the ticket is closed, rated 1 to 5 stars.

Acceptance criteria:
- Each number opens the list of orders it represents.

Pages: A20

#### ADM-042 — Shift, Takeover, and Handover [Launch-critical]

Rules:
- Each staff member starts their shift by tapping "Take over", then reads and confirms the previous shift's notes
- A staff member ends their shift only with "Hand over". The staff member writes a note for each open order or alert under their name: what they did, what is pending, and what is needed next. These orders and alerts are then moved to the staff member on the next shift
- The system records the handover with both parties' names and the time.
- When two or three staff are on together, each alert is automatically distributed to one staff member in rotation according to their cities and current load, or the staff member takes it with the "Mine" button
- The name of the staff member appears on the order they are working on so other staff can see it. No other staff member takes action on the order except by transferring the order or by the supervisor's decision
- The supervisor distributes cities or services among staff, and redistributes alerts.
- Quality of shift handover notes is rated by the supervisor on a weekly sample.

Acceptance criteria:
- Handover is not closed if it contains an open alert without a note
- Two staff members do not work on the same alert at the same time.

Pages: A02 A19 A20

#### ADM-043 — Operations and Support Permissions [Launch-critical]

Rules:
- Ready-made roles: admin, support supervisor, support agent, operations, finance, and sales (ADM-001). The support agent cancels the order after the time limit, refunds the amount, and sets the loss charge or penalty and the liable party with a written reason (ORD-004, PAY-025).
- Within the role's financial limit, a cancellation, refund, loss charge, or penalty does not need a second approval, and anything above it is approved by a higher role.
- Every financial action is recorded with the executor, time, reason, and values before and after. No operations code and no automatic penalty decision.
- The default distribution of permissions across roles, including disabling, ban, exclusion, catalogs, preferred captain, instant incentive, wallet freeze, points, and sensitive data, is in the "Roles and Permissions" table, which is its reference, and the admin edits it.
- A financial limit per decision is mandatory: support agent 50 SAR, support supervisor 200 SAR, and anything above goes to admin.
- "Driver supervisor" is the operations role; the steps of the driver penalty ladder belong to operations and the support supervisor (DRV-023).

Acceptance criteria:
- A support agent cancels an order after the time limit, the amount is refunded to the customer, and the liable party and reason are recorded.
- An operations staff member does not see the cancel button or the refund button.
- The system does not issue an operations code or an automatic penalty.

Pages: A03 A04 A13 A19 A22 A26

#### ADM-044 — Targeted Instant Incentive [Important]

Rules:
- When launching an instant incentive, platform staff choose the target audience: all drivers in a city or area, specific drivers, or a group.
- The ready-made groups are: most active this week, those online now, those stopped within a distance, a specific level, those who have not worked for a while, and those with a rating above a threshold.
- Platform staff save groups with their conditions to use them again.
- The amount, duration, upper limit, and expected cost before launch

Acceptance criteria:
- The incentive is not shown to a driver outside the group.
- The incentive stops at its upper limit

Pages: A11

### Support (SUP)

#### SUP-001 — Access to Support [Launch-critical]

Rules:
- From the order page, the customer sees self-help buttons according to the order status, before opening the chat: "Where is my order", "I want to cancel", "Missing item", "I did not receive it".
- The "Contact support" button opens the chat with the order context.
- The customer reaches support from the side menu in Settings: "Support", then "Help with an order" or "Help with the app".
- Currently the team provides support inside the app. Later, AI replies can be turned on from settings, with the chat transferred to a staff member
- The customer raises any problem with the payment or the amount to support from the order itself

Acceptance criteria:
- A ticket from the order carries the order number automatically
- Help buttons change with the order status
- Turning on the smart reply does not require an app update

Pages: C14 C21 A19

#### SUP-002 — Shortage, Damage, and Non-Delivery [Launch-critical]

Rules:
- An item report specifies the products, the reason, and a photo from the in-app camera; "I did not receive it" needs no photo.
- The evidence file gathers the route, staying within 100 m, communication, and photos, with no customer code.
- The actual loss is charged to the party whose responsibility is established after support review; it is not an automatic penalty.
- A support agent performs the refund or compensation; anything above their role's mandatory limit (ADM-043) is escalated.

Acceptance criteria:
- An "I did not receive it" report does not ask for a photo.
- The loss charge does not exceed the proven damage; anything above it is a penalty by a separate manual decision.

Pages: C19 C21 A19

#### SUP-003 — Reason and Cost Allocation [Launch-critical]

Rules:
- The system records the reason, the responsible party, and the evidence for every support decision.
- The charged merchant or driver has the right to object to the support decision within 7 days of the decision notification (SUP-006).
- The support decision is final for the customer: they cannot object to it, and they can open a general ticket that does not reopen the decision.
- The customer sees only the reason for the support decision and its outcome, not the liable party.

Acceptance criteria:
- When a decision is amended, a reversing entry is recorded

Pages: C21 A03 A04 A19

#### SUP-004 — Small Claims [Launch-critical]

Rules:
- No automatic refund: every report, small or large, is reviewed by a support agent who decides on the refund or compensation.
- This handling is not used to impose an automatic financial penalty; charging a responsible party requires evidence and conformity with the approved rule.
- No one bears an amount initially: the staff member determines the liable party at the time of decision (SUP-002).

Acceptance criteria:
- No amount is refunded for any report without a decision by a staff member recorded under their name.
- The reason and status of the refund are visible.

Pages: A19 A22

#### SUP-005 — Report Time Limit [Launch-critical]

Rules:
- The time limit for a customer report about a shortage, error, damage, or expiry is one hour from delivery (configurable value), in all sections including Mart; after that the report button disappears from the order and the report is not accepted.

Acceptance criteria:
- One hour after delivery, the report button does not appear, and the server rejects a report that arrives after that.

Pages: C19 C21

#### SUP-006 — Merchant and Driver Objection [Launch-critical]

Rules:
- The merchant or driver can object to any loss charge or penalty within 7 days of the decision notification (configurable value).
- The objection is decided within 48 hours of its submission; anything not decided is escalated to the support supervisor

Acceptance criteria:
- The system does not accept an objection that arrives more than 7 days after the decision notification.

Pages: MD08

#### SUP-007 — Refund Trust Limits [Launch-critical]

Rules:
- The system calculates a refund rate for each customer.
- If the refund rate exceeds a limit set by platform staff, a warning badge appears to the support agent on the customer's reports.
- If this recurs, the customer receives a notification and is then restricted.
- Restriction means the customer's reports are decided only by the support supervisor, and ordering remains available to them. Notification text: "We noticed many refund requests on your account; your upcoming reports will be reviewed by the support supervisor".
- The refund rate is calculated over the last 90 days and includes compensation; the default limit is 20% of orders.

Acceptance criteria:
- A report from a customer who exceeded the limit appears to the staff member with a warning badge and their refund rate.

Pages: C21 A13 A19 A22

#### SUP-009 — Mart Quality Guarantee [Launch-critical]

Rules:
- In the Mart section, the customer is refunded the value of a damaged or expired item if they submit a report with a photo within the time limit
- The refund to the customer is made after support review, and is charged to the party whose responsibility support establishes (SUP-002).
- The time limit for a damage or expiry report is one hour from delivery, like other reports (SUP-005).

Acceptance criteria:
- When a report with a photo about an expired item is made within the time limit, the item's price is refunded after support review, and the refund appears in the statement of the liable party

Pages: C19 C21 A19 A22

### Offers, Ads, and Loyalty (MKT)

#### MKT-001 — Coupons [Launch-critical]

Rules:
- These properties are set for each coupon: cities, stores, categories, customers, period, usage limit, budget, funding, and stacking.
- "First order" offers are granted once: they are not granted if the mobile number, device or payment method was previously used in an earlier first order. They are not granted to a device previously used with another account.
- The coupon targets the customer's segment relative to the branch: new (has never ordered from it), repeat (ordered from it within the idle period), or idle (ordered from it before, then stopped for the idle period). The idle period is a single setting, default 30 days, applying to coupons and campaigns (MKT-005).
- A coupon can be restricted to cards of a specific issuing bank, and it is then funded by the bank or the platform according to the agreement.
- A configurable setting determines whether the coupon may be combined with wallet balance, and platform staff turn it on or off

Acceptance criteria:
- A city coupon does not work outside it
- The last of the budget is not used twice
- A new account does not get a "first order" offer on a device that was used before.
- A coupon for the "idle" segment does not work for a customer who ordered from the branch within the idle period.

Pages: A14

#### MKT-002 — Repeat-Order Credit [Launch-critical]

Rules:
- The support agent sets the repeat-order credit manually for the customer: the amount and the reason, and it is added as promotional credit directly, without a reward awaiting collection (PAY-002).
- The promotional credit is used across several orders.

Acceptance criteria:
- A cancelled order does not consume repeat-order credit.
- Repeat-order credit is not granted without a recorded executor and reason.

Pages: C20 A13 A19

#### MKT-003 — Ad Placements [Launch-critical]

Rules:
- Banner ads and pinning in featured stores; no keywords or purchased search ranking.
- The platform sets the price of each placement, its city, duration, and capacity.
- The merchant sees the price before submitting the ad, and the amount is deducted from their dues after approval; no publishing and no deduction before approval.
- Disabling an ad for platform reasons refunds the unexecuted part; stopping at the merchant's request applies a placement policy visible before the request.
- If the merchant stops an ad at their request, the remaining full days are refunded, and the current day is not refunded.
- When an ad is approved and its amount deducted, the platform automatically issues the merchant an ad invoice: a separate tax invoice for its amount and its 15% VAT through Odoo (INT-010), and the deduction appears in their statement with its invoice number (MER-008). Advertising fees are not included in the fees invoice (PAY-022).
- Any refund from a stopped ad is issued as a credit note linked to the ad invoice.

Acceptance criteria:
- The price appears before the ad is submitted.
- No keywords field.
- A 100 SAR ad is approved: 115 is deducted from the merchant's balance and its invoice of 100 + VAT 15 is issued immediately, and it does not appear on the fees invoice.

Pages: MD05 A08 A16

#### MKT-005 — Store Customer Campaigns [Launch-critical]

Rules:
- The merchant targets their store's previous customers through the platform by segment, city, and zone.
- The merchant does not get customers' numbers; audience counts and results are shown.
- Frequency limits, budget, and templates are set by the platform.
- Store customer campaigns have a price that the platform sets per region and per city and can change at any time, and a price of zero makes them free; the merchant sees the price before sending, the campaign goes through platform approval, and its price is deducted from the branch's dues after approval with a separate tax invoice like an ad (MKT-003). Segments: new, repeat, and lapsed with the same inactivity period as in MKT-001.

Acceptance criteria:
- Results are aggregated and do not reveal customers' numbers.
- The zone excludes a customer who is not served.
- The platform set one campaign price in Riyadh and another in Jeddah: a merchant in Jeddah sees the Jeddah price before sending, and nothing is deducted before approval.

Pages: MD05 A14 A17

#### MKT-007 — Offers and Funding [Launch-critical]

Rules:
- A platform offer is created by the platform, and an eligible branch subscribes to it directly without review, so it is activated as soon as the branch subscribes with the funding share that the platform sets for each party as an amount or a percentage.
- A merchant offer is created by the merchant and fully funded by them, and it shows to them as "Under review" until the platform approves; if the platform wants to share in funding it, it creates it as a platform offer on their behalf.
- Each offer has cities, branches, products, duration, stock, minimum, budget, and a combining rule.
- Its funding is percentages or amounts per party; the actual cost is split and double deduction is prevented.
- An order can combine a delivery offer with one discount offer on products; two discount offers on products do not combine, so the system applies the one that saves the customer the most after its conditions are verified; the applied sequence is saved on the order.
- A discount funded by the platform does not reduce the base of the merchant's commission; the merchant's share of the discount reduces it.
- If a merchant's offer is rejected, they see the reason, edit it, and resubmit.
- Ending a branch's subscription to a platform offer takes effect immediately for new orders.
- Subscription to a platform offer is per branch, and the merchant manager can select all branches with one click.
- The merchant's funding share is fixed when their branch subscribes; raising it suspends their subscription until they approve the new share, and lowering it takes effect immediately.

Acceptance criteria:
- An offer outside the branch zone does not appear.
- Subscribing to a platform offer does not enter review.
- A funding share does not exceed the offer's cost.
- The platform raising the merchant's share in an existing offer suspends its branches' subscriptions until the merchant approves, and nothing is deducted from the merchant at the new share before their approval.
- An order with a free delivery offer and two product discount offers of 20% and 30%: free delivery and the 30% discount alone are applied.

Pages: MD04 A08 A14

#### MKT-008 — Merchant Ads [Launch-critical]

Rules:
- The merchant designs their ad (banner or pin) from the placements that the platform provides.
- The ad starts with the status "Pending approval", then is approved or rejected.

Acceptance criteria:
- An unapproved ad does not appear
- Rejection does not deduct spend

Pages: MD05 A16

#### MKT-010 — Customer Loyalty via OpenLoyalty [Important]

Rules:
- Points and rules are managed through OpenLoyalty; the Mahallat ledger is the financial reference and the integration carries events with unique IDs.
- Order points come from the platform's net after the offer funder, the coupon, and the Moyasar fee; a base ≤0 gives no points.
- Points are pending until the end of the report time limit (SUP-005) and are withdrawn on refund.
- Value, limit, expiry, and cap per city or period, and the multiplied points that the merchant buys, are settings.
- An outage of the tool does not stop the order; the event is re-synced without duplicate points.
- Points can be redeemed from 500 points, and expire after 12 months.
- The points-to-riyal conversion rate is a configurable setting that platform staff set per city or period, and it has no fixed value in the code; the page shows the value in SAR according to the rate in effect.

Acceptance criteria:
- A duplicate event does not duplicate points.
- The financial liabilities of the points are shown in SAR.

Pages: C19 C23 A15

#### MKT-013 — Referral via OpenLoyalty and Adjust [Important]

Rules:
- An invitation link whose source is measured via Adjust, with referral prizes carried out by OpenLoyalty rules.
- After the invitee's first completed order, both parties become entitled to the referral prize set for their city and period.
- The prize stays pending until the end of the report time limit (SUP-005) and is withdrawn if the order is refunded; repeated first-order offers are prevented by device, number, and payment method.
- The type is credit, coupon, or free delivery, and the cost is a funded liability.
- The default referral prize is 15 SAR as promotional credit for each party, and its value is shown on the invitation page.

Acceptance criteria:
- The link source does not grant a prize before the order is verified.
- Replaying the payment event does not duplicate the prize.

Pages: C23 A15

#### MKT-014 — Quality Badge [Launch-critical]

Rules:
- A quality badge is shown to the customer on stores that meet the thresholds set by platform staff.
- The thresholds include rating, order count, and the MER-026 indicators
- The name shown to the customer is "Quality", it is calculated per branch over the last 30 days, and the merchant sees the required numbers.
- Default thresholds: rating 4.5 or higher, at least 50 orders, preparation-time overrun under 10%, and reports under 2%.

Acceptance criteria:
- If the branch falls below the thresholds, its badge is dropped.

Pages: C01 C02 C03 C04 C05 C06 C07 MD01 MD14 A22

#### MKT-015 — Ad Spend Dashboard [Important]

Rules:
- Each branch's page shows its ad spend and the promotional credit it funded for its customers (PAY-002).
- The page shows the orders and new customers resulting from each ad.

Acceptance criteria:
- The ad spend shown to the merchant on the page matches the merchant statement.

Pages: A16

#### MKT-016 — Store Loyalty [Later]

Rules:
- The store offers its own loyalty program, in which the customer earns a discount after spending a set amount at the store.
- The merchant bears the discount only when the customer uses it.

Acceptance criteria:
- The system does not count what the customer spends at another store.
- The system does not deduct from the merchant before the discount is used.

#### MKT-017 — Recurring Hour Deal [Launch-critical]

Rules:
- The hour offer is a platform offer with a schedule and stock, not a separate type: the branch subscribes to it by choosing a product, a discount of at least 30%, stock, and a schedule: one time or recurring days, with a start and end hour.
- It publishes automatically when the discount is 30% or more and the conditions are met; no individual approval for each recurrence.
- The countdown runs to the end of the scheduled period for everyone; there is no separate hour per customer.
- Running out of deal stock or the end of the period stops it; the usual price returns, and a recurring deal runs again in its next cycle.
- Hour Deal limit: one item per customer in the period.
- The branch bears the full Hour Deal discount.

Acceptance criteria:
- 30% is eligible to publish.
- A 5-6 deal ends at 6 even for a customer who entered at 5:50.

Pages: C22 MD04 A14

### Services (EXT)

#### EXT-004 — Pharmacies [Launch-critical]

Rules:
- There is a separate section for write-in orders ( PHR-012 ).
- The pharmacist reviews the order and the prescription before attaching the products invoice ( PHR-012 ).

Acceptance criteria:
- The driver does not see the prescription content

Pages: C06

#### EXT-006 — Self-pickup [Launch-critical]

Rules:
- For menu orders outside Mart: the customer orders and pays, and after the 60-second cancellation window (ORD-002) the order reaches the merchant without a driver or delivery.
- No self-pickup for Mart, nor for write-in and pharmacy orders at launch.
- Discount and distance follow the branch setting and its funder.
- The Ready page stays, with directions, a reminder, and a notification after 60 minutes; no customer code.
- The merchant confirms pickup by order number. If the customer does not show up by the end of business hours, the order enters "Awaiting support decision" for the reason "No-show", and the support agent decides what is captured and what is refunded, then it is closed (ORD-001).
- After 15 minutes with no driver, conversion becomes available for 5 minutes; the delivery fee is refunded, and the conversion discount is borne by the platform.
- No extra discount when converting to self-pickup at launch: only the delivery fee and the tip are refunded; the conversion discount is a setting whose default value is zero.
- Self-pickup shows stores in the customer's city within 10 km (a per-branch setting). An order is blocked if the expected readiness is after the branch closes.
- The 60-minute notification is counted from "Ready", and reaches both the customer and the merchant.

Acceptance criteria:
- The page is kept without a code.
- Conversion reverses delivery once.
- Customer cancellation within 60 seconds prevents the order from reaching the merchant.
- An order whose owner did not show up stays "Awaiting support decision", and is not captured or closed before the decision.

Pages: C15 C16 C24 M01 M03 A02 A03 A06

#### EXT-007 — Delivery for Store Channels [Later]

Rules:
- A service in which the platform's drivers deliver store orders that come from the stores' own channels
- The service is enabled after licensing requirements are confirmed.

Acceptance criteria:
- The system does not enable the service before licensing requirements are confirmed.

#### EXT-008 — Business Accounts [Later]

Rules:
- An account for businesses that is issued a tax invoice carrying the buyer's tax number
- Spending limits for employees

Acceptance criteria:
- If an order exceeds the employee's spending limit, the order does not complete.

#### EXT-012 — Nupco Integration for Medicine Delivery [Later]

Rules:
- Nupco medicines are delivered through the platform in a later phase.
- The service's orders appear in the unified operations room as a separate service with its own filter
- The system applies the pharmacy rules: privacy, the driver not seeing the prescription, the cooler bag, and return by code.

Acceptance criteria:
- The Nupco service is added as a row in the services table, without modifying the operations room

### Service Integrations (INT)

#### INT-001 — Moyasar [Launch-critical]

Rules:
- Sandbox environment, then production
- Daily reconciliation with the Moyasar report
- All displayed payment methods support authorization then capture through Moyasar (PAY-001).
- Split payment is always enabled and there is no setting to disable it: each order's share is split into its branch wallet at Moyasar, and Moyasar transfers the wallet balance to the bank only when an approved payout order arrives from the platform (PAY-006).

Acceptance criteria:
- Successful, failed, and refunded payments appear in their correct state.
- Before launch, the results of the authorization, capture, cancellation, and refund trial are documented for each approved payment method, and what concerns Moyasar is confirmed in writing. This is an item in the manual acceptance checklist (SYS-014).
- Before launch, splitting into branch wallets, executing the payout order from them only upon approval, and deducting from them are tested, and whatever concerns Moyasar is confirmed in writing. This is an item in the manual acceptance checklist (SYS-014).

Pages: A18 A22

#### INT-014 — STC Pay: driver payouts [Later]

Rules:
- At launch, driver dues are paid out by bank transfer after approval (PAY-006); the STC Pay integration replaces it later under the following rules.
- A direct integration with STC Pay to pay out freelance driver dues after the accountant's approval; each payout carries the STC Pay transaction number as its reference.
- The driver adds an STC Pay wallet number in their name in their details (D10), and Finance approves it after matching the holder's name; payouts are not made to a new number before it is approved, and the previously approved one stays active until then.
- In the payout cycle, each freelance driver's net enters the approval list (PAY-006) after their negative balance is deducted (PAY-026), and is sent only after it is approved; no line is created for a zero or negative net.
- The system prevents duplicate payouts: one key per driver and period, and resending never pays twice.
- The payout appears to the driver in D07 and to Finance in A18 with its status: in progress, sent, or failed; a failed payout is not counted as paid and appears to Finance to be retried.
- Every payout through STC Pay needs a recorded approval (PAY-006, ADM-002), including the driver deposit refund and the account-closure settlement (PAY-024).
- An STC Pay outage does not stop orders; payouts wait and are sent when it returns, without duplication.

Acceptance criteria:
- A freelance driver with a net of 250 SAR in the payout cycle appears in the approval list, and does not receive the payout through STC Pay before it is approved.
- A new STC Pay number awaiting Finance approval is not paid to before approval.
- Re-running the payout job on the same day does not create a second payout for the same driver and period.
- A failed payout does not appear as paid, and appears to Finance to be retried.
- A driver whose net after deducting the negative balance in their dues account is zero or less gets no payout created.

Pages: D07 D10 A18 A22

#### INT-004 — Notifications and Messages [Launch-critical]

Rules:
- OneSignal for notifications, with central Arabic and English templates from the admin dashboard.
- Order events are independent of marketing; each event has an ID that prevents duplicate sending and a link that opens the correct order.
- Audience: specific customers, city, store, spend, order recency, purchase frequency; store offers are limited to its branch zone.
- AI-suggested text and audience require platform staff approval before sending.
- Login codes go through the provider approved in INT-SEL; no hard-coded text inside the screens.
- The customer has a notifications page showing order and offer notifications for the last 30 days (C26).

Acceptance criteria:
- The order link checks user ownership.
- Adding a language does not require rewriting the screens.

Pages: C26 A17

#### INT-008 — PostHog and Adjust Analytics [Launch-critical]

Rules:
- PostHog for visit analytics, customer journey, conversion, and product events; Adjust for measuring source, links, and attribution.
- Events do not include sensitive financial data, messages, or prescriptions; data permissions are respected.
- The integration is analytical; if it is disabled, purchasing does not stop.

Acceptance criteria:
- Analytics does not duplicate the order and does not block payment.

Pages: A22

#### INT-009 — Store Links [Launch-critical]

Rules:
- The link opens the store inside the app on iOS and Android, or opens the app store to download it.

Acceptance criteria:
- When a link to a deleted branch is opened, the platform shows an understandable alternative.

Pages: MD09 MD13

#### INT-010 — Odoo [Launch-critical]

Rules:
- Accounting, settlements, and platform invoices
- All invoices are issued automatically through Odoo on command from the platform system (admin dashboard); no staff member issues an invoice manually inside Odoo: the platform invoice for the order, the merchant's monthly fees invoice, the ad invoice, cashier invoices, and the credit note on refund.
- The system sends the issue command at the event: the platform invoice when the order is captured, the fees invoice at month close, the ad invoice when the ad is approved and its amount deducted, and the credit note on refund; it saves the invoice number and link on the order, statement or ad and sends it to the customer or merchant.
- If Odoo is down, issuing commands queue and are retried automatically in order without duplicates, and the number pending is shown in Accounts.
- Odoo is connected to the ZATCA Fatoora e-invoicing system: every invoice and credit note the platform issues is issued as an approved e-invoice there.

Acceptance criteria:
- An Odoo outage does not stop orders
- Capturing an order issues the platform invoice in Odoo with no staff involvement, and its number appears in the order file.
- Repeating the issue command for the same order does not create two invoices.
- The platform invoice for a captured order appears as approved in Fatoora, and its number is saved on the order.

Pages: A18 A22

#### INT-011 — AI Assistants via MCP [Launch-critical]

Rules:
- Queries and reports in plain language within the user's permissions; read-only by default.
- Any financial change requires explicit approval from inside the admin dashboard, and applies the role limits.
- Queries and edits are logged; no access to a branch or city that is not permitted.

Acceptance criteria:
- An unauthorized request is rejected.
- No penalty or transfer is executed merely by text in a conversation.

Pages: A21 A26

#### INT-012 — Partner API [Important]

Rules:
- The platform provides a documented API for partners, cashier systems, and intermediary platforms.
- The API covers orders, menu, stock, and branch status.
- It has a sandbox environment
- The platform adds order management inside the cashier system when its providers request it.
- It is not a launch requirement: it is built after the cashier integration, and covers restaurants and Shops with a menu and Mart, excluding pharmacies.

Acceptance criteria:
- The partner can access only the data of the branches linked to it.

Pages: MD13

#### INT-013 — Call Center [Later]

Rules:
- A later integration, not a core one, and not a launch acceptance requirement.
- Masked one-click calling, call reception and distribution, and recording them against the order and the employee.
- Before integration, tickets, chat, and the basic communication channels keep working.

Acceptance criteria:
- Not running the call center does not block orders or support.

Pages: A19 A20 A22

### Pharmacies (PHR)

#### PHR-003 — Wasfaty Prescriptions [Later]

Rules:
- The system places a tag on a pharmacy that participates in "Wasfaty".
- The medicine in a "Wasfaty" order is dispensed at a value of zero, and the customer pays the delivery fee only.

Acceptance criteria:
- The system does not charge a price for the medicine in a "Wasfaty" order.

Pages: C06

#### PHR-008 — Privacy in Notifications [Launch-critical]

Rules:
- System notifications and mobile messages for pharmacy orders do not mention the name of any medicine.
- They suffice with the phrase "Your order from the pharmacy" in the notification.

Acceptance criteria:
- The system does not display a medicine name in any notification for a pharmacy order.

Pages: C06 C11

#### PHR-010 — Non-response on a Medicine Order [Launch-critical]

Rules:
- The status of a medicine order that was not delivered is "Returning to the pharmacy", and the driver returns the medicine to the pharmacy at the return stop within the same task
- The return is done by a code like the pickup code, and the pharmacy enters this code.
- The return window is configurable. After it ends, an alert reaches operations to decide, even if the pharmacy has closed
- The customer does not get the delivery fee back, and gets back the medicine price and the 5% service fee after the pharmacy confirms the return is intact. Rejecting the refund is a support or operations decision based on the pharmacy's confirmation.
- The default return window is 60 minutes.
- Re-delivering the medicine to the customer is a new order with a new delivery fee.
- No extra pay for the driver for the return stop; the driver has earned the full pay and tip.
- Medicine whose refund was refused is kept by the pharmacy in the customer's name for 7 days (setting), and it is re-delivered with a new order in which the customer pays only the delivery fee; after that period it is destroyed without a refund, and this is recorded in the order file.

Acceptance criteria:
- A medicine order is not closed before the return code is entered or an operations decision is issued.
- When the window ends, an alert reaches operations.
- Medicine 100 and service 5 returned intact: 105 is refunded to the customer and the delivery fee is not refunded.
- Medicine whose refund was refused and whose delivery the customer did not request within 7 days: "Destroyed" is recorded in the order file and nothing is refunded.

Pages: D06 D15

#### PHR-012 — Pharmacy Order [Launch-critical]

Rules:
- The customer writes the order, attaches the prescription if there is one, then pays delivery first ( ORD-013 ).
- Before sending, the customer sees a message: if the medicine requires a prescription and the customer did not attach it, the order is canceled
- The pharmacist reviews the order and the prescription, then prepares the order, and attaches the products invoice and its amount.
- 5% is added to the customer, then the customer pays, and after that the driver picks up the order.
- When a prescription medicine is ordered without a prescription, the pharmacist rejects the order before uploading the products invoice, so the order enters "Awaiting support decision"; the support agent decides how much of the delivery fee is refunded and how much is paid to the driver, with the reason recorded, then it is closed. The customer receives a cancellation notification.
- The driver does not see the prescription

Acceptance criteria:
- A pharmacy order rejected for lack of a prescription stays "Awaiting support decision" and is not closed before the support decision on the delivery fee.

Pages: C06 C17 C18 A03

### Reports (REP)

#### REP-001 — Custom Date Range [Launch-critical]

Rules:
- Every report or metrics page inside the admin or merchant dashboard and driver performance combines the ready-made shortcuts and a custom option.
- Custom allows a start and end date in Riyadh time; the screen, export, comparison, and scheduling use the same period.
- The view saves the period and the filters; a start after the end is prevented, and the screen clarifies whether the end day is included.
- The default includes the whole end day using a query bound before the start of the next day; the tier indicator stays at the last 30 days regardless of the view filter.

Acceptance criteria:
- A period from the 3rd to the 7th includes the whole of the 7th.
- A range with a start after the end does not run.
- Exporting the period matches the screen's numbers.

Pages: MD01 MD06 A21

### Build and Operations (SYS)

#### SYS-001 — One Project with Non-overlapping Modules [Launch-critical]

Rules:
- Each module is a folder with a public interface and its own tables, and no module reads another module's tables
- A check tool runs in every build and prevents this.
- A new service (such as Taxi) is a module that uses the dispatch, pricing, payments, and finance modules

Acceptance criteria:
- The build fails if a module reads tables belonging to another module.

#### SYS-002 — Fees, Durations, and Operating Limits in Settings [Launch-critical]

Rules:
- Sections, store types, statuses, fees, tiers, incentives, the home page, and roles are stored in admin dashboard tables and settings. This lets authorized platform staff change them without releasing a new version.
- The code reads the section's property and does not depend on its name.

Acceptance criteria:
- When a new section or a new tier of the supported types is added, the addition is done from settings without development.

Pages: A22

#### SYS-003 — Order, Task, and Trip [Launch-critical]

Rules:
- The driver task is independent of the order and has pickup, delivery, and return stops; the trip groups tasks according to a configurable capacity with a default of 3.
- The order has separate payments for each purpose, status, and reference, including the two write-in payments.
- Contract versions are date-bound; a shared task structure extensible for the deferred Taxi.

Acceptance criteria:
- A change in payment status does not falsify delivery.
- Batching preserves the order of the stops and the time of each order.

#### SYS-004 — Internal Events [Launch-critical]

Rules:
- Every significant change fires an event. The event is written together with the change itself, then distributed in the background
- Notifications, accounting, and reports listen to these events, and a new feature is added as a new listener

Acceptance criteria:
- If notifications fail, the order does not stop.

#### SYS-005 — Durable Scheduler for All Timeouts [Launch-critical]

Rules:
- Timeouts and scheduling are in the database, and resume after a server restart.
- The server clock is the reference for timeouts and statuses; device events are recorded evidence.
- Repeating a scheduler task does not repeat a cancellation, refund, notification, or ledger entry.

Acceptance criteria:
- A server restart does not lose the expiry time of a write-in invoice.

#### SYS-006 — Feature Flags and Remote Configuration [Launch-critical]

Rules:
- A flag per feature and city; it starts off, then a pilot city, then rollout.
- The app fetches the minimum allowed version, the flags, the translations, and the home page order from the server.
- Changing content and settings does not require a store update; app code changes are distributed according to the release mechanism appropriate to the platform.

Acceptance criteria:
- Disabling a section in a city does not need a new release.
- The setting does not override the minimum supported version.

Pages: A22

#### SYS-007 — Server-driven Home [Launch-critical]

Rules:
- The server sends the home page as ordered blocks per city.
- The app ignores any block it does not recognize.

Acceptance criteria:
- When a seasonal row is added from settings, it appears in the app without a new release of it.

#### SYS-008 — Versioned APIs [Launch-critical]

Rules:
- Change within a version is additive only.
- Old versions of the apps keep working.

Acceptance criteria:
- When the server is updated, the old app version does not break.

#### SYS-009 — External Services Adapter [Launch-critical]

Rules:
- Moyasar, the cashier, maps, messages, and the call center are behind separate interfaces and adapters, each with a sandbox substitute without real keys.
- The reference result used is saved on the order, so switching the provider does not change times or constraints of old orders.

Acceptance criteria:
- Replacing the provider does not change the calculation of a completed order.

#### SYS-010 — Preventing Duplicate Operations [Launch-critical]

Rules:
- Every command that creates an order or moves money carries a unique key.
- When the network is weak, the system does not create two orders and does not transfer money twice.

Acceptance criteria:
- When the same order is resent, the system does not create a second order.

#### SYS-011 — Reports from a Read Replica [Launch-critical]

Rules:
- Reports and the AI assistant read from a separate replica
- The definition of each metric is written once.

Acceptance criteria:
- If a heavy report is run at peak time, orders do not slow down.

#### SYS-012 — Administrative Levels, Currency, and Time Zone [Launch-critical]

Rules:
- One administrative-levels table with a hierarchy (country, region, city), and each level inherits settings from the level above it
- A currency field next to every amount
- Times are stored in UTC with the city's time zone, and tax is stored with an effective date

Acceptance criteria:
- A setting specific to a city applies to it alone, and the rest of the region's cities inherit the region setting or the global setting.

Pages: A22

#### SYS-013 — Translation and Notification Templates [Launch-critical]

Rules:
- No hard-coded text inside the screens
- A new language, such as Urdu, is added as data rows

Acceptance criteria:
- When a new language is added, no screen changes are needed.

Pages: A17 A22

#### SYS-014 — Environments and Automated Testing [Launch-critical]

Rules:
- There are three environments: development, staging, and production, each with a separate database and keys.
- There are test builds of the three apps, a fake city, and a "driver simulator".
- Every acceptance criterion has an automated test carrying its ID, and every row in "financial operation examples" has a test in which amounts are computed in halalas
- Procedural criteria that are not tested automatically (such as the Moyasar trial before launch in INT-001, and the monthly restore drill in SYS-015) are tracked in a manual acceptance checklist under the same ID, and do not block deployment.
- Automated tests run with every change, and deployment is blocked if any of them fails.
- The "financial operation examples" tests are adopted after the accountant approves the base and tax table (PAY-029).

Acceptance criteria:
- A deployment with a failing automated test is rejected

#### SYS-015 — Monitoring and Backup [Launch-critical]

Rules:
- An availability check every minute. An alert reaches the owner's mobile when errors rise, payment fails, Moyasar notifications stop, scheduled jobs pile up, or the messaging balance runs out
- A tool that collects errors with the version number, logs carrying the order number, and a "failed events" list with a retry button
- An automatic daily backup, with the ability to restore to any moment within 7 days. The backup includes images, invoices, and prescriptions, and the restore is tested monthly

Acceptance criteria:
- The monthly restore test succeeds and its result is recorded.

#### SYS-016 — Secrets and Signing Keys [Launch-critical]

Rules:
- Secrets are kept on the server only, and are not placed in the apps or the repository.
- App signing keys, store accounts, and service passwords are kept in a vault under the platform's name

Acceptance criteria:
- The apps' code contains no secret key.

#### SYS-017 — Performance Targets [Launch-critical]

Rules:
- 95% of server requests under 500 milliseconds, and the home page under 2 seconds on a mid-range phone.
- After acceptance or assignment, the order reaches the merchant's device and the task reaches the driver within 3 seconds.
- Location is sent every 20 seconds by default; it is displayed in under 10 seconds from receipt, and the last update time is shown.
- The target monthly availability is 99.5% in the first year; last location in fast memory and bulk messages in batches.
- A load test of 400 drivers sending every 5 seconds to test a margin above the operating setting.

Acceptance criteria:
- The load test passes without losing events or an order being linked to two drivers.
- An old location of 120 seconds is excluded from new dispatch.

#### SYS-018 — Weak Network [Launch-critical]

Rules:
- The driver saves their events with the device time and location and sends them in order when connected.
- The operational decision time comes from the server; the device time is evidence corrected by the last sync offset, and it does not revive a finished order or cancel a new acceptance or assignment.
- The merchant's order comes through a live connection, with a notification, periodic polling, and the automated call as fallbacks.
- A customer disconnection after payment does not duplicate the order; no delivery code is saved for the customer.

Acceptance criteria:
- A late event does not reopen a closed task.
- Re-paying does not create two orders.

#### SYS-019 — Gradual Rollout [Launch-critical]

Rules:
- The platform launches in all cities at once, while keeping the per-city feature toggles to stop a city when needed.
- Cities and sections are opened with the flags and the city checklist ( ADM-037 ).
- App updates are published in the stores to a percentage of users first

Acceptance criteria:
- A new city is opened with a flag without a new release.

Pages: A22

#### SYS-021 — Maps and Call Cost [Launch-critical]

Rules:
- Google Maps is the reference for the branch-to-customer route duration; the live location comes from the driver's device.
- Distance and duration estimates between recurring locations are cached, and arrival is updated at an interval or on a significant change.
- The arrival distance of 100 m is computed geographically without a paid call.
- A daily and monthly cap and a visible cost; when it is reached, a saved estimate is used without stopping the order.
- No automatic penalty calculation is tied to a maps call.
- The default Google Maps cap is 3,000 SAR monthly and 150 SAR daily; after it, the saved estimate is used if available, otherwise pricing distance is air distance × road factor (PAY-013).

Acceptance criteria:
- Updating each location does not call a distance matrix.
- Reaching the cap does not stop the order.

Pages: A22

### Migration from the current platform (TRN)

#### TRN-001 — Opening balances [Launch-critical]

Rules:
- Finance enters each customer's, driver's and merchant's balance from the approved statement of the current platform as an opening balance in their new wallet.
- Each entry with the reason "Opening balance" and the statement reference, and it needs a second approver (ADM-002), and it is recorded in the ledger (PAY-005).
- The merchant's opening balance is paid from the platform's bank in the first approval cycle (PAY-006), and does not pass through the branch wallet at Moyasar (Appendix PAY-005, entry 29b).

Acceptance criteria:
- The total of opening balances matches the current platform's statement to the halala.
- An opening balance not approved by a second approver does not appear in the wallet.

Pages: A18

#### TRN-002 — Onboarding from current platform data [Launch-critical]

Rules:
- A one-time export, with the data owner's consent, of merchant and branch names, images, and driver documents to prefill registration.
- The menu and its prices (store price and selling price) are entered manually by platform staff.
- No balances or contracts are exported.

Acceptance criteria:
- A merchant who did not consent does not have its data prefilled.

#### TRN-003 — Freezing the current platform [Launch-critical]

Rules:
- New orders stop on the current platform 3 days before the migration, to complete refunds, payouts, reconciliation, and the approval of balance statements.

#### TRN-004 — Current platform archive [Launch-critical]

Rules:
- The current platform's orders, invoices, payments and tickets are exported to a searchable archive that finance and support can read, then the old system is shut down.
- Retention period per the data retention policy (Q-06).

#### TRN-005 — Mandatory update of the current apps [Launch-critical]

Rules:
- Before the migration, an update to the current apps is published that reads the "minimum version" from the server, so old versions show "Update required" on migration day instead of crashing. This is the first delivery in the program (SYS-008).

Acceptance criteria:
- An old version opened after the migration shows "Update required" and the store link, and does not crash.

#### TRN-006 — Stopping express shipping [Launch-critical]

Rules:
- The "express shipping" service stops when the current platform is shut down, and is not built in the new platform.

### Taxi (TAX)

#### TAX-FND — Deferred Taxi Foundation [Deferred foundation]

Rules:
- Set up an independent service module, activation flags, a task type, and compatibility with dispatch, pricing, and payments.
- No operating screens and no Taxi trips or eligibility at launch.
- No start code or customer code in the approved foundation; details of the future launch are decided later.

Acceptance criteria:
- The apps do not display an active trip request.
- Disabling the foundation does not affect delivery.
