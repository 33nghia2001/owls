import { Link, useLoaderData, type LoaderFunctionArgs, Form } from "react-router";
import { 
  ChevronRight, Sparkles, TrendingUp, Clock, Tag, Truck, Shield, 
  RotateCcw, CreditCard, ArrowRight, Star, Zap, Search, Flame, Timer, Store
} from "lucide-react";
import { motion, useScroll, useTransform } from "framer-motion";
import { productsApi, vendorsApi } from "~/lib/services";
import { ProductGrid } from "~/components/product";
import { Button } from "~/components/ui";
import { cn, formatPrice, getImageUrl } from "~/lib/utils";
import type { Category, Vendor } from "~/lib/types";

export function meta() {
  return [
    { title: "OWLS Marketplace - Mua sắm thông minh" },
    { name: "description", content: "Nền tảng thương mại điện tử đa người bán hàng đầu Việt Nam" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  try {
    const [featured, bestSellers, newArrivals, categories, vendorsData] = await Promise.all([
      productsApi.getFeaturedProducts(),
      productsApi.getBestSellers(),
      productsApi.getNewArrivals(),
      productsApi.getCategories(),
      vendorsApi.getVendors({ page: 1 }),
    ]);

    return {
      featured: featured || [],
      bestSellers: bestSellers || [],
      newArrivals: newArrivals || [],
      categories: categories?.results || categories || [],
      topVendors: vendorsData?.results?.slice(0, 8) || [],
    };
  } catch (error) {
    console.error("Failed to load homepage data:", error);
    return {
      featured: [],
      bestSellers: [],
      newArrivals: [],
      categories: [],
      topVendors: [],
    };
  }
}

// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.6, ease: "easeOut" }
};

const staggerContainer = {
  animate: { transition: { staggerChildren: 0.1 } }
};

export default function Home() {
  const { featured, bestSellers, newArrivals, categories, topVendors } = useLoaderData<typeof loader>();
  const { scrollY } = useScroll();
  
  // Parallax effects
  const y1 = useTransform(scrollY, [0, 500], [0, 200]);
  const y2 = useTransform(scrollY, [0, 500], [0, -150]);
  const opacityHero = useTransform(scrollY, [0, 400], [1, 0]);
  const scaleHero = useTransform(scrollY, [0, 400], [1, 0.95]);

  return (
    <div className="overflow-hidden bg-white dark:bg-[#0a0a0a] min-h-screen">
      
      {/* 1. HERO SECTION - MARKETPLACE STYLE */}
      <section className="relative min-h-[85vh] flex items-center justify-center overflow-hidden bg-[#050505]">
        
        {/* Animated Background Mesh */}
        <div className="absolute inset-0 z-0">
            <div className="absolute top-0 left-0 w-full h-full bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.3),rgba(255,255,255,0))]" />
            <motion.div 
              style={{ y: y1, x: -50 }}
              className="absolute top-[20%] left-[10%] w-[30vw] h-[30vw] rounded-full bg-orange-500/20 blur-[100px] mix-blend-screen animate-pulse"
            />
            <motion.div 
              style={{ y: y2, x: 50 }}
              className="absolute bottom-[10%] right-[10%] w-[35vw] h-[35vw] rounded-full bg-purple-600/20 blur-[120px] mix-blend-screen" 
            />
            {/* Grid Pattern */}
            <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
        </div>

        <motion.div 
          style={{ opacity: opacityHero, scale: scaleHero }}
          className="container relative z-10 mx-auto px-4 py-20 text-center"
        >
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mx-auto max-w-5xl"
          >
            <div className="mb-6 flex justify-center">
              <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-sm font-medium text-orange-400 backdrop-blur-md shadow-lg shadow-orange-500/10">
                <Sparkles className="h-4 w-4" />
                <span className="bg-gradient-to-r from-orange-400 to-amber-200 bg-clip-text text-transparent">
                  Sàn thương mại điện tử đa người bán
                </span>
              </span>
            </div>

            <h1 className="mb-8 text-5xl font-extrabold tracking-tight text-white sm:text-7xl lg:text-8xl">
              Mua sắm thông minh <br />
              <span className="bg-gradient-to-r from-orange-500 via-red-500 to-purple-600 bg-clip-text text-transparent">
                cùng OWLS
              </span>
            </h1>

            {/* Marketplace Search Bar */}
            <div className="mx-auto mb-8 max-w-2xl relative">
              <Form action="/search" method="get" className="relative flex items-center group">
                <Search className="absolute left-5 h-6 w-6 text-gray-400 group-focus-within:text-orange-500 transition-colors" />
                <input 
                  type="text" 
                  name="q"
                  placeholder="Bạn đang tìm kiếm gì hôm nay?" 
                  className="h-16 w-full rounded-full border-2 border-white/10 bg-white/5 pl-14 pr-32 text-lg text-white placeholder:text-gray-400 backdrop-blur-xl transition-all focus:border-orange-500/50 focus:bg-white/10 focus:outline-none focus:ring-4 focus:ring-orange-500/20 shadow-2xl"
                />
                <button 
                  type="submit"
                  className="absolute right-2 h-12 rounded-full bg-gradient-to-r from-orange-500 to-red-600 px-8 font-bold text-white transition-all hover:scale-105 hover:shadow-lg hover:shadow-orange-500/30"
                >
                  Tìm kiếm
                </button>
              </Form>
              
              {/* Popular Tags */}
              <div className="mt-4 flex flex-wrap justify-center gap-2 text-sm text-gray-400">
                <span>Phổ biến:</span>
                {['iPhone 15', 'Giày Sneaker', 'Bàn phím cơ', 'Son môi', 'Tai nghe'].map((tag, i) => (
                  <Link 
                    key={i} 
                    to={`/search?q=${encodeURIComponent(tag)}`}
                    className="hover:text-orange-400 hover:underline decoration-orange-400/50 transition-colors"
                  >
                    {tag}
                  </Link>
                ))}
              </div>
            </div>
          </motion.div>
        </motion.div>
      </section>

      {/* 2. FLASH SALE SECTION - URGENCY */}
      <section className="bg-gradient-to-r from-orange-50 to-red-50 py-12 dark:from-orange-950/20 dark:to-red-950/20 border-y border-orange-100 dark:border-orange-900/30">
        <div className="container mx-auto px-4">
          <div className="mb-8 flex flex-col md:flex-row md:items-end justify-between gap-4">
             <div className="flex items-center gap-4">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-orange-500 to-red-600 text-white shadow-lg shadow-orange-500/30 animate-pulse">
                   <Flame className="w-8 h-8 fill-current" />
                </div>
                <div>
                   <h2 className="text-3xl font-black text-gray-900 dark:text-white uppercase tracking-tight italic">
                     Flash Sale
                   </h2>
                   <div className="flex items-center gap-2 mt-1 text-red-600 dark:text-red-400 font-medium">
                      <Timer className="w-4 h-4" />
                      <span>Kết thúc trong:</span>
                      <span className="flex gap-1 font-mono font-bold bg-red-100 dark:bg-red-900/40 px-2 rounded text-red-700 dark:text-red-300">02:15:40</span>
                   </div>
                </div>
             </div>
             <Link to="/deals" className="flex items-center gap-1 font-semibold text-orange-600 hover:text-orange-700 dark:text-orange-400">
               Xem tất cả <ChevronRight className="w-4 h-4" />
             </Link>
          </div>
          
          {/* Horizontal Scroll Flash Sale Items */}
          <div className="flex gap-4 overflow-x-auto pb-4 scrollbar-hide snap-x">
             {bestSellers.slice(0, 6).map((product: any) => (
                <div key={product.id} className="min-w-[200px] w-[200px] snap-center rounded-xl bg-white dark:bg-gray-900 border border-orange-100 dark:border-orange-900/30 p-3 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">
                   <div className="absolute top-2 left-2 z-10 bg-red-600 text-white text-xs font-bold px-2 py-0.5 rounded-full">-30%</div>
                   <div className="relative aspect-square rounded-lg overflow-hidden mb-3 bg-gray-100 dark:bg-gray-800">
                      <img src={getImageUrl(product.primary_image?.image)} alt={product.name} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                   </div>
                   <div className="space-y-1">
                      <div className="h-1.5 w-full bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                         <div className="h-full bg-orange-500 w-[70%] rounded-full" />
                      </div>
                      <div className="flex justify-between text-[10px] text-gray-500 uppercase font-bold">
                         <span>Đã bán {product.sold_count}</span>
                         <span className="text-orange-600">Sắp hết</span>
                      </div>
                      <h4 className="font-semibold text-gray-900 dark:text-white truncate mt-1">{product.name}</h4>
                      <div className="flex items-center gap-2">
                         <span className="text-lg font-bold text-red-600">{formatPrice(product.price)}</span>
                      </div>
                   </div>
                </div>
             ))}
          </div>
        </div>
      </section>

      {/* 3. CATEGORIES - GLASSMORPHISM CARDS */}
      {categories.length > 0 && (
        <section className="py-20 bg-gray-50 dark:bg-[#0a0a0a]">
          <div className="container mx-auto px-4">
            <div className="mb-10 flex items-center justify-between">
               <h2 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                 <span className="w-1 h-8 bg-orange-500 rounded-full block"></span>
                 Danh mục nổi bật
               </h2>
               <Link to="/categories" className="text-sm font-medium text-gray-500 hover:text-orange-600 flex items-center gap-1 transition-colors">
                  Xem thêm <ArrowRight className="w-4 h-4" />
               </Link>
            </div>
            
            <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8">
              {categories.slice(0, 16).map((cat: Category, idx: number) => (
                <motion.div
                  key={cat.id}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: idx * 0.03, duration: 0.4 }}
                  viewport={{ once: true }}
                >
                  <Link to={`/categories/${cat.slug}`} className="group relative block h-full">
                    <div className="relative h-full flex flex-col items-center justify-center rounded-2xl border border-white bg-white/50 p-4 shadow-sm backdrop-blur-sm transition-all duration-300 hover:-translate-y-1 hover:border-orange-200 hover:bg-white hover:shadow-lg dark:border-gray-800 dark:bg-gray-900/50 dark:hover:bg-gray-900">
                        <div className="mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-gray-100 text-3xl shadow-inner transition-transform duration-300 group-hover:scale-110 group-hover:bg-orange-50 dark:bg-gray-800 dark:group-hover:bg-orange-900/20">
                          {cat.image ? (
                            <img src={cat.image} alt={cat.name} className="h-9 w-9 object-contain" />
                          ) : (
                            <span>{cat.icon || "📦"}</span>
                          )}
                        </div>
                        <h3 className="text-center text-sm font-semibold text-gray-700 transition-colors group-hover:text-orange-600 dark:text-gray-300">
                          {cat.name}
                        </h3>
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* 4. TOP VENDORS / OFFICIAL STORES */}
      {topVendors && topVendors.length > 0 && (
        <section className="py-20 bg-white dark:bg-[#111]">
          <div className="container mx-auto px-4">
             <div className="mb-10 flex items-center justify-between">
                <div className="flex items-center gap-3">
                   <div className="p-2 rounded-xl bg-blue-600 text-white">
                      <Store className="w-6 h-6" />
                   </div>
                   <div>
                      <h2 className="text-2xl font-bold text-gray-900 dark:text-white uppercase">Gian hàng nổi bật</h2>
                      <p className="text-sm text-gray-500">Mua sắm từ các nhà bán hàng uy tín nhất</p>
                   </div>
                </div>
                <Link to="/shops" className="text-sm font-medium text-blue-600 hover:underline">Xem tất cả shop</Link>
             </div>

             <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {topVendors.map((vendor: Vendor, idx: number) => (
                   <Link key={vendor.id} to={`/shops/${vendor.slug}`} className="group relative overflow-hidden rounded-2xl border border-gray-200 bg-white p-6 transition-all hover:shadow-xl dark:border-gray-800 dark:bg-gray-900">
                      {/* Background Banner Blur */}
                      <div className="absolute inset-0 h-24 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 opacity-50 transition-opacity group-hover:opacity-100" />
                      
                      <div className="relative z-10 flex flex-col items-center">
                         <div className="mb-3 h-20 w-20 rounded-full border-4 border-white bg-white shadow-md overflow-hidden dark:border-gray-800 dark:bg-gray-800">
                            {vendor.logo ? (
                               <img src={vendor.logo} alt={vendor.shop_name} className="h-full w-full object-cover" />
                            ) : (
                               <div className="flex h-full w-full items-center justify-center bg-blue-100 text-2xl font-bold text-blue-600">
                                  {vendor.shop_name.charAt(0)}
                               </div>
                            )}
                         </div>
                         <h3 className="text-lg font-bold text-gray-900 dark:text-white group-hover:text-blue-600 transition-colors">{vendor.shop_name}</h3>
                         <div className="mt-2 flex items-center gap-1 text-sm text-gray-500">
                            <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                            <span className="font-medium text-gray-900 dark:text-gray-100">{vendor.rating.toFixed(1)}</span>
                            <span>•</span>
                            <span>{vendor.total_products} sản phẩm</span>
                         </div>
                         <Button variant="secondary" className="mt-4 w-full h-9 rounded-full text-xs hover:bg-blue-600 hover:text-white dark:border-gray-700">
                            Xem Shop
                         </Button>
                      </div>
                   </Link>
                ))}
             </div>
          </div>
        </section>
      )}

      {/* 5. FEATURED PRODUCTS */}
      {featured.length > 0 && (
        <section className="py-20 bg-gray-50 dark:bg-[#0a0a0a]">
          <div className="container mx-auto px-4">
            <div className="mb-10 flex flex-col items-center text-center">
                <span className="mb-2 rounded-full bg-orange-100 px-3 py-1 text-xs font-bold text-orange-600 dark:bg-orange-900/30 dark:text-orange-400 uppercase tracking-wide">
                  Dành riêng cho bạn
                </span>
                <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white">Gợi ý hôm nay</h2>
                <div className="mt-4 h-1 w-20 rounded-full bg-gradient-to-r from-orange-500 to-red-500" />
            </div>
            
            <ProductGrid products={featured} columns={5} />
            
            <div className="mt-12 flex justify-center">
                <Link to="/products">
                  <Button variant="outline" className="h-12 rounded-full px-8 border-gray-300 hover:border-gray-900 hover:bg-gray-900 hover:text-white dark:border-gray-700 dark:hover:bg-white dark:hover:text-black transition-all">
                    Xem thêm sản phẩm
                  </Button>
                </Link>
            </div>
          </div>
        </section>
      )}

      {/* 6. PROMOTIONS - BENTO GRID */}
      <section className="py-20 bg-white dark:bg-[#111]">
         <div className="container mx-auto px-4">
            <h2 className="mb-10 text-3xl font-bold text-gray-900 dark:text-white">Bộ sưu tập & Ưu đãi</h2>
            <div className="grid grid-cols-1 gap-6 md:grid-cols-3 md:grid-rows-2 h-auto md:h-[600px]">
               {/* Banner 1 - Large */}
               <motion.div 
                 whileHover={{ scale: 1.005 }}
                 className="group relative overflow-hidden rounded-3xl bg-gradient-to-br from-indigo-600 to-purple-700 p-8 text-white shadow-2xl md:col-span-2 md:row-span-2"
               >
                  <div className="relative z-10 flex h-full flex-col justify-between">
                     <div>
                       <span className="inline-block rounded-lg bg-white/20 px-3 py-1 text-xs font-bold backdrop-blur-sm">TECH TREND 2024</span>
                       <h3 className="mt-4 text-4xl font-bold leading-tight md:text-5xl">Nâng cấp không gian<br/>Làm việc của bạn</h3>
                       <p className="mt-4 max-w-sm text-indigo-100 opacity-90">Bàn phím cơ, chuột gaming, màn hình 4K và nhiều hơn nữa với giá ưu đãi.</p>
                     </div>
                     <div className="mt-8">
                       <Link to="/products?category=electronics">
                         <Button className="h-12 rounded-full bg-white px-8 font-bold text-indigo-600 hover:bg-gray-100 border-none transition-transform hover:scale-105">
                           Khám phá ngay
                         </Button>
                       </Link>
                     </div>
                  </div>
                  {/* Decorative Elements */}
                  <div className="absolute right-0 top-0 h-[500px] w-[500px] translate-x-1/3 -translate-y-1/3 rounded-full bg-white/10 blur-[80px]" />
                  <div className="absolute bottom-0 right-0 h-64 w-64 rounded-full bg-indigo-500/30 blur-[60px]" />
                  <img src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?auto=format&fit=crop&q=80&w=800" alt="Tech" className="absolute right-0 bottom-0 h-full w-2/3 object-cover opacity-20 mix-blend-overlay transition-transform duration-700 group-hover:scale-105" style={{maskImage: 'linear-gradient(to left, black, transparent)'}} />
               </motion.div>

               {/* Banner 2 - Top Right */}
               <motion.div 
                 whileHover={{ scale: 1.01 }}
                 className="relative overflow-hidden rounded-3xl bg-[#1A1A1A] p-8 text-white shadow-xl dark:bg-gray-800"
               >
                  <div className="relative z-10">
                     <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-gray-400 tracking-widest">MEMBER EXCLUSIVE</span>
                        <Tag className="h-5 w-5 text-orange-500" />
                     </div>
                     <h3 className="mt-4 text-2xl font-bold">Voucher 50K</h3>
                     <p className="text-sm text-gray-400 mt-1">Cho đơn hàng từ 200K khi thanh toán qua VNPay</p>
                  </div>
                  <div className="absolute -right-10 -top-10 h-32 w-32 rounded-full bg-orange-500/20 blur-2xl" />
                  <div className="absolute bottom-4 right-4 opacity-10">
                     <CreditCard className="w-24 h-24" />
                  </div>
               </motion.div>

               {/* Banner 3 - Bottom Right */}
               <motion.div 
                 whileHover={{ scale: 1.01 }}
                 className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-green-500 to-teal-600 p-8 text-white shadow-xl"
               >
                  <div className="relative z-10">
                     <div className="flex items-center gap-2">
                        <Truck className="h-6 w-6" />
                        <h3 className="text-xl font-bold">Freeship Xtra</h3>
                     </div>
                     <p className="mt-2 text-sm text-white/90">Miễn phí vận chuyển lên đến 70K cho mọi đơn hàng.</p>
                     <Link to="/products" className="mt-6 inline-flex items-center gap-1 text-sm font-bold hover:gap-2 transition-all">
                        Lấy mã ngay <ArrowRight className="w-4 h-4" />
                     </Link>
                  </div>
                  <div className="absolute -bottom-10 -left-10 h-40 w-40 rounded-full bg-white/20 blur-3xl" />
               </motion.div>
            </div>
         </div>
      </section>

      {/* 7. SPLIT SECTION - BEST SELLERS & NEW ARRIVALS */}
      <section className="py-20 bg-gray-50 dark:bg-[#0a0a0a]">
         <div className="container mx-auto px-4">
            <div className="grid gap-12 lg:grid-cols-2">
               {/* Best Sellers */}
               {bestSellers.length > 0 && (
                <div className="bg-white dark:bg-gray-900 rounded-3xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
                    <div className="mb-6 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-red-100 text-red-600 dark:bg-red-900/30">
                          <TrendingUp className="h-5 w-5" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">Xu hướng tìm kiếm</h3>
                      </div>
                      <Link to="/products?sort=-sold_count" className="text-sm font-medium text-gray-500 hover:text-red-600">Xem thêm</Link>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      {bestSellers.slice(0, 4).map((product: any) => (
                        <div key={product.id} className="group relative rounded-xl border border-gray-100 bg-white p-3 transition-all hover:shadow-lg hover:border-red-100 dark:border-gray-800 dark:bg-gray-950 dark:hover:border-gray-700">
                          <div className="relative aspect-square overflow-hidden rounded-lg bg-gray-100 mb-3">
                             <img src={getImageUrl(product.primary_image?.image)} alt={product.name} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                             <div className="absolute top-2 left-2 rounded bg-gradient-to-r from-red-500 to-orange-500 px-2 py-0.5 text-[10px] font-bold text-white shadow-sm">TOP</div>
                          </div>
                          <Link to={`/products/${product.slug}`} className="block">
                            <h4 className="line-clamp-2 text-sm font-medium text-gray-900 group-hover:text-red-600 dark:text-gray-100 min-h-[2.5em]">{product.name}</h4>
                            <div className="mt-2 font-bold text-red-600">{formatPrice(product.price)}</div>
                            <div className="mt-1 text-xs text-gray-500">Đã bán {product.sold_count}</div>
                          </Link>
                        </div>
                      ))}
                    </div>
                </div>
               )}

               {/* New Arrivals */}
               {newArrivals.length > 0 && (
                <div className="bg-white dark:bg-gray-900 rounded-3xl p-6 shadow-sm border border-gray-100 dark:border-gray-800">
                    <div className="mb-6 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-green-100 text-green-600 dark:bg-green-900/30">
                          <Clock className="h-5 w-5" />
                        </div>
                        <h3 className="text-xl font-bold text-gray-900 dark:text-white">Mới lên kệ</h3>
                      </div>
                      <Link to="/products?sort=-created_at" className="text-sm font-medium text-gray-500 hover:text-green-600">Xem thêm</Link>
                    </div>
                    <div className="space-y-4">
                      {newArrivals.slice(0, 3).map((product: any) => (
                        <Link key={product.id} to={`/products/${product.slug}`} className="group flex gap-4 rounded-xl border border-gray-100 bg-white p-3 transition-colors hover:border-green-200 hover:bg-green-50/10 dark:border-gray-800 dark:bg-gray-950 dark:hover:border-green-900/50">
                          <div className="h-24 w-24 flex-shrink-0 overflow-hidden rounded-lg bg-gray-100">
                             <img src={getImageUrl(product.primary_image?.image)} alt={product.name} className="h-full w-full object-cover transition-transform group-hover:scale-105" />
                          </div>
                          <div className="flex flex-1 flex-col justify-center">
                             <div className="mb-1 text-xs font-bold text-green-600 uppercase tracking-wider">New Arrival</div>
                             <h4 className="line-clamp-2 font-medium text-gray-900 group-hover:text-green-700 dark:text-gray-100">{product.name}</h4>
                             <div className="mt-2 flex items-center justify-between">
                                <span className="text-lg font-bold text-gray-900 dark:text-white">{formatPrice(product.price)}</span>
                                <span className="text-xs text-gray-500">{product.vendor.shop_name}</span>
                             </div>
                          </div>
                        </Link>
                      ))}
                    </div>
                </div>
               )}
            </div>
         </div>
      </section>

      {/* 8. TRUST BADGES - MINIMALIST */}
      <section className="py-16 border-t border-gray-100 bg-white dark:bg-[#0a0a0a] dark:border-gray-800">
         <div className="container mx-auto px-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
               {[
                  { icon: Truck, title: "Giao hàng siêu tốc", sub: "Nhận hàng trong 2-5 ngày" },
                  { icon: Shield, title: "Bảo hành chính hãng", sub: "Hoàn tiền 100% nếu giả" },
                  { icon: RotateCcw, title: "Đổi trả miễn phí", sub: "Trong vòng 7 ngày" },
                  { icon: CreditCard, title: "Thanh toán an toàn", sub: "Đa dạng hình thức" },
               ].map((item, idx) => (
                  <motion.div 
                    key={idx} 
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    viewport={{ once: true }}
                    className="flex flex-col items-center text-center gap-4"
                  >
                     <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gray-50 text-gray-400 transition-colors hover:bg-orange-50 hover:text-orange-500 dark:bg-gray-900 dark:hover:bg-orange-900/20">
                        <item.icon className="h-8 w-8" />
                     </div>
                     <div>
                        <h4 className="font-bold text-gray-900 dark:text-gray-100">{item.title}</h4>
                        <p className="text-sm text-gray-500 mt-1">{item.sub}</p>
                     </div>
                  </motion.div>
               ))}
            </div>
         </div>
      </section>
      
    </div>
  );
}