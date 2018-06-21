def find_pattern_in_tree(commit_tree, pattern, commit_sha):
    matches = []
    if commit_tree.type != 'submodule':
        for item in commit_tree:
            if item.type == 'blob':
                # read the data contained in that file
                try:
                    object_contents = item.data_stream.read().decode('utf-8')
                    matched_issues = pattern.findall(object_contents)

                    # if a string match for issue found
                    if matched_issues is not None:
                        matches.extend(matched_issues)
                except UnicodeDecodeError:
                    pass
            else:
                matches.extend(find_pattern_in_tree(
                    item, pattern, commit_sha))
    return matches
