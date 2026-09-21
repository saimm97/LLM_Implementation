# LLM Prompt Evaluation Registry

This project explores how to design the persistence layer for a versioned LLM prompt registry and evaluation system. It models the complete traceability path from a stable prompt task, through a specific prompt version and model evaluation run, to the result produced for each labeled golden example.

The strongest completed part of the project is its PostgreSQL schema, SQLAlchemy domain model, and Alembic migration history. The schema can store prompt versions, evaluation evidence, aggregate metrics, token usage, latency, cost, raw model responses, and failure states. The FastAPI application and automated evaluation runner are not yet complete; the current API exposes only a health-style root endpoint.

## What this project demonstrates

- Designing a versioned prompt registry and evaluation data model.
- Modeling offline prompt evaluation against a labeled golden dataset.
- Linking prompt families, prompt versions, evaluation runs, golden examples, and per-example results.
- Capturing quality, performance, cost, usage, and reliability metrics.
- Preserving raw model output and error information for debugging.
- Expressing one-to-many relationships with primary and foreign keys.
- Enforcing domain rules with nullability, uniqueness, and enum-backed check constraints.
- Evolving an existing PostgreSQL schema through ordered Alembic migrations.
- Understanding the difference between ORM relationships and database constraints.
- Understanding the difference between application-side defaults and database defaults.

## System model

The central relationship chain is:

```text
PromptFamily
    1
    └── 0..* PromptVersion
                  1
                  └── 0..* EvalRunner
                                1
                                └── 0..* EvalResult
                                               *
                                               └── 1 GoldenExample
```

In table terms:

```text
prompt_families
    ↓
prompt_versions
    ↓
eval_runs
    ↓
eval_results
    ↑
golden_examples
```

Each layer answers a separate question:

| Entity | Question it answers |
| --- | --- |
| `PromptFamily` | What stable task are we trying to solve? |
| `PromptVersion` | Which exact prompt implementation was tested? |
| `EvalRunner` / `eval_runs` | Which model evaluation execution produced the measurements? |
| `GoldenExample` | Which labeled input and expected category were used? |
| `EvalResult` | What happened for one example during one evaluation run? |

`EvalResult` is the evidence record that connects an evaluation run to a golden example. A run can test many golden examples, and the same golden example can be reused across many runs. This makes comparisons across prompt versions and models possible.

## Relationship implementation

The foreign key is stored on the many side of every one-to-many relationship:

| Parent | Child | Cardinality | Foreign key |
| --- | --- | --- | --- |
| `prompt_families` | `prompt_versions` | One to zero-or-many | `prompt_versions.prompt_family_id` |
| `prompt_versions` | `eval_runs` | One to zero-or-many | `eval_runs.prompt_version_id` |
| `eval_runs` | `eval_results` | One to zero-or-many | `eval_results.eval_run_id` |
| `golden_examples` | `eval_results` | One to zero-or-many | `eval_results.golden_example_id` |

Every child foreign key is required. The current schema does not declare `ON DELETE CASCADE`, so parent deletion behavior must be decided explicitly by the application or by a future migration.

The SQLAlchemy `relationship(..., back_populates=...)` declarations provide bidirectional Python object navigation. The foreign keys provide database integrity. Changing only `back_populates` does not require database DDL, which is why revision `9ae3e45f1d0b` contains no upgrade or downgrade operations.

## Database schema

The schema below reflects the current model and migration head `fdd324cb4b25`.

### `prompt_families`

Stores one stable identity for each prompt-driven task.

| Column | Type | Null | Rules | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | No | Primary key | Family identifier |
| `name` | Enum-backed `VARCHAR` | No | Unique and checked | Allowed prompt-family name |
| `created_at` | `TIMESTAMPTZ` | No | Model declares `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | Model declares `now()` and `onupdate` | Last update timestamp |

Allowed prompt-family enum members:

```text
SUPPORT_TICKET_TRIAGE
SUPPORT_REPLY_GENERATION
TICKET_SUMMARIZATION
TICKET_PRIORITY_CLASSIFICATION
TICKET_ROUTING
SENTIMENT_ANALYSIS
CUSTOMER_INTENT_CLASSIFICATION
TICKET_ENTITY_EXTRACTION
DUPLICATE_TICKET_DETECTION
ESCALATION_DETECTION
URGENCY_DETECTION
LANGUAGE_DETECTION
RESPONSE_QUALITY_EVALUATION
RESPONSE_TONE_EVALUATION
KNOWLEDGE_BASE_SEARCH_QUERY
```

### `prompt_versions`

Stores immutable prompt candidates within a prompt family.

| Column | Type | Null | Rules | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | No | Primary key | Version identifier |
| `text` | `TEXT` | No | — | Prompt content |
| `version` | `VARCHAR` | No | Unique within family | Semantic or application version such as `1.0.0` |
| `is_active` | `BOOLEAN` | Yes | ORM default `false` | Whether the version is active |
| `created_at` | `TIMESTAMPTZ` | No | Model declares `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | Model declares `now()` and `onupdate` | Last update timestamp |
| `prompt_family_id` | `INTEGER` | No | Foreign key | Owning prompt family |

