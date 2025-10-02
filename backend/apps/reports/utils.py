# apps/reports/utils.py

import csv
from io import StringIO
from django.db.models.fields.related import ManyToManyField, ForeignKey
from django.db.models.fields import DateTimeField
from django.utils import timezone

def queryset_to_csv(queryset, fields=None, exclude=None):
    """
    A generic utility function to convert a Django QuerySet into a CSV string.

    Args:
        queryset (QuerySet): The QuerySet to convert.
        fields (list): A list of field names to include. If None, all fields will be included.
        exclude (list): A list of field names to exclude.

    Returns:
        str: A CSV formatted string.
    """
    if not queryset:
        return ""

    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)

    # Determine fields to include
    model = queryset.model
    if fields:
        field_names = [field for field in fields if field in [f.name for f in model._meta.get_fields()]]
    else:
        field_names = [f.name for f in model._meta.get_fields()]

    if exclude:
        field_names = [f for f in field_names if f not in exclude]

    # Write headers
    writer.writerow(field_names)

    # Write data rows
    for obj in queryset:
        row = []
        for field in field_names:
            try:
                value = getattr(obj, field)
                
                # Handle specific field types for clean CSV export
                if isinstance(model._meta.get_field(field), ForeignKey):
                    value = getattr(value, 'pk') if value else None
                elif isinstance(model._meta.get_field(field), DateTimeField):
                    value = timezone.localtime(value).strftime("%Y-%m-%d %H:%M:%S") if value else None
                elif isinstance(model._meta.get_field(field), ManyToManyField):
                    # For Many-to-Many fields, we don't include them in simple exports
                    # or you could handle them by listing PKs
                    value = "N/A"
                
                row.append(value)
            except AttributeError:
                # Handle custom methods or properties on the model
                row.append(str(getattr(obj, field)()))
        writer.writerow(row)

    return csv_buffer.getvalue()