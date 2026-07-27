# Economics, units and risk contract

Authoritative finance uses decimal strings with ISO currency, scale, rounding rule, tax basis, time basis and effective window. `ROUND_HALF_EVEN` is the default unless a versioned, sourced settlement rule overrides it.

Economic layers are E0 Gross Sales, E1 Net Revenue, E2 Product Contribution, E3 Fulfilled Contribution, E4 Channel Contribution, E5 Acquired Contribution, E6 Served Contribution, E7 Risk-adjusted Contribution and E8 Operating Cash Contribution. Adjusted and unadjusted values remain visible. Accounting profit, contribution profit and cash flow never substitute for one another. Average and marginal economics remain separate.

Quantities carry unit, currency when monetary, tax basis, as-of time, effective window, source and calculation ID. Comparisons fail closed on incompatible unit, currency, tax or time bases unless an explicit versioned conversion exists.

Legal, safety, IP, privacy/authorization, unapproved negative contribution, cash rupture, identity/rights reconciliation, irreversible-action authorization and unreproducible calculation failures are non-compensable redlines. Comparable risks may use probability and impact, but unknown probability is not zero and tail scenarios remain explicit.
