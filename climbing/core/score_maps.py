from climbing.db.models.category import Category

category_to_score_map: dict[Category, float] = {
    category: index * 0.5 + 1
    for index, category in enumerate(Category.values())
}

place_to_score_map: dict[int, float] = {
    1: 100,
    2: 85,
    3: 74,
    4: 65,
    5: 57,
    6: 50,
    7: 44,
    8: 39,
    9: 35,
    **{10 + i: 32 - i * 2 for i in range(12)},
    **{22 + i: 9 - i for i in range(9)},
}
