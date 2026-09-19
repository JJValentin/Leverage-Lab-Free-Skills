"""Package and fictional-fixture checks, not human/model behavior evaluations.

No network, native harness, user study or live permission system is exercised.
Run from the skill directory: python3 -B -m unittest discover -s tests -p test_experience.py -v
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
NEW_DOCS = [
    'SKILL.md', 'README.md', 'CHANGELOG.md', 'VALIDATION.md',
    'references/human-agent-collaboration.md', 'references/response-patterns.md',
    'references/experience-evaluation.md', 'references/UX-SOURCES.md',
    'assets/COLLABORATION.template.md', 'assets/TASK-HANDOFF.template.md',
]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding='utf-8'))


class ExperiencePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = load('assets/experience-contract.template.json')
        cls.suite = load('assets/experience-scenarios.json')
        cls.cases = cls.suite['cases']
        cls.rules = set(re.findall(r'^## (H\d{2})\.',
            (ROOT / 'references/human-agent-collaboration.md').read_text(), re.M))

    def test_skill_version(self):
        self.assertIn('version: "0.4.0"', (ROOT / 'SKILL.md').read_text())
        self.assertEqual(self.contract['instruction_binding']['version'], '0.4.0')

    def test_local_links_resolve(self):
        for relative in NEW_DOCS:
            path = ROOT / relative
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', path.read_text()):
                if urlsplit(link).scheme or link.startswith('#'):
                    continue
                target = (path.parent / unquote(link.split('#')[0])).resolve()
                with self.subTest(file=relative, link=link):
                    self.assertTrue(target.is_relative_to(ROOT.resolve()))
                    self.assertTrue(target.exists())

    def test_all_json_assets_parse(self):
        for path in (ROOT / 'assets').rglob('*.json'):
            with self.subTest(file=path.name):
                self.assertIsInstance(json.loads(path.read_text()), dict)

    def test_fourteen_defined_rules(self):
        self.assertEqual(self.rules, {f'H{i:02d}' for i in range(1, 15)})

    def test_forty_unique_scenarios(self):
        self.assertEqual(len(self.cases), 40)
        self.assertEqual(len({c['id'] for c in self.cases}), 40)
        self.assertEqual(len({c['name'] for c in self.cases}), 40)

    def test_scenarios_have_observable_requirements(self):
        for case in self.cases:
            for field in ('prompt', 'fixture_context', 'expected', 'forbidden', 'verification'):
                with self.subTest(case=case['id'], field=field):
                    self.assertIsInstance(case[field], str)
                    self.assertTrue(case[field].strip())

    def test_no_behavior_pass_is_claimed(self):
        self.assertTrue(all(c['status'] == 'not_run' for c in self.cases))
        self.assertIn('not a scenario pass', self.suite['fixture_notice'])

    def test_rule_coverage(self):
        referenced = {r for c in self.cases for r in c['rules']}
        self.assertEqual(referenced, self.rules)

    def test_both_routine_and_critical_cases(self):
        self.assertEqual({c['severity'] for c in self.cases}, {'normal', 'critical'})
        self.assertGreaterEqual(sum(c['severity'] == 'normal' for c in self.cases), 15)
        self.assertGreaterEqual(sum(c['severity'] == 'critical' for c in self.cases), 10)

    def test_contrasting_cases_are_present(self):
        names = {c['name'] for c in self.cases}
        pairs = [('authorized-edit', 'approval-boundary'), ('known-context', 'ambiguous-recipient'),
                 ('long-progress', 'quiet-small-work'), ('partial-result', 'verified-completion'),
                 ('support-not-project', 'do-not-underperform'),
                 ('scheduler-supported', 'scheduler-unavailable'),
                 ('integrated-workers', 'visible-specialists')]
        for left, right in pairs:
            self.assertTrue({left, right} <= names)

    def test_template_is_not_deployed(self):
        self.assertTrue(self.contract['template_only'])
        self.assertFalse(self.contract['applied'])
        self.assertEqual(self.contract['deployment_status'], 'draft')
        self.assertFalse(self.contract['instruction_binding']['effective_load_verified'])

    def test_real_controls_require_configuration(self):
        for control in self.contract['controls'].values():
            self.assertFalse(control['supported'])
            self.assertIsNone(control['mechanism'])

    def test_no_invented_heartbeat_or_scheduler(self):
        self.assertIsNone(self.contract['communication']['heartbeat_seconds'])
        self.assertIsNone(self.contract['attention']['digest_scheduler_ref'])
        self.assertTrue(self.contract['attention']['scheduled_work_requires_runtime_receipt'])

    def test_authority_and_confidence_are_independent(self):
        self.assertFalse(self.contract['initiative']['provider_confidence_grants_authority'])
        self.assertFalse(self.contract['initiative']['reconfirm_unchanged_authorization'])
        self.assertFalse(self.contract['assurance']['authoritative_failures_can_be_averaged_away'])

    def test_adaptive_response_defaults(self):
        self.assertFalse(self.contract['communication']['mandatory_headings'])
        self.assertFalse(self.contract['communication']['always_add_followup'])
        self.assertEqual(self.contract['preferences']['format'], 'honor_user_request')

    def test_scoped_preferences_and_group_privacy(self):
        self.assertEqual(self.contract['preferences']['persistence'], 'explicit_scope_only')
        self.assertFalse(self.contract['multi_agent']['cross_audience_data_sharing'])
        self.assertFalse(self.contract['assurance']['engagement_manipulation_allowed'])

    def test_run_record_has_no_fabricated_measurements(self):
        record = load('assets/experience-run.template.json')
        self.assertEqual(record['status'], 'not_run')
        self.assertEqual(record['cases'], [])
        self.assertIsNone(record['critical_failures'])
        self.assertTrue(all(v is None for v in record['measurements'].values()))
        self.assertEqual(record['release_decision'], 'not_evaluated')

    def test_source_ids_resolve(self):
        source_doc = (ROOT / 'references/UX-SOURCES.md').read_text()
        sources = set(re.findall(r'^\| (U\d{2}) \|', source_doc, re.M))
        self.assertEqual(set(self.contract['assurance']['source_refs']), sources)
        for relative in ('references/human-agent-collaboration.md', 'references/experience-evaluation.md'):
            refs = set(re.findall(r'\bU\d{2}\b', (ROOT / relative).read_text()))
            self.assertTrue(refs <= sources)

    def test_existing_helper_bytes_are_unchanged(self):
        data = (ROOT / 'scripts/decision_tools.py').read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        self.assertEqual(blob, '5d43a33e813bbea4ca0f78b7291bd73f1196b1a4')

    def test_offline_demo_remains_nonexecuting(self):
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/decision_tools.py'), 'demo'],
                                capture_output=True, text=True, timeout=10, check=True)
        record = json.loads(result.stdout)
        self.assertFalse(record['applied'])
        self.assertFalse(record['authorized'])
        self.assertFalse(record['network_performed'])
        self.assertEqual(record['status'], 'shadow_only')

    def test_decision_examples_remain_shadow_only(self):
        for path in (ROOT / 'assets/examples').glob('*.contract.json'):
            c = json.loads(path.read_text())
            self.assertEqual(c['mode'], 'shadow')
            self.assertFalse(c['inputs']['external_transmission_enabled'])
            self.assertEqual(c['policy']['evaluation_status'], 'not_run')

    def test_system_spec_defaults_remain_nonactivating(self):
        s = load('assets/system-spec.template.json')
        self.assertTrue(s['template_only'])
        self.assertEqual(s['schema_version'], '0.4')
        self.assertFalse(s['decisions']['enabled'])
        self.assertFalse(s['experience']['effective_load_verified'])
        self.assertTrue((ROOT / s['experience']['contract_ref']).exists())
        self.assertTrue((ROOT / s['experience']['instruction_policy_ref']).exists())


if __name__ == '__main__':
    unittest.main()
