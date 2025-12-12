/**
 * Vietnam Address Form Component
 * 
 * Updated for new administrative structure effective 01/07/2025:
 * - Vietnam now has 34 provinces/cities (down from 63 after mergers)
 * - Ward (Phường/Xã) is directly under Province in new structure
 * - District field is optional (kept for backward compatibility with GHN API)
 * 
 * Uses GHN API for location dropdowns (API may still use old district structure
 * during transition period).
 */
import { useState, useEffect } from 'react';
import { useProvinces, useWards } from '~/lib/hooks/useLocation';

// 34 provinces/cities after 01/07/2025 merger
const VIETNAM_PROVINCES_2025 = [
  // 6 Municipalities
  "Hà Nội",
  "Hồ Chí Minh",
  "Đà Nẵng",
  "Hải Phòng",
  "Cần Thơ",
  "Huế",
  // 28 Provinces
  "An Giang",
  "Bắc Ninh",
  "Cà Mau",
  "Cao Bằng",
  "Điện Biên",
  "Đắk Lắk",
  "Đồng Nai",
  "Đồng Tháp",
  "Gia Lai",
  "Hà Tĩnh",
  "Hưng Yên",
  "Khánh Hòa",
  "Lai Châu",
  "Lạng Sơn",
  "Lào Cai",
  "Lâm Đồng",
  "Nghệ An",
  "Ninh Bình",
  "Phú Thọ",
  "Quảng Ngãi",
  "Quảng Ninh",
  "Quảng Trị",
  "Sơn La",
  "Tây Ninh",
  "Thái Nguyên",
  "Thanh Hóa",
  "Tuyên Quang",
  "Vĩnh Long",
];

interface AddressFormData {
  full_name: string;
  phone: string;
  street_address: string;
  apartment?: string;
  province: string;
  province_id: number | null;
  ward: string;
  ward_code: string;
  // Legacy fields (optional)
  district?: string;
  district_id?: number | null;
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
    province_id: initialData?.province_id || null,
    ward: initialData?.ward || '',
    ward_code: initialData?.ward_code || '',
    district: initialData?.district || '',
    district_id: initialData?.district_id || null,
  });

  // GHN API hooks - during transition, GHN may still use old district structure
  const { data: ghnProvinces, isLoading: loadingProvinces } = useProvinces();
  const { data: wards, isLoading: loadingWards } = useWards(formData.district_id);

  // Update parent when form data changes
  useEffect(() => {
    onChange(formData);
  }, [formData, onChange]);

  // Handle province selection from static list
  const handleProvinceChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const provinceName = e.target.value;
    
    // Find matching GHN province ID if available
    const ghnProvince = ghnProvinces?.find(p => 
      p.ProvinceName.toLowerCase().includes(provinceName.toLowerCase()) ||
      provinceName.toLowerCase().includes(p.ProvinceName.toLowerCase())
    );
    
    setFormData(prev => ({
      ...prev,
      province: provinceName,
      province_id: ghnProvince?.ProvinceID || null,
      // Reset ward when province changes
      ward: '',
      ward_code: '',
      district: '',
      district_id: null,
    }));
  };

  // Handle ward input (free text since structure is changing)
  const handleWardChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      ward: e.target.value,
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

      {/* Province - Using static list of 34 provinces */}
      <div>
        <label htmlFor="province" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Tỉnh/Thành phố <span className="text-red-500">*</span>
          <span className="text-xs text-gray-500 ml-1">(34 tỉnh thành sau sáp nhập)</span>
        </label>
        <select
          id="province"
          value={formData.province}
          onChange={handleProvinceChange}
          disabled={disabled}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.province ? 'border-red-500' : ''
          }`}
        >
          <option value="">Chọn Tỉnh/Thành phố</option>
          {VIETNAM_PROVINCES_2025.map(province => (
            <option key={province} value={province}>
              {province}
            </option>
          ))}
        </select>
        {errors.province && (
          <p className="mt-1 text-sm text-red-500">{errors.province}</p>
        )}
      </div>

      {/* Ward - Free text input since structure is changing */}
      <div>
        <label htmlFor="ward" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Phường/Xã <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          id="ward"
          name="ward"
          value={formData.ward}
          onChange={handleWardChange}
          disabled={disabled || !formData.province}
          className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white sm:text-sm ${
            errors.ward ? 'border-red-500' : ''
          }`}
          placeholder={formData.province ? 'Nhập tên Phường/Xã' : 'Vui lòng chọn Tỉnh/TP trước'}
        />
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
