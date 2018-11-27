# Contributing

This is a guideline for anybody interesting in contributing.

You may be part of the HackRU R&D team, in which case you probably know a lot more about this project than the average open source contributor.

That said, it's nice to have stuff written down - not only for those not in the team.

## What is R&D and can I join?

R&D is the HackRU dev team and they oversee the creation of HackRU applications.

You can join if you're at Rutgers. Otherwise, feel free to contribute but we may not be
able to easily accommodate you.

## How to contribute?

There'll always be issues opened to summarise what the project is up to and the main heading. If an issue is labelled
"bug" or "security," it has priority. Otherwise it might bot be very important.

There's also a [list of TO-DOs in the README.](README#whats-next-for-lcs)
So that will give you an idea of the priorities. Feel free to open issues too, but the R&D team will have a project
lead who will chose the priorities.

## More technical stuff

Basically, you'll have to clone, branch, and set up the python to work.
```
git clone https://github.com/HackRU/lcs.git
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

git checkout -b my-feature-branch
```

So yeah... then you'll have to just code.
See [#20](#20) for more on the testing.

## Notes on PRs

The PRs, besides being automatically linted and tested,
will also need a review. This is to give the project lead a little more control and to force changes to be a little
more open.

Desperate bug fixes may have to be reviewed faster, but in general many people tend to pay attention when there's a bug,
so the review should come quickly.

This is to force feature branches. Because feature branches are good and nice.

### Rebasing?

Yes.

Rebase master as much as reasonable.

This is to have a linear commit history.

And no merge commits, please.

See [the atlassian tutorial for more.](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase)

The only time and place it's OK to rebase is on master with a PR. Do not rebase elsewhere unless everybody you're collaborating
with knows you're rebasing and prepares for it.

Talk to us if you need help with a rebase or anything.

### Delete all your branches when you merge

Please. Let's not have loads of useless branches floating around.
