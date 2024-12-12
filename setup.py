from setuptools import setup

APP = ['simple_ui.py']
OPTIONS = {
    'argv_emulation': False,
    'includes': [
        'PyQt5',
    ],
    'packages': [],
    'plist': {
        'CFBundleName': "Simple Script Runner",
        'CFBundleDisplayName': "Simple Script Runner",
        'CFBundleIdentifier': "com.simplescriptrunner.app",
        'CFBundleVersion': "0.1.0",
        'LSMinimumSystemVersion': "10.13",
        'NSHighResolutionCapable': True,
    },
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)