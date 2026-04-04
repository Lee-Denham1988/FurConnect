with open('events/views.py', 'r') as f:
    content = f.read()

# Replace the broken download_csv_template function
old_code = '''@login_required
def download_csv_template(request, convention_pk):
    def batch_host_details(request):
    existing_tags = list(Tag.objects.all().values_list('name', flat=True)[:2]) or ['Art', 'Workshop']
    existing_hosts = list(PanelHost.objects.all().values_list('name', flat=True)[:2]) or ['John Doe', 'Jane Smith']
    
    # Write example row
    writer.writerow([
        'Furry Art Workshop',
        'Learn to draw furry art',
        '2024-03-15',
        '10:00',
        '12:00',
        existing_rooms[0],
        ', '.join(existing_tags),
        ', '.join(existing_hosts)
    ])
    
    return response'''

new_code = '''@login_required
def download_csv_template(request, convention_pk):
    convention = get_object_or_404(Convention, pk=convention_pk)
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{convention.name}_panels_template.csv"'
    
    # Create CSV writer
    writer = csv.writer(response, quoting=csv.QUOTE_ALL, lineterminator='\n')
    
    # Write header row
    writer.writerow([
        'title',
        'description', 
        'date',
        'start_time',
        'end_time',
        'room',
        'tags',
        'hosts'
    ])
    
    # Get example data
    existing_rooms = list(Room.objects.filter(convention=convention).values_list('name', flat=True)[:1]) or ['Main Hall']
    existing_tags = list(Tag.objects.all().values_list('name', flat=True)[:2]) or ['Art', 'Workshop']
    existing_hosts = list(PanelHost.objects.all().values_list('name', flat=True)[:2]) or ['John Doe', 'Jane Smith']
    
    # Write example row
    writer.writerow([
        'Furry Art Workshop',
        'Learn to draw furry art',
        '2024-03-15',
        '10:00',
        '12:00',
        existing_rooms[0],
        ', '.join(existing_tags),
        ', '.join(existing_hosts)
    ])
    
    return response'''

content = content.replace(old_code, new_code)

with open('events/views.py', 'w') as f:
    f.write(content)