import argparse
import os
import re
import sys

import yaml
from expandvars import expandvars
from six import StringIO


class RunTimeError(Exception):
    def __init__(self, reason):
        self.reason = reason


def compile(env_line):
    regex = r"(export\s*)?([^=]+)=(.*)"
    matches = list(re.finditer(regex, env_line, re.DOTALL))

    if len(matches) == 1:
        groups = matches[0].groups()
        prefix = groups[0] or ""
        key = groups[1]
        value = expandvars(groups[2])
        os.environ[key] = value
        return "%s%s=%s" % (prefix, key, value)

    return None


def get_lines(f):
    quote = None
    escape = False
    line = ""

    for char in f.read():
        line += char

        if char == os.linesep:
            if quote:
                continue
            yield line
            line, quote, escape = "", None, False
        elif quote and escape:
            escape = False
        elif quote and char == "\\":
            escape = True
        elif char == "'" or char == '"':
            if quote and quote == char:
                quote = None
            elif not quote:
                quote = char
    yield line


def compile_files(root_dir, target_files, write_single_lines):
    content = ""

    for target_file in target_files:
        with open(os.path.join(root_dir, target_file)) as f:
            for env_line in get_lines(f):
                if write_single_lines:
                    env_line = env_line.replace(os.linesep, '')
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


def run(spec_file, write_single_lines):
    if not os.path.exists(spec_file):
        raise RunTimeError("Spec file not found: %s" % spec_file)

    root_dir = os.path.dirname(spec_file)

    with open(spec_file) as f:
        spec_file_str = expandvars(f.read())
        global_spec = yaml.load(StringIO(spec_file_str), Loader=yaml.FullLoader)
        require_variables(global_spec.get("required_variables", []))

        for output_filename, spec in global_spec["outputs"].items():
            memo = dict(os.environ)
            compile_files(root_dir, global_spec.get("global_dependencies", []), write_single_lines)
            compile_files(root_dir, spec.get("dependencies", []), write_single_lines)
            try:
                content = compile_files(root_dir, spec["targets"], write_single_lines)
            finally:
                os.environ.clear()
                os.environ.update(memo)
            with open(output_filename, 'w') as f:
                f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")
    parser.add_argument("--write-single-lines", action="store_true")

    args = parser.parse_args()
    try:
        run(args.spec_file, args.write_single_lines)
    except RunTimeError as e:
        print("Error: %s" % e.reason)
        sys.exit(1)


if __name__ == "__main__":
    main()
