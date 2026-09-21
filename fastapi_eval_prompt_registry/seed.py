import json
import math
import random
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from config.database_connection import get_sqlalchemy_session
from factories import (
    EvalResultFactory,
    EvalRunnerFactory,
    GoldenExampleFactory,
    PromptFamilyFactory,
    PromptVersionFactory,
    faker,
)
from models import (
    EvalResult,
    EvalResultStatusEnum,
    EvalRunner,
    GoldenExample,
    OutputCategories,
    PromptFamily,
    PromptFamilyEnum,
    PromptVersion,
)


GOLDEN_EXAMPLES_FILE = Path(__file__).with_name("golden_examples.json")
SEED_FAMILY = PromptFamilyEnum.SUPPORT_TICKET_TRIAGE
SEED_MODEL = "seed-model-v1"
SEED_VERSIONS = ("1.0.0", "1.1.0", "1.2.0", "1.3.0", "1.4.0")


def data_seed(database_session: Session, random_seed: int = 42) -> dict[str, int]:
    """Insert a repeatable prompt-evaluation dataset in one transaction."""
    rng = random.Random(random_seed)
    faker.seed_instance(random_seed)

    try:
        family, family_created = get_or_create_prompt_family(database_session)
        versions, versions_created = get_or_create_prompt_versions(
            database_session, family
        )
        golden_examples, examples_created = fetch_golden_examples(database_session)
        runs_created, results_created = create_evaluation_runs(
            database_session,
            versions,
            golden_examples,
            rng,
        )
        database_session.commit()
    except Exception:
        database_session.rollback()
        raise

    return {
        "prompt_families_created": int(family_created),
        "prompt_versions_created": versions_created,
        "golden_examples_created": examples_created,
        "eval_runs_created": runs_created,
        "eval_results_created": results_created,
    }


def get_or_create_prompt_family(
    session: Session,
) -> tuple[PromptFamily, bool]:
    family = session.scalar(
        select(PromptFamily).where(PromptFamily.name == SEED_FAMILY)
    )
    if family is not None:
        return family, False

    family = PromptFamilyFactory.build(name=SEED_FAMILY)
    session.add(family)
    session.flush()
    return family, True


def get_or_create_prompt_versions(
    session: Session,
    family: PromptFamily,
) -> tuple[list[PromptVersion], int]:
    versions: list[PromptVersion] = []
    created = 0

    for index, version_number in enumerate(SEED_VERSIONS):
        version = session.scalar(
            select(PromptVersion).where(
                PromptVersion.prompt_family_id == family.id,
                PromptVersion.version == version_number,
            )
        )
        if version is None:
            version = PromptVersionFactory.build(
                prompt_family_id=family.id,
                version=version_number,
                is_active=index == len(SEED_VERSIONS) - 1,
            )
            session.add(version)
            session.flush()
            created += 1
        versions.append(version)

    return versions, created


def fetch_golden_examples(
    session: Session,
) -> tuple[list[GoldenExample], int]:
    """Load JSON examples without duplicating inputs already in the database."""
    with GOLDEN_EXAMPLES_FILE.open(encoding="utf-8") as stream:
        rows = json.load(stream)

    examples: list[GoldenExample] = []
    created = 0

    for row in rows:
        example = session.scalar(
            select(GoldenExample).where(GoldenExample.input == row["input"])
        )
        if example is None:
            example = GoldenExampleFactory.build(
                input=row["input"],
                expected_output=OutputCategories[row["expected_output"]],
                is_active=True,
            )
            session.add(example)
            session.flush()
            created += 1
        examples.append(example)

    return examples, created


def create_evaluation_runs(
    session: Session,
    versions: list[PromptVersion],
    golden_examples: list[GoldenExample],
    rng: random.Random,
) -> tuple[int, int]:
    runs_created = 0
    results_created = 0

    for version in versions:
        existing_run = session.scalar(
            select(EvalRunner).where(
                EvalRunner.prompt_version_id == version.id,
                EvalRunner.model_used == SEED_MODEL,
            )
        )
        if existing_run is not None:
            continue

        eval_run = EvalRunnerFactory.build(
            prompt_version_id=version.id,
            model_used=SEED_MODEL,
            p95_latency_ms=0.0,
            accuracy=0.0,
            average_cost=0.0,
        )
        session.add(eval_run)
        session.flush()

        results = [
            build_eval_result(eval_run, example, rng) for example in golden_examples
        ]
        session.add_all(results)
        session.flush()

        update_aggregate_metrics(eval_run, results)
        runs_created += 1
        results_created += len(results)

    return runs_created, results_created


def build_eval_result(
    eval_run: EvalRunner,
    golden_example: GoldenExample,
    rng: random.Random,
) -> EvalResult:
    passed = rng.random() < 0.8
    predicted_category = (
        golden_example.expected_output
        if passed
        else rng.choice(
            [
                category
                for category in OutputCategories
                if category != golden_example.expected_output
            ]
        )
    )
    input_tokens = rng.randint(20, 250)
    output_tokens = rng.randint(1, 30)
    total_tokens = input_tokens + output_tokens
    latency_ms = rng.randint(50, 2_000)
    cost = round(total_tokens * 0.000002, 6)

    return EvalResultFactory.build(
        input=golden_example.input,
        predicted_category=predicted_category,
        raw_output=predicted_category.value,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        passed=passed,
        latency_ms=latency_ms,
        cost=cost,
        error_message=None,
        status=EvalResultStatusEnum.COMPLETED,
        golden_example_id=golden_example.id,
        eval_run_id=eval_run.id,
    )


def update_aggregate_metrics(
    eval_run: EvalRunner,
    results: list[EvalResult],
) -> None:
    if not results:
        eval_run.accuracy = 0.0
        eval_run.average_cost = 0.0
        eval_run.p95_latency_ms = 0.0
        return

    eval_run.accuracy = sum(result.passed for result in results) / len(results)
    eval_run.average_cost = sum(result.cost for result in results) / len(results)

    latencies = sorted(
        result.latency_ms for result in results if result.latency_ms is not None
    )
    if not latencies:
        eval_run.p95_latency_ms = 0.0
        return

    percentile_index = max(0, math.ceil(0.95 * len(latencies)) - 1)
    eval_run.p95_latency_ms = float(latencies[percentile_index])


if __name__ == "__main__":
    session = get_sqlalchemy_session()
    try:
        summary = data_seed(session)
        print("Seed completed:", summary)
    finally:
        session.close()
