"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Search, Star } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState, EmptyState, Pagination } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Paginated, Rider } from "@/lib/types";

const STATUS_COLORS: Record<string, string> = {
  active: "green",
  on_trip: "blue",
  offline: "slate",
  suspended: "red",
};

export default function RidersPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["riders", search, page],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: pageSize };
      if (search) params.search = search;
      return (await api.get<Paginated<Rider>>("/api/riders", { params })).data;
    },
  });

  return (
    <>
      <Topbar title="Riders" />
      <main className="p-4 lg:p-8 space-y-4">
        <div className="relative max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
          <input
            value={search}
            onChange={(e) => {
              setPage(1);
              setSearch(e.target.value);
            }}
            placeholder="Search by name or phone..."
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>

        <Card>
          {isLoading ? (
            <LoadingState />
          ) : isError ? (
            <ErrorState message={friendlyError(error)} />
          ) : !data || data.items.length === 0 ? (
            <EmptyState message="No riders match your search." />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-slate-500 border-b border-slate-200 dark:border-slate-800">
                      <th className="px-4 py-3 font-medium">Name</th>
                      <th className="px-4 py-3 font-medium">City</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                      <th className="px-4 py-3 font-medium">Rating</th>
                      <th className="px-4 py-3 font-medium">Deliveries</th>
                      <th className="px-4 py-3 font-medium">On-Time Rate</th>
                      <th className="px-4 py-3 font-medium">Performance</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((r) => (
                      <tr key={r.id} className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{r.full_name}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{r.city}</td>
                        <td className="px-4 py-3">
                          <Badge color={STATUS_COLORS[r.status] || "slate"}>{r.status.replace("_", " ")}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1">
                            <Star size={13} className="text-amber-400 fill-amber-400" /> {r.rating}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{r.total_deliveries}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{r.on_time_rate}%</td>
                        <td className="px-4 py-3">
                          <Badge color={r.performance_score < 50 ? "red" : r.performance_score < 75 ? "amber" : "green"}>
                            {r.performance_score}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <Pagination page={page} pageSize={pageSize} total={data.total} onPageChange={setPage} />
            </>
          )}
        </Card>
      </main>
    </>
  );
}
