# Repository for certification.ubuntu.com

[![CircleCI build status](https://circleci.com/gh/canonical-web-and-design/certification.ubuntu.com.svg?style=shield)](https://circleci.com/gh/canonical-web-and-design/certification.ubuntu.com)
[![Code coverage](https://codecov.io/gh/canonical-web-and-design/certification.ubuntu.com/branch/master/graph/badge.svg)](https://codecov.io/gh/canonical-web-and-design/certification.ubuntu.com)


This is the repository for the new certification.ubuntu.com website.

At the moment this is under heavy development and does not relate to any website in production.

## Architecture overview

This website is written with the help of the [flask](http://flask.pocoo.org/) framework. In order to use functionalities that multiple of our websites here at Canonical share, we import the [base-flask-extension](https://github.com/canonical-web-and-design/canonicalwebteam.flask-base) module.


## Development

Run `./run` inside the root of the repository and all dependencies will automatically be installed. Afterwards the website will be available at <http://localhost:8034>.

When you start changing files, the server should reload and make the changes available immediately.
