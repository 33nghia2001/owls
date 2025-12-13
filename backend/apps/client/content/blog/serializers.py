"""
Blog Serializers for Owls E-commerce Platform
=============================================
"""

from rest_framework import serializers
from .models import BlogCategory, BlogTag, BlogPost, BlogComment


class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories."""
    
    post_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'description', 'image', 'post_count']

    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()


class BlogTagSerializer(serializers.ModelSerializer):
    """Serializer for blog tags."""

    class Meta:
        model = BlogTag
        fields = ['id', 'name', 'slug']


class BlogPostListSerializer(serializers.ModelSerializer):
    """Compact serializer for blog post list."""
    
    author_name = serializers.SerializerMethodField()
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'category', 'category_name', 'author_name',
            'published_at', 'reading_time', 'view_count', 'is_featured'
        ]

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.email
        return 'Anonymous'


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for blog post."""
    
    author_name = serializers.SerializerMethodField()
    category = BlogCategorySerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content',
            'featured_image', 'featured_video',
            'category', 'tags', 'author_name',
            'published_at', 'reading_time', 'view_count',
            'is_featured', 'allow_comments', 'comment_count',
            'meta_title', 'meta_description'
        ]

    def get_author_name(self, obj):
        if obj.author:
            return obj.author.get_full_name() or obj.author.email
        return 'Anonymous'

    def get_comment_count(self, obj):
        return obj.comments.filter(status='approved').count()


class BlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for blog comments."""
    
    user_name = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = BlogComment
        fields = [
            'id', 'user_name', 'content', 'parent',
            'replies', 'created_at'
        ]

    def get_user_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.email.split('@')[0]
        return obj.name or 'Anonymous'

    def get_replies(self, obj):
        if obj.parent is None:
            replies = obj.replies.filter(status='approved')
            return BlogCommentSerializer(replies, many=True).data
        return []


class CreateBlogCommentSerializer(serializers.ModelSerializer):
    """Serializer for creating blog comments."""

    class Meta:
        model = BlogComment
        fields = ['post', 'content', 'parent', 'name', 'email']
        extra_kwargs = {
            'name': {'required': False},
            'email': {'required': False},
        }
