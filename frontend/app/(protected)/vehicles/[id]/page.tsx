"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { ArrowLeft, BatteryMedium, Gauge, Wrench, MapPin } from "lucide-react";
import Link from "next/link";
import { Topbar } from "@/components/Topbar";
import { Card, Badge, LoadingState, ErrorState } from "@/components/ui";
import { api, friendlyError } from "@/lib/api";
import type { Vehicle, MaintenanceRecord, Paginated } from "@/lib/types";

export default function VehicleDetailPage() {
  const params = useParams();
  const id = params?.id;

  const vehicleQuery = useQuery({
    queryKey: ["vehicle", id],
    queryFn: async () => (await api.get<Vehicle>(`/api/vehicles/${id}`)).data,
  });

  const batteryForecastQuery = useQuery({
    queryKey: ["battery-forecast", id],
    queryFn: async () => (await api.get(`/api/ml/vehicle/${id}/battery-health-forecast`)).data,
    enabled: !!vehicleQuery.data,
  });

  const maintenancePredictionQuery = useQuery({
    queryKey: ["maintenance-prediction", id],
    queryFn: async () => (await api.get(`/api/ml/vehicle/${id}/maintenance-prediction`)).data,
    enabled: !!vehicleQuery.data,
  });

  const maintenanceHistoryQuery = useQuery({
    queryKey: ["maintenance-history", id],
    queryFn: async () =>
      (await api.get<Paginated<MaintenanceRecord>>("/api/maintenance", { params: { vehicle_id: id, page_size: 20 } })).data,
    enabled: !!vehicleQuery.data,
  });

  if (vehicleQuery.isLoading) {
    return (
      <>
        <Topbar title="Vehicle Details" />
        <LoadingState />
      </>
    );
  }

  if (vehicleQuery.isError || !vehicleQuery.data) {
    return (
      <>
        <Topbar title="Vehicle Details" />
        <ErrorState message={vehicleQuery.error ? friendlyError(vehicleQuery.error) : "Vehicle not found."} />
      </>
    );
  }

  const v = vehicleQuery.data;

  return (
    <>
      <Topbar title={v.registration_number} />
      <main className="p-4 lg:p-8 space-y-6">
        <Link href="/vehicles" className="inline-flex items-center gap-1.5 text-sm text-slate-500 hover:text-brand-600">
          <ArrowLeft size={16} /> Back to vehicles
        </Link>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="p-5">
            <p className="text-sm text-slate-500 mb-1">Model & City</p>
            <p className="font-semibold text-slate-900 dark:text-white">{v.model}</p>
            <p className="text-sm text-slate-500 flex items-center gap-1 mt-1">
              <MapPin size={14} /> {v.city}
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-slate-500 mb-1">Status</p>
            <Badge color={v.status === "active" ? "green" : v.status === "maintenance" ? "amber" : "slate"}>
              {v.status.replace("_", " ")}
            </Badge>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-slate-500 mb-1 flex items-center gap-1">
              <BatteryMedium size={14} /> Battery
            </p>
            <p className="font-semibold text-slate-900 dark:text-white">
              {v.battery_level}% charge / {v.battery_health}% health
            </p>
          </Card>
          <Card className="p-5">
            <p className="text-sm text-slate-500 mb-1 flex items-center gap-1">
              <Gauge size={14} /> Odometer
            </p>
            <p className="font-semibold text-slate-900 dark:text-white">{Math.round(v.odometer_km).toLocaleString()} km</p>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <Card className="p-5">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3">AI Battery Health Forecast</h3>
            {batteryForecastQuery.isLoading ? (
              <LoadingState label="Running prediction model..." />
            ) : batteryForecastQuery.data ? (
              <p className="text-slate-600 dark:text-slate-400 text-sm">
                Current health: <strong>{batteryForecastQuery.data.current_battery_health}%</strong> &rarr; ML-predicted
                trajectory: <strong>{batteryForecastQuery.data.predicted_battery_health}%</strong>
              </p>
            ) : null}
          </Card>

          <Card className="p-5">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-3 flex items-center gap-1.5">
              <Wrench size={14} /> Maintenance Prediction
            </h3>
            {maintenancePredictionQuery.isLoading ? (
              <LoadingState label="Running prediction model..." />
            ) : maintenancePredictionQuery.data ? (
              <Badge color={maintenancePredictionQuery.data.maintenance_recommended ? "amber" : "green"}>
                {maintenancePredictionQuery.data.maintenance_recommended
                  ? "Service recommended soon"
                  : "No service needed right now"}
              </Badge>
            ) : null}
          </Card>
        </div>

        <Card>
          <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800">
            <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-300">Maintenance History</h3>
          </div>
          {maintenanceHistoryQuery.isLoading ? (
            <LoadingState />
          ) : maintenanceHistoryQuery.data && maintenanceHistoryQuery.data.items.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="text-left text-slate-500 border-b border-slate-200 dark:border-slate-800">
                    <th className="px-4 py-3 font-medium">Type</th>
                    <th className="px-4 py-3 font-medium">Description</th>
                    <th className="px-4 py-3 font-medium">Cost</th>
                    <th className="px-4 py-3 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {maintenanceHistoryQuery.data.items.map((m) => (
                    <tr key={m.id} className="border-b border-slate-100 dark:border-slate-800/60">
                      <td className="px-4 py-3 capitalize">{m.maintenance_type.replace("_", " ")}</td>
                      <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{m.description}</td>
                      <td className="px-4 py-3">Rs. {m.cost.toLocaleString()}</td>
                      <td className="px-4 py-3 text-slate-600 dark:text-slate-400">
                        {new Date(m.performed_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="px-4 py-8 text-center text-sm text-slate-500">No maintenance records for this vehicle.</p>
          )}
        </Card>
      </main>
    </>
  );
}
