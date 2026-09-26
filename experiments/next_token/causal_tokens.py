"""Passive indexed lag/token sources, with no Runtime or publication authority.

The full source family is declared. A window computes values without a
dense one-hot expansion; it does not erase the corpus or learner history.
"""
from dataclasses import dataclass
from numbers import Integral


def natural(value, *, positive=False):
    if type(value) is not int or value < int(positive):
        raise ValueError('an exact nonnegative/positive integer is required')
    return value


@dataclass(frozen=True)
class TokenSources:
    vocabulary: int
    context: int

    def __post_init__(self):
        natural(self.vocabulary, positive=True)
        natural(self.context, positive=True)

    @property
    def padding(self):
        # Missing pre-file positions are distinct from every predicted token.
        return self.vocabulary

    @property
    def source_count(self):
        return self.context*(self.vocabulary+1)

    def window(self, tokens, position):
        natural(position)
        if position > len(tokens):
            raise ValueError('forecast position exceeds the retained token tape')
        values = []
        for lag in range(1, self.context+1):
            if lag > position:
                values.append(self.padding)
            else:
                raw = tokens[position-lag]
                if isinstance(raw, bool) or not isinstance(raw, Integral):
                    raise ValueError('historical tokens must be exact integer IDs')
                value = int(raw)
                if not 0 <= value < self.vocabulary:
                    raise ValueError('historical token outside the declared prediction alphabet')
                values.append(value)
        return TokenWindow(self, position, tuple(values))


@dataclass(frozen=True)
class TokenWindow:
    schema: TokenSources
    position: int
    # Increasing lag: lag 1 is the most recent token.
    past: tuple[int, ...]

    def __post_init__(self):
        if type(self.schema) is not TokenSources:
            raise ValueError('closed token-source schema required')
        self.schema.__post_init__()
        natural(self.position)
        if type(self.past) is not tuple or len(self.past) != self.schema.context:
            raise ValueError('complete immutable lag tuple required')
        for lag, token in enumerate(self.past, 1):
            natural(token)
            if lag > self.position:
                if token != self.schema.padding:
                    raise ValueError('unavailable pre-file context must be explicit padding')
            elif token >= self.schema.vocabulary:
                raise ValueError('an available history position cannot be padding')

    def atom(self, lag, token):
        natural(lag, positive=True)
        natural(token)
        if lag > self.schema.context or token > self.schema.padding:
            raise ValueError('undeclared lag/token atom')
        return int(self.past[lag-1] == token)

    def append(self, target):
        """Passive source-reader successor after one target is revealed."""
        natural(target)
        if target >= self.schema.vocabulary:
            raise ValueError('target outside the declared prediction alphabet')
        return TokenWindow(self.schema, self.position+1, (target,)+self.past[:-1])
