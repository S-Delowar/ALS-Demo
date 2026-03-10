from rest_framework import serializers
from .models import Article, Course, Video, Book

class ArticleSerializer(serializers.ModelSerializer):
    # Explicitly add the dynamic property
    content_type = serializers.ReadOnlyField()

    class Meta:
        model = Article
        fields = '__all__'

class CourseSerializer(serializers.ModelSerializer):
    content_type = serializers.ReadOnlyField()

    class Meta:
        model = Course
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer):
    content_type = serializers.ReadOnlyField()

    class Meta:
        model = Video
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    content_type = serializers.ReadOnlyField()

    class Meta:
        model = Book
        fields = '__all__'
        

class ToggleSaveSerializer(serializers.Serializer):
    # Using ChoiceField automatically documents the exact allowed strings in Swagger!
    content_type = serializers.ChoiceField(choices=['article', 'book', 'course', 'video'])
    item_id = serializers.IntegerField()