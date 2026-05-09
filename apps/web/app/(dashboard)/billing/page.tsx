"use client";

import { useQuery } from "@tanstack/react-query";
import { api } from "@/lib/api-client";
import { CreditCard, CheckCircle, Loader2 } from "lucide-react";

const TIER_INFO: Record<string, { label: string; price: string; limit: string; color: string }> = {
  free:    { label: "Free",    price: "CHF 0",   limit: "1 Video/Monat",        color: "border-slate-700" },
  starter: { label: "Starter", price: "CHF 29",  limit: "5 Videos/Monat",       color: "border-indigo-500" },
  pro:     { label: "Pro",     price: "CHF 79",  limit: "20 Videos/Monat",      color: "border-indigo-400" },
  agency:  { label: "Agency",  price: "CHF 249", limit: "Unbegrenzte Videos",   color: "border-purple-500" },
};

const UPGRADE_TIERS = [
  { key: "starter", features: ["Kein Wasserzeichen", "Alle Stile", "5 Videos/Monat"] },
  { key: "pro",     features: ["Priority Queue", "Alle Features", "20 Videos/Monat"] },
  { key: "agency",  features: ["White-Label", "Team-Konten", "Batch-Generierung", "Unbegrenzt"] },
];

export default function BillingPage() {
  const { data: sub, isLoading } = useQuery({
    queryKey: ["subscription"],
    queryFn: () => api.getSubscription(),
  });

  const tierInfo = sub ? (TIER_INFO[sub.tier] ?? TIER_INFO.free) : null;

  return (
    <div className="p-8 max-w-3xl">
      <h1 className="text-2xl font-bold text-white mb-8">Abonnement</h1>

      {isLoading && (
        <div className="flex items-center gap-3 text-slate-400 py-8">
          <Loader2 size={18} className="animate-spin" />
          Lade Plan…
        </div>
      )}

      {tierInfo && sub && (
        <div className={`bg-slate-900 border-2 ${tierInfo.color} rounded-xl p-6 mb-8`}>
          <div className="flex items-start justify-between">
            <div>
              <p className="text-slate-400 text-sm mb-1">Aktueller Plan</p>
              <p className="text-3xl font-bold text-white">{tierInfo.label}</p>
              <p className="text-slate-400 mt-1">{tierInfo.limit}</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-white">{tierInfo.price}</p>
              <p className="text-slate-500 text-sm">pro Monat</p>
            </div>
          </div>

          <div className="mt-6 pt-5 border-t border-slate-800">
            <div className="flex items-center justify-between text-sm">
              <span className="text-slate-400">Videos diesen Monat</span>
              <span className="text-white font-medium">
                {sub.videos_used} / {sub.videos_limit === 9999 ? "∞" : sub.videos_limit}
              </span>
            </div>
            <div className="mt-2 h-2 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-600 rounded-full transition-all"
                style={{ width: `${Math.min(100, (sub.videos_used / (sub.videos_limit || 1)) * 100)}%` }}
              />
            </div>
          </div>

          {sub.period_end && (
            <p className="text-slate-500 text-xs mt-4">
              Nächste Abrechnung: {new Date(sub.period_end).toLocaleDateString("de-CH")}
            </p>
          )}
        </div>
      )}

      {sub?.tier === "free" && (
        <>
          <h2 className="text-lg font-bold text-white mb-4">Upgraden</h2>
          <div className="grid gap-4">
            {UPGRADE_TIERS.map((t) => {
              const info = TIER_INFO[t.key];
              return (
                <div key={t.key} className="bg-slate-900 border border-slate-800 rounded-xl p-5 flex items-center gap-6">
                  <div className="flex-1">
                    <div className="flex items-baseline gap-2 mb-2">
                      <p className="text-white font-bold text-lg">{info.label}</p>
                      <p className="text-slate-400 text-sm">{info.price}/Monat</p>
                    </div>
                    <ul className="space-y-1">
                      {t.features.map((f) => (
                        <li key={f} className="flex items-center gap-2 text-sm text-slate-300">
                          <CheckCircle size={14} className="text-green-400 shrink-0" />
                          {f}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <a
                    href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscriptions/checkout`}
                    className="shrink-0 flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-colors"
                  >
                    <CreditCard size={16} />
                    Upgraden
                  </a>
                </div>
              );
            })}
          </div>
        </>
      )}

      {sub && sub.tier !== "free" && (
        <a
          href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscriptions/portal`}
          className="inline-flex items-center gap-2 border border-slate-700 hover:border-slate-500 text-slate-300 hover:text-white px-5 py-2.5 rounded-lg font-medium text-sm transition-colors"
        >
          <CreditCard size={16} />
          Billing-Portal öffnen
        </a>
      )}
    </div>
  );
}
