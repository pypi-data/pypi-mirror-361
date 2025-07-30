# Copyright (c) 2022, California Institute of Technology and contributors
#
# You should have received a copy of the licensing terms for this
# software included in the file "LICENSE" located in the top-level
# directory of this package. If you did not, you can view a copy at
# https://git.ligo.org/ngdd/arrakis-python/-/raw/main/LICENSE

"""Series block representation of timeseries data."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from functools import cached_property
from typing import TYPE_CHECKING, Generic, TypeVar

import numpy
import pyarrow
import pyarrow.compute

from .channel import Channel

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator, KeysView
    from numbers import Real


ChannelLike = TypeVar("ChannelLike", bound=Channel)


class Time(int, Enum):
    SECONDS = 1_000_000_000
    MILLISECONDS = 1_000_000
    MICROSECONDS = 1_000
    NANOSECONDS = 1
    s = 1_000_000_000
    ms = 1_000_000
    us = 1_000
    ns = 1


class Freq(Enum):
    GHz = 1_000_000_000
    MHz = 1_000_000
    kHz = 1_000  # noqa: N815
    Hz = 1

    def __rmul__(self, other: Real) -> int:  # type: ignore
        return int((self.value / other) * Time.s)  # type: ignore


def time_as_ns(time: float) -> int:
    """Convert a timestamp from seconds to nanoseconds.

    Parameters
    ----------
    time : float
        The timestamp to convert, in seconds.

    Returns
    -------
    int
        The converted timestamp, in nanoseconds.

    """
    seconds = int(time) * Time.s
    nanoseconds = int((time % 1)) * Time.s
    return seconds + nanoseconds


@dataclass(frozen=True)
class Series(Generic[ChannelLike]):
    """Single-channel timeseries data for a given timestamp.

    Parameters
    ----------
    time_ns : int
        The timestamp associated with this data, in nanoseconds.
    data : numpy.ndarray
        The timeseries data.
    channel : Channel
        Channel metadata associated with this timeseries.

    """

    time_ns: int
    data: numpy.ndarray | numpy.ma.MaskedArray
    channel: ChannelLike

    @cached_property
    def time(self) -> float:
        """Timestamp associated with this data, in seconds."""
        return self.time_ns / Time.s

    @property
    def t0(self) -> float:
        """Timestamp associated with this data, in seconds."""
        return self.time

    @cached_property
    def duration(self) -> float:
        """Series duration in seconds."""
        return self.duration_ns / Time.s

    @cached_property
    def duration_ns(self) -> int:
        """Series duration in nanoseconds."""
        return int((len(self) * Time.s) / self.sample_rate)

    @property
    def dt(self) -> float:
        """The time separation in seconds between successive samples."""
        return 1 / self.sample_rate

    @property
    def name(self) -> str:
        """Channel name."""
        return str(self.channel)

    @property
    def data_type(self) -> numpy.dtype:
        """Data type of the data array's elements."""
        return self.data.dtype

    @property
    def dtype(self) -> numpy.dtype:
        """Data type of the data array's elements."""
        return self.data.dtype

    @property
    def sample_rate(self) -> float:
        """Data rate for this series in samples per second (Hz)."""
        return self.channel.sample_rate

    @cached_property
    def times(self) -> numpy.ndarray:
        """The array of times corresponding to all data points in the series."""
        return numpy.arange(len(self)) * self.dt + self.time

    @property
    def has_nulls(self):
        """Whether the timeseries data contains any null values."""
        return numpy.ma.is_masked(self.data)

    def __len__(self) -> int:
        return len(self.data)


