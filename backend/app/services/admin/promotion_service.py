promotions = []


def get_all_promotions():
    return promotions


def get_promotion_by_id(promotion_id: int):

    for promo in promotions:
        if promo["id"] == promotion_id:
            return promo

    return None


def create_promotion(
    code: str,
    discount_percent: float,
    valid_from: str,
    valid_to: str,
    description: str
):

    promotion = {
        "id": len(promotions) + 1,
        "code": code,
        "discount_percent": discount_percent,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "description": description,
        "is_active": True
    }

    promotions.append(promotion)

    return promotion


def update_promotion(promotion_id: int, new_data: dict):

    promo = get_promotion_by_id(promotion_id)

    if promo is None:
        return None

    promo.update(new_data)

    return promo


def delete_promotion(promotion_id: int):

    promo = get_promotion_by_id(promotion_id)

    if promo:
        promotions.remove(promo)

    return promo
