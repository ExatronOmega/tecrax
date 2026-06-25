# Future product activation gates

No intent is added merely because a product is planned. Proxmox, PBS, Wazuh, Samba, Grafana,
Frigate-specific checks, Hillstone and printers remain inactive until the product or endpoint
exists and passes all gates below:

1. read-only discovery and explicit threat model;
2. least-privilege technical access boundary;
3. sanitized bounded fixtures and negative vectors;
4. immutable connector action contract;
5. standalone read-only intent with versioned facts and non-claims;
6. GovEngine admission, RExecOp receipt and SCLite bundle;
7. sanitized operator-verified sign-off.

Backup work must distinguish readiness, job execution, restore evidence and coverage. A job
status without restore evidence must not be called a healthy backup. Frigate is activated
only for bounded signals not already covered by generic Ubuntu host observations.
