"""
Banner Views for Owls E-commerce Platform
==========================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.db.models import F
from django.shortcuts import get_object_or_404
from .models import Banner, PopupBanner, SliderSettings, BannerPosition
from .serializers import (
    BannerListSerializer, PopupBannerPublicSerializer, SliderSettingsSerializer
)


class HeroSliderView(APIView):
    """Get hero slider banners."""
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        banners = Banner.objects.filter(
            is_active=True,
            position=BannerPosition.HERO_SLIDER,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        ).order_by('order')

        serializer = BannerListSerializer(banners, many=True)

        # Get slider settings
        settings = SliderSettings.objects.filter(is_active=True, name='default').first()
        settings_data = SliderSettingsSerializer(settings).data if settings else {}

        return Response({
            'banners': serializer.data,
            'settings': settings_data
        })


class BannersByPositionView(APIView):
    """Get banners for a specific position."""
    permission_classes = [AllowAny]

    def get(self, request, position):
        # Validate position
        valid_positions = [p.value for p in BannerPosition]
        if position not in valid_positions:
            return Response(
                {'detail': f'Invalid position. Valid: {valid_positions}'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        banners = Banner.objects.filter(
            is_active=True,
            position=position,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        ).order_by('order')

        serializer = BannerListSerializer(banners, many=True)
        return Response(serializer.data)


class HomepageBannersView(APIView):
    """Get all homepage banners grouped by position."""
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        homepage_positions = [
            BannerPosition.HERO_SLIDER,
            BannerPosition.HOMEPAGE_TOP,
            BannerPosition.HOMEPAGE_MIDDLE,
            BannerPosition.HOMEPAGE_BOTTOM,
        ]

        result = {}
        for position in homepage_positions:
            banners = Banner.objects.filter(
                is_active=True,
                position=position,
                start_date__lte=now
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
            ).order_by('order')
            result[position] = BannerListSerializer(banners, many=True).data

        # Include slider settings
        settings = SliderSettings.objects.filter(is_active=True, name='default').first()
        result['slider_settings'] = SliderSettingsSerializer(settings).data if settings else {}

        return Response(result)


class ActivePopupsView(APIView):
    """Get active popups for current page."""
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        page_path = request.query_params.get('page', '/')

        popups = PopupBanner.objects.filter(
            is_active=True,
            start_date__lte=now
        ).filter(
            models.Q(end_date__isnull=True) | models.Q(end_date__gte=now)
        )

        # Filter by target pages if specified
        filtered_popups = []
        for popup in popups:
            if popup.target_pages:
                if page_path in popup.target_pages or any(
                    page_path.startswith(p) for p in popup.target_pages
                ):
                    filtered_popups.append(popup)
            else:
                filtered_popups.append(popup)

        # Exclude for logged in users if configured
        if request.user.is_authenticated:
            filtered_popups = [
                p for p in filtered_popups if not p.exclude_logged_in
            ]

        serializer = PopupBannerPublicSerializer(filtered_popups, many=True)
        return Response(serializer.data)


class TrackPopupImpressionView(APIView):
    """Track popup impression."""
    permission_classes = [AllowAny]

    def post(self, request):
        popup_id = request.data.get('popup_id')
        if not popup_id:
            return Response(
                {'detail': 'popup_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        PopupBanner.objects.filter(id=popup_id).update(
            impressions=F('impressions') + 1
        )
        return Response({'detail': 'Impression recorded'})


class TrackPopupClickView(APIView):
    """Track popup click."""
    permission_classes = [AllowAny]

    def post(self, request):
        popup_id = request.data.get('popup_id')
        if not popup_id:
            return Response(
                {'detail': 'popup_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        PopupBanner.objects.filter(id=popup_id).update(
            clicks=F('clicks') + 1
        )
        return Response({'detail': 'Click recorded'})


class TrackPopupConversionView(APIView):
    """Track popup conversion."""
    permission_classes = [AllowAny]

    def post(self, request):
        popup_id = request.data.get('popup_id')
        if not popup_id:
            return Response(
                {'detail': 'popup_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        PopupBanner.objects.filter(id=popup_id).update(
            conversions=F('conversions') + 1
        )
        return Response({'detail': 'Conversion recorded'})


# Need to import models for Q
from django.db import models
