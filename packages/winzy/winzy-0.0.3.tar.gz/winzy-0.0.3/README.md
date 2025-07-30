
[![PyPI](https://img.shields.io/pypi/v/winzy.svg)](https://pypi.org/project/winzy/)
[![Changelog](https://img.shields.io/github/v/release/sukhbinder/winzy?include_prereleases&label=changelog)](https://github.com/sukhbinder/winzy/releases)
[![Tests](https://github.com/sukhbinder/winzy/workflows/Test/badge.svg)](https://github.com/sukhbinder/winzy/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/sukhbinder/winzy/blob/main/LICENSE)


# winzy
A plugin-based CLI toolset for Windows, built on top of the Python language.

**Overview**
-----------

Winzy is a collection of command-line tools designed to make working with windows easier. The project takes a plugin-based approach, allowing users to extend its functionality by creating custom plugins.

There are few plugins that i am activiley using. I will soon add all of them here.

**Features**
------------

*   A simple and intuitive CLI interface
*   Extensive plugin support for customizing and extending the toolset
*   Integration with popular Python libraries and frameworks
*   Support for multiple Python versions (>=3.9)

**Requirements**
----------------

*   Python 3.9 or later
*   The `pluggy` library for plugin ment

**Installation**
----------------

```bash
pip install winzy
```

## Developing your plugin
------------------------

You'll need to have [cookiecutter](https://cookiecutter.readthedocs.io/) installed.

```bash
pipx install cookiecutter
```

Regular `pip` will work OK too.

## Usage

Run `cookiecutter gh:sukhbinder/winzy-plugin` and then answer the prompts. Here's an example run:

```bash
cookiecutter gh:sukhbinder/winzy-plugin
```

This will show this. Fill this and the template is ready. Just add your code.

```
plugin_name []: winzy plugin template demo
description []: Demonstrating https://github.com/sukhbinder/winzy-plugin
hyphenated [winzy-plugin-template-demo]:
underscored [winzy_plugin_template_demo]:
github_username []: sukhbinder
author_name []: Sukhbinder Singh
```

# List of Available Plugins
Here's the list of plugin available in pypi.

- [winzy-banner](https://pypi.org/project/winzy-banner/)	
- [winzy-calendar](https://pypi.org/project/winzy-calendar/)	
- [winzy-checkmail](https://pypi.org/project/winzy-checkmail/)	
- [winzy-cut](https://pypi.org/project/winzy-cut/)		
- [winzy-days-till](https://pypi.org/project/winzy-days-till/)	
- [winzy-extract](https://pypi.org/project/winzy-extract/)		
- [winzy-laptop-battery](https://pypi.org/project/winzy-laptop-battery/)	
- [winzy-notify](https://pypi.org/project/winzy-notify/)		
- [winzy-outlook-meetings](https://pypi.org/project/winzy-outlook-meetings/)	
- [winzy-pdf-to-text](https://pypi.org/project/winzy-pdf-to-text/)	
- [winzy-screencapture](https://pypi.org/project/winzy-screencapture/)	
- [winzy-screenshot](https://pypi.org/project/winzy-screenshot/)		
- [winzy-text-on-image](https://pypi.org/project/winzy-text-on-image/)	
- [winzy-text-to-image](https://pypi.org/project/winzy-text-to-image/)	
- [winzy-txt2img-val-town](https://pypi.org/project/winzy-txt2img-val-town/)		
- [winzy-wc](https://pypi.org/project/winzy-wc/)	
- [winzy-weather](https://pypi.org/project/winzy-weather/)	
- [winzy-webcam](https://pypi.org/project/winzy-webcam/)		
- [winzy-whitelist](https://pypi.org/project/winzy-whitelist/)	
- [winzy-win-geometry](https://pypi.org/project/winzy-win-geometry/)	

