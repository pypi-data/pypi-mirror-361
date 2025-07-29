from datetime import datetime
from dataclasses import dataclass, field
from warnings import deprecated
from dataclasses_json import DataClassJsonMixin, LetterCase, config
from sslib.base.dict import DictEx


def dt_encoder(val: object) -> object:
    # datetime만 포맷하고 나머지는 그대로 넘기기
    print('엔코더')
    if isinstance(val, datetime):
        return val.strftime("%Y-%m-%d %H:%M:%S")
    return val


def dt_decoder(val: object) -> object:
    # 문자열 포맷이 맞으면 datetime으로, 아니면 그대로
    print('디코더')
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            ...
    return val


class MyJsonMixin(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.CAMEL, encoder=dt_encoder, decoder=dt_decoder)['dataclasses_json']

    def to_json(self, *, ensure_ascii=False, **kwargs):
        return super().to_json(ensure_ascii=ensure_ascii, **kwargs)

    @classmethod
    def dumps(cls, obj, *, ensure_ascii: bool = False, **kwargs) -> str:
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
