from setuptools import setup, find_packages

setup(
    name="flaskShop",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "blinker==1.7.0",
        "build==1.2.1",
        "click==8.1.7",
        "colorama==0.4.6",
        "Flask==3.0.2",
        "Flask-Cors==4.0.0",
        "Flask-SQLAlchemy==3.1.1",
        "greenlet==3.0.3",
        "gunicorn==21.2.0",
        "itsdangerous==2.1.2",
        "Jinja2==3.1.3",
        "MarkupSafe==2.1.5",
        "packaging==24.0",
        "pillow==10.2.0",
        "pyproject_hooks==1.0.0",
        "SQLAlchemy==2.0.28",
        "typing_extensions==4.10.0",
        "Werkzeug==3.0.1",
    ],
)