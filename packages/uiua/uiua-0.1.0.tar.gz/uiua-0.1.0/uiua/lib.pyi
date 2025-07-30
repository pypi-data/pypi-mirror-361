class UiuaPrimitive:
    glyph: str | None
    name: str
    num_arguments: int | None
    num_outputs: int | None
    aliases: list[str]

class UiuaInterpreter:
    primitives: list[UiuaPrimitive]
    def eval(self, code: str) -> str: ...
    def eval_multi(self, codes: list[str]) -> list[str | None]: ...
