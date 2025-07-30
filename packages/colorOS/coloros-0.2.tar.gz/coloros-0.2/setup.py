from setuptools import setup, find_packages

setup(
    name="colorOS",  # pip install colorOS için bu gerekli
    version="0.2",
    description="Terminal renk ve konumlandırma kütüphanesi",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="TheRaven",
    author_email="RavenisThere@proton.me",
    url="https://github.com/TheRaven",  # Varsa GitHub
    packages=find_packages(),  # otomatik olarak coloros içindeki py dosyalarını bulur
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",  # lisansını değiştir istersen
    ],
    python_requires=">=3.7",
)
