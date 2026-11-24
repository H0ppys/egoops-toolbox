#!/usr/bin/env python
"""Minimal non-interactive SSH command runner (password auth).

Usage:
  python ssh_exec.py "<command>"              # run command
  python ssh_exec.py -f script.sh             # run script file via bash -s
  python ssh_exec.py -u <file> -d <remote>    # upload file
Environment overrides: DEPLOY_HOST, DEPLOY_PORT, DEPLOY_USER, DEPLOY_PASS
"""
import os
import sys
import paramiko

HOST = os.environ.get("DEPLOY_HOST", "<FILL_ME>")
PORT = int(os.environ.get("DEPLOY_PORT", "22"))
USER = os.environ.get("DEPLOY_USER", "root")
PASS = os.environ.get("DEPLOY_PASS", "<FILL_ME>")
KEY = os.environ.get("DEPLOY_KEY", os.path.join(os.path.expanduser("~"), ".ssh", "egoops_ed25519"))


def connect():
    c = paramiko.SSHClient()
    c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    c.connect(
        HOST,
        port=PORT,
        username=USER,
        password=PASS,
        key_filename=KEY if os.path.exists(KEY) else None,
        timeout=25,
        banner_timeout=25,
        auth_timeout=25,
        look_for_keys=False,
        allow_agent=False,
    )
    return c


def run(cmd):
    c = connect()
    try:
        si, so, se = c.exec_command(cmd, timeout=1800, get_pty=False)
        out = so.read().decode("utf-8", "replace")
        err = se.read().decode("utf-8", "replace")
        rc = so.channel.recv_exit_status()
    finally:
        c.close()
    sys.stdout.write(out)
    if err.strip():
        sys.stdout.write("\n[stderr]\n" + err)
    sys.exit(rc)


def upload(local, remote):
    c = connect()
    try:
        sftp = c.open_sftp()
        sftp.put(local, remote)
        sftp.close()
        print(f"uploaded {local} -> {remote}")
    finally:
        c.close()


def main():
    a = sys.argv[1:]
    if not a:
        sys.exit("no command")
    if a[0] == "-f":
        with open(a[1], "rb") as f:
            script = f.read().decode("utf-8")
        run("bash -s <<'DSH_EOF'\n" + script + "\nDSH_EOF")
    elif a[0] == "-u":
        upload(a[1], a[2])
    else:
        run(" ".join(a))


if __name__ == "__main__":
    main()
