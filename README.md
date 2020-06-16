# docker-compose-env

Solve the problem that environment variables are not interpolated by docker-compose

## Introduction

The docker-compose-env tool solves the problem that environment variables are not interpolated by docker-compose.
It follows these steps:

1. read a spec file that lists a number of .env files
2. read every variable declaration in every .env file (in order)
3. write the interpolated environment variable to the output .env file

## Specification file format

The spec file is a yaml file that contains a dictionary that maps an <output_filename> to a list of <input_filename>, e.g.

one.env:
  - foo.env
  - bar.env

two.env:
  - foo.env
  - hello.env
  - baz.env

