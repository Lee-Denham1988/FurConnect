from django import forms
from datetime import timedelta, datetime
from .models import Convention, ConventionDay, Panel, PanelHost, Tag, Room, PanelHostOrder

class ConventionForm(forms.ModelForm):
    hotel_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    address = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    country = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': ' '})
    )
    banner_image = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = Convention
        fields = ['name', 'description', 'start_date', 'end_date', 'banner_image']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'rows': 3,
                'required': False
            }),
            'start_date': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'required': True
            }),
            'end_date': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'text',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            # Populate location fields
            if self.instance.location:
                location_parts = [part.strip() for part in self.instance.location.split(',')]
                # Assign parts based on the order in the clean method
                self.fields['hotel_name'].initial = location_parts[0] if len(location_parts) > 0 else ''
                self.fields['address'].initial = location_parts[1] if len(location_parts) > 1 else ''
                self.fields['city'].initial = location_parts[2] if len(location_parts) > 2 else ''
                self.fields['state'].initial = location_parts[3] if len(location_parts) > 3 else ''
                self.fields['country'].initial = location_parts[4] if len(location_parts) > 4 else ''

            # Populate date fields
            if self.instance.start_date:
                self.fields['start_date'].initial = self.instance.start_date
            if self.instance.end_date:
                self.fields['end_date'].initial = self.instance.end_date

    def clean(self):
        cleaned_data = super().clean()
        # Combine location fields into a single string
        location_parts = []
        if cleaned_data.get('hotel_name'):
            location_parts.append(cleaned_data['hotel_name'])
        if cleaned_data.get('address'):
            location_parts.append(cleaned_data['address'])
        if cleaned_data.get('city'):
            location_parts.append(cleaned_data['city'])
        if cleaned_data.get('state'):
            location_parts.append(cleaned_data['state'])
        if cleaned_data.get('country'):
            location_parts.append(cleaned_data['country'])
        
        # Store the combined location in cleaned_data
        cleaned_data['location'] = ', '.join(location_parts)
        return cleaned_data

    def save(self, commit=True):
        # Get the model instance from the form
        instance = super().save(commit=False)
        
        # Assign the combined location from cleaned_data to the instance's location field
        instance.location = self.cleaned_data['location']

        # Check if the instance is new or being updated
        is_new = instance.pk is None

        # Call the model instance's save method to ensure it has a PK if commit is True
        if commit:
            instance.save()

            # Get start and end dates from cleaned data
            start_date = self.cleaned_data.get('start_date')
            end_date = self.cleaned_data.get('end_date')

            if start_date and end_date and start_date <= end_date:
                # Get existing days
                existing_days = {day.date: day for day in instance.days.all()}
                
                # Create a set of all dates in the new range
                new_dates = set()
                current_date = start_date
                while current_date <= end_date:
                    new_dates.add(current_date)
                    current_date += timedelta(days=1)

                # Delete days that are outside the new date range
                for date, day in existing_days.items():
                    if date not in new_dates:
                        day.delete()

                # Create new days for dates that don't exist
                for date in new_dates:
                    if date not in existing_days:
                        ConventionDay.objects.create(convention=instance, date=date)

        return instance

