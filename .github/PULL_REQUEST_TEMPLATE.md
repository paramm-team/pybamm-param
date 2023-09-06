# Description

Please include a summary of the change and which issue is fixed. Please also include relevant motivation and context. List any dependencies that are required for this change.

Fixes # (issue)

## Type of change

Please add a line in the relevant section of [CHANGELOG.md](https://github.com/paramm-team/pybamm-param/blob/main/CHANGELOG.md) to document the change (include PR #) - note reverse order of PR #s. If necessary, also add to the list of breaking changes.

- [ ] New feature (non-breaking change which adds functionality)
- [ ] Optimization (back-end change that speeds up the code)
- [ ] Bug fix (non-breaking change which fixes an issue)

## Key checklist

- [ ] No style issues: `$ python -m nox -s lint`
- [ ] All tests pass: `$ python -m nox -s unit examples integration`
- [ ] Coverage is complete `$ python -m nox -s coverage`
- [ ] The documentation builds: `$ python -m nox -s sphinx`

## Further checks

- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Tests added that prove fix is effective or that feature works
