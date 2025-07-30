# python-jbussdieker

A helpful CLI and project generator.

## Installing

```bash
pip install jbussdieker --upgrade
````

## Commands

`jbussdieker` comes with a simple CLI with the following subcommands:

---

### 📌 `version`

Prints the current version.

```bash
$ jbussdieker version
jbussdieker v0.7.2
```

---

### ⚙️ `config`

Inspect or update your configuration.

By default, `jbussdieker` uses a config file at:

```
~/.jbussdieker.json
```

**Show your config:**

```bash
$ jbussdieker config
```

**Set a config value:**

```bash
$ jbussdieker config --set log_level=DEBUG
```

Values can be top-level config fields (like `log_level`) or custom keys (saved under `custom_settings`).

---

### 🗂️ `create`

Generate a new project directory in your current working directory.

```bash
$ jbussdieker create myproject
```

This will:

* Make a new folder `./myproject/`
* Add a `README.md` and `main.py` boilerplate

---

## Configuration File Override & Testing

You can override the config file location with an environment variable:

```bash
export JBUSSDIEKER_CONFIG=/path/to/custom_config.json
```

This is useful if you want to:

* Use multiple different config files
* Avoid overwriting your default config during development or testing

Our tests use this environment variable to isolate config files in temporary directories — your real config is never touched.

**Example:**

```bash
# Run with custom config file
JBUSSDIEKER_CONFIG=/tmp/myconfig.json jbussdieker config
```

---

Enjoy! 🚀
