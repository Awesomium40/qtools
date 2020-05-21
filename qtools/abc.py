import enum

__all__ = ['StringEnum']


class StringEnum(enum.Enum):

    def __str__(self):
        return self.value
