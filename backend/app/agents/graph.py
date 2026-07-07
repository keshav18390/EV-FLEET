"""
Multi-agent orchestration built with LangGraph.

Flow:
    START -> manager_router (classifies intent, deterministic keyword routing)
          -> one specialist agent (gathers grounded DB facts)
          -> manager_agent (synthesizes final natural-language reply, uses LLM
             if a key is configured, otherwise falls back to a clean
             deterministic summary so the app NEVER breaks without a key)
          -> END

10 agents total: fleet_monitoring, battery_health, maintenance_prediction,
delivery_optimization, operations, rider_performance, manager,
report_generator, alert, executive_dashboard.
"""
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from app.agents.state import AgentState
from app.core.llm import call_llm
from app.agents import tools as t


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
_INTENT_KEYWORDS = {
    "battery_health": ["battery", "charge", "charging", "degrad", "soh", "state of health"],
    "maintenance_prediction": ["servic", "maintenance", "repair", "predict"],
    "delivery_optimization": ["deliver", "route", "delay", "eta", "optimi"],
    "rider_performance": ["rider", "driver", "performance"],
    "alert": ["alert", "warning", "issue", "problem"],
    "report_generator": ["report", "weekly", "summary", "generate"],
    "executive_dashboard": ["kpi", "executive", "overview", "dashboard"],
    "operations": ["operation", "status", "health score"],
}


def classify_intent(query: str) -> str:
    q = query.lower()
    for intent, keywords in _INTENT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            return intent
    return "fleet_monitoring"  # default catch-all agent


def build_router_node():
    def _node(state: AgentState) -> AgentState:
        state["intent"] = classify_intent(state["query"])
        return state
    return _node


# ---------------------------------------------------------------------------
# Specialist agent node factory -- each closes over a `db` Session
# ---------------------------------------------------------------------------
def build_specialist_nodes(db: Session):

    def fleet_monitoring(state: AgentState) -> AgentState:
        summary = t.get_fleet_summary(db)
        state["agent_name"] = "Fleet Monitoring Agent"
        state["db_context"] = (
            f"Total vehicles: {summary['total_vehicles']}, active: {summary['active_vehicles']}, "
            f"in maintenance: {summary['vehicles_in_maintenance']}, "
            f"avg battery level: {summary['avg_battery_level']}%, "
            f"avg fleet health score: {summary['avg_fleet_health_score']}/100."
        )
        return state

    def battery_health(state: AgentState) -> AgentState:
        low = t.get_low_battery_vehicles(db)
        degrading = t.get_degrading_battery_vehicles(db)
        low_list = ", ".join(f"{v.registration_number} ({v.battery_level}%)" for v in low[:10]) or "none"
        degrading_list = ", ".join(f"{v.registration_number} (SoH {v.battery_health}%)" for v in degrading[:10]) or "none"
        state["agent_name"] = "Battery Health Agent"
        state["db_context"] = (
            f"Vehicles with battery below 20%: {low_list}. "
            f"Vehicles with degrading battery health (<75% SoH): {degrading_list}."
        )
        return state

    def maintenance_prediction(state: AgentState) -> AgentState:
        due = t.get_vehicles_needing_service(db)
        cost = t.get_maintenance_cost_summary(db)
        due_list = ", ".join(f"{v.registration_number} (odometer {round(v.odometer_km)}km)" for v in due[:10]) or "none currently"
        state["agent_name"] = "Maintenance Prediction Agent"
        state["db_context"] = (
            f"Vehicles predicted to need servicing now: {due_list}. "
            f"Total historical maintenance spend: {cost['total_cost']} across {cost['record_count']} records."
        )
        return state

    def delivery_optimization(state: AgentState) -> AgentState:
        delayed = t.get_recent_delayed_deliveries(db)
        summary = t.get_fleet_summary(db)
        delayed_list = ", ".join(
            f"#{d.id} {d.pickup_area}->{d.drop_area} delayed {round(d.delay_minutes)}min" for d in delayed[:10]
        ) or "none in the last 7 days"
        state["agent_name"] = "Delivery Optimization Agent"
        state["db_context"] = (
            f"Recent delayed deliveries: {delayed_list}. "
            f"Fleet-wide on-time rate: {summary['on_time_rate']}%."
        )
        return state

    def rider_performance(state: AgentState) -> AgentState:
        worst = t.get_worst_riders(db)
        best = t.get_best_riders(db)
        worst_list = ", ".join(f"{r.full_name} (score {r.performance_score})" for r in worst[:10]) or "none"
        best_list = ", ".join(f"{r.full_name} (score {r.performance_score})" for r in best[:5]) or "none"
        state["agent_name"] = "Rider Performance Agent"
        state["db_context"] = f"Lowest performing riders: {worst_list}. Top performing riders: {best_list}."
        return state

    def alert_agent(state: AgentState) -> AgentState:
        summary = t.get_fleet_summary(db)
        state["agent_name"] = "Alert Agent"
        state["db_context"] = (
            f"Open alerts: {summary['open_alerts']}, of which critical: {summary['critical_alerts']}."
        )
        return state

    def report_generator(state: AgentState) -> AgentState:
        summary = t.get_fleet_summary(db)
        cost = t.get_maintenance_cost_summary(db)
        state["agent_name"] = "Report Generator Agent"
        state["db_context"] = (
            f"WEEKLY FLEET REPORT DATA -- Vehicles: {summary['total_vehicles']} "
            f"({summary['active_vehicles']} active, {summary['vehicles_in_maintenance']} in maintenance). "
            f"Avg battery level {summary['avg_battery_level']}%, avg fleet health score "
            f"{summary['avg_fleet_health_score']}/100. Riders: {summary['total_riders']} "
            f"({summary['active_riders']} active). On-time delivery rate: {summary['on_time_rate']}%. "
            f"Open alerts: {summary['open_alerts']} (critical: {summary['critical_alerts']}). "
            f"Maintenance spend to date: {cost['total_cost']}."
        )
        return state

    def executive_dashboard(state: AgentState) -> AgentState:
        summary = t.get_fleet_summary(db)
        state["agent_name"] = "Executive Dashboard Agent"
        state["db_context"] = (
            f"Executive KPIs -- Fleet health: {summary['avg_fleet_health_score']}/100, "
            f"On-time delivery: {summary['on_time_rate']}%, Active vehicles: {summary['active_vehicles']}/"
            f"{summary['total_vehicles']}, Critical alerts: {summary['critical_alerts']}."
        )
        return state

    def operations(state: AgentState) -> AgentState:
        summary = t.get_fleet_summary(db)
        state["agent_name"] = "Operations Agent"
        state["db_context"] = (
            f"Operational snapshot -- {summary['active_vehicles']} vehicles active, "
            f"{summary['deliveries_today']} deliveries scheduled today, "
            f"{summary['deliveries_delayed_today']} delayed so far today."
        )
        return state

    return {
        "fleet_monitoring": fleet_monitoring,
        "battery_health": battery_health,
        "maintenance_prediction": maintenance_prediction,
        "delivery_optimization": delivery_optimization,
        "rider_performance": rider_performance,
        "alert": alert_agent,
        "report_generator": report_generator,
        "executive_dashboard": executive_dashboard,
        "operations": operations,
    }


