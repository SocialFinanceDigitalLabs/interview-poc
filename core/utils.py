# core/utils.py
from django.db.models import Count
from datetime import datetime
from .models import Person
from django.db.models.functions import ExtractYear

def parse_date(date_str):
    """Parse date from DD/MM/YYYY format to YYYY-MM-DD."""
    if date_str:
        try:
            return datetime.strptime(date_str, '%d/%m/%Y').date()
        except ValueError:
            return None  # Return None if the date format is incorrect
    return None  # Handle empty date case


def fetch_gender_data():
    """Fetch and prepare gender distribution data."""
    gender_count = Person.objects.values('gender').annotate(count=Count('id'))  
    genders = [entry['gender'] for entry in gender_count]
    gender_counts = [entry['count'] for entry in gender_count]
    return genders, gender_counts

def fetch_region_data():
    """Fetch and prepare region distribution data."""
    region_count = Person.objects.values('region').annotate(count=Count('id'))
    regions = [entry['region'] for entry in region_count if entry['region']]
    region_counts = [entry['count'] for entry in region_count if entry['region']]
    return regions, region_counts

def fetch_yearly_birth_data():
    """Fetch and prepare yearly birth count data."""
    birth_year_count = (
        Person.objects
        .annotate(year=ExtractYear('date_of_birth'))  
        .values('year')
        .annotate(count=Count('id'))
        .order_by('year')
    )
    years = [entry['year'] for entry in birth_year_count]
    counts = [entry['count'] for entry in birth_year_count]
    return years, counts