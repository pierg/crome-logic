# from dataclasses import dataclass, field, fields, replace
#
#
#
# @dataclass(frozen=True)
# class Test:
#     name: str
#
#     _name: str = field(init=False, repr=False, default='baz')
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @name.setter
#     def name(self, value: str) -> None:
#         object.__setattr__(self, '_name', value + "MOD")
#
#
# test = Test(name="ciao")
#
# print(test)
# print(test.name)
# print(test)
#
# test.name = "ddd"
#
# print(test)
