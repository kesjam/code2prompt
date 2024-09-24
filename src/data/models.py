# src/data/data_manager.py

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import sqlite3
import logging
import os

Base = declarative_base()

class Dictation(Base):
    __tablename__ = 'dictations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject = Column(String, nullable=False)
    summary = Column(String, nullable=True)
    content = Column(String, nullable=False)
    audio_file_path = Column(String, nullable=False)
    dictation_type = Column(String, nullable=False)
    date_time = Column(DateTime, nullable=False)

# Ensure the data directory exists
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

# Initialize SQLAlchemy engine
engine = create_engine('sqlite:///data/dictations.db', echo=False)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    Base.metadata.create_all(engine)
    add_summary_column(engine)

def save_dictation(subject, summary, content, audio_file_path, dictation_type):
    try:
        with Session() as session:
            new_dictation = Dictation(
                subject=subject,
                summary=summary,
                content=content,
                audio_file_path=audio_file_path,
                dictation_type=dictation_type,
                date_time=datetime.now()
            )
            session.add(new_dictation)
            session.commit()
        logging.info("Dictation saved successfully.")
    except Exception as e:
        logging.error(f"Error saving dictation: {e}")

def get_all_dictations():
    session = Session()
    try:
        dictations = session.query(Dictation).order_by(Dictation.date_time.desc()).all()
        return dictations
    except Exception as e:
        logging.error(f"Error fetching dictations: {e}")
        return []
    finally:
        session.close()

def delete_dictation(dictation_id):
    try:
        with Session() as session:
            dictation = session.query(Dictation).filter(Dictation.id == dictation_id).first()
            if dictation:
                session.delete(dictation)
                session.commit()
                logging.info(f"Dictation with ID {dictation_id} deleted successfully.")
            else:
                logging.warning(f"Dictation with ID {dictation_id} not found.")
    except Exception as e:
        logging.error(f"Error deleting dictation: {e}")

def add_summary_column_if_not_exists():
    try:
        # Determine the absolute path to the database
        db_path = os.path.join(data_dir, 'dictations.db')
        
        logging.debug(f"Connecting to database at {db_path}")
        
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the 'summary' column exists
        cursor.execute("PRAGMA table_info(dictations);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'summary' not in columns:
            cursor.execute("ALTER TABLE dictations ADD COLUMN summary TEXT;")
            logging.info("Added 'summary' column to 'dictations' table.")
        else:
            logging.info("'summary' column already exists in 'dictations' table.")
        
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

