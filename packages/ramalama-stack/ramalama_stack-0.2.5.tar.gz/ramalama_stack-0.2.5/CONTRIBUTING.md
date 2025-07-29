# Contributing to ramalama-stack

We'd love to have you join the community!
Below summarizes the processes that we follow.

## Topics
`
* [Reporting Issues](#reporting-issues)
* [Working On Issues](#working-on-issues)
* [Contributing To ramalama-stack](#contributing-to-ramalama-stack-1)
* [Submitting Pull Requests](#submitting-pull-requests)
* [Communications](#communications)
* [Code of Conduct](#code-of-conduct)


## Reporting Issues

Before reporting an issue, check our backlog of [open issues](https://github.com/containers/ramalama-stack/issues) to see if someone else has already reported it.
If so, feel free to add your scenario, or additional information, to the discussion.
Or simply "subscribe" to it to be notified when it is updated.
Please do not add comments like "+1" or "I have this issue as well" without adding any new information.
Instead, please add a thumbs-up emoji to the original report.

Note: Older closed issues/PRs are automatically locked.
If you have a similar problem please open a new issue instead of commenting.

If you find a new issue with the project we'd love to hear about it!
The most important aspect of a bug report is that it includes enough information for us to reproduce it.
To make this easier, there are three types of issue templates you can use.
* If you have a bug to report, please use *Bug Report* template.
* If you have an idea to propose, please use the *Feature Request* template.
* If your issue is something else, please use the default *Blank issue* template.

Please include as much detail as possible, including all requested fields in the template.
Not having all requested information makes it much harder to find and fix issues.
A reproducer is the best thing you can include.
Reproducers make finding and fixing issues much easier for maintainers.
The easier it is for us to reproduce a bug, the faster it'll be fixed!

Please don't include any private/sensitive information in your issue!
Security issues should NOT be reported via Github and should instead be reported via the process described [here](https://github.com/containers/common/blob/main/SECURITY.md).

## Working On Issues

Once you have decided to contribute to ramalama-stack by working on an issue, check our backlog of [open issues](https://github.com/containers/ramalama-stack/issues) looking for any that are unassigned.
If you want to work on a specific issue that is already assigned but does not appear to be actively being worked on, please ping the assignee in the issue and ask if you can take over.
If they do not respond after several days, you can notify a maintainer to have the issue reassigned.
When working on an issue, please assign it to yourself.
If you lack permissions to do so, you can ping the `@containers/ramalama-stack-maintainers` group to have a maintainer set you as assignee.

## Contributing To ramalama-stack

This section describes how to make a contribution to ramalama-stack.

### Prepare your environment

The minimum version of Python required to use ramalama-stack is Python 3.12

### Fork and clone ramalama-stack

First, you need to fork this project on GitHub.
Then clone your fork locally:
```shell
$ git clone git@github.com:<you>/ramalama-stack
$ cd ./ramalama-stack/
```

### Install required tools

We use [uv](https://github.com/astral-sh/uv) to manage python dependencies and virtual environments.
You can install `uv` by following this [guide](https://docs.astral.sh/uv/getting-started/installation/).

You can install the dependencies by running:

```bash
cd ramalama-stack
uv sync
source .venv/bin/activate
```

> [!NOTE]
> You can use a specific version of Python with `uv` by adding the `--python <version>` flag (e.g. `--python 3.12`)
> Otherwise, `uv` will automatically select a Python version according to the `requires-python` section of the `pyproject.toml`.
> For more info, see the [uv docs around Python versions](https://docs.astral.sh/uv/concepts/python-versions/).

### Adding dependencies

Please add dependencies using the [uv-documented approach](https://docs.astral.sh/uv/concepts/projects/dependencies/#adding-dependencies).

This should update both the `pyproject.toml` and the `uv.lock` file.

The `requirements.txt` file should be updated as well by `pre-commit` - you can also do this manually via `uv export --frozen --no-hashes --no-emit-project --no-default-groups --output-file=requirements.txt`.

## Testing

ramalama-stack provides a small suite of tests in the `test/` directory.
Most pull requests should be accompanied by test changes covering the changes in the PR.
Pull requests without tests will receive additional scrutiny from maintainers and may be blocked from merging unless tests are added.
Maintainers will decide if tests are not necessary during review.

### Types of Tests

There are several types of tests run by ramalama-stack's upstream CI.
* Pre-commit checks
* Functional testing
* Integration testing
* PyPI build and upload testing

## Documentation

Make sure to update the documentation if needed.
ramalama-stack is documented via its [README](https://github.com/containers/ramalama-stack/blob/main/docs/README.md) and files in the `docs/` directory.

## Submitting Pull Requests

No Pull Request (PR) is too small!
Typos, additional comments in the code, new test cases, bug fixes, new features, more documentation, ... it's all welcome!

While bug fixes can first be identified via an "issue" in Github, that is not required.
It's ok to just open up a PR with the fix, but make sure you include the same information you would have included in an issue - like how to reproduce it.

PRs for new features should include some background on what use cases the new code is trying to address.
When possible and when it makes sense, try to break up larger PRs into smaller ones - it's easier to review smaller code changes.
But only if those smaller ones make sense as stand-alone PRs.

Regardless of the type of PR, all PRs should include:
* Well-documented code changes, both through comments in the code itself and high-quality commit messages.
* Additional tests. Ideally, they should fail w/o your code change applied.
* Documentation updates to reflect the changes made in the pull request.

Squash your commits into logical pieces of work that might want to be reviewed separately from the rest of the PRs.
Squashing down to just one commit is also acceptable since in the end the entire PR will be reviewed anyway.
When in doubt, squash.

When your PR fixes an issue, please note that by including `Fixes: #00000` in the commit description.
More details on this are below, in the "Describe your changes in Commit Messages" section.

