from django.contrib import admin
from .models import User,Menu,Order,Post,Author,Book,School,Location
# Register your models here.

admin.site.register(User)
admin.site.register(School)
admin.site.register(Location)
admin.site.register(Order)
admin.site.register(Menu)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(Post)