from django.contrib import admin
from hrms.registration.models import *



class CategoryAdmin(admin.ModelAdmin):
    list_display = ('industry_type',)
    
    
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name','email','category','business_year_start',\
                    'business_year_end')
    search_field = ('name',)
    list_filter = ('name',)
    list_per_page = 50
    date_hierarchy = 'business_year_start'

class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name','employee')
    
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user','key')
    
    
class LeaveAdmin(admin.ModelAdmin):
    list_display = ('type_of_leave',)
    
class RestrictedDayAdmin(admin.ModelAdmin):
    list_display = ('title','restriction_day_date')
    
    
admin.site.register(Category,CategoryAdmin)
admin.site.register(Country,CountryAdmin)
admin.site.register(Company,CompanyAdmin)
admin.site.register(Supervisor,SupervisorAdmin)
admin.site.register(Department,DepartmentAdmin)
admin.site.register(UserProfile,UserProfileAdmin)
admin.site.register(Leave,LeaveAdmin)
admin.site.register(RestrictedDay,RestrictedDayAdmin)