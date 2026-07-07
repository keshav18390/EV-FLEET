"use client";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Search, Download, BatteryMedium } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState, EmptyState, Pagination } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Paginated, Vehicle } from "@/lib/types";

const STATUS_COLORS: Record<string, string> = {
  active: "green",
  charging: "blue",
  maintenance: "amber",
  idle: "slate",
  out_of_service: "red",
};

export default function VehiclesPage() {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["vehicles", search, status, page],
    queryFn: async () => {
      const params: Record<string, any> = { page, page_size: pageSize };
      if (search) params.search = search;
      if (status) params.status = status;
      const resp = await api.get<Paginated<Vehicle>>("/api/vehicles", { params });
      return resp.data;
    },
  });

  async function downloadCsv() {
    const resp = await api.get("/api/reports/vehicles/csv", { responseType: "blob" });
    const url = window.URL.createObjectURL(new Blob([resp.data]));
    const a = document.createElement("a");
    a.href = url;
    a.download = "vehicles_report.csv";
    a.click();
    window.URL.revokeObjectURL(url);
  }

  return (
    <>
      <Topbar title="Vehicles" />
      <main className="p-4 lg:p-8 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
          <div className="flex flex-1 gap-3 flex-col sm:flex-row">
            <div className="relative flex-1 max-w-sm">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={16} />
              <input
                value={search}
                onChange={(e) => {
                  setPage(1);
                  setSearch(e.target.value);
                }}
                placeholder="Search registration or model..."
                className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <select
              value={status}
              onChange={(e) => {
                setPage(1);
                setStatus(e.target.value);
              }}
              className="px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All statuses</option>
              <option value="active">Active</option>
              <option value="charging">Charging</option>
              <option value="maintenance">Maintenance</option>
              <option value="idle">Idle</option>
              <option value="out_of_service">Out of service</option>
            </select>
          </div>
          <button
            onClick={downloadCsv}
            className="flex items-center gap-2 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-700 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800"
          >
            <Download size={16} /> Export CSV
          </button>
        </div>

        <Card>
          {isLoading ? (
            <LoadingState label="Loading vehicles..." />
          ) : isError ? (
            <ErrorState message={friendlyError(error)} />
          ) : !data || data.items.length === 0 ? (
            <EmptyState message="No vehicles match your filters." />
          ) : (
            <>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="text-left text-slate-500 border-b border-slate-200 dark:border-slate-800">
                      <th className="px-4 py-3 font-medium">Registration</th>
                      <th className="px-4 py-3 font-medium">Model</th>
                      <th className="px-4 py-3 font-medium">City</th>
                      <th className="px-4 py-3 font-medium">Status</th>
                      <th className="px-4 py-3 font-medium">Battery</th>
                      <th className="px-4 py-3 font-medium">Health Score</th>
                      <th className="px-4 py-3 font-medium">Odometer</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.items.map((v) => (
                      <tr
                        key={v.id}
                        className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-50 dark:hover:bg-slate-800/40"
                      >
                        <td className="px-4 py-3">
                          <Link href={`/vehicles/${v.id}`} className="font-medium text-brand-700 dark:text-brand-400 hover:underline">
                            {v.registration_number}
                          </Link>
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{v.model}</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{v.city}</td>
                        <td className="px-4 py-3">
                          <Badge color={STATUS_COLORS[v.status] || "slate"}>{v.status.replace("_", " ")}</Badge>
                        </td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center gap-1.5">
                            <BatteryMedium
                              size={14}
                              className={v.battery_level < 20 ? "text-red-500" : "text-slate-400"}
                            />
                            {v.battery_level}%
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{v.fleet_health_score}/100</td>
                        <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                          {Math.round(v.odometer_km).toLocaleString()} km
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
