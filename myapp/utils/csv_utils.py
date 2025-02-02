import csv
import datetime
from ..models import Person
import logging
from django.db.models import Count
import chardet

logger = logging.getLogger('django')


def upload_csv(csv_file):
    """
    Reads a CSV file, validates row data, and bulk-creates Person objects.

    This function detects the file's encoding, read the CSV content, and
    parses each row. It applies validations such as checking date formats,
    and ensures no future dates are accepted, and skips rows where the region is numeric.
    Rows that pass this validation are stored in 'bulk_list; and inserted into the database using
    bulk_create()

    :param csv_file: An uploaded CSV file object from the request.
    :returns: A dictionary summarizing the results:
               'error_count': number of rows that failed validation or insertion,
               'success_count': number of rows successfully inserted,
               'total_count': total rows processed in the CSV
             
    """


    try:
        uploaded_file = csv_file.read()
    except Exception as e:
        logger.error(f"Error reading file {e}")
        return {'error_count': 0, 'success_count': 0, 'total_count': 0}
    
    try:
        detect_encoding = chardet.detect(uploaded_file)
        decoded_file = uploaded_file.decode(detect_encoding['encoding']).splitlines()
        reader = csv.DictReader(decoded_file)
    except Exception as e:
        logger.error(f"Error decoding file {e}")
        return {'error_count': 0, 'success_count': 0, 'total_count': 0}
   
    result_status = {'error_count': 0, 'success_count': 0, 'total_count': 0}
    today = datetime.date.today()
    bulk_create_list = []  

    for rownum, row in enumerate(reader,start=1):
        try:
            dob = datetime.datetime.strptime(row['date_of_birth'], '%d/%m/%Y').date()
            if not dob:
                logger.warning(f"DOB is empty, {dob}")
                result_status['error_count'] += 1
                continue
            if dob > today:
                logger.warning(f"DOB is in the future, {dob}")
                result_status['error_count'] += 1
                continue
        except (ValueError, KeyError):
            logger.warning(f"Problem with DOB for row num {rownum}")
            result_status['error_count'] += 1
            continue

        try:
            if row.get('region','').isdigit():
                logger.warning('Region is a number')
                result_status['error_count'] += 1
                continue
        except KeyError:
            logger.warning(f"Problem with region for row num {rownum}")
            result_status['error_count'] += 1
            continue
        try:    
            person = Person(
                external_id = row['id'],
                date_of_birth = dob,
                gender = row['gender'],
                region = row.get('region') or None
                )
            bulk_create_list.append(person)
            result_status['success_count'] += 1
        except Exception as e:
            logger.error(f"Error creating person {e}")
            result_status['error_count'] += 1
            continue
        
    result_status['total_count'] = rownum

    if bulk_create_list:
        try:
            Person.objects.bulk_create(bulk_create_list)
        except Exception as e:
            logger.error(f'Error during bulk creation {e}')
    logger.info(f"Total rows, {rownum}, Uploaded {result_status['success_count']} rows, {result_status['error_count']} rows failed")
    return result_status           


def chart_data():
    """
    aggregated data for charts, grouped by gender and region.

    This function performs the tasks below:
      1. Counts the number of Person records per gender.
      2. Counts the number of Person records per region and gender, also excluding empty or null regions.
    The results are structured into a dictionary that makes it easier to create
    charts in the front-end.

    :return: A dictionary containing:
               'gender_labels': list of unique genders,
               'gender_counts': number of persons per gender,
               'all_regions': list of distinct regions (alphabetically sorted),
               'region_datasets': gender-specific data distributed across different regions
    """

    try:
        gender_data = (Person.objects.values('gender')
                    .annotate(count = Count('id'))
                    .order_by('-count'))
        gender_labels = [item['gender'] for item in gender_data]
        gender_counts = [item['count'] for item in gender_data]

    except Exception as e:
        logger.error(f"Error getting gender queryset {e}")
    

    
    try:
        region_dataset = (Person.objects.exclude(region__isnull=True)
                        .exclude(region='')
                        .values('region','gender')
                        .annotate(count=Count('id'))
                        .order_by('-count')                    
                        )
        all_regions = sorted(set([item['region'] for item in region_dataset]))
        all_genders = sorted(set(item['gender'] for item in region_dataset))
   
    except Exception as e:
        logger.error(f"Error getting region queryset {e}")



    region_gender_counts = {}
    try:
        for item in region_dataset:
            region = item['region']
            gender = item['gender']
            count = item['count']

            if region not in region_gender_counts:
                region_gender_counts[region] = {}
            region_gender_counts[region][gender] = count

        region_datasets = []
        for gender in all_genders:
            data_for_gender = []
            for region in all_regions:
                count = region_gender_counts.get(region, {}).get(gender,0)
                data_for_gender.append(count)

            region_datasets.append({
                'label' : gender,
                'data': data_for_gender
            })
    except Exception as e:
        logger.error(f"Error creating region datasets {e}")

    return {'gender_labels':gender_labels,
            'gender_counts':gender_counts,
            'all_regions':all_regions,
            'region_datasets':region_datasets}
