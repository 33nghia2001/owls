import { Link, useLoaderData, type LoaderFunctionArgs } from "react-router";
import { ChevronRight, Sparkles, TrendingUp, Clock, Tag, Truck, Shield, RotateCcw, CreditCard, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";
import { productsApi } from "~/lib/services";
import { ProductGrid } from "~/components/product";
import type { ProductListItem, Category } from "~/lib/types";

export function meta() {
  return [
    { title: "OWLS Marketplace - Mua sắm thông minh" },
    { name: "description", content: "Nền tảng thương mại điện tử đa người bán hàng đầu Việt Nam" },
  ];
}

export async function loader({}: LoaderFunctionArgs) {
  try {
    const [featured, bestSellers, newArrivals, categories] = await Promise.all([
      productsApi.getFeaturedProducts(),
      productsApi.getBestSellers(),
      productsApi.getNewArrivals(),
      productsApi.getCategories(),
    ]);

    return {
      featured: featured || [],
      bestSellers: bestSellers || [],
      newArrivals: newArrivals || [],
      categories: categories?.results || categories || [],
    };
  } catch (error) {
    console.error("Failed to load homepage data:", error);
    return {
      featured: [],
      bestSellers: [],
      newArrivals: [],
      categories: [],
    };
  }
}

// Animation variants
const fadeInUp = {
  initial: { opacity: 0, y: 30 },
  animate: { opacity: 1, y: 0 },
  transition: { duration: 0.5 }
};

const staggerContainer = {
  animate: { transition: { staggerChildren: 0.1 } }
};

export default function Home() {
  const { featured, bestSellers, newArrivals, categories } = useLoaderData<typeof loader>();

  return (
    <div className="overflow-hidden">
      {/* Hero Section - Modern Design */}
      <section className="relative min-h-[600px] overflow-hidden bg-gradient-to-br from-orange-500 via-orange-600 to-red-500">
        {/* Animated background shapes */}
        <div className="absolute inset-0">
          <motion.div
            className="absolute -left-20 top-20 h-72 w-72 rounded-full bg-white/10"
            animate={{ y: [0, 30, 0], x: [0, 20, 0] }}
            transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute -right-32 bottom-20 h-96 w-96 rounded-full bg-white/5"
            animate={{ y: [0, -40, 0], x: [0, -30, 0] }}
            transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
          />
          <motion.div
            className="absolute left-1/2 top-1/3 h-48 w-48 rounded-full bg-yellow-400/20"
            animate={{ scale: [1, 1.2, 1] }}
            transition={{ duration: 6, repeat: Infinity, ease: "easeInOut" }}
          />
        </div>

        <div className="container relative z-10 mx-auto px-4 py-20 lg:py-32">
          <div className="grid items-center gap-12 lg:grid-cols-2">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7 }}
              className="text-center lg:text-left"
            >
              <motion.span
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="mb-4 inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-2 text-sm font-medium text-white backdrop-blur-sm"
              >
                <Sparkles className="h-4 w-4" />
                Khuyến mãi mùa hè lên đến 50%
              </motion.span>
              <motion.h1
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
                className="mb-6 text-4xl font-bold leading-tight text-white md:text-5xl lg:text-6xl"
              >
                Mua sắm thông minh
                <br />
                <span className="text-yellow-300">cùng OWLS</span>
              </motion.h1>
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
                className="mb-8 text-lg text-white/90 md:text-xl"
              >
                Hàng ngàn sản phẩm chất lượng từ các nhà bán hàng uy tín.
                <br className="hidden md:block" />
                Giao hàng nhanh, đổi trả dễ dàng.
              </motion.p>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="flex flex-wrap justify-center gap-4 lg:justify-start"
              >
                <Link
                  to="/products"
                  className="group flex items-center gap-2 rounded-2xl bg-white px-8 py-4 font-bold text-orange-500 shadow-xl shadow-orange-900/20 transition-all hover:-translate-y-1 hover:shadow-2xl"
                >
                  Khám phá ngay
                  <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
                </Link>
                <Link
                  to="/seller"
                  className="rounded-2xl border-2 border-white/50 px-8 py-4 font-bold text-white backdrop-blur-sm transition-all hover:border-white hover:bg-white/10"
                >
                  Bán hàng cùng OWLS
                </Link>
              </motion.div>
            </motion.div>

            {/* Hero Stats */}
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.7, delay: 0.3 }}
              className="hidden lg:block"
            >
              <div className="grid grid-cols-2 gap-4">
                {[
                  { number: "10K+", label: "Sản phẩm" },
                  { number: "5K+", label: "Người bán" },
                  { number: "50K+", label: "Khách hàng" },
                  { number: "4.8★", label: "Đánh giá" },
                ].map((stat, index) => (
                  <motion.div
                    key={stat.label}
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.5 + index * 0.1 }}
                    className="rounded-2xl bg-white/10 p-6 text-center backdrop-blur-sm"
                  >
                    <div className="text-3xl font-bold text-white">{stat.number}</div>
                    <div className="text-sm text-white/80">{stat.label}</div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </div>

        {/* Wave decoration */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" className="w-full fill-white dark:fill-gray-950">
            <path d="M0,64L80,69.3C160,75,320,85,480,80C640,75,800,53,960,48C1120,43,1280,53,1360,58.7L1440,64L1440,120L1360,120C1280,120,1120,120,960,120C800,120,640,120,480,120C320,120,160,120,80,120L0,120Z"></path>
          </svg>
        </div>
      </section>

      {/* Categories - Modern Grid */}
      {categories.length > 0 && (
        <section className="py-16">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-8 flex items-center justify-between"
            >
              <div>
                <h2 className="text-2xl font-bold md:text-3xl">Danh mục nổi bật</h2>
                <p className="mt-1 text-gray-500">Khám phá các danh mục sản phẩm phổ biến</p>
              </div>
              <Link
                to="/categories"
                className="group flex items-center gap-1 rounded-xl bg-orange-50 px-4 py-2 font-medium text-orange-600 transition-colors hover:bg-orange-100 dark:bg-orange-900/20 dark:text-orange-400"
              >
                Xem tất cả
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </motion.div>
            <motion.div
              variants={staggerContainer}
              initial="initial"
              whileInView="animate"
              viewport={{ once: true }}
              className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8"
            >
              {categories.slice(0, 8).map((category: Category, index: number) => (
                <motion.div
                  key={category.id}
                  variants={fadeInUp}
                  whileHover={{ y: -8, scale: 1.02 }}
                  transition={{ duration: 0.3 }}
                >
                  <Link
                    to={`/categories/${category.slug}`}
                    className="group flex flex-col items-center rounded-2xl bg-gradient-to-b from-gray-50 to-white p-5 shadow-sm transition-all hover:shadow-lg dark:from-gray-800 dark:to-gray-900"
                  >
                    <div className="mb-3 flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-100 to-orange-50 text-3xl shadow-inner transition-transform group-hover:scale-110 dark:from-orange-900/30 dark:to-orange-800/20">
                      {category.icon || "📦"}
                    </div>
                    <span className="text-center text-sm font-semibold text-gray-700 transition-colors group-hover:text-orange-500 dark:text-gray-300">
                      {category.name}
                    </span>
                  </Link>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>
      )}

      {/* Featured Products */}
      {featured.length > 0 && (
        <section className="bg-gradient-to-b from-gray-50 to-white py-16 dark:from-gray-900 dark:to-gray-950">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-8 flex items-center gap-3"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-400 to-orange-600 shadow-lg shadow-orange-500/30">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div>
                <h2 className="text-2xl font-bold md:text-3xl">Sản phẩm nổi bật</h2>
                <p className="text-gray-500">Được yêu thích nhất tuần này</p>
              </div>
            </motion.div>
            <ProductGrid products={featured} columns={6} />
          </div>
        </section>
      )}

      {/* Promotions Banner */}
      <section className="py-16">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="grid gap-6 md:grid-cols-2"
          >
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="group relative overflow-hidden rounded-3xl bg-gradient-to-br from-purple-500 via-purple-600 to-pink-500 p-8 text-white shadow-xl shadow-purple-500/20"
            >
              <div className="relative z-10">
                <span className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-1.5 text-sm font-medium backdrop-blur-sm">
                  🔥 Khuyến mãi hot
                </span>
                <h3 className="mb-2 text-3xl font-bold">Giảm đến 50%</h3>
                <p className="mb-6 text-lg opacity-90">Cho đơn hàng đầu tiên</p>
                <Link
                  to="/deals"
                  className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 font-bold text-purple-600 shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl"
                >
                  Xem ngay <Tag className="h-5 w-5" />
                </Link>
              </div>
              <motion.div
                className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-white/10"
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 4, repeat: Infinity }}
              />
              <motion.div
                className="absolute -bottom-20 -right-20 h-72 w-72 rounded-full bg-white/5"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 6, repeat: Infinity }}
              />
            </motion.div>
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="group relative overflow-hidden rounded-3xl bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-500 p-8 text-white shadow-xl shadow-blue-500/20"
            >
              <div className="relative z-10">
                <span className="mb-3 inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-1.5 text-sm font-medium backdrop-blur-sm">
                  🚚 Free ship
                </span>
                <h3 className="mb-2 text-3xl font-bold">Miễn phí vận chuyển</h3>
                <p className="mb-6 text-lg opacity-90">Cho đơn hàng từ 300K</p>
                <Link
                  to="/products"
                  className="inline-flex items-center gap-2 rounded-xl bg-white px-6 py-3 font-bold text-blue-600 shadow-lg transition-all hover:-translate-y-1 hover:shadow-xl"
                >
                  Mua sắm ngay <ChevronRight className="h-5 w-5" />
                </Link>
              </div>
              <motion.div
                className="absolute -right-16 -top-16 h-48 w-48 rounded-full bg-white/10"
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 4, repeat: Infinity, delay: 1 }}
              />
              <motion.div
                className="absolute -bottom-20 -right-20 h-72 w-72 rounded-full bg-white/5"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 6, repeat: Infinity, delay: 1 }}
              />
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* Best Sellers */}
      {bestSellers.length > 0 && (
        <section className="py-16">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-8 flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-red-400 to-red-600 shadow-lg shadow-red-500/30">
                  <TrendingUp className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold md:text-3xl">Bán chạy nhất</h2>
                  <p className="text-gray-500">Top sản phẩm được mua nhiều</p>
                </div>
              </div>
              <Link
                to="/products?ordering=-sold_count"
                className="group flex items-center gap-1 rounded-xl bg-red-50 px-4 py-2 font-medium text-red-600 transition-colors hover:bg-red-100 dark:bg-red-900/20 dark:text-red-400"
              >
                Xem tất cả
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </motion.div>
            <ProductGrid products={bestSellers} columns={6} />
          </div>
        </section>
      )}

      {/* New Arrivals */}
      {newArrivals.length > 0 && (
        <section className="bg-gradient-to-b from-gray-50 to-white py-16 dark:from-gray-900 dark:to-gray-950">
          <div className="container mx-auto px-4">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="mb-8 flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-green-400 to-green-600 shadow-lg shadow-green-500/30">
                  <Clock className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold md:text-3xl">Hàng mới về</h2>
                  <p className="text-gray-500">Cập nhật mới nhất</p>
                </div>
              </div>
              <Link
                to="/products?ordering=-created_at"
                className="group flex items-center gap-1 rounded-xl bg-green-50 px-4 py-2 font-medium text-green-600 transition-colors hover:bg-green-100 dark:bg-green-900/20 dark:text-green-400"
              >
                Xem tất cả
                <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </Link>
            </motion.div>
            <ProductGrid products={newArrivals} columns={6} />
          </div>
        </section>
      )}

      {/* Trust Badges - Modern Design */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="mb-12 text-center"
          >
            <h2 className="text-2xl font-bold md:text-3xl">Tại sao chọn OWLS?</h2>
            <p className="mt-2 text-gray-500">Cam kết mang đến trải nghiệm mua sắm tốt nhất</p>
          </motion.div>
          <motion.div
            variants={staggerContainer}
            initial="initial"
            whileInView="animate"
            viewport={{ once: true }}
            className="grid grid-cols-2 gap-6 md:grid-cols-4"
          >
            {[
              { icon: Truck, title: "Giao hàng nhanh", desc: "Trong 2-5 ngày", color: "orange" },
              { icon: Shield, title: "Hàng chính hãng", desc: "100% authentic", color: "green" },
              { icon: RotateCcw, title: "Đổi trả dễ dàng", desc: "Trong 7 ngày", color: "blue" },
              { icon: CreditCard, title: "Thanh toán an toàn", desc: "Bảo mật tuyệt đối", color: "purple" },
            ].map((item, index) => (
              <motion.div
                key={item.title}
                variants={fadeInUp}
                whileHover={{ y: -8 }}
                className="group rounded-2xl bg-white p-6 text-center shadow-lg shadow-gray-200/50 transition-all hover:shadow-xl dark:bg-gray-900 dark:shadow-gray-900/50"
              >
                <div className={`mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-${item.color}-100 transition-transform group-hover:scale-110 dark:bg-${item.color}-900/30`}>
                  <item.icon className={`h-8 w-8 text-${item.color}-500`} />
                </div>
                <h3 className="mb-1 font-bold text-gray-900 dark:text-white">{item.title}</h3>
                <p className="text-sm text-gray-500">{item.desc}</p>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>
    </div>
  );
}
