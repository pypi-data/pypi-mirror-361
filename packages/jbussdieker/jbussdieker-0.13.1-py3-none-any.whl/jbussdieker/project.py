import os
import logging

from jbussdieker.template_loader import load_and_substitute, load_template
from jbussdieker.git_utils import get_default_branch


class ProjectGenerator:
    def __init__(self, name):
        self.name = name

    def run(self):
        if os.path.exists(self.name):
            logging.error(f"Directory '{self.name}' already exists.")
            return
        os.makedirs(self.name)
        gh_workflow_dir = os.path.join(self.name, ".github", "workflows")
        os.makedirs(gh_workflow_dir)
        src_dir = os.path.join(self.name, "src", self.name)
        os.makedirs(src_dir)
        tests_dir = os.path.join(self.name, "tests")
        os.makedirs(tests_dir)
        default_branch = get_default_branch()
        with open(os.path.join(self.name, "Makefile"), "w") as f:
            f.write(load_template("Makefile"))
        with open(os.path.join(self.name, ".gitignore"), "w") as f:
            f.write(load_template(".gitignore"))
        with open(os.path.join(gh_workflow_dir, "ci.yml"), "w") as f:
            f.write(
                load_and_substitute(
                    "ci.yml", PROJECT_NAME=self.name, DEFAULT_BRANCH=default_branch
                )
            )
        with open(os.path.join(gh_workflow_dir, "publish.yml"), "w") as f:
            f.write(load_template("publish.yml"))
        with open(os.path.join(self.name, "pyproject.toml"), "w") as f:
            f.write(
                load_and_substitute(
                    "pyproject.toml",
                    PROJECT_NAME=self.name,
                    DEFAULT_BRANCH=default_branch,
                )
            )
        with open(os.path.join(self.name, "LICENSE"), "w") as f:
            f.write(load_template("LICENSE"))
        with open(os.path.join(self.name, "README.md"), "w") as f:
            f.write(load_and_substitute("README.md", PROJECT_NAME=self.name))
        with open(os.path.join(src_dir, "__init__.py"), "w") as f:
            f.write(load_template("__init__.py"))
        with open(os.path.join(tests_dir, "__init__.py"), "w") as f:
            f.write("")
        with open(os.path.join(tests_dir, f"test_{self.name}.py"), "w") as f:
            f.write(load_and_substitute("test_project.py", PROJECT_NAME=self.name))
        logging.info(f"Created new project at: {os.path.abspath(self.name)}")
