#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2014, Ruggero Marchei <ruggero.marchei@daemonzone.net>
# Copyright: (c) 2015, Brian Coca <bcoca@ansible.com>
# Copyright: (c) 2016-2017, Konstantin Shalygin <k0ste@k0ste.ru>
# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}

DOCUMENTATION = r'''
---
module: find
author: Brian Coca (@bcoca)
version_added: "2.0"
short_description: Return a list of files based on specific criteria
description:
    - Return a list of files based on specific criteria. Multiple criteria are AND'd together.
    - For Windows targets, use the M(win_find) module instead.
options:
    age:
        description:
            - Select files whose age is equal to or greater than the specified time.
            - Use a negative age to find files equal to or less than the specified time.
            - You can choose seconds, minutes, hours, days, or weeks by specifying the
              first letter of any of those words (e.g., "1w").
        type: str
    patterns:
        default: '*'
        description:
            - One or more (shell or regex) patterns, which type is controlled by C(use_regex) option.
            - The patterns restrict the list of files to be returned to those whose basenames match at
              least one of the patterns specified. Multiple patterns can be specified using a list.
            - The pattern is matched against the file base name, excluding the directory.
            - When using regexen, the pattern MUST match the ENTIRE file name, not just parts of it. So
              if you are looking to match all files ending in .default, you'd need to use '.*\.default'
              as a regexp and not just '\.default'.
            - This parameter expects a list, which can be either comma separated or YAML. If any of the
              patterns contain a comma, make sure to put them in a list to avoid splitting the patterns
              in undesirable ways.
        type: list
        aliases: [ pattern ]
    excludes:
        description:
            - One or more (shell or regex) patterns, which type is controlled by C(use_regex) option.
            - Items whose basenames match an C(excludes) pattern are culled from C(patterns) matches.
              Multiple patterns can be specified using a list.
        type: list
        aliases: [ exclude ]
        version_added: "2.5"
    contains:
        description:
            - A regular expression or pattern which should be matched against the file content.
        type: str
    paths:
        description:
            - List of paths of directories to search. All paths must be fully qualified.
        type: list
        required: true
        aliases: [ name, path ]
    file_type:
        description:
            - Type of file to select.
            - The 'link' and 'any' choices were added in Ansible 2.3.
        type: str
        choices: [ any, directory, file, link ]
        default: file
    recurse:
        description:
            - If target is a directory, recursively descend into the directory looking for files.
        type: bool
        default: no
    size:
        description:
            - Select files whose size is equal to or greater than the specified size.
            - Use a negative size to find files equal to or less than the specified size.
            - Unqualified values are in bytes but b, k, m, g, and t can be appended to specify
              bytes, kilobytes, megabytes, gigabytes, and terabytes, respectively.
            - Size is not evaluated for directories.
    age_stamp:
        description:
            - Choose the file property against which we compare age.
        type: str
        choices: [ atime, ctime, mtime ]
        default: mtime
    hidden:
        description:
            - Set this to C(yes) to include hidden files, otherwise they will be ignored.
        type: bool
        default: no
    follow:
        description:
            - Set this to C(yes) to follow symlinks in path for systems with python 2.6+.
        type: bool
        default: no
    get_checksum:
        description:
            - Set this to C(yes) to retrieve a file's SHA1 checksum.
        type: bool
        default: no
    use_regex:
        description:
            - If C(no), the patterns are file globs (shell).
            - If C(yes), they are python regexes.
        type: bool
        default: no
    min_depth:
        description:
            - Set the minimum number of levels to descend into.
            - Default is a minimal depth of 1.
        type: int
    depth:
        description:
            - Set the maximum number of levels to descend into.
            - Setting recurse to C(no) will override this value, which is effectively depth 1.
            - Default is unlimited depth.
        type: int
        version_added: "2.6"
seealso:
- module: win_find
'''


EXAMPLES = r'''
- name: Recursively find /tmp files older than 2 days
  find:
    paths: /tmp
    age: 2d
    recurse: yes

- name: Recursively find /tmp files older than 4 weeks and equal or greater than 1 megabyte
  find:
    paths: /tmp
    age: 4w
    size: 1m
    recurse: yes

- name: Recursively find /var/tmp files with last access time greater than 3600 seconds
  find:
    paths: /var/tmp
    age: 3600
    age_stamp: atime
    recurse: yes

- name: Find /var/log files equal or greater than 10 megabytes ending with .old or .log.gz
  find:
    paths: /var/log
    patterns: '*.old,*.log.gz'
    size: 10m

# Note that YAML double quotes require escaping backslashes but yaml single quotes do not.
- name: Find /var/log files equal or greater than 10 megabytes ending with .old or .log.gz via regex
  find:
    paths: /var/log
    patterns: "^.*?\\.(?:old|log\\.gz)$"
    size: 10m
    use_regex: yes

- name: Find /var/log all directories, exclude nginx and mysql
  find:
    paths: /var/log
    recurse: no
    file_type: directory
    excludes: 'nginx,mysql'

# When using patterns that contain a comma, make sure they are formatted as lists to avoid splitting the pattern
- name: Use a single pattern that contains a comma formatted as a list
  find:
    paths: /var/log
    file_type: file
    use_regex: yes
    patterns: ['^_[0-9]{2,4}_.*.log$']

- name: Use multiple patterns that contain a comma formatted as a YAML list
  find:
    paths: /var/log
    file_type: file
    use_regex: yes
    patterns:
      - '^_[0-9]{2,4}_.*.log$'
      - '^[a-z]{1,5}_.*log$'

'''

