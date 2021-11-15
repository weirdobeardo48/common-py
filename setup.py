from setuptools import setup


with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='common_py',
    version='1.0.0',
    license='',
    author='TruongNX',
    install_requires=required,
    author_email='truongnx@easyshoppingfeed.com',
    description='Common Module',
    # long_description = long_description,
    long_description_content_type="text/markdown"
)