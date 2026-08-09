# Spartan Core Contract

This document defines what belongs in `spartan-framework` (Core) versus the
cloud-specific ecosystem packages — [Bogart](https://github.com/nerdmonkey/spartan-bogart)
(AWS), [Lazaro](https://github.com/nerdmonkey/spartan-lazaro) (GCP), and
[Orbit](https://github.com/nerdmonkey/spartan-orbit) (Azure) — and the rule
that keeps that boundary from eroding. It formalizes the scope agreed in
[issue #11](https://github.com/nerdmonkey/spartan-framework/issues/11).

## The rule

```
application code
      |
      v
Spartan interface / abstraction   <- Core (spartan-framework)
      |
      v
provider implementation           <- Bogart / Lazaro / Orbit
```

Application code (handlers, services, tests) only ever depends on a Core
interface — never on a provider SDK directly. Provider implementations live
behind that interface and are swapped via configuration, not import paths.

## Core vs. ecosystem packages

| Layer | Lives in | Examples |
|---|---|---|
| Interfaces / contracts | `spartan-framework` (Core) | `BaseLogger`, `BaseTracer`, `BaseRepository`, `BaseService` |
| Runtime-agnostic pieces | `spartan-framework` (Core) | models, requests/responses, middleware, config, exceptions, `LocalTracer`, `StreamLogger`/`FileLogger` |
| AWS implementations | `spartan-bogart` (long-term) — currently co-located in Core | `AWSCloudWatchLogger`, `AWSTracer`, `DynamoDBRepository` |
| GCP implementations | `spartan-lazaro` (long-term) — currently co-located in Core | `GCPLogger`, `GCPTracer` |
| Azure implementations | `spartan-orbit` (not started) | `AzureLogger`, `AzureTracer` |

The AWS/GCP implementations currently ship inside `spartan-framework` itself
(there's no dependency split into separate installable packages yet). That's
acceptable short-term, but every provider-specific class must implement a
Core interface — it must never become the interface itself. Moving these
implementations into their own packages is a packaging change for a later
milestone, not a blocker for defining the contract now.

## Contract status

### Logger — conforms

`BaseLogger` (`app/services/logging/base.py`) defines `info`/`error`/`warning`/`debug`/`exception`.
`LoggerFactory` (`app/services/logging/factory.py`) selects an implementation
(`stream`, `file`, `aws`, `gcp`, `both`) via the `LOGGER_TYPE` / `LOG_CHANNEL`
environment variable. No changes were needed.

```python
Logger (BaseLogger)
├── StreamLogger / FileLogger   (Core, runtime-agnostic)
├── AWSCloudWatchLogger         (AWS-flavored)
└── GCPLogger                   (GCP-flavored)
```

### Tracer — conforms, plus a runtime-neutral entry point

`BaseTracer` (`app/services/tracing/base.py`) defines `capture_lambda_handler`,
`capture_method`, and `create_segment`. `TracerFactory` selects an
implementation (`local`, `aws`, `gcp`) via `TRACER_TYPE`.

`capture_lambda_handler` is a serverless-specific name baked into the
contract. Rather than rename it (breaking change across `aws.py`, `gcp.py`,
`local.py`, `TracerService`, and existing tests), this issue adds a
provider- and runtime-neutral alias, `capture_handler`, alongside it. Both
names wrap the same underlying tracing behavior:

```python
Tracer (BaseTracer)
├── capture_lambda_handler(handler)   # kept for serverless callers
└── capture_handler(handler)          # runtime-agnostic alias, use this going forward
```

`AWSTracer` previously did not declare `BaseTracer` as its base class despite
implementing the same methods — that's fixed as part of this issue so the
contract is actually enforced (`AWSTracer(BaseTracer)`), not just
duck-typed.

### Repository — fixed by this issue

`app/repositories/base.py` was, despite its name, a fully AWS-DynamoDB-specific
implementation (direct `boto3` calls) — not an abstraction. Nothing extended
it (the package's `__init__.py` referenced nine repository subclasses that
don't exist in this repo — dead imports, removed as part of this change).

This is now split:

- `app/repositories/contracts.py` — `BaseRepository`, a persistence-agnostic
  ABC (method signatures only: `get_by_id`, `save`, `delete_by_id`,
  `soft_delete_by_id`, `get_by_id_including_deleted`, `list_by_entity_type`,
  `batch_get_by_ids`, `exists`, `get_model_class`, `get_entity_type`).
- `app/repositories/dynamodb.py` — `DynamoDBRepository(BaseRepository)`, the
  concrete AWS implementation (unchanged behavior, moved verbatim).

```python
Repository (BaseRepository)
└── DynamoDBRepository   (AWS-flavored; a SQL or GCP-flavored repository
                           would implement the same BaseRepository contract)
```

### Service — new contract, not yet adopted by existing services

`app/services/base.py` adds `BaseService`, a persistence-agnostic contract
(`get_by_id`, `list`, `create`, `update`, `delete`). Existing services do
**not** implement it yet:

- `UserService` (`app/services/user.py`) talks directly to a SQLAlchemy
  `Session` — wiring it to `BaseService`/`BaseRepository` is reference-app
  work, tracked under issue #14 (golden path), not this issue.
- `AppService` (`app/services/app.py`) is a Core service that is 100% AWS
  DynamoDB (`boto3`) — a Core/provider boundary violation in its own right,
  tracked as a follow-up issue rather than fixed here.

## Runtime scope decision

Core is **runtime-agnostic**, not serverless-only. Nothing in the Core
layers (models, repositories, services, requests/responses, middleware,
handlers, database abstractions) requires a serverless deployment target —
a handler can sit behind a container-run HTTP server just as easily as
behind a Lambda trigger. Concretely:

- `capture_lambda_handler` remains for Lambda-style `handler(event, context)`
  callers.
- `capture_handler` is the provider/runtime-neutral entry point for
  container or microservice callers, and the one new code should prefer.

Renaming the framework's public branding (the README title/tagline, e.g.
"Spartan Serverless Framework") is a separate, deliberate decision and is
out of scope for this issue — it's a marketing/positioning choice, not an
interface one.

## Package identity

`pyproject.toml`'s `description` no longer names AWS specifically, since
Core itself is provider-agnostic — only Bogart/Lazaro/Orbit are cloud-specific.
