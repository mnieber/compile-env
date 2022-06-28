import os

from compile_env import run

expected_result_1 = """# blah
# $FOO=some foo value
RESULT1=foofoosecret
"""

expected_result_2 = """RESULT1=foofoobar

# space

RESULT2=secret
"""


def test_compile_env():
    base_dir = os.path.dirname(__file__)
    spec_fn = os.path.join(base_dir, "env-spec.yaml")
    run(spec_fn)

    with open(os.path.join(base_dir, "result1.env")) as f:
        result = f.read()
        assert result == expected_result_1

    with open(os.path.join(base_dir, "result2.env")) as f:
        result = f.read()
        assert result == expected_result_2
