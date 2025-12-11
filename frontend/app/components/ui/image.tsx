import { useState, useRef, useEffect, forwardRef, type ImgHTMLAttributes } from "react";
import { cn } from "~/lib/utils";

// Default placeholder for images that fail to load or don't exist
const DEFAULT_FALLBACK = "/placeholder.jpg";

// Image loading states
type ImageLoadingState = "idle" | "loading" | "loaded" | "error";

export interface ImageProps extends Omit<ImgHTMLAttributes<HTMLImageElement>, "src"> {
  /** Image source URL */
  src?: string | null;
  /** Alt text for accessibility */
  alt: string;
  /** Fallback image URL when source fails to load */
  fallback?: string;
  /** Aspect ratio for the container (e.g., "16/9", "1/1", "4/3") */
  aspectRatio?: string;
  /** Enable lazy loading with Intersection Observer */
  lazy?: boolean;
  /** Show skeleton while loading */
  skeleton?: boolean;
  /** Object fit style */
  fit?: "cover" | "contain" | "fill" | "none" | "scale-down";
  /** Border radius preset */
  rounded?: "none" | "sm" | "md" | "lg" | "xl" | "2xl" | "full";
  /** Custom wrapper className */
  wrapperClassName?: string;
  /** Callback when image loads successfully */
  onLoad?: () => void;
  /** Callback when image fails to load */
  onError?: () => void;
}

/**
 * Optimized Image component with:
 * - Lazy loading via Intersection Observer
 * - Fallback image support
 * - Loading skeleton
 * - Responsive aspect ratio container
 * - Error handling
 */
export const Image = forwardRef<HTMLImageElement, ImageProps>(
  (
    {
      src,
      alt,
      fallback = DEFAULT_FALLBACK,
      aspectRatio,
      lazy = true,
      skeleton = true,
      fit = "cover",
      rounded = "none",
      wrapperClassName,
      className,
      onLoad,
      onError,
      ...props
    },
    ref
  ) => {
    const [loadingState, setLoadingState] = useState<ImageLoadingState>("idle");
    const [currentSrc, setCurrentSrc] = useState<string | null>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const hasTriedFallback = useRef(false);

    // Determine the actual source to use
    const actualSrc = src || fallback;

    // Setup Intersection Observer for lazy loading
    useEffect(() => {
      if (!lazy) {
        setCurrentSrc(actualSrc);
        setLoadingState("loading");
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              setCurrentSrc(actualSrc);
              setLoadingState("loading");
              observer.disconnect();
            }
          });
        },
        {
          rootMargin: "100px", // Start loading 100px before entering viewport
          threshold: 0,
        }
      );

      if (containerRef.current) {
        observer.observe(containerRef.current);
      }

      return () => observer.disconnect();
    }, [actualSrc, lazy]);

    // Handle successful image load
    const handleLoad = () => {
      setLoadingState("loaded");
      hasTriedFallback.current = false;
      onLoad?.();
    };

    // Handle image load error
    const handleError = () => {
      // Try fallback if we haven't already
      if (!hasTriedFallback.current && currentSrc !== fallback) {
        hasTriedFallback.current = true;
        setCurrentSrc(fallback);
        return;
      }
      
      setLoadingState("error");
      onError?.();
    };

    // Border radius classes
    const roundedClasses = {
      none: "",
      sm: "rounded-sm",
      md: "rounded-md",
      lg: "rounded-lg",
      xl: "rounded-xl",
      "2xl": "rounded-2xl",
      full: "rounded-full",
    };

    // Object fit classes
    const fitClasses = {
      cover: "object-cover",
      contain: "object-contain",
      fill: "object-fill",
      none: "object-none",
      "scale-down": "object-scale-down",
    };

    const showSkeleton = skeleton && (loadingState === "idle" || loadingState === "loading");

    return (
      <div
        ref={containerRef}
        className={cn(
          "relative overflow-hidden bg-gray-100 dark:bg-gray-800",
          roundedClasses[rounded],
          aspectRatio && `aspect-[${aspectRatio}]`,
          wrapperClassName
        )}
        style={aspectRatio ? { aspectRatio } : undefined}
      >
        {/* Loading skeleton */}
        {showSkeleton && (
          <div
            className={cn(
              "absolute inset-0 animate-pulse bg-gradient-to-r from-gray-200 via-gray-100 to-gray-200 dark:from-gray-700 dark:via-gray-800 dark:to-gray-700",
              roundedClasses[rounded]
            )}
          />
        )}

        {/* Actual image */}
        {currentSrc && (
          <img
            ref={ref}
            src={currentSrc}
            alt={alt}
            onLoad={handleLoad}
            onError={handleError}
            className={cn(
              "h-full w-full transition-opacity duration-300",
              fitClasses[fit],
              roundedClasses[rounded],
              loadingState === "loaded" ? "opacity-100" : "opacity-0",
              className
            )}
            loading={lazy ? "lazy" : "eager"}
            decoding="async"
            {...props}
          />
        )}

        {/* Error state */}
        {loadingState === "error" && (
          <div
            className={cn(
              "absolute inset-0 flex items-center justify-center bg-gray-100 text-gray-400 dark:bg-gray-800 dark:text-gray-600",
              roundedClasses[rounded]
            )}
          >
            <svg
              className="h-8 w-8"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
        )}
      </div>
    );
  }
);

Image.displayName = "Image";

/**
 * Product Image component with preset styles for product cards
 */
export interface ProductImageProps extends Omit<ImageProps, "rounded" | "fit"> {
  /** Size preset */
  size?: "sm" | "md" | "lg" | "xl";
}

export function ProductImage({
  size = "md",
  aspectRatio = "1/1",
  className,
  ...props
}: ProductImageProps) {
  const sizeClasses = {
    sm: "h-16 w-16",
    md: "h-24 w-24",
    lg: "h-32 w-32",
    xl: "h-48 w-48",
  };

  return (
    <Image
      aspectRatio={aspectRatio}
      rounded="lg"
      fit="cover"
      wrapperClassName={cn(sizeClasses[size], className)}
      {...props}
    />
  );
}

/**
 * Avatar Image component with circular styling
 */
export interface AvatarImageProps extends Omit<ImageProps, "rounded" | "aspectRatio"> {
  /** Size in pixels */
  size?: number;
}

export function AvatarImage({
  size = 40,
  fallback = "/default-avatar.png",
  className,
  wrapperClassName,
  ...props
}: AvatarImageProps) {
  return (
    <Image
      aspectRatio="1/1"
      rounded="full"
      fit="cover"
      fallback={fallback}
      wrapperClassName={cn(wrapperClassName)}
      className={className}
      style={{ width: size, height: size }}
      {...props}
    />
  );
}

/**
 * Banner/Hero Image component with wide aspect ratio
 */
export interface BannerImageProps extends Omit<ImageProps, "aspectRatio"> {
  /** Aspect ratio preset */
  ratio?: "wide" | "ultrawide" | "cinema";
}

export function BannerImage({
  ratio = "wide",
  rounded = "xl",
  ...props
}: BannerImageProps) {
  const ratios = {
    wide: "16/9",
    ultrawide: "21/9",
    cinema: "2.35/1",
  };

  return <Image aspectRatio={ratios[ratio]} rounded={rounded} {...props} />;
}
