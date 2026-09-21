from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import PostGenerated, Require, Use

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


faker = Faker()


class PromptFamilyFactory(SQLAlchemyFactory[PromptFamily]):
    __set_primary_key__ = False
    __set_relationships__ = False

    name = Use(lambda: faker.random_element(tuple(PromptFamilyEnum)))


class PromptVersionFactory(SQLAlchemyFactory[PromptVersion]):
    __set_primary_key__ = False
    __set_relationships__ = False

    text = Use(lambda: faker.paragraph(nb_sentences=3))
    version = Use(lambda: faker.numerify(text="#.#.#"))
    is_active = Use(faker.pybool)
    prompt_family_id = Require()


class GoldenExampleFactory(SQLAlchemyFactory[GoldenExample]):
    __set_primary_key__ = False
    __set_relationships__ = False

    input = Use(lambda: faker.text(max_nb_chars=200))
    expected_output = Use(lambda: faker.random_element(tuple(OutputCategories)))
    is_active = True


class EvalRunnerFactory(SQLAlchemyFactory[EvalRunner]):
    __set_primary_key__ = False
    __set_relationships__ = False

    p95_latency_ms = Use(lambda: faker.random_int(min=5_000, max=300_000) / 100)
    accuracy = Use(lambda: faker.random_int(min=0, max=10_000) / 10_000)
    average_cost = Use(lambda: faker.random_int(min=0, max=100_000) / 1_000_000)
    model_used = Use(
        lambda: faker.random_element(("gpt-4.1-mini", "gpt-4.1", "gpt-5-mini"))
    )
    prompt_version_id = Require()


class EvalResultFactory(SQLAlchemyFactory[EvalResult]):
    __set_primary_key__ = False
    __set_relationships__ = False

    input = Use(lambda: faker.text(max_nb_chars=200))
    predicted_category = Use(lambda: faker.random_element(tuple(OutputCategories)))
    raw_output = Use(lambda: faker.text(max_nb_chars=100))
    input_tokens = Use(lambda: faker.random_int(min=20, max=1_000))
    output_tokens = Use(lambda: faker.random_int(min=1, max=300))
    total_tokens = PostGenerated(
        lambda _name, values: values["input_tokens"] + values["output_tokens"]
    )
    passed = Use(faker.pybool)
    latency_ms = Use(lambda: faker.random_int(min=50, max=3_000))
    cost = Use(lambda: faker.random_int(min=1, max=100_000) / 1_000_000)
    error_message = None
    status = EvalResultStatusEnum.COMPLETED
    golden_example_id = Require()
    eval_run_id = Require()
