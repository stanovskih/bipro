from django.contrib import admin

from ads.models import DistrictInBuilding, FotosInOrder, Numbering, Order, WorkSystemInBuilding

# Register your models here.

class NumberingAdmin(admin.ModelAdmin):
    list_display = ('company', 'prefix', 'current_number', 'suffix', 'district')


class FotosInOrderInline(admin.TabularInline):
    extra = 1
    model = FotosInOrder
    classes = ['collapse']
    readonly_fields = ('admin_image','max_url')
    fields = ('name','foto','admin_image')


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id',)

    inlines = (FotosInOrderInline,)


class DistrictInBuildingAdmin(admin.ModelAdmin):
    list_display = ('company', 'district')

class WorkSystemInBuildingAdmin(admin.ModelAdmin):
    filter_horizontal = ('building',)
    list_display = ('company','get_buildings','get_worksystems','company_exec')
    readonly_fields = ('get_buildings','get_worksystems')
    list_filter = ('company', 'building', 'worksystem')



admin.site.register(Order, OrderAdmin)
admin.site.register(Numbering, NumberingAdmin)
admin.site.register(DistrictInBuilding, DistrictInBuildingAdmin)
admin.site.register(WorkSystemInBuilding, WorkSystemInBuildingAdmin)