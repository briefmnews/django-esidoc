from setuptools import setup

setup(
    name="django-esidoc",
    version="0.1.2",
    description="Handle login and ticket validation for e-sidoc",
    url="https://github.com/briefmnews/django-esidoc",
    author="Brief.me",
    author_email="tech@brief.me",
    license="GNU GPL v3",
    packages=["django_esidoc", "django_esidoc.migrations"],
    python_requires="==2.7.*",
    install_requires=[
        "Django>=1.11.0",
        "djangorestframework>=3.8.2",
        "python-cas==1.4.0",
        "lxml>=4.2.5",
        "requests>=2.19.1",
    ],
    zip_safe=False,
)
