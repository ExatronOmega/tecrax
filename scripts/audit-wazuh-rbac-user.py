#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


def _load_rule(raw_rule: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_rule)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _rule_matches_user(raw_rule: str, username: str) -> bool:
    parsed = _load_rule(raw_rule)
    find = parsed.get("FIND")
    if not isinstance(find, dict):
        return False

    user_name = find.get("user_name")
    legacy_username = find.get("username")
    return user_name == username or legacy_username == username


def inspect_user(db_path: Path, username: str) -> dict[str, Any]:
    con = sqlite3.connect(db_path)
    cur = con.cursor()

    user_row = cur.execute(
        "select id, username, allow_run_as from users where username = ?",
        (username,),
    ).fetchone()

    direct_roles: list[dict[str, Any]] = []
    if user_row:
        direct_roles = [
            {"id": row[0], "name": row[1]}
            for row in cur.execute(
                """
                select r.id, r.name
                from user_roles ur
                join roles r on r.id = ur.role_id
                where ur.user_id = ?
                order by r.id
                """,
                (user_row[0],),
            )
        ]

    mapping_rules: list[dict[str, Any]] = []
    for row in cur.execute(
        """
        select ru.id, ru.name, ru.rule, r.id, r.name
        from rules ru
        join roles_rules rr on rr.rule_id = ru.id
        join roles r on r.id = rr.role_id
        order by ru.id, r.id
        """
    ):
        rule_id, rule_name, raw_rule, role_id, role_name = row
        if _rule_matches_user(str(raw_rule), username):
            mapping_rules.append(
                {
                    "id": rule_id,
                    "name": rule_name,
                    "role_id": role_id,
                    "role": role_name,
                    "rule": _load_rule(str(raw_rule)),
                }
            )

    con.close()

    administrator_direct_role = any(role["name"] == "administrator" for role in direct_roles)
    administrator_mapping_rule = any(rule["role"] == "administrator" for rule in mapping_rules)
    ready_for_dashboard_admin = bool(user_row and administrator_mapping_rule)

    return {
        "username": username,
        "user_exists": bool(user_row),
        "allow_run_as": bool(user_row[2]) if user_row else None,
        "direct_roles": direct_roles,
        "administrator_direct_role": administrator_direct_role,
        "matching_role_mapping_rules": mapping_rules,
        "administrator_mapping_rule": administrator_mapping_rule,
        "ready_for_dashboard_admin": ready_for_dashboard_admin,
        "notes": [
            "Wazuh Dashboard run_as administrator checks require an administrator role-mapping rule.",
            "A direct Wazuh API RBAC user role alone may not satisfy Dashboard administrator screens.",
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Audit a Wazuh API RBAC user without printing password hashes or secrets."
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=Path("/var/ossec/api/configuration/security/rbac.db"),
        help="Path to Wazuh API RBAC SQLite database.",
    )
    parser.add_argument("--username", required=True, help="Wazuh/OpenSearch dashboard username.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    result = inspect_user(args.db, args.username)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["ready_for_dashboard_admin"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
