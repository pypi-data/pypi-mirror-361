import subprocess
import os
import sys
import argparse
import json
from typing import Optional

from glrp.internal_parser import parse, parse_to_all_representations
from glrp.version import string as version_string
from glrp.utils import find, mkdir, rm, write_json
from glrp.pretty import pretty as prettify

# Usage:
# git log -p --format=raw --show-signature --stat | python3 git_log_raw_parser.py

all_processes = []


class GlobalState:
    def __init__(self):
        self.quiet = False
        self.emails = {}
        self.names = {}
        self.fingerprints = {}
        self.unsigneds = {}

        self.counts = {
            "empty": [],
            "unsigned": [],
            "signed-trusted": [],
            "signed-untrusted": [],
        }

        self.commits = {}

        self.by_name = {}
        self.by_email = {}
        self.by_fingerprint = {}
        self.by_id = {}
        self.summary = {}
        self.trusted = None

        self.set_trusted_fingerprints()

    def _get_trusted_fingerprints(self):
        if not os.path.isdir("trusted"):
            return
        for file in find("trusted", extension=".fp"):
            with open(file, "r") as f:
                for line in f:
                    line = line.strip()
                    line = line.replace(" ", "")
                    if line:
                        yield line

    def set_trusted_fingerprints(self):
        self.trusted = list(self._get_trusted_fingerprints())

    def record_email(self, email):
        if email not in self.emails:
            self.emails[email] = 1
            # print("New email: " + email)
        else:
            self.emails[email] += 1

    def record_name(self, name):
        if name not in self.names:
            self.names[name] = 1
            # print("New name: " + name)
        else:
            self.names[name] += 1

    def record_fingerprint(self, fingerprint):
        if fingerprint not in self.fingerprints:
            self.fingerprints[fingerprint] = 1
            # print("New fingerprint: " + fingerprint)
        else:
            self.fingerprints[fingerprint] += 1

    def record_unsigned(self, unsigned):
        if unsigned not in self.unsigneds:
            self.unsigneds[unsigned] = 1
            # print("New unsigned: " + unsigned)
        else:
            self.unsigneds[unsigned] += 1

    def record_user(self, user):
        name = user["name"]
        email = user["email"]
        id = user["id"]

        if name not in self.by_name:
            self.by_name[name] = {"emails": [], "fingerprints": []}
        if email not in self.by_email:
            self.by_email[email] = {"names": [], "fingerprints": []}
        if id not in self.by_id:
            self.by_id[id] = {"fingerprints": []}

        if email not in self.by_name[name]["emails"]:
            self.by_name[name]["emails"].append(email)

        if name not in self.by_email[email]["names"]:
            self.by_email[email]["names"].append(name)

    def record_by(self, commit):
        self.record_user(commit["author"])
        self.record_user(commit["committer"])
        id = commit["committer"]["id"]
        fingerprint = commit.get("fingerprint", "unsigned")
        if fingerprint != "unsigned":
            if fingerprint not in self.by_fingerprint:
                self.by_fingerprint[fingerprint] = {"ids": []}
            if id not in self.by_fingerprint[fingerprint]["ids"]:
                self.by_fingerprint[fingerprint]["ids"].append(id)
                if fingerprint not in self.by_id[id]["fingerprints"]:
                    self.by_id[id]["fingerprints"].append(fingerprint)

    def record_commit(self, commit):
        self.commits[commit["commit"]] = commit
        self.record_by(commit)
        self.record_email(commit["author"]["email"])

        if commit["author"]["email"] != commit["committer"]["email"]:
            self.record_email(commit["committer"]["email"])

        self.record_name(commit["author"]["name"])
        if commit["author"]["name"] != commit["committer"]["name"]:
            self.record_name(commit["committer"]["name"])

        if "fingerprint" in commit:
            self.record_fingerprint(
                commit["committer"]["id"] + " " + commit["fingerprint"]
            )
        else:
            self.record_unsigned(commit["committer"]["id"])

        if "diff" not in commit:
            self.counts["empty"].append(commit)
        elif "fingerprint" in commit and commit["fingerprint"] in self.trusted:
            self.counts["signed-trusted"].append(commit)
        elif "fingerprint" in commit and commit["fingerprint"] not in self.trusted:
            self.counts["signed-untrusted"].append(commit)
        else:
            self.counts["unsigned"].append(commit)

    def generate_summary(self):
        self.by_email = {
            k: v
            for k, v in self.by_email.items()
            if len(v["names"]) > 1 or len(v["fingerprints"]) > 1
        }
        self.by_name = {
            k: v
            for k, v in self.by_name.items()
            if len(v["emails"]) > 1 or len(v["fingerprints"]) > 1
        }
        self.by_id = {k: v for k, v in self.by_id.items() if len(v["fingerprints"]) > 1}
        self.by_fingerprint = {
            k: v for k, v in self.by_fingerprint.items() if len(v["ids"]) > 1
        }
        self.summary = {
            "emails": self.emails,
            "names": self.names,
            "fingerprints": self.fingerprints,
            "unsigneds": self.unsigneds,
            "commit_counts": {
                "empty": len(self.counts["empty"]),
                "signed-trusted": len(self.counts["signed-trusted"]),
                "signed-untrusted": len(self.counts["signed-untrusted"]),
                "unsigned": len(self.counts["unsigned"]),
            },
            "by_name": self.by_name,
            "by_email": self.by_email,
            "by_id": self.by_id,
            "by_fingerprint": self.by_fingerprint,
        }


global_state = GlobalState()


