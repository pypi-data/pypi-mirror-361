[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/pyut2xml/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/pyut2xml/tree/master)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)


# Introduction

A simple python console script to let me convert [Pyut](https://github.com/hasii2011/PyUt) files to XML.

# Overview

The basic command structure is:

```
Usage: pyut2xml [OPTIONS]

Options:
  --version               Show the version and exit.
  -i, --input-file TEXT   The input .put file to decompress.  [required]
  -o, --output-file TEXT  The output xml file.
  --help                  Show this message and exit.
```

By default, pyut2xml assumes that the input file has a `.put` suffix and the output file has a `.xml` suffix. 

However, pyut2xml is flexible and can deduce file names and suffixes.  The best option is if you do not specify the output file.  Then, pyut2xml deduces that the output file is the same as the input file name with the .xml suffix.  For example:

```pyut2xml -i TestFileV10.put```

causes pyut2xml to write to a file named TestFileV10.xml

The command line:

```pyut2xml -i TestFileV10 -o TestFileV10```

reads from TestFileV10.put and writes to TestFileV10.xml


Another simple example:

```pyut2xml -i TestFileV10```

causes pyut2xml to reads from a file named TestFileV10.put and write to a file named TestFileV10.xml

# Installation

```pip install pyut2xml```


___

Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2025

 

 
## Note
For all kind of problems, requests, enhancements, bug reports, etc.,
please drop me an e-mail.
