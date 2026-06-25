# Zabbix intent rename impact

`check_zabbix_container_health` currently proves only unauthenticated API reachability and
version. It does not prove container health. The id remains unchanged in this release to
avoid an uncoordinated break across its intent, workflow, validation, policy pack, reaction
pack, RExecOp integration tests and operator automation.

Candidate future id: `check_zabbix_api_reachability`. The rename must be one coordinated
alpha release boundary. Two active aliases are forbidden because they would represent one
operation twice in the operator catalog. Until that boundary, all titles, summaries and
non-claims must describe API reachability only.
