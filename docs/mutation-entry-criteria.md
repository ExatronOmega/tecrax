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

## First candidate: Proxmox chrony/NTP server

The first approved candidate for crossing the read-only boundary is a bounded
chrony/NTP server activation on a freshly installed Proxmox node.

Before implementation, `docs/proxmox-access-handoff.md` must be complete. In
particular, the target host identity must be verified as fresh, access must use
the `rexecop` account, and all real target bindings, keys and known-hosts files
must remain outside Git.

The candidate operation must not widen into generic Proxmox administration. It
may only cover the exact NTP server state transition declared by the profile,
with read-only pre-state, GovEngine admission, bounded backend execution,
post-state validation, rollback or compensation, target locking and SCLite
evidence.
