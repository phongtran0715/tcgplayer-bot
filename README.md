<!--
*** Thanks for checking out this README Template. If you have a suggestion that would
*** make this better, please fork the repo and create a pull request or simply open
*** an issue with the tag "enhancement".
*** Thanks again! Now go create something AMAZING! :D
-->





<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">Tcgplayer</h3>
  <div>

  </div>

  <p align="center">
    Sub Title
    <br />
    <br />
  </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)



<!-- ABOUT THE PROJECT -->
## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)

<!-- GETTING STARTED -->
## Getting Started


## Requirements

This is an example of how to list things you need to use the software and how to install them.
* Python 3.9

### Installation

## Setup using Docker
This required you having [docker](https://docs.docker.com/get-docker/)
 and [docker-compose](https://docs.docker.com/compose/install/) installed and running.

### Initial setup
Make a copy of the `docker-compose.yml.sample` file. Optionally, make copies of the sample environment files if needed.

```bash
cp docker-compose.yml.example docker-compose.yml
```

The project used django-environ package for managing environment variable. You also need to make a copy of the `.env.example` in the `tcgplayer/settings/` directory. 
After that, udpate the variables in `.env` file with your local environment.

```bash
cp tcgplayer/settings/.env.example tcgplayer/settings/.env
```

Build docker containers
```bash
docker-compose build
```

Now start the core backend service
```bash
docker-compose up -d
```
___
## Usage

Set up initial user
```
$ python manage.py createsuperuser
```


<!-- USAGE EXAMPLES -->
___
## Usage

___
### Running tests
Run test suite
```
$ make test
```

Check sorting on imports
```
make isort
```

Check code formating
```
make flake8
```

Autoformat code
```
make autopep8
```

Audit code
```
$ make flake8
```

Run checks
```
$ make checks
```

___
### How to use git branches: master, production, and feature

The main development branch is `develop`. Every feature branch must start from this branch and merge back when tested and ready.

When your feature branches are ready, please create `merge request` and assign to @phongtran0715.

The feature branches must be named `feature/the-feature-name`.

If you use git-flow, the settings are:
* develpment branch name = "master"
* production branch name = "production"
* feature branch prefix = "feature" (default)
* hotfix branch prefix = "hotfix" (default)
* release branch prefix = "release" (default)
___

### API Documentation