The ramalama-stack repo follows a one-ack policy for merges.
PRs will be approved and merged by a repo owner.
Two reviews are required for a pull request to merge, including sourcery.ai

### Describe your Changes in Commit Messages

Describe your problem.
Whether your patch is a one-line bug fix or 5000 lines of a new feature, there must be an underlying problem that motivated you to do this work.
Convince the reviewer that there is a problem worth fixing and that it makes sense for them to read past the first paragraph.

Describe user-visible impact.
Straight up crashes and lockups are pretty convincing, but not all bugs are that blatant.
Even if the problem was spotted during code review, describe the impact you think it can have on users.
Keep in mind that the majority of users run packages provided by distributions, so include anything that could help route your change downstream.

Quantify optimizations and trade-offs.
If you claim improvements in performance, memory consumption, stack footprint, or binary size, include
numbers that back them up.
But also describe non-obvious costs.
Optimizations usually aren’t free but trade-offs between CPU, memory, and readability; or, when it comes to heuristics, between different workloads.
Describe the expected downsides of your optimization so that the reviewer can weigh costs against
benefits.

Once the problem is established, describe what you are actually doing about it in technical detail.
It’s important to describe the change in plain English for the reviewer to verify that the code is behaving as you intend it to.

Solve only one problem per patch.
If your description starts to get long, that’s a sign that you probably need to split up your patch.

If the patch fixes a logged bug entry, refer to that bug entry by number and URL.
If the patch follows from a mailing list discussion, give a URL to the mailing list archive.
Please format these lines as `Fixes:` followed by the URL or, for Github bugs, the bug number preceded by a #.
For example:

```
Fixes: #00000
Fixes: https://github.com/containers/ramalama-stack/issues/00000
Fixes: https://issues.redhat.com/browse/RHEL-00000
Fixes: RHEL-00000
```

However, try to make your explanation understandable without external resources.
In addition to giving a URL to a mailing list archive or bug, summarize the relevant points of the discussion that led to the patch as submitted.

If you want to refer to a specific commit, don’t just refer to the SHA-1 ID of the commit.
Please also include the one-line summary of the commit, to make it easier for reviewers to know what it is about. If the commit was merged in GitHub, referring to a GitHub PR number is also a good option, as that will retain all discussion from development, and makes including a summary less critical.
Examples:

```
Commit f641c2d9384e ("fix bug in rm -fa parallel deletes") [...]
PR #00000
```

When referring to a commit by SHA, you should also be sure to use at least the first twelve characters of the SHA-1 ID.
The ramalama-stack repository holds a lot of objects, making collisions with shorter IDs a real possibility.
Bear in mind that, even if there is no collision with your six-character ID now, that condition may change five years from now.

