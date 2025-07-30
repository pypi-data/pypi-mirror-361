from django.http import HttpResponse
import csv


def export_queryset_to_csv(queryset, field_names, filename="export.csv"):
    """
    Exports a Django queryset to a CSV file.

    Args:
        queryset (QuerySet): Django QuerySet to export.
        field_names (list): List of model field names to include in the export.
        filename (str): Name of the generated CSV file.

    Returns:
        HttpResponse: Django HTTP response with CSV data.
    """
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.writer(response)
    writer.writerow(field_names)

    for obj in queryset:
        row = []
        for field in field_names:
            value = getattr(obj, field, '')
            row.append(value)
        writer.writerow(row)

    return response
