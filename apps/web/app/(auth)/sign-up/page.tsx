"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function SignUpPage() {
  const router = useRouter();
  const [form, setForm] = useState({ fullName: "", email: "", password: "", organizationName: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        email: form.email,
        password: form.password,
        full_name: form.fullName,
        organization_name: form.organizationName || undefined,
      }),
    });

    if (!res.ok) {
      const data = await res.json();
      setError(data.detail || "Registrierung fehlgeschlagen.");
      setLoading(false);
      return;
    }

    // Auto sign-in after registration
    await signIn("credentials", { email: form.email, password: form.password, redirect: false });
    router.push("/dashboard");
  }

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-8">
        <Link href="/" className="text-indigo-400 font-bold text-xl block mb-8">AIvid</Link>
        <h1 className="text-2xl font-bold text-white mb-2">Konto erstellen</h1>
        <p className="text-slate-400 mb-8">Kostenlos – kein Abo erforderlich.</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium text-slate-300 block mb-1.5">Name</label>
            <input
              type="text"
              value={form.fullName}
              onChange={set("fullName")}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-300 block mb-1.5">E-Mail</label>
            <input
              type="email"
              value={form.email}
              onChange={set("email")}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-300 block mb-1.5">Passwort</label>
            <input
              type="password"
              value={form.password}
              onChange={set("password")}
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              required
              minLength={8}
            />
          </div>
          <div>
            <label className="text-sm font-medium text-slate-300 block mb-1.5">Firma / Agentur (optional)</label>
            <input
              type="text"
              value={form.organizationName}
              onChange={set("organizationName")}
              placeholder="z.B. Acme Studio GmbH"
              className="w-full bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {error && <p className="text-red-400 text-sm">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors"
          >
            {loading ? "Konto wird erstellt…" : "Kostenlos registrieren"}
          </button>
        </form>

        <p className="text-slate-400 text-sm text-center mt-6">
          Bereits registriert?{" "}
          <Link href="/sign-in" className="text-indigo-400 hover:underline">Anmelden</Link>
        </p>
      </div>
    </div>
  );
}
