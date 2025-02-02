from django.shortcuts import render, redirect
from myapp.forms import CSVUploadForm
from .models import Person
import logging
from .utils import csv_utils
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.cache import cache

logger = logging.getLogger('django')

def home(request):
    return render(request, "referrals/home.html")

def upload(request):
    """
    Displays and handles the CSV upload form.

    If request method is POST and the form is valid, this view calls a 
    function which process the uploaded CSV and creates Person records. It then displays
    a message indicating how many rows were successfully or unsuccessfully processed.
    If data already exists in the database, the template prevents further uploads by checking 'data_exists'.
    """
    data_exists = Person.objects.exists()
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            result_status = csv_utils.upload_csv(csv_file)
            success_count = result_status['success_count']
            error_count = result_status['error_count']
            total_count = result_status['total_count']
            messages.info(request, f'Uploaded {success_count} rows, {error_count} rows failed out of {total_count} rows')
            return redirect('data')
            
    
    else:
        form = CSVUploadForm()
    context = {'form': form, 'data_exists': data_exists}
    return render(request, "referrals/upload.html", context)

def data(request):
    """
    Lists all Person objects in a paginated table.

    This view retrieves all Person records from the database, ordered by ID,
    and uses Paginator to show 20 rows per page. It also checks if 'data_exists'
    to determine what html is rendered on the template
    passes if any data is present. If data is not present, the template lets the user know with message. 

    """

    people = Person.objects.all().order_by('id')
    data_exists = people.exists()
    paginator = Paginator(people, 20)
    page_number  = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'page_obj': page_obj,'data_exists': data_exists}   
    return render(request, "referrals/data.html", context)

def charts(request):
    """
    Displays charts based on aggregated Person data.

    This view attemts to retrieve chart data from the cache. If cache miss occurs,
    it calls the chart_data() utility function to retrieve data from the function
    and then caches the result for future requests. It also checks if 'data_exists'
    to determine what html is rendered on the template
    If data is not present, the template lets the user know with a message. 
    """
    if not Person.objects.exists():
        # The DB is empty, so ignore or clear the cache
        cache.delete('chart_data')
        data_exists = False
        context = {'data_exists': data_exists}
        return render(request, 'referrals/charts.html', context)

    cache_key = 'chart_data'
    cached_data = cache.get(cache_key)
    if cached_data is not None:
        logger.info('Cache Hit')
        gender_labels = cached_data['gender_labels']
        gender_counts = cached_data['gender_counts']
        all_regions = cached_data['all_regions']
        region_datasets = cached_data['region_datasets']

    else:
        logger.info('Cache Miss')
        chart_data = csv_utils.chart_data()
        gender_labels = chart_data['gender_labels']
        gender_counts = chart_data['gender_counts']
        all_regions = chart_data['all_regions']
        region_datasets = chart_data['region_datasets']

        cache.set(cache_key, chart_data, 600)

    data_exists = bool(gender_labels or gender_counts or all_regions or region_datasets)
    context = {
        'gender_labels': gender_labels,
        'gender_counts': gender_counts,
        'region_labels': all_regions,
        'region_count': region_datasets,
        'data_exists': data_exists
    }

    return render(request, "referrals/charts.html", context)

