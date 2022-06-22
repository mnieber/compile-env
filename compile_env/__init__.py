import argparse
import os
import re
import sys

import yaml
from expandvars import UnboundVariable, expandvars
from six import StringIO


class RunTimeError(Exception):
    def __init__(self, reason):
        self.reason = reason


def compile(env_line, is_strict=True):
    regex = r"(export\s*)?([^=]+)=(.*)"
    matches = list(re.finditer(regex, env_line, re.DOTALL))

    if len(matches) == 1:
        groups = matches[0].groups()
        prefix = groups[0] or ""
        key = groups[1]
        value = expandvars(groups[2], nounset=is_strict)
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


def compile_files(root_dir, target_files, is_strict):
    content = ""

    for target_file in target_files:
        with open(os.path.join(root_dir, target_file)) as f:
            for env_line in get_lines(f):
                output_line = compile(env_line.strip(), is_strict)
                if output_line:
                    content += output_line + os.linesep
    return content


def render_files(root_dir, target_files, is_strict):
    content = ""

    for target_file in target_files:
        with open(os.path.join(root_dir, target_file)) as f:
            for env_line in get_lines(f):
                output_line = expandvars(env_line, nounset=is_strict)
                content += output_line
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
        spec_file_str = expandvars(f.read(), nounset=True)

        global_spec = yaml.load(StringIO(spec_file_str), Loader=yaml.FullLoader)
        is_strict = global_spec.get("settings", {}).get("is_strict", True)

        require_variables(global_spec.get("required_variables", []))

        for output_filename, spec in global_spec["outputs"].items():
            memo = dict(os.environ)
            compile_files(
                root_dir, global_spec.get("global_dependencies", []), is_strict
            )
            compile_files(root_dir, spec.get("dependencies", []), is_strict)
            try:
                content = render_files(root_dir, spec["targets"], is_strict)
            finally:
                os.environ.clear()
                os.environ.update(memo)
            with open(os.path.join(root_dir, output_filename), "w") as f:
                f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")

    args = parser.parse_args()
    try:
        run(args.spec_file)
    except UnboundVariable as e:
        print("Error: %s" % e)
        sys.exit(1)
    except RunTimeError as e:
        print("Error: %s" % e.reason)
        sys.exit(1)


if __name__ == "__main__":
    main()
