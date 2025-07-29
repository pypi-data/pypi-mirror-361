from warnings import deprecated
from dataclasses import dataclass, field
from dataclasses_json import DataClassJsonMixin, LetterCase, config
from marshmallow import fields

# NOTE - 삭제예정
from sslib.base.dict import DictEx


TDatetimeField = field(metadata=config(mm_field=fields.DateTime(format='%Y-%m-%d %H:%M:%S')))


class MyJsonMixin(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)["dataclasses_json"]

    def to_json(self, *, ensure_ascii=False, **kwargs):
        return super().to_json(ensure_ascii=ensure_ascii, **kwargs)

    @classmethod
    def dumps(cls, objs, *, ensure_ascii=False, **kw):
        many = isinstance(objs, (list, tuple))
        return cls.schema(many=many).dumps(objs, ensure_ascii=ensure_ascii, **kw)


@dataclass
class IdEntity(MyJsonMixin):
    id: int = field(default=0)


class JsonEntity(MyJsonMixin):
    pass


class JsonWithIdEntity(IdEntity):
    pass


class JsonCamelEntity(MyJsonMixin):
    pass


@deprecated('CamelEntity 사용')
class Entity(DictEx):
    pass


@deprecated('JsonWithIdEntity 사용')
@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
