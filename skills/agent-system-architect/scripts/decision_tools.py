#!/usr/bin/env python3
"""Offline decision-contract tools. No network, task writes, or action authorization.

Supports this kit's contract schema 1.0 and the documented Jev HTTP JSON shape.
Threshold checks are hypothetical; metadata cannot authenticate calibration.
Run `demo` for a synthetic, fixed-clock replay. No third-party packages required.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
from typing import Any

VERSION = '0.3.0'
ADAPTER = 'jev-http-v1'
MAX_FILE_BYTES = 2_000_000
TOLERANCE = 1e-6


class DecisionError(ValueError):
    """Invalid, stale, disabled, or mismatched input; do not use a prediction."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise DecisionError(message)


def text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def number(value: Any) -> bool:
    return type(value) is int or (type(value) is float and math.isfinite(value))


def probability(value: Any) -> bool:
    return number(value) and 0 <= value <= 1


def strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        require(key not in result, 'Duplicate JSON key rejected.')
        result[key] = value
    return result


def invalid_constant(value: str) -> None:
    raise DecisionError('Non-finite JSON number rejected.')


def read_json(path: Path) -> dict[str, Any]:
    require(path.is_file(), 'Input JSON file not found.')
    require(path.stat().st_size <= MAX_FILE_BYTES, 'Input JSON file exceeds local limit.')
    try:
        data = json.loads(path.read_text(encoding='utf-8'),
                          object_pairs_hook=strict_object, parse_constant=invalid_constant)
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise DecisionError('Invalid JSON input.') from exc
    require(isinstance(data, dict), 'Expected a JSON object.')
    return data


def canonical(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True,
                          separators=(',', ':'), allow_nan=False)
    except (ValueError, TypeError, RecursionError) as exc:
        raise DecisionError('Expected finite JSON-compatible data.') from exc


def timestamp(value: Any) -> datetime:
    require(text(value), 'A timezone-aware timestamp is required.')
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError as exc:
        raise DecisionError('Invalid timestamp.') from exc
    require(parsed.tzinfo is not None and parsed.utcoffset() is not None,
            'Naive timestamps are not accepted.')
    return parsed.astimezone(timezone.utc)


def validate_contract(contract: dict[str, Any]) -> None:
    require(isinstance(contract, dict), 'Contract must be an object.')
    require(contract.get('schema_version') == '1.0', 'Unsupported contract schema.')
    for field in ('contract_id', 'contract_version', 'purpose', 'scope_id'):
        require(text(contract.get(field)), f'Missing contract field: {field}.')
    require(re.fullmatch(r'[a-z][a-z0-9_-]{0,79}', contract['contract_id']) is not None,
            'Invalid contract ID.')
    require(contract.get('mode') in ('off', 'shadow', 'advisory'), 'Invalid contract mode.')
    require(contract.get('authority') == 'advisory_only', 'Contracts cannot grant authority.')
    provider = contract.get('provider', {})
    require(isinstance(provider, dict) and provider.get('name') == 'typesafe-jev',
            'This offline adapter supports typesafe-jev only.')
    require(provider.get('adapter_version') == ADAPTER, 'Unsupported wire adapter.')
    require(text(provider.get('model')), 'An explicit model ID is required.')
    require(provider['model'] not in ('jev-latest', 'jev-preview'),
            'Pin a model ID for reproducible contract checks.')
    inp = contract.get('inputs', {})
    require(isinstance(inp, dict), 'Invalid input specification.')
    allowed, required = inp.get('allowed_fields'), inp.get('required_fields')
    for values in (allowed, required):
        require(isinstance(values, list) and all(text(x) for x in values),
                'Input fields must be lists of nonempty strings.')
        require(len(values) == len(set(values)), 'Duplicate input field.')
    require(bool(allowed) and bool(required) and set(required) <= set(allowed),
            'Required fields must be a nonempty subset of allowed fields.')
    for field in ('max_state_chars', 'max_age_seconds'):
        require(type(inp.get(field)) is int and inp[field] > 0,
                f'Invalid input limit: {field}.')
    require(type(inp.get('external_transmission_enabled')) is bool,
            'Declare external transmission separately from prediction mode.')
    questions = contract.get('questions')
    require(isinstance(questions, dict) and 1 <= len(questions) <= 64,
            'Expected between 1 and 64 questions for this local helper.')
    policy = contract.get('policy', {})
    require(isinstance(policy, dict) and text(policy.get('fallback')),
            'A named existing fallback is required.')
    require(policy.get('evaluation_status') in ('not_run', 'validated'),
            'Invalid evaluation status.')
    if policy['evaluation_status'] == 'validated':
        require(text(policy.get('evaluation_ref')), 'Validated status needs an evidence reference.')
    gates = policy.get('gates', {})
    require(isinstance(gates, dict) and set(gates) == set(questions),
            'Every question requires its own gate specification.')
    for qid, question in questions.items():
        require(isinstance(qid, str) and re.fullmatch(r'[a-z][a-z0-9_]{0,79}', qid) is not None, 'Invalid question ID.')
        require(isinstance(question, dict) and text(question.get('prompt')),
                'Put the actual question in prompt; IDs are not instructions.')
        kind, gate = question.get('kind'), gates[qid]
        require(isinstance(gate, dict), 'Invalid gate.')
        if kind == 'categorical':
            options = question.get('options')
            require(isinstance(options, dict) and 2 <= len(options) <= 255,
                    'Categorical questions need 2–255 described options.')
            require(all(text(k) and text(v) for k, v in options.items()),
                    'Each categorical option needs a name and description.')
            abstain = gate.get('abstain_options')
            require(isinstance(abstain, list) and bool(abstain)
                    and all(text(x) for x in abstain)
                    and set(abstain) <= set(options), 'Include an explicit unknown/no-match path.')
            require(set(gate) == {'min_probability', 'min_margin',
                                 'min_provider_confidence', 'abstain_options'}, 'Invalid categorical gate fields.')
            for key in ('min_probability', 'min_margin', 'min_provider_confidence'):
                require(gate[key] is None or probability(gate[key]), 'Invalid categorical threshold.')
        elif kind == 'binary':
            require(set(gate) == {'yes_at_or_above', 'no_at_or_below'},
                    'Binary/Noul has no provider-confidence gate.')
            yes, no = gate['yes_at_or_above'], gate['no_at_or_below']
            require((yes is None and no is None) or
                    (probability(yes) and probability(no) and no < yes),
                    'Binary gates need ordered no/yes cutoffs or both unset.')
        elif kind == 'ordinal':
            levels = question.get('levels')
            require(isinstance(levels, list) and 2 <= len(levels) <= 10
                    and all(text(x) for x in levels), 'Ordinal questions need 2–10 described levels.')
            require(set(gate) == {'trigger_at_or_above', 'min_provider_confidence'},
                    'Invalid ordinal gate fields.')
            trigger = gate['trigger_at_or_above']
            require(trigger is None or (number(trigger) and 0 <= trigger <= len(levels)-1),
                    'Ordinal threshold is outside the zero-based rubric.')
            conf = gate['min_provider_confidence']
            require(conf is None or probability(conf), 'Invalid ordinal confidence threshold.')
        else:
            raise DecisionError('Unsupported question kind.')
    canonical(contract)  # Reject non-finite values even in unused metadata.


