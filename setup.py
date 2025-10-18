from setuptools import setup, find_packages

setup(
    name="microservice_chassis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pika",
        "sqlalchemy",
        "fastapi",
        "pydantic-settings"
    ],
    author="Gorka Fernandez",
    author_email="gorka.fernandezg@alumni.mondragon.edu",
    description="A reusable library for microservices",
    url="https://gitlab.com/macc_ci_cd/aas/chassis",
)
