"use client";

type StyleTheme = "modern" | "gaming" | "corporate" | "fun";

const THEMES: { value: StyleTheme; label: string; desc: string; emoji: string; colors: string }[] = [
  {
    value: "modern",
    label: "Modern",
    desc: "Klean, minimalistisch, zeitgemäß. Ideal für Productivity & Tools.",
    emoji: "⚡",
    colors: "from-indigo-900 to-slate-900",
  },
  {
    value: "gaming",
    label: "Gaming",
    desc: "Energiegeladen, Neon-Effekte, actionreich. Für Games & Entertainment.",
    emoji: "🎮",
    colors: "from-cyan-900 to-slate-900",
  },
  {
    value: "corporate",
    label: "Corporate",
    desc: "Professionell, vertrauenswürdig. Für B2B & Business-Apps.",
    emoji: "💼",
    colors: "from-blue-900 to-slate-900",
  },
  {
    value: "fun",
    label: "Fun",
    desc: "Lebendig, bunt, verspielt. Für Social, Kids & Lifestyle-Apps.",
    emoji: "🎉",
    colors: "from-purple-900 to-amber-900",
  },
];

type Props = {
  value: StyleTheme;
  onChange: (v: StyleTheme) => void;
  onNext: () => void;
  onBack: () => void;
};

export function StepStyleSelect({ value, onChange, onNext, onBack }: Props) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-white mb-6">Video-Style wählen</h2>

      <div className="grid grid-cols-2 gap-4">
        {THEMES.map((theme) => (
          <button
            key={theme.value}
            onClick={() => onChange(theme.value)}
            className={`text-left rounded-xl p-5 border-2 transition-all bg-gradient-to-br ${theme.colors} ${
              value === theme.value
                ? "border-indigo-500 ring-4 ring-indigo-500/20 scale-[1.02]"
                : "border-slate-700 hover:border-slate-500"
            }`}
          >
            <div className="text-3xl mb-3">{theme.emoji}</div>
            <p className="font-bold text-white">{theme.label}</p>
            <p className="text-slate-300 text-sm mt-1">{theme.desc}</p>
          </button>
        ))}
      </div>

      <div className="flex justify-between pt-2">
        <button onClick={onBack} className="text-slate-400 hover:text-white px-6 py-3 rounded-lg transition-colors">
          ← Zurück
        </button>
        <button
          onClick={onNext}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-8 py-3 rounded-lg font-medium transition-colors"
        >
          Weiter →
        </button>
      </div>
    </div>
  );
}
