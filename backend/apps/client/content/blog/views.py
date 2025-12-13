"""
Blog Views for Owls E-commerce Platform
========================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import F
from .models import BlogCategory, BlogTag, BlogPost, BlogComment
from .serializers import (
    BlogCategorySerializer, BlogTagSerializer,
    BlogPostListSerializer, BlogPostDetailSerializer,
    BlogCommentSerializer, CreateBlogCommentSerializer
)


class BlogCategoryListView(APIView):
    """List all blog categories."""
    permission_classes = [AllowAny]

    def get(self, request):
        categories = BlogCategory.objects.filter(
            is_active=True
        ).order_by('order', 'name')
        serializer = BlogCategorySerializer(categories, many=True)
        return Response(serializer.data)


class BlogTagListView(APIView):
    """List all blog tags."""
    permission_classes = [AllowAny]

    def get(self, request):
        tags = BlogTag.objects.all().order_by('name')
        serializer = BlogTagSerializer(tags, many=True)
        return Response(serializer.data)


class BlogPostListView(APIView):
    """List published blog posts with filtering."""
    permission_classes = [AllowAny]

    def get(self, request):
        posts = BlogPost.objects.filter(
            status='published'
        ).select_related('category', 'author').order_by('-published_at')

        # Filter by category
        category_slug = request.query_params.get('category')
        if category_slug:
            posts = posts.filter(category__slug=category_slug)

        # Filter by tag
        tag_slug = request.query_params.get('tag')
        if tag_slug:
            posts = posts.filter(tags__slug=tag_slug)

        # Filter featured
        featured = request.query_params.get('featured')
        if featured == 'true':
            posts = posts.filter(is_featured=True)

        # Pagination
        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 12))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = posts.count()
        posts = posts[start:end]

        serializer = BlogPostListSerializer(posts, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        })


class FeaturedPostsView(APIView):
    """List featured blog posts."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 5))
        posts = BlogPost.objects.filter(
            status='published',
            is_featured=True
        ).select_related('category', 'author').order_by('-published_at')[:limit]
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)


class RecentPostsView(APIView):
    """List recent blog posts."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 5))
        posts = BlogPost.objects.filter(
            status='published'
        ).select_related('category', 'author').order_by('-published_at')[:limit]
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)


class PopularPostsView(APIView):
    """List popular blog posts by view count."""
    permission_classes = [AllowAny]

    def get(self, request):
        limit = int(request.query_params.get('limit', 5))
        posts = BlogPost.objects.filter(
            status='published'
        ).select_related('category', 'author').order_by('-view_count')[:limit]
        serializer = BlogPostListSerializer(posts, many=True)
        return Response(serializer.data)


class RelatedPostsView(APIView):
    """Get related posts based on category and tags."""
    permission_classes = [AllowAny]

    def get(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status='published')
        limit = int(request.query_params.get('limit', 4))

        # Get posts from same category or with same tags
        related = BlogPost.objects.filter(
            status='published'
        ).exclude(id=post.id)

        if post.category:
            related = related.filter(category=post.category)

        related = related.select_related('category', 'author').order_by('-published_at')[:limit]
        serializer = BlogPostListSerializer(related, many=True)
        return Response(serializer.data)


class BlogPostDetailView(APIView):
    """Retrieve a single blog post and increment view count."""
    permission_classes = [AllowAny]

    def get(self, request, slug):
        post = get_object_or_404(
            BlogPost.objects.select_related('category', 'author').prefetch_related('tags'),
            slug=slug,
            status='published'
        )

        # Increment view count
        BlogPost.objects.filter(id=post.id).update(view_count=F('view_count') + 1)

        serializer = BlogPostDetailSerializer(post)
        return Response(serializer.data)


class BlogPostCommentsView(APIView):
    """List and create comments for a blog post."""
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status='published')
        comments = post.comments.filter(
            status='approved',
            parent__isnull=True
        ).select_related('user').prefetch_related('replies')
        serializer = BlogCommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, slug):
        post = get_object_or_404(BlogPost, slug=slug, status='published')

        if not post.allow_comments:
            return Response(
                {'detail': 'Comments are not allowed on this post.'},
                status=status.HTTP_403_FORBIDDEN
            )

        data = request.data.copy()
        data['post'] = post.id

        serializer = CreateBlogCommentSerializer(data=data)
        if serializer.is_valid():
            comment = serializer.save(
                user=request.user if request.user.is_authenticated else None,
                status='pending'  # Require approval
            )
            return Response(
                {'detail': 'Comment submitted for review.', 'id': str(comment.id)},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SearchBlogView(APIView):
    """Search blog posts."""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response({'results': [], 'count': 0})

        posts = BlogPost.objects.filter(
            status='published'
        ).filter(
            title__icontains=query
        ) | BlogPost.objects.filter(
            status='published'
        ).filter(
            content__icontains=query
        )

        posts = posts.distinct().select_related('category', 'author').order_by('-published_at')

        page = int(request.query_params.get('page', 1))
        per_page = int(request.query_params.get('per_page', 12))
        start = (page - 1) * per_page
        end = start + per_page

        total_count = posts.count()
        posts = posts[start:end]

        serializer = BlogPostListSerializer(posts, many=True)
        return Response({
            'results': serializer.data,
            'count': total_count,
            'query': query
        })
