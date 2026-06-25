# Mutation entry criteria

Mutation is not implemented in the current Tecrax line. A future single action requires a
separate architecture decision and all of the following:

- stable versioned read-only pre-state and diagnosis;
- one exact action contract and explicit side effect;
- GovEngine approval plus enforceable obligations/constraints and operator confirmation;
- post-state validation and feasible rollback or compensation;
- target lock, idempotency, bounded retry and lockout prevention;
- SCLite evidence chain and no-backend-before-admission tests;
- no unattended apply and no direct LLM execution.

Failure of any gate keeps the action outside the active profile. This document is criteria,
not a deployer design or implementation backlog.
