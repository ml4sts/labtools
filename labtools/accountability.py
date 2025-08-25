from datetime import datetime, timedelta
import json
import string
import os
from .utils import load_template_file
from markdown_it import MarkdownIt
from markdown_it.tree import SyntaxTreeNode


# These are defined here so they can be used in multiple places and only maintained in one place
file_generator = {'open_issues':'gh search issues --owner=ml4sts --assignee {username} --json title,url  --state=open \
          -- -label:goals,log > open_issues.json',
               'closed_issues':'gh search issues --owner=ml4sts --assignee {username} --json title,url  --updated "{dates}" \
          --state=closed -- -label:goals,log > closed_issues.json'}

acc_issue_defaults = {'questions':'```\n- *question1 here*:\n- *question2 here*:\n```' ,
                        'challenges':'',
                        'help_needed':'',
}

# secret constants 
# this is the basic gh secret
SECRET_BASIC = '{{ secrets.GITHUB_TOKEN }}'
# this has the following permissions to all ml4sts repos:
#  Read access to code and metadata
#  Read and Write access to issues
SECRET_LAB_REPO_ISSUES = '{{ secrets.LAB_REPO_ISSUES }}'
# this has the following permissions on the one accountability repo
#   Read access to metadata
#   Read and Write access to actions, code, issues, pull requests, and workflows
SECRET_WORKFLOW_EDIT = '{{ secrets.WORKFLOW_EDITING_TOKEN }}'

# for splitting the files as through the interactive logging 
file_split = '~~~~~~'

def initialize_accountability_repo(path):
    '''
    Initialize the accountability repo at the given path
    '''
    progress = []
    # write the scheduleer.yml to .github/workflows
    os.makedirs(os.path.join(path,'.github','workflows'),exist_ok=True)
    # write the template for issues to .github/ISSUE_TEMPLATE
    os.makedirs(os.path.join(path,'.github','ISSUE_TEMPLATE'),exist_ok=True)
    
      
    scheduler_action = load_template_file('scheduler.yml')
    # write the scheduler action to .github/workflows/scheduler.yml
    sched_path = os.path.join(path,'.github','workflows','scheduler.yml')
    
    with open(sched_path,'w') as f:
        f.write(scheduler_action) 
    progress.append(f'Wrote scheduler action to {sched_path}')

    # get gitignore content and write to .gitignore
    git_ignore_content = load_template_file('gitignore.txt')
    gitignore_path = os.path.join(path,'.gitignore')

    # determine to write or append the difference
    gi_exist = os.path.exists(gitignore_path)
    # if gitinore exists, read it and figure out what template content is new
    if gi_exist:
        with open(gitignore_path,'r') as f:
            existing_content = f.readlines()

        existing_content = [line.strip() for line in existing_content]
        git_ignore_content = [line.strip() for line in git_ignore_content.split('\n') 
                              if line.strip() not in existing_content]

    if git_ignore_content:    
        gi_write_type_from_exist = {True: 'appended',
                False: 'wrote'}
        gi_write = gi_write_type_from_exist[gi_exist]
        with open(gitignore_path,gi_write[0]) as f:
            f.write('\n'.join(git_ignore_content) )
            
        progress.append(f'{gi_write} to {gitignore_path}')
    else:
        progress.append(f'.gitignore already has all required content, no changes made')

    return progress
    
    

    

def issues_to_checklist(issues_json_dict,open=True):
    '''
    Convert a json of gh issues to a markdown checklist
    '''
    state_char = ' ' if open else 'x'
    checklist = []
    for issue in issues_json_dict:
        checklist.append(f"- [{state_char}] [{issue['title']}]({issue['url']}) ")

    return '\n'.join(checklist) 


def get_date_range(reference_date=None, duration=7):
    '''
    Get the search string for the duration days prior to the reference date


    Returns:    
    --------
    date_range : str
        date range string for gh issue search
    '''
    if reference_date:
        today = datetime.fromisoformat(reference_date)
    else:
        today = datetime.now()

    week_ago = today - timedelta(days=duration)
    date_range = f"{week_ago.date()}..{today.date()}"
    return date_range

