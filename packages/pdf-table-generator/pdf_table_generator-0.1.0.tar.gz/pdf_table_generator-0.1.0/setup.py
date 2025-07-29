from setuptools import setup, find_packages

setup(
    name="pdf_table_generator",
    version="0.1.0",
    author="RAJASEKAR E C <rajasekar_e_c@outlook.com>",
    description="Generate PDF tables with dynamic headers, wrapping, and styling using fpdf",
    packages=find_packages(),
    install_requires=["fpdf"],
    python_requires=">=3.7",
)
