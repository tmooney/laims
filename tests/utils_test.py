import laims.utils as pu
import datetime as dt


def test_md5_checksum(tmpdir):
    test_file = tmpdir.mkdir("sub").join('test.txt')
    test_file.write('This is just a test.\nSeriously!')
    expected_checksum = '36925bfbf7b3d3284706ae2582215cce'
    assert pu.md5_checksum(str(test_file)) == expected_checksum


def test_read_first_checksum(tmpdir):
    expected = '36925bfbf7b3d3284706ae2582215cce'
    tmp = tmpdir.mkdir("sub").join('checksum.txt')
    tmp.write('{0}  {1}'.format(expected, 'test.txt'))
    assert pu.read_first_checksum(str(tmp)) == expected


def test_file_mtime(tmpdir):
    tmp = tmpdir.join('mtime')
    tmp.write('test')
    expected = dt.datetime.utcfromtimestamp(tmp.mtime())
    assert pu.file_mtime(str(tmp)) == expected
