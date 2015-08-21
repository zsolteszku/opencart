__author__ = 'zsoltessig'


def read_config(file):
    result = []
    with open(file) as f:
        linenum = 0
        for line in f.readlines():
            linenum += 1
            line = line.strip()
            if not line.startswith("#") and len(line) is not 0:
                if line.endswith("="):
                    raise Exception("Incorrect line in file({}:{}): {}".format(file, linenum, line))
                key = line[0:line.index("=")].strip()
                value = line[line.index("=")+1:].strip()
                result.append((key, value))
    return result


def read_config_map(file):
    lst = read_config(file)
    result = dict()
    for item in lst:
        result[item[0]] = item[1]
    return result

def add_config(file, key, value):
    with open(file, "ab") as f:
        f.write("\n{} = {}".format(key, value))