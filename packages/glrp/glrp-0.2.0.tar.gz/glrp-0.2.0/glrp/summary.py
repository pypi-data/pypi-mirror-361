import os
import json
from copy import deepcopy


class Person:
    def __init__(self, id_string: str):
        assert type(id_string) is str
        assert len(id_string) > 0
        assert id_string.count(" <") == 1, "Invalid id_string"
        assert id_string.count(">") == 1, "Invalid id_string"
        self.id = id_string
        self.name, self.email = id_string.split(" <")
        self.email = self.email[:-1]
        assert len(self.name) > 0
        assert len(self.email) > 0


class Commit:
    def __init__(
        self,
        author: Person,
        committer: Person,
        message: str,
        fingerprint: str | None = None,
    ):
        self.author = author
        self.committer = committer
        self.message = message
        self.fingerprint = fingerprint

    @staticmethod
    def from_json(json_obj):
        author = Person(json_obj["author"]["id"])
        committer = Person(json_obj["committer"]["id"])
        message = json_obj["message"]
        fingerprint = json_obj.get("fingerprint", None)
        return Commit(author, committer, message, fingerprint)


def add_entries(a, b):
    # "commits": 1,
    # "names": [commit.committer.name],
    # "ids": [commit.committer.id],
    # "fingerprints": [commit.fingerprint],
    a, b = deepcopy(a), deepcopy(b)
    r = {}
    common = []
    # Add everyting from a
    for k, v in a.items():
        r[k] = v
        if k in b:
            common.append(k)
    # Add unique items from b:
    for k, v in b.items():
        if k not in a:
            r[k] = v
        else:
            assert k in common
    # Combine / add comon items:
    for k in common:
        if k == "commits":
            r[k] = a[k] + b[k]
        else:
            # All others are lists of strings:
            for s in b[k]:
                if s not in r[k]:
                    r[k].append(s)
    return r


class CommitSummary:
    def __init__(self, commit: Commit | None = None, filename: str | None = None):
        assert commit is None or filename is None
        assert commit is None or isinstance(commit, Commit)
        assert filename is None or isinstance(filename, str)
        assert filename is None or os.path.isfile(filename)

        self.counts = {"commits": 0}
        self.emails = {}
        self.names = {}
        self.ids = {}
        self.fingerprints = {}

        if filename:
            assert not commit
            with open(filename, "r") as f:
                data = json.load(f)
            self.counts = data["counts"]
            self.emails = data["emails"]
            self.names = data["names"]
            self.ids = data["ids"]
            self.fingerprints = data["fingerprints"]
            return

        if commit:
            assert not filename
            self.counts["commits"] += 1
            fp = commit.fingerprint
            self.emails[commit.committer.email] = {
                "commits": 1,
                "names": [commit.committer.name],
                "ids": [commit.committer.id],
                "fingerprints": [fp] if fp else [],
            }
            self.names[commit.committer.name] = {
                "commits": 1,
                "emails": [commit.committer.email],
                "ids": [commit.committer.id],
                "fingerprints": [fp] if fp else [],
            }
            self.ids[commit.committer.id] = {
                "commits": 1,
                "names": [commit.committer.name],
                "emails": [commit.committer.email],
                "fingerprints": [fp] if fp else [],
            }
            if fp:
                self.fingerprints[fp] = {
                    "commits": 1,
                    "names": [commit.committer.name],
                    "emails": [commit.committer.email],
                    "ids": [commit.committer.id],
                }
            if commit.committer.id != commit.author.id:
                self.emails[commit.author.email] = {
                    "commits": 1,
                    "names": [commit.author.name],
                    "ids": [commit.author.id],
                }
                self.names[commit.author.name] = {
                    "commits": 1,
                    "emails": [commit.author.email],
                    "ids": [commit.author.id],
                }
                self.ids[commit.author.id] = {
                    "commits": 1,
                    "names": [commit.author.name],
                    "emails": [commit.author.email],
                }

    def add_update(self, other):
        assert isinstance(other, CommitSummary)
        self.counts["commits"] += other.counts["commits"]
        for email, data in other.emails.items():
            if email not in self.emails:
                self.emails[email] = data
            else:
                self.emails[email] = add_entries(self.emails[email], data)
        for name, data in other.names.items():
            if name not in self.names:
                self.names[name] = data
            else:
                self.names[name] = add_entries(self.names[name], data)
        for id, data in other.ids.items():
            if id not in self.ids:
                self.ids[id] = data
            else:
                self.ids[id] = add_entries(self.ids[id], data)
        for fingerprint, data in other.fingerprints.items():
            if fingerprint not in self.fingerprints:
                self.fingerprints[fingerprint] = data
            else:
                self.fingerprints[fingerprint] = add_entries(
                    self.fingerprints[fingerprint], data
                )

        pass

    def __add__(self, other):
        result = CommitSummary()
        result.add_update(self)
        result.add_update(other)
        return result

    def to_dict(self):
        return {
            "counts": self.counts,
            "emails": self.emails,
            "names": self.names,
            "fingerprints": self.fingerprints,
            "ids": self.ids,
        }

    def __str__(self):
        return json.dumps(self.to_dict())
