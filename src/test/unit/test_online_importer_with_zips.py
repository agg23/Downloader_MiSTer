# Copyright (c) 2021-2022 José Manuel Barroso Galindo <theypsilon@gmail.com>

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

import unittest

from downloader.config import default_config
from downloader.constants import K_BASE_PATH, K_ZIP_FILE_COUNT_THRESHOLD, K_ZIP_ACCUMULATED_MB_THRESHOLD
from test.fake_file_system_factory import fs_data
from test.fake_importer_implicit_inputs import ImporterImplicitInputs
from test.objects import db_test_descr, empty_zip_summary, store_descr, empty_test_store, media_fat
from test.objects import file_a, zipped_file_a_descr, zip_desc
from test.fake_online_importer import OnlineImporter
from test.zip_objects import store_with_unzipped_cheats, cheats_folder_zip_desc, \
    cheats_folder_nes_file_path, \
    summary_json_from_cheats_folder, \
    zipped_files_from_cheats_folder, cheats_folder_id, cheats_folder_sms_file_path, cheats_folder_folders, \
    cheats_folder_files, with_installed_cheats_folder_on_fs


class TestOnlineImporterWithZips(unittest.TestCase):

    def setUp(self) -> None:
        self.config = default_config()
        self.implicit_inputs = ImporterImplicitInputs(config=self.config)
        self.sut = OnlineImporter.from_implicit_inputs(self.implicit_inputs)

    def download(self, db, store):
        self.sut.add_db(db, store)
        self.sut.download(False)
        return store

    def test_download_zipped_cheats_folder___on_empty_store_from_summary_and_contents_files_when_file_count_threshold_is_surpassed___installs_from_zip_content(self):
        self.config[K_ZIP_FILE_COUNT_THRESHOLD] = 0  # This will cause to unzip the contents
        store = self.download_zipped_cheats_folder(empty_test_store(), from_zip_content=True)
        self.assertEqual(store_with_unzipped_cheats(url=False), store)

    def test_download_zipped_cheats_folder___on_empty_store_from_internal_summary_and_contents_file_when_file_count_threshold_is_surpassed___installs_from_zip_content(self):
        self.config[K_ZIP_FILE_COUNT_THRESHOLD] = 0  # This will cause to unzip the contents
        store = self.download_zipped_cheats_folder(empty_test_store(), from_zip_content=True, is_summary_internal=True)
        self.assertEqual(store_with_unzipped_cheats(url=False, is_summary_internal=True), store)

    def test_download_zipped_cheats_folder___on_empty_store_from_summary_and_contents_files_when_accumulated_mb_threshold_is_surpassed___installs_from_zip_content(self):
        self.config[K_ZIP_ACCUMULATED_MB_THRESHOLD] = 0  # This will cause to unzip the contents
        store = self.download_zipped_cheats_folder(empty_test_store(), from_zip_content=True)
        self.assertEqual(store_with_unzipped_cheats(url=False), store)

    def test_download_zipped_cheats_folder___on_empty_store_from_summary_file_but_no_contents_because_thresholds_are_not_surpassed___installs_from_url(self):
        self.assertEqual(store_with_unzipped_cheats(), self.download_zipped_cheats_folder(empty_test_store(), from_zip_content=False))

    def test_download_zipped_cheats_folder___on_empty_store_from_internal_summary_but_no_contents_because_thresholds_are_not_surpassed___installs_from_zip_content(self):
        expected_store = store_with_unzipped_cheats(is_summary_internal=True)
        self.assertEqual(expected_store, self.download_zipped_cheats_folder(empty_test_store(), from_zip_content=False, is_summary_internal=True))

    def test_download_zipped_cheats_folder___with_already_downloaded_summary_file___restores_file_contained_in_summary(self):
        self.assertEqual(store_with_unzipped_cheats(), self.download_zipped_cheats_folder(store_with_unzipped_cheats(), from_zip_content=False, save=False))

    def test_download_zipped_cheats_folder___with_already_stored_internal_summary___restores_file_contained_in_summary(self):
        expected_store = store_with_unzipped_cheats(is_summary_internal=True)
        self.assertEqual(expected_store, self.download_zipped_cheats_folder(store_with_unzipped_cheats(), from_zip_content=False, is_summary_internal=True))

    def test_download_zipped_cheats_folder___with_summary_file_containing_already_existing_files___updates_files_in_the_store_now_pointing_to_summary(self):
        self.assertEqual(store_with_unzipped_cheats(), self.download_zipped_cheats_folder(store_with_unzipped_cheats(zip_id=False, zips=False), from_zip_content=False))

    def test_download_zipped_cheats_folder___with_internal_summary_containing_already_existing_files___updates_files_in_the_store_now_pointing_to_summary(self):
        expected_store = store_with_unzipped_cheats(is_summary_internal=True)
        self.assertEqual(expected_store, self.download_zipped_cheats_folder(store_with_unzipped_cheats(zip_id=False, zips=False), from_zip_content=False, is_summary_internal=True))

    def test_download_zipped_contents___on_existing_store_with_zips___removes_old_zip_id_and_inserts_new_one(self):
        with_installed_cheats_folder_on_fs(self.implicit_inputs.file_system_state)

        different_zip_id = 'a_different_id'
        different_folder = "Different"

        store = self.download(db_test_descr(zips={
            different_zip_id: zip_desc([different_folder], "./", different_folder, summary={
                "files": {file_a: zipped_file_a_descr(different_zip_id)},
                "files_count": 1,
                "folders": {different_folder: {"zip_id": different_zip_id}},
                "folders_count": 1,
            })
        }), store_with_unzipped_cheats())

        self.assertReports([file_a])
        self.assertEqual({
            K_BASE_PATH: "/media/fat",
            "files": {file_a: zipped_file_a_descr(different_zip_id, url=True)},
            "offline_databases_imported": [],
            "folders": {different_folder: {"zip_id": different_zip_id}},
            "zips": {different_zip_id: zip_desc([different_folder], "./", different_folder)}
        }, store)
        self.assertFalse(self.sut.file_system.is_file(cheats_folder_nes_file_path))
        self.assertFalse(self.sut.file_system.is_file(cheats_folder_sms_file_path))
        self.assertTrue(self.sut.file_system.is_file(file_a))

    def test_download_non_zipped_contents___with_file_already_on_store_with_zip_id___removes_zip_id_from_file_on_store(self):
        store = self.download(db_test_descr(
            folders=cheats_folder_folders(zip_id=False),
            files=cheats_folder_files(zip_id=False),
        ), store_with_unzipped_cheats())
        self.assertReports(list(cheats_folder_files()))
        self.assertEqual(store_with_unzipped_cheats(zip_id=False, zips=False, tags=False), store)

    def test_download_zip_summary___after_previous_summary_is_present_when_new_summary_is_found_with_no_file_changes___updates_summary_hash(self):
        with_installed_cheats_folder_on_fs(self.implicit_inputs.file_system_state)

        previous_store = store_with_unzipped_cheats(url=False)
        expected_store = store_with_unzipped_cheats(url=False, summary_hash="something_new")

        actual_store = self.download(db_test_descr(zips={
            cheats_folder_id: cheats_folder_zip_desc(summary_hash="something_new", summary=summary_json_from_cheats_folder())
        }), previous_store)

        self.assertReports([])
        self.assertEqual(expected_store, actual_store)

    def test_download_zip_summary_without_files___for_the_first_time___adds_zip_id_to_store(self):
        zip_descriptions = {cheats_folder_id: cheats_folder_zip_desc(summary=empty_zip_summary())}
        expected_store = store_descr(zips=zip_descriptions)
        actual_store = self.download(db_test_descr(zips=zip_descriptions), empty_test_store())
        self.assertEqual(expected_store, actual_store)

    def test_download_zipped_cheats_folder___with_summary_file_containing_already_existing_files_but_old_hash___when_file_count_threshold_is_surpassed_but_network_fails____reports_error_and_installs_from_zip_content_using_store_information(self):
        self.config[K_ZIP_FILE_COUNT_THRESHOLD] = 0  # This will cause to unzip the contents
        self.implicit_inputs.network_state.remote_failures['/tmp/cheats_id_summary.json.zip'] = 99
        self.assertEqual(fs_data(), self.sut.fs_data)

        store = self.download(db_test_descr(zips={
            cheats_folder_id: cheats_folder_zip_desc(
                zipped_files=zipped_files_from_cheats_folder(),
                summary=summary_json_from_cheats_folder()
            )
        }), store_with_unzipped_cheats(url=False, summary_hash='old'))

        self.assertReports(list(cheats_folder_files()), errors=['/tmp/cheats_id_summary.json.zip'], save=False)
        self.assertEqual(store_with_unzipped_cheats(url=False, summary_hash='old'), store)
        self.assertEqual(fs_data(
            folders=cheats_folder_folders(zip_id=False),
            files=cheats_folder_files(zip_id=False),
        ), self.sut.fs_data)

    def test_download_zipped_cheats_folder___on_empty_store_when_file_count_threshold_is_surpassed_but_network_fails___reports_error_and_installs_nothing(self):
        self.config[K_ZIP_FILE_COUNT_THRESHOLD] = 0  # This will cause to unzip the contents
        self.implicit_inputs.network_state.remote_failures['/tmp/cheats_id_summary.json.zip'] = 99
        store = self.download(db_test_descr(zips={
            cheats_folder_id: cheats_folder_zip_desc(
                zipped_files=zipped_files_from_cheats_folder(),
                summary=summary_json_from_cheats_folder()
            )
        }), empty_test_store())
        self.assertReports([], errors=['/tmp/cheats_id_summary.json.zip'], save=False)
        self.assertEqual(empty_test_store(), store)
        self.assertEqual(fs_data(), self.sut.fs_data)

    def download_zipped_cheats_folder(self, input_store, from_zip_content, is_summary_internal=False, save=True):
        zipped_files = zipped_files_from_cheats_folder() if from_zip_content else None

        output_store = self.download(db_test_descr(zips={
            cheats_folder_id: cheats_folder_zip_desc(zipped_files=zipped_files, summary=summary_json_from_cheats_folder(), is_summary_internal=is_summary_internal)
        }), input_store)

        self.assertReports(list(cheats_folder_files()), save=save)

        return output_store

    def assertReports(self, installed, errors=None, needs_reboot=False, save=True):
        if errors is None:
            errors = []
        self.assertEqual([_report_path(i) for i in installed], self.sut.correctly_installed_files())
        self.assertEqual([_report_path(e) for e in errors], self.sut.files_that_failed())
        self.assertEqual(needs_reboot, self.sut.needs_reboot())
        self.assertEqual(save, self.sut.needs_save)


def _report_path(path):
    return path

    if path[0] == '/':
        return path

    return media_fat(path)
