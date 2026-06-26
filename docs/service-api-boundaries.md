# Service API boundaries

The HTTP action ownership and activation rules are recorded in
`docs/http-action-identity-checkpoint.md`. RExecOp owns generic shape validation and digest
binding; Tecrax owns domain action declarations, facts contracts, non-claims and validation.

## Zabbix: T4 blocked beyond reachability

The active `check_zabbix_container_health` id is compatibility-bound but proves only the
unauthenticated `apiinfo.version` path. Bounded problem and host-availability summaries are
not active because no technically constrained read-only token/role and response projection
have been accepted. A broad token is not an acceptable substitute.

Activation requires a least-privilege role, external secret reference, immutable HTTP action
shape, bounded pagination/projection, secret canaries, negative permission tests and a
sanitized operator sign-off. Host names, raw problems, history, macros and configuration
must not enter evidence by default.

## AdGuard: current boundary

The current operation proves only DNS resolution and login-page reachability. Management API,
configuration, clients and filter lists remain deliberately not observed. No read-only
management slice is active because a technical read-only boundary has not been verified.

## Portainer: current boundary

The current operation uses only unauthenticated `/api/status` through verified TLS and drops
instance identity. Environments, stacks, containers, users, tokens and configuration remain
not observed. Portainer is not treated as a safe substitute for Docker socket access.

## Docker: current boundary

Tecrax observes only `docker.service` and `docker.socket` systemd state. It does not use the
Docker socket, `docker exec`, inspect, logs, compose, restart or configuration mutation.
