from typing import Annotated, Optional

from pydantic import BaseModel, Field


def gen_update_class[ModelType: BaseModel](model: type[ModelType]) -> type[ModelType]:
    annotations = {}
    fields = {}
    for field, info in filter(lambda x: x[0] != "id", model.model_fields.items()):
        annotations[field] = Annotated[
            Optional[info.annotation],
            Field(description=f"New {field} of the {model.__name__}"),
        ]
        fields[field] = None
    return type(
        f"PatchUpdate{model.__name__}",
        (BaseModel,),
        {
            "__annotations__": annotations,
            **fields,
        },
    )
