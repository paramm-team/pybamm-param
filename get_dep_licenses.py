from importlib import metadata
import prettytable


def get_pkg_license(pkg):
    license_text = pkg.get('license')
    if license_text is None:
        license_text = pkg.get('License', 'License not found')
    if '\n' in license_text:
        license_text = f'{license_text.splitlines()[0]}: Multi-line license found, first line shown.'
    return license_text


def print_packages_and_licenses():
    t = prettytable.PrettyTable(['Package', 'License'])
    package_names = sorted([str(pkg.name).lower() for pkg in metadata.distributions()])
    for pkg_name in package_names:
        pkg = metadata.metadata(pkg_name)
        t.add_row((pkg.get('Name'), get_pkg_license(pkg)))
    print(t)


if __name__ == "__main__":
    print_packages_and_licenses()
