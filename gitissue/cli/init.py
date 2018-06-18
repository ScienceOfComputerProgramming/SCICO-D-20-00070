from gitissue.tools.repo import get_git_remote_type, get_repo_type_from_user


def main(args):
    remotes = get_git_remote_type()

    if not remotes:
        repo_type = get_repo_type_from_user()
        remotes.append(repo_type)

    print(remotes)

    return
