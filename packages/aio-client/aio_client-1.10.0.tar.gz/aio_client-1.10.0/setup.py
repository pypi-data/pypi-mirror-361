# coding: utf-8

from os.path import abspath
from os.path import dirname
from os.path import join
import re
from pathlib import Path

from pkg_resources import Requirement
from setuptools import find_packages
from setuptools import setup


_COMMENT_RE = re.compile(r'(^|\s)+#.*$')

current_dir_path = Path().resolve()


#  Получение полного описания
with open(str(current_dir_path / 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(str(current_dir_path / 'CHANGELOG.md'), encoding='utf-8') as f:
    long_description += f.read()


def _get_requirements(file_path):
    with open(file_path, 'r') as file:
        for line in file:
            line = _COMMENT_RE.sub('', line)
            line = line.strip()
            if line.startswith('-r '):
                for req in _get_requirements(
                    join(dirname(abspath(file_path)), line[3:])
                ):
                    yield req
            elif line:
                req = Requirement(line)
                req_str = req.name + str(req.specifier)
                if req.marker:
                    req_str += '; ' + str(req.marker)
                yield req_str


def _read(file_name):
    with open(file_name, 'r', encoding='utf-8') as infile:
        return infile.read()


def main():
    setup(
        name='aio-client',

        description='AIO-клиент',
        long_description=long_description,
        long_description_content_type='text/markdown',

        author='BARS Group',
        author_email='education_dev@bars-open.ru',
        keywords='django СМЭВ3',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        dependency_links=(
            'http://pypi.bars-open.ru/simple/m3-builder',
        ),
        setup_requires=(
            'm3-builder>=1.2,<2',
        ),
        install_requires=tuple(_get_requirements('requirements/base.txt')),
        set_build_info=join(dirname(__file__), 'src', 'aio_client'),
        zip_safe=False,
    )


if __name__ == '__main__':
    main()