RETURN = r'''
files:
    description: All matches found with the specified criteria (see stat module for full output of each dictionary)
    returned: success
    type: list
    sample: [
        { path: "/var/tmp/test1",
          mode: "0644",
          "...": "...",
          checksum: 16fac7be61a6e4591a33ef4b729c5c3302307523
        },
        { path: "/var/tmp/test2",
          "...": "..."
        },
        ]
matched:
    description: Number of matches
    returned: success
    type: int
    sample: 14
examined:
    description: Number of filesystem objects looked at
    returned: success
    type: int
    sample: 34
'''

import fnmatch
import grp
import os
import pwd
import re
import stat
import sys
import time

from ansible.module_utils.basic import AnsibleModule


def pfilter(f, patterns=None, excludes=None, use_regex=False):
    '''filter using glob patterns'''
    if patterns is None and excludes is None:
        return True

    if use_regex:
        if patterns and excludes is None:
            for p in patterns:
                r = re.compile(p)
                if r.match(f):
                    return True

        elif patterns and excludes:
            for p in patterns:
                r = re.compile(p)
                if r.match(f):
                    for e in excludes:
                        r = re.compile(e)
                        if r.match(f):
                            return False
                    return True

    else:
        if patterns and excludes is None:
            for p in patterns:
                if fnmatch.fnmatch(f, p):
                    return True

        elif patterns and excludes:
            for p in patterns:
                if fnmatch.fnmatch(f, p):
                    for e in excludes:
                        if fnmatch.fnmatch(f, e):
                            return False
                    return True

    return False


def agefilter(st, now, age, timestamp):
    '''filter files older than age'''
    if age is None:
        return True
    elif age >= 0 and now - st.__getattribute__("st_%s" % timestamp) >= abs(age):
        return True
    elif age < 0 and now - st.__getattribute__("st_%s" % timestamp) <= abs(age):
        return True
    return False


def sizefilter(st, size):
    '''filter files greater than size'''
    if size is None:
        return True
    elif size >= 0 and st.st_size >= abs(size):
        return True
    elif size < 0 and st.st_size <= abs(size):
        return True
    return False


def contentfilter(fsname, pattern):
    """
    Filter files which contain the given expression
    :arg fsname: Filename to scan for lines matching a pattern
    :arg pattern: Pattern to look for inside of line
    :rtype: bool
    :returns: True if one of the lines in fsname matches the pattern. Otherwise False
    """
    if pattern is None:
        return True

    prog = re.compile(pattern)

    try:
        with open(fsname) as f:
            for line in f:
                if prog.match(line):
                    return True

    except Exception:
        pass

    return False


def statinfo(st):
    pw_name = ""
    gr_name = ""

    try:  # user data
        pw_name = pwd.getpwuid(st.st_uid).pw_name
    except Exception:
        pass

    try:  # group data
        gr_name = grp.getgrgid(st.st_gid).gr_name
    except Exception:
        pass

    return {
        'mode': "%04o" % stat.S_IMODE(st.st_mode),
        'isdir': stat.S_ISDIR(st.st_mode),
        'ischr': stat.S_ISCHR(st.st_mode),
        'isblk': stat.S_ISBLK(st.st_mode),
        'isreg': stat.S_ISREG(st.st_mode),
        'isfifo': stat.S_ISFIFO(st.st_mode),
        'islnk': stat.S_ISLNK(st.st_mode),
        'issock': stat.S_ISSOCK(st.st_mode),
        'uid': st.st_uid,
        'gid': st.st_gid,
        'size': st.st_size,
        'inode': st.st_ino,
        'dev': st.st_dev,
        'nlink': st.st_nlink,
        'atime': st.st_atime,
        'mtime': st.st_mtime,
        'ctime': st.st_ctime,
        'gr_name': gr_name,
        'pw_name': pw_name,
        'wusr': bool(st.st_mode & stat.S_IWUSR),
        'rusr': bool(st.st_mode & stat.S_IRUSR),
        'xusr': bool(st.st_mode & stat.S_IXUSR),
        'wgrp': bool(st.st_mode & stat.S_IWGRP),
        'rgrp': bool(st.st_mode & stat.S_IRGRP),
        'xgrp': bool(st.st_mode & stat.S_IXGRP),
        'woth': bool(st.st_mode & stat.S_IWOTH),
        'roth': bool(st.st_mode & stat.S_IROTH),
        'xoth': bool(st.st_mode & stat.S_IXOTH),
        'isuid': bool(st.st_mode & stat.S_ISUID),
        'isgid': bool(st.st_mode & stat.S_ISGID),
    }


