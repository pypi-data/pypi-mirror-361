from setuptools import setup
from setuptools.command.install_scripts import install_scripts
import sys


class ManualAdminInstallation(install_scripts):
    def run(self):
        install_scripts.run(self)
        for script in self.get_outputs():
            if "matrix-admin" in script:
                with open(script, 'r+') as f:
                    content = f.read()
                    if not content.startswith('#!'):
                        f.seek(0)
                        f.write('#!{python}\n\n'.format(python=sys.executable))
                        f.write(content)


setup(
    name='matrix-sdk',
    version='1.0.1',
    description='A module to handle projects and connections to the Matrix repo server',
    author='Matrix-AI Developers',
    author_email='amirhosseinseddigh@gmail.com',
    packages=["matrix", "matrix.manager", "matrix.templates", "matrix.utils", "matrix.client"],
    package_dir={
        "matrix":"matrix"
                 },
    package_data={"": ["*.zip", "Dockerfile*"]},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'matrix-admin=matrix.matrix_admin:main',
        ]
    },
    cmdclass={'install_scripts': ManualAdminInstallation},
    install_requires=[
        'setuptools',
        'zipfile36>=0.1.3',
        'requests>=2.31.0',
        'tqdm>=4.66.2',
        'importlib_metadata;python_version<"3.8"',
        'packaging>=20.0',
        'typing_extensions;python_version<"3.8"',
    ],
)
