"use client";

import { useQuery } from "@tanstack/react-query";
import {
  Car,
  BatteryMedium,
  Users,
  Package,
  Bell,
  Wrench,
  TrendingUp,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { Topbar } from "@/components/Topbar";
import { Card, StatCard, LoadingState, ErrorState } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { DashboardKPIs, Vehicle } from "@/lib/types";

const PIE_COLORS = ["#22a571", "#0ea5e9", "#f59e0b", "#94a3b8", "#ef4444"];

export default function DashboardPage() {
  const kpiQuery = useQuery({
    queryKey: ["dashboard-kpis"],
    queryFn: async () => (await api.get<DashboardKPIs>("/api/dashboard/kpis")).data,
    refetchInterval: 30_000,
  });

  const vehiclesQuery = useQuery({
    queryKey: ["vehicles-for-chart"],
    queryFn: async () => (await api.get("/api/vehicles?page=1&page_size=200")).data.items as Vehicle[],
  });

  if (kpiQuery.isLoading) {
    return (
      <>
        <Topbar title="Dashboard" />
        <LoadingState label="Loading fleet dashboard..." />
      </>
    );
  }

  if (kpiQuery.isError) {
    return (
      <>
        <Topbar title="Dashboard" />
        <ErrorState message={friendlyError(kpiQuery.error)} />
      </>
    );
  }

  const kpis = kpiQuery.data!;
  const vehicles = vehiclesQuery.data || [];

  const statusCounts = vehicles.reduce<Record<string, number>>((acc, v) => {
    acc[v.status] = (acc[v.status] || 0) + 1;
    return acc;
  }, {});
  const statusData = Object.entries(statusCounts).map(([name, value]) => ({ name, value }));

  const batteryBuckets = [
    { name: "0-20%", value: vehicles.filter((v) => v.battery_level <= 20).length },
    { name: "21-50%", value: vehicles.filter((v) => v.battery_level > 20 && v.battery_level <= 50).length },
    { name: "51-80%", value: vehicles.filter((v) => v.battery_level > 50 && v.battery_level <= 80).length },
    { name: "81-100%", value: vehicles.filter((v) => v.battery_level > 80).length },
  ];

  return (
    <>
      <Topbar title="Dashboard" />
      <main className="p-4 lg:p-8 space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            label="Active Vehicles"
            value={`${kpis.active_vehicles} / ${kpis.total_vehicles}`}
            icon={Car}
            accent="brand"
          />
          <StatCard label="Avg Battery Level" value={`${kpis.avg_battery_level}%`} icon={BatteryMedium} accent="sky" />
          <StatCard
            label="Fleet Health Score"
            value={`${kpis.avg_fleet_health_score}/100`}
            icon={TrendingUp}
            accent="brand"
          />
          <StatCard
            label="Open Alerts"
            value={kpis.open_alerts}
            trend={`${kpis.critical_alerts} critical`}
            icon={Bell}
            accent={kpis.critical_alerts > 0 ? "red" : "amber"}
          />
          <StatCard label="Active Riders" value={`${kpis.active_riders} / ${kpis.total_riders}`} icon={Users} accent="brand" />
          <StatCard label="Deliveries Today" value={kpis.deliveries_today} icon={Package} accent="sky" />
          <StatCard label="On-Time Rate" value={`${kpis.on_time_rate}%`} icon={TrendingUp} accent="brand" />
          <StatCard label="In Maintenance" value={kpis.vehicles_in_maintenance} icon={Wrench} accent="amber" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="p-5">
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">
              Battery Level Distribution
            </h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={batteryBuckets}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-slate-200 dark:stroke-slate-800" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="value" fill="#22a571" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>

          <Card className="p-5">
            <h2 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-4">Vehicle Status Breakdown</h2>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={95} paddingAngle={2}>
                  {statusData.map((_, idx) => (
                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </div>
      </main>
    </>
  );
}
