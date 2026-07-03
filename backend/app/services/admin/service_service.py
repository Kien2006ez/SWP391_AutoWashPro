wash_services = []


def get_all_services():
    return wash_services


def get_service_by_id(service_id: int):

    for service in wash_services:
        if service["id"] == service_id:
            return service

    return None


def create_service(
    name: str,
    description: str,
    price: float,
    duration_minutes: int
):

    service = {
        "id": len(wash_services) + 1,
        "name": name,
        "description": description,
        "price": price,
        "duration_minutes": duration_minutes,
        "is_active": True
    }

    wash_services.append(service)

    return service


def update_service(service_id: int, new_data: dict):

    service = get_service_by_id(service_id)

    if service is None:
        return None

    service.update(new_data)

    return service


def delete_service(service_id: int):

    service = get_service_by_id(service_id)

    if service:
        wash_services.remove(service)

    return service
