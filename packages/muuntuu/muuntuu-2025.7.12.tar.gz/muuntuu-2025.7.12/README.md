# Muuntuu

Transforms (Finnish: muuntuu) helper tool.

## Usage:

```bash
❯ muuntuu
usage: muuntuu [-h] [--source FILE] [--target FILE] [--debug] [--quiet] [--version] [SOURCE_FILE] [TARGET_FILE]

Transforms (Finish: muuntuu) helper tool.

positional arguments:
  SOURCE_FILE           JSON or YAML source as positional argument
  TARGET_FILE           JSON or YAML target as positional argument

options:
  -h, --help            show this help message and exit
  --source FILE, -s FILE
                        JSON or YAML source
  --target FILE, -t FILE
                        JSON or YAML target
  --debug, -d           work in debug mode (default: False), overwrites any environment variable MUUNTUU_DEBUG value
  --quiet, -q           work in quiet mode (default: False)
  --version, -V         display version and exit
```

## Version

```bash
❯ muuntuu --vesion
2025.7.12
```

## Status

Prototype.
