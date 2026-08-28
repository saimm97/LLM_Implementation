from models import *
from faker import Faker
# from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory import Use

faker = Faker()

class PromptVersionsFactory(SQLAlchemyFactory[PromptVersions]):
  __set_primary_key__ = False  
  __tablename__ = "Prompt_versions"
  __set_relationships__ = False
  text = Use(lambda: faker.text())
  version = '1.0.0'
  is_active = Use(faker.pybool)

class PromptFamilyFactory(SQLAlchemyFactory[PromptFamily]):
    __set_primary_key__ = False  
    __tablename__ = 'prompt_families'
    # name = Use(faker.enum(PromptFamilyEnum))  # wrong way to do this: 
    # name = Use(faker.random_element(elements=PromptFamilyEnum))
    name = Use(lambda: faker.enum(PromptFamilyEnum))
    # prompt_version_id: Mapped[int] = mapped_column(ForeignKey("prompt_versions.id"))

class GoldenExamplesFactory(SQLAlchemyFactory[GoldenExamples]):
    __set_primary_key__ = False  
    __tablename__ = 'golden_examples'
    __set_relationships__ = False

    input = Use(faker.text(max_nb_chars=200))
    expected_output = Use(lambda: faker.enum(OutputCategories))
    is_active = Use(faker.pybool)
    # eval_results: Mapped[List["EvalResults"]] = relationship()

class EvalResultsFactory(SQLAlchemyFactory[EvalResults]):
    __set_primary_key__ = False  
    __tablename__ = 'eval_results'
    __set_relationships__ = False

    input = Use(lambda: faker.text(max_nb_chars=200))
    output = Use(lambda: faker.text(max_nb_chars=200))
    passed = Use(faker.pybool)
    latency = Use(lambda: str(faker.random_int(min=50, max=3000)))
    cost    = Use(lambda: faker.pyfloat(left_digits=2, right_digits=2, positive=True))

    # FKs 
    # golden_examples_id: Mapped[int] = mapped_column(ForeignKey("golden_examples.id"))
    # eval_runs_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"))

class EvalRunnerFactory(SQLAlchemyFactory[EvalRunner]):
    __set_primary_key__ = False  
    __tablename__ = 'eval_runs'
    __set_relationships__ = False

    p95_latency = Use(lambda: faker.pyfloat(left_digits=2, right_digits=2, positive=True))
    accuracy = Use(lambda: faker.pyfloat(left_digits=2, right_digits=2, positive=True))
    average_cost = Use(lambda: faker.pyfloat(left_digits=2, right_digits=2, positive=True))
    # eval_results: Mapped[List["EvalResults"]] = relationship()