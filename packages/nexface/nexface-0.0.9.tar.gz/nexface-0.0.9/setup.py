from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="nexface",
    version="0.0.9",
    author="Fatih Dagdeviren",
    author_email="fatihdagdeviren21@gmail.com",
    description="A face recognition and embedding extraction library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fatihdagdeviren/NexFace",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'opencv-python==4.12.0.88',
        'opencv-contrib-python==4.12.0.88',
        'scikit-learn==1.7.0',
        'onnx==1.18.0',
        'hdbscan==0.8.40',
        'typing-extensions',
        'tensorflow==2.19.0'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)