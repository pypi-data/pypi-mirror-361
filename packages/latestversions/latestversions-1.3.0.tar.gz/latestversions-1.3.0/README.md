
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org/)

# Introduction

A simple python console script to 
# Overview

The basic command structure is:

```
Usage: latestversions [OPTIONS]

  This command reports the latest package versions of the specified input packages
  
  By default output is just written to the default file name

Options:
  --version                Show the version and exit.
  -p, --package-name TEXT  Specify package names  [required]
  -o, --output-file TEXT   The optional file.
  --help                   Show this message and exit.
```

# Installation

```
pip install latestversions
```

# Prerequisites

[Curl](https://everything.curl.dev/project/index.html) is pre-installed on Mac OSX

[jq](https://jqlang.github.io/jq/) CLI JSON processor.  Use [brew](https://brew.sh) to install this.



# Sample Output



```bash
latestversions -p wheel -p setuptools -p twine -p build -p mypy 
wheel==0.45.1
setuptools==75.8.0
twine==6.0.1
build==1.2.2.post1
mypy==1.14.1

```





___

Written by Humberto A. Sanchez II <mailto@humberto.a.sanchez.ii@gmail.com>, (C) 2025

 


## Note
For all kind of problems, requests, enhancements, bug reports, etc.,
please drop me an e-mail.


------


![Humberto's Modified Logo](https://raw.githubusercontent.com/wiki/hasii2011/gittodoistclone/images/SillyGitHub.png)

I am concerned about GitHub's Copilot project



I urge you to read about the
[Give up GitHub](https://GiveUpGitHub.org) campaign from
[the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there I do not like that
a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  But, I continue
to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done
without my permission.  I do not consent to GitHub's use of this project's
code in Copilot.

A repository owner may opt out of Copilot by changing Settings --> GitHub Copilot.

I have done so.
I have done so.