def project_state(contract: dict[str, Any], packet: dict[str, Any], now: datetime) -> dict[str, Any]:
    require(now.tzinfo is not None and now.utcoffset() is not None, 'Trusted current clock must be aware.')
    require(isinstance(packet, dict), 'State packet must be an object.')
    require(packet.get('scope_id') == contract['scope_id'], 'Input scope does not match contract.')
    observed = timestamp(packet.get('observed_at'))
    age = (now - observed).total_seconds()
    require(-5 <= age <= contract['inputs']['max_age_seconds'], 'Input is stale or future-dated.')
    sources = packet.get('sources')
    require(isinstance(sources, list) and bool(sources), 'At least one source/revision is required.')
    ids = []
    for source in sources:
        require(isinstance(source, dict) and text(source.get('id')) and text(source.get('revision')),
                'Source IDs and revisions are required.')
        ids.append(source['id'])
    require(len(ids) == len(set(ids)), 'Duplicate source identity.')
    fields = packet.get('fields')
    require(isinstance(fields, dict), 'Input fields must be an object.')
    for name in contract['inputs']['required_fields']:
        require(name in fields and fields[name] is not None, 'Required input is missing.')
        if isinstance(fields[name], str):
            require(text(fields[name]), 'Required text input is empty.')
    selected = {key: fields[key] for key in contract['inputs']['allowed_fields'] if key in fields}
    require(len(canonical(selected)) <= contract['inputs']['max_state_chars'],
            'Selected state exceeds local budget; narrow it explicitly.')
    return selected


def prepare_request(contract: dict[str, Any], packet: dict[str, Any], now: datetime) -> dict[str, Any]:
    validate_contract(contract)
    require(contract['mode'] != 'off', 'Decision provider is disabled for this contract.')
    selected = project_state(contract, packet, now)
    questions = {}
    for qid, q in contract['questions'].items():
        wire = {'type': {'binary': 'noul', 'categorical': 'choice', 'ordinal': 'score'}[q['kind']],
                'instructions': q['prompt']}
        if q['kind'] == 'categorical':
            wire['criteria'] = q['options']
        if q['kind'] == 'ordinal':
            wire['criteria'] = q['levels']
        questions[qid] = wire
    request = {'state': selected, 'model': contract['provider']['model'], 'questions': questions}
    binding = {'contract': contract, 'scope_id': packet['scope_id'],
               'sources': packet['sources'], 'observed_at': packet['observed_at'], 'request': request}
    fingerprint = hashlib.sha256(canonical(binding).encode('utf-8')).hexdigest()
    return {'kind': 'offline_request_preview', 'network_performed': False,
            'external_transmission_enabled': contract['inputs']['external_transmission_enabled'],
            'request_fingerprint': fingerprint, 'request': request}


