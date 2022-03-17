## 1.0.1 (2022-03-17)

### Fix

- **db/models**: remove created_at field from UserCreate model
- **util/alembic**: remove drop table statement from add_created_at_column_to_route_table patch that crashed upgrade process

## 1.0.0 (2022-03-16)

### Fix

- **BaseRouteImage**: fix port in image urls
- **routes**: remove excess author column and rename uploader column to author

### Feat

- set RouteImages' urls to absolute, fix bug that occured after renaming uploader_id to author_id

## 0.2.0 (2022-01-26)

### Fix

- **fastapi_users**: :bug: Fix UserDatabase's get method

### Refactor

- Move classes, not used as database tables or it's superclasses to separate module schemas
- Add four separate schemas to get route information

### Docs

- **users**: Add docs to DELETE /users/me endpoint

### Feat

- **users**: Add /users/me/routes endpoint to fetch current user's routes

## 0.1.0 (2022-01-25)
