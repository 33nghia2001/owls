"""
Location Views for Owls E-commerce Platform
============================================
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Country, Region, City, District, Ward, Address, ShippingZone
from .serializers import (
    CountrySerializer, CountryListSerializer,
    RegionSerializer, RegionListSerializer,
    CitySerializer, CityListSerializer,
    DistrictSerializer, DistrictListSerializer,
    WardSerializer, WardListSerializer,
    AddressSerializer, AddressListSerializer, CreateAddressSerializer,
    ShippingZoneSerializer
)


# ===== Country Views =====

class CountryListView(APIView):
    """List all active countries."""
    permission_classes = [AllowAny]

    def get(self, request):
        shipping_only = request.query_params.get('shipping_only', 'false').lower() == 'true'

        countries = Country.objects.filter(is_active=True)
        if shipping_only:
            countries = countries.filter(is_shipping_available=True)

        countries = countries.order_by('order', 'name')
        serializer = CountryListSerializer(countries, many=True)
        return Response(serializer.data)


class CountryDetailView(APIView):
    """Get country details."""
    permission_classes = [AllowAny]

    def get(self, request, code):
        country = get_object_or_404(Country, code=code.upper(), is_active=True)
        serializer = CountrySerializer(country)
        return Response(serializer.data)


# ===== Region Views =====

class RegionListView(APIView):
    """List regions for a country."""
    permission_classes = [AllowAny]

    def get(self, request, country_code):
        country = get_object_or_404(Country, code=country_code.upper(), is_active=True)
        regions = Region.objects.filter(country=country, is_active=True).order_by('name')
        serializer = RegionListSerializer(regions, many=True)
        return Response(serializer.data)


# ===== City Views =====

class CityListView(APIView):
    """List cities for a region."""
    permission_classes = [AllowAny]

    def get(self, request, region_id):
        region = get_object_or_404(Region, id=region_id, is_active=True)
        cities = City.objects.filter(region=region, is_active=True).order_by('name')
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)


class CitySearchView(APIView):
    """Search cities by name."""
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        country_code = request.query_params.get('country')

        if len(query) < 2:
            return Response([])

        cities = City.objects.filter(
            is_active=True,
            name__icontains=query
        )

        if country_code:
            cities = cities.filter(region__country__code=country_code.upper())

        cities = cities.select_related('region', 'region__country').order_by('name')[:20]
        serializer = CitySerializer(cities, many=True)
        return Response(serializer.data)


# ===== District Views =====

class DistrictListView(APIView):
    """List districts for a city."""
    permission_classes = [AllowAny]

    def get(self, request, city_id):
        city = get_object_or_404(City, id=city_id, is_active=True)
        districts = District.objects.filter(city=city, is_active=True).order_by('name')
        serializer = DistrictListSerializer(districts, many=True)
        return Response(serializer.data)


# ===== Ward Views =====

class WardListView(APIView):
    """List wards for a district."""
    permission_classes = [AllowAny]

    def get(self, request, district_id):
        district = get_object_or_404(District, id=district_id, is_active=True)
        wards = Ward.objects.filter(district=district, is_active=True).order_by('name')
        serializer = WardListSerializer(wards, many=True)
        return Response(serializer.data)


# ===== Address Views =====

class MyAddressesView(APIView):
    """List and create user addresses."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = Address.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('country', 'region', 'city', 'district', 'ward')
        serializer = AddressListSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CreateAddressSerializer(data=request.data)
        if serializer.is_valid():
            address = serializer.save(user=request.user)
            return Response(
                AddressSerializer(address).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    """Retrieve, update, or delete a specific address."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return get_object_or_404(Address, pk=pk, user=user, is_active=True)

    def get(self, request, pk):
        address = self.get_object(pk, request.user)
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def put(self, request, pk):
        address = self.get_object(pk, request.user)
        serializer = CreateAddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            address = serializer.save()
            return Response(AddressSerializer(address).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        address.is_active = False
        address.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SetDefaultAddressView(APIView):
    """Set an address as default."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        address = get_object_or_404(Address, pk=pk, user=request.user, is_active=True)
        address.is_default = True
        address.save()  # save() handles unsetting other defaults
        return Response({'detail': 'Address set as default.'})


class DefaultAddressView(APIView):
    """Get user's default address."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        address_type = request.query_params.get('type', 'shipping')

        address = Address.objects.filter(
            user=request.user,
            is_active=True,
            is_default=True,
            address_type__in=[address_type, 'both']
        ).select_related('country', 'region', 'city', 'district', 'ward').first()

        if not address:
            return Response({'detail': 'No default address found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AddressSerializer(address)
        return Response(serializer.data)


# ===== Shipping Zone Views =====

class ShippingZoneCheckView(APIView):
    """Check shipping zone and rates for an address."""
    permission_classes = [AllowAny]

    def get(self, request):
        country_id = request.query_params.get('country')
        region_id = request.query_params.get('region')

        if not country_id:
            return Response(
                {'detail': 'country parameter is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Find applicable shipping zone
        zone = None

        if region_id:
            zone = ShippingZone.objects.filter(
                is_active=True,
                regions__id=region_id
            ).first()

        if not zone:
            zone = ShippingZone.objects.filter(
                is_active=True,
                countries__id=country_id
            ).first()

        if not zone:
            return Response({
                'available': False,
                'detail': 'Shipping not available to this location.'
            })

        serializer = ShippingZoneSerializer(zone)
        return Response({
            'available': True,
            'zone': serializer.data
        })