def distribution(raw: Any, keys: set[str]) -> dict[str, float]:
    require(isinstance(raw, dict) and set(raw) == keys, 'Probability options do not match the contract.')
    require(all(probability(x) for x in raw.values()), 'Probabilities must be finite numbers in [0, 1].')
    require(abs(sum(raw.values()) - 1.0) <= TOLERANCE, 'Probability distribution must sum to one.')
    return {key: float(value) for key, value in raw.items()}


def normalize_jev(contract: dict[str, Any], response: dict[str, Any]) -> dict[str, Any]:
    """Validate the documented HTTP shape; do not normalize away provider errors."""
    require(isinstance(response, dict), 'Response must be an object.')
    require(response.get('model') == contract['provider']['model'], 'Response model does not match pinned model.')
    answers = response.get('answers')
    require(isinstance(answers, dict) and set(answers) == set(contract['questions']),
            'Response must cover exactly the requested question IDs.')
    normalized = {}
    for qid, q in contract['questions'].items():
        answer = answers[qid]
        require(isinstance(answer, dict), 'Invalid answer object.')
        if q['kind'] == 'binary':
            require(set(answer) == {'type', 'noul'} and answer['type'] == 'noul',
                    'Noul answer has no separate confidence field in this wire version.')
            require(probability(answer['noul']), 'Invalid yes probability.')
            normalized[qid] = {'kind': 'binary', 'p_yes': float(answer['noul'])}
        elif q['kind'] == 'categorical':
            require(set(answer) == {'type', 'choice', 'probabilities', 'confidence'}
                    and answer['type'] == 'choice', 'Invalid Choice shape.')
            probs = distribution(answer['probabilities'], set(q['options']))
            choice = answer['choice']
            require(isinstance(choice, str) and choice in probs, 'Unknown chosen option.')
            require(abs(probs[choice] - max(probs.values())) <= TOLERANCE,
                    'Choice is not a highest-probability option.')
            require(probability(answer['confidence']), 'Invalid provider confidence.')
            normalized[qid] = {'kind': 'categorical', 'value': choice,
                               'probabilities': probs, 'provider_confidence': answer['confidence']}
        else:
            require(set(answer) == {'type', 'score', 'probabilities', 'legend', 'confidence'}
                    and answer['type'] == 'score', 'Invalid Score shape.')
            legend = {str(i): value for i, value in enumerate(q['levels'])}
            require(answer['legend'] == legend, 'Score legend does not match the contract.')
            probs = distribution(answer['probabilities'], set(legend))
            mean = sum(int(key) * val for key, val in probs.items())
            require(number(answer['score']) and 0 <= answer['score'] <= len(q['levels'])-1
                    and abs(answer['score'] - mean) <= TOLERANCE,
                    'Score must match the probability-weighted zero-based level index.')
            require(probability(answer['confidence']), 'Invalid provider confidence.')
            normalized[qid] = {'kind': 'ordinal', 'value': float(answer['score']),
                               'probabilities': probs, 'levels': legend,
                               'provider_confidence': answer['confidence']}
    usage = response.get('usage')
    require(isinstance(usage, dict) and all(type(usage.get(k)) is int and usage[k] >= 0
                for k in ('input_tokens', 'output_tokens')), 'Missing or invalid usage metadata.')
    return normalized


def hypothetical_gate(answer: dict[str, Any], gate: dict[str, Any]) -> dict[str, Any]:
    """Evaluate only candidate thresholds. This function does not authorize or route."""
    kind = answer['kind']
    if kind == 'categorical':
        value = answer['value']
        if value in gate['abstain_options']:
            return {'status': 'abstain', 'reason': 'unknown_or_no_match'}
        p = answer['probabilities'][value]
        other = max(v for k, v in answer['probabilities'].items() if k != value)
        if p - other <= TOLERANCE:
            return {'status': 'abstain', 'reason': 'tie'}
        if gate['min_probability'] is None or gate['min_margin'] is None:
            return {'status': 'not_configured', 'reason': 'unset_thresholds'}
        if p < gate['min_probability'] or p-other < gate['min_margin']:
            return {'status': 'abstain', 'reason': 'probability_or_margin'}
        floor = gate['min_provider_confidence']
        if floor is not None and answer['provider_confidence'] < floor:
            return {'status': 'abstain', 'reason': 'provider_confidence'}
        return {'status': 'passed', 'candidate': value}
    if kind == 'binary':
        yes, no = gate['yes_at_or_above'], gate['no_at_or_below']
        if yes is None:
            return {'status': 'not_configured', 'reason': 'unset_thresholds'}
        if answer['p_yes'] >= yes:
            return {'status': 'passed', 'candidate': True}
        if answer['p_yes'] <= no:
            return {'status': 'passed', 'candidate': False}
        return {'status': 'abstain', 'reason': 'abstention_band'}
    trigger, floor = gate['trigger_at_or_above'], gate['min_provider_confidence']
    if trigger is None or floor is None:
        return {'status': 'not_configured', 'reason': 'unset_thresholds'}
    if answer['provider_confidence'] < floor:
        return {'status': 'abstain', 'reason': 'provider_confidence'}
    return {'status': 'passed', 'candidate': answer['value'] >= trigger}


