import logging
logging.basicConfig(level=logging.ERROR)

import os.path
import argparse
import time
import subprocess
from ConfigParser import ConfigParser
from github2.client import Github

__here__ = os.path.dirname(__file__)
__sounds__ = os.path.join(__here__, 'sounds')


def play_audio(filename):
    return subprocess.Popen(['afplay %s' % filename],
                            shell=True, stdin=None,
                            stdout=None, stderr=None)


def github_client():
    config = ConfigParser()
    config.read(os.path.join(os.getenv('HOME'), '.gitconfig'))
    return Github(username=config.get('github', 'user'),
                  api_token=config.get('github', 'token'),
                  requests_per_second=1)


class IssueWatcher(object):

    def __init__(self, github, repo, silent=False):
        self.github = github
        self.repo = repo
        self.silent = silent
        self.open_before = set()

    def query(self, state):
        return set([issue.number for issue in
                    self.github.issues.list(self.repo, state=state)])

    def check(self):
        """
        Check open issues. Return a set of all issues closed since the last
        check.
        """
        open = self.query('open')
        newly_closed = set()
        newly_gone = self.open_before - open
        if len(newly_gone) > 0:
            # Some issues are no longer open, make sure they were closed
            # instead of deleted.
            closed = self.query('closed')
            newly_closed = newly_gone & closed
        self.open_before = open
        return newly_closed
    
    def run(self):
        newly_closed = self.check()
        if len(newly_closed) > 0:
            if not self.silent:
                print ("Closed issues in %s: %s" %
                       (self.repo,
                        ', '.join(["%d" % ii for ii in newly_closed])))
            self.issues_closed(newly_closed)

    def issues_closed(self, newly_closed):
        "Override this to do something cool."
        play_audio(os.path.join(__sounds__, 'small-clapping.mp3'))


def main():
    p = argparse.ArgumentParser(description='Applaud closing bugs.')
    p.add_argument('-s', '--silent', dest='silent', action='store_true',
                   help='no output')
    p.add_argument('--plist', dest='plist', action='store_true',
                   help="don't run, just generate a launchd plist")
    p.add_argument('repos', metavar='repos', type=str, nargs='+',
                   help='repos to check')
    p.add_argument('--check-seconds', metavar='N', type=int,
                   default=10, dest='check_seconds',
                   help='check issues every N seconds')
    args = p.parse_args()
    if not args.silent:
        print "Watching %s every %d seconds" % (', '.join(args.repos),
                                                args.check_seconds)

    github = github_client()
    watchers = []
    for repo in args.repos:
        watchers.append(IssueWatcher(github, repo, silent=args.silent))

    while True:
        for watcher in watchers:
            watcher.run()
        time.sleep(args.check_seconds)


if __name__ == '__main__':
    main()
