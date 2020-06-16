import argparse
import subprocess

from docker_compose_env import compile_env


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("spec_file")
    parser.add_argument("docker_compose_args", nargs="*")

    args = parser.parse_args()
    compile_env.run(args.spec_file)

    subprocess.run(
        ["docker-compose %s" % " ".join(args.docker_compose_args)], shell=True
    )


if __name__ == "__main__":
    main()
