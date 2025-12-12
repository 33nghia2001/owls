import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useLoaderData,
  type LoaderFunctionArgs,
} from "react-router";
import { useEffect } from "react";
import { QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

import "./app.css";
import { Header, Footer, CartSidebar } from "~/components/layout";
import { useAuthStore, useWishlistStore } from "~/lib/stores";
import { TooltipProvider } from "~/components/ui/tooltip";
import { Toaster } from "~/components/ui/toast";
import { queryClient } from "~/lib/query";
import { createApi, getGuestCartIdFromServerRequest } from "~/lib/api";
import { NotificationListener } from "~/components/notifications";
import type { User } from "~/lib/types";

export const links = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
  },
];

// --- Loader: Fetch user from server to prevent auth flicker ---
export async function loader({ request }: LoaderFunctionArgs) {
  const api = createApi(request);
  let user: User | null = null;
  
  try {
    const res = await api.get("/users/me/");
    user = res.data;
  } catch {
    // Not logged in or token expired - that's OK
  }
  
  // Also get guestCartId from cookie for SSR consistency
  const guestCartId = getGuestCartIdFromServerRequest(request);
  
  return { user, guestCartId };
}

export function Layout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export default function App() {
  const { user } = useLoaderData<typeof loader>();
  const { setUser, checkAuth } = useAuthStore();

  useEffect(() => {
    // Sync server-fetched user into store immediately to prevent flicker
    if (user) {
      setUser(user);
    } else {
      // Fallback: check auth client-side if server didn't return user
      checkAuth();
    }
    // Hydrate wishlist store to avoid SSR mismatch
    useWishlistStore.persist.rehydrate();
    // Fetch wishlist from server if user is authenticated
    if (user) {
      useWishlistStore.getState().fetchWishlist();
    }
  }, [user, setUser, checkAuth]);

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">
            <Outlet />
          </main>
          <Footer />
          <CartSidebar />
          <Toaster />
          <NotificationListener />
        </div>
      </TooltipProvider>
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  );
}

export function ErrorBoundary({ error }: { error: unknown }) {
  let message = "Oops!";
  let details = "An unexpected error occurred.";
  let stack: string | undefined;

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? "404" : "Error";
    details =
      error.status === 404
        ? "The requested page could not be found."
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <main className="pt-16 p-4 container mx-auto">
      <h1 className="text-2xl font-bold text-red-600 mb-2">{message}</h1>
      <p className="text-gray-600">{details}</p>
      {stack && (
        <pre className="w-full p-4 overflow-x-auto bg-gray-100 rounded mt-4 text-xs">
          <code>{stack}</code>
        </pre>
      )}
    </main>
  );
}