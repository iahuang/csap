# `csap`

> A avr-gcc wrapper for SAP
> 
> Designed for the Math 656 final project

## Purpose
To design a system for compiling C/C++ to SAP by compiling to AVR assembly then translating it to SAP assembly

## Getting started (Mac)
First make sure you have [Homebrew](https://brew.sh/) and [Python 3.6+](https://www.python.org/downloads/) installed

```bash
$ xcode-select --install # If you don't already have Xcode command line tools installed
$ brew tap osx-cross/avr
$ brew install avr-gcc
```

## Usage

Remember to replace `python` with `python3` if you're on Mac. 

```bash
$ python3 csap.py myprogram.c
```

## Libraries and standard IO

csap does not support linking libraries for either C++ and C. This includes standard libraries such as `iostream` and `stdio.h` For the moment, you can access functions such as printing by including `csap/lib/saplib.h` in your source file.

### Known exceptions to this rule (C)

- stdbool.h