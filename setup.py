from setuptools import setup

setup(
    name='TracAutoCompleteUserAccountPlugin',
    #description='',
    #keywords='',
    #url='',
    version='0.1',
    #license='',
    #author='',
    #author_email='',
    #long_description="",
    packages=['autocompluseraccount'],
    package_data={
        'autocompluseraccount': [
            'htdocs/js/*.js',
            'htdocs/css/*.css',
        ]
    },
    entry_points={
        'trac.plugins': [
            'autocompluseraccount.web_ui = autocompluseraccount.web_ui'
        ]
    }
)
