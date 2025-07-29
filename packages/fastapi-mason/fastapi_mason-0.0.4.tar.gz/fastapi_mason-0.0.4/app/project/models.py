from tortoise import fields
from tortoise.models import Model


class Project(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)


class Tast(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    project = fields.ForeignKeyField('models.Project', related_name='tasks')


class Issue(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    project = fields.ForeignKeyField('models.Project', related_name='issues')


class Comment(Model):
    id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=255)
    project = fields.ForeignKeyField('models.Project', related_name='comments')