# ---------------------------------------------------------------------------
# Manager agent -- final synthesis step, always runs last
# ---------------------------------------------------------------------------
def manager_agent(state: AgentState) -> AgentState:
    context = state.get("db_context", "No data available.")
    query = state["query"]
    agent_name = state.get("agent_name", "Fleet Monitoring Agent")

    result = call_llm(
        prompt=(
            f"User question: {query}\n\n"
            f"Grounded fleet data from our database (use ONLY these facts, do not invent numbers):\n{context}\n\n"
            "Write a concise, helpful answer for a fleet operations manager. Use bullet points if listing "
            "multiple vehicles/riders/items."
        ),
        system=(
            "You are the Manager Agent of an EV fleet intelligence system, synthesizing input from "
            "specialist agents. Be concise, factual, and only use the provided data."
        ),
    )

    if result.success:
        state["reply"] = result.text
    else:
        # Graceful fallback -- deterministic, still useful without any LLM key
        prefix = {
            "no_key": "(AI phrasing unavailable -- API key not configured. Showing raw data.)",
            "invalid_key": "(AI phrasing unavailable -- invalid API key. Showing raw data.)",
            "connection": "(AI phrasing unavailable -- could not reach provider. Showing raw data.)",
        }.get(result.error_code, "(AI phrasing unavailable. Showing raw data.)")
        state["reply"] = f"{prefix}\n\n{context}"

    state["agent_name"] = agent_name
    return state


# ---------------------------------------------------------------------------
# Graph builder
# ---------------------------------------------------------------------------
def build_graph(db: Session):
    graph = StateGraph(AgentState)
    specialists = build_specialist_nodes(db)

    graph.add_node("router", build_router_node())
    for name, fn in specialists.items():
        graph.add_node(name, fn)
    graph.add_node("manager", manager_agent)

    graph.set_entry_point("router")
    graph.add_conditional_edges("router", lambda s: s["intent"], {name: name for name in specialists})
    for name in specialists:
        graph.add_edge(name, "manager")
    graph.add_edge("manager", END)

    return graph.compile()


def run_chat_agent(db: Session, query: str) -> dict:
    app = build_graph(db)
    result = app.invoke({"query": query})
    return {"reply": result.get("reply", "Sorry, I couldn't process that."), "agent": result.get("agent_name", "Manager Agent")}
