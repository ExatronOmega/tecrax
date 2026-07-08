# Wazuh Dashboard RBAC operator access runbook

This runbook covers a bounded repair path for an operator who can log in to
Wazuh Dashboard but receives an administrator-permission error inside Wazuh
application sections.

Typical symptom:

```text
You have no permissions
This section requires administrator privileges: User has no administrator role in the selected API connection.
```

## Scope

This procedure covers:

- verifying the OpenSearch internal dashboard user exists;
- verifying Wazuh API RBAC user state without printing password hashes;
- verifying Wazuh Dashboard role-mapping rules;
- adding a missing administrator role-mapping rule only after a DB backup;
- restarting Wazuh Dashboard;
- requiring operator confirmation before documenting the fix as closed.

It does not cover SSO, LDAP, broad Wazuh security redesign, password reset,
index deletion, alert deletion, or hardening of final administrative roles.

## Public and Private Boundary

Safe in public docs and sign-offs:

- usernames when already approved as operator aliases;
- role names such as `administrator`;
- rule names and high-level RBAC state;
- service restart status;
- backup path shape without secret payload.

Keep outside Git and public sign-offs:

- password hashes from `internal_users.yml`;
- dashboard/API passwords;
- generated tokens;
- raw API payloads containing private topology;
- shell history containing secrets.

## Access Model

Wazuh Dashboard administrator access has multiple layers:

1. OpenSearch Security internal user, stored in
   `opensearch-security/internal_users.yml`.
2. Wazuh API RBAC user, stored in the Wazuh RBAC database.
3. Wazuh Dashboard role mapping for the selected API connection.

When Dashboard host config uses `run_as: true`, a direct Wazuh API RBAC role can
be insufficient for Dashboard administrator pages. The Dashboard administrator
check may require a role-mapping rule that maps the logged-in OpenSearch
dashboard username to the Wazuh `administrator` role.

## Read-Only Audit

Run a read-only audit on the Wazuh host or against a private copy of the RBAC DB:

```sh
python scripts/audit-wazuh-rbac-user.py \
  --db /var/ossec/api/configuration/security/rbac.db \
  --username OPERATOR_USERNAME
```

The helper intentionally does not print password hashes. A healthy Dashboard
administrator operator should have:

- `user_exists: true`;
- `allow_run_as: true`;
- `administrator_mapping_rule: true`;
- `ready_for_dashboard_admin: true`.

If `administrator_direct_role` is true but `administrator_mapping_rule` is
false, the user can exist in Wazuh API RBAC while still failing Dashboard
administrator checks.

## Repair Procedure

Prefer supported Wazuh API or UI operations when they are available and already
authorized. If the operator is locked out of administrator pages, a controlled
local RBAC DB repair may be used as a break-glass action.

### 1. Back up RBAC DB

```sh
cp -a /var/ossec/api/configuration/security/rbac.db \
  /var/ossec/api/configuration/security/rbac.db.bak-YYYYMMDD-dashboard-rbac
```

Do not continue without a backup.

### 2. Confirm Existing State

Check:

- the operator exists in the Wazuh API RBAC `users` table;
- the operator has `allow_run_as` enabled;
- the `administrator` role exists;
- existing administrator role-mapping rules do not already match the operator
  username.

### 3. Add Missing Administrator Role-Mapping Rule

Add one explicit rule mapping the operator dashboard username to the
`administrator` role. The observed Dashboard-compatible rule shape is:

```json
{"FIND":{"user_name":"OPERATOR_USERNAME"}}
```

Link that rule to the `administrator` role in `roles_rules`.

Keep the rule name explicit, for example:

```text
wui_OPERATOR_USERNAME_admin
```

### 4. Restart Dashboard

```sh
systemctl restart wazuh-dashboard
systemctl is-active wazuh-dashboard
```

The Wazuh manager and indexer should remain active.

### 5. Browser Validation

The operator must sign out of Wazuh Dashboard and sign in again. If the browser
keeps stale permissions, clear cookies for the Wazuh Dashboard URL or use a
private browser window.

Validate:

- Wazuh Dashboard login works;
- the previously blocked Wazuh section opens;
- Security or Options pages no longer show the administrator-permission error;
- no password or hash has been written to Git, public docs or chat.

## Stop Conditions

Stop before mutation if any of these are true:

- the selected username is not approved as an operator account;
- the RBAC DB cannot be backed up;
- Wazuh services are already unhealthy;
- the intended role would grant broader access than the operator approved;
- the repair would require printing or storing password hashes in public
  artifacts.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `wazuh-dashboard-rbac-operator-access`;
- affected operator alias;
- backup path;
- before/after summary from the read-only helper;
- service restart status;
- browser validation result;
- explicit non-claims.

Non-claims:

- no final Wazuh hardening policy;
- no SSO or LDAP integration;
- no Wazuh alert tuning change;
- no index or alert deletion;
- no password disclosure.
