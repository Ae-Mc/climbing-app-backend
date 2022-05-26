from climbing.db.models.category import Category

category_to_score_map: dict[Category, float] = {
    category: index * 0.5 + 1
    for index, category in enumerate(Category.values())
}

place_to_score_map: dict[int, float] = {
    1: 25,
    2: 20,
    3: 16,
    4: 13,
    **{i: 16 - i for i in range(5, 16)},
}
