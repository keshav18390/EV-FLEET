"use client";

import { useQuery } from "@tanstack/react-query";
import { BatteryWarning, BatteryMedium } from "lucide-react";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState, EmptyState } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Vehicle } from "@/lib/types";
import { ResponsiveContainer, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ZAxis } from "recharts";
import Link from "next/link";

export default function BatteryAnalyticsPage() {
  const lowBatteryQuery = useQuery({
    queryKey: ["low-battery"],
    queryFn: async () => (await api.get<Vehicle[]>("/api/vehicles/low-battery/list", { params: { threshold: 20 } })).data,
  });

  const allVehiclesQuery = useQuery({
    queryKey: ["all-vehicles-battery"],
    queryFn: async () => (await api.get("/api/vehicles?page=1&page_size=200")).data.items as Vehicle[],
  });

  const degrading = (allVehiclesQuery.data || []).filter((v) => v.battery_health < 75);

  return (
    <>
      <Topbar title="Battery Analytics" />
      <main className="p-4 lg:p-8 space-y-6">
        <Card className="p-5">
          <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">
            Battery Health vs. Charge Cycles
          </h2>
          {allVehiclesQuery.isLoading ? (
            <LoadingState />
          ) : (
            <ResponsiveContainer width="100%" height={320}>
              <ScatterChart>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-800" />
                <XAxis type="number" dataKey="total_charge_cycles" name="Charge Cycles" tick={{ fontSize: 12 }} />
                <YAxis type="number" dataKey="battery_health" name="Battery Health %" tick={{ fontSize: 12 }} />
                <ZAxis range={[60, 60]} />
                <Tooltip cursor={{ strokeDasharray: "3 3" }} />
                <Scatter data={allVehiclesQuery.data || []} fill="#22a571" />
              </ScatterChart>
            </ResponsiveContainer>
          )}
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card>
            <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
              <BatteryWarning size={16} className="text-red-500" />
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Low Battery (below 20%)</h3>
            </div>
            {lowBatteryQuery.isLoading ? (
              <LoadingState />
            ) : lowBatteryQuery.isError ? (
              <ErrorState message={friendlyError(lowBatteryQuery.error)} />
            ) : lowBatteryQuery.data && lowBatteryQuery.data.length > 0 ? (
              <ul className="divide-y divide-slate-100 dark:divide-slate-800">
                {lowBatteryQuery.data.map((v) => (
                  <li key={v.id} className="px-5 py-3 flex items-center justify-between text-sm">
                    <Link href={`/vehicles/${v.id}`} className="font-medium text-brand-700 dark:text-brand-400 hover:underline">
                      {v.registration_number}
                    </Link>
                    <Badge color="red">{v.battery_level}%</Badge>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState message="No vehicles currently below 20% battery." />
            )}
          </Card>

          <Card>
            <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center gap-2">
              <BatteryMedium size={16} className="text-amber-500" />
              <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Degrading Battery Health (below 75%)</h3>
            </div>
            {allVehiclesQuery.isLoading ? (
              <LoadingState />
            ) : degrading.length > 0 ? (
              <ul className="divide-y divide-slate-100 dark:divide-slate-800">
                {degrading.map((v) => (
                  <li key={v.id} className="px-5 py-3 flex items-center justify-between text-sm">
                    <Link href={`/vehicles/${v.id}`} className="font-medium text-brand-700 dark:text-brand-400 hover:underline">
                      {v.registration_number}
                    </Link>
                    <Badge color="amber">{v.battery_health}% SoH</Badge>
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState message="No vehicles with degrading battery health." />
            )}
          </Card>
        </div>
      </main>
    </>
  );
}
