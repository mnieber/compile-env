import argparse
import os
import re
import sys

import yaml
from expandvars import expandvars


class RunTimeError(Exception):
    def __init__(self, reason):
        self.reason = reason


def compile(env_line):
    regex = r"(export\s*)?([^=]+)=([^=]+)\s*"
    matches = list(re.finditer(regex, env_line))

    if len(matches) == 1:
        groups = matches[0].groups()
        prefix = groups[0] or ""
        key = groups[1]
        value = expandvars(groups[2])
        os.environ[key] = value
        return f"{prefix}{key}={value}"

    return None


def compile_files(root_dir, input_files):
    content = ""

    for input_file in input_files:
        with open(os.path.join(root_dir, input_file)) as f:
            for env_line in f.readlines():
                output_line = compile(env_line.strip())
                if output_line:
                    content += output_line + os.linesep
    return content


def require_variables(variables):
    for variable in variables:
        if variable not in os.environ:
            raise RunTimeError(
                "Required variable %s is not in the environment" % variable
            )


def run(spec_file):
    if not os.path.exists(spec_file):
        raise RunTimeError("Spec file not found: %s" % spec_file)

    root_dir = os.path.dirname(spec_file)

    with open(spec_file) as f:
        global_spec = yaml.load(f, Loader=yaml.FullLoader)
        require_variables(global_spec.get("required_variables", []))

        for output_filename, spec in global_spec["outputs"].items():
            memo = dict(os.environ)
            compile_files(root_dir, global_spec.get("global_dependencies", []))
            compile_files(root_dir, spec.get("dependencies", []))
            try:
                content = compile_files(root_dir, spec["includes"])
            finally:
                os.environ.clear()
                os.environ.update(memo)
            with open(output_filename, 'w') as f:
                f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")

    args = parser.parse_args()
    try:
        run(args.spec_file)
    except RunTimeError as e:
        print("Error: %s" % e.reason)
        sys.exit(1)


if __name__ == "__main__":
    main()
