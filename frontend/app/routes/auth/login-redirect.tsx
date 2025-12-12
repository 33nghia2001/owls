import { redirect, type ClientLoaderFunctionArgs } from "react-router";

// Redirect /login to /auth/login for backward compatibility
export async function clientLoader({ request }: ClientLoaderFunctionArgs) {
  throw redirect("/auth/login", { status: 301 });
}
