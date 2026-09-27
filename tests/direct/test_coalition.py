"""Direct-mode tests for COALITION.

These tests target the primitive boundary: semantic consensus establishes
provider-to-requirement capability edges; deterministic code alone selects
the cheapest complete coalition.
"""

import json
from pathlib import Path
from datetime import datetime, timezone

CONTRACT = "contracts/coalition.py"
CLASSIFIER = r"COALITION / CAPABILITY QUALIFICATION"
EVIDENCE_JUDGE = r"COALITION / EVIDENCE SUPPORT CHECK"

BASE = "2026-09-27T10:00:00+00:00"
BEFORE_DEADLINE = "2026-09-27T10:05:00+00:00"
AFTER_DEADLINE = "2026-09-27T10:11:00+00:00"
DEADLINE_TS = int(datetime(2026, 9, 27, 10, 10, tzinfo=timezone.utc).timestamp())


def addr(name):
    from gltest.direct import create_address
    return create_address(name)


def result(verdict="QUALIFIED", evidence="", reason="public evidence supports the frozen capability", source_index=0):
    return json.dumps({
        "verdict": verdict,
        "reason": reason,
        "source_index": source_index if verdict == "QUALIFIED" else -1,
        "evidence": evidence if verdict == "QUALIFIED" else "",
    })


def mock_qualified(vm, slug, evidence):
    vm.clear_mocks()
    vm.mock_web(rf".*{slug}\.example\.com/evidence.*", {"status": 200, "body": evidence})
    vm.mock_llm(CLASSIFIER, result("QUALIFIED", evidence))
    vm.mock_llm(EVIDENCE_JUDGE, "PASS")


def mock_not_qualified(vm, slug):
    vm.clear_mocks()
    vm.mock_web(rf".*{slug}\.example\.com/evidence.*", {"status": 200, "body": "Public page with unrelated work."})
    vm.mock_llm(CLASSIFIER, result("NOT_QUALIFIED", "", "source does not establish the capability", -1))


def profile(vm, contract, owner, slug):
    with vm.prank(owner):
        pid = contract.create_provider(slug, f"{slug} is a specialist provider with public evidence of completed technical work.")
        contract.add_provider_evidence(pid, "portfolio", f"https://{slug}.example.com/evidence")
        contract.seal_provider(pid)
    return pid


def task(vm, contract, creator, reqs, budget=100, max_team=3):
    with vm.prank(creator):
        tid = contract.create_task(
            "Coalition task",
            "Form the cheapest qualified team that jointly covers every frozen capability requirement.",
            budget,
            max_team,
            DEADLINE_TS,
        )
        ids = []
        for label, description, coverage in reqs:
            ids.append(contract.add_requirement(tid, label, description, coverage))
        contract.seal_task(tid)
    return tid, ids


def bid(vm, contract, owner, tid, pid, price):
    with vm.prank(owner):
        return contract.submit_bid(tid, pid, price)


def close(vm, contract, tid):
    vm.warp(AFTER_DEADLINE)
    contract.close_bidding(tid)


def qualify(vm, contract, tid, bid_id, req_id, slug, evidence):
    mock_qualified(vm, slug, evidence)
    qid = contract.resolve_qualification(tid, bid_id, req_id)
    assert contract.get_qualification(qid)["verdict_name"] == "QUALIFIED"
    assert vm.run_validator() is True
    return qid


def reject(vm, contract, tid, bid_id, req_id, slug):
    mock_not_qualified(vm, slug)
    qid = contract.resolve_qualification(tid, bid_id, req_id)
    assert contract.get_qualification(qid)["verdict_name"] == "NOT_QUALIFIED"
    assert vm.run_validator() is True
    return qid


