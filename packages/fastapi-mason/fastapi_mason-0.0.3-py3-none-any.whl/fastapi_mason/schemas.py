class SchemaMeta:
    include: tuple[str, ...] = ()
    exclude: tuple[str, ...] = ()
    optional: tuple[str, ...] = ()


def generate_schema_meta(
        meta_structure: tuple[SchemaMeta | tuple[str, SchemaMeta], ...], class_name: str = 'SchemaMeta'
):
    def build_fields(_meta_structure, attr_name: str):
        result = []
        for item in _meta_structure:
            if isinstance(item, tuple):
                field_name, meta_cls = item
                fields = getattr(meta_cls, attr_name, ())
                for field in fields:
                    result.append(f'{field_name}.{field}')
            else:
                fields = getattr(item, attr_name, ())
                result.extend(fields)
        return tuple(result)

    return type[SchemaMeta](
        class_name,
        (SchemaMeta,),
        {
            'include': build_fields(meta_structure, 'include'),
            'exclude': build_fields(meta_structure, 'exclude'),
            'optional': build_fields(meta_structure, 'optional'),
        },
    )
