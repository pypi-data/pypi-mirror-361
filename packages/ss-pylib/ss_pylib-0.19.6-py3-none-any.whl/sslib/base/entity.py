from typing import Type, TypeVar, Union, List
from dataclasses import dataclass, field
from warnings import deprecated
from dataclasses_json import DataClassJsonMixin, LetterCase, config
from sslib.base.dict import DictEx

T = TypeVar('T', bound='DataClassJsonMixin')


class MyJsonMixin(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL)['dataclasses_json']

    def to_json(self, *, ensure_ascii=False, **kwargs):
        return super().to_json(ensure_ascii=ensure_ascii, **kwargs)

    @classmethod
    def dumps(cls: Type[T], obj: Union[T, List[T]], *, ensure_ascii: bool = False, **kwargs) -> str:
        many = isinstance(obj, (list, tuple))
        schema = cls.schema(many=many)
        return schema.dumps(obj, ensure_ascii=ensure_ascii, **kwargs)


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