@dataclass(frozen=True)
class SeriesBlock(Generic[ChannelLike]):
    """Series block containing timeseries for channels for a given timestamp.

    Parameters
    ----------
    time_ns : int
        The timestamp associated with this data, in nanoseconds.
    data : dict[str, numpy.ndarray]
        Mapping between channels and timeseries.
    channels : dict[str, Channel]
        Channel metadata associated with this data block.

    """

    time_ns: int
    data: dict[str, numpy.ndarray] | dict[str, numpy.ma.MaskedArray]
    channels: dict[str, ChannelLike] = field(default_factory=dict)
    _duration_ns: int = field(init=False, default=0)

    def __post_init__(self):
        # various validation checks
        #
        # check that the channel lists are consistent
        assert set(self.data) == set(self.channels), (
            "data and channels dicts have different keys"
        )
        # check that the duration of all Series are consistent
        for channel, data in self.data.items():
            duration_ns = int((len(data) * Time.s) / self.channels[channel].sample_rate)
            if self._duration_ns == 0:
                # NOTE: this is a hacky way to set an attribute of a
                # frozen dataclass
                object.__setattr__(self, "_duration_ns", duration_ns)
            assert duration_ns == self._duration_ns, "Series durations do not agree"

    @cached_property
    def time(self) -> float:
        """Timestamp associated with this block, in seconds."""
        return self.time_ns / Time.s

    @property
    def t0(self) -> float:
        """Timestamp associated with this block, in seconds."""
        return self.time

    @cached_property
    def duration(self) -> float:
        """Duration of this block, in seconds."""
        return self._duration_ns / Time.s

    @property
    def duration_ns(self) -> int:
        """Duration of this block, in nanoseconds."""
        return self._duration_ns

    def __getitem__(self, channel: str) -> Series:
        return Series(self.time_ns, self.data[channel], self.channels[channel])

    def __len__(self) -> int:
        return len(self.data)

    def keys(self) -> KeysView[str]:
        return self.data.keys()

    def items(self) -> Generator[tuple[str, Series], None, None]:
        for channel in self.keys():
            yield (channel, self[channel])

    def values(self) -> list[Series]:
        return [self[channel] for channel in self.keys()]

    def filter(self, channels: list[str] | None = None) -> SeriesBlock:
        """Filter a block based on criteria.

        FIXME: more info needed

        Parameters
        ----------
        channels : list[str], optional
            If specified, keep only these channels.

        Returns
        -------
        SeriesBlock
            The filtered series.

        """
        if not channels:
            return self

        data = {channel: self.data[channel] for channel in channels}
        if self.channels:
            channel_dict = {channel: self.channels[channel] for channel in channels}
        else:
            channel_dict = self.channels

        return type(self)(self.time_ns, data, channel_dict)

    def create_gaps(self, channels: Iterable[Channel]) -> SeriesBlock:
        """Add channels with all null values (gaps).

        Parameters
        ----------
        channels : Iterable[Channel]
            The channels to create gaps for. Any channels currently present
            will be ignored.

        Returns
        -------
        SeriesBlock
            The block with additional gaps present.

        """
        series_dict = self.data
        channel_dict = self.channels
        for channel in channels:
            if channel in channel_dict:
                continue
            size = int(channel.sample_rate * self.duration_ns) // Time.s
            series_dict[channel.name] = numpy.ma.masked_all(size, dtype=channel.dtype)
            channel_dict[channel.name] = channel

        return type(self)(self.time_ns, series_dict, channel_dict)

    def to_column_batch(self) -> pyarrow.RecordBatch:
        """Create a row-based record batch from a series block.

        Returns
        -------
        pyarrow.RecordBatch
            A record batch, with a 'time' column with the timestamp
            and channel columns with all channels to publish.

        """
        schema = self._generate_column_schema()
        return pyarrow.RecordBatch.from_arrays(
            [
                pyarrow.array([self.time_ns], type=schema.field("time").type),
                *[
                    pyarrow.array(
                        [pyarrow.array(series)], type=schema.field(channel).type
                    )
                    for channel, series in self.data.items()
                ],
            ],
            schema=schema,
        )

    def to_row_batches(self, partitions: dict) -> Iterator[pyarrow.RecordBatch]:
        """Create column-based record batches from a series block.

        Yields
        -------
        pyarrow.RecordBatch
            Record batches, one per data type. The record batches have a
            'time' column with the timestamp, a 'channel' column with
            the channel name, and a 'data' column containing the timeseries.

        """
        # group channels by partitions
        channels_by_part = defaultdict(list)
        for channel in self.keys():
            if channel in partitions:
                partition = partitions[channel]
                channels_by_part[partition].append(channel)

        # generate column-based record batches
        for partition_id, channels in channels_by_part.items():
            # all channels have the same data type
            dtype = self.channels[channels[0]].data_type
            schema = self._generate_row_schema(pyarrow.from_numpy_dtype(dtype))
            series: list[numpy.ndarray] = [
                pyarrow.array(self.data[channel]) for channel in channels
            ]
            yield (
                partition_id,
                pyarrow.RecordBatch.from_arrays(
                    [
                        pyarrow.array(
                            numpy.full(len(channels), self.time_ns),
                            type=schema.field("time").type,
                        ),
                        pyarrow.array(channels, type=schema.field("channel").type),
                        pyarrow.array(series, type=schema.field("data").type),
                    ],
                    schema=schema,
                ),
            )

    @classmethod
    def from_column_batch(
        cls,
        batch: pyarrow.RecordBatch,
        channels: dict[str, ChannelLike],
    ) -> SeriesBlock:
        """Create a series block from a record batch.

        Parameters
        ----------
        batch : pyarrow.RecordBatch
            A record batch, with a 'time' column with the timestamp
            and channel columns with all channels to publish.
        channels : dict[str, Channel]
            Channel metadata.  The metadata for the channels defined
            in the batch will be extracted from this dictionary, so
            this dictionary may include metadata for additional
            channels now included in the batch.

        Returns
        -------
        SeriesBlock
            The block representation of the record batch.

        """
        time = batch.column("time").to_numpy()[0]
        fields: list[pyarrow.field] = list(batch.schema)
        channel_names = [field.name for field in fields[1:]]
        series_dict = {
            channel: _arrow_to_numpy_array(
                pyarrow.compute.list_flatten(batch.column(channel))
            )
            for channel in channel_names
        }
        channel_dict = {channel: channels[channel] for channel in channel_names}
        return cls(time, series_dict, channel_dict)

    @classmethod
    def from_row_batch(
        cls,
        batch: pyarrow.RecordBatch,
        channels: dict[str, ChannelLike],
    ) -> SeriesBlock:
        """Create a series block from a record batch.

        Parameters
        ----------
        batch : pyarrow.RecordBatch
            A record batch, with a 'time' column with the timestamp, a
            'channel' column with the channel name, and a 'data' column
            containing the timeseries.
        channels : dict[str, Channel]
            Channel metadata.  The metadata for the channels defined
            in the batch will be extracted from this dictionary, so
            this dictionary may include metadata for additional
            channels now included in the batch.

        Returns
        -------
        SeriesBlock
            The block representation of the record batch.

        """
        time = batch.column("time").to_numpy()[0]
        channel_names = batch.column("channel").to_pylist()
        data = batch.column("data")
        series_dict = {}
        channel_dict = {}
        for idx, channel in enumerate(channel_names):
            series_dict[channel] = _arrow_to_numpy_array(pyarrow.array(data[idx]))
            channel_dict[channel] = channels[channel]
        return cls(time, series_dict, channel_dict)

    def _generate_column_schema(self) -> pyarrow.Schema:
        fields = [pyarrow.field("time", pyarrow.int64())]
        for channel, arr in self.data.items():
            dtype = pyarrow.from_numpy_dtype(arr.dtype)
            fields.append(pyarrow.field(channel, pyarrow.list_(dtype)))
        return pyarrow.schema(fields)

    def _generate_row_schema(self, dtype: pyarrow.DataType) -> pyarrow.Schema:
        return pyarrow.schema(
            [
                pyarrow.field("time", pyarrow.int64()),
                pyarrow.field("channel", pyarrow.string()),
                pyarrow.field("data", pyarrow.list_(dtype)),
            ]
        )


