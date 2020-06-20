# docker-compose-env

Solve the problem that environment variables are not interpolated by docker-compose

## Introduction

The docker-compose-env tool solves the problem that environment variables are not interpolated by docker-compose.
It follows these steps:

1. read a spec file that lists a number of .env files
2. read every variable declaration in every .env file (in order)
3. write the interpolated environment variable to the output .env file

## Specification file format

The spec file is a yaml file that contains a dictionary that maps an <output_filename> to a list of dependencies and a list of targets. The list of dependencies contains .env files that should be read but not added to the output file.
The list of targets contains .env files that should be interpolated and merged into the output file. For example:

```
        # my-env-spec.yaml

        global_dependencies:
          - secrets.env

        required_variables:
          - BUILD_ID

        outputs:
          one.env:
            dependencies:
              - foo.env
            targets:
              - bar.env
              - baz.env

          two.env:
            targets:
              - bar.env
```

## Running docker-compose-env

When you run `docker-compose-env my-env-spec.yaml up` then it will temporarily add the  variables in `secrets.env` (the global dependency) and `foo.env` (the dependency of `one.env`) to the environment and use them to interpolate the variables in `bar.env` and `baz.env` (the targets for `one.env`). The result of that interpolation is written as a new .env file to `one.env`. The processing of `two.env` is similar. The docker-compose file can then refer to `one.env` and `two.env` in its `env_file` section.
Note that `one.env` and `two.env` are created independently (reading the variables to create `one.env` does not affect the creation of `two.env`).

## Variable interpolation

The interpolation depends on the [expandvars](https://pypi.org/project/expandvars/) package.

## The export keyword

If a line in a .env file starts with 'export' then this keyword is ignored. In this case,
the corresponding line in the output .env file will also start with 'export'.

## Undefined variables

Undefined variables will be interpolated to an empty string. You can add variables to the `require_variables` list to guard against cases where the caller forgot to define a variable.

## Running compile-env

It's also possible to run only the .env file compilation step using `compile-env my-env-spec.yaml`.
