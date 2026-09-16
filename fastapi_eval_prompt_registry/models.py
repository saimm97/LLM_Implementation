import enum
from typing import List
from sqlalchemy import Enum, Boolean, Column, Integer, String, ForeignKey, Text, Float,DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class OutputCategories(enum.Enum):
    SPT = 'Support ticket'
    BUG = "Bug"
    FEAT = "Feature Request"
    BILL = "Billing"

class PromptFamilyEnum(enum.Enum):
   SUPPORT_TICKET_TRIAGE = "support_ticket_triage"
   SUPPORT_REPLY_GENERATION = "support_reply_generation"
   TICKET_SUMMARIZATION = "ticket_summarization"
   TICKET_PRIORITY_CLASSIFICATION = "ticket_priority_classification"
   TICKET_ROUTING = "ticket_routing"
   SENTIMENT_ANALYSIS = "sentiment_analysis"
   CUSTOMER_INTENT_CLASSIFICATION = "customer_intent_classification"
   TICKET_ENTITY_EXTRACTION = "ticket_entity_extraction"
   DUPLICATE_TICKET_DETECTION = "duplicate_ticket_detection"
   ESCALATION_DETECTION = "escalation_detection"
   URGENCY_DETECTION = "urgency_detection"
   LANGUAGE_DETECTION = "language_detection"
   RESPONSE_QUALITY_EVALUATION = "response_quality_evaluation"
   RESPONSE_TONE_EVALUATION = "response_tone_evaluation"
   KNOWLEDGE_BASE_SEARCH_QUERY = "knowledge_base_search_query"


class EvalResultStatusEnum(enum.Enum):
    COMPLETED = "completed"
    INVALID_OUTPUT = "invalid_output"
    MODEL_ERROR = "model_error"
    TIMEOUT = "timeout"

class PromptVersion(Base):
    __tablename__ = 'prompt_versions'
    __table_args__ = (
        UniqueConstraint(
            "prompt_family_id",
            "version",
            name="uq_prompt_versions_family_version",
        ),
    )
    id = Column(Integer, primary_key=True)
    text = Column(Text,nullable=False)
    version = Column(String,nullable=False)
    is_active = Column(Boolean,unique=False, default=False)
    created_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    updated_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    prompt_family_id: Mapped[int] = mapped_column(ForeignKey("prompt_families.id"),nullable=False)
    prompt_family: Mapped["PromptFamily"] = relationship(back_populates="prompt_versions")
    eval_runners: Mapped[List["EvalRunner"]] = relationship(back_populates="prompt_version")

class PromptFamily(Base):
    __tablename__ = 'prompt_families'
    id = Column(Integer, primary_key=True)
    name = Column(Enum(PromptFamilyEnum,name='prompt_family_enum',native_enum=False,create_constraint=True),nullable=False,unique=True)
    created_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    updated_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    prompt_versions: Mapped[List["PromptVersion"]] = relationship(back_populates="prompt_family")

class GoldenExample(Base):
    __tablename__ = 'golden_examples'
    id = Column(Integer, primary_key=True)
    input = Column(String, nullable=False)
    expected_output = Column(Enum(OutputCategories,native_enum=False,create_constraint=True),nullable=False)
    is_active = Column(Boolean,nullable=False)
    created_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    updated_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    eval_results: Mapped[List["EvalResult"]] = relationship(back_populates="golden_example")


class EvalResult(Base):
    __tablename__ = 'eval_results'
    id = Column(Integer, primary_key=True)
    input = Column(String,nullable=False)
    predicted_category = Column(Enum(OutputCategories,native_enum=False,create_constraint=True), nullable=True)
    raw_output = Column(Text,nullable=True)
    input_tokens = Column(Integer,nullable=False,default=0)
    output_tokens = Column(Integer, nullable=False,default=0)
    total_tokens = Column(Integer, nullable=False,default=0)
    passed = Column(Boolean, nullable=False)
    latency_ms = Column(Integer, default=0)
    cost    = Column(Float,nullable=False,default=0.0)
    error_message = Column(Text,nullable=True)
    status = Column(Enum(EvalResultStatusEnum,name='eval_result_status_enum',native_enum=False,create_constraint=True),nullable=False)
    created_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    updated_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    # FKs 
    golden_example_id: Mapped[int] = mapped_column(ForeignKey("golden_examples.id"), nullable=False)
    eval_run_id: Mapped[int] = mapped_column(ForeignKey("eval_runs.id"), nullable=False)
    golden_example: Mapped["GoldenExample"] = relationship(back_populates="eval_results")
    eval_run: Mapped["EvalRunner"] = relationship(back_populates="eval_results")

class EvalRunner(Base):
    __tablename__ = 'eval_runs'
    id = Column(Integer, primary_key=True)
    p95_latency_ms = Column(Float,nullable=False,default=0.0)
    accuracy = Column(Float,nullable=False,default=0.0)
    average_cost = Column(Float,nullable=False,default=0.0)
    model_used = Column(String,nullable=False)
    prompt_version_id: Mapped[int] = mapped_column(ForeignKey("prompt_versions.id"),nullable=False)
    created_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now())
    updated_at = Column(DateTime(timezone=True),nullable=False,server_default=func.now(),onupdate=func.now())
    eval_results: Mapped[List["EvalResult"]] = relationship(back_populates="eval_run")
    prompt_version: Mapped["PromptVersion"] = relationship(back_populates="eval_runners")