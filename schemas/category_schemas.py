from marshmallow import Schema, fields, validate

class CategoryCreateSchema(Schema):
    nombre = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=64),
        error_messages={"required": "El nombre de la categoría es obligatorio"}
    )

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str()