# Lab Tools

Templates and scripts for lab operations

## Getting started

```
git clone https://github.com/ml4sts/labtools.git
cd labtools
pip install .
```

## Current Features

- work with accountability issues, try `lab acc --help` for docs


## Design 

Short version: 
- provides the `lab` command with sub commands in groups
- everything in here should allow us to make new/multiple repos for other functions (like accountability and reading groups)


### Detailed example (accountability)

I locally ran 
```
gh repo clone ml4sts/accountability
cd accountability
lab acc init 
```

This set up the scheduler action which is stored in this repo in the templates folder ([scheduler.yml](labtools/templates/scheduler.yml)) and a gitignore (also from this repo's templates [gitignore template](labtools/templates/gitignore.txt))

Then, each of us can use that action triggered manually in the [accountability repo](https://github.com/ml4sts/accountability) to create a personalized issue creating action on a schedule (choosing day and setting it to pull issues assigned to our username). The action installs this library when it runs, then uses commands from this repo.  

The actions required permissions, so I created fine grained PATs with the permissions and added them as secrets in the accountability repo.

Permissions: 
 Read access to metadata
 Read and Write access to actions, code, issues, pull requests, and workflows

### How to add new features 


If it is related to existing features add a function to the appropriate existing .py file (eg if extending accountabilit edit [accountability.py](labtools/accountability.py)), if a new big feature, add a new .py file with the functions needed in the `labtools` folder. 
Note: 
- All of the functionality should be in these files. 
- Nothing in these files should depend on Click. 
- All functions in these files should return something

Add the interface commands to [cli.py](labtools/cli.py). This should be as minimal as possible and call functions from other files. 
- Most lines in this file should be dependent on the click library. 
- Commands should mostly use `click.echo` to give result to user, but may have side effect primarily (eg write file, but click.echo a progress update)

## Adding a news post (currently broken)

if you haven't yet cloned the lab site:
```
git clone https://github.com/ml4sts/ml4sts.github.io.git
```

Once you have it, cd and creata  new branch
```
cd ml4sts.github.io
git checkout -b news_topic
```

To create a post dated at the current date/time:
```
labnews kewyword --title 'a phrase title headline that will show'
```
For more options use: `labnews --help`

Then edit the file `YYYY-MM-DD-keyword.md` and add in any details to the body.

When it's done

```
git add _news/
git commit -m 'add <topic> post'
git push
```

and then use the link in the response to make a pull request
