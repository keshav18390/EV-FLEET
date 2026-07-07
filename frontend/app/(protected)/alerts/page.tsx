"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle2, AlertCircle } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState, EmptyState, Pagination } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Paginated, AlertItem } from "@/lib/types";

const SEVERITY_COLORS: Record<string, string> = {
  low: "slate",
  medium: "blue",
  high: "amber",
  critical: "red",
};

export default function AlertsPage() {
  const [resolved, setResolved] = useState<string>("false");
  const [page, setPage] = useState(1);
  const pageSize = 15;
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["alerts", resolved, page],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: pageSize };
      if (resolved !== "") params.resolved = resolved === "true";
      return (await api.get<Paginated<AlertItem>>("/api/alerts", { params })).data;
    },
  });

  async function resolveAlert(id: number) {
    await api.post(`/api/alerts/${id}/resolve`);
    queryClient.invalidateQueries({ queryKey: ["alerts"] });
  }

  return (
    <>
      <Topbar title="Alerts" />
      <main className="p-4 lg:p-8 space-y-4">
        <select
          value={resolved}
          onChange={(e) => {
            setPage(1);
            setResolved(e.target.value);
          }}
          className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="false">Open alerts</option>
          <option value="true">Resolved alerts</option>
          <option value="">All alerts</option>
        </select>

        <Card>
          {isLoading ? (
            <LoadingState />
          ) : isError ? (
            <ErrorState message={friendlyError(error)} />
          ) : !data || data.items.length === 0 ? (
            <EmptyState message="No alerts to show." />
          ) : (
            <>
              <ul className="divide-y divide-slate-100 dark:divide-slate-800">
                {data.items.map((a) => (
                  <li key={a.id} className="px-5 py-4 flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3">
                      <AlertCircle
                        size={18}
                        className={a.severity === "critical" || a.severity === "high" ? "text-red-500 mt-0.5" : "text-amber-500 mt-0.5"}
                      />
                      <div>
                        <p className="text-sm text-slate-800 dark:text-slate-200">{a.message}</p>
                        <div className="flex items-center gap-2 mt-1.5">
                          <Badge color={SEVERITY_COLORS[a.severity]}>{a.severity}</Badge>
                          <span className="text-xs text-slate-500">{new Date(a.created_at).toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                    {!a.is_resolved && (
                      <button
                        onClick={() => resolveAlert(a.id)}
                        className="flex items-center gap-1.5 text-xs font-medium text-brand-700 dark:text-brand-400 hover:underline whitespace-nowrap"
                      >
                        <CheckCircle2 size={14} /> Resolve
                      </button>
                    )}
                  </li>
                ))}
              </ul>
              <Pagination page={page} pageSize={pageSize} total={data.total} onPageChange={setPage} />
            </>
          )}
        </Card>
      </main>
    </>
  );
}
