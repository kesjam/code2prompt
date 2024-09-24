import logging

logging.basicConfig(level=logging.DEBUG)
logging.debug("Importing data_manager.py")

from datetime import datetime
from src.data.models import Dictation, Session, engine
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

# Get the user's home directory
user_home = os.path.expanduser("~")
app_data_dir = os.path.join(user_home, ".DictationApp")

# Ensure the app data directory exists
os.makedirs(app_data_dir, exist_ok=True)

# Update the database file path
db_path = os.path.join(app_data_dir, "dictations.db")

# Update the engine to use the new path
engine = create_engine(f"sqlite:///{db_path}")

# Create all tables
Dictation.metadata.create_all(engine)

# Create a sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Update other functions to use the new get_db function
def save_dictation(subject, content, audio_file_path, dictation_type):
    db = next(get_db())
    try:
        new_dictation = Dictation(
            subject=subject,
            content=content,
            audio_file_path=audio_file_path,
            dictation_type=dictation_type,
            date_time=datetime.now()
        )
        db.add(new_dictation)
        db.commit()
        logging.info("Dictation saved successfully.")
    except Exception as e:
        db.rollback()
        logging.error(f"Error saving dictation: {str(e)}")
        raise

def get_all_dictations():
    db = next(get_db())
    try:
        dictations = db.query(Dictation).order_by(Dictation.date_time.desc()).all()
        return dictations
    except Exception as e:
        logging.error(f"Error retrieving dictations: {str(e)}")
        raise
    finally:
        db.close()

def delete_dictation(dictation_id):
    db = next(get_db())
    try:
        dictation = db.query(Dictation).filter_by(id=dictation_id).first()
        if dictation:
            db.delete(dictation)
            db.commit()
            logging.info(f"Dictation with id {dictation_id} deleted successfully.")
            return True
        else:
            logging.warning(f"No dictation found with id {dictation_id}")
            return False
    except Exception as e:
        db.rollback()
        logging.error(f"Error deleting dictation: {str(e)}")
        raise
    finally:
        db.close()

def get_dictation_by_id(dictation_id):
    db = next(get_db())
    try:
        dictation = db.query(Dictation).filter_by(id=dictation_id).first()
        return dictation
    except Exception as e:
        logging.error(f"Error retrieving dictation: {str(e)}")
        return None
    finally:
        db.close()