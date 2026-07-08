from __future__ import annotations

import importlib.util
import sqlite3
from pathlib import Path
from types import ModuleType


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit-wazuh-rbac-user.py"


def _load_script() -> ModuleType:
    spec = importlib.util.spec_from_file_location("audit_wazuh_rbac_user", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rbac_db(path: Path) -> None:
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.executescript(
        """
        create table users (
          id integer primary key,
          username varchar(32) not null,
          password varchar(256) not null,
          allow_run_as boolean not null
        );
        create table roles (
          id integer primary key,
          name varchar(20) not null
        );
        create table user_roles (
          id integer primary key,
          user_id integer,
          role_id integer
        );
        create table rules (
          id integer primary key,
          name varchar(20) not null,
          rule text not null
        );
        create table roles_rules (
          id integer primary key,
          role_id integer,
          rule_id integer
        );
        insert into roles (id, name) values (1, 'administrator'), (2, 'readonly');
        insert into users (id, username, password, allow_run_as)
          values (100, 'operator', 'redacted-hash', 1);
        insert into user_roles (id, user_id, role_id) values (1, 100, 1);
        insert into rules (id, name, rule)
          values (1, 'wui_admin', '{"FIND":{"user_name":"admin"}}');
        insert into roles_rules (id, role_id, rule_id) values (1, 1, 1);
        """
    )
    con.commit()
    con.close()


def test_direct_administrator_role_is_not_enough_for_dashboard_admin(tmp_path: Path) -> None:
    db_path = tmp_path / "rbac.db"
    _rbac_db(db_path)
    module = _load_script()

    result = module.inspect_user(db_path, "operator")

    assert result["user_exists"] is True
    assert result["administrator_direct_role"] is True
    assert result["administrator_mapping_rule"] is False
    assert result["ready_for_dashboard_admin"] is False


def test_administrator_mapping_rule_marks_dashboard_admin_ready(tmp_path: Path) -> None:
    db_path = tmp_path / "rbac.db"
    _rbac_db(db_path)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        "insert into rules (id, name, rule) values (?, ?, ?)",
        (2, "wui_operator", '{"FIND":{"user_name":"operator"}}'),
    )
    cur.execute("insert into roles_rules (id, role_id, rule_id) values (?, ?, ?)", (2, 1, 2))
    con.commit()
    con.close()
    module = _load_script()

    result = module.inspect_user(db_path, "operator")

    assert result["administrator_mapping_rule"] is True
    assert result["ready_for_dashboard_admin"] is True
    assert result["matching_role_mapping_rules"][0]["name"] == "wui_operator"
