from setuptools import setup, find_packages

# Читаем содержимое README.md для длинного описания
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="GramApi",
    version="1.0.0",
    packages=find_packages(),
    install_requires=["requests"],
    author="yourname", # <- ЗАМЕНИТЕ НА ВАШ НИК
    author_email="your@email.com", # <- ЗАМЕНИТЕ НА ВАШ EMAIL
    description="Auto exec Python code from Telegram bot files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourname/GramApi", # <- ОПЦИОНАЛЬНО: ССЫЛКА НА GITHUB
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License", # Добавим лицензию для примера
    ],
    python_requires='>=3.6',
) 