The composite unique constraint `uq_prompt_versions_family_version` prevents the same version label from appearing twice inside one family while allowing different families to use the same version label.

### `eval_runs`

Stores one evaluation execution for a specific prompt version and model.

| Column | Type | Null | Rules | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | No | Primary key | Run identifier |
| `p95_latency_ms` | `FLOAT` | No | ORM default `0.0` | 95th-percentile latency in milliseconds |
| `accuracy` | `FLOAT` | No | ORM default `0.0` | Aggregate proportion of correct results |
| `average_cost` | `FLOAT` | No | ORM default `0.0` | Average cost across evaluated examples |
| `model_used` | `VARCHAR` | No | — | Model used for the run |
| `prompt_version_id` | `INTEGER` | No | Foreign key | Prompt version evaluated by the run |
| `created_at` | `TIMESTAMPTZ` | No | Model declares `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | Model declares `now()` and `onupdate` | Last update timestamp |

### `golden_examples`

Stores labeled examples used as evaluation ground truth.

| Column | Type | Null | Rules | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | No | Primary key | Example identifier |
| `input` | `VARCHAR` | No | — | Input sent to the evaluated prompt |
| `expected_output` | Enum-backed `VARCHAR` | No | Checked | Expected classification |
| `is_active` | `BOOLEAN` | No | — | Whether the example is included in active evaluation data |
| `created_at` | `TIMESTAMPTZ` | No | Model declares `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | Model declares `now()` and `onupdate` | Last update timestamp |

The available output categories are:

| Enum member | Domain label |
| --- | --- |
| `SPT` | Support ticket |
| `BUG` | Bug |
| `FEAT` | Feature request |
| `BILL` | Billing |

### `eval_results`

Stores the result of testing one golden example during one evaluation run.

| Column | Type | Null | Rules | Meaning |
| --- | --- | --- | --- | --- |
| `id` | `INTEGER` | No | Primary key | Result identifier |
| `input` | `VARCHAR` | No | — | Evaluated input snapshot |
| `predicted_category` | Enum-backed `VARCHAR` | Yes | Checked | Normalized model prediction |
| `raw_output` | `TEXT` | Yes | — | Original provider response for debugging |
| `input_tokens` | `INTEGER` | No | ORM default `0` | Prompt/input token count |
| `output_tokens` | `INTEGER` | No | ORM default `0` | Completion/output token count |
| `total_tokens` | `INTEGER` | No | ORM default `0` | Total token count |
| `passed` | `BOOLEAN` | No | — | Whether prediction matched the expected result |
| `latency_ms` | `INTEGER` | Yes | ORM default `0` | Request latency in milliseconds |
| `cost` | `FLOAT` | No | ORM default `0.0` | Estimated request cost |
| `error_message` | `TEXT` | Yes | — | Failure detail when evaluation does not complete normally |
| `status` | Enum-backed `VARCHAR` | No | Checked | Evaluation outcome status |
| `created_at` | `TIMESTAMPTZ` | No | Model declares `now()` | Creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | No | Model declares `now()` and `onupdate` | Last update timestamp |
| `golden_example_id` | `INTEGER` | No | Foreign key | Golden example used as ground truth |
| `eval_run_id` | `INTEGER` | No | Foreign key | Evaluation run that produced the result |

Result status values:

```text
COMPLETED
INVALID_OUTPUT
MODEL_ERROR
TIMEOUT
```

## Evaluation dimensions

The schema supports several complementary dimensions of evaluation:

| Dimension | Stored evidence |
| --- | --- |
| Quality | Run accuracy, per-result `passed`, expected category, predicted category |
| Performance | Per-result latency and run-level p95 latency |
| Cost | Per-result cost and run-level average cost |
| Usage | Input, output, and total token counts |
| Reliability | Completion, invalid output, model error, timeout, and error message |
| Debuggability | Raw output, normalized output, model identity, and timestamps |
| Traceability | Family → version → run → result, plus the linked golden example |

Accuracy alone is not enough to compare prompts. A candidate could be slightly more accurate but substantially slower or more expensive. Recording all these dimensions enables an explicit tradeoff among quality, latency, cost, and reliability.

## Intended evaluation lifecycle

The target workflow is:

