from setuptools import setup, find_packages

setup(
    name="django-dynamictexts",
    version="0.2.1",
    description="Reusable Django app for dynamic multilingual texts with template tags.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="BasistaPlay",
    author_email="basistaplay@gmail.com",
    url="https://git.tormaks.com/basistaplay/django-dynamictexts",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "Django>=4.2",
        "django-modeltranslation>=0.17",
    ],
classifiers=[
        "Framework :: Django",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)