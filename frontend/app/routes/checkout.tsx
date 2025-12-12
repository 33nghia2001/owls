import { useNavigate } from "react-router";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { 
  MapPin, Phone, User, CreditCard, Truck, Package, 
  AlertCircle, CheckCircle, ChevronRight, Tag, Loader2,
  RefreshCw, AlertTriangle, X, Mail
} from "lucide-react";
import { useAuthStore } from "~/lib/stores";
import { useCart, useApplyCoupon } from "~/lib/query";
import { ordersApi, paymentsApi } from "~/lib/services";
import { checkoutSchema, type CheckoutFormData } from "~/lib/validations";
import { formatCurrency, cn, parsePrice } from "~/lib/utils";
import { Button } from "~/components/ui";
import { getErrorMessage } from "~/lib/types/api-errors";
import { getGuestCartId } from "~/lib/api";
import { getConfig } from "~/lib/config";
import type { CartItem } from "~/lib/types";
import toast from "react-hot-toast";
import { useQueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";

export function meta() {
  return [
    { title: "Thanh toán - OWLS Marketplace" },
    { name: "description", content: "Hoàn tất đơn hàng của bạn" },
  ];
}

const paymentMethods = [
  { 
    id: "cod", 
    name: "Thanh toán khi nhận hàng (COD)", 
    icon: Truck,
    description: "Thanh toán bằng tiền mặt khi nhận hàng"
  },
  { 
    id: "vnpay", 
    name: "VNPay", 
    icon: CreditCard,
    description: "Thanh toán qua ví VNPay, ATM, Visa/Mastercard"
  },
  { 
    id: "stripe", 
    name: "Stripe (Quốc tế)", 
    icon: CreditCard,
    description: "Visa, Mastercard, và các thẻ quốc tế"
  },
] as const;

interface PriceChange {
  product: string;
  old_price: string;
  new_price: string;
}

export default function CheckoutPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  
  const { data: cart, isLoading: isCartLoading, refetch: refetchCart } = useCart();
  const applyCouponMutation = useApplyCoupon();
  
  const { user } = useAuthStore();
  const [serverError, setServerError] = useState<string | null>(null);
  const [couponDiscount, setCouponDiscount] = useState<number>(0);
  const [appliedCoupon, setAppliedCoupon] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [priceChanges, setPriceChanges] = useState<PriceChange[] | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  
  // Fetch system config for shipping thresholds
  const [freeShippingThreshold, setFreeShippingThreshold] = useState<number>(500000);
  const [defaultShippingCost, setDefaultShippingCost] = useState<number>(30000);
  
  useEffect(() => {
    getConfig().then(config => {
      setFreeShippingThreshold(config.shipping.free_shipping_threshold);
      setDefaultShippingCost(config.shipping.default_shipping_cost);
    }).catch(() => {
      // Use defaults if config fetch fails
      console.warn('Failed to fetch config, using defaults');
    });
  }, []);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<CheckoutFormData>({
    resolver: zodResolver(checkoutSchema),
    defaultValues: {
      full_name: user?.full_name || "",
      phone: user?.phone || "",
      address: "",
      city: "",
      // district removed
      ward: "",
      note: "",
      payment_method: "cod",
      coupon_code: "",
      email: user?.email || "",
      isLoggedIn: !!user,
    },
  });

  const selectedPayment = watch("payment_method");

  // Pre-fill user data and update isLoggedIn status
  useEffect(() => {
    setValue("isLoggedIn", !!user);
    if (user) {
      if (user.full_name) setValue("full_name", user.full_name);
      if (user.phone) setValue("phone", user.phone);
      if (user.email) setValue("email", user.email);
    }
  }, [user, setValue]);

  // Handle apply coupon
  const handleApplyCoupon = async () => {
    const couponCode = watch("coupon_code");
    if (!couponCode?.trim()) {
      toast.error("Vui lòng nhập mã giảm giá");
      return;
    }
    
    try {
      const result = await applyCouponMutation.mutateAsync(couponCode.trim());
      if (result.discount_amount) {
        setCouponDiscount(parsePrice(result.discount_amount));
        setAppliedCoupon(couponCode.trim());
        toast.success(`Áp dụng mã giảm giá thành công! Giảm ${formatCurrency(parsePrice(result.discount_amount))}`);
      }
    } catch (error) {
      const message = getErrorMessage(error);
      toast.error(message || "Mã giảm giá không hợp lệ");
      setCouponDiscount(0);
      setAppliedCoupon(null);
    }
  };

  // Handle refresh cart after price changes
  const handleRefreshCart = async () => {
    setIsRefreshing(true);
    try {
      await refetchCart();
      // Invalidate cart query to get fresh data
      await queryClient.invalidateQueries({ queryKey: ["cart"] });
      setPriceChanges(null);
      toast.success("Giỏ hàng đã được cập nhật với giá mới");
    } catch (error) {
      toast.error("Không thể cập nhật giỏ hàng. Vui lòng thử lại.");
    } finally {
      setIsRefreshing(false);
    }
  };

  const onSubmit = async (data: CheckoutFormData) => {
    setServerError(null);
    setPriceChanges(null);
    setIsProcessing(true);

    try {
      // Get guest cart ID for guest checkout
      const guestCartId = !user ? getGuestCartId() : null;
      
      // Step 1: Create order with shipping address (New Mapping)
      const orderData = {
        shipping_name: data.full_name,
        shipping_phone: data.phone,
        
        // Mapping mới cho địa chỉ
        shipping_address: data.address, // Số nhà, tên đường
        shipping_province: data.city,   // Tỉnh / Thành phố
        shipping_ward: data.ward || "", // Phường / Xã
        shipping_country: "Vietnam",
        shipping_postal_code: "",       // Để trống hoặc xử lý nếu cần
        
        customer_note: data.note || "",
        coupon_code: data.coupon_code || undefined,
        payment_method: data.payment_method,
        
        // Guest checkout fields
        guest_cart_id: guestCartId || undefined,
        guest_email: !user ? data.email : undefined,
      };

      const orderResponse = await ordersApi.createOrder(orderData);
      const orderId = orderResponse.id;

      // Step 2: Handle payment based on selected method
      if (data.payment_method === "cod") {
        toast.success("Đặt hàng thành công!");
        navigate(`/checkout/success?order_id=${orderId}`);
      } else {
        const paymentResponse = await paymentsApi.createPayment({
          order_id: orderId,
          method: data.payment_method,
        });

        // Validate payment redirect URL before navigating
        const allowedDomains = [
          "sandbox.vnpayment.vn",
          "vnpayment.vn",
          "checkout.stripe.com",
          "stripe.com",
        ];
        
        const validatePaymentUrl = (url: string): boolean => {
          try {
            const parsedUrl = new URL(url);
            return allowedDomains.some(domain => parsedUrl.hostname.endsWith(domain));
          } catch {
            return false;
          }
        };

        if (paymentResponse.payment_url && validatePaymentUrl(paymentResponse.payment_url)) {
          window.location.href = paymentResponse.payment_url;
        } else if (paymentResponse.checkout_url && validatePaymentUrl(paymentResponse.checkout_url)) {
          window.location.href = paymentResponse.checkout_url;
        } else {
          toast.success("Đặt hàng thành công!");
          navigate(`/checkout/success?order_id=${orderId}`);
        }
      }
    } catch (error: unknown) {
      // Handle 409 Conflict - Price changed
      if (isAxiosError(error) && error.response?.status === 409) {
        const responseData = error.response.data;
        if (responseData?.price_changes) {
          setPriceChanges(responseData.price_changes);
          toast.error("Giá sản phẩm đã thay đổi. Vui lòng xem lại giỏ hàng.");
          return;
        }
      }
      
      const message = getErrorMessage(error);
      setServerError(message);
      toast.error(message);
    } finally {
      setIsProcessing(false);
    }
  };

  const inputClasses = (hasError: boolean) =>
    cn(
      "h-11 w-full rounded-lg border px-3 text-sm transition-colors",
      "focus:border-orange-500 focus:ring-2 focus:ring-orange-500/20 focus:outline-none",
      "dark:bg-gray-900 dark:text-gray-100",
      hasError
        ? "border-red-500 dark:border-red-500"
        : "border-gray-200 dark:border-gray-800"
    );

  // Loading state
  if (isCartLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50/50 dark:bg-[#050505]">
        <Loader2 className="h-8 w-8 animate-spin text-orange-500" />
      </div>
    );
  }

  // Empty cart check
  if (!cart || cart.items.length === 0) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center px-4 py-12 text-center">
        <Package className="h-16 w-16 text-gray-300 dark:text-gray-700 mb-4" />
        <h2 className="text-xl font-bold text-gray-900 dark:text-gray-100 mb-2">
          Giỏ hàng trống
        </h2>
        <p className="text-gray-600 dark:text-gray-400 mb-6">
          Vui lòng thêm sản phẩm vào giỏ hàng trước khi thanh toán
        </p>
        <Button onClick={() => navigate("/products")}>
          Tiếp tục mua sắm
        </Button>
      </div>
    );
  }

  const subtotal = parsePrice(cart.subtotal);
  
  // Shipping cost calculation (synced from backend via API)
  const shippingCost = subtotal >= freeShippingThreshold ? 0 : defaultShippingCost;
  // Include coupon discount in total calculation
  const total = subtotal + shippingCost - couponDiscount;

  return (
    <div className="min-h-screen bg-gray-50/50 dark:bg-[#050505] py-8">
      {/* Price Change Modal */}
      {priceChanges && priceChanges.length > 0 && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl dark:bg-gray-900">
            <div className="flex items-start gap-3">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-yellow-100 dark:bg-yellow-900/30">
                <AlertTriangle className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                  Giá sản phẩm đã thay đổi
                </h3>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  Một số sản phẩm trong giỏ hàng đã được cập nhật giá. Vui lòng xem lại trước khi tiếp tục.
                </p>
              </div>
              <button
                onClick={() => setPriceChanges(null)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="mt-4 max-h-60 space-y-3 overflow-y-auto">
              {priceChanges.map((change, index) => (
                <div
                  key={index}
                  className="rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-gray-700 dark:bg-gray-800"
                >
                  <p className="font-medium text-gray-900 dark:text-gray-100">
                    {change.product}
                  </p>
                  <div className="mt-1 flex items-center gap-2 text-sm">
                    <span className="text-gray-500 line-through">
                      {formatCurrency(parsePrice(change.old_price))}
                    </span>
                    <ChevronRight className="h-3 w-3 text-gray-400" />
                    <span className="font-semibold text-orange-500">
                      {formatCurrency(parsePrice(change.new_price))}
                    </span>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 flex gap-3">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => navigate("/cart")}
              >
                Xem giỏ hàng
              </Button>
              <Button
                className="flex-1"
                onClick={handleRefreshCart}
                disabled={isRefreshing}
              >
                {isRefreshing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Đang cập nhật...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Cập nhật giá
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}

      <div className="container mx-auto px-4">
        {/* Progress Steps */}
        <div className="mb-8 flex items-center justify-center gap-2 text-sm">
          <span className="flex items-center gap-1 text-gray-400">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Giỏ hàng
          </span>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <span className="flex items-center gap-1 font-medium text-orange-500">
            <div className="flex h-5 w-5 items-center justify-center rounded-full bg-orange-500 text-xs text-white">
              2
            </div>
            Thanh toán
          </span>
          <ChevronRight className="h-4 w-4 text-gray-400" />
          <span className="text-gray-400">Hoàn tất</span>
        </div>

        <h1 className="mb-6 text-3xl font-bold text-gray-900 dark:text-gray-100">
          Thanh toán
        </h1>

        {/* Server Error */}
        {serverError && (
          <div className="mb-6 flex items-center gap-2 rounded-lg bg-red-50 p-4 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
            <AlertCircle className="h-5 w-5 shrink-0" />
            <span>{serverError}</span>
          </div>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid gap-6 lg:grid-cols-[1fr,400px]">
            {/* Left Column - Form */}
            <div className="space-y-6">
              {/* Shipping Address */}
              <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
                  <MapPin className="h-5 w-5 text-orange-500" />
                  Địa chỉ giao hàng
                </h2>

                <div className="grid gap-4 md:grid-cols-2">
                  {/* Full Name */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Họ tên người nhận <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        {...register("full_name")}
                        placeholder="Nguyễn Văn A"
                        className={cn(inputClasses(!!errors.full_name), "pl-10")}
                      />
                    </div>
                    {errors.full_name && (
                      <p className="mt-1 text-xs text-red-500">{errors.full_name.message}</p>
                    )}
                  </div>

                  {/* Email (for guest checkout) */}
                  {!user && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Email <span className="text-red-500">*</span>
                      </label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                        <input
                          {...register("email")}
                          type="email"
                          placeholder="email@example.com"
                          className={cn(inputClasses(!!errors.email), "pl-10")}
                        />
                      </div>
                      {errors.email && (
                        <p className="mt-1 text-xs text-red-500">{errors.email.message}</p>
                      )}
                    </div>
                  )}

                  {/* Phone */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Số điện thoại <span className="text-red-500">*</span>
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-gray-400" />
                      <input
                        {...register("phone")}
                        placeholder="0901234567"
                        inputMode="numeric"
                        className={cn(inputClasses(!!errors.phone), "pl-10")}
                      />
                    </div>
                    {errors.phone && (
                      <p className="mt-1 text-xs text-red-500">{errors.phone.message}</p>
                    )}
                  </div>

                  {/* City (Province) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Tỉnh/Thành phố <span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register("city")}
                      placeholder="Hồ Chí Minh"
                      className={inputClasses(!!errors.city)}
                    />
                    {errors.city && (
                      <p className="mt-1 text-xs text-red-500">{errors.city.message}</p>
                    )}
                  </div>

                  {/* Ward (New Field) */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Phường/Xã <span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register("ward")}
                      placeholder="Phường Bến Nghé"
                      className={inputClasses(!!errors.ward)}
                    />
                    {errors.ward && (
                      <p className="mt-1 text-xs text-red-500">{errors.ward.message}</p>
                    )}
                  </div>

                  {/* Address */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Địa chỉ chi tiết <span className="text-red-500">*</span>
                    </label>
                    <input
                      {...register("address")}
                      placeholder="Số nhà, tên đường..."
                      className={inputClasses(!!errors.address)}
                    />
                    {errors.address && (
                      <p className="mt-1 text-xs text-red-500">{errors.address.message}</p>
                    )}
                  </div>

                  {/* Note */}
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Ghi chú
                    </label>
                    <textarea
                      {...register("note")}
                      placeholder="Ghi chú cho người giao hàng (nếu có)"
                      rows={3}
                      className={cn(
                        inputClasses(!!errors.note), 
                        "h-auto py-3 resize-none"
                      )}
                    />
                  </div>
                </div>
              </div>

              {/* Payment Method */}
              <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100 mb-6">
                  <CreditCard className="h-5 w-5 text-orange-500" />
                  Phương thức thanh toán
                </h2>

                <div className="space-y-3">
                  {paymentMethods.map((method) => (
                    <label
                      key={method.id}
                      className={cn(
                        "flex items-start gap-4 rounded-xl border p-4 cursor-pointer transition-all",
                        selectedPayment === method.id
                          ? "border-orange-500 bg-orange-50 dark:bg-orange-900/10"
                          : "border-gray-200 hover:border-gray-300 dark:border-gray-800 dark:hover:border-gray-700"
                      )}
                    >
                      <input
                        {...register("payment_method")}
                        type="radio"
                        value={method.id}
                        className="mt-1 h-4 w-4 text-orange-500 focus:ring-orange-500"
                      />
                      <div className="flex-1">
                        <div className="flex items-center gap-2">
                          <method.icon className={cn(
                            "h-5 w-5",
                            selectedPayment === method.id ? "text-orange-500" : "text-gray-400"
                          )} />
                          <span className="font-medium text-gray-900 dark:text-gray-100">
                            {method.name}
                          </span>
                        </div>
                        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                          {method.description}
                        </p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column - Order Summary */}
            <div className="lg:sticky lg:top-24 h-fit space-y-6">
              {/* Order Items */}
              <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-800 dark:bg-gray-900">
                <h2 className="flex items-center gap-2 text-lg font-semibold text-gray-900 dark:text-gray-100 mb-4">
                  <Package className="h-5 w-5 text-orange-500" />
                  Đơn hàng ({cart.items.length} sản phẩm)
                </h2>

                <div className="max-h-[300px] overflow-y-auto space-y-4 pr-2">
                  {cart.items.map((item: CartItem) => (
                    <div key={item.id} className="flex gap-3">
                      <div className="h-16 w-16 shrink-0 overflow-hidden rounded-lg border border-gray-100 dark:border-gray-800">
                        {item.product.primary_image ? (
                          <img
                            src={item.product.primary_image.image}
                            alt={item.product.name}
                            className="h-full w-full object-cover"
                          />
                        ) : (
                          <div className="flex h-full w-full items-center justify-center bg-gray-100 dark:bg-gray-800">
                            <Package className="h-6 w-6 text-gray-400" />
                          </div>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 dark:text-gray-100 truncate">
                          {item.product.name}
                        </p>
                        <p className="text-sm text-gray-500">x{item.quantity}</p>
                      </div>
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 whitespace-nowrap">
                        {formatCurrency(parsePrice(item.total_price))}
                      </p>
                    </div>
                  ))}
                </div>

                {/* Coupon Code */}
                <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Tag className="h-4 w-4" />
                    Mã giảm giá
                  </label>
                  <div className="flex gap-2">
                    <input
                      {...register("coupon_code")}
                      placeholder="Nhập mã giảm giá"
                      className={cn(inputClasses(false), "flex-1")}
                      disabled={!!appliedCoupon}
                    />
                    <Button 
                      type="button" 
                      variant="outline" 
                      size="sm"
                      onClick={handleApplyCoupon}
                      disabled={applyCouponMutation.isPending || !!appliedCoupon}
                    >
                      {applyCouponMutation.isPending ? "Đang kiểm tra..." : appliedCoupon ? "Đã áp dụng" : "Áp dụng"}
                    </Button>
                  </div>
                  {appliedCoupon && (
                    <div className="mt-2 flex items-center justify-between text-sm">
                      <span className="text-green-600 dark:text-green-400">Mã "{appliedCoupon}" - Giảm {formatCurrency(couponDiscount)}</span>
                      <button 
                        type="button"
                        className="text-red-500 hover:text-red-600 text-xs"
                        onClick={() => {
                          setAppliedCoupon(null);
                          setCouponDiscount(0);
                          setValue("coupon_code", "");
                        }}
                      >
                        Xóa
                      </button>
                    </div>
                  )}
                </div>

                {/* Summary */}
                <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Tạm tính</span>
                    <span className="text-gray-900 dark:text-gray-100">
                      {formatCurrency(subtotal)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 dark:text-gray-400">Phí vận chuyển</span>
                    {shippingCost === 0 ? (
                      <span className="text-green-600 dark:text-green-400 font-medium">
                        Miễn phí
                      </span>
                    ) : (
                      <span className="text-gray-900 dark:text-gray-100">
                        {formatCurrency(shippingCost)}
                      </span>
                    )}
                  </div>
                  {subtotal > 0 && subtotal < freeShippingThreshold && (
                    <p className="text-xs text-gray-500 dark:text-gray-400">
                      Mua thêm {formatCurrency(freeShippingThreshold - subtotal)} để được miễn phí vận chuyển
                    </p>
                  )}
                  {couponDiscount > 0 && (
                    <div className="flex justify-between text-sm">
                      <span className="text-green-600 dark:text-green-400">Giảm giá</span>
                      <span className="text-green-600 dark:text-green-400 font-medium">
                        -{formatCurrency(couponDiscount)}
                      </span>
                    </div>
                  )}
                </div>

                <div className="mt-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                  <div className="flex justify-between">
                    <span className="text-lg font-semibold text-gray-900 dark:text-gray-100">
                      Tổng cộng
                    </span>
                    <span className="text-xl font-bold text-orange-500">
                      {formatCurrency(total)}
                    </span>
                  </div>
                </div>

                <Button
                  type="submit"
                  className="w-full mt-6"
                  size="lg"
                  isLoading={isSubmitting || isProcessing}
                >
                  Đặt hàng
                </Button>

                <p className="mt-4 text-center text-xs text-gray-500 dark:text-gray-400">
                  Bằng việc đặt hàng, bạn đồng ý với{" "}
                  <a href="/terms" className="text-orange-500 hover:underline">
                    Điều khoản dịch vụ
                  </a>{" "}
                  của OWLS
                </p>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}