1. Select a `PromptFamily` representing a stable task.
2. Select or create a specific `PromptVersion`.
3. Create an `EvalRunner` row containing the prompt version and model identity.
4. Load the active `GoldenExample` dataset.
5. Execute the prompt and model once for each example.
6. Normalize the response into an allowed output category.
7. Store one `EvalResult` with raw output, normalized prediction, tokens, latency, cost, status, and any error.
8. Compare the prediction with the expected output and set `passed`.
9. Aggregate result rows into accuracy, p95 latency, and average cost on the run.
10. Compare runs across prompt versions or models.

The schema supports this lifecycle, but the automated runner that performs all ten steps is future work.

## Alembic migration history

The migration chain records how the schema evolved instead of replacing its history with one final definition:

```text
47335c58910c
    ↓
a09c6e7839a9
    ↓
8780ad61cb55
    ↓
c84a39cb88c3
    ↓
69cf56477a15
    ↓
826cd905a355
    ↓
e711cb279e0a
    ↓
16d1d49ff4ce
    ↓
dbff4232fa46
    ↓
6697e66ccd26
    ↓
9ae3e45f1d0b
    ↓
fdd324cb4b25
```

| Revision | Main purpose |
| --- | --- |
| `47335c58910c` | Created a temporary `dummy` table for migration practice. |
| `a09c6e7839a9` | Created the first prompt and evaluation tables. |
| `8780ad61cb55` | Began converting golden-example output into an enum. |
| `c84a39cb88c3` | Corrected cost and aggregate metric types and created output categories. |
| `69cf56477a15` | Changed prompt version from integer to string to support semantic versions. |
| `826cd905a355` | Reversed the misplaced family/version foreign key so the FK lives on `prompt_versions`. |
| `e711cb279e0a` | Connected evaluation runs to prompt versions. |
| `16d1d49ff4ce` | Added audit timestamps and model identity. |
| `dbff4232fa46` | Added token usage and converted latency fields to numeric types. |
| `6697e66ccd26` | Added raw output and error-related storage. |
| `9ae3e45f1d0b` | Recorded ORM `back_populates` work; no database operation was required. |
| `fdd324cb4b25` | Aligned the database with the final models, constraints, enum values, field names, and foreign keys and removed the temporary table. |

Important migration lessons from the project:

- The foreign key for a one-to-many relationship belongs on the many side.
- Adding a required column to a populated table normally requires: add it as nullable, backfill existing rows, and then enforce `NOT NULL`.
- PostgreSQL type changes may require an explicit `USING` expression.
- ORM relationship configuration is different from database foreign-key enforcement.
- Enum migrations require careful creation, conversion, constraint naming, and downgrade ordering.
- Every committed migration revision must remain available because later revisions refer to their parent revision IDs.
- A migration that succeeds on a clean database still requires a separate review for production data safety.

## Application-side defaults versus database defaults

Several SQLAlchemy columns declare values such as `default=0`, `default=0.0`, or `server_default=func.now()`. The migration history did not install corresponding database defaults consistently for every existing column.

This distinction matters:

- An ORM default is applied when SQLAlchemy constructs an insert.
- A database default is applied by PostgreSQL when an insert omits the column.
- Direct SQL, another service, or a bulk loader does not receive a Python ORM default.

The migrations currently backfilled required timestamp and metric columns but did not consistently establish permanent database defaults. A future alignment migration should be generated and reviewed if database-level defaults are required.

## Project structure

```text
fastapi_eval_prompt_registry/
├── alembic/
│   ├── versions/              # Ordered schema migrations
│   ├── env.py                 # Alembic runtime configuration
│   └── script.py.mako         # Migration template
├── config/
│   └── database_connection.py # SQLAlchemy engine and session construction
├── docs/                      # Detailed Word documentation
├── factories.py              # Experimental test-data factories; currently stale
├── golden_examples.json      # Labeled support-ticket examples
├── main.py                   # Minimal FastAPI application
├── models.py                 # SQLAlchemy schema and relationships
├── seed.py                   # Experimental seed workflow; currently stale/destructive
├── alembic.ini               # Alembic configuration
└── README.md
```

Additional documentation:

- [Detailed database schema](<docs/LLM Prompt Eval Registry Detailed DB Schema.docx>)
- [Migration and design learning record](<docs/LLM Prompt Eval Registry Pipeline.docx>)
- [Complete schema diagram PDF](<docs/output/pdf/llm_prompt_eval_registry_complete_schema.pdf>)
- [Complete schema diagram PNG](<docs/output/png/llm_prompt_eval_registry_complete_schema.png>)

## Local setup

The repository does not currently include a pinned dependency file. Based on the imports in the project, the development dependencies include:

```text
fastapi
uvicorn
sqlalchemy
alembic
psycopg2-binary
python-dotenv
faker
polyfactory
```

