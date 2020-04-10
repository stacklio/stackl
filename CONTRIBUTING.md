<!-- How to file a bug report (try using issue and pull request templates)
How to suggest a new feature
How to set up your environment and run tests
The types of contributions youre looking for
Your roadmap or vision for the project
How contributors should (or should not) get in touch with you -->



# Contributing to STACKL <!-- omit in toc -->
First off, thank you for considering to contribute to STACKL. As an open source project all feedback is welcome and its people like you who make this a great tool!


## Table of Contents <!-- omit in toc -->

<!-- - [Contributing to STACKL](#contributing-to-stackl)
  - [Table of Contents](#table-of-contents) -->
- [Setting up STACKL locally](#setting-up-stackl-locally)
- [Making a contribution](#making-a-contribution)
  - [Submitting a contribution](#submitting-a-contribution)
  - [Submitting an issue fix](#submitting-an-issue-fix)
  - [Submitting a bug report](#submitting-a-bug-report)
  - [Submitting a feature or enhancement suggestion](#submitting-a-feature-or-enhancement-suggestion)
- [Styleguides](#styleguides)

Why they should read this
What we are looking for
Link to code of conduct

# Setting up STACKL locally

To install STACKL and start having a look at the codebase and tinkering around with it, you need to

1.  [Fork](https://help.github.com/articles/fork-a-repo/) the project, clone
    your fork:

    ```sh
    # Clone your fork
    git clone https://github.com/<your-username>/stackl.git

    # Navigate to the newly cloned directory
    cd stackl
    ```

2.  ...

> Handy Tip: Keep your `master` branch pointing at the original repository and make
> pull requests from branches on your fork. To do this, run:
>
> ```sh
> git remote add upstream https://github.com/<your-username>/readme-md-generator.git
> git fetch upstream
> git branch --set-upstream-to=upstream/master master
> ```
>
> This will add the original repository as a "remote" called "upstream," then
> fetch the git information from that remote, then set your local `master`
> branch to use the upstream master branch whenever you run `git pull`. Then you
> can make all of your pull request branches based on this `master` branch.
> Whenever you want to update your version of `master`, do a regular `git pull`.

# Making a contribution

## Submitting an issue fix

To submit an issue fix, fork the repository by clicking on `Fork` in the top right corner, create a new branch according to the following naming conventions:

- feature/issue-100
- bug/issue-100

Try to make all your changes in one commit. Make sure the commit message is structured as follows:

```markdown
Subject -> max 140 characters, describe the change

Body -> describe why the change was necessary 

Fixes #issue-number -> the issue number you are fixing
```

Please go through existing issues and pull requests to check if somebody else is already working on it.

Also, make sure to run the tests and lint the code before you commit your changes. Stackl uses [YAPF](https://github.com/google/yapf) to format Python code.

Make sure to create a pull request. Additionally, you can provide extra information.

If changes are requested, you can make a new commit. If there are multiple commits, the Stackl team will [squash](https://github.blog/2016-04-01-squash-your-commits/) the commits when merging.

Feel free to also make a pull request to start a discussion or ask questions.

## Submitting a bug report

To submit a bug report, visit the GitHub page, click on `issues`, click on `New Issue`, pick the `Bug` template and describe the bug.
The Stackl team tries to answer these as fast as possible.

## Submitting a feature or enhancement request

To submit a feature or enhancement request, visit the GitHub page, click on `issues`, click on `New Issue`, pick the `Feature` template and describe the feature you would like to have implemented.
The Stackl team tries to answer these as fast as possible.

# Styleguides