# backwards compatibility with previous name
DataBlock = SeriesBlock


def concatenate_blocks(*blocks: SeriesBlock) -> SeriesBlock:
    """Join a sequence of timeseries blocks into a single block.

    If the SeriesBlock arguments are not sequential in time an
    AssertionError will be thrown.

    Parameters
    ----------
    *blocks : SeriesBlock
        The timeseries blocks to concatenate.

    Returns
    -------
    SeriesBlock
        The combined timeseries block.

    """
    channel_dict = blocks[0].channels
    channel_set = set(channel_dict)
    start_time_ns = end_time_ns = blocks[0].time_ns
    duration_ns = 0
    for block in blocks:
        assert set(block.data.keys()) == channel_set, (
            "all blocks must contain the same channel sets"
        )
        assert block.time_ns == end_time_ns, (
            f"block start time ({block.time_ns}) does not match "
            f"concatenated block end time ({end_time_ns})"
        )
        duration_ns += block.duration_ns
        end_time_ns += block.duration_ns
    series_dict: dict[str, numpy.ndarray] = {}
    for channel in channel_set:
        series_dict[str(channel)] = numpy.concatenate(
            [block[str(channel)].data for block in blocks]
        )
    return SeriesBlock(start_time_ns, series_dict, channel_dict)


