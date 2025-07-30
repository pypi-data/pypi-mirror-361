import pathlib
import tempfile

import pytest  # type: ignore

import muuntuu.cli as cli
from muuntuu import ENCODING, ENC_ERRS, VERSION

FIXTURE = pathlib.Path('test/fixtures/')


def test_main_ok_empty(capsys):
    cli.main([])
    out, err = capsys.readouterr()
    assert not err
    assert 'show this help message and exit' in out
    assert 'JSON' in out


def test_main_ok_smvp(capsys):
    with pytest.raises(SystemExit, match='0'):
        cli.main(['-h'])
    out, err = capsys.readouterr()
    assert not err
    assert 'show this help message and exit' in out
    assert 'JSON' in out


def test_parse_request_version(capsys):
    options = cli.parse_request(['--version'])
    assert options == 0
    out, err = capsys.readouterr()
    assert not err
    assert out.rstrip() == VERSION


def test_main_nok_no_files(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main(['-d'])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'muuntuu: error: source path must be given'
        ' - either as first positional argument or as value to the --source option'
    )
    assert not out


def test_main_nok_debug_and_quiet(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--debug', '--quiet'])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith('muuntuu: error: Cannot be quiet and debug - pick one')
    assert not out


def test_main_nok_no_target_file(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.json')])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'error: target path must be given - either as second positional argument or as value to the --target option'
    )
    assert not out


def test_main_nok_no_source_file(capsys):
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--target', str(FIXTURE / 'not-present.json')])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'error: source path must be given - either as first positional argument or as value to the --source option'
    )
    assert not out


def test_main_nok_source_file_not_present(capsys):
    source = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--source', str(source)])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(f'error: requested source ({source}) is not a file')
    assert not out


def test_main_nok_source_file_has_unknown_suffix(capsys):
    target = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.jason'), str(target)])
    out, err = capsys.readouterr()
    # assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'error: requested source suffix (.jason) is not in known suffixes (.json, .yaml, .yml)'
    )
    assert not out


def test_main_nok_doubled_source_files(capsys):
    source = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main(['--source', str(source), str(source)])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'error: source path given both as first positional argument and as value to the --source option - pick one'
    )
    assert not out


def test_main_nok_target_file_exists(capsys):
    target = FIXTURE / 'empty-array.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.json'), str(target)])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(f'error: requested target ({target}) already exist - remove or request other target')
    assert not out


def test_main_nok_target_file_has_unknown_suffix(capsys):
    target = FIXTURE / 'empty-array.jason'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(FIXTURE / 'empty.json'), str(target)])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'error: requested target suffix (.jason) is not in known suffixes (.json, .yaml, .yml)'
    )
    assert not out


def test_main_nok_doubled_target_files(capsys):
    source = FIXTURE / 'empty.json'
    target = FIXTURE / 'not-present.json'
    with pytest.raises(SystemExit, match='2'):
        cli.main([str(source), '--target', str(target), str(target)])
    out, err = capsys.readouterr()
    assert err.startswith('usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet]')
    assert err.rstrip().endswith(
        'error: target path given both as second positional argument and as value to the --target option - pick one'
    )
    assert not out


def test_main_ok_some_json_object_to_yaml(capsys):
    source = FIXTURE / 'some-object.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yml'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
        with open(target, 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            result = handle.read()
        with open(FIXTURE / 'some-object.yml', 'rt', encoding=ENCODING, errors=ENC_ERRS) as handle:
            expected = handle.read()
        assert result == expected
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested transform from json to yaml' in out
    assert 'json_load(path=test/fixtures/some-object.json, debug=True)' in out
    assert 'away-you-object-thing.yml' in out


def test_main_ok_some_yaml_object_to_json(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.json'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested transform from yaml to json' in out
    assert 'yaml_load(path=test/fixtures/some-object.yml, debug=True)' in out
    assert 'away-you-object-thing.json' in out


def test_main_ok_some_json_object_to_json(capsys):
    source = FIXTURE / 'some-object.json'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.JSON'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested transform from json to json' in out
    assert 'json_load(path=test/fixtures/some-object.json, debug=True)' in out
    assert 'away-you-object-thing.json' in out.lower()


def test_main_ok_some_yaml_object_to_yaml(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-d', str(source), str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested transform from yaml to yaml' in out
    assert 'yaml_load(path=test/fixtures/some-object.yml, debug=True)' in out
    assert 'away-you-object-thing.yaml' in out


def test_main_ok_target_from_option(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-d', '-s', str(source), '-t', str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert out.startswith('Debug mode requested.')
    assert 'Requested transform from yaml to yaml' in out
    assert 'yaml_load(path=test/fixtures/some-object.yml, debug=True)' in out
    assert 'away-you-object-thing.yaml' in out


def test_main_ok_quiet(capsys):
    source = FIXTURE / 'some-object.yml'
    with tempfile.TemporaryDirectory() as temp_dir:
        target = pathlib.Path(temp_dir) / 'away-you-object-thing.yaml'
        cli.main(['-q', '-s', str(source), '-t', str(target)])
        assert target.is_file()
    out, err = capsys.readouterr()
    assert not err
    assert not out
