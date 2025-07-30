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
from typing import Never, TypeVar, overload

from pythonic_fp.circulararray import CA
from pythonic_fp.containers.maybe import MayBe
from pythonic_fp.fptools.function import swap

__all__ = ['LIFOQueue', 'lifo_queue']

D = TypeVar('D')


class LIFOQueue[D]:
    """
    Stateful Last In First Out (LIFO) data structure. Initial data
    pushed on in natural FIFO order.
    """

    __slots__ = ('_ca',)

    T = TypeVar('T')
    U = TypeVar('U')

    def __init__(self, *dss: Iterable[D]) -> None:
        """
        :param dss: takes one or no iterables
        :raises ValueError: if more than 1 iterable is given
        """
        if (size := len(dss)) > 1:
            msg = f'LIFOQueue expects at most 1 iterable argument, got {size}'
            raise ValueError(msg)
        self._ca = CA(dss[0]) if size == 1 else CA()

    def __bool__(self) -> bool:
        return len(self._ca) > 0

    def __len__(self) -> int:
        return len(self._ca)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, LIFOQueue):
            return False
        return self._ca == other._ca

    @overload
    def __getitem__(self, idx: int) -> D: ...
    @overload
    def __getitem__(self, idx: slice) -> Sequence[D]: ...

    def __getitem__(self, idx: int | slice) -> Never:
        if isinstance(idx, slice):
            msg = 'fptools_fp.queues.LIFOQueue is not slicable by design'
            raise NotImplementedError(msg)
        msg = 'fptools_fp.queues.LIFOQueue is not indexable by design'
        raise NotImplementedError(msg)

    def __iter__(self) -> Iterator[D]:
        return reversed(list(self._ca))

    def __repr__(self) -> str:
        if len(self) == 0:
            return 'LIFOQueue()'
        return 'LIFOQueue(' + ', '.join(map(repr, self._ca)) + ')'

    def __str__(self) -> str:
        return '|| ' + ' > '.join(map(str, self)) + ' ><'

    def copy(self) -> LIFOQueue[D]:
        """Copy.

        :returns: shallow copy of the LIFOQueue
        """
        return LIFOQueue(reversed(self._ca))

    def push(self, *ds: D) -> None:
        """Push an item onto LIFOQueue."""
        self._ca.pushr(*ds)

    def pop(self) -> MayBe[D]:
        """Pop top item off of LIFOQueue.

        :returns: MayBe of item popped from queue
        """
        if self._ca:
            return MayBe(self._ca.popr())
        return MayBe()

    def peak(self) -> MayBe[D]:
        """Peak lans in/next out. Does not consume data.

        :returns: MayBe of item at top of queue.
        """
        if self._ca:
            return MayBe(self._ca[-1])
        return MayBe()

    def fold[T](self, f: Callable[[T, D], T], initial: T | None = None) -> MayBe[T]:
        """Reduces in natural LIFO Order (newest to oldest.

        :param f: reducing function, second argument is for accumulator
        :param initial: Optional initial value
        :returns: MayBe of reduced value with f
        """
        if initial is None:
            if not self._ca:
                return MayBe()
        return MayBe(self._ca.foldr(swap(f), initial))

    def map[U](self, f: Callable[[D], U]) -> LIFOQueue[U]:
        """Map f over the LIFOQueue, retain original order.

        :returns: new LIFOQueue
        """
        return LIFOQueue(reversed(CA(map(f, reversed(self._ca)))))


def lifo_queue[D](*ds: D) -> LIFOQueue[D]:
    """LIFOQueue factory function."""
    return LIFOQueue(ds)
