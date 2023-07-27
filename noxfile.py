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
    session.run("./tests/integration/")


@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def unit(session):
    """Run the unit test suite."""
    session.install('-e', './[dev]')
    session.run("./tests/unit/")

