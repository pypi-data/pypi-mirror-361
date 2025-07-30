from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setuptools.setup(
    name="streamlit-sidebar-accordion-menu",
    version="0.0.2",
    author="Ayumu Yamaguchi",
    description="A Streamlit component for creating sidebar accordion menus with navigation support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gussan-me/streamlit_sidebar_accordion_menu.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        # st.switch_page() was introduced in Streamlit 1.31.0
        "streamlit >= 1.31.0",
    ]
)
