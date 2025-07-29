from fastapi_mason.schemas import SchemaMeta


class ProjectMeta(SchemaMeta):
    include = (
        'id',
        'name',
        'description',
        'created_at',
        'updated_at',
    )
