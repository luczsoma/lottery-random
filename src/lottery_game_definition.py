class FieldDefinition:
    n: int
    min: int
    max: int

    def __init__(self, n: int, min: int, max: int) -> None:
        self.n = n
        self.min = min
        self.max = max

    def validate(self, game_name: str) -> None:
        if self.n < 1:
            raise RuntimeError(
                f'Invalid game definition "{game_name}": n < 1 in at least one field'
            )

        if self.min < 1:
            raise RuntimeError(
                f'Invalid game definition "{game_name}": min < 1 in at least one field'
            )

        if self.max < self.min + self.n - 1:
            raise RuntimeError(
                f'Invalid game definition "{game_name}": max < min + n - 1 in at least one field'
            )


class LotteryGameDefinition:
    fields: list[FieldDefinition]

    def __init__(self, drawing_sets: list[FieldDefinition]) -> None:
        self.fields = drawing_sets

    def validate(self, game_name: str) -> None:
        if len(self.fields) == 0:
            raise RuntimeError(f'Invalid game definition "{game_name}": no fields')

        self.validate_fields(game_name)

    def validate_fields(self, game_name: str) -> None:
        for field in self.fields:
            field.validate(game_name)
