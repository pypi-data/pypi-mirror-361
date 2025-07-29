from unittest import mock

import pytest

from morphi.libs import packages


class TestPackagesEnclosePackagePathExists(object):
    @mock.patch('morphi.libs.packages.files', autospec=True, spec_set=True)
    def test_enclose_package_path_exists(self, m_files):
        m_files.return_value.is_file.return_value = True
        retval = packages.enclose_package_path_exists('foobar')
        m_files.assert_called_with('foobar')
        assert retval

    def test_enclose_package_path_exists_functional(self):
        """verify the enclosure performs as expected"""
        path_exists = packages.enclose_package_path_exists('logging')
        assert path_exists('__init__.py') is True
        assert path_exists('nosuchfile.py') is False


@mock.patch('morphi.libs.packages.files', autospec=True, spec_set=True)
class TestPackagesPackageOpen:
    def test_open_fails(self, m_files):
        provider = m_files.return_value
        provider.is_file.return_value = False

        with pytest.raises(IOError):
            with packages.package_open('foobar', '/foo'):
                pass

    @mock.patch(
        'builtins.open',
        new_callable=mock.mock_open,
        read_data=b'asdf',
    )
    @mock.patch('morphi.libs.packages.as_file', autospec=True, spec_set=True)
    def test_open(self, m_as_file, m_open, m_files):
        provider = m_files.return_value
        provider.is_file.return_value = True
        m_as_file.return_value.__enter__.return_value = '/mock/path/to/resource'

        with packages.package_open('foobar', '/foo') as f:
            data = f.read()

        assert b'asdf' == data
