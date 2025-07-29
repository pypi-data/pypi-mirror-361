from setuptools import setup


with open(r'README.md','r',encoding='utf-8') as f:
    descricao_longa = f.read()

with open("requirements.txt") as f:
    install_requires = f.read().splitlines()

setup(
    name='py_ri_ufsc',
    version='0.5',
    # packages=find_packages(),
    packages=[
        "py_ri_ufsc",
        "py_ri_ufsc.common",
        "py_ri_ufsc.etl",
        "py_ri_ufsc.etl.extraction",
        "py_ri_ufsc.etl.extraction.courses_info",
        "py_ri_ufsc.etl.transform_and_load",
        "py_ri_ufsc.get_metadata",
        "py_ri_ufsc.src_files",
        "py_ri_ufsc.ui_graphs"
    ],
    package_dir={"": "src"},
    package_data={"py_ri_ufsc.src_files": ["*.parquet"]},
    include_package_data = True,
    install_requires = install_requires,
    description='Program design to handle searches in metadata stored in UFSC Institucional Repository',
    long_description=descricao_longa,
    long_description_content_type="text/markdown",
    author='Igor Caetano de Souza',
    project_urls={
        "GitHub Repository":"https://github.com/IgorCaetano/py_ri_ufsc"
    },
)
