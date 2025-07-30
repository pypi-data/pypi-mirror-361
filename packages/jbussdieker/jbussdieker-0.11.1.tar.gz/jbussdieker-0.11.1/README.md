# python-jbussdieker

A helpful Python CLI and project generator — perfect for bootstrapping new Python projects with best practices baked in.

---

## 📦 Install

Install or upgrade using `pip`:

```bash
pip install --upgrade jbussdieker
````

---

## 🚀 Commands

`jbussdieker` provides a simple CLI with a few handy commands:

---

### `jbussdieker version`

Prints the current version.

```bash
$ jbussdieker version
jbussdieker v0.7.2
```

---

### `jbussdieker config`

Inspect or update your configuration.

By default, `jbussdieker` stores its config in:

```bash
~/.jbussdieker.json
```

**Show your config:**

```bash
jbussdieker config
```

**Update your config:**

```bash
jbussdieker config --set log_level=DEBUG
```

*You can set any built-in field (like `log_level`) or define custom settings, which are saved under `custom_settings`.*

---

### `jbussdieker create`

Bootstrap a new project directory.

```bash
jbussdieker create myproject
```

This will:

✅ Create `./myproject/`
✅ Add a `README.md`, `pyproject.toml`, `LICENSE.txt`
✅ Add starter `src/` and `tests/` folders
✅ Add GitHub CI workflows

---

## 🗂️ Using a Custom Config File

You can override the default config path with the `JBUSSDIEKER_CONFIG` environment variable:

```bash
export JBUSSDIEKER_CONFIG=/path/to/custom_config.json
```

This is useful for:

* Working with multiple config files
* Keeping test/dev configs separate from your main config

**Example:**

```bash
# Run with a custom config file
JBUSSDIEKER_CONFIG=/tmp/myconfig.json jbussdieker config
```

---

## ❤️ Contributing

Have an idea or found a bug?
Please open an [issue](https://github.com/jbussdieker/python-jbussdieker/issues) or send a pull request!

---

## 📄 License

This project is licensed under the [MIT License](LICENSE.txt).

---

Happy hacking! ✨
