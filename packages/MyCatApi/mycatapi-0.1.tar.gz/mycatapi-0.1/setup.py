from setuptools import setup, find_packages

setup(
    name="MyCatApi",          # Уникальное имя (должно быть свободно в PyPI)
    version="0.1",             # Версия
    author="Твоё имя",
    description="API для работы с фактами о котах",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=["requests"],  # Зависимости
    python_requires=">=3.6",
)