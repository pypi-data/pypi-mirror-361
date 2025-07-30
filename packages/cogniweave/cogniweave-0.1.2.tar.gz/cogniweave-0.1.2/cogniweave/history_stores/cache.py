from __future__ import annotations

import bisect
from collections import defaultdict
from functools import partial
from itertools import groupby
from typing import TYPE_CHECKING, Any, TypeVar, cast
from typing_extensions import override

from langchain_core.messages import BaseMessage  # noqa: TC002
from pydantic import BaseModel, Field, PrivateAttr
from sortedcontainers import SortedDict, SortedList

from .base import BaseHistoryStore

if TYPE_CHECKING:
    from collections.abc import Iterable


_T = TypeVar("_T", bound="Any")


class SessionCache(BaseModel):
    """Cache for a single session."""

    max_blocks: int

    blocks: dict[tuple[str, float], list[tuple[BaseMessage, float]]] = Field(
        default_factory=lambda: SortedDict(lambda x: x[1]), init=False
    )
    start_block_ts: float = Field(default=float("inf"), init=False)
    end_block_ts: float = Field(default=float("inf"), init=False)
    start_msg_ts: float = Field(default=float("inf"), init=False)
    end_msg_ts: float = Field(default=float("inf"), init=False)

    def _recompute_ranges(self) -> None:
        """Recompute the start and end timestamps for blocks and messages."""
        first_block = cast("SortedDict", self.blocks).keys()[0]
        last_block = cast("SortedDict", self.blocks).keys()[-1]

        self.start_block_ts = first_block[1]
        self.end_block_ts = last_block[1]

        self.start_msg_ts = self.blocks[first_block][0][1]
        self.end_msg_ts = self.blocks[last_block][-1][1]

    def add_messages(
        self, block_id: str, block_ts: float, messages: Iterable[tuple[BaseMessage, float]]
    ) -> None:
        """Add messages with timestamps to the cache for a specific block."""
        key = (block_id, float(block_ts))
        if key in self.blocks:
            cast("SortedList", self.blocks[key]).update(messages)
        else:
            self.blocks[key] = SortedList(messages, key=lambda x: x[1])
        while len(self.blocks) > self.max_blocks:
            cast("SortedDict", self.blocks).popitem(index=0)
        self._recompute_ranges()

    def get_blocks(self, start_time: float, end_time: float) -> list[tuple[str, float]]:
        """Get block IDs and their start timestamps within a time range."""
        return list(
            cast("SortedDict", self.blocks).irange(("", start_time), (chr(0x10FFFF), end_time))
        )

    def get_block_histories_with_timestamps(
        self, block_ids: list[str]
    ) -> list[tuple[BaseMessage, float]]:
        """Get messages with timestamps for specified block IDs."""
        result: list[tuple[BaseMessage, float]] = []
        for block_id in block_ids:
            for (bid, _), messages in self.blocks.items():
                if bid == block_id:
                    result.extend(messages)
        return result

    def get_messages(self, start_time: float, end_time: float) -> list[tuple[BaseMessage, float]]:
        """Get messages with timestamps within a time range."""
        keys = list(self.blocks.keys())
        block_ids = [k[0] for k in keys]
        timestamps = [k[1] for k in keys]
        start, end = (
            bisect.bisect_left(timestamps, start_time),
            bisect.bisect_right(timestamps, end_time) - 1,
        )
        left, right = max(0, start - 1), min(len(keys) - 1, end + 1)
        selected_ids = block_ids[left : right + 1]
        if not selected_ids:
            return []

        history = self.get_block_histories_with_timestamps(selected_ids)
        return [(msg, ts) for msg, ts in history if start_time <= ts <= end_time]


