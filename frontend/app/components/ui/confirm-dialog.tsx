"use client";

import * as React from "react";
import { AlertTriangle, Trash2, Info } from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./dialog";
import { Button } from "./button";
import { cn } from "~/lib/utils";

export type ConfirmVariant = "danger" | "warning" | "info";

interface ConfirmDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: ConfirmVariant;
  onConfirm: () => void | Promise<void>;
  isLoading?: boolean;
}

const variantConfig: Record<ConfirmVariant, { icon: typeof AlertTriangle; iconClass: string; buttonClass: string }> = {
  danger: {
    icon: Trash2,
    iconClass: "text-red-500 bg-red-100 dark:bg-red-900/30",
    buttonClass: "bg-red-500 hover:bg-red-600 text-white",
  },
  warning: {
    icon: AlertTriangle,
    iconClass: "text-yellow-500 bg-yellow-100 dark:bg-yellow-900/30",
    buttonClass: "bg-yellow-500 hover:bg-yellow-600 text-white",
  },
  info: {
    icon: Info,
    iconClass: "text-blue-500 bg-blue-100 dark:bg-blue-900/30",
    buttonClass: "bg-blue-500 hover:bg-blue-600 text-white",
  },
};

export function ConfirmDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmText = "Xác nhận",
  cancelText = "Hủy",
  variant = "danger",
  onConfirm,
  isLoading = false,
}: ConfirmDialogProps) {
  const config = variantConfig[variant];
  const Icon = config.icon;

  const handleConfirm = async () => {
    await onConfirm();
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader className="flex flex-col items-center text-center sm:items-start sm:text-left">
          <div className={cn("mb-4 flex h-12 w-12 items-center justify-center rounded-full", config.iconClass)}>
            <Icon className="h-6 w-6" />
          </div>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription className="mt-2">{description}</DialogDescription>
        </DialogHeader>
        <DialogFooter className="mt-4 flex gap-3 sm:gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
            className="flex-1 sm:flex-none"
          >
            {cancelText}
          </Button>
          <Button
            type="button"
            onClick={handleConfirm}
            disabled={isLoading}
            className={cn("flex-1 sm:flex-none", config.buttonClass)}
          >
            {isLoading ? "Đang xử lý..." : confirmText}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

// Hook for easier usage
interface UseConfirmOptions {
  title: string;
  description: string;
  confirmText?: string;
  cancelText?: string;
  variant?: ConfirmVariant;
}

export function useConfirm() {
  const [state, setState] = React.useState<{
    open: boolean;
    options: UseConfirmOptions | null;
    resolve: ((value: boolean) => void) | null;
  }>({
    open: false,
    options: null,
    resolve: null,
  });

  const confirm = React.useCallback((options: UseConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      setState({ open: true, options, resolve });
    });
  }, []);

  const handleOpenChange = React.useCallback((open: boolean) => {
    if (!open && state.resolve) {
      state.resolve(false);
    }
    setState((prev) => ({ ...prev, open }));
  }, [state.resolve]);

  const handleConfirm = React.useCallback(() => {
    if (state.resolve) {
      state.resolve(true);
    }
    setState((prev) => ({ ...prev, open: false }));
  }, [state.resolve]);

  // Always return a valid React element (fragment if no options)
  const ConfirmDialogElement = state.options ? (
    <ConfirmDialog
      open={state.open}
      onOpenChange={handleOpenChange}
      title={state.options.title}
      description={state.options.description}
      confirmText={state.options.confirmText}
      cancelText={state.options.cancelText}
      variant={state.options.variant}
      onConfirm={handleConfirm}
    />
  ) : (
    <></>
  );

  return { confirm, ConfirmDialog: ConfirmDialogElement };
}
