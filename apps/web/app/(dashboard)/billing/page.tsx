export default function BillingPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-white mb-8">Abonnement</h1>
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-6">
        <p className="text-slate-400 text-sm mb-1">Aktueller Plan</p>
        <p className="text-3xl font-bold text-white">Free</p>
        <p className="text-slate-400 mt-2">1 Video pro Monat inklusive</p>
      </div>
      <a
        href={`${process.env.NEXT_PUBLIC_API_URL}/api/v1/subscriptions/checkout`}
        className="inline-block bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-lg font-medium transition-colors"
      >
        Upgraden →
      </a>
    </div>
  );
}
