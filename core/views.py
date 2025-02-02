# core/views.py
import io
import csv
from .models import Person
from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from .models import Person
from .forms import UploadFileForm  # Import the form from forms.py
from .utils import parse_date,fetch_gender_data,fetch_region_data,fetch_yearly_birth_data       # Import the utility function from utils.py

def home(request):
    person_list = Person.objects.all()
    paginator = Paginator(person_list, 10) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'referrals/home.html', {'page_obj': page_obj})

def upload(request):
    """Handle file upload and process CSV data to update Person records."""
    form = UploadFileForm(request.POST or None, request.FILES or None)

    if request.method == 'POST' and form.is_valid():
        file = request.FILES['file']
        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)  # Create a StringIO object
        next(io_string)  # Skip header row

        for row in csv.reader(io_string, delimiter=','):
            date_of_birth = parse_date(row[1])  # Use the helper function to parse date

            # Update or create Person records based on the CSV data
            Person.objects.update_or_create(
                id=row[0],
                defaults={
                    'date_of_birth': date_of_birth,
                    'gender': row[2],
                    'region': row[3] if len(row) > 3 else None
                }
            )
        return render(request, 'referrals/upload.html', {'form': form, 'success': True})

    elif request.method == 'POST':
        messages.error(request, 'Unable to upload file.')

    return render(request, 'referrals/upload.html', {'form': form})




def charts(request):
    """Fetch and prepare data for charts based on Person records."""
    genders, gender_counts = fetch_gender_data()
    regions, region_counts = fetch_region_data()
    years, yearly_counts = fetch_yearly_birth_data()

    context = {
        'genders': genders,
        'gender_counts': gender_counts,
        'regions': regions,
        'region_counts': region_counts,
        'years': years,
        'yearly_counts': yearly_counts,
    }

    return render(request, "referrals/charts.html", context)
