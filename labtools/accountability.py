from datetime import datetime, timedelta

def issues_to_checklist(issues_json_dict,open=True):
    '''
    Convert a json of gh issues to a markdown checklist
    '''
    state_char = ' ' if open else 'x'
    checklist = []
    for issue in issues_json_dict:
        checklist.append(f"- [{state_char}] {issue['url']} ")

    return '\n'.join(checklist) 


def get_date_range(reference_date=None):
    '''
    Get the search string for the last 7 days


    Returns:    
    --------
    date_range : str
        date range string for gh issue search
    '''
    if reference_date:
        today = datetime.fromisoformat(reference_date)
    else:
        today = datetime.now()

    week_ago = today - timedelta(days=7)
    date_range = f"{week_ago.date()}..{today.date()}"
    return date_range