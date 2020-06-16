import argparse
import os
import re

import yaml


def compile(env_line):
    regex = r"(export\s*)?([^=]+)=([^=]+)\s*"
    matches = list(re.finditer(regex, env_line))

    if len(matches) == 1:
        groups = matches[0].groups()
        prefix = groups[0] or ""
        key = groups[1]
        value = os.path.expandvars(groups[2])
        os.environ[key] = value
        return f"{prefix}{key}={value}"

    return None


def compile_files(input_files):
    content = ""

    for input_file in input_files:
        with open(input_file) as f:
            for env_line in f.readlines():
                output_line = compile(env_line.strip())
                if output_line:
                    content += output_line + os.linesep
    return content


def run(spec_file):
    with open(spec_file) as f:
        spec = yaml.load(f, Loader=yaml.FullLoader)

        for output_filename, input_files in spec.items():
            memo = dict(os.environ)
            try:
                content = compile_files(input_files)
            finally:
                os.environ.clear()
                os.environ.update(memo)
            with open(output_filename, 'w') as f:
                f.write(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")

    args = parser.parse_args()
    run(args.spec_file)


if __name__ == "__main__":
    main()
