from sqlalchemy import Column, String, text
from sqlalchemy.exc import OperationalError
from src.data.models import Dictation

def add_summary_column(engine):
    from sqlalchemy import inspect

    inspector = inspect(engine)
    if 'dictations' in inspector.get_table_names():
        columns = [col['name'] for col in inspector.get_columns('dictations')]
        if 'summary' not in columns:
            try:
                with engine.begin() as connection:
                    connection.execute(text("ALTER TABLE dictations ADD COLUMN summary TEXT"))
                print("Added 'summary' column to 'dictations' table.")
            except OperationalError:
                print("'summary' column already exists in 'dictations' table.")
        else:
            print("'summary' column already exists in 'dictations' table.")
    else:
        print("'dictations' table does not exist. It will be created with all columns.")