def assess_receipt(contract: dict[str, Any], packet: dict[str, Any],
                   receipt: dict[str, Any], now: datetime) -> dict[str, Any]:
    preview = prepare_request(contract, packet, now)
    require(isinstance(receipt, dict), 'Receipt must be an object.')
    require(receipt.get('provider') == contract['provider']['name'], 'Receipt provider mismatch.')
    require(receipt.get('request_fingerprint') == preview['request_fingerprint'],
            'Receipt does not match contract, source revision, scope, or selected inputs.')
    received = timestamp(receipt.get('received_at'))
    require(timestamp(packet['observed_at'])-timedelta(seconds=5) <= received <= now+timedelta(seconds=5),
            'Receipt timestamp is inconsistent with the observed state/current clock.')
    require((now-received).total_seconds() <= contract['inputs']['max_age_seconds'], 'Receipt has expired.')
    answers = normalize_jev(contract, receipt.get('response'))
    gates = {qid: hypothetical_gate(answer, contract['policy']['gates'][qid]) for qid, answer in answers.items()}
    if any(g['status'] == 'abstain' for g in gates.values()):
        disposition = 'abstain'
    elif contract['policy']['evaluation_status'] != 'validated' or any(g['status'] != 'passed' for g in gates.values()):
        disposition = 'not_calibrated'
    else:
        disposition = 'eligible_proposal_only'
    return {'schema_version': '1.0', 'contract_id': contract['contract_id'],
            'contract_version': contract['contract_version'], 'model': contract['provider']['model'],
            'request_fingerprint': preview['request_fingerprint'],
            'status': 'shadow_only' if contract['mode'] == 'shadow' else disposition,
            'candidate_disposition': disposition, 'answers': answers, 'hypothetical_gates': gates,
            'fallback': contract['policy']['fallback'], 'applied': False, 'authorized': False,
            'network_performed': False,
            'warning': 'Offline structural check only. No semantic truth, calibration, permission or source authenticity established.'}


def demo() -> dict[str, Any]:
    base = Path(__file__).resolve().parents[1] / 'assets/examples'
    contract = read_json(base/'route-request.contract.json')
    state = read_json(base/'route-request.state.json')
    receipt = read_json(base/'route-request.receipt.fixture.json')
    result = assess_receipt(contract, state, receipt, timestamp('2026-09-19T12:00:00Z'))
    result['fixture_notice'] = 'Synthetic probabilities and fixed replay clock, not a Jev call.'
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    v = sub.add_parser('validate', help='Validate one contract without contacting a provider.')
    v.add_argument('contract', type=Path)
    for name in ('request', 'assess'):
        p = sub.add_parser(name)
        p.add_argument('contract', type=Path)
        p.add_argument('state', type=Path)
        if name == 'assess':
            p.add_argument('receipt', type=Path)
        p.add_argument('--now', help='Fixed ISO clock for offline fixtures only; defaults to current UTC.')
    sub.add_parser('demo', help='Replay a fictional fixture offline with its original clock.')
    args = parser.parse_args(argv)
    try:
        if args.command == 'demo':
            result = demo()
        else:
            contract = read_json(args.contract)
            if args.command == 'validate':
                validate_contract(contract)
                result = {'valid': True, 'contract_id': contract['contract_id'], 'network_performed': False}
            else:
                now = timestamp(args.now) if args.now else datetime.now(timezone.utc)
                packet = read_json(args.state)
                result = (prepare_request(contract, packet, now) if args.command == 'request'
                          else assess_receipt(contract, packet, read_json(args.receipt), now))
        print(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False))
        return 0
    except (DecisionError, OSError, RecursionError) as exc:
        # Deliberately avoid echoing private input values or server response bodies.
        message = str(exc) if isinstance(exc, DecisionError) else 'Unable to read or process input files.'
        print(json.dumps({'error': message, 'applied': False, 'authorized': False,
                          'network_performed': False}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
