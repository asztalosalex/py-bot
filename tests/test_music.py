from unittest.mock import MagicMock

import pytest

from bot.cogs.music import GuildMusicState, Music


@pytest.fixture
def music_cog():
    return Music(bot=MagicMock())


@pytest.mark.parametrize(
    "query,expected",
    [
        ("bohemian rhapsody", False),
        ("my favorite playlist song", False),
        ("https://youtube.com/watch?v=abc123", False),
        ("https://youtube.com/watch?v=abc123&list=PLxyz", True),
    ],
)
def test_is_playlist(music_cog, query, expected):
    assert music_cog.is_playlist(query) is expected


def test_shuffle_queue_reorders_without_losing_items():
    state = GuildMusicState(bot=MagicMock())
    items = [(f"title{i}", f"url{i}") for i in range(10)]
    for item in items:
        state.queue.put_nowait(item)

    assert state.shuffle_queue() is True

    remaining = []
    while not state.queue.empty():
        remaining.append(state.queue.get_nowait())

    assert sorted(remaining) == sorted(items)


def test_shuffle_queue_empty_returns_false():
    state = GuildMusicState(bot=MagicMock())
    assert state.shuffle_queue() is False
