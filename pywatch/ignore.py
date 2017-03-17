from fnmatch import fnmatch

# Parse the contents of the gitignore folder
gitignore_contents = []
try:
    with open('.gitignore', 'r') as f:
        for line in f.readlines():
            line = line.strip()
            if line == '':
                continue
            if line[0] == '#':
                continue
            if '.' in line:
                # Exclude file types as-is
                gitignore_contents.append(line)
            else:
                line = './%s*' % line
                gitignore_contents.append(line)
except IOError:
    print('No .gitignore file found')


# Manually add some stuff
custom_ignore = ['./.git*']

ignore_args = []
ignore_args.extend(gitignore_contents)
ignore_args.extend(custom_ignore)


# Return True if we should
def do_ignore(path):
    ignore = False
    for i in ignore_args:
        if fnmatch(path, i):
            ignore = True
            break
    return ignore
