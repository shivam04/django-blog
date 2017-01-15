from django.contrib import admin
from .models import Comment
# Register your models here.
class CommentAdmin(admin.ModelAdmin):
	list_display = ["id","content_type","object_id","parent",'content_object','timestamp']
	class Meta:
		model = Comment
admin.site.register(Comment,CommentAdmin)
