from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.db import transaction
from .models import Convention, ConventionDay, Panel, PanelHost, Tag, PanelHostOrder, PanelTag


class ConventionDayInline(admin.TabularInline):
    model = ConventionDay
    extra = 1


class PanelInline(admin.TabularInline):
    model = Panel
    extra = 1
    fields = ['title', 'description', 'start_time', 'end_time', 'room', 'cancelled']


class PanelHostOrderInline(admin.TabularInline):
    model = PanelHostOrder
    extra = 1
    ordering = ['priority']


class PanelTagInline(admin.TabularInline):
    model = PanelTag
    extra = 1
    ordering = ['priority']


class PanelHostOrderAdmin(admin.ModelAdmin):
    list_display = ('panel', 'host', 'priority')
    list_filter = ('panel', 'host')
    ordering = ('panel', 'priority')


class PanelTagAdmin(admin.ModelAdmin):
    list_display = ('panel', 'tag', 'priority')
    list_filter = ('panel', 'tag')
    ordering = ('panel', 'priority')


@admin.register(Convention)
class ConventionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('start_date', 'end_date')
    search_fields = ('name',)
    inlines = [ConventionDayInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if qs.exists():
            convention = qs.first()
            admin.site.site_header = f"{convention.name} Admin"
            admin.site.site_title = f"{convention.name} Admin Portal"
            admin.site.index_title = f"Welcome to {convention.name} Admin Portal"
        return qs

    def changelist_view(self, request, extra_context=None):
        convention = Convention.objects.first()
        if convention:
            return redirect(reverse('admin:events_convention_change', args=[convention.pk]))
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        return not Convention.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ConventionDay)
class ConventionDayAdmin(admin.ModelAdmin):
    list_display = ('convention', 'date')
    list_filter = ('convention', 'date')
    search_fields = ('convention__name',)
    inlines = [PanelInline]


@admin.register(Panel)
class PanelAdmin(admin.ModelAdmin):
    list_display = ('title', 'convention_day', 'start_time', 'end_time', 'room', 'is_featured', 'cancelled', 'get_hosts', 'get_tags')
    list_filter = ('convention_day__convention', 'convention_day__date', 'is_featured', 'cancelled')
    search_fields = ('title', 'description', 'room__name')
    inlines = [PanelHostOrderInline, PanelTagInline]
    actions = ['mark_featured', 'unmark_featured', 'cancel_panels', 'uncancel_panels']

    def get_hosts(self, obj):
        return ', '.join([h.name for h in obj.get_ordered_hosts()])
    get_hosts.short_description = 'Hosts'

    def get_tags(self, obj):
        return ', '.join([t.name for t in obj.ordered_tags if hasattr(obj, 'ordered_tags')]) if hasattr(obj, 'ordered_tags') else ', '.join([t.name for t in obj.tags.all()])
    get_tags.short_description = 'Tags'

    @admin.action(description='Mark selected panels as featured')
    def mark_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} panel(s) marked as featured.', messages.SUCCESS)

    @admin.action(description='Unmark selected panels as featured')
    def unmark_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} panel(s) unmarked as featured.', messages.SUCCESS)

    @admin.action(description='Cancel selected panels')
    def cancel_panels(self, request, queryset):
        count = queryset.update(cancelled=True)
        self.message_user(request, f'{count} panel(s) cancelled.', messages.SUCCESS)

    @admin.action(description='Uncancel selected panels')
    def uncancel_panels(self, request, queryset):
        count = queryset.update(cancelled=False)
        self.message_user(request, f'{count} panel(s) uncancelled.', messages.SUCCESS)

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if obj.start_time and obj.end_time and obj.start_time >= obj.end_time:
                raise ValueError('End time must be after start time.')
            super().save_model(request, obj, form, change)


@admin.register(PanelHost)
class PanelHostAdmin(admin.ModelAdmin):
    list_display = ('name', 'panels_count')
    search_fields = ('name',)

    def panels_count(self, obj):
        return obj.panels.count()
    panels_count.short_description = 'Panels'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'panel_count')
    search_fields = ('name',)

    def panel_count(self, obj):
        return obj.panels.count()
    panel_count.short_description = 'Panels'


@admin.register(PanelHostOrder)
class PanelHostOrderModelAdmin(PanelHostOrderAdmin):
    pass


@admin.register(PanelTag)
class PanelTagModelAdmin(PanelTagAdmin):
    pass
