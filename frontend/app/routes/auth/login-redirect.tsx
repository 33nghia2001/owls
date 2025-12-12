import { redirect, type LoaderFunctionArgs } from "react-router";

// Redirect /login to /auth/login for backward compatibility
export async function loader({ request }: LoaderFunctionArgs) {
  throw redirect("/auth/login", { status: 301 });
}
