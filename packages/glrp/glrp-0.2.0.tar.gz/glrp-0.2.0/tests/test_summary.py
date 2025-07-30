import json
from glrp.summary import CommitSummary, Commit, Person


def test_summary_to_dict_empty():
    summary = CommitSummary()

    expected = {
        "counts": {"commits": 0},
        "emails": {},
        "names": {},
        "fingerprints": {},
        "ids": {},
    }

    assert summary.to_dict() == expected


def test_person():
    person = Person("John Doe <john.doe@example.com>")
    assert person.email == "john.doe@example.com"
    assert person.name == "John Doe"
    assert person.id == "John Doe <john.doe@example.com>"


def test_commit():
    author = Person("John Doe <john.doe@example.com>")
    committer = Person("John Doe <john.doe@example.com>")
    commit = Commit(author, committer, "Initial commit")
    assert commit.author.id == "John Doe <john.doe@example.com>"
    assert commit.committer.id == "John Doe <john.doe@example.com>"
    assert commit.message == "Initial commit"
    assert commit.fingerprint == None

    author = Person("Alice <alice@example.com>")
    committer = Person("Bob <bob@example.com>")
    commit = Commit(
        author, committer, "Second commit", "AFE8C5F43057C0093122299F584211AF6AB3EE12"
    )
    assert commit.author.id == "Alice <alice@example.com>"
    assert commit.author.name == "Alice"
    assert commit.author.email == "alice@example.com"
    assert commit.committer.id == "Bob <bob@example.com>"
    assert commit.committer.name == "Bob"
    assert commit.committer.email == "bob@example.com"
    assert commit.message == "Second commit"
    assert commit.fingerprint == "AFE8C5F43057C0093122299F584211AF6AB3EE12"


def test_commit_summary():
    john = Person("John Doe <john.doe@example.com>")
    commit = Commit(john, john, "Initial commit")
    summary = CommitSummary(commit)
    assert summary.to_dict() == {
        "counts": {"commits": 1},
        "emails": {
            "john.doe@example.com": {
                "commits": 1,
                "names": ["John Doe"],
                "ids": ["John Doe <john.doe@example.com>"],
                "fingerprints": [],
            }
        },
        "names": {
            "John Doe": {
                "commits": 1,
                "emails": ["john.doe@example.com"],
                "ids": ["John Doe <john.doe@example.com>"],
                "fingerprints": [],
            }
        },
        "fingerprints": {},
        "ids": {
            "John Doe <john.doe@example.com>": {
                "commits": 1,
                "names": ["John Doe"],
                "emails": ["john.doe@example.com"],
                "fingerprints": [],
            }
        },
    }


def test_commit_summary_json():
    john = Person("John Doe <john.doe@example.com>")
    commit = Commit(john, john, "Initial commit")
    summary = CommitSummary(commit)
    dump = str(summary)
    data = json.loads(dump)
    assert data == summary.to_dict()
