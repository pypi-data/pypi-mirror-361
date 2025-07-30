# Copyright 2023-2024 Geoffrey R. Scheller
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from typing import Never, overload, TypeVar

from pythonic_fp.circulararray import CA
from pythonic_fp.containers.maybe import MayBe

__all__ = ['DEQueue', 'de_queue']

D = TypeVar('D')


class DEQueue[D]:
    """
    Stateful Double-Ended (DEQueue) data structure. Order of initial
    data retained, as if pushed on from the right.
    """
    L = TypeVar('L')
    R = TypeVar('R')

    __slots__ = ('_ca',)

    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        """
        :param dss: takes one or no iterables
        :raises ValueError: if more than 1 iterable is given
        """
        if (size := len(dss)) > 1:
            msg = f'DEQueue expects at most 1 iterable argument, got {size}'
            raise ValueError(msg)
        self._ca = CA(dss[0]) if size == 1 else CA()

    def __bool__(self) -> bool:
        return len(self._ca) > 0

    def __len__(self) -> int:
        return len(self._ca)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DEQueue):
            return False
        return self._ca == other._ca

    @overload
    def __getitem__(self, idx: int) -> D: ...
    @overload
    def __getitem__(self, idx: slice) -> Sequence[D]: ...

    def __getitem__(self, idx: int | slice) -> Never:
        if isinstance(idx, slice):
            msg = 'fptools_fp.queues.DEQueue is not slicable by design'
            raise NotImplementedError(msg)
        msg = 'fptools_fp.queues.DEQueue is not indexable by design'
        raise NotImplementedError(msg)

    def __iter__(self) -> Iterator[D]:
        return iter(list(self._ca))

    def __reversed__(self) -> Iterator[D]:
        return reversed(list(self._ca))

    def __repr__(self) -> str:
        if len(self) == 0:
            return 'DEQueue()'
        return 'DEQueue(' + ', '.join(map(repr, self._ca)) + ')'

    def __str__(self) -> str:
        return '>< ' + ' | '.join(map(str, self)) + ' ><'

    def copy(self) -> DEQueue[D]:
        """Copy.

        :returns: shallow copy of the DEQueue
        """
        return DEQueue(self._ca)

    def pushl(self, *ds: D) -> None:
        """Push items onto left side of DEQueue."""
        self._ca.pushl(*ds)

    def pushr(self, *ds: D) -> None:
        """Push items onto right side of DEQueue."""
        self._ca.pushr(*ds)

    def popl(self) -> MayBe[D]:
        """Pop next item from left side DEQueue.

        :returns: MayBe of next item popped off left side of queue
        """
        if self._ca:
            return MayBe(self._ca.popl())
        return MayBe()

    def popr(self) -> MayBe[D]:
        """Pop next item off right side DEQueue.

        :returns: MayBe of item popped off right side of queue
        """
        if self._ca:
            return MayBe(self._ca.popr())
        return MayBe()

    def peakl(self) -> MayBe[D]:
        """Peak at left side of DEQueue. Does not consume item.

        :returns: MayBe of first item on left
        """
        if self._ca:
            return MayBe(self._ca[0])
        return MayBe()

    def peakr(self) -> MayBe[D]:
        """Peak at right side of DEQueue. Does not consume item.

        :returns: MayBe of last item on right
        """
        if self._ca:
            return MayBe(self._ca[-1])
        return MayBe()

    def foldl[L](self, f: Callable[[L, D], L], initial: L | None = None) -> MayBe[L]:
        """Reduces DEQueue left to right.

        :param f: reducing function, first argument is for accumulator
        :param initial: optional initial value
        :returns: MayBe of reduced value with f
        """
        if initial is None:
            if not self._ca:
                return MayBe()
        return MayBe(self._ca.foldl(f, initial))

    def foldr[R](self, f: Callable[[D, R], R], initial: R | None = None) -> MayBe[R]:
        """Reduces DEQueue right to left.

        :param f: reducing function, second argument is for accumulator
        :param initial: optional initial value
        :returns: MayBe of reduced value with f
        """
        if initial is None:
            if not self._ca:
                return MayBe()
        return MayBe(self._ca.foldr(f, initial))

    def map[U](self, f: Callable[[D], U]) -> DEQueue[U]:
        """Map f over the DEQueue left to right, retain original order.

        :returns: new DEQueue
        """
        return DEQueue(map(f, self._ca))


def de_queue[D](*ds: D) -> DEQueue[D]:
    """DEQueue factory function."""
    return DEQueue(ds)
