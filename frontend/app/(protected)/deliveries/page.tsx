"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState, EmptyState, Pagination } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Paginated, Delivery } from "@/lib/types";

const STATUS_COLORS: Record<string, string> = {
  completed: "green",
  delayed: "amber",
  cancelled: "red",
  in_progress: "blue",
};

export default function DeliveriesPage() {
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["deliveries", status, page],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: pageSize };
      if (status) params.status = status;
      return (await api.get<Paginated<Delivery>>("/api/deliveries", { params })).data;
    },
  });

  return (
    <>
      <Topbar title="Deliveries" />
      <main className="p-4 lg:p-8 space-y-4">
        <select
          value={status}
          onChange={(e) => {
            setPage(1);
            setStatus(e.target.value);
          }}
          className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
        >
          <option value="">All statuses</option>
          <option value="completed">Completed</option>
          <option value="delayed">Delayed</option>
          <option value="cancelled">Cancelled</option>
          <option value="in_progress">In Progress</option>
        </select>

        <Card>
          {isLoading ? (
            <LoadingState />
          ) : isError ? (
            <ErrorState message={friendlyError(error)} />
          ) : !data || data.items.length === 0 ? (
            <EmptyState message="No deliveries found." />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-slate-500 border-b border-slate-200 dark:border-slate-800">
                      <th className="px-4 py-3 font-medium">#</th>
                      <th className="px-4 py-3 font-medium">Route</th>
                      <th className="px-4 py-3 font-medium">Distance</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                      <th className="px-4 py-3 font-medium">Delay</th>
                      <th className="px-4 py-3 font-medium">Scheduled</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((d) => (
                      <tr key={d.id} className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-3 text-slate-500">#{d.id}</td>
                        <td className="px-4 py-3 text-slate-700 dark:text-slate-300">
                          {d.pickup_area} &rarr; {d.drop_area}
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{d.distance_km} km</td>
                        <td className="px-4 py-3">
                          <Badge color={STATUS_COLORS[d.status] || "slate"}>{d.status.replace("_", " ")}</Badge>
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                          {d.delay_minutes > 0 ? `${Math.round(d.delay_minutes)} min` : "-"}
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                          {new Date(d.scheduled_time).toLocaleString()}
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
