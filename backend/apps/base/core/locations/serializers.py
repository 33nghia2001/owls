"""
Location Serializers for Owls E-commerce Platform
=================================================
"""

from rest_framework import serializers
from .models import Country, Region, City, District, Ward, Address, ShippingZone


class CountrySerializer(serializers.ModelSerializer):
    """Serializer for countries."""

    class Meta:
        model = Country
        fields = [
            'id', 'name', 'name_native', 'code', 'code_alpha3',
            'phone_code', 'currency_code', 'flag_emoji',
            'is_shipping_available'
        ]


class CountryListSerializer(serializers.ModelSerializer):
    """Compact serializer for country list."""

    class Meta:
        model = Country
        fields = ['id', 'name', 'code', 'flag_emoji', 'phone_code']


class RegionSerializer(serializers.ModelSerializer):
    """Serializer for regions."""

    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = Region
        fields = ['id', 'name', 'code', 'country', 'country_name']


class RegionListSerializer(serializers.ModelSerializer):
    """Compact serializer for region list."""

    class Meta:
        model = Region
        fields = ['id', 'name', 'code']


class CitySerializer(serializers.ModelSerializer):
    """Serializer for cities."""

    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = City
        fields = [
            'id', 'name', 'postal_code', 'region', 'region_name',
            'is_delivery_available', 'delivery_days'
        ]


class CityListSerializer(serializers.ModelSerializer):
    """Compact serializer for city list."""

    class Meta:
        model = City
        fields = ['id', 'name', 'postal_code']


class DistrictSerializer(serializers.ModelSerializer):
    """Serializer for districts."""

    class Meta:
        model = District
        fields = ['id', 'name', 'code', 'city']


class DistrictListSerializer(serializers.ModelSerializer):
    """Compact serializer for district list."""

    class Meta:
        model = District
        fields = ['id', 'name', 'code']


class WardSerializer(serializers.ModelSerializer):
    """Serializer for wards."""

    class Meta:
        model = Ward
        fields = ['id', 'name', 'code', 'district']


class WardListSerializer(serializers.ModelSerializer):
    """Compact serializer for ward list."""

    class Meta:
        model = Ward
        fields = ['id', 'name', 'code']


class AddressSerializer(serializers.ModelSerializer):
    """Serializer for addresses."""

    country_name = serializers.CharField(source='country.name', read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True)
    ward_name = serializers.CharField(source='ward.name', read_only=True)
    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Address
        fields = [
            'id', 'address_type', 'label',
            'full_name', 'phone', 'email',
            'country', 'country_name',
            'region', 'region_name',
            'city', 'city_name',
            'district', 'district_name',
            'ward', 'ward_name',
            'street_address', 'street_address_2', 'postal_code',
            'latitude', 'longitude',
            'is_default', 'delivery_instructions',
            'full_address', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AddressListSerializer(serializers.ModelSerializer):
    """Compact serializer for address list."""

    full_address = serializers.ReadOnlyField()

    class Meta:
        model = Address
        fields = [
            'id', 'label', 'full_name', 'phone',
            'full_address', 'is_default', 'address_type'
        ]


class CreateAddressSerializer(serializers.ModelSerializer):
    """Serializer for creating addresses."""

    class Meta:
        model = Address
        fields = [
            'address_type', 'label',
            'full_name', 'phone', 'email',
            'country', 'region', 'city', 'district', 'ward',
            'street_address', 'street_address_2', 'postal_code',
            'latitude', 'longitude',
            'is_default', 'delivery_instructions'
        ]


class ShippingZoneSerializer(serializers.ModelSerializer):
    """Serializer for shipping zones."""

    class Meta:
        model = ShippingZone
        fields = [
            'id', 'name', 'description',
            'base_rate', 'per_kg_rate', 'free_shipping_threshold',
            'min_delivery_days', 'max_delivery_days'
        ]
