# Database Schema

SQLite database (`fleet.db`), managed via SQLAlchemy ORM. Tables are created automatically on startup (`Base.metadata.create_all`) — no manual migration step is required for a fresh install. If you need real migrations for schema evolution later, add Alembic (`pip install alembic`, `alembic init migrations`) — it's already listed as a natural next step but not wired in by default to keep the quick-start simple.

## Entity relationship overview

```
users (standalone — auth only)

vehicles ──1───────*── deliveries ──*───────1── riders
   │
   └──1────────*── maintenance_records

vehicles ──1────*── alerts (nullable vehicle_id)
riders   ──1────*── alerts (nullable rider_id)
```

## `users`
| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| full_name | String(120) | |
| email | String(180) | unique, indexed |
| hashed_password | String(255) | bcrypt hash |
| role | Enum | admin / fleet_manager / operations_manager |
| created_at | DateTime | |

## `vehicles`
| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| registration_number | String(30) | unique, indexed |
| model | String(60) | |
| city | String(60) | |
| status | Enum | active / charging / maintenance / idle / out_of_service |
| battery_level | Float | current charge % |
| battery_health | Float | state of health % |
| odometer_km | Float | |
| total_charge_cycles | Integer | |
| avg_daily_km | Float | |
| latitude, longitude | Float | |
| last_service_date | DateTime, nullable | |
| next_service_due_km | Float, nullable | |
| purchase_date | DateTime, nullable | |
| fleet_health_score | Float | composite 0-100 score |
| created_at | DateTime | |

## `riders`
| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| full_name | String(120) | |
| phone | String(20) | unique |
| city | String(60) | |
| status | Enum | active / on_trip / offline / suspended |
| rating | Float | 0-5 |
| total_deliveries | Integer | |
| on_time_rate | Float | % |
| performance_score | Float | 0-100 |
| joined_date | DateTime | |

## `deliveries`
| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| vehicle_id | Integer FK → vehicles.id | |
| rider_id | Integer FK → riders.id | |
| pickup_area, drop_area | String(100) | |
| distance_km | Float | |
| status | Enum | completed / delayed / cancelled / in_progress |
| scheduled_time | DateTime | |
| completed_time | DateTime, nullable | |
| delay_minutes | Float | |
| created_at | DateTime | |

## `maintenance_records`
| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| vehicle_id | Integer FK → vehicles.id | |
| maintenance_type | Enum | battery_replacement / tire_change / brake_service / general_checkup / motor_repair |
| description | String(255), nullable | |
| cost | Float | |
| performed_at | DateTime | |
| odometer_at_service | Float | |

## `alerts`
| Column | Type | Notes |
|---|---|---|
| id | Integer PK | |
| vehicle_id | Integer FK, nullable | |
| rider_id | Integer FK, nullable | |
| alert_type | Enum | low_battery / maintenance_due / delivery_delay / battery_degradation / rider_performance |
| severity | Enum | low / medium / high / critical |
| message | String(255) | |
| is_resolved | Boolean | |
| created_at | DateTime | |

## Switching to PostgreSQL

Change `DATABASE_URL` in `.env` to a Postgres DSN, e.g.:

```
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/evfleet
```

Install the driver (`pip install psycopg2-binary`), remove the SQLite-only `connect_args` in `app/db/database.py` (it's already conditional on the URL prefix, so no code change is actually required), and re-run `python -m app.seed`.
