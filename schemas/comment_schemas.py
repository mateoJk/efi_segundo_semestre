from marshmallow import Schema, fields, validate

class CommentCreateSchema(Schema):
    contenido = fields.Str(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "El contenido es obligatorio"}
    )