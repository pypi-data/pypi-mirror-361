import contextlib
import posixpath
import types

import scanner_auto as sa

args = types.SimpleNamespace(
    institute='liverpool',
    operator='avt',
    password='clOUdy3percePtION40',
    sftp='/Users/avt/.ds20kdb_scanner_rc'
)

cred = sa.read_credentials(args.sftp)
args.key, args.user = cred['key'], cred['username']

remote_path = posixpath.join('/scratch4/DarkSide/scanner', args.institute, 'avt', 'sdfasdf')

con = sa.Connect(args)

with contextlib.closing(con.ssh.open_sftp()) as sftp:
    sftp.mkdir(remote_path)
    try:
        sftp.mkdir(remote_path)
    except OSError:
        print('already exists')
    except PermissionError:
        print('cannot create directory')

