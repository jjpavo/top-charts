from django.contrib import admin

from .models.Category import Category
from .models.Chart import Chart
from .models.Image import Image
from .models.Tag import Tag
from .models.User import User

admin.site.register(Category)
admin.site.register(Chart)
admin.site.register(Image)
admin.site.register(Tag)
admin.site.register(User)