class ConventionDayForm(forms.ModelForm):
    class Meta:
        model = ConventionDay
        fields = ['date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class PanelForm(forms.ModelForm):
    convention_day = forms.ModelChoiceField(
        queryset=ConventionDay.objects.none(), # Start with an empty queryset
        label="Day",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True # Assuming a day is required for a panel
    )
    room = forms.ModelChoiceField(
        queryset=Room.objects.none(), # Start with an empty queryset
        label="Room",
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        empty_label="Select a room..."
    )

    class Meta:
        model = Panel
        fields = ['title', 'description', 'convention_day', 'start_time', 'end_time', 'room', 'tags', 'host', 'is_featured', 'cancelled']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'convention_day': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'host': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'cancelled': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        convention = kwargs.pop('convention', None)
        super().__init__(*args, **kwargs)

        if convention:
            # Filter the queryset to only include days for the given convention
            self.fields['convention_day'].queryset = ConventionDay.objects.filter(convention=convention).order_by('date')
            # Filter rooms for the given convention
            self.fields['room'].queryset = Room.objects.filter(convention=convention).order_by('name')

            # Filter and order tags by priority for the current panel
            if self.instance.pk:
                # Set the queryset for available options, ordered by priority for existing panels
                self.fields['tags'].queryset = Tag.objects.filter(panels=self.instance).order_by('paneltag__priority')
                # Explicitly set the initial value for selected tags, ordered by priority
                self.fields['tags'].initial = self.instance.tags.all().order_by('paneltag__priority')
                
                # Set the queryset for hosts, ordered by priority
                self.fields['host'].queryset = PanelHost.objects.filter(panels=self.instance).order_by('panelhostorder__priority')
                # Explicitly set the initial value for selected hosts, ordered by priority
                self.fields['host'].initial = self.instance.host.all().order_by('panelhostorder__priority')
            else:
                # For new panels, order alphabetically
                self.fields['tags'].queryset = Tag.objects.all().order_by('name')
                self.fields['host'].queryset = PanelHost.objects.all().order_by('name')

        else:
            # If no convention is provided (e.g., in edit view directly via PK),
            # try to get the convention from the instance's convention_day
            if self.instance and self.instance.pk and self.instance.convention_day:
                convention = self.instance.convention_day.convention
                self.fields['convention_day'].queryset = ConventionDay.objects.filter(convention=convention).order_by('date')
                self.fields['room'].queryset = Room.objects.filter(convention=convention).order_by('name')
                # Explicitly set the initial value for selected tags, ordered by priority in this case too
                self.fields['tags'].initial = self.instance.tags.all().order_by('paneltag__priority')

    def save(self, commit=True):
        panel = super().save(commit=False)
        if commit:
            # Get the host order from the form data before saving
            host_order = self.data.getlist('host')
            print(f"Host order from form data: {host_order}")  # Debug log
            
            # Save the panel first
            panel.save()
            
            # Update host order before save_m2m
            for index, host_id in enumerate(host_order):
                print(f"Setting host {host_id} to priority {index}")  # Debug log
                PanelHostOrder.objects.update_or_create(
                    panel=panel,
                    host_id=host_id,
                    defaults={'priority': index}
                )
            
            # Remove any hosts that are no longer associated with the panel
            PanelHostOrder.objects.filter(panel=panel).exclude(host_id__in=host_order).delete()
            
            # Now save many-to-many relationships
            self.save_m2m()
            
            # Verify the order after saving
            final_order = list(PanelHostOrder.objects.filter(panel=panel).order_by('priority').values_list('host_id', flat=True))
            print(f"Final host order in database: {final_order}")  # Debug log
            
        return panel

class PanelHostForm(forms.ModelForm):
    class Meta:
        model = PanelHost
        fields = ['name', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control jscolor'}),
        }

class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label='CSV File',
        help_text='Upload a CSV file with panel information. Required columns: title, description, date, start_time, end_time, room, tags, hosts',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'})
    )
    convention = forms.ModelChoiceField(
        queryset=Convention.objects.all(),
        label='Convention',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

class XLSXImportForm(forms.Form):
    xlsx_file = forms.FileField(
        label='XLSX File',
        help_text='Upload an Excel file (.xlsx) with panel information. Required columns: title, description, date, start_time, end_time, room, tags, hosts',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )
    convention = forms.ModelChoiceField(
        queryset=Convention.objects.all(),
        label='Convention',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_xlsx_file(self):
        xlsx_file = self.cleaned_data['xlsx_file']
        if not (xlsx_file.name.endswith('.xlsx') or xlsx_file.name.endswith('.xls')):
            raise forms.ValidationError('File must be an Excel file (.xlsx or .xls)')
        return xlsx_file 