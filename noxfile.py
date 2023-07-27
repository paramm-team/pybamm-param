import nox


@nox.session
def lint(session):
    session.install('flake8')
    session.run('flake8', './pbparam/', './tests/')


@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def integration(session):
    """Run the intergration test suite."""
    session.install('-e', './[dev]')
    session.run()


@nox.session(python=['3.8', '3.9', '3.10', '3.11'])
def unit(session):
    """Run the unit test suite."""
    session.install('-e', './[dev]')
    session.run()