def main():
    module = AnsibleModule(
        argument_spec=dict(
            paths=dict(type='list', required=True, aliases=['name', 'path']),
            patterns=dict(type='list', default=['*'], aliases=['pattern']),
            excludes=dict(type='list', aliases=['exclude']),
            contains=dict(type='str'),
            file_type=dict(type='str', default="file", choices=['any', 'directory', 'file', 'link']),
            age=dict(type='str'),
            age_stamp=dict(type='str', default="mtime", choices=['atime', 'ctime', 'mtime']),
            size=dict(type='str'),
            recurse=dict(type='bool', default=False),
            hidden=dict(type='bool', default=False),
            follow=dict(type='bool', default=False),
            get_checksum=dict(type='bool', default=False),
            use_regex=dict(type='bool', default=False),
            min_depth=dict(type='int'),
            depth=dict(type='int'),
        ),
        supports_check_mode=True,
    )

    params = module.params

    filelist = []

    if params['age'] is None:
        age = None
    else:
        # convert age to seconds:
        m = re.match(r"^(-?\d+)(s|m|h|d|w)?$", params['age'].lower())
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
        if m:
            age = int(m.group(1)) * seconds_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(age=params['age'], msg="failed to process age")

    if params['size'] is None:
        size = None
    else:
        # convert size to bytes:
        m = re.match(r"^(-?\d+)(b|k|m|g|t)?$", params['size'].lower())
        bytes_per_unit = {"b": 1, "k": 1024, "m": 1024**2, "g": 1024**3, "t": 1024**4}
        if m:
            size = int(m.group(1)) * bytes_per_unit.get(m.group(2), 1)
        else:
            module.fail_json(size=params['size'], msg="failed to process size")

    now = time.time()
    msg = ''
    looked = 0
    for npath in params['paths']:
        npath = os.path.expanduser(os.path.expandvars(npath))
        if os.path.isdir(npath):
            ''' ignore followlinks for python version < 2.6 '''
            for root, dirs, files in (sys.version_info < (2, 6, 0) and os.walk(npath)) or os.walk(npath, followlinks=params['follow']):
                if params['max_depth']:
                    depth = root.replace(npath.rstrip(os.path.sep), '').count(os.path.sep)
                    if files or dirs:
                        depth += 1
                    if depth > params['max_depth']:
                        del(dirs[:])
                        continue
                if params['min_depth']:
                    depth = root.replace(npath.rstrip(os.path.sep), '').count(os.path.sep)
                    if files or dirs:
                        depth += 1
                    if depth < params['min_depth']:
                        continue
                looked = looked + len(files) + len(dirs)
                for fsobj in (files + dirs):
                    fsname = os.path.normpath(os.path.join(root, fsobj))

                    if os.path.basename(fsname).startswith('.') and not params['hidden']:
                        continue

                    try:
                        st = os.lstat(fsname)
                    except Exception:
                        msg += "%s was skipped as it does not seem to be a valid file or it cannot be accessed\n" % fsname
                        continue

                    r = {'path': fsname}
                    if params['file_type'] == 'any':
                        if pfilter(fsobj, params['patterns'], params['excludes'], params['use_regex']) and agefilter(st, now, age, params['age_stamp']):

                            r.update(statinfo(st))
                            if stat.S_ISREG(st.st_mode) and params['get_checksum']:
                                r['checksum'] = module.sha1(fsname)
                            filelist.append(r)

                    elif stat.S_ISDIR(st.st_mode) and params['file_type'] == 'directory':
                        if pfilter(fsobj, params['patterns'], params['excludes'], params['use_regex']) and agefilter(st, now, age, params['age_stamp']):

                            r.update(statinfo(st))
                            filelist.append(r)

                    elif stat.S_ISREG(st.st_mode) and params['file_type'] == 'file':
                        if pfilter(fsobj, params['patterns'], params['excludes'], params['use_regex']) and \
                           agefilter(st, now, age, params['age_stamp']) and \
                           sizefilter(st, size) and contentfilter(fsname, params['contains']):

                            r.update(statinfo(st))
                            if params['get_checksum']:
                                r['checksum'] = module.sha1(fsname)
                            filelist.append(r)

                    elif stat.S_ISLNK(st.st_mode) and params['file_type'] == 'link':
                        if pfilter(fsobj, params['patterns'], params['excludes'], params['use_regex']) and agefilter(st, now, age, params['age_stamp']):

                            r.update(statinfo(st))
                            filelist.append(r)

                if not params['recurse']:
                    break
        else:
            msg += "%s was skipped as it does not seem to be a valid directory or it cannot be accessed\n" % npath

    matched = len(filelist)
    module.exit_json(files=filelist, changed=False, msg=msg, matched=matched, examined=looked)


if __name__ == '__main__':
    main()
