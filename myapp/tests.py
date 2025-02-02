from django.test import TestCase
from io import StringIO
import csv
from .utils.csv_utils import upload_csv
from django.core.files.uploadedfile import SimpleUploadedFile

class CSVUploadTests(TestCase):
    """
    Tests for the upload_csv function in csv_utils.py 
    Checks if the function correctly rejects rows with future dates and numeric regions
    """
    def create_test_csv(self, rows):
        csv_file = StringIO()
        writer = csv.DictWriter(csv_file, fieldnames=['id', 'date_of_birth', 'gender', 'region'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        
        csv_content = csv_file.getvalue().encode()
        return SimpleUploadedFile("test.csv", csv_content, content_type="text/csv")

    def test_future_date_rejection(self):

        test_data = [{
            'id': '1',
            'date_of_birth': '2025-01-01',
            'gender': 'F',
            'region': 'North'
        }]
        csv_file = self.create_test_csv(test_data)
        

        result = upload_csv(csv_file)
        

        self.assertEqual(result['error_count'], 1)
        self.assertEqual(result['success_count'], 0)
        self.assertEqual(result['total_count'], 1)

    def test_numeric_region_rejection(self):

        test_data = [{
            'id': '1',
            'date_of_birth': '1990-01-01', 
            'gender': 'M',
            'region': '123'
        }]
        csv_file = self.create_test_csv(test_data)
        

        result = upload_csv(csv_file)
        

        self.assertEqual(result['error_count'], 1)
        self.assertEqual(result['success_count'], 0)
        self.assertEqual(result['total_count'], 1)
