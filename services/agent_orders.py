from services.supabase_client import supabase


def has_ordered(agent_id: str) -> bool:
    result = supabase.table("agent_orders").select("agent_id").eq("agent_id", agent_id).execute()
    return len(result.data) > 0


def record_order(agent_id: str) -> None:
    supabase.table("agent_orders").insert({"agent_id": agent_id}).execute()
