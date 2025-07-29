from setuptools import setup, find_packages

with open("README.md", 'r') as f:
    description = f.read()

setup(
    name="deamstools",
    version="1.3.0",
    description="A Few Tools i made for my self. You can use them too!",
    author="DEAMJAVA",
    author_email="deamminecraft3@gmail.com",
    packages=find_packages(),
    install_requires=["packaging"],
    python_requires=">=3.12",
    entry_points={"console_scripts":["deamstools = deamstools:deamstools_check",
                                     "deamstools-license = deamstools:deamstools_license",
                                     "deamstools-help = deamstools:help"
                                     ]},
    #long_description=description,
    #long_description_content_type='text/markdown'
)
