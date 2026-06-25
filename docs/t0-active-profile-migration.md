# Active profile migration

The active profile no longer contains `check_backup_status`, `restart_zabbix_agent`,
Proxmox/PBS connector contracts or registered Tecrax fixture backends. RExecOp owns the
domain-neutral `runtime-fixture` used for lifecycle regression tests.

Proxmox/PBS historical behavior remains available in Git history, not as a hidden operator
feature. Future support must enter through `future-product-activation.md` rather than a
compatibility shim. `check_zabbix_container_health` remains temporarily compatibility-bound;
see `zabbix-intent-rename-impact.md`.
