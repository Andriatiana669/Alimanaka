from django.contrib import admin
from django.utils.html import format_html
from .models import Event


class EventAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'event_type', 'start_date', 'user_link', 'is_system', 'colored_block'
    ]
    list_filter = ['event_type', 'is_system', 'is_blocked', 'start_date']
    search_fields = ['title', 'description', 'user__username']
    date_hierarchy = 'start_date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'event_type')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date', 'start_time', 'end_time', 'all_day')
        }),
        ('Apparence', {
            'fields': ('color', 'icon'),
            'classes': ('collapse',),
        }),
        ('Comportement', {
            'fields': ('is_blocked', 'is_system'),
        }),
        ('Utilisateur', {
            'fields': ('user', 'statut'),
            'classes': ('collapse',),
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description="Utilisateur")
    def user_link(self, obj):
        if obj.user:
            url = f"/alimanaka-admin/users/user/{obj.user.id}/change/"
            return format_html(
                '<a href="{}">{}</a>',
                url, obj.user.get_display_name()
            )
        return '-'
    
    @admin.display(description="Couleur")
    def colored_block(self, obj):
        return format_html(
            '<div style="width: 30px; height: 20px; background: {}; border-radius: 4px;"></div>',
            obj.color or '#cccccc'
        )


admin.site.register(Event, EventAdmin)