def combine_blocks(*blocks: SeriesBlock) -> SeriesBlock:
    """Combine multiple SeriesBlocks from the same time into a single SeriesBlock

    Each block must contain a distinct set of channels, and the time
    properties of each block must agree, otherwise an AssertionError
    will be thrown.

    Parameters
    ----------
    *blocks : SeriesBlock
        The blocks to combine.

    Returns
    -------
    SeriesBlock
        The combined block.

    """
    time_ns = blocks[0].time_ns
    duration_ns = blocks[0].duration_ns
    series_dict: dict[str, numpy.ndarray] = {}
    channel_dict: dict[str, Channel] = {}
    for block in blocks:
        assert block.time_ns == time_ns, "all block times must agree"
        assert block.duration_ns == duration_ns, "all block durations must agree"
        for channel, series in block.items():
            assert channel not in series_dict, (
                f"channel {channel} has already been included from another block"
            )
            series_dict[channel] = series.data
            channel_dict[channel] = series.channel
    return SeriesBlock(time_ns, series_dict, channel_dict)


def _arrow_to_numpy_array(arrow_array: pyarrow.Array) -> numpy.ndarray:
    """Convert an Arrow array to a numpy ndarray."""
    bitmap_buffer, data_buffer = arrow_array.buffers()
    if bitmap_buffer is None:
        # no null values
        return arrow_array.to_numpy()
    offset = arrow_array.offset

    # compute mask from arrow bitmap
    # see https://arrow.apache.org/docs/format/Columnar.html#validity-bitmaps
    bitmap = numpy.frombuffer(bitmap_buffer, numpy.uint8, len(bitmap_buffer))
    length = len(arrow_array) + offset
    shape = (len(bitmap), 8)
    mask = 1 - numpy.unpackbits(bitmap).reshape(shape)[:, ::-1].reshape(-1)[:length]

    # create masked array
    dtype = _arrow_to_numpy_dtype(arrow_array.type)
    data_array = numpy.frombuffer(data_buffer, dtype, length)[offset:]
    array = numpy.ma.array(data_array, mask=mask)
    assert len(array) == len(arrow_array)
    return array


def _arrow_to_numpy_dtype(dtype: pyarrow.DataType) -> numpy.dtype:
    """Return the numpy dtype equivalent to its Arrow dtype."""
    arrow_dtype = str(dtype)
    if arrow_dtype == "float":
        return numpy.dtype("float32")
    if arrow_dtype == "double":
        return numpy.dtype("float64")
    return numpy.dtype(arrow_dtype)
