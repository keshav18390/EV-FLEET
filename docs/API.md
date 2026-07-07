# API Reference

Base URL (local): `http://localhost:8000`
Interactive Swagger UI: `http://localhost:8000/docs`
Interactive ReDoc: `http://localhost:8000/redoc`

All endpoints except `/api/health`, `/api/auth/register`, and `/api/auth/login` require a JWT bearer token:

```
Authorization: Bearer <access_token>
```

## Auth

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create a new user. Body: `{ full_name, email, password, role? }`. Returns `Token`. |
| POST | `/api/auth/login` | Log in. Body: `{ email, password }`. Returns `Token`. |
| GET | `/api/auth/me` | Returns the current authenticated user. |

`Token` shape: `{ access_token, token_type: "bearer", user: { id, full_name, email, role } }`

Roles: `admin`, `fleet_manager`, `operations_manager`.

## Vehicles

| Method | Path | Description |
|---|---|---|
| GET | `/api/vehicles` | Paginated list. Query: `search`, `status`, `city`, `page`, `page_size`. |
| GET | `/api/vehicles/{id}` | Single vehicle detail. |
| GET | `/api/vehicles/low-battery/list` | Vehicles below a battery `threshold` (default 20%). |

## Riders

| Method | Path | Description |
|---|---|---|
| GET | `/api/riders` | Paginated list. Query: `search`, `status`, `page`, `page_size`. |
| GET | `/api/riders/{id}` | Single rider detail. |

## Deliveries

| Method | Path | Description |
|---|---|---|
| GET | `/api/deliveries` | Paginated list. Query: `status`, `vehicle_id`, `rider_id`, `page`, `page_size`. |

## Maintenance

| Method | Path | Description |
|---|---|---|
| GET | `/api/maintenance` | Paginated list. Query: `vehicle_id`, `page`, `page_size`. |

## Alerts

| Method | Path | Description |
|---|---|---|
| GET | `/api/alerts` | Paginated list. Query: `severity`, `resolved`, `page`, `page_size`. |
| POST | `/api/alerts/{id}/resolve` | Marks an alert resolved. |

## Dashboard

| Method | Path | Description |
|---|---|---|
| GET | `/api/dashboard/kpis` | Fleet-wide KPI snapshot (vehicle counts, battery averages, on-time rate, alert counts, etc). |

## AI Chat

| Method | Path | Description |
|---|---|---|
| POST | `/api/chat` | Body: `{ message }`. Returns `{ reply, agent }`. Routes through the 10-agent LangGraph system — see `docs/ARCHITECTURE.md`. |

## ML Predictions

| Method | Path | Description |
|---|---|---|
| GET | `/api/ml/vehicle/{id}/battery-health-forecast` | Predicted battery state-of-health. |
| GET | `/api/ml/vehicle/{id}/maintenance-prediction` | Boolean: is service recommended. |
| GET | `/api/ml/delivery-delay-risk?distance_km=<float>&hour_of_day=<int>` | Boolean: predicted delay risk. |
| GET | `/api/ml/rider/{id}/performance-forecast` | Predicted rider performance score. |

## Reports

| Method | Path | Description |
|---|---|---|
| GET | `/api/reports/vehicles/csv` | Downloads a CSV of all vehicles. |
| GET | `/api/reports/fleet-summary/pdf` | Downloads a one-page PDF fleet summary. |

## Admin (requires `admin` role)

| Method | Path | Description |
|---|---|---|
| GET | `/api/admin/users` | Lists all registered users. |

## Health

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | `{ status, environment, llm_provider, llm_key_configured }`. No auth required. |

## Error format

Errors return `{ "detail": "message" }` with the appropriate HTTP status code (400, 401, 403, 404). Unhandled server errors are caught by a global handler and return a generic 500 with a friendly message rather than a stack trace.

## Pagination shape

All list endpoints return:

```json
{
  "total": 50,
  "page": 1,
  "page_size": 20,
  "items": [ ... ]
}
```
