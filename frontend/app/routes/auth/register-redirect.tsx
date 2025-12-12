import { redirect } from "react-router";

// Redirect /register to /auth/register for backward compatibility
export function clientLoader() {
  return redirect("/auth/register", { status: 301 });
}

export default function RegisterRedirect() {
  return null;
}