def generate_basic_acc_issue(closed_issues_json='closed_issues.json',
                             open_issues_json='open_issues.json',
                             data_dict={}):
    '''
    Generate a basic accountability issue from json of closed and open issues

    Parameters:
    -----------
    closed_issues_json : file-like or dict
        json file-like object of closed issues
    open_issues_json : file-like or dict
        json file-like object of open issues

    Returns:
    --------
    md_issue : str
        markdown text for the issue
    '''
    if not isinstance(closed_issues_json,dict):
        closed_issues_dict = json.load(closed_issues_json)
    else:
        closed_issues_dict = closed_issues_json

    if not isinstance(open_issues_json,dict):
        open_issues_dict = json.load(open_issues_json)
    else:
        open_issues_dict = open_issues_json

    closed_checklist = issues_to_checklist(closed_issues_dict,open=False)
    open_checklist = issues_to_checklist(open_issues_dict,open=True)

    # put the info into a dicationary for the template
    data_dict.update({'closed_checklist':closed_checklist,
                'open_checklist':open_checklist})
    
    md_issue = load_and_fill_template('accountability_issue.md', data_dict)
    return md_issue
    
def load_and_fill_template(template_file, data_dict):
    '''
    fill a template, with potentially missing fields, with data
    '''
    # load the template
    # load the template
    if '\n' in template_file:
        md_template = template_file
    else:
        md_template = load_template_file(template_file)
        md_template, _ ,_ = parse_template(md_template)

    # fill not provided values with defult values 
    formatter = string.Formatter()
    for _, key, _, _ in formatter.parse(md_template):
        if key not in data_dict:
            data_dict[key] = ''

    # merge data with the template
    md_issue = md_template.format_map(data_dict)
    return md_issue

def get_prompt(context, display=True):
    '''
    get the prompt (last  comment) from context 

    Parameters:
    -----------
    context : str
        the context (literal text from the fstring)
    display : bool
        whether to format the prompt for display or not(for file use)
    '''
    md = MarkdownIt()
    tokens = md.parse(context)
    # get heading and prompt 
    mdtree = SyntaxTreeNode(tokens)
    
    # find the first 'html_block' and 'heading'
    last_comment = ''
    heading = ''
    for node in reversed(mdtree.children):
        node_type = node.type
        if node_type == 'html_block':
            # convert html comment to text
            last_comment = node.content
        elif node_type == 'heading':
            # already clean
            heading = node.children[0].content
        if heading and last_comment:
            break
    # format for type of display
    if display:
        prompt = f'{heading}: {last_comment.strip('><!--\n ') }'
    else:
        prompt = f'<!-- {heading}: {last_comment.strip("><!--\n ")} -->'
    return prompt


def parse_template(template_file,display_prompts=True):
    '''
    Parse a template file to get the fields it requires

    Parameters:
    -----------
    template_file : str 
        the template file name of a valid template in the package's template dir or 
        a string of another tempalte

    Returns:
    --------
    md_template_out : str
        template with file fields converted to {field}
    text_feilds : dict
        dictionary of text fields required by the template and their prompts
    file_feilds : list
        list of files required by the template
    '''
    # load the template
    if '\n' in template_file:
        md_template_in = template_file
    else:
        md_template_in = load_template_file(template_file)

    # parse the template to get the fields
    formatter = string.Formatter()
    file_feilds =[]
    text_feilds = {}
    md_template_out = ''
    for context, key, src, _ in formatter.parse(md_template_in):
        md_template_out += context + '\n\n' 
        if  src == 'file':
            text_key = key.replace('issues','checklist')
            file_feilds.append(key)
            text_feilds[text_key] = f' review the checklist and reorder as needed lines above {file_split} will be removed'
            md_template_out += f'{{{text_key}}}'
        else:
            # further parse the context to get the prompt (as md)
            text_feilds[key] = get_prompt(context,display=display_prompts)
            md_template_out += f'{{{key}}}'
    return md_template_out, text_feilds, file_feilds

def generate_schedule_action(username,name,day_of_week):
    '''
    Generate the action to schedule acc issues

    Parameters:
    -----------
    username : str
        github username
    name : str
        real name
    day_of_week : int
        day of week to run (1=Mon, 5=Friday)
    
    Returns:
    --------
    action : str
        the action text
    '''
    template = load_template_file('create_acc_issue.yml')

    # these parts are template that need values before beign placed in the template
    prefilled_scripts = {'open_issues':file_generator['open_issues'].format(username=username),
                         'closed_issues':file_generator['closed_issues'].format(username=username,
                                                                               dates='$dates')}
    
    #  these are the values that will be filled in the template
    template_info = {'SECRET_BASIC':SECRET_BASIC,
                    'SECRET_LAB_REPO_ISSUES':SECRET_LAB_REPO_ISSUES,
                    'SECRET_WORKFLOW_EDIT':SECRET_WORKFLOW_EDIT, 
                    'username':username, 'name':name,
                    'day_of_week':day_of_week,
                    'event':'{{ github.event_name }}',
                    'duration':'{{ github.event.inputs.days }}'}
    
    template_info.update(prefilled_scripts)
    action = template.format_map(template_info)
    return action