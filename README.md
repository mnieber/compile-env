# compile-env

## Introduction

This tool uses template rendering to transform a set of input .env files into a set of output .env files. It solves the following problem:

- "If every service in a stack has its own .env file, then how can we avoid duplicating the definitions of these environment variables?"

The solution takes the following approach:

1. The input .env files are organized by concern or tool (e.g. aws.env, django.env, postgres.env)
2. For every service we have a template that selects the required environment variables from the input files.
3. The output of the template is written to a new file that is used in the corresponding service.

## Variable interpolation

Values are interpolated when reading the input .env files. This means that you can have derived environment variables:

```
    # input.env

    PROJECT_NAME=foo
    FILE_STORAGE=${PROJECT_NAME}_files
```

The interpolation depends on the [expandvars](https://pypi.org/project/expandvars/) package. This package supports a wide variety of special formatting options.(e.g. default values).

## Specification file format

The spec file is a yaml file that contains a dictionary that maps an <output_filename> to a list of dependencies and a list of targets. The list of dependencies contains .env files that should be read but not added to the output file.
The list of targets contains .env files that should be interpolated and merged into the output file. For example:

```
    # my-env-spec.yaml

    settings:
      # toggle strict checking of unbound variables
      is_strict: True

    global_dependencies:
      - secrets.env

    required_variables:
      - BUILD_ID

    outputs:
      # output filename are either absolute or relative to the
      # location of the specification file
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

## Running compile-env on the above example

When you run `compile-env my-env-spec.yaml` then it will temporarily add the variables in `secrets.env` (the global dependency) and `foo.env` (the dependency of `one.env`) to the environment and use them to interpolate the variables in `bar.env` and `baz.env` (the targets for `one.env`). The result of that interpolation is written as a new .env file to `one.env`. The processing of `two.env` is similar.
Note that `one.env` and `two.env` are created independently (reading the variables to create `one.env` does not affect the creation of `two.env`).

## The export keyword

If a line in a .env file starts with 'export' then this keyword is ignored. In this case,
the corresponding line in the output .env file will also start with 'export'.

## Undefined variables

When is_strict is false, undefined variables will be interpolated to an empty string. You can add variables to the `require_variables` list to guard against cases where the caller forgot to define a variable. In that case, a missing variable will result in a runtime error.