def test_provider_profile_is_hash_pinned_and_frozen(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    alice = addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    data = contract.get_provider(pid)
    assert len(data["profile_hash"]) == 64
    with direct_vm.prank(alice):
        with direct_vm.expect_revert("not editable"):
            contract.add_provider_evidence(pid, "late", "https://late.example.com/evidence")


def test_private_and_non_https_evidence_urls_are_rejected(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    alice = addr("alice")
    with direct_vm.prank(alice):
        pid = contract.create_provider("Alice", "Alice is a specialist provider with public technical evidence.")
        for bad in (
            "http://example.com/evidence",
            "https://localhost/evidence",
            "https://127.0.0.1/evidence",
            "https://10.0.0.1/evidence",
            "https://169.254.169.254/latest/meta-data",
            "https://service.internal/evidence",
            "https://user:pass@example.com/evidence",
            "https://example.com:8443/evidence",
        ):
            with direct_vm.expect_revert("EXPECTED"):
                contract.add_provider_evidence(pid, "evidence", bad)


def test_task_is_hash_pinned_and_cannot_change_after_seal(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator = addr("creator")
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    assert len(contract.get_task(tid)["definition_hash"]) == 64
    with direct_vm.prank(creator):
        with direct_vm.expect_revert("frozen"):
            contract.add_requirement(tid, "PYTHON", "Provider demonstrates completed Python systems work.", 1)


def test_bidding_cannot_close_early(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator = addr("creator")
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    direct_vm.warp(BEFORE_DEADLINE)
    with direct_vm.expect_revert("has not passed"):
        contract.close_bidding(tid)


def test_profile_owner_only_and_one_bid_per_address(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob = addr("creator"), addr("alice"), addr("bob")
    p1 = profile(direct_vm, contract, alice, "alice")
    p2 = profile(direct_vm, contract, alice, "alice2")
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    with direct_vm.prank(bob):
        with direct_vm.expect_revert("only provider owner"):
            contract.submit_bid(tid, p1, 20)
    bid(direct_vm, contract, alice, tid, p1, 20)
    with direct_vm.prank(alice):
        with direct_vm.expect_revert("one bid"):
            contract.submit_bid(tid, p2, 19)


def test_withdrawn_bid_is_not_in_selection_matrix(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    bid_id = bid(direct_vm, contract, alice, tid, pid, 20)
    with direct_vm.prank(alice):
        contract.withdraw_bid(bid_id)
    close(direct_vm, contract, tid)
    contract.solve_task(tid)
    assert contract.get_solution(tid)["status_name"] == "UNSATISFIABLE"


def test_withdrawn_bid_releases_admission_slot(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator = addr("creator")
    providers = []
    for index in range(12):
        owner = addr(f"slot-owner-{index}")
        providers.append((owner, profile(direct_vm, contract, owner, f"slot-{index}")))
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    bids = [bid(direct_vm, contract, owner, tid, pid, index + 1)
            for index, (owner, pid) in enumerate(providers[:10])]
    with direct_vm.prank(providers[0][0]):
        contract.withdraw_bid(bids[0])
    replacement = bid(direct_vm, contract, providers[10][0], tid, providers[10][1], 11)
    assert replacement > bids[-1]
    with direct_vm.prank(providers[11][0]):
        with direct_vm.expect_revert("bid limit"):
            contract.submit_bid(tid, providers[11][1], 12)


def test_bid_history_churn_is_bounded(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator = addr("creator")
    providers = []
    for index in range(21):
        owner = addr(f"churn-owner-{index}")
        providers.append((owner, profile(direct_vm, contract, owner, f"churn-{index}")))
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    for index in range(20):
        owner, pid = providers[index]
        bid_id = bid(direct_vm, contract, owner, tid, pid, index + 1)
        with direct_vm.prank(owner):
            contract.withdraw_bid(bid_id)
    owner, pid = providers[20]
    with direct_vm.prank(owner):
        with direct_vm.expect_revert("bid history limit"):
            contract.submit_bid(tid, pid, 21)
    assert len(contract.get_task(tid)["bid_ids"]) == 20


def test_unavailable_qualification_can_be_retried(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, reqs = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    bid_id = bid(direct_vm, contract, alice, tid, pid, 20)
    close(direct_vm, contract, tid)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*alice\.example\.com/evidence.*", {"status": 200, "body": ""})
    qid = contract.resolve_qualification(tid, bid_id, reqs[0])
    assert contract.get_qualification(qid)["verdict_name"] == "UNAVAILABLE"
    first_hash = contract.get_qualification(qid)["receipt_hash"]
    assert len(first_hash) == 64
    assert contract.is_qualification(qid, first_hash) is True
    assert contract.is_qualification(qid, "00" * 32) is False

    evidence = "Public portfolio demonstrates production Solidity security reviews."
    qid_retry = qualify(direct_vm, contract, tid, bid_id, reqs[0], "alice", evidence)
    assert qid_retry == qid
    assert contract.get_qualification(qid)["verdict_name"] == "QUALIFIED"
    assert contract.get_qualification(qid)["receipt_hash"] != first_hash


def frozen_task(vm, contract, creator, profile_ids, coverage=1):
    with vm.prank(creator):
        tid = contract.create_task(
            "Frozen coalition task",
            "Use an explicitly frozen provider universe for a bounded coalition decision.",
            100,
            3,
            DEADLINE_TS,
        )
        contract.add_requirement(
            tid,
            "CAPABILITY",
            "Provider demonstrates the required capability using sealed public evidence.",
            coverage,
        )
        contract.set_admission_mode(tid, 1)
        for profile_id in profile_ids:
            contract.admit_profile(tid, profile_id)
        contract.seal_task(tid)
    return tid


def test_frozen_admission_requires_creator_sealed_unique_bounded_profiles(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob, outsider = [addr(name) for name in ("creator", "alice", "bob", "outsider")]
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    outsider_profile = profile(direct_vm, contract, outsider, "outsider")
    with direct_vm.prank(creator):
        tid = contract.create_task("Frozen", "A frozen provider set must be configured before bidding.", 100, 2, DEADLINE_TS)
        contract.add_requirement(tid, "CAPABILITY", "Provider demonstrates the required capability using sealed public evidence.", 1)
        with direct_vm.prank(alice):
            with direct_vm.expect_revert("only task creator"):
                contract.set_admission_mode(tid, 1)
        with direct_vm.prank(creator):
            contract.set_admission_mode(tid, 1)
        with direct_vm.prank(alice):
            with direct_vm.expect_revert("only task creator"):
                contract.admit_profile(tid, pa)
        with direct_vm.prank(creator):
            contract.admit_profile(tid, pa)
        contract.admit_profile(tid, pb)
        with direct_vm.expect_revert("profile already admitted"):
            contract.admit_profile(tid, pa)
        with direct_vm.expect_revert("clear frozen profiles"):
            contract.set_admission_mode(tid, 0)
        contract.seal_task(tid)
    data = contract.get_task(tid)
    assert data["admission_mode"] == 1
    assert data["admitted_profile_ids"] == [pa, pb]
    with direct_vm.prank(outsider):
        with direct_vm.expect_revert("not admitted"):
            contract.submit_bid(tid, outsider_profile, 10)
    with direct_vm.prank(alice):
        contract.submit_bid(tid, pa, 10)
    with direct_vm.prank(creator):
        with direct_vm.expect_revert("admission policy is frozen"):
            contract.set_admission_mode(tid, 0)


def test_frozen_admission_rejects_empty_or_insufficient_set(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob = addr("creator"), addr("alice"), addr("bob")
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    with direct_vm.prank(creator):
        empty = contract.create_task("Empty", "Frozen admission must contain a valid sealed profile.", 100, 2, DEADLINE_TS)
        contract.add_requirement(empty, "CAPABILITY", "Two independent providers must satisfy this capability requirement.", 2)
        contract.set_admission_mode(empty, 1)
        with direct_vm.expect_revert("admitted profile"):
            contract.seal_task(empty)
        limited = contract.create_task("Limited", "Admission must be sufficient for the frozen coverage requirement.", 100, 2, DEADLINE_TS)
        contract.add_requirement(limited, "CAPABILITY", "Two independent providers must satisfy this capability requirement.", 2)
        contract.set_admission_mode(limited, 1)
        contract.admit_profile(limited, pa)
        with direct_vm.expect_revert("cannot satisfy"):
            contract.seal_task(limited)
        contract.admit_profile(limited, pb)
        contract.seal_task(limited)


def test_frozen_admission_definition_hash_binds_candidate_set(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob = addr("creator"), addr("alice"), addr("bob")
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    first = frozen_task(direct_vm, contract, creator, [pa])
    second = frozen_task(direct_vm, contract, creator, [pa, pb])
    assert contract.get_task(first)["definition_hash"] != contract.get_task(second)["definition_hash"]


def test_open_admission_remains_backward_compatible(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, _ = task(direct_vm, contract, creator, [("CAPABILITY", "Provider demonstrates the required capability using sealed public evidence.", 1)])
    assert contract.get_task(tid)["admission_mode"] == 0
    assert bid(direct_vm, contract, alice, tid, pid, 10) != 0


def test_unsealed_profile_cannot_be_admitted(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    with direct_vm.prank(alice):
        pid = contract.create_provider("draft", "A draft profile with evidence pending sealing and admission.")
        contract.add_provider_evidence(pid, "portfolio", "https://draft.example.com/evidence")
    with direct_vm.prank(creator):
        tid = contract.create_task("Frozen", "Only sealed profiles may enter the frozen candidate universe.", 100, 1, DEADLINE_TS)
        contract.set_admission_mode(tid, 1)
        with direct_vm.expect_revert("must be sealed"):
            contract.admit_profile(tid, pid)


def test_duplicate_owner_cannot_fill_two_frozen_entries(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    first = profile(direct_vm, contract, alice, "alice-one")
    second = profile(direct_vm, contract, alice, "alice-two")
    with direct_vm.prank(creator):
        tid = contract.create_task("Frozen", "A provider owner may occupy only one frozen admission entry.", 100, 1, DEADLINE_TS)
        contract.set_admission_mode(tid, 1)
        contract.admit_profile(tid, first)
        with direct_vm.expect_revert("one admitted profile"):
            contract.admit_profile(tid, second)


def test_frozen_admission_has_ten_profile_bound(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator = addr("creator")
    profiles = []
    for index in range(11):
        owner = addr(f"provider-{index}")
        profiles.append(profile(direct_vm, contract, owner, f"provider-{index}"))
    with direct_vm.prank(creator):
        tid = contract.create_task("Frozen", "The frozen candidate universe is bounded to the solver bid limit.", 100, 1, DEADLINE_TS)
        contract.set_admission_mode(tid, 1)
        for profile_id in profiles[:10]:
            contract.admit_profile(tid, profile_id)
        with direct_vm.expect_revert("limit reached"):
            contract.admit_profile(tid, profiles[10])


def test_terminal_qualification_receipt_cannot_be_rewritten(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, reqs = task(direct_vm, contract, creator, [("CAPABILITY", "Provider demonstrates the required capability using sealed public evidence.", 1)])
    bid_id = bid(direct_vm, contract, alice, tid, pid, 10)
    close(direct_vm, contract, tid)
    qid = reject(direct_vm, contract, tid, bid_id, reqs[0], "alice")
    before = contract.get_qualification(qid)["receipt_hash"]
    with direct_vm.expect_revert("already resolved"):
        contract.resolve_qualification(tid, bid_id, reqs[0])
    assert contract.get_qualification(qid)["receipt_hash"] == before


def test_solution_bundle_commits_full_matrix_provenance(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob = addr("creator"), addr("alice"), addr("bob")
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    tid, reqs = task(direct_vm, contract, creator, [("CAPABILITY", "Provider demonstrates the required capability using sealed public evidence.", 1)])
    ba = bid(direct_vm, contract, alice, tid, pa, 10)
    bb = bid(direct_vm, contract, bob, tid, pb, 20)
    close(direct_vm, contract, tid)
    qualify(direct_vm, contract, tid, ba, reqs[0], "alice", "Public portfolio demonstrates the required capability.")
    qualify(direct_vm, contract, tid, bb, reqs[0], "bob", "Public portfolio demonstrates the required capability.")
    contract.solve_task(tid)
    solution = contract.get_solution(tid)
    assert len(solution["matrix_hash"]) == 64
    assert contract.is_solution_bundle(tid, solution["definition_hash"], solution["matrix_hash"], solution["solution_hash"]) is True
    assert contract.is_solution_bundle(tid, "00" * 32, solution["matrix_hash"], solution["solution_hash"]) is False
    assert contract.is_solution_bundle(tid, solution["definition_hash"], "00" * 32, solution["solution_hash"]) is False
    assert contract.is_solution_bundle(tid, solution["definition_hash"], solution["matrix_hash"], "00" * 32) is False


def test_losing_qualification_receipt_changes_matrix_and_solution_hash(direct_vm, direct_deploy, tmp_path):
    """The final receipt commits the complete matrix, including losing bids."""
    direct_vm.warp(BASE)

    second_contract_path = tmp_path / "coalition_second_deployment.py"
    second_contract_path.write_bytes(Path(CONTRACT).read_bytes())

    def run_scenario(loser_verdict, contract_path):
        contract = direct_deploy(contract_path)
        creator, winner_owner, loser_owner = addr("creator"), addr("winner"), addr("loser")
        winner_profile = profile(direct_vm, contract, winner_owner, "winner")
        loser_profile = profile(direct_vm, contract, loser_owner, "loser")
        task_id, requirement_ids = task(direct_vm, contract, creator, [
            ("CAPABILITY", "Provider demonstrates the required capability using sealed public evidence.", 1),
        ], budget=100, max_team=1)
        winner_bid = bid(direct_vm, contract, winner_owner, task_id, winner_profile, 10)
        loser_bid = bid(direct_vm, contract, loser_owner, task_id, loser_profile, 20)
        close(direct_vm, contract, task_id)

        qualify(direct_vm, contract, task_id, winner_bid, requirement_ids[0], "winner", "Public portfolio demonstrates the required capability.")
        if loser_verdict == "NOT_QUALIFIED":
            reject(direct_vm, contract, task_id, loser_bid, requirement_ids[0], "loser")
        else:
            direct_vm.clear_mocks()
            direct_vm.mock_web(r".*loser\.example\.com/evidence.*", {"status": 200, "body": "Public page is inconclusive."})
            direct_vm.mock_llm(CLASSIFIER, result("AMBIGUOUS", "", "public evidence is inconclusive", -1))
            qid = contract.resolve_qualification(task_id, loser_bid, requirement_ids[0])
            assert contract.get_qualification(qid)["verdict_name"] == "AMBIGUOUS"
            assert direct_vm.run_validator() is True

        contract.solve_task(task_id)
        return contract, task_id, contract.get_solution(task_id), contract.get_qualification(
            contract.get_bid(loser_bid)["qualification_ids"][0]
        )

    snapshot = direct_vm.snapshot()
    contract_a, task_a, solution_a, losing_receipt_a = run_scenario("NOT_QUALIFIED", CONTRACT)
    bundle_a = contract_a.is_solution_bundle(task_a, solution_a["definition_hash"], solution_a["matrix_hash"], solution_a["solution_hash"])
    direct_vm.revert(snapshot)
    # gltest 0.29 keeps a one-contract-per-module registry. Clear that
    # harness-only registry so this regression can exercise two fresh
    # deployments without changing production code or protocol state.
    import genlayer.gl.genvm_contracts as genvm_contracts
    genvm_contracts.__known_contract__ = None
    contract_b, task_b, solution_b, losing_receipt_b = run_scenario("AMBIGUOUS", str(second_contract_path))

    assert solution_a["definition_hash"] == solution_b["definition_hash"]
    assert solution_a["selected"] == solution_b["selected"]
    assert solution_a["total_cost"] == solution_b["total_cost"]
    assert losing_receipt_a["receipt_hash"] != losing_receipt_b["receipt_hash"]
    assert solution_a["matrix_hash"] != solution_b["matrix_hash"]
    assert solution_a["solution_hash"] != solution_b["solution_hash"]
    assert bundle_a is True
    assert contract_b.is_solution_bundle(task_b, solution_b["definition_hash"], solution_b["matrix_hash"], solution_b["solution_hash"]) is True


def test_positive_qualification_is_source_anchored_and_rechecked(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, reqs = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    bid_id = bid(direct_vm, contract, alice, tid, pid, 20)
    close(direct_vm, contract, tid)
    evidence = "Public portfolio demonstrates production Solidity security reviews."
    qid = qualify(direct_vm, contract, tid, bid_id, reqs[0], "alice", evidence)
    receipt = contract.get_qualification(qid)
    assert receipt["evidence"] == evidence
    assert receipt["source_url"] == "https://alice.example.com/evidence"


def test_validator_rejects_forged_qualified_leader(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, reqs = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    bid_id = bid(direct_vm, contract, alice, tid, pid, 20)
    close(direct_vm, contract, tid)
    evidence = "Public portfolio demonstrates production Solidity security reviews."
    qualify(direct_vm, contract, tid, bid_id, reqs[0], "alice", evidence)
    direct_vm.clear_mocks()
    direct_vm.mock_web(r".*alice\.example\.com/evidence.*", {"status": 200, "body": "Unrelated profile."})
    direct_vm.mock_llm(CLASSIFIER, result("NOT_QUALIFIED", "", "not established", -1))
    assert direct_vm.run_validator() is False


def test_solver_refuses_selectively_incomplete_matrix(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice = addr("creator"), addr("alice")
    pid = profile(direct_vm, contract, alice, "alice")
    tid, _ = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1)
    ])
    bid(direct_vm, contract, alice, tid, pid, 20)
    close(direct_vm, contract, tid)
    with direct_vm.expect_revert("qualification matrix incomplete"):
        contract.solve_task(tid)


def test_cheapest_complete_coalition_wins(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator = addr("creator")
    alice, bob, carol = addr("alice"), addr("bob"), addr("carol")
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    pc = profile(direct_vm, contract, carol, "carol")
    tid, reqs = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1),
        ("ECONOMICS", "Provider demonstrates completed mechanism-design or economic modelling work.", 1),
    ], budget=100, max_team=2)
    ba = bid(direct_vm, contract, alice, tid, pa, 20)
    bb = bid(direct_vm, contract, bob, tid, pb, 25)
    bc = bid(direct_vm, contract, carol, tid, pc, 10)
    close(direct_vm, contract, tid)
    sol = "Public portfolio demonstrates production Solidity security reviews."
    econ = "Public portfolio demonstrates mechanism-design and economic modelling work."
    qualify(direct_vm, contract, tid, ba, reqs[0], "alice", sol)
    reject(direct_vm, contract, tid, ba, reqs[1], "alice")
    reject(direct_vm, contract, tid, bb, reqs[0], "bob")
    qualify(direct_vm, contract, tid, bb, reqs[1], "bob", econ)
    qualify(direct_vm, contract, tid, bc, reqs[0], "carol", sol)
    reject(direct_vm, contract, tid, bc, reqs[1], "carol")
    contract.solve_task(tid)
    solution = contract.get_solution(tid)
    assert solution["status_name"] == "SOLVED"
    assert solution["total_cost"] == 35
    assert [item["bid_id"] for item in solution["selected"]] == [bb, bc]
    assert len(solution["solution_hash"]) == 64
    assert contract.is_solution(tid, solution["definition_hash"], solution["solution_hash"]) is True
    assert contract.is_solution(tid, "00" * 32, solution["solution_hash"]) is False


def test_redundancy_requires_distinct_qualified_bids(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob = addr("creator"), addr("alice"), addr("bob")
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    tid, reqs = task(direct_vm, contract, creator, [
        ("SECURITY", "Provider demonstrates completed independent security review work.", 2)
    ], budget=100, max_team=2)
    ba = bid(direct_vm, contract, alice, tid, pa, 20)
    bb = bid(direct_vm, contract, bob, tid, pb, 25)
    close(direct_vm, contract, tid)
    evidence = "Public portfolio demonstrates completed independent security review work."
    qualify(direct_vm, contract, tid, ba, reqs[0], "alice", evidence)
    qualify(direct_vm, contract, tid, bb, reqs[0], "bob", evidence)
    contract.solve_task(tid)
    solution = contract.get_solution(tid)
    assert solution["total_cost"] == 45
    assert len(solution["selected"]) == 2


def test_unsatisfiable_when_complete_team_exceeds_budget(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    creator, alice, bob = addr("creator"), addr("alice"), addr("bob")
    pa = profile(direct_vm, contract, alice, "alice")
    pb = profile(direct_vm, contract, bob, "bob")
    tid, reqs = task(direct_vm, contract, creator, [
        ("SOLIDITY", "Provider demonstrates completed Solidity smart-contract security work.", 1),
        ("ECONOMICS", "Provider demonstrates completed mechanism-design or economic modelling work.", 1),
    ], budget=30, max_team=2)
    ba = bid(direct_vm, contract, alice, tid, pa, 20)
    bb = bid(direct_vm, contract, bob, tid, pb, 20)
    close(direct_vm, contract, tid)
    qualify(direct_vm, contract, tid, ba, reqs[0], "alice", "Public portfolio demonstrates production Solidity security reviews.")
    reject(direct_vm, contract, tid, ba, reqs[1], "alice")
    reject(direct_vm, contract, tid, bb, reqs[0], "bob")
    qualify(direct_vm, contract, tid, bb, reqs[1], "bob", "Public portfolio demonstrates mechanism-design and economic modelling work.")
    contract.solve_task(tid)
    assert contract.get_solution(tid)["status_name"] == "UNSATISFIABLE"


def test_status_dictionary_is_stable(direct_vm, direct_deploy):
    direct_vm.warp(BASE)
    contract = direct_deploy(CONTRACT)
    d = contract.get_status_dictionary()
    assert d["task"]["SOLVED"] == 3
    assert d["qualification"]["QUALIFIED"] == 1
    assert d["bid"]["SELECTED"] == 3
