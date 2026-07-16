# BookStack controlled documentation publication runbook

This public-safe runbook defines the bounded publication semantics for reviewed
technical documentation in BookStack. It covers reusable templates, detailed
service cards and operator-facing runbooks without exposing private topology,
credentials, raw evidence or user data.

It does not define the organization's formal ISMS, approve risk, establish
statutory ownership or authorize publication of restricted content.

## Ownership boundary

- Tecrax owns the public-safe documentation structure, quality rules, safety
  gates and source runbook links.
- Private operator context owns the real BookStack target, content bundle,
  current infrastructure state and publication evidence.
- Runtime custody owns the BookStack publisher credential.
- BookStack owns the published page, tags and revision history.
- Formal policies, risk acceptance and statutory ownership remain
  organizational governance artifacts outside this mechanism.

The publication helper is not a generic content-management framework and must
not write directly to the BookStack database.

## Allowed content

The controlled publication path may create or update:

- Polish technical service cards;
- Polish operator-facing redactions of public Tecrax runbooks;
- documentation templates;
- visible `TODO` markers for transitional or unvalidated state;
- links to public-safe source runbooks and private evidence classes.

Every detailed service card must identify:

- purpose and audience;
- scope and explicit exclusions;
- classification and status;
- operational owner;
- source of truth;
- current, target and deferred state;
- impact and dependencies;
- monitoring and recovery;
- known limitations;
- `TODO` items with closure gates;
- last validation and review trigger;
- explicit non-claims.

## Prohibited content

Never publish:

- passwords, tokens, private keys, recovery codes or database credentials;
- private credential paths or reconstruction material;
- raw logs, alert payloads, database dumps or full configurations;
- user files, mail archives, browser profiles or personal data;
- exact private topology unless separately classified and permission-tested;
- formal risk acceptance or statutory ownership inferred by the publisher;
- content marked `restricted` before its BookStack permission boundary has been
  explicitly validated.

## Preflight

Before a large content wave:

1. Confirm the exact BookStack host and service identity.
2. Confirm the web, database and PHP services are healthy.
3. Require a fresh application-aware backup and isolated restore/read proof.
4. Confirm the publisher identity is least-privileged and has no delete rights.
5. Resolve every target book and chapter by exact name; stop on zero or
   multiple matches.
6. Validate the content bundle and scan it for secret and private-address
   patterns.
7. Verify that `storage/`, `bootstrap/cache` and `public/uploads` contain no
   descendants that the PHP/web user cannot update. BookStack application CLI
   or diagnostics that can warm cache or create uploads must run as the
   PHP/web user rather than leaving root-owned application artifacts.
8. Calculate the exact create/update plan.
9. Define revision-history rollback and prohibit direct SQL writes.

Do not treat an earlier backup as fresh when it predates the latest material
documentation changes.

## Publication

Use the supported BookStack API for books, chapters, pages and tags. Use the
authenticated UI only for BookStack features not exposed by the supported API,
such as template flags when required by the installed version.

The helper must:

- require an explicit apply flag;
- load credentials only from runtime custody;
- stop on ambiguous book, chapter or page identity;
- create only the reviewed allowlist;
- compare normalized page content before updating;
- preserve page revision history;
- avoid delete permissions;
- avoid default-template changes unless the manifest requests them;
- emit only bounded non-secret results.

## Validation

After publication require:

- exact chapter and page counts for the wave;
- API readback equality for every published page;
- expected classification and metadata tags;
- required `Wpływ i zależności` and `TODO` sections;
- no secret or private-address pattern;
- successful revision-history UI access;
- publisher API denial for user and role administration;
- healthy BookStack services and web endpoint;
- writable-path ownership consistent with the PHP/web process;
- an idempotent second run with zero creates and zero updates.

If any page fails readback, do not broaden the next run. Diagnose the exact page
and leave unrelated content unchanged.

## Rollback

Use BookStack revision history to restore prior page content. Do not grant page
or chapter delete rights merely to automate rollback.

If publisher custody is uncertain, revoke the token and stop publication. If a
new helper version regresses, restore the prior runtime helper and retain the
published revision evidence.

## Persistence

After a successful wave:

- retain a non-secret content manifest and validation evidence in private
  operator state;
- synchronize the tested environment-bound helper to the runtime operator host;
- update the private roadmap only after live validation;
- update public Tecrax documentation only with generic, public-safe semantics;
- record repository delivery as pending until the operator explicitly requests
  commit and push.

## Stop conditions

Stop when:

- target identity is ambiguous;
- the fresh backup or restore/read gate is missing;
- a target book or chapter has zero or multiple exact matches;
- the content contains secrets, raw evidence or user data;
- restricted permissions have not been tested;
- the publisher requires delete or administrative rights;
- direct SQL writes would be required;
- an application cache or upload path is owned in a way that prevents the
  PHP/web user from updating it;
- post-publication readback or idempotence fails.

## Non-claims

This mechanism does not prove:

- formal NIS2/KSC2 compliance;
- an approved ISMS or risk analysis;
- complete documentation of the environment;
- accuracy of a source system that was not freshly validated;
- authority to publish restricted or secret material;
- autonomous AI publication or mutation authority.
