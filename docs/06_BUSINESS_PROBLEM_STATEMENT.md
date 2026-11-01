# StayWise AI — Business Problem Statement

## 1. Industry Context & Motivation

Hotel revenue management and hospitality operations operate in an environment characterized by perishable inventory, dynamic demand volatility, high customer acquisition costs, and significant cancellation risk. 

When a hotel room sits vacant on any given night, that revenue opportunity is lost forever. Conversely, high cancellation rates (averaging over 37% in this dataset) force properties into risky overbooking strategies, leading to involuntary guest reassignments, operational strain, and customer dissatisfaction.

To achieve sustainable profitability, hotel operators must bridge the gap between retrospective reporting and actionable operational intelligence.

---

## 2. Key Stakeholder Personas

1. **Hotel General Managers & Owners**:
   - Focus: Overall property performance, portfolio revenue trajectory, brand reputation, occupancy stability, and long-term channel strategy.
2. **Revenue Managers & Yield Analysts**:
   - Focus: Pricing strategies (ADR), lead-time curves, deposit policy enforcement, cancellation forecasting, customer segment profitability, and minimizing distribution intermediary fees.
3. **Front Desk & Operations Managers**:
   - Focus: Daily check-in volumes, room allocation conflicts (reserved vs assigned room mismatches), guest staffing needs, meal inventory planning, and special service execution (parking, baby cribs).
4. **Sales & Distribution Strategy Teams**:
   - Focus: Channel mix optimization (Direct vs Online Travel Agencies vs Corporate Contracts), travel agent productivity, and repeat guest loyalty growth.

---

## 3. Ten Core Analytical Business Questions

The StayWise AI platform is specifically engineered to answer the following ten questions through deterministic analytics and conversational AI:

1. **Demand & Cancellation Trends**: How do booking volumes and cancellation rates fluctuate seasonally and year-over-year across City and Resort properties?
2. **Property Comparison**: What fundamental differences exist between City Hotels (high-volume, corporate/short-stay) and Resort Hotels (leisure, longer lead times, family stays)?
3. **Channel Performance**: Which distribution channels and market segments generate the highest gross reservation volume?
4. **Cancellation Risk by Channel**: Which distribution channels suffer from the highest cancellation rates, and what is the associated lost room-night impact?
5. **Driver Analysis of Cancellations**: How do lead time, deposit type (Non-Refundable vs No Deposit), repeat-guest status, and customer contract type influence the probability of cancellation?
6. **Rate & Value Dynamics (ADR)**: How do Average Daily Rates (ADR) and estimated booking values vary across seasons, property types, and customer segments?
7. **Operational Room Allocation**: How frequently are guests assigned a different room type than originally reserved, and what proportion of reassignments occur without guest-initiated booking changes?
8. **Guest Composition & Meal Preferences**: What are the prevailing travel party demographics (solo, couples, families) and food/beverage boarding package choices?
9. **Origin Markets & Special Services**: How do international guest origins, advance waiting list times, and special requests correlate with booking conversion and retention?
10. **Actionable Operations Recommendations**: What data-backed operational adjustments (e.g., non-refundable deposit thresholds, overbooking buffers, direct booking incentives) are justified by historical patterns?

---

## 4. Platform Objectives & Scope

- **Deterministic Analytics Engine**: Provide 100% verified SQL metrics powering FastAPI REST endpoints and interactive Plotly charts in Streamlit.
- **AI Analytics Assistant**: Enable business stakeholders to query complex multi-table relationships using natural language, backed by SQLGlot security AST validation and LangSmith tracing.
- **Enterprise Governance**: Maintain clear distinction between estimated booking value and realized revenue, eliminating future-leakage and speculative metrics.
