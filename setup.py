from setuptools import setup, find_packages

setup(
    name="microservice_chassis",
    version="0.1.4",
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
    url="https://github.com/monolith2microservice/Chassis",
)

#python setup.py sdist bdist_wheel  