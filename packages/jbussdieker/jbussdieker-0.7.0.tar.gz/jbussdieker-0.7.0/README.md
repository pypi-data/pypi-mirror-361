# python-jbussdieker

## Installing

```
$ pip install jbussdieker --upgrade
```

## Usage

Basic usage:

```bash
$ jbussdieker
jbussdieker v0.2.1
```

## Configuration File Override & Testing

By default, `jbussdieker` uses a config file at:

```
~/.jbussdieker.json
```

### Override Config Location

You can override the config file path by setting the environment variable:

```bash
export JBUSSDIEKER_CONFIG=/path/to/custom_config.json
```

This is useful if you want to:

* Use multiple different config files
* Avoid overwriting your default config during development or testing

### Testing & Temporary Configs

Our tests leverage this environment variable to isolate config files in temporary directories, ensuring your personal config file is never overwritten or affected by tests.

If you want to test or run the CLI with a different config, just set `JBUSSDIEKER_CONFIG` to point to your desired file.

```bash
# Run with custom config file
JBUSSDIEKER_CONFIG=/tmp/myconfig.json jbussdieker config
```
