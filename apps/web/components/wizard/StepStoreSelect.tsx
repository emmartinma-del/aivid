"use client";

type TargetStore = "ios" | "android" | "both";

const STORES: { value: TargetStore; label: string; desc: string; emoji: string }[] = [
  { value: "ios", label: "App Store (iOS)", desc: "iPhone & iPad · max. 30 Sek. · H.264", emoji: "" },
  { value: "android", label: "Google Play (Android)", desc: "Android · max. 2 Min. · H.264", emoji: "🤖" },
  { value: "both", label: "Beide Stores", desc: "iOS + Android – je ein optimiertes Video", emoji: "🌍" },
];

type Props = {
  value: TargetStore;
  onChange: (v: TargetStore) => void;
  onNext: () => void;
  onBack: () => void;
};

export function StepStoreSelect({ value, onChange, onNext, onBack }: Props) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-white mb-6">Ziel-Store wählen</h2>

      <div className="space-y-3">
        {STORES.map((store) => (
          <button
            key={store.value}
            onClick={() => onChange(store.value)}
            className={`w-full text-left rounded-xl p-5 border-2 transition-all ${
              value === store.value
                ? "border-indigo-500 bg-indigo-500/10 ring-4 ring-indigo-500/10"
                : "border-slate-700 hover:border-slate-500 bg-slate-800/50"
            }`}
          >
            <div className="flex items-center gap-4">
              <span className="text-3xl">{store.emoji}</span>
              <div>
                <p className="font-bold text-white">{store.label}</p>
                <p className="text-slate-400 text-sm">{store.desc}</p>
              </div>
              <div className="ml-auto">
                <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                  value === store.value ? "border-indigo-500 bg-indigo-500" : "border-slate-600"
                }`}>
                  {value === store.value && <div className="w-2 h-2 rounded-full bg-white" />}
                </div>
              </div>
            </div>
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
