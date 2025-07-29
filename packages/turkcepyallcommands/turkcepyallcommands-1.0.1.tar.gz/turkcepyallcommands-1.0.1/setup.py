from setuptools import setup, find_packages

setup(
    name="turkcepyallcommands",
    version="1.0.1",
    author="Yağızalp Darıcı",
    author_email="yagodarici@gmail.com",
    description="Bütün Python fonksiyonlarını Türkçeye çeviren modül",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/ydrcoder",  # GitHub adresin
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