The following git config settings can be used to add a pretty format for outputting the above style in the git log or git show commands:

```
[core]
	abbrev = 12
[pretty]
	fixes = Fixes: %h (\"%s\")
```

### Sign your PRs

The sign-off is a line at the end of the explanation for the patch.
Your signature certifies that you wrote the patch or otherwise have the right to pass it on as an open-source patch.
The rules are simple: if you can certify the below (from [developercertificate.org](https://developercertificate.org/)):

```
Developer Certificate of Origin
Version 1.1

Copyright (C) 2004, 2006 The Linux Foundation and its contributors.
660 York Street, Suite 102,
San Francisco, CA 94110 USA

Everyone is permitted to copy and distribute verbatim copies of this
license document, but changing it is not allowed.

Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the best
    of my knowledge, is covered under an appropriate open source
    license and I have the right under that license to submit that
    work with modifications, whether created in whole or in part
    by me, under the same open source license (unless I am
    permitted to submit under a different license), as indicated
    in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including all
    personal information I submit with it, including my sign-off) is
    maintained indefinitely and may be redistributed consistent with
    this project or the open source license(s) involved.
```

Then you just add a line to every git commit message:

    Signed-off-by: Joe Smith <joe.smith@email.com>

Use your real name (sorry, no pseudonyms or anonymous contributions).

If you set your `user.name` and `user.email` git configs, you can sign your commit automatically with `git commit -s`.

### Continuous Integration

All pull requests automatically run ramalama-stack's test suite.

There is always additional complexity added by automation, and so it sometimes can fail for any number of reasons.
This includes post-merge testing on all branches, which you may occasionally see [red bars on the status graph](https://github.com/containers/ramalama-stack/blob/main/docs/ci.md).

Most notably, the tests will occasionally flake.
If you see a single test on your PR has failed, and you do not believe it is caused by your changes, you can rerun the tests.
If you lack permissions to rerun the tests, please ping the maintainers using the `@containers/ramalama-stack-maintainers` group and request that the failing test be rerun.

If you see multiple test failures, you may wish to check the status graph mentioned above.
When the graph shows mostly green bars on the right, it's a good indication the main branch is currently stable.
Alternating red/green bars is indicative of a testing "flake", and should be examined (anybody can do this):

* *One or a small handful of tests, on a single task, (i.e. specific distro/version)
  where all others ran successfully:*  Frequently the cause is networking or a brief
  external service outage.  The failed tasks may simply be re-run by pressing the
  corresponding button on the task details page.

* *Multiple tasks failing*: Logically this should be due to some shared/common element.
  If that element is identifiable as a networking or external service (e.g. packaging
  repository outage), a re-run should be attempted.

* *All tasks are failing*: If a common element is **not** identifiable as
  temporary (i.e. container registry outage), please seek assistance via
  [the methods below](#communications) as this may be early indication of
  a more serious problem.

In the (hopefully) rare case there are multiple, contiguous red bars, this is
a ***very bad*** sign.  It means additional merges are occurring despite an uncorrected
or persistently faulty condition.  This risks additional bugs being introduced
and further complication of necessary corrective measures.  Most likely people
are aware and working on this, but it doesn't hurt [to confirm and/or try and help
if possible.](#communications).

## Communications

If you need help, you can contact the maintainers using the channels mentioned in RamaLama's [communications](https://github.com/containers/ramalama/blob/main/README.md#community) document.

For discussions around issues/bugs and features, you can use the GitHub
[issues](https://github.com/containers/ramalama-stack/issues)
and
[PRs](https://github.com/containers/ramalama-stack/pulls)
tracking system.

## Code of Conduct

As contributors and maintainers of the projects under the [Containers](https://github.com/containers) repository,
and in the interest of fostering an open and welcoming community, we pledge to
respect all people who contribute through reporting issues, posting feature
requests, updating documentation, submitting pull requests or patches, and other
activities to any of the projects under the containers umbrella. The full code of conduct guidelines can be
found [here](https://github.com/containers/common/blob/main/CODE-OF-CONDUCT.md).


### Bot Interactions

ramalama-stack uses [sourcery.ai](https://sourcery.ai/) for AI code reviews.

You can read their docs [here](https://docs.sourcery.ai/Code-Review/#interacting-with-sourcery) on how to interact with the bot.
