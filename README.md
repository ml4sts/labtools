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

- provides the `lab` command with sub commands in groups
- everything in here should allow us to make new/multiple repos for other functions (like accountability and reading groups)



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
