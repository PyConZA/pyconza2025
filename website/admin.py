from import_export.admin import ImportExportModelAdmin

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from wafer.users.admin import UserAdmin
from wafer.talks.admin import TalkAdmin 
from wafer.talks.models import Talk

class UserAdmin(UserAdmin, ImportExportModelAdmin):
    pass
admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), UserAdmin)


class TalkAdmin(TalkAdmin,ImportExportModelAdmin):
    pass

admin.site.unregister(Talk)
admin.site.register(Talk, TalkAdmin)


