"""
postrebuild.py
Author: Joshua Parker

Builds a list of ALL the posts a user has commented on saving the post id 
- excludes posts submitted by the user
- only their comments on posts

To run use:
    python postrebuild.py username
    * where username is the user you want the list of comments for
"""

import praw, os, sys, time
from requests import HTTPError

def saveList(itemToSave, listToSave):
    """
    Writes the updated list of summed articles to disk puts newest posts at bottom of list
    @param itemToSave: the curent value to save to disk
    @param listToSave: the current list to append the value to
    """
    if not os.path.exists(listToSave.strip()+".txt"):
    	f = open(listToSave.strip() + ".txt", "w")
    	f.close()
    with open(listToSave.strip() + ".txt", "r+") as f: 
    	content = f.read()
    	f.seek(0,0)
    	f.write(itemToSave.replace('\r\n', '') + '\r\n' + content)

def getComments(r, userName):
    """
    Gets the list of the users comments
    @param r: reddit instance
    @param userName: the user name of the redditor to collect the posts of
    @return all_comments: the list of all comments by the given user
    """
    try:
        # gets the comments sorted by new, with no limit to the amount to get
        all_comments = r.get_redditor(userName).get_comments(sort='new', time='all', limit=None)
    except praw.errors.RateLimitExceeded as e:
        print "Rate limit error sleeping for: " + str(e.sleep_time)
        time.sleep(e.sleep_time)
    except praw.errors.APIException:
        print "PRAW API error"
    except HTTPError as e:
        print "http error: " + str(e.response.status_code)
        time.sleep(30)
        # try again on http errors
        all_comments = getComments(r, userName)
    return all_comments

## Main Method ##
if __name__ == "__main__":
    if len(sys.argv) < 2: 
        print "User name missing"
        print "e.g.\npython postrebuild.py timbl"
        sys.exit(1)
    
    r = praw.Reddit(user_agent="comment_restore_bot")
    print "Getting old comments for " + str(sys.argv[1]) + "..."
    all_comments = getComments(r, sys.argv[1])

    print "sorting..."
    for c in all_comments:
        # assuming t1 is for self/user posted content
        # where as t3 appears to be on comments on others posts
        if 't1' not in str(c.parent_id):
    	   saveList(str(c.parent_id).replace('t3_',''), str(c.subreddit).lower())
    print "done..."