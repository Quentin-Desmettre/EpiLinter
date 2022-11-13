import os, re, sys
from datetime import datetime

# steps:
# - get list of every commit
# - from this list, get list of new commits
#   => to do that, add every commit from the beg of the list, and stop once a commit matches release(major|minor|fix): message
# - get last release version, and the type for this release
# - Pretty format the previous list
# - merge it into the changelog (after the HEADER section)


# How to get commits for a version ?
#   Parse commits from oldest to newest:
#       If a commit matches the regex release(major|minor|fix): text, stop collecting commits, and generate the changelog for the collected commits.
#       The version for this changelog, will be the last one incremented with the type for this release

COMMIT_TYPES = {
    "feat": "Features",
    "fix": "Bug fixes",
}
# getting the current date and time
CURRENT_DATETIME = datetime.now()

REALESE_PATTERN = re.compile("release\((major|minor|patch)\): [\s\S]+")

RELEASE_TYPES = ["major", "minor", "patch"]

def getBodyForCommitHash(commit_hash):
    if commit_hash == "-1":
        with open("pr_body", "r") as commit_msg:
            return commit_msg.read()

    os.system("git log --format=%b -n 1 " + commit_hash + " > out")
    with open("out", "r") as bodies_file:
        return bodies_file.read()

def getCommitMessageFromHash(hash):
    if commit_hash == "-1":
        with open("pr_msg", "r") as commit_msg:
            return commit_msg.read()

    command = "git log --format=%s -n 1 " + hash + " > out"
    os.system(command)
    with open("out", "r") as bodies_file:
        return bodies_file.read()

def getCommitDateFromHash(hash):
    if commit_hash == "-1":
        return CURRENT_DATETIME.strftime("%d/%m/%Y")
    command = "git log --format=%cs -n 1 " + hash + " > out"
    os.system(command)
    with open("out", "r") as bodies_file:
        body = bodies_file.read()
        if body[-1] == "\n":
            body = body[:-1]
        body = body.split("-")
        body.reverse()
        return "/".join(body)

def gen_changelog_for_commits(commits, release, release_commit_message, release_commit_hash):
    changelog_to_merge = "# Release {}.{}.{} ({}): {}\n\n".format(release[0], release[1], release[2], getCommitDateFromHash(release_commit_hash), release_commit_message)
    changelog_to_merge += "## What's new ?\n"
    if len(getBodyForCommitHash(release_commit_hash)) > 1:
        changelog_to_merge += getBodyForCommitHash(release_commit_hash)
        changelog_to_merge += "\n\n## Full explanations\n\n"
    category_is_empty = True
    for commit_type in COMMIT_TYPES:
        to_add = "### {}\n\n\n".format(COMMIT_TYPES[commit_type])
        for commit in commits:
            if commit.startswith(commit_type):
                category_is_empty = False
                to_add += " *{}\n".format(commit.split(":")[1])
        if not category_is_empty:
            changelog_to_merge += to_add + "\n"
        category_is_empty = True
    changelog_to_merge += "\n---\n"
    return changelog_to_merge

def getEveryCommitHash():
    # Get list of every commit
    os.system('git log --pretty=format:"%H" > messages')

    commits_file = open("messages", "r")
    commits_hashes = commits_file.readlines()
    commits_hashes.reverse() # To order commits from oldest to newest
    commits_hashes.append("-1")
    commits_file.close()

    return commits_hashes

def doesRegexMatch(commit):
    return  (REALESE_PATTERN.match(commit) and REALESE_PATTERN.match(commit).group(1) in RELEASE_TYPES)


# Parse this list of commit
every_commit_hash = getEveryCommitHash()
# exit(0)
# exit(1)
commits_for_changelog = []
changelogs = []
release = [0, 0, 0]
line = 0
for commit_hash in every_commit_hash:
    if commit_hash[-1] == "\n":
        commit_hash = commit_hash[:-1]
    commit = getCommitMessageFromHash(commit_hash)
    if commit[-1] == "\n":
        commit = commit[:-1]
    if doesRegexMatch(commit):
        release_type = REALESE_PATTERN.match(commit).group(1)
        index = RELEASE_TYPES.index(release_type)
        release[index] += 1
        for i in range(index + 1, 3):
            release[i] = 0
        changelogs.append(gen_changelog_for_commits(commits_for_changelog, release, commit.split(":", 2)[1], commit_hash))
        commits_for_changelog = []
    else:
        commits_for_changelog.append(commit)
    line += 1

# Put changes, newer first
print("# Changelog\n\nAll notable changes to this project are documented here.\n")
changelogs.reverse()
for i in changelogs:
    print(i)

with open("version.json", "w") as version:
    version.write("{")
    version.write('"version": "{}.{}.{}"'.format(str(release[0]), str(release[1]), str(release[2])))
    version.write("}")