from django.contrib import admin
from forum_app.models import Question, Answer, Like

# Register your models here.
# admin.site.register(Question),
# admin.site.register(Answer),
# admin.site.register(Like),


@admin.register(Question)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'author', 'created_at', 'category')
    list_filter = ["category"]


@admin.register(Answer)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'author', 'question_title', 'created_at')
    
    def question_title(self, obj):
        return obj.question.title
    question_title.short_description = 'Question'


@admin.register(Like)
class BoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'question_title', 'created_at')
    
    def question_title(self, obj):
        return obj.question.title
    question_title.short_description = 'Question'
