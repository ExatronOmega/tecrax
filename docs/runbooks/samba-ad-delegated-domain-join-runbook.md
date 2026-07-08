# Samba AD Delegated Domain Join Runbook

This runbook covers the controlled delegation model for joining Windows
workstations to a Samba AD domain without using a Domain Admin account for
routine endpoint onboarding.

It is intentionally narrow. It documents a public-safe operator procedure for a
dedicated join operator account and OU-specific ACL delegation. It is not a
generic Active Directory permission editor and it does not automate endpoint
domain join.

## Scope

Allowed:

- verify the join operator account and join operator group exist;
- verify the target workstation OU exists;
- capture a pre-change ACL backup on the DC;
- apply narrow ACL entries for computer-object creation on the workstation OU;
- keep a temporary fallback group membership until a live join test passes;
- validate the delegated ACEs without dumping full directory state into public
  artifacts;
- record a public-safe sign-off.

Not allowed:

- use Domain Admin for routine workstation joins after delegation is proven;
- expose the join operator password to chat, Git, docs, shell history or LLM
  tooling;
- grant broad domain-wide rights as a shortcut;
- remove the fallback path before a real join test confirms the delegated ACL;
- apply the delegation to all OUs unless separately reviewed and approved;
- delete computer objects as cleanup without explicit operator approval.

## Public and Private Boundary

Safe in public docs and sign-offs:

- account role such as `join operator`;
- group name and target OU name when they are already part of public-safe infra
  documentation;
- class of ACL granted, for example create/delete child computer objects and
  inherited computer-object management rights;
- backup file location on the DC, without secret contents;
- whether fallback removal is done or deferred.

Must remain outside Git and public sign-offs:

- passwords and password reset transcripts;
- raw secret-bearing host transcripts;
- private key material;
- full directory exports if they expose private users, descriptions or notes;
- unredacted operational logs.

## Preconditions

- Samba AD DC is healthy.
- A dedicated join account exists and is enabled.
- The join account is a normal domain user, not a Domain Admin.
- A dedicated join operator group exists.
- The join account is a member of the join operator group.
- The target workstation OU exists.
- The operator has an approved privileged path on the DC.
- A test endpoint is available, or the live join test is explicitly deferred.

## Target Model

The preferred pattern is:

```text
join operator user
  -> join operator group
  -> OU-specific delegated ACL on Workstations OU
  -> live endpoint join test
  -> remove temporary broad fallback after validation
```

The temporary broad fallback, if present, is a transition mechanism only. It
must not be treated as the final delegated-join model.

## Procedure

### 1. Inspect Current State

On the DC, inspect only the bounded facts needed for the change:

```bash
sudo samba-tool user show joinadmin
sudo samba-tool group listmembers GG_MBP_Join_Operators
sudo samba-tool group listmembers "Account Operators"
sudo samba-tool ou list
```

Expected facts:

- the join account exists and is enabled;
- the join account is a member of the dedicated join operator group;
- the target workstation OU exists;
- any broad fallback membership is identified before changing ACLs.

Do not copy full user or directory dumps into public docs.

### 2. Capture ACL Backup

Before changing the target OU ACL, capture the current descriptor on the DC:

```bash
sudo mkdir -p /root/tecrax-ad-delegation
sudo samba-tool dsacl get \
  --URL=/var/lib/samba/private/sam.ldb \
  --objectdn="OU=Workstations,OU=Computers,OU=MBP,DC=mbp,DC=infra,DC=lan" \
  > /root/tecrax-ad-delegation/workstations-acl-before-YYYYMMDDTHHMMSSZ.sddl.txt
```

The backup stays on the DC. Public sign-offs may reference the backup path, but
must not inline full descriptors unless they have been reviewed and redacted.

### 3. Apply Delegated ACL

Apply only the reviewed ACE set for the dedicated join operator group SID.

The intended ACL shape is:

- create/delete child computer objects on the workstation OU;
- inherited computer-object rights needed for the joined workstation object;
- no Domain Admin membership;
- no domain-root delegation.

Use `samba-tool dsacl set` or an approved deterministic helper only after the
exact target OU, trust group SID and ACE shape have been reviewed.

### 4. Validate Delegation

Validate with bounded output:

```bash
sudo samba-tool dsacl get \
  --URL=/var/lib/samba/private/sam.ldb \
  --objectdn="OU=Workstations,OU=Computers,OU=MBP,DC=mbp,DC=infra,DC=lan" \
  | grep "<join-operator-group-sid>"
```

Expected result:

- the delegated ACEs are present;
- the previous ACL backup exists;
- no unexpected long-running `dsacl` process remains;
- the broad fallback has not been removed yet unless the live join test passed.

### 5. Live Join Test

Join one pilot workstation using the join operator account, not Domain Admin.

Expected result:

- workstation joins the domain;
- the computer object lands in the intended workstation OU or is moved there by
  an approved process;
- GPO refresh succeeds;
- login using an ordinary domain user succeeds;
- no unrelated domain objects are changed.

If no endpoint is available, record the join test as deferred. Do not claim the
delegation is final.

### 6. Remove Temporary Fallback

Only after a successful live join test, remove the dedicated join operator group
from broad fallback groups such as `Account Operators`.

Then validate:

```bash
sudo samba-tool group listmembers "Account Operators"
sudo samba-tool group listmembers GG_MBP_Join_Operators
```

Run another join test after fallback removal if possible.

## Stop Conditions

Stop if:

- the join account is privileged beyond the intended operator role;
- the target OU is ambiguous;
- the command would require exposing a password to tooling;
- the ACL backup fails;
- the proposed ACE grants domain-wide rights;
- the live join test fails and the fallback removal has not yet been reviewed;
- the operation would affect production endpoints without a pilot window.

## Rollback

Preferred rollback is ACL restoration from the captured pre-change descriptor,
performed by an approved privileged operator on the DC.

If endpoint join was attempted:

- do not delete the computer object automatically;
- inspect the object and OU placement;
- decide whether to leave, move, disable or remove it under explicit operator
  approval;
- preserve evidence needed to debug the failed join.

## Evidence and Sign-Off

Public-safe sign-off may include:

- run class: `samba-ad-delegated-domain-join`;
- target OU;
- join operator group;
- ACL backup path;
- delegated ACE class;
- fallback status;
- live join test status;
- non-claims.

Do not include:

- passwords;
- raw private transcripts;
- full account dumps;
- unredacted directory exports;
- private key material.

## Tecrax Artifact Decision

Current activation level: `L1 - public-safe runbook`.

A deterministic helper may be added later, but only after the first live join
and fallback-removal cycle is validated. Required properties for a future helper:

- fixed target OU and group inputs from operator-owned context;
- dry-run showing bounded current state and proposed ACE classes;
- automatic pre-change ACL backup;
- no password handling;
- no generic SDDL passthrough for normal use;
- explicit guard that broad fallback removal is a separate step;
- concise public-safe evidence output.

Do not promote this directly into a Tecrax mutation until the custody model,
GovEngine policy admission, RExecOp execution envelope and SCLite evidence
shape are defined.
