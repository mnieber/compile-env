import argparse
import os
import subprocess
import sys

from docker_compose_env import compile_env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")
    parser.add_argument("docker_compose_args", nargs="*")

    args = parser.parse_args()
    if not os.path.exists(args.spec_file):
        print("Spec file not found: %s" % args.spec_file)
        sys.exit(1)
    compile_env.run(args.spec_file)

    subprocess.run(
        ["docker-compose %s" % " ".join(args.docker_compose_args)], shell=True
    )


if __name__ == "__main__":
    main()
