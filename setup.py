import setuptools
from whatweb import __version__

with open("README.md", "r") as readme_file:
	readme = readme_file.read()

setuptools.setup(
	name="whatweb",
	version=__version__,
	author="Jak Bin",
	author_email="jakbin4747@gmail.com",
	description="Next generation web scanner",
	long_description=readme,
	long_description_content_type="text/markdown",
	url="https://github.com/jakbin/whatweb",
	install_requires=["requests","beautifulsoup4","dnspython","colorama"],
	python_requires=">=3",
	project_urls={
		"Bug Tracker": "https://github.com/jakbin/whatweb/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
	],
	keywords='whatweb,web-scanner',
	py_modules=['whatweb'],
	entry_points={
		"console_scripts":[
			"whatweb = whatweb:main"
		]
	}
)