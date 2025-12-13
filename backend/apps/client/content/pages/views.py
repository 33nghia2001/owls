"""
Pages Views for Owls E-commerce Platform
========================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from django.db.models import F
from collections import defaultdict
from .models import Page, FAQ, ContactMessage
from .serializers import (
    PageListSerializer, PageDetailSerializer,
    FAQSerializer, ContactMessageSerializer
)


class MenuPagesView(APIView):
    """List pages for navigation menu."""
    permission_classes = [AllowAny]

    def get(self, request):
        pages = Page.objects.filter(
            is_active=True,
            show_in_menu=True
        ).order_by('menu_order', 'title')
        serializer = PageListSerializer(pages, many=True)
        return Response(serializer.data)


class FooterPagesView(APIView):
    """List pages for footer."""
    permission_classes = [AllowAny]

    def get(self, request):
        pages = Page.objects.filter(
            is_active=True,
            show_in_footer=True
        ).order_by('menu_order', 'title')
        serializer = PageListSerializer(pages, many=True)
        return Response(serializer.data)


class PageDetailView(APIView):
    """Retrieve a single static page by slug."""
    permission_classes = [AllowAny]

    def get(self, request, slug):
        page = get_object_or_404(Page, slug=slug, is_active=True)
        serializer = PageDetailSerializer(page)
        return Response(serializer.data)


class FAQListView(APIView):
    """List all FAQs grouped by category."""
    permission_classes = [AllowAny]

    def get(self, request):
        faqs = FAQ.objects.filter(is_active=True).order_by('category', 'order')

        # Group by category
        grouped = defaultdict(list)
        for faq in faqs:
            grouped[faq.category].append(faq)

        result = []
        for category, items in grouped.items():
            result.append({
                'category': category,
                'faqs': FAQSerializer(items, many=True).data
            })

        return Response(result)


class FAQSearchView(APIView):
    """Search FAQs."""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query or len(query) < 2:
            return Response({'results': [], 'count': 0})

        faqs = FAQ.objects.filter(
            is_active=True
        ).filter(
            question__icontains=query
        ) | FAQ.objects.filter(
            is_active=True
        ).filter(
            answer__icontains=query
        )

        faqs = faqs.distinct().order_by('category', 'order')
        serializer = FAQSerializer(faqs, many=True)
        return Response({
            'results': serializer.data,
            'count': faqs.count(),
            'query': query
        })


class FAQHelpfulView(APIView):
    """Mark FAQ as helpful."""
    permission_classes = [AllowAny]

    def post(self, request, pk):
        faq = get_object_or_404(FAQ, pk=pk, is_active=True)
        FAQ.objects.filter(pk=pk).update(helpful_count=F('helpful_count') + 1)
        return Response({'detail': 'Thanks for your feedback!'})


class ContactFormView(APIView):
    """Submit contact form."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            contact = serializer.save()
            if request.user.is_authenticated:
                contact.user = request.user
                contact.save()
            return Response(
                {'detail': 'Your message has been submitted. We will respond soon.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AboutPageView(APIView):
    """Retrieve the About Us page."""
    permission_classes = [AllowAny]

    def get(self, request):
        page = Page.objects.filter(
            slug__in=['about', 'about-us', 've-chung-toi'],
            is_active=True
        ).first()
        if not page:
            return Response(
                {'detail': 'About page not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PageDetailSerializer(page)
        return Response(serializer.data)


class PrivacyPolicyView(APIView):
    """Retrieve the Privacy Policy page."""
    permission_classes = [AllowAny]

    def get(self, request):
        page = Page.objects.filter(
            slug__in=['privacy', 'privacy-policy', 'chinh-sach-bao-mat'],
            is_active=True
        ).first()
        if not page:
            return Response(
                {'detail': 'Privacy policy not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PageDetailSerializer(page)
        return Response(serializer.data)


class TermsOfServiceView(APIView):
    """Retrieve the Terms of Service page."""
    permission_classes = [AllowAny]

    def get(self, request):
        page = Page.objects.filter(
            slug__in=['terms', 'terms-of-service', 'dieu-khoan-dich-vu'],
            is_active=True
        ).first()
        if not page:
            return Response(
                {'detail': 'Terms of service not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = PageDetailSerializer(page)
        return Response(serializer.data)