class BaseHistoryStoreWithCache(BaseHistoryStore):
    """
    Base class for history stores with caching capabilities.

    This class extends BaseHistoryStore to include caching functionality.
    It can be used as a base class for specific history store implementations
    that require caching.
    """

    _session_caches: dict[str, SessionCache] = PrivateAttr()
    _blocks_time_session_ids: dict[str, tuple[float, str]] = PrivateAttr(default_factory=dict)

    def __init__(
        self,
        *,
        db_url: str,
        echo: bool = False,
        max_cache_blocks: int = 20,
        **kwargs: Any,
    ) -> None:
        """
        Initialize the history store with caching capabilities.

        Args:
            db_url (str | None): Database URL for the history store.
            echo (bool): Whether to echo SQL statements.
            max_cache_blocks (int): Maximum number of blocks to cache per session.
            **kwargs: Additional keyword arguments for compatibility with subclasses.
        """
        super().__init__(db_url=db_url, echo=echo, **kwargs)
        self._session_caches = defaultdict(lambda: SessionCache(max_blocks=max_cache_blocks))

    @override
    def add_messages(
        self,
        messages: list[tuple[BaseMessage, float]],
        *,
        block_id: str,
        block_ts: float | None = None,
        session_id: str | None = None,
    ) -> None:
        """Persist a list of messages with timestamps to the store.

        Args:
            messages: List of (message, timestamp) pairs to store.
            block_id: Unique identifier for the message block.
            block_ts: Unix timestamp for the block start time.
            session_id: Optional session/user ID. Uses block_id if not provided.

        Return:
            None: Messages are persisted to the database.
        """
        if not messages:
            return
        session_id = session_id or block_id
        super().add_messages(messages, block_id=block_id, block_ts=block_ts, session_id=session_id)
        self._session_caches[session_id].add_messages(block_id, block_ts or 0.0, messages)
        self._blocks_time_session_ids[block_id] = (block_ts or 0.0, session_id)

    @override
    async def aadd_messages(
        self,
        messages: list[tuple[BaseMessage, float]],
        *,
        block_id: str,
        block_ts: float | None = None,
        session_id: str | None = None,
    ) -> None:
        """Async version of :meth:`add_messages`.

        Persist a list of messages with timestamps to the store asynchronously.

        Args:
            messages: List of (message, timestamp) pairs to store.
            block_id: Unique identifier for the message block.
            block_ts: Unix timestamp for the block start time.
            session_id: Optional session/user ID. Uses block_id if not provided.

        Return:
            None: Messages are persisted to the database.
        """
        if not messages:
            return
        session_id = session_id or block_id
        await super().aadd_messages(
            messages, block_id=block_id, block_ts=block_ts, session_id=session_id
        )
        self._session_caches[session_id].add_messages(block_id, block_ts or 0.0, messages)
        self._blocks_time_session_ids[block_id] = (block_ts or 0.0, session_id)

    @override
    def get_block_timestamp(self, block_id: str) -> float | None:
        """Get the start timestamp of a chat block.

        Args:
            block_id: The ID of the chat block to query.

        Return:
            float | None: Unix timestamp of block start time, or None if not found.
        """
        if block_id in self._blocks_time_session_ids:
            return self._blocks_time_session_ids[block_id][0]
        return super().get_block_timestamp(block_id)

    @override
    async def aget_block_timestamp(self, block_id: str) -> float | None:
        """Async version of get_block_timestamp.

        Args:
            block_id: The ID of the chat block to query.

        Return:
            float | None: Unix timestamp of block start time, or None if not found.
        """
        if block_id in self._blocks_time_session_ids:
            return self._blocks_time_session_ids[block_id][0]
        return await super().aget_block_timestamp(block_id)

    @override
    def get_block_history_with_timestamps(self, block_id: str) -> list[tuple[BaseMessage, float]]:
        """Get all messages in a block with their timestamps.

        Args:
            block_id: The ID of the chat block to query.

        Return:
            list[tuple[BaseMessage, float]]: List of (message, timestamp) pairs in chronological order.
        """
        if block_id in self._blocks_time_session_ids:
            cache = self._session_caches[self._blocks_time_session_ids[block_id][1]]
            return cache.get_block_histories_with_timestamps([block_id])
        return super().get_block_history_with_timestamps(block_id)

    @override
    async def aget_block_history_with_timestamps(
        self, block_id: str
    ) -> list[tuple[BaseMessage, float]]:
        """Async version of get_history_with_timestamps.

        Args:
            block_id: The ID of the chat block to query.

        Return:
            list[tuple[BaseMessage, float]]: List of (message, timestamp) pairs in chronological order.
        """
        if block_id in self._blocks_time_session_ids:
            cache = self._session_caches[self._blocks_time_session_ids[block_id][1]]
            return cache.get_block_histories_with_timestamps([block_id])
        return await super().aget_block_history_with_timestamps(block_id)

    @override
    def get_block_histories_with_timestamps(
        self, block_ids: list[str]
    ) -> list[tuple[BaseMessage, float]]:
        """Get messages with timestamps from multiple blocks, concatenated in order.

        Args:
            block_ids: List of block IDs to retrieve messages from.

        Return:
            list[tuple[BaseMessage, float]]: Combined list of (message, timestamp) pairs
                from all blocks, in chronological order.
        """
        existing_ids = set(block_ids) & set(self._blocks_time_session_ids.keys())
        session_blocks: dict[str, list[tuple[str, float]]] = defaultdict(list)
        ordered_history = SortedList(key=lambda x: x[1])

        for bid in existing_ids:
            timestamp, session = self._blocks_time_session_ids[bid]
            session_blocks[session].append((bid, timestamp))

        for session, blocks in session_blocks.items():
            cache = self._session_caches[session]
            for bid in blocks:
                ordered_history.update(cache.blocks[bid])

        missing_ids = set(block_ids) - existing_ids
        for bid in missing_ids:
            ordered_history.update(super().get_block_history_with_timestamps(bid))

        return list(ordered_history)

    @override
    async def aget_block_histories_with_timestamps(
        self, block_ids: list[str]
    ) -> list[tuple[BaseMessage, float]]:
        """Async version of get_histories_with_timestamps.

        Args:
            block_ids: List of block IDs to retrieve messages from.

        Return:
            list[tuple[BaseMessage, float]]: Combined list of (message, timestamp) pairs
                from all blocks, in chronological order.
        """
        existing_ids = set(block_ids) & set(self._blocks_time_session_ids.keys())
        session_blocks: dict[str, list[tuple[str, float]]] = defaultdict(list)
        ordered_history = SortedList(key=lambda x: x[1])

        for bid in existing_ids:
            timestamp, session = self._blocks_time_session_ids[bid]
            session_blocks[session].append((bid, timestamp))

        for session, blocks in session_blocks.items():
            cache = self._session_caches[session]
            for bid in blocks:
                ordered_history.update(cache.blocks[bid])

        missing_ids = set(block_ids) - existing_ids
        for bid in missing_ids:
            ordered_history.update(await super().aget_block_history_with_timestamps(bid))

        return list(ordered_history)

    @override
    def get_session_block_ids_with_timestamps(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        **kwargs: Any,
    ) -> list[tuple[str, float]]:
        """Get block IDs and their start timestamps for a session, optionally filtered by time range.

        Args:
            session_id: The session/user ID to query.
            limit: Maximum number of blocks to return (returns most recent if specified).
            start_time: Optional minimum timestamp (inclusive) to filter blocks.
            end_time: Optional maximum timestamp (inclusive) to filter blocks.

        Return:
            list[tuple[str, float]]: List of (block_id, start_timestamp) pairs in chronological order.
                Returns empty list if session not found or no matching blocks.
        """
        if limit is not None and limit <= 0:
            return []

        start_time = start_time or 0.0
        end_time = end_time or float("inf")
        from_first = kwargs.get("from_first", False)

        cache = self._session_caches[session_id]
        get_blocks_from_db = partial(
            super().get_session_block_ids_with_timestamps, session_id=session_id
        )

        result: list[tuple[str, float]] = []
        if start_time >= cache.start_block_ts:
            result = cache.get_blocks(start_time=start_time, end_time=end_time)
        elif end_time >= cache.start_block_ts:
            if from_first:
                result = get_blocks_from_db(
                    limit=limit,
                    start_time=start_time,
                    end_time=cache.start_block_ts,
                )
                if limit is not None and len(result) < limit:
                    result += cache.get_blocks(
                        start_time=cache.start_block_ts,
                        end_time=end_time,
                    )
            else:
                result = cache.get_blocks(
                    start_time=cache.start_block_ts,
                    end_time=end_time,
                )
                if limit is None or len(result) < limit:
                    result = (
                        get_blocks_from_db(
                            limit=limit + 2 - len(result) if limit else None,
                            start_time=start_time,
                            end_time=cache.start_block_ts,
                        )
                        + result
                    )
        if result:
            result = self.deduplicate_unhashable(result)
            if limit is not None:
                result = result[:limit] if from_first else result[-limit:]
            return result

        return get_blocks_from_db(
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            **kwargs,
        )

    @override
    async def aget_session_block_ids_with_timestamps(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        **kwargs: Any,
    ) -> list[tuple[str, float]]:
        """Async version of get_session_block_ids_with_timestamps.

        Args:
            session_id: The session/user ID to query.
            limit: Maximum number of blocks to return (returns most recent if specified).
            start_time: Optional minimum timestamp (inclusive) to filter blocks.
            end_time: Optional maximum timestamp (inclusive) to filter blocks.

        Return:
            list[tuple[str, float]]: List of (block_id, start_timestamp) pairs in chronological order.
                Returns empty list if session not found or no matching blocks.
        """
        if limit is not None and limit <= 0:
            return []

        start_time = start_time or 0.0
        end_time = end_time or float("inf")
        from_first = kwargs.get("from_first", False)

        cache = self._session_caches[session_id]
        aget_blocks_from_db = partial(
            super().aget_session_block_ids_with_timestamps, session_id=session_id
        )

        result: list[tuple[str, float]] = []
        if start_time >= cache.start_block_ts:
            result = cache.get_blocks(start_time=start_time, end_time=end_time)
        elif end_time >= cache.start_block_ts:
            if from_first:
                result = await aget_blocks_from_db(
                    limit=limit,
                    start_time=start_time,
                    end_time=cache.start_block_ts,
                )
                if limit is not None and len(result) < limit:
                    result += cache.get_blocks(
                        start_time=cache.start_block_ts,
                        end_time=end_time,
                    )
            else:
                result = cache.get_blocks(
                    start_time=cache.start_block_ts,
                    end_time=end_time,
                )
                if limit is None or len(result) < limit:
                    result = (
                        await aget_blocks_from_db(
                            limit=limit + 2 - len(result) if limit else None,
                            start_time=start_time,
                            end_time=cache.start_block_ts,
                        )
                        + result
                    )
        if result:
            result = self.deduplicate_unhashable(result)
            if limit is not None:
                result = result[:limit] if from_first else result[-limit:]
            return result

        return await aget_blocks_from_db(
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            **kwargs,
        )

    @override
    def get_session_history_with_timestamps(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        **kwargs: Any,
    ) -> list[tuple[BaseMessage, float]]:
        """Get all messages with timestamps for a session, optionally filtered by time range.

        Args:
            session_id: The session/user ID to query.
            limit: Maximum number of messages to return (returns most recent if specified).
            start_time: Optional minimum timestamp (inclusive) to filter messages.
            end_time: Optional maximum timestamp (inclusive) to filter messages.

        Return:
            list[tuple[BaseMessage, float]]: List of (message, timestamp) pairs in chronological order.
                Returns empty list if session not found or no matching messages.
        """
        if limit is not None and limit <= 0:
            return []

        start_time = start_time or 0.0
        end_time = end_time or float("inf")
        from_first = kwargs.get("from_first", False)

        cache = self._session_caches[session_id]
        get_history_from_db = partial(
            super().get_session_history_with_timestamps, session_id=session_id
        )

        result: list[tuple[BaseMessage, float]] = []
        if start_time >= cache.start_msg_ts:
            result = cache.get_messages(start_time=start_time, end_time=end_time)
        elif end_time >= cache.start_msg_ts:
            if from_first:
                result = get_history_from_db(
                    limit=limit,
                    start_time=start_time,
                    end_time=cache.start_msg_ts,
                )
                if limit is not None and len(result) < limit:
                    result += cache.get_messages(
                        start_time=cache.start_msg_ts,
                        end_time=end_time,
                    )
            else:
                result = cache.get_messages(
                    start_time=cache.start_msg_ts,
                    end_time=end_time,
                )
                if limit is None or len(result) < limit:
                    result = (
                        get_history_from_db(
                            limit=limit + 2 - len(result) if limit else None,
                            start_time=start_time,
                            end_time=cache.start_msg_ts,
                        )
                        + result
                    )
        if result:
            result = self.deduplicate_unhashable(result)
            if limit is not None:
                result = result[:limit] if from_first else result[-limit:]
            return result

        return get_history_from_db(
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            **kwargs,
        )

    @override
    async def aget_session_history_with_timestamps(
        self,
        session_id: str,
        *,
        limit: int | None = None,
        start_time: float | None = None,
        end_time: float | None = None,
        **kwargs: Any,
    ) -> list[tuple[BaseMessage, float]]:
        """Async version of get_session_history_with_timestamps.

        Args:
            session_id: The session/user ID to query.
            limit: Maximum number of messages to return (returns most recent if specified).
            start_time: Optional minimum timestamp (inclusive) to filter messages.
            end_time: Optional maximum timestamp (inclusive) to filter messages.

        Return:
            list[tuple[BaseMessage, float]]: List of (message, timestamp) pairs in chronological order.
                Returns empty list if session not found or no matching messages.
        """
        if limit is not None and limit <= 0:
            return []

        start_time = start_time or 0.0
        end_time = end_time or float("inf")
        from_first = kwargs.get("from_first", False)

        cache = self._session_caches[session_id]
        aget_history_from_db = partial(
            super().aget_session_history_with_timestamps, session_id=session_id
        )

        result: list[tuple[BaseMessage, float]] = []
        if start_time >= cache.start_msg_ts:
            result = cache.get_messages(start_time=start_time, end_time=end_time)
        elif end_time >= cache.start_msg_ts:
            if from_first:
                result = await aget_history_from_db(
                    limit=limit,
                    start_time=start_time,
                    end_time=cache.start_msg_ts,
                )
                if limit is not None and len(result) < limit:
                    result += cache.get_messages(
                        start_time=cache.start_msg_ts,
                        end_time=end_time,
                    )
            else:
                result = cache.get_messages(
                    start_time=cache.start_msg_ts,
                    end_time=end_time,
                )
                if limit is None or len(result) < limit:
                    result = (
                        await aget_history_from_db(
                            limit=limit + 2 - len(result) if limit else None,
                            start_time=start_time,
                            end_time=cache.start_msg_ts,
                        )
                        + result
                    )
        if result:
            result = self.deduplicate_unhashable(result)
            if limit is not None:
                result = result[:limit] if from_first else result[-limit:]
            return result

        return await aget_history_from_db(
            limit=limit,
            start_time=start_time,
            end_time=end_time,
            **kwargs,
        )

    @staticmethod
    def deduplicate_unhashable(
        messages: list[tuple[_T, float]],
    ) -> list[tuple[_T, float]]:
        """Removes duplicate messages that are unhashable.

        Args:
            messages: List of (message, timestamp) pairs to deduplicate.

        Return:
            list[tuple[_T, float]]: List of unique (message, timestamp) pairs.
        """
        return [
            next(group)
            for _, group in groupby(
                sorted([(msg, round(ts, 3)) for msg, ts in messages], key=lambda x: x[1])
            )
        ]
