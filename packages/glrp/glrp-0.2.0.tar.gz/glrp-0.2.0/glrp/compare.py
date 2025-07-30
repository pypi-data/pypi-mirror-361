def compare_summaries(before, after):
    for fingerprint in after["fingerprints"]:
        if fingerprint not in before["fingerprints"]:
            id = after["fingerprints"][fingerprint]["ids"][0]
            print(f"Note: New fingerprint {fingerprint} ({id})")
    for id in after["ids"]:
        if id not in before["ids"]:
            print(f"Note: New ID {id}")

    # Look through emails, warn about changes in fingerprints:
    for email in (e for e in after["emails"] if e in before["emails"]):
        if "fingerprints" not in after["emails"][email]:
            continue
        for fingerprint in after["emails"][email]["fingerprints"]:
            if (
                "fingerprints" not in before["emails"][email]
                or len(before["emails"][email]["fingerprints"]) == 0
            ):
                print(f"Note: First fingerprint for email {email}")
                continue
            if fingerprint not in before["emails"][email]["fingerprints"]:
                print(f"Warning: Changed fingerprint {fingerprint}")

    # Look through emails, warn about changes in names:
    for email in (e for e in after["emails"] if e in before["emails"]):
        for name in after["emails"][email]["names"]:
            if name not in before["emails"][email]["names"]:
                print(f"Warning: New name for {email} - {name}")

    # Look through fingerprints, warn about changes in names:
    for fingerprint in (
        e for e in after["fingerprints"] if e in before["fingerprints"]
    ):
        for id in after["fingerprints"][fingerprint]["ids"]:
            if id not in before["fingerprints"][fingerprint]["ids"]:
                print(f"Warning: New ID for {fingerprint} - {id}")
