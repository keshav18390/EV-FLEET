"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Wrench } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card, LoadingState, ErrorState, EmptyState, Pagination } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Paginated, MaintenanceRecord } from "@/lib/types";

export default function MaintenancePage() {
  const [page, setPage] = useState(1);
  const pageSize = 15;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["maintenance-all", page],
    queryFn: async () =>
      (await api.get<Paginated<MaintenanceRecord>>("/api/maintenance", { params: { page, page_size: pageSize } })).data,
  });

  return (
    <>
      <Topbar title="Maintenance Records" />
      <main className="p-4 lg:p-8 space-y-4">
        <Card>
          {isLoading ? (
            <LoadingState />
          ) : isError ? (
            <ErrorState message={friendlyError(error)} />
          ) : !data || data.items.length === 0 ? (
            <EmptyState message="No maintenance records found." />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-slate-500 border-b border-slate-200 dark:border-slate-800">
                      <th className="px-4 py-3 font-medium">Vehicle ID</th>
                      <th className="px-4 py-3 font-medium">Type</th>
                      <th className="px-4 py-3 font-medium">Description</th>
                      <th className="px-4 py-3 font-medium">Cost</th>
                      <th className="px-4 py-3 font-medium">Odometer</th>
                      <th className="px-4 py-3 font-medium">Date</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((m) => (
                      <tr key={m.id} className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/40">
                        <td className="px-4 py-3 text-slate-700 dark:text-slate-300">#{m.vehicle_id}</td>
                        <td className="px-4 py-3 capitalize flex items-center gap-1.5">
                          <Wrench size={13} className="text-slate-400" /> {m.maintenance_type.replace("_", " ")}
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{m.description}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">Rs. {m.cost.toLocaleString()}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                          {Math.round(m.odometer_at_service).toLocaleString()} km
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                          {new Date(m.performed_at).toLocaleDateString()}
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