def output_to_directory(output_dir):
    assert output_dir is not None and output_dir != ""
    if not output_dir.endswith("/"):
        output_dir = output_dir + "/"
    if (
        not output_dir.startswith("./")
        and not output_dir.startswith("/")
        and not output_dir.startswith("~/")
    ):
        output_dir = "./" + output_dir

    assert output_dir != "/"
    assert output_dir != "./"
    assert output_dir != "~/"
    assert output_dir != "."

    assert os.path.isdir(output_dir) or not os.path.exists(output_dir)

    rm(output_dir, missing_ok=True)

    mkdir(f"{output_dir}", exist_ok=True)

    with open(f"{output_dir}summary.json", "w") as f:
        f.write(prettify(global_state.summary) + "\n")

    index = 0
    for sha, commit in global_state.commits.items():
        write_json(
            f"{output_dir}shas/{sha}.json",
            commit,
        )
        write_json(
            f"{output_dir}index/{str(index).rjust(6, '0')}.json",
            commit,
        )
        index += 1


def dump_commit(raw_commit, split_commit, pretty_commit):
    sha = pretty_commit["commit"]
    with open(f"./debug/{sha}.1.raw.txt", "w") as f:
        f.write("\n".join(raw_commit))
    with open(f"./debug/{sha}.2.raw.json", "w") as f:
        f.write(prettify(raw_commit))
    with open(f"./debug/{sha}.3.split.json", "w") as f:
        f.write(prettify(split_commit))
    with open(f"./debug/{sha}.4.pretty.json", "w") as f:
        f.write(prettify(pretty_commit))


def _validate(
    input: Optional[str] = None,
    output: Optional[str] = None,
    output_dir: Optional[str] = None,
    quiet: bool = False,
    debug: bool = False,
    summary: Optional[str] = None,
    pretty: bool = False,
):
    assert (
        input == None or input == "-" or os.path.isfile(input) or os.path.isdir(input)
    )
    if output is not None:
        assert isinstance(output, str) and len(output) > 0
        assert os.path.isfile(output) or not os.path.exists(output)
    if output_dir is not None:
        assert isinstance(output_dir, str) and len(output_dir) > 0
        assert os.path.isdir(output_dir) or not os.path.exists(output_dir)
    assert quiet == True or quiet == False
    assert debug == True or debug == False
    if summary is not None:
        assert isinstance(summary, str) and len(summary) > 0
        assert os.path.isfile(summary) or not os.path.exists(summary)
    assert pretty == True or pretty == False
    return


def _parse_logs(
    input,
    output_dir: Optional[str],
    quiet: bool,
    debug: bool,
    summary: Optional[str],
    pretty: bool,
):
    if debug:
        rm("./debug/", missing_ok=True)
        mkdir("./debug/", exist_ok=False)
        for raw_commit, split_commit, pretty_commit in parse_to_all_representations(
            input
        ):
            dump_commit(raw_commit, split_commit, pretty_commit)
            if not quiet:
                if pretty:
                    print(prettify(pretty_commit))
                else:
                    print(json.dumps(pretty_commit))
        return

    for commit in parse(input):
        if not summary and not quiet:
            if pretty:
                print(prettify(commit))
            else:
                print(json.dumps(commit))
        if summary or output_dir:
            global_state.record_commit(commit)

    if not summary and not output_dir:
        return

    global_state.generate_summary()

    if summary:
        print(prettify(global_state.summary))
    if output_dir:
        output_to_directory(output_dir)
    pass


class UserError(Exception):
    pass


def parse_logs(
    input: Optional[str] = None,
    output_dir: Optional[str] = None,
    quiet: bool = False,
    debug: bool = False,
    summary: Optional[str] = None,
    pretty: bool = False,
):
    _validate(
        input=input,
        output_dir=output_dir,
        quiet=quiet,
        debug=debug,
        summary=summary,
        pretty=pretty,
    )

    if input in (None, "-"):
        input_file = sys.stdin
    else:
        if os.path.isdir(input):
            process = subprocess.Popen(
                ["git", "log", "-p", "--format=raw", "--show-signature", "--stat"],
                cwd=input,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            all_processes.append(process)
            input_file = process.stdout
        else:
            try:
                input_file = open(input, "r")
            except:
                raise UserError(f"Could not open '{input}'.")

    _parse_logs(
        input=input_file,
        output_dir=output_dir,
        quiet=quiet,
        debug=debug,
        summary=summary,
        pretty=pretty,
    )
    for process in all_processes:
        process.wait()


def get_args():
    parser = argparse.ArgumentParser(
        prog="glrp",
        description="Parses the output of 'git log -p --format=raw --show-signature --stat'",
    )
    parser.add_argument(
        "input",
        type=str,
        nargs="?",
        help="File to read input from or folder to run 'git' in",
    )
    parser.add_argument("--version", action="version", version=version_string())
    parser.add_argument(
        "-o", "--output-dir", help="Output commits to a folder structure"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        help="Stop printing JSON commits to standard out",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="Enable debug information",
    )
    parser.add_argument(
        "--summary",
        type=str,
        help="Filename for JSON summary",
    )
    parser.add_argument(
        "--pretty",
        default=False,
        action="store_true",
        help="Print commit JSONs on multiple lines, with indentation",
    )
    args = parser.parse_args()
    return args


def main():
    args = get_args()
    parse_logs(
        input=args.input,
        output_dir=args.output_dir,
        quiet=args.quiet,
        debug=args.debug,
        summary=args.summary,
        pretty=args.pretty,
    )


if __name__ == "__main__":
    main()
