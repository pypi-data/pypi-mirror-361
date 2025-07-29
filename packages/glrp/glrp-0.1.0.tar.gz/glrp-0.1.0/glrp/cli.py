import subprocess
import os
import sys
import argparse
import json
from typing import Optional

from glrp.internal_parser import parse, parse_to_all_representations
from glrp.version import string as version_string
from glrp.utils import find, mkdir, rm, write_json, read_json
from glrp.pretty import pretty as prettify
from glrp.summary import CommitSummary, Commit
from glrp.compare import compare_summaries

# Usage:
# git log -p --format=raw --show-signature --stat | glrp
#
# glrp .
#
# glrp --compare main~2,main...main~2
#
# glrp --combine .before.json,.after.json

all_processes = []


class GlobalState:
    def __init__(self):
        self.quiet = False

        self.unsigneds = {}

        self.counts = {
            "empty": [],
            "unsigned": [],
            "signed-trusted": [],
            "signed-untrusted": [],
        }

        self.commits = {}
        self.summary = CommitSummary()
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

    def record_commit(self, commit):
        self.commits[commit["commit"]] = commit

        commit_obj = Commit.from_json(commit)
        summary = CommitSummary(commit_obj)
        self.summary = self.summary + summary

        if "diff" not in commit:
            self.counts["empty"].append(commit)
        elif "fingerprint" in commit and commit["fingerprint"] in self.trusted:
            self.counts["signed-trusted"].append(commit)
        elif "fingerprint" in commit and commit["fingerprint"] not in self.trusted:
            self.counts["signed-untrusted"].append(commit)
        else:
            self.counts["unsigned"].append(commit)


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
        f.write(prettify(global_state.summary.to_dict()) + "\n")

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
        input is None or input == "-" or os.path.isfile(input) or os.path.isdir(input)
    )
    if output is not None:
        assert isinstance(output, str) and len(output) > 0
        assert os.path.isfile(output) or not os.path.exists(output)
    if output_dir is not None:
        assert isinstance(output_dir, str) and len(output_dir) > 0
        assert os.path.isdir(output_dir) or not os.path.exists(output_dir)
    assert quiet is True or quiet is False
    assert debug is True or debug is False
    if summary is not None:
        assert isinstance(summary, str) and len(summary) > 0
        assert os.path.isfile(summary) or not os.path.exists(summary)
    assert pretty is True or pretty is False
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

    if summary:
        with open(summary, "w") as f:
            f.write(prettify(global_state.summary.to_dict()))
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
    commit_range: Optional[str] = None,
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
                (
                    ["git", "log", "-p", "--format=raw", "--show-signature", "--stat"]
                    + ([commit_range] if commit_range else [])
                ),
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
        "--compare",
        type=str,
        help="Two comma separated commit hashes / ranges to compare",
    )
    parser.add_argument(
        "--combine",
        type=str,
        help="Comma separated list of summary filenames to combine",
    )
    parser.add_argument(
        "--pretty",
        default=False,
        action="store_true",
        help="Print commit JSONs on multiple lines, with indentation",
    )
    args = parser.parse_args()
    return args


def validate_args(args):
    if args.compare and args.combine:
        raise UserError("The --combine option cannot be used with --compare")
    if args.input and (args.combine or args.compare):
        raise UserError("The input argument cannot be used with --compare or --combine")
    if args.compare and (len(args.compare) < 3 or "," not in args.compare):
        raise UserError(
            "The --compare option requires two comma separated commit hashes / ranges"
        )
    if args.combine and (len(args.combine) < 3 or "," not in args.combine):
        raise UserError(
            "The --combine option requires two or more comma separated JSON filenames"
        )
    return


def get_summary(ref, fname):
    global global_state
    if ref.endswith(".json"):
        r = read_json(ref)
        write_json(r, fname)
        return r
    parse_logs(
        input=".",
        output_dir=None,
        quiet=False,
        debug=False,
        summary=fname,
        pretty=False,
        commit_range=ref,
    )
    global_state = GlobalState()
    return read_json(fname)


def compare_commits(compare):
    a, b = compare.split(",")
    before = get_summary(a, ".before.json")
    assert before is not None
    print(f"Saved .before.json with stats from {before['counts']['commits']} commits")
    after = get_summary(b, ".after.json")
    assert after is not None
    print(f"Saved .after.json with stats from {after['counts']['commits']} commits")
    compare_summaries(before, after)


def combine_summaries(filenames):
    summaries = [CommitSummary(filename=f) for f in filenames.split(",")]
    combined = summaries[0]
    for summary in summaries[1:]:
        combined = combined + summary
    print(prettify(combined.to_dict()))


def main():
    args = get_args()
    validate_args(args)
    if args.compare:
        compare_commits(args.compare)
        return
    if args.combine:
        combine_summaries(args.combine)
        return
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
