from fastapi_mason.schemas import SchemaMeta, generate_schema_meta


class ProjectMeta(SchemaMeta):
    include = (
        'id',
        'name',
        'description',
        'created_at',
        'updated_at',
    )


class TaskMeta(SchemaMeta):
    include = (
        'id',
        'name',
        'project_id',
    )


def get_project_with_tasks_meta() -> SchemaMeta:
    return generate_schema_meta(ProjectMeta, ('tasks', get_task_with_project_meta()))


def get_task_with_project_meta() -> SchemaMeta:
    return generate_schema_meta(TaskMeta, ('project', ProjectMeta))
