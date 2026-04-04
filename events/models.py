from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import random

class Convention(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    location = models.CharField(max_length=200, blank=True, null=True)
    banner_image = models.TextField(blank=True, null=True)
    enable_schedule_pdf_export = models.BooleanField(default=False, help_text="Enable A3 PDF export of the full schedule")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        # Check if this is a new convention
        if not self.pk:
            # If there's already a convention, raise an error
            if Convention.objects.exists():
                raise ValidationError("Only one convention can exist at a time. Please edit the existing convention instead.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['start_date']

class ConventionDay(models.Model):
    convention = models.ForeignKey(Convention, on_delete=models.CASCADE, related_name='days')
    date = models.DateField()
    description = models.TextField(blank=True)

    def __str__(self):
        # Display format as Month Day, Year
        return self.date.strftime('%B %d, %Y')

    class Meta:
        ordering = ['date']
        unique_together = ['convention', 'date']

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(max_length=7, default='#007bff', help_text="Tag color in hex format (e.g., #007bff)")

    def __str__(self):
        return self.name

class PanelTag(models.Model):
    panel = models.ForeignKey('Panel', on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0, help_text="Priority of the tag (lower number = higher priority)")

    class Meta:
        ordering = ['priority']
        unique_together = ['panel', 'tag']

class PanelHostOrder(models.Model):
    panel = models.ForeignKey('Panel', on_delete=models.CASCADE)
    host = models.ForeignKey('PanelHost', on_delete=models.CASCADE)
    priority = models.IntegerField(default=0, help_text="Priority of the host (lower number = higher priority)")

    class Meta:
        ordering = ['priority']
        unique_together = ['panel', 'host']

class Panel(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    convention_day = models.ForeignKey(ConventionDay, on_delete=models.CASCADE, related_name='panels')
    start_time = models.TimeField()
    end_time = models.TimeField()
    room = models.ForeignKey('Room', on_delete=models.SET_NULL, null=True, blank=True, related_name='panels')
    tags = models.ManyToManyField(Tag, through=PanelTag, related_name='panels', blank=True)
    host = models.ManyToManyField('PanelHost', through=PanelHostOrder, related_name='panels', blank=True)
    cancelled = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, verbose_name="Featured Event")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.convention_day.date}"

    class Meta:
        ordering = ['start_time']

    def get_ordered_hosts(self):
        """Get hosts ordered by their priority in PanelHostOrder"""
        return self.host.all().order_by('panelhostorder__priority')

class PanelHost(models.Model):
    name = models.CharField(max_length=100)
    image = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def get_initials(self):
        """Generate initials from the host's name"""
        if not self.name:
            return "?"
        
        # Split the name and get first letter of each part
        name_parts = self.name.strip().split()
        if len(name_parts) == 1:
            # Single name, return first two letters
            return self.name[:2].upper()
        else:
            # Multiple names, return first letter of first and last name
            return (name_parts[0][0] + name_parts[-1][0]).upper()

    def get_avatar_color(self):
        """Generate a consistent color based on the host's name (stable across runs)"""
        import hashlib
        if not self.name:
            return "#6c757d"  # Default gray
        # Use md5 hash for stable, deterministic color selection
        name_bytes = self.name.lower().encode('utf-8')
        hash_digest = hashlib.md5(name_bytes).hexdigest()
        hash_int = int(hash_digest, 16)
        colors = [
            "#007bff", "#28a745", "#dc3545", "#ffc107", "#17a2b8",
            "#6f42c1", "#fd7e14", "#20c997", "#e83e8c", "#6c757d"
        ]
        return colors[hash_int % len(colors)]

    def get_initials_avatar(self):
        """Generate a data URL for an initials-based avatar"""
        try:
            # Create a 200x200 image
            size = 200
            img = Image.new('RGB', (size, size), self.get_avatar_color())
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fallback to default if not available
            try:
                # Try to use a larger font size
                font_size = size // 3
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                try:
                    # Fallback to system font
                    font = ImageFont.load_default()
                except:
                    # Last resort - use default
                    font = ImageFont.load_default()
            
            # Get initials
            initials = self.get_initials()
            
            # Calculate text position to center it
            bbox = draw.textbbox((0, 0), initials, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Draw the text in white
            draw.text((x, y), initials, fill="white", font=font)
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
        except Exception as e:
            # Fallback to a simple colored div approach
            return None

    class Meta:
        ordering = ['name']

class Room(models.Model):
    name = models.CharField(max_length=100)
    convention = models.ForeignKey(Convention, on_delete=models.CASCADE, related_name='rooms')

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['name', 'convention']
