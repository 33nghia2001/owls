"use client";

import { motion, type HTMLMotionProps } from "framer-motion";
import { cn } from "~/lib/utils";
import * as React from "react";

export interface CardProps extends HTMLMotionProps<"div"> {
  variant?: "default" | "elevated" | "bordered" | "ghost";
  hover?: boolean;
}

const cardVariants = {
  default: "bg-white dark:bg-gray-900",
  elevated: "bg-white dark:bg-gray-900 shadow-lg",
  bordered: "bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800",
  ghost: "bg-transparent",
};

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant = "bordered", hover = false, children, ...props }, ref) => (
    <motion.div
      ref={ref}
      className={cn(
        "rounded-2xl overflow-hidden",
        cardVariants[variant],
        hover && "transition-all duration-300 hover:shadow-xl hover:-translate-y-1",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      {...props}
    >
      {children}
    </motion.div>
  )
);
Card.displayName = "Card";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-xl font-semibold leading-none tracking-tight text-gray-900 dark:text-white",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-gray-500 dark:text-gray-400", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