Create and activate a virtual environment, then install those dependencies. A future improvement should capture exact versions in `requirements.txt` or `pyproject.toml`.

Create a local `.env` file inside `fastapi_eval_prompt_registry`:

```dotenv
DB_DRIVER=postgresql+psycopg2
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_database_name
```

Do not commit `.env` because it can contain credentials.

## Running migrations

Run Alembic commands from the project directory:

```bash
cd fastapi_eval_prompt_registry
alembic history
alembic heads
alembic upgrade head
alembic current
```

The expected single migration head is:

```text
fdd324cb4b25
```

Before applying the migrations to a shared or production database:

1. Back up the database.
2. Review hard-coded backfills in historical migrations.
3. Test both upgrade and downgrade behavior against representative data.
4. Confirm enum conversions against the values already stored in PostgreSQL.
5. Run Alembic from the correct working directory with the intended `.env` file.

## Running the current API

From the project directory:

```bash
uvicorn main:app --reload
```

The current endpoint is:

```http
GET /
```

Current response:

```json
{"HELLO": "WORLD!!!"}
```

Prompt management, evaluation execution, and result-query endpoints are not implemented yet.

## Seed-data warning

`golden_examples.json` contains labeled examples for four categories: support ticket, bug, feature request, and billing.

However, `factories.py` and `seed.py` still use earlier plural model names and retired column names such as `PromptVersions`, `GoldenExamples`, `EvalResults`, `output`, `latency`, `eval_runs_id`, and `golden_examples_id`. They are not aligned with the current models.

Additionally, running `seed.py` invokes:

```python
Base.metadata.drop_all(...)
Base.metadata.create_all(...)
```

That operation deletes the existing tables and their data before rebuilding them. Do not run the seed script against a database containing data that must be preserved. The seed workflow should be updated to use current model names and non-destructive, idempotent inserts.

## Current implementation status

### Implemented

- SQLAlchemy models for all five domain tables.
- Bidirectional ORM relationships.
- Foreign keys and core uniqueness constraints.
- Prompt-family, output-category, and result-status enums.
- Ordered Alembic migration history through `fdd324cb4b25`.
- Golden-example JSON dataset.
- Storage design for quality, latency, cost, usage, raw output, and failures.
- Minimal FastAPI application startup and root endpoint.

### Not yet implemented or not yet aligned

- API endpoints for families, versions, runs, examples, and results.
- LLM provider integration.
- Prompt rendering and model invocation.
- Output normalization and validation.
- Automatic pass/fail calculation.
- Aggregate accuracy, p95 latency, and average-cost calculation.
- Transactional evaluation-run lifecycle.
- Dataset identity, dataset versioning, or dataset snapshot tracking.
- Reproducibility fields such as temperature, seed, provider, and model revision.
- Updated factories and safe idempotent seed commands.
- Automated tests.
- Pinned dependencies and repeatable environment setup.
- Explicit database-level defaults where required.
- A documented deletion and retention policy.

## Recommended next steps

1. Align `factories.py` and `seed.py` with the current singular model classes and column names.
2. Replace destructive schema recreation with Alembic plus idempotent seed inserts.
3. Add a pinned `pyproject.toml` or `requirements.txt`.
4. Create CRUD endpoints for prompt families, prompt versions, and golden examples.
5. Implement an evaluation service that creates a run and writes one result per golden example.
6. Calculate aggregate metrics only after all result rows reach a terminal status.
7. Add dataset-version and model-configuration fields for reproducibility.
8. Add tests for constraints, relationships, migration upgrades, and evaluation aggregation.
9. Add indexes based on real query patterns, especially foreign keys and run/result lookups.
10. Decide deletion, retention, and cascading behavior before production use.

## Learning summary

This project provided practical experience in three connected areas:

### Prompt registry design

A prompt is not treated as one mutable string. A stable task is represented by a prompt family, while every candidate implementation is stored as a separately identifiable version. This preserves history and makes comparison possible.

### Multi-metric prompt evaluation

Prompt quality is represented by more than accuracy. The schema captures correctness, latency, token usage, cost, raw output, normalized output, and failure state so that prompt versions can be compared across operational as well as quality dimensions.

### End-to-end evaluation traceability

Every individual result can be traced to:

- The golden example and expected output.
- The evaluation run and model identity.
- The exact prompt version.
- The stable prompt family.

That chain makes an evaluation result explainable and auditable instead of leaving it as an isolated metric.

## Résumé-ready summary

> Designed a versioned LLM prompt registry and evaluation schema using FastAPI, SQLAlchemy, PostgreSQL, and Alembic. Established traceability across prompt families, prompt versions, model evaluation runs, golden examples, and per-example results while capturing accuracy, latency, cost, token usage, raw outputs, and failure states.
