from django.contrib import admin
from .models.lob_opt import LOB
from .models.bucket import Bucket
from .models.role import Role
from .models.userRole import UserRole
from .models.mev import Mev
from .models.MEV_var import MevVar
from .models.micro_pairs import MicroPair
from .models.other_input import OtherInput
from .models.hfc_status_validation import Hfc_Status_Validation
# Register your models here.


class AdminLOB(admin.ModelAdmin):
    list_display = ['id', 'options']
    ordering = ('id',)


class AdminBucket(admin.ModelAdmin):
    list_display = ('id', 'LD_limit', 'bucket', 'stage')
    ordering = ('id',)


class AdminMev(admin.ModelAdmin):
    list_display = ('Year', 'GDP', 'Inflation', 'Interest_rate','Domestic_credit_growth','Reporting_date','LOB')
    ordering = ('Reporting_date',)


class AdminMevVar(admin.ModelAdmin):
    list_display = ('Micro_Economic_variable', 'Best_case', 'Worst_case', 'Reporting_date','LOB')
    ordering = ('Reporting_date',)


class AdminOther(admin.ModelAdmin):
    list_display = ('variable', 'input','Reporting_date','LOB')
    ordering = ('Reporting_date',)


class AdminUserRole(admin.ModelAdmin):
    list_display = ('UserId', 'RoleId')
    # ordering = ('LOB',)


class AdminPair(admin.ModelAdmin):
    list_display = ('Pair', 'Variable_1', 'Variable_2', 'Reporting_date','LOB')
    ordering = ('LOB',)
# class AdminUserRole(admin.ModelAdmin):
#     list_display = ('Userid_id',)
#     #ordering = ('id',)


class AdminValidation(admin.ModelAdmin):
    list_display = ('id','LoB', 'Report_date','Flag')
    ordering = ('Report_date',)


admin.site.register(LOB, AdminLOB)
admin.site.register(Bucket, AdminBucket)
# admin.site.register(Role)
admin.site.register(UserRole, AdminUserRole)
admin.site.register(Mev,AdminMev)
admin.site.register(MevVar,AdminMevVar)
admin.site.register(MicroPair, AdminPair)
admin.site.register(OtherInput,AdminOther)
admin.site.register(Hfc_Status_Validation, AdminValidation)

