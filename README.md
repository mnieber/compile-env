# compile-env


## Introduction

This tool transforms a set of source .env files into a set of target files. Variable interpolation is
performed during this step. It follows these steps:

1. read a spec file that lists a number of .env files
2. read every variable declaration in every .env file (in order)
3. write the interpolated environment variable to the output .env file

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

## Variable interpolation

The interpolation depends on the [expandvars](https://pypi.org/project/expandvars/) package.

## The export keyword

If a line in a .env file starts with 'export' then this keyword is ignored. In this case,
the corresponding line in the output .env file will also start with 'export'.

## Undefined variables

Undefined variables will be interpolated to an empty string. You can add variables to the `require_variables` list to guard against cases where the caller forgot to define a variable. In that case, a missing variable
will result in a runtime error.
