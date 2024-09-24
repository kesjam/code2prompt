# tests/test_data.py

import os
import sys
import unittest

# Adjust the path to include the 'src' directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))))

from data.data_manager import (
    init_db, save_dictation, get_all_dictations, delete_dictation
)

class TestDataManager(unittest.TestCase):
    def setUp(self):
        # Initialize the database before each test
        init_db()
        # Optionally, clear the database if needed

    def test_save_and_retrieve_dictation(self):
        save_dictation(
            subject='Test Subject',
            content='Test Content',
            audio_file_path='path/to/audio.wav',
            dictation_type='Test Type'
        )
        dictations = get_all_dictations()
        self.assertEqual(len(dictations), 1)
        self.assertEqual(dictations[0].subject, 'Test Subject')

    def test_delete_dictation(self):
        save_dictation(
            subject='To Be Deleted',
            content='Content',
            audio_file_path='path/to/audio.wav',
            dictation_type='Test Type'
        )
        dictations = get_all_dictations()
        dictation_id = dictations[0].id
        delete_dictation(dictation_id)
        dictations_after_delete = get_all_dictations()
        self.assertEqual(len(dictations_after_delete), 0)

if __name__ == '__main__':
    unittest.main()
