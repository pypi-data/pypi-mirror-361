import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="flask_shoppingcart",
    version="0.3.1",
    author="Brixt18",
    author_email="",
    description="Add a shopping cart to your Flask app",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Brixt18/flask-shoppingcart",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Typing :: Typed",
    ],
)

# development status:
# Development Status :: 1 - Planning: The project is in the planning phase and no code has been written yet.
# Development Status :: 2 - Pre-Alpha: The project is in the early stages of development. It may be experimental and not fully functional.
# Development Status :: 3 - Alpha: The project is in the alpha stage. It is more developed than pre-alpha but still likely to change significantly and may be unstable.
# Development Status :: 4 - Beta: The project is in the beta stage. It is more stable than alpha, but still may have bugs and is not yet considered production-ready.
# Development Status :: 5 - Production/Stable: The project is stable and ready for production use. It has been thoroughly tested and is considered reliable.
# Development Status :: 6 - Mature: The project is very stable and mature. It has been in production use for a long time and is unlikely to change significantly.
# Development Status :: 7 - Inactive: The project is no longer being actively developed. It may still be usable, but no further updates are expected.

# versioning:
# Major.Minor.Patch