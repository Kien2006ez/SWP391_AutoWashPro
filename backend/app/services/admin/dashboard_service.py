from app.services.booking_service import bookings
from app.services.auth_service import users
from app.services.admin.service_service import wash_services
from app.services.admin.promotion_service import promotions


def get_dashboard_stats():
    """Aggregate overview stats for the admin dashboard."""

    status_counts = {}

    for booking in bookings:
        status = booking["status"]
        status_counts[status] = status_counts.get(status, 0) + 1

    active_promotions = [
        p for p in promotions if p.get("is_active")
    ]

    return {
        "total_users": len(users),
        "total_bookings": len(bookings),
        "bookings_by_status": status_counts,
        "total_services": len(wash_services),
        "total_promotions": len(promotions),
        "active_promotions": len(active_promotions)
    }
