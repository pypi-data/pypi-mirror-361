from dataclasses import dataclass, field
from warnings import deprecated
from dataclasses_json import DataClassJsonMixin, dataclass_json
from sslib.base.dict import DictEx


class MyJsonMixin(DataClassJsonMixin):
    def to_json(self, *, ensure_ascii=False, **kwargs):
        return super().to_json(ensure_ascii=ensure_ascii, **kwargs)


@dataclass
class IdEntity(MyJsonMixin):
    id: int = field(default=0)


@dataclass_json
class JsonEntity(MyJsonMixin):
    pass


@dataclass_json
class JsonWithIdEntity(IdEntity):
    pass


# NOTE
# @dataclass_json 데코레이터만 사용하면 schema() 오류 발생,
# DataClassJsonMixin과 함께 사용해서 막는다 (좋은 방법은 아닌듯)
class JsonCamelEntity(MyJsonMixin):
    pass


@deprecated('CamelEntity 사용')
@dataclass
class Entity(DictEx):
    pass


@deprecated('JsonWithIdEntity 사용')
@dataclass
class EntityWithId(Entity):
    id: int = field(default=0)
