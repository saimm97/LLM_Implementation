
from config.database_connection import get_sqlalchemy_session
from factories import * 
import json, random
from models import Base
from sqlalchemy.orm import Session
from polyfactory import AsyncPersistenceProtocol, SyncPersistenceProtocol

def data_seed(database_session):

  try: 
    
    for factory in (PromptVersionsFactory, PromptFamilyFactory, EvalResultsFactory, EvalRunnerFactory):
      factory.__session__ = database_session

    # 3. Create Prompt Versions & Families
    versions =  PromptVersionsFactory.create_batch_sync(5)
    for version in versions:
      PromptFamilyFactory.create_batch_sync(5,prompt_version_id=version.id)

    golden_examples = fetch_golden_examples(database_session)
    golden_ids = [ge.id for ge in golden_examples]

    # 4. Create Eval Runs
    eval_runs = EvalRunnerFactory.create_batch_sync(5)

    for eval_run in eval_runs:
      EvalResultsFactory.create_sync(eval_runs_id=eval_run.id,
      golden_examples_id=random.choice(golden_ids))


    # for eval_run in eval_runs:
    #   for _ in range(5):
    #     result = EvalResultsFactory.build()
    #     result.golden_examples_id = random.choice(golden_ids)
    #     result.eval_runs_id = eval_run.id
    #     database_session.add(result)

    database_session.commit()

  except Exception as error: 
    database_session.rollback()
    raise error

  finally: 
    database_session.close()


def fetch_golden_examples(session):
  """Reads golden_examples.json, stages records into DB, and returns created instances with populated IDs."""
  with open("golden_examples.json") as f:
    rows = json.load(f)

  created_examples = []

  for row in rows:
    example = GoldenExamples(input=row['input'],
    expected_output = OutputCategories[row['expected_output']],
    is_active=True,
    )
    session.add(example)
    created_examples.append(example)

  session.flush()  
  session.commit()

  print(f"Committed {len(created_examples)} golden examples, first id: {created_examples[0].id}")

  return created_examples


if __name__ == "__main__":
  database_session = get_sqlalchemy_session()

  print("Resetting database schema...")
  Base.metadata.drop_all(bind=database_session.bind)
  Base.metadata.create_all(bind=database_session.bind)

  print("Seeding data...")
  data_seed(database_session)