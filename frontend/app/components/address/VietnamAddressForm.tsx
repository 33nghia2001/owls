/**
 * Vietnam Address Form Component
 * 
 * Updated for new administrative structure effective 01/07/2025:
 * - Vietnam now has 34 provinces/cities (down from 63 after mergers)
 * - Backend validates against 34 provinces with legacy mapping
 * 
 * Note: GHN API still uses old 63-province structure during transition.
 * This form uses GHN API for accurate shipping fee calculation while
 * displaying user-friendly province names.
 */
import { useState, useEffect, useCallback } from 'react';
import { useProvinces, useDistricts, useWards } from '~/lib/hooks/useLocation';

interface AddressFormData {
  full_name: string;
  phone: string;
  street_address: string;
  apartment?: string;
  province: string;
  province_id: number | null;
  district: string;
  district_id: number | null;
  ward: string;
  ward_code: string;
}

interface VietnamAddressFormProps {
  initialData?: Partial<AddressFormData>;
  onChange: (data: AddressFormData) => void;
  errors?: Partial<Record<keyof AddressFormData, string>>;
  disabled?: boolean;
}

export function VietnamAddressForm({
  initialData,
  onChange,
  errors = {},
  disabled = false,
}: VietnamAddressFormProps) {
  // Form state
  const [formData, setFormData] = useState<AddressFormData>({
    full_name: initialData?.full_name || '',
    phone: initialData?.phone || '',
    street_address: initialData?.street_address || '',
    apartment: initialData?.apartment || '',
    province: initialData?.province || '',
    province_id: initialData?.province_id ?? null,
    district: initialData?.district || '',
    district_id: initialData?.district_id ?? null,
    ward: initialData?.ward || '',
    ward_code: initialData?.ward_code || '',
  });

  // GHN API hooks
  const { data: provinces, isLoading: loadingProvinces } = useProvinces();
  const { data: districts, isLoading: loadingDistricts } = useDistricts(formData.province_id);
  const { data: wards, isLoading: loadingWards } = useWards(formData.district_id);

  // Memoized onChange callback
  const handleChange = useCallback((newData: AddressFormData) => {
    onChange(newData);
  }, [onChange]);

  // Update parent when form data changes
  useEffect(() => {
    handleChange(formData);
  }, [formData, handleChange]);

  // Handle province selection
  const handleProvinceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provinceId = Number(e.target.value) || null;
    const province = provinces?.find(p => p.ProvinceID === provinceId);
    
    setFormData(prev => ({
      ...prev,
      province: province?.ProvinceName || '',
      province_id: provinceId,
      // Reset district and ward when province changes
      district: '',
      district_id: null,
      ward: '',
      ward_code: '',
    }));
  };

  // Handle district selection
  const handleDistrictChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const districtId = Number(e.target.value) || null;
    const district = districts?.find(d => d.DistrictID === districtId);
    
    setFormData(prev => ({
      ...prev,
      district: district?.DistrictName || '',
      district_id: districtId,
      // Reset ward when district changes
      ward: '',
      ward_code: '',
    }));
  };

  // Handle ward selection
  const handleWardChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const wardCode = e.target.value;
    const ward = wards?.find(w => w.WardCode === wardCode);
    
    setFormData(prev => ({
      ...prev,
      ward: ward?.WardName || '',
      ward_code: wardCode,
    }));
  };

  // Handle text input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
  };

  return (
    <div className="space-y-4">
      {/* Full Name */}
      <div>
        <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Họ và tên <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="full_name"
          name="full_name"
          value={formData.full_name}
          onChange={handleInputChange}
          disabled={disabled}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.full_name ? 'border-red-500' : ''
          }`}
          placeholder="Nguyễn Văn A"
        />
        {errors.full_name && (
          <p className="mt-1 text-sm text-red-500">{errors.full_name}</p>
        )}
      </div>

      {/* Phone */}
      <div>
        <label htmlFor="phone" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Số điện thoại <span className="text-red-500">*</span>
        </label>
        <input
          type="tel"
          id="phone"
          name="phone"
          value={formData.phone}
          onChange={handleInputChange}
          disabled={disabled}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.phone ? 'border-red-500' : ''
          }`}
          placeholder="0901234567"
        />
        {errors.phone && (
          <p className="mt-1 text-sm text-red-500">{errors.phone}</p>
        )}
      </div>

      {/* Province */}
      <div>
        <label htmlFor="province" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Tỉnh/Thành phố <span className="text-red-500">*</span>
        </label>
        <select
          id="province"
          value={formData.province_id || ''}
          onChange={handleProvinceChange}
          disabled={disabled || loadingProvinces}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.province ? 'border-red-500' : ''
          }`}
        >
          <option value="">
            {loadingProvinces ? 'Đang tải...' : 'Chọn Tỉnh/Thành phố'}
          </option>
          {provinces?.map(province => (
            <option key={province.ProvinceID} value={province.ProvinceID}>
              {province.ProvinceName}
            </option>
          ))}
        </select>
        {errors.province && (
          <p className="mt-1 text-sm text-red-500">{errors.province}</p>
        )}
      </div>

      {/* District */}
      <div>
        <label htmlFor="district" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Quận/Huyện <span className="text-red-500">*</span>
        </label>
        <select
          id="district"
          value={formData.district_id || ''}
          onChange={handleDistrictChange}
          disabled={disabled || !formData.province_id || loadingDistricts}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.district ? 'border-red-500' : ''
          }`}
        >
          <option value="">
            {loadingDistricts ? 'Đang tải...' : formData.province_id ? 'Chọn Quận/Huyện' : 'Vui lòng chọn Tỉnh/TP trước'}
          </option>
          {districts?.map(district => (
            <option key={district.DistrictID} value={district.DistrictID}>
              {district.DistrictName}
            </option>
          ))}
        </select>
        {errors.district && (
          <p className="mt-1 text-sm text-red-500">{errors.district}</p>
        )}
      </div>

      {/* Ward */}
      <div>
        <label htmlFor="ward" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Phường/Xã <span className="text-red-500">*</span>
        </label>
        <select
          id="ward"
          value={formData.ward_code || ''}
          onChange={handleWardChange}
          disabled={disabled || !formData.district_id || loadingWards}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.ward ? 'border-red-500' : ''
          }`}
        >
          <option value="">
            {loadingWards ? 'Đang tải...' : formData.district_id ? 'Chọn Phường/Xã' : 'Vui lòng chọn Quận/Huyện trước'}
          </option>
          {wards?.map(ward => (
            <option key={ward.WardCode} value={ward.WardCode}>
              {ward.WardName}
            </option>
          ))}
        </select>
        {errors.ward && (
          <p className="mt-1 text-sm text-red-500">{errors.ward}</p>
        )}
      </div>

      {/* Street Address */}
      <div>
        <label htmlFor="street_address" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Địa chỉ (Số nhà, Đường) <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="street_address"
          name="street_address"
          value={formData.street_address}
          onChange={handleInputChange}
          disabled={disabled}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.street_address ? 'border-red-500' : ''
          }`}
          placeholder="123 Đường ABC"
        />
        {errors.street_address && (
          <p className="mt-1 text-sm text-red-500">{errors.street_address}</p>
        )}
      </div>

      {/* Apartment (Optional) */}
      <div>
        <label htmlFor="apartment" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Tòa nhà, Căn hộ (không bắt buộc)
        </label>
        <input
          type="text"
          id="apartment"
          name="apartment"
          value={formData.apartment}
          onChange={handleInputChange}
          disabled={disabled}
          className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm"
          placeholder="Tòa A, Căn 101"
        />
      </div>
    </div>
  );
}

export default VietnamAddressForm;
