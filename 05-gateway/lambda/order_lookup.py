"""Order-lookup Lambda — the 'your own API' the agent will call through Gateway.

Honest stub: orders are a hardcoded dict, not a real database. The point is that
YOUR service becomes an agent-callable tool, not order management.
"""

ORDERS = {
    "123": {"items": ["Wireless Mouse", "USB-C Cable"], "total": 48.00,
            "status": "delivered", "days_since_purchase": 5},
    "456": {"items": ["Mechanical Keyboard"], "total": 120.00,
            "status": "delivered", "days_since_purchase": 40},
}


def handler(event, context):
    # Gateway passes the tool input; accept a few shapes defensively.
    order_id = str(event.get("order_id") or event.get("orderId") or "").strip()
    order = ORDERS.get(order_id)
    if not order:
        return {"found": False, "order_id": order_id,
                "message": f"No order found with id {order_id}"}
    return {"found": True, "order_id": order_id, **order}
