from setuptools import setup, find_namespace_packages

setup(
    name='clean_folder',
    version='1',
    description='Package for sorting files in a specific folder',
    url='https://github.com/Natali2411/GoIT-module7',
    author='Nataliia Tiutiunnyk',
    author_email='nat.tiutiunnyk@gmail.com',
    license='MIT',
    packages=find_namespace_packages(),
    entry_points={'console_scripts': ['clean-folder = clean_folder.clean:sort_folder']}
)
