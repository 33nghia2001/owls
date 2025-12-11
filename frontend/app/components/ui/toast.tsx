"use client";

import { Toaster as HotToaster, toast as hotToast } from "react-hot-toast";
import {
  CheckCircle2,
  XCircle,
  AlertCircle,
  Info,
  X,
} from "lucide-react";

export function Toaster() {
  return (
    <HotToaster
      position="top-right"
      gutter={12}
      containerStyle={{
        top: 80,
      }}
      toastOptions={{
        duration: 4000,
        style: {
          background: "white",
          color: "#1f2937",
          padding: "16px",
          borderRadius: "12px",
          boxShadow: "0 10px 40px -10px rgba(0, 0, 0, 0.2)",
          maxWidth: "400px",
        },
      }}
    />
  );
}

interface ToastOptions {
  title?: string;
  description: string;
  duration?: number;
}

export const toast = {
  success: ({ title, description, duration = 4000 }: ToastOptions) => {
    hotToast.custom(
      (t) => (
        <div
          className={`${
            t.visible ? "animate-enter" : "animate-leave"
          } flex w-full max-w-md items-start gap-3 rounded-xl bg-white p-4 shadow-lg ring-1 ring-black/5`}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-green-100">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
          </div>
          <div className="flex-1">
            {title && (
              <p className="font-semibold text-gray-900">{title}</p>
            )}
            <p className="text-sm text-gray-600">{description}</p>
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ),
      { duration }
    );
  },

  error: ({ title, description, duration = 5000 }: ToastOptions) => {
    hotToast.custom(
      (t) => (
        <div
          className={`${
            t.visible ? "animate-enter" : "animate-leave"
          } flex w-full max-w-md items-start gap-3 rounded-xl bg-white p-4 shadow-lg ring-1 ring-black/5`}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-red-100">
            <XCircle className="h-5 w-5 text-red-600" />
          </div>
          <div className="flex-1">
            {title && (
              <p className="font-semibold text-gray-900">{title}</p>
            )}
            <p className="text-sm text-gray-600">{description}</p>
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ),
      { duration }
    );
  },

  warning: ({ title, description, duration = 4000 }: ToastOptions) => {
    hotToast.custom(
      (t) => (
        <div
          className={`${
            t.visible ? "animate-enter" : "animate-leave"
          } flex w-full max-w-md items-start gap-3 rounded-xl bg-white p-4 shadow-lg ring-1 ring-black/5`}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-yellow-100">
            <AlertCircle className="h-5 w-5 text-yellow-600" />
          </div>
          <div className="flex-1">
            {title && (
              <p className="font-semibold text-gray-900">{title}</p>
            )}
            <p className="text-sm text-gray-600">{description}</p>
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ),
      { duration }
    );
  },

  info: ({ title, description, duration = 4000 }: ToastOptions) => {
    hotToast.custom(
      (t) => (
        <div
          className={`${
            t.visible ? "animate-enter" : "animate-leave"
          } flex w-full max-w-md items-start gap-3 rounded-xl bg-white p-4 shadow-lg ring-1 ring-black/5`}
        >
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-blue-100">
            <Info className="h-5 w-5 text-blue-600" />
          </div>
          <div className="flex-1">
            {title && (
              <p className="font-semibold text-gray-900">{title}</p>
            )}
            <p className="text-sm text-gray-600">{description}</p>
          </div>
          <button
            onClick={() => hotToast.dismiss(t.id)}
            className="rounded-lg p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ),
      { duration }
    );
  },

  promise: <T,>(
    promise: Promise<T>,
    {
      loading,
      success,
      error,
    }: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((err: unknown) => string);
    }
  ) => {
    return hotToast.promise(promise, {
      loading,
      success,
      error,
    });
  },

  dismiss: (toastId?: string) => {
    hotToast.dismiss(toastId);
  },
};
