# Copyright (c) 2021 José Manuel Barroso Galindo <theypsilon@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# You can download the latest version of this tool from:
# https://github.com/MiSTer-devel/Downloader_MiSTer

from downloader.config import default_config
from downloader.online_importer import OnlineImporter as ProductionOnlineImporter
from test.fake_file_downloader import FileDownloaderFactory
from test.fake_file_system import FileSystem
from test.fake_logger import NoLogger


class OnlineImporter(ProductionOnlineImporter):
    def __init__(self, file_downloader_factory=None, config=None, file_system=None):
        self.file_system = FileSystem() if file_system is None else file_system
        self.config = default_config() if config is None else config
        super().__init__(
            self.config,
            self.file_system,
            FileDownloaderFactory(self.config, self.file_system) if file_downloader_factory is None else file_downloader_factory,
            NoLogger())
