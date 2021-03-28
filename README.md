# Lab Tools

Templates and scripts for lab operations

## Getting started

```
git clone https://github.com/ml4sts/labtools.git
cd labtools
pip install .
```
## New member

if you haven't yet cloned the lab site:
```
git clone https://github.com/ml4sts/ml4sts.github.io.git
```

Once you have it, navigate to it and create a branch with your name in the place of add_name
```
cd ml4sts.github.io
git checkout -b add_name
```

To create a your file
```
newmember 'first last' --role 'undergraduate researcher'
```

then edit the file named `first_last.md` to include your bio and add any links you want.

When it's done

```
git add _members/
git commit -m 'add <topic> post'
git push
```

and then use the link in the response to make a pull request


## Adding a news post

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
