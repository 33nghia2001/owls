/**
 * SEO utilities for generating meta tags
 */

export interface SEOConfig {
  title: string;
  description: string;
  image?: string;
  url?: string;
  type?: "website" | "article" | "product";
  keywords?: string[];
  author?: string;
  noIndex?: boolean;
  canonical?: string;
  product?: {
    price: string;
    currency?: string;
    availability?: "in stock" | "out of stock" | "preorder";
    brand?: string;
    category?: string;
  };
  article?: {
    publishedTime?: string;
    modifiedTime?: string;
    author?: string;
    section?: string;
    tags?: string[];
  };
}

const SITE_NAME = "OWLS Marketplace";
const DEFAULT_IMAGE = "/og-default.jpg";
const SITE_URL = "https://owls.vn";
const TWITTER_HANDLE = "@owlsmarketplace";

/**
 * Generate comprehensive meta tags for SEO
 */
export function generateMeta(config: SEOConfig) {
  const {
    title,
    description,
    image = DEFAULT_IMAGE,
    url,
    type = "website",
    keywords = [],
    author,
    noIndex = false,
    canonical,
    product,
    article,
  } = config;

  const fullTitle = title.includes(SITE_NAME) ? title : `${title} - ${SITE_NAME}`;
  const fullUrl = url?.startsWith("http") ? url : `${SITE_URL}${url || ""}`;
  const fullImage = image?.startsWith("http") ? image : `${SITE_URL}${image}`;

  const meta: Array<Record<string, string | object | undefined>> = [
    // Basic
    { title: fullTitle },
    { name: "description", content: description },
    
    // Robots
    { name: "robots", content: noIndex ? "noindex, nofollow" : "index, follow" },
    
    // Canonical
    ...(canonical ? [{ tagName: "link", rel: "canonical", href: canonical }] : []),
    
    // Open Graph
    { property: "og:type", content: type },
    { property: "og:title", content: fullTitle },
    { property: "og:description", content: description },
    { property: "og:image", content: fullImage },
    { property: "og:url", content: fullUrl },
    { property: "og:site_name", content: SITE_NAME },
    { property: "og:locale", content: "vi_VN" },
    
    // Twitter Card
    { name: "twitter:card", content: "summary_large_image" },
    { name: "twitter:site", content: TWITTER_HANDLE },
    { name: "twitter:title", content: fullTitle },
    { name: "twitter:description", content: description },
    { name: "twitter:image", content: fullImage },
  ];

  // Keywords
  if (keywords.length > 0) {
    meta.push({ name: "keywords", content: keywords.join(", ") });
  }

  // Author
  if (author) {
    meta.push({ name: "author", content: author });
  }

  // Product specific meta
  if (product) {
    meta.push(
      { property: "product:price:amount", content: product.price },
      { property: "product:price:currency", content: product.currency || "VND" }
    );
    
    if (product.availability) {
      meta.push({ property: "product:availability", content: product.availability });
    }
    if (product.brand) {
      meta.push({ property: "product:brand", content: product.brand });
    }
    if (product.category) {
      meta.push({ property: "product:category", content: product.category });
    }
  }

  // Article specific meta
  if (article) {
    if (article.publishedTime) {
      meta.push({ property: "article:published_time", content: article.publishedTime });
    }
    if (article.modifiedTime) {
      meta.push({ property: "article:modified_time", content: article.modifiedTime });
    }
    if (article.author) {
      meta.push({ property: "article:author", content: article.author });
    }
    if (article.section) {
      meta.push({ property: "article:section", content: article.section });
    }
    article.tags?.forEach((tag) => {
      meta.push({ property: "article:tag", content: tag });
    });
  }

  return meta;
}

/**
 * Generate JSON-LD structured data for products
 */
export function generateProductSchema(product: {
  name: string;
  description: string;
  images: string[];
  price: string;
  currency?: string;
  brand?: string;
  seller?: string;
  rating?: number;
  reviewCount?: number;
  sku?: string;
  availability?: "InStock" | "OutOfStock" | "PreOrder";
}) {
  return {
    "script:ld+json": {
      "@context": "https://schema.org",
      "@type": "Product",
      name: product.name,
      description: product.description,
      image: product.images,
      sku: product.sku,
      brand: product.brand
        ? {
            "@type": "Brand",
            name: product.brand,
          }
        : undefined,
      offers: {
        "@type": "Offer",
        price: product.price,
        priceCurrency: product.currency || "VND",
        availability: `https://schema.org/${product.availability || "InStock"}`,
        seller: product.seller
          ? {
              "@type": "Organization",
              name: product.seller,
            }
          : undefined,
      },
      aggregateRating:
        product.rating && product.reviewCount
          ? {
              "@type": "AggregateRating",
              ratingValue: product.rating,
              reviewCount: product.reviewCount,
            }
          : undefined,
    },
  };
}

/**
 * Generate JSON-LD structured data for organization
 */
export function generateOrganizationSchema() {
  return {
    "script:ld+json": {
      "@context": "https://schema.org",
      "@type": "Organization",
      name: SITE_NAME,
      url: SITE_URL,
      logo: `${SITE_URL}/logo.png`,
      sameAs: [
        "https://facebook.com/owlsmarketplace",
        "https://twitter.com/owlsmarketplace",
        "https://instagram.com/owlsmarketplace",
      ],
      contactPoint: {
        "@type": "ContactPoint",
        telephone: "+84-xxx-xxx-xxx",
        contactType: "customer service",
        availableLanguage: ["Vietnamese", "English"],
      },
    },
  };
}

/**
 * Generate JSON-LD breadcrumb structured data
 */
export function generateBreadcrumbSchema(
  items: Array<{ name: string; url: string }>
) {
  return {
    "script:ld+json": {
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: items.map((item, index) => ({
        "@type": "ListItem",
        position: index + 1,
        name: item.name,
        item: item.url.startsWith("http") ? item.url : `${SITE_URL}${item.url}`,
      })),
    },
  };
}
