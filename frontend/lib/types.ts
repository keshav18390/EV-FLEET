export type UserRole = "admin" | "fleet_manager" | "operations_manager";

export interface User {
  id: number;
  full_name: string;
  email: string;
  role: UserRole;
}

export interface Vehicle {
  id: number;
  registration_number: string;
  model: string;
  city: string;
  status: "active" | "charging" | "maintenance" | "idle" | "out_of_service";
  battery_level: number;
  battery_health: number;
  odometer_km: number;
  total_charge_cycles: number;
  avg_daily_km: number;
  latitude: number;
  longitude: number;
  last_service_date: string | null;
  next_service_due_km: number | null;
  fleet_health_score: number;
}

export interface Rider {
  id: number;
  full_name: string;
  phone: string;
  city: string;
  status: "active" | "on_trip" | "offline" | "suspended";
  rating: number;
  total_deliveries: number;
  on_time_rate: number;
  performance_score: number;
}

export interface Delivery {
  id: number;
  vehicle_id: number;
  rider_id: number;
  pickup_area: string;
  drop_area: string;
  distance_km: number;
  status: "completed" | "delayed" | "cancelled" | "in_progress";
  scheduled_time: string;
  completed_time: string | null;
  delay_minutes: number;
}

export interface MaintenanceRecord {
  id: number;
  vehicle_id: number;
  maintenance_type: string;
  description: string | null;
  cost: number;
  performed_at: string;
  odometer_at_service: number;
}

export interface AlertItem {
  id: number;
  vehicle_id: number | null;
  rider_id: number | null;
  alert_type: string;
  severity: "low" | "medium" | "high" | "critical";
  message: string;
  is_resolved: boolean;
  created_at: string;
}

export interface DashboardKPIs {
  total_vehicles: number;
  active_vehicles: number;
  vehicles_in_maintenance: number;
  avg_battery_level: number;
  avg_fleet_health_score: number;
  total_riders: number;
  active_riders: number;
  deliveries_today: number;
  deliveries_delayed_today: number;
  on_time_rate: number;
  open_alerts: number;
  critical_alerts: number;
}

export interface Paginated<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  agent?: string;
}
