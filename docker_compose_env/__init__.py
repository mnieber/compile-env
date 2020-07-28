import argparse
import subprocess
import sys

from docker_compose_env import compile_env
from expandvars import UnboundVariable


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")
    parser.add_argument("docker_compose_args", nargs="*")

    args = parser.parse_args()
    try:
        compile_env.run(args.spec_file)
    except UnboundVariable as e:
        print("Error: %s" % e)
        sys.exit(1)
    except compile_env.RunTimeError as e:
        print("Error: %s" % e.reason)
        sys.exit(1)

    subprocess.run(
        ["docker-compose %s" % " ".join(args.docker_compose_args)], shell=True
    )


if __name__ == "__main__":
    main()
