import Link from "next/link";

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
        <span className="text-2xl font-bold tracking-tight text-indigo-400">AIvid</span>
        <div className="flex items-center gap-6">
          <Link href="#features" className="text-slate-300 hover:text-white transition-colors">Features</Link>
          <Link href="#pricing" className="text-slate-300 hover:text-white transition-colors">Preise</Link>
          <Link href="/sign-in" className="text-slate-300 hover:text-white transition-colors">Anmelden</Link>
          <Link
            href="/sign-up"
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-lg font-medium transition-colors"
          >
            Kostenlos starten
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="text-center px-4 py-24 max-w-5xl mx-auto">
        <span className="inline-block bg-indigo-500/20 text-indigo-300 text-sm font-medium px-4 py-1.5 rounded-full mb-6">
          NEU – KI-Video-Generator für App Stores
        </span>
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 leading-tight">
          Mehr Downloads mit<br />
          <span className="text-indigo-400">professionellen</span> App-Videos
        </h1>
        <p className="text-xl text-slate-300 mb-10 max-w-2xl mx-auto">
          Generiere in Minuten ein App-Store-konformes Previewvideo – vollautomatisch per KI.
          Apps mit Videos werden bis zu 3× häufiger heruntergeladen.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/sign-up"
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-4 rounded-xl font-semibold text-lg transition-all hover:scale-105"
          >
            Jetzt kostenlos testen →
          </Link>
          <button className="border border-slate-600 hover:border-slate-400 text-slate-300 px-8 py-4 rounded-xl font-semibold text-lg transition-colors">
            Demo ansehen
          </button>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-24 px-4 max-w-6xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-16">Wie es funktioniert</h2>
        <div className="grid md:grid-cols-3 gap-8">
          {[
            {
              step: "01",
              title: "Screenshots hochladen",
              desc: "Lade deine App-Screenshots, das Icon und optional einen Gameplay-Clip hoch.",
            },
            {
              step: "02",
              title: "KI generiert alles",
              desc: "Claude erstellt das Skript, ElevenLabs den Voiceover, FFmpeg komponiert das Video.",
            },
            {
              step: "03",
              title: "Herunterladen & veröffentlichen",
              desc: "Dein Video ist App-Store-konform (H.264, korrekte Auflösung) – direkt hochladbar.",
            },
          ].map((f) => (
            <div key={f.step} className="bg-slate-800/50 border border-slate-700 rounded-2xl p-8">
              <span className="text-indigo-400 text-4xl font-black">{f.step}</span>
              <h3 className="text-xl font-bold mt-4 mb-3">{f.title}</h3>
              <p className="text-slate-400">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-24 px-4 max-w-5xl mx-auto">
        <h2 className="text-4xl font-bold text-center mb-4">Einfache Preise</h2>
        <p className="text-slate-400 text-center mb-16">Ohne versteckte Kosten. Monatlich kündbar.</p>
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { name: "Free", price: "CHF 0", videos: "1 Video/Monat", features: ["Wasserzeichen", "30-Tage-Ablauf"] },
            { name: "Starter", price: "CHF 29", videos: "5 Videos/Monat", features: ["Kein Wasserzeichen", "Alle Stile"] },
            { name: "Pro", price: "CHF 79", videos: "20 Videos/Monat", features: ["Priority Queue", "Alle Features"], highlight: true },
            { name: "Agency", price: "CHF 249", videos: "Unbegrenzt", features: ["White-Label", "Team-Konten", "Batch"] },
          ].map((plan) => (
            <div
              key={plan.name}
              className={`rounded-2xl p-6 border ${
                plan.highlight
                  ? "bg-indigo-600 border-indigo-500 scale-105"
                  : "bg-slate-800/50 border-slate-700"
              }`}
            >
              <h3 className="font-bold text-lg mb-1">{plan.name}</h3>
              <p className="text-3xl font-black mb-1">{plan.price}</p>
              <p className="text-sm text-slate-300 mb-4">{plan.videos}</p>
              <ul className="space-y-2 mb-6">
                {plan.features.map((f) => (
                  <li key={f} className="text-sm text-slate-300 flex gap-2">
                    <span className="text-green-400">✓</span> {f}
                  </li>
                ))}
              </ul>
              <Link
                href="/sign-up"
                className={`block text-center py-2.5 rounded-lg font-medium transition-colors ${
                  plan.highlight
                    ? "bg-white text-indigo-700 hover:bg-slate-100"
                    : "bg-indigo-600 text-white hover:bg-indigo-500"
                }`}
              >
                Starten
              </Link>
            </div>
          ))}
        </div>
      </section>

      <footer className="border-t border-slate-800 py-8 text-center text-slate-500 text-sm">
        © {new Date().getFullYear()} AIvid · app.aivid.ch
      </footer>
    </main>
  );
}
