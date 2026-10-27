import pytest

from beets.test.helper import IOMixin, PluginMixin, TestHelper
from beetsplug.duplicates import DuplicatesPlugin


class TestDuplicatesPlugin(PluginMixin, TestHelper, IOMixin):
    plugin = "duplicates"

    @pytest.fixture(autouse=True)
    def setup(self):
        self.setup_beets()
        self.dup_item = self.create_item(
            album="Pretend Album",
            albumartist="Pretend Artist",
            artist="Pretend Artist",
            title="Pretend Track",
            genres=["Original Genre"],
            mb_trackid="abc",
            mb_albumid="def",
        )
        try:
            yield
        finally:
            self.teardown_beets()
            self.dup_item = None

    def run_cmd(self, count=False, path=False) -> str:
        args = ["duplicates"]
        if count:
            args.append("--count")
        if path:
            args.append("--path")

        return self.run_with_output(*args).strip()

    def create_dups(self, count: int):
        for _ in range(count):
            self.lib.add(self.dup_item)

    def test_duplicate(self):
        self.create_dups(2)
        out = self.run_cmd()

        assert self.dup_item.artist in out
        assert self.dup_item.album in out
        assert self.dup_item.title in out

    def test_duplicate_path(self):
        self.create_dups(2)
        out = self.run_cmd(path=True)

        assert str(self.dup_item.filepath) in out

    def test_duplicate_with_count(self):
        self.create_dups(4)
        out = self.run_cmd(count=True)

        assert self.dup_item.artist in out
        assert self.dup_item.album in out
        assert self.dup_item.title in out
        assert out.endswith("3")

    def test_duplicate_path_with_count(self):
        self.create_dups(6)
        out = self.run_cmd(count=True, path=True)

        assert str(self.dup_item.filepath) in out
        assert out.endswith("5")

    def test_order_with_missing_tiebreak_field(self):
            """Regression test for #6227: using a field for _order() that doesn't exist
            shouldn't crash the program."""

            song1 = self.create_item(title="Song", bitrate=128000)
            song2 = self.create_item(title="Song", bitrate=320000)

            tiebreak = {"items": ["lossless", "bitrate"]}

            plugin = DuplicatesPlugin()
            result = plugin._order([song1, song2], tiebreak)

            assert result == [song2, song1]
