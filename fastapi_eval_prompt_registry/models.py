import enum
from typing import List
# from ssl import _PasswordType
# from tokenize import ContStr
from sqlalchemy import Enum, Boolean, Column, Integer, String, ForeignKey, Text, Float
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class OutputCategories(enum.Enum):
    SPT = 'Support ticket'
    BUG = "Bug"
    FEAT = "Feature Request"
    BILL = "Billing"

class PromptFamilyEnum(enum.Enum):
    AFAM = 'AFM'
    BFAM = "BFAM"
    CFAM = "CFAM"
    DFAM = "DFAM"

class Dummy(Base):
    __tablename__ = 'dummy'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100))

class PromptVersions(Base):
    __tablename__ = 'prompt_versions'
    id = Column(Integer, primary_key=True)
    text = Column(Text,nullable=False)
    version = Column(String,nullable=False)
    is_active = Column(Boolean,unique=False, default=False)

    prompt_families: Mapped[List["PromptFamily"]] = relationship()

class PromptFamily(Base):
    __tablename__ = 'prompt_families'
    id = Column(Integer, primary_key=True)
    name = Column(Enum(PromptFamilyEnum))
    prompt_version_id: Mapped[int] = mapped_column(ForeignKey("prompt_versions.id"))

class GoldenExamples(Base):
    __tablename__ = 'golden_examples'
    id = Column(Integer, primary_key=True)
    input = Column(String, nullable=False)
    expected_output = Column(Enum(OutputCategories,native_enum=False))
    is_active = Column(Boolean,nullable=False)

    eval_results: Mapped[List["EvalResults"]] = relationship()

class EvalResults(Base):
    __tablename__ = 'eval_results'
    id = Column(Integer, primary_key=True)
    input = Column(String,nullable=False)
    output = Column(String, nullable=False)
    passed = Column(Boolean, nullable=False)
    latency = Column(String)
    cost    = Column(Float,nullable=False)
    # FKs 
    golden_examples_id: Mapped[int] = mapped_column(ForeignKey("golden_examples.id"))
    eval_runs_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"))

class EvalRunner(Base):
    __tablename__ = 'eval_runs'
    id = Column(Integer, primary_key=True)
    p95_latency = Column(String,nullable=False)
    accuracy = Column(Float,nullable=False)
    average_cost = Column(Float,nullable=False)

    eval_results: Mapped[List["EvalResults"]] = relationship()