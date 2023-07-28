import nox


@nox.session
def lint(session):
    """Run the flake8 linter."""
    session.install('flake8')
    session.run('flake8', './pbparam/', './tests/')


@nox.session
def sphinx(session):
    """Build the documentation."""
    session.install('-e', './[docs]')
    session.run('sphinx-build', '-b', 'html', 'docs', 'docs/_build/html', '-W')


@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def integration(session):
    """Run the intergration test suite."""
    session.install('-e', './[dev]')

    # Get the files to test
    if session.posargs:
        test_files = session.posargs
    else:
        test_files = ["./tests/integration/"]

    session.run("python", "-m", "unittest", "discover", *test_files)


@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def unit(session):
    """Run the unit test suite."""
    session.install('-e', './[dev]')

    # Get the files to test
    if session.posargs:
        test_files = session.posargs
    else:
        test_files = ["./tests/unit/"]

    session.run("python", "-m", "unittest", "discover", *test_files)


@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def examples(session):
    """Run the examples."""
    session.install('-e', './[dev]')

    # Get the files to test
    if session.posargs:
        test_files = session.posargs
    else:
        test_files = ["./examples/scripts/"]

    session.run("python", "-m", "unittest", "discover", *test_files)


@nox.session(python=['3.11'])
def coverage(session):
    """Run the unit test suite with coverage."""
    session.install('-e', './[dev]')

    session.run("coverage", "run", "--source=./pbparam", "--rcfile=.coveragerc", "-m", "unittest", "discover", "./tests/")
    session.run("coverage", "combine")
    session.run("coverage", "report", "-m")
    session.run("coverage", "xml")
