#🚰 ⚡💧🔨🗑🛁🛠

from datetime import datetime,timedelta
from django import forms
from django.contrib import admin

from .models import Building, District, Location, Street, StreetInCompany, WorkSystem, Employee, Company, StandardDescription

from django.db import models
from django.contrib.admin import DateFieldListFilter
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from django.db.models import Q

from django.http import FileResponse, HttpResponse, StreamingHttpResponse

from django.utils.html import format_html

from django.utils.translation import gettext_lazy as _

from django.contrib import admin
from django.template.response import TemplateResponse
from django.urls import path

from django.utils.timezone import make_aware

from django.utils import timezone
from django.http import HttpResponseRedirect
from django.db import connection
import requests




from django.contrib import messages
from django.shortcuts import redirect


from django.forms.widgets import DateInput, SelectDateWidget, TextInput, DateTimeBaseInput, SplitDateTimeWidget


class LocationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', )


class StreetAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'name','legal_name','is_used')
    search_fields = ('id','name','legal_name')
    list_filter = ('is_used',)

class WorkSystemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_used')

class StreetInCompanyInline(admin.TabularInline):
    extra = 0
    model = StreetInCompany
    raw_id_fields = ('street',)
    show_change_link = True


class CompanyAdmin(admin.ModelAdmin):
    list_display = ('id','location','name','company_type','phone','email','is_used')
    search_fields = ('id','name','phone','email')
    list_filter = ('company_type','is_used',)
    inlines = (StreetInCompanyInline,)
    #form = CompanyAdminForm

#@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company')


class BuildingAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('company', 'name', 'channelid')
    list_filter = ('company','street')
    search_fields = ('name','company__name')
    
    
    raw_id_fields = ('company',)
    
    fieldsets = (
        ("Реквизиты объекта", {
            'fields': (
                        ('name','photo'),
                        ('street','house',),
                        ('company'),
                        ('lon','lat'),
                        ('flat_count','floor_count'),
                        ('channelid'),
                        ('square',),
                       )
        }),
        ('Дополнительно', {
            'classes': ('collapse',),
            'fields': (('description','comment',),),
        }),        
    )

    
    def save_model(self, request, obj, form, change):
        if obj.name is None:
            obj.name = f"{obj.street.name}, {obj.house}"
        super().save_model(request, obj, form, change)  

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('id','company', 'name', 'user', 'post', 'district_main', 'get_districts', 'get_worksystems','phone',)
    search_fields = ('name',)
    list_filter = ('deleted','district','worksystem')

    def get_districts(self, obj):
        return "; ".join([d.name for d in obj.district.all()])
    get_districts.short_description = 'Участки'

    def get_worksystems(self, obj):
        return "; ".join([ws.name for ws in obj.worksystem.all()])
    get_worksystems.short_description = 'Система'

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        if len(request.GET) == 0:
            get_param = "deleted__exact=0"
            return redirect("{url}?{get_parms}".format(url=request.path, get_parms=get_param))
        return super(EmployeeAdmin, self).changelist_view(request, extra_context=extra_context)

class StandardDescriptionAdmin(admin.ModelAdmin):
    list_display = ('name','worksystem', )
    search_fields = ('name',)
    list_filter = ('worksystem',)

#admin.site.unregister(User)
admin.site.register(Location, LocationAdmin)
admin.site.register(Street, StreetAdmin)
admin.site.register(WorkSystem, WorkSystemAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(District, DistrictAdmin)
admin.site.register(Building, BuildingAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(StandardDescription, StandardDescriptionAdmin)
