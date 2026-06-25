# Target taxonomy

Tecrax defines a bounded vocabulary in `src/tecrax/profile/taxonomy.yaml`; it does not own a
CMDB or a private target catalog. RExecOp remains responsible for loading the operator-owned
catalog and evaluating mechanical applicability.

The initial kinds are `host` and `network_device`. Roles describe domain purpose, while
namespaced capabilities such as `tecrax.host.basic_inventory.v1` state which Tecrax contract
a target is prepared to support. Transport capabilities such as `ssh_readonly` and
`http_api` remain separate and do not imply product or role support.

Real hostnames, addresses, usernames, key paths, topology and credentials never belong in
the taxonomy or public catalog example.
