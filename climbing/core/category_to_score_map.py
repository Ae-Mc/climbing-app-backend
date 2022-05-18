from climbing.db.models.category import Category

category_to_score_map: dict[Category, float] = {
    category: index * 0.5 + 1
    for index, category in enumerate(Category.values())
}
