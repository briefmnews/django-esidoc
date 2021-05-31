from setuptools import setup

setup(
    name="django-esidoc",
    version="1.5.2",
    description="Handle login and ticket validation for french ent (Esidoc, HDF and Occitanie)",
    url="https://github.com/briefmnews/django-esidoc",
    author="Brief.me",
    author_email="tech@brief.me",
    license="GNU GPL v3",
    packages=["django_esidoc", "django_esidoc.migrations"],
    python_requires=">=3.7",
    install_requires=[
        "Django>=2.2",
        "djangorestframework>=3.8.2",
        "python-cas>=1.4.0",
        "lxml>=4.6",
        "requests>=2.19.1",
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 2.2",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    include_package_data=True,
    zip_safe=False,
)
