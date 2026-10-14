import { CalendarDays, Filter, Layers3, Sigma } from "lucide-react";

export type AnalysisState = {
  metrics?: string[];
  time_range?: string | null;
  dimensions?: string[];
  filters?: string[];
  sort?: string | null;
  limit?: number | null;
};

const rows = [
  { key: "metrics", label: "指标", icon: Sigma },
  { key: "time_range", label: "时间", icon: CalendarDays },
  { key: "dimensions", label: "维度", icon: Layers3 },
  { key: "filters", label: "筛选", icon: Filter },
] as const;

export function AnalysisStatePanel({ state }: { state: AnalysisState }) {
  return (
    <section className="border border-ink/10 bg-white/50 p-4">
      <div className="mb-3 text-xs font-semibold uppercase tracking-[0.16em] text-ink/45">连续分析状态</div>
      <div className="space-y-3">
        {rows.map(({ key, label, icon: Icon }) => {
          const raw = state[key];
          const values = Array.isArray(raw) ? raw : raw ? [raw] : [];
          return (
            <div key={key} className="grid grid-cols-[18px_44px_minmax(0,1fr)] items-start gap-2 text-xs">
              <Icon className="mt-0.5 h-3.5 w-3.5 text-moss" aria-hidden="true" />
              <span className="text-ink/50">{label}</span>
              <div className="flex flex-wrap gap-1">
                {values.length ? values.map((value) => <span key={value} className="bg-moss/10 px-1.5 py-0.5 text-moss">{value}</span>) : <span className="text-ink/35">未设置</span>}
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
