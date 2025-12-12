/**
 * Vietnam Location API hooks for address forms.
 * Uses GHN API for accurate province/district/ward data.
 */
import { useQuery } from '@tanstack/react-query';
import { api } from '../api';

interface Province {
  ProvinceID: number;
  ProvinceName: string;
  Code: string;
}

interface District {
  DistrictID: number;
  DistrictName: string;
  ProvinceID: number;
  Code: string;
}

interface Ward {
  WardCode: string;
  WardName: string;
  DistrictID: number;
}

/**
 * Hook to fetch all Vietnam provinces from GHN API.
 */
export function useProvinces() {
  return useQuery({
    queryKey: ['ghn', 'provinces'],
    queryFn: async () => {
      const response = await api.get<{ provinces: Province[] }>('/api/v1/shipping/ghn/provinces/');
      return response.data.provinces;
    },
    staleTime: 1000 * 60 * 60 * 24, // Cache for 24 hours - provinces don't change
    gcTime: 1000 * 60 * 60 * 24 * 7, // Keep in cache for 7 days
  });
}

/**
 * Hook to fetch districts for a province.
 */
export function useDistricts(provinceId: number | null) {
  return useQuery({
    queryKey: ['ghn', 'districts', provinceId],
    queryFn: async () => {
      if (!provinceId) return [];
      const response = await api.get<{ districts: District[] }>(
        `/api/v1/shipping/ghn/districts/?province_id=${provinceId}`
      );
      return response.data.districts;
    },
    enabled: !!provinceId,
    staleTime: 1000 * 60 * 60 * 24, // Cache for 24 hours
  });
}

/**
 * Hook to fetch wards for a district.
 */
export function useWards(districtId: number | null) {
  return useQuery({
    queryKey: ['ghn', 'wards', districtId],
    queryFn: async () => {
      if (!districtId) return [];
      const response = await api.get<{ wards: Ward[] }>(
        `/api/v1/shipping/ghn/wards/?district_id=${districtId}`
      );
      return response.data.wards;
    },
    enabled: !!districtId,
    staleTime: 1000 * 60 * 60 * 24, // Cache for 24 hours
  });
}

/**
 * Hook to calculate shipping fee.
 */
interface ShippingQuote {
  provider: string;
  service_type: string;
  service_name: string;
  fee: number;
  insurance_fee: number;
  total_fee: number;
  estimated_days: number;
}

interface CalculateFeeParams {
  provider?: 'GHN' | 'GHTK';
  to_district_id: number;
  to_ward_code: string;
  weight?: number;
  insurance_value?: number;
  items?: Array<{ weight: number; quantity: number }>;
}

export function useShippingFee(params: CalculateFeeParams | null) {
  return useQuery({
    queryKey: ['shipping', 'fee', params],
    queryFn: async () => {
      if (!params?.to_district_id || !params?.to_ward_code) {
        return null;
      }
      const response = await api.post<{ quotes: ShippingQuote[]; weight: number }>(
        '/api/v1/shipping/calculate-fee/',
        params
      );
      return response.data;
    },
    enabled: !!params?.to_district_id && !!params?.to_ward_code,
    staleTime: 1000 * 60 * 5, // Cache for 5 minutes
  });
}
