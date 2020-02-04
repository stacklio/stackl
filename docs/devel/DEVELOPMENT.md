## Development

STACKL is written in the [Python](https://www.python.org) programming language.

If you are not familiar with Python we recommend you read through the [Python For
Beginners](https://www.python.org/about/gettingstarted/) article to familiarize yourself with the Python development environment.

Requirements:

- Git
- GitHub account (if you are contributing)
- Python (version 3.6.x)
- GNU Make

## Getting Started


## Workflow

1. Go to [https://github.com/stacklio/stackl](https://github.com/stacklio/stackl) and fork the repository
   into your account by clicking the "Fork" button.

1. Clone the fork to your local machine.

    ```bash
    git clone git@github.com:stacklio/stackl.git stackl
    cd stackl
    git remote add upstream https://github.com/stacklio/stackl.git
    ```

1. Create a branch for your changes.

    ```
    git checkout -b somefeature
    ```

2. Update your local branch with upstream.

    ```
    git fetch upstream
    git rebase upstream/master
    ```

3. Develop your changes and regularly update your local branch against upstream.

    - Be sure to run `make check` before submitting your pull request. You
      may need to run `go fmt` on your code to make it comply with standard Go
      style.

4. Commit changes and push to your fork.

    ```
    git commit -s
    git push origin somefeature
    ```

5. Submit a Pull Request via https://github.com/\<GITHUB USERNAME>/stackl. You
   should be prompted to with a "Compare and Pull Request" button that
   mentions your branch.

6. Once your Pull Request has been reviewed and signed off please squash your
   commits. If you have a specific reason to leave multiple commits in the
   Pull Request, please mention it in the discussion.

   > If you are not familiar with squashing commits, see [the following blog post for a good overview](http://gitready.com/advanced/2009/02/10/squashing-commits-with-rebase.html).


### Tool Dependencies

> placeholder
