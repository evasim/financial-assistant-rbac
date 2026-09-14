# RBAC Schema — Nexora Retail Holdings Inc.

This document defines the three access tiers used throughout this project's
document store and financial statement data. Every document and data field
in this dataset is tagged with one of the tiers below.

## Tier 1: Executive (role = "exec")
Maps to: CFO
Access: Full visibility — all financial statements at full line-item detail,
all department budgets, executive compensation, M&A activity, board-level
strategic notes, and all Tier 2 / Tier 3 content.

## Tier 2: Manager (role = "manager")
Maps to: Finance Director, Treasury Manager, FP&A Manager
Access: Full detail within their own department (e.g. Treasury Manager sees
all treasury data — cash position, investment portfolio, debt covenants) plus
company-wide *aggregated* figures (total revenue, total net income) without
other departments' line-item detail. Cannot see executive compensation,
M&A activity, or board-level strategic notes.

## Tier 3: Staff (role = "staff")
Maps to: Accounting Manager, Tax Manager, Business Partnering, Business
Intelligence
Access: Operational data relevant to their own function only (e.g. Tax
Manager sees tax filings only, not payroll or treasury data). Cannot see
other departments' data, company-wide budget figures, or any Tier 1/2
strategic content.

## Financial statement field-level tagging (for the RAG retrieval layer)

| Statement          | Field(s)                                              | Min tier required |
|---------------------|--------------------------------------------------------|--------------------|
| Income Statement    | revenue, gross_profit, net_income (aggregate totals)   | manager            |
| Income Statement     | expense breakdown by department (marketing, logistics, it, ga, payroll) | manager (own dept only) |
| Income Statement     | full line-item detail, all departments                 | exec               |
| Balance Sheet        | total_assets, total_liabilities, total_equity (totals) | manager            |
| Balance Sheet        | debt covenant detail, investment portfolio breakdown    | manager (treasury only) / exec |
| Cash Flow Statement  | ending_cash_balance (total only)                        | manager            |
| Cash Flow Statement  | full financing activity (dividends, debt repayment)      | exec               |
| Payroll figures       | aggregate payroll expense                                | manager            |
| Payroll figures       | individual/department payroll detail                     | staff (accounting only) / exec |

This table is what your RBAC-aware retrieval agent should reference: given a
user's role, filter both the narrative documents *and* which statement fields
are returned, not just which files are visible.
