"""
Modern Filter Engine with manual filtering support only.
Enhanced with better type safety, performance optimizations, and extended filtering capabilities.
"""
from typing import List, Tuple, Optional, Pattern, Callable, Any
import re
from dataclasses import dataclass
from pathlib import Path
from src.utils.logging_utils import LoggingManager
from src.core.packet import Packet


@dataclass
class FilterRule:
    """Container for filter rule with compiled versions"""
    original: str
    manual_matcher: Optional[Callable[[Packet], bool]] = None


class FilterEngine:
    def __init__(self, logging_manager: LoggingManager, filter_config: dict):
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.config = filter_config or {}
        self._rules: List[FilterRule] = []
        self._port_range_pattern: Pattern = re.compile(r'^(\d+)-(\d+)$')
        if self.config.get('enable', False):
            manual_rules = self.config.get('manual_rules', [])
            self.update_filters(manual_rules)
        else:
            self.logger.info("Filtering is disabled in configuration")

    def update_filters(self, rules: List[str]) -> bool:
        new_rules = []
        success = True
        for rule in rules:
            try:
                validated_rule = self._validate_and_compile(rule)
                if validated_rule:
                    new_rules.append(validated_rule)
                else:
                    success = False
            except Exception as e:
                self.logger.error(f"Error processing rule '{rule}': {e}", exc_info=True)
                success = False
        if success:
            self._rules = new_rules
            self.logger.info(f"Updated manual filters: {len(self._rules)} active rules")
        return success

    def _validate_and_compile(self, rule: str) -> Optional[FilterRule]:
        rule = rule.strip()
        if not rule:
            return None
        manual_matcher = self._create_manual_matcher(rule)
        if manual_matcher:
            return FilterRule(original=rule, manual_matcher=manual_matcher)
        self.logger.error(f"Invalid manual rule syntax: {rule}")
        return None

    def _create_manual_matcher(self, rule: str) -> Optional[Callable[[Packet], bool]]:
        # Remove outer parentheses
        rule = rule.strip()
        if rule.startswith('(') and rule.endswith(')'):
            rule = rule[1:-1].strip()

        # Split by ' or ' (lowest precedence)
        or_parts = self._split_logical(rule, 'or')
        if len(or_parts) > 1:
            matchers = [self._create_manual_matcher(part) for part in or_parts]
            if any(m is None for m in matchers):
                return None
            return lambda p: any(m(p) for m in matchers)

        # Split by ' and ' (higher precedence)
        and_parts = self._split_logical(rule, 'and')
        if len(and_parts) > 1:
            matchers = [self._create_manual_matcher(part) for part in and_parts]
            if any(m is None for m in matchers):
                return None
            return lambda p: all(m(p) for m in matchers)

        # Base cases (simple rules)
        return self._create_simple_matcher(rule)

    def _split_logical(self, rule: str, op: str):
        # Splits by logical op, respecting parentheses
        parts, depth, last, i = [], 0, 0, 0
        op_str = f' {op} '
        while i < len(rule):
            if rule[i] == '(':
                depth += 1
            elif rule[i] == ')':
                depth -= 1
            elif depth == 0 and rule[i:i+len(op_str)] == op_str:
                parts.append(rule[last:i].strip())
                last = i + len(op_str)
                i += len(op_str) - 1
            i += 1
        parts.append(rule[last:].strip())
        return parts

    def _create_simple_matcher(self, rule: str) -> Optional[Callable[[Packet], bool]]:
        rule_lower = rule.lower()
        if rule_lower.startswith("port "):
            port_spec = rule[5:].strip()
            return self._create_port_matcher(port_spec)
        elif rule_lower.startswith("src host "):
            ip = rule[9:].strip()
            return lambda p: p.src_ip == ip
        elif rule_lower.startswith("dst host "):
            ip = rule[9:].strip()
            return lambda p: p.dst_ip == ip
        elif rule_lower in {"tcp", "udp", "icmp", "ip", "ip6"}:
            return lambda p: p.protocol.lower() == rule_lower
        return None


    def _create_port_matcher(self, port_spec: str) -> Callable[[Packet], bool]:
        if '-' in port_spec:
            try:
                start, end = map(int, port_spec.split('-'))
                return lambda p: (
                    (p.dst_port and start <= p.dst_port <= end) or
                    (p.src_port and start <= p.src_port <= end)
                )
            except ValueError:
                self.logger.warning(f"Invalid port range: {port_spec}")
                return lambda p: False
        try:
            port = int(port_spec)
            return lambda p: p.dst_port == port or p.src_port == port
        except ValueError:
            self.logger.warning(f"Invalid port: {port_spec}")
            return lambda p: False

    def _match_host(self, packet: Packet, direction: str, ip: str) -> bool:
        if direction == "src":
            return packet.src_ip == ip
        return packet.dst_ip == ip

    def apply_filter(self, packet: Packet) -> bool:
        if not self._rules:
            # If filtering is enabled but no rules are defined, default to 'deny'
            # To allow all, 'enable' should be false or a rule like 'ip' should be added
            return True
        try:
            for rule in self._rules:
                if rule.manual_matcher and rule.manual_matcher(packet):
                    return False
            return True
        except Exception as e:
            self.logger.error(f"Filter error on packet: {e}", exc_info=True)
            return False # Fail-safe

    def reload_config(self, filter_config: dict) -> None:
        self.config = filter_config or {}
        if self.config.get('enable', False):
            manual_rules = self.config.get('manual_rules', [])
            self.update_filters(manual_rules)
        else:
            self._rules = [] # Clear rules if filtering is disabled
            self.logger.info("Filtering disabled upon reload.")

    def get_bpf_string(self) -> str:
        """Constructs a BPF filter string from the configuration."""
        if self.config.get('enable', False):
            bpf_rules = self.config.get('bpf_rules', [])
            return " and ".join(rule for rule in bpf_rules if rule)
        return ""

    def __str__(self) -> str:
        return f"Manual FilterEngine with {len(self._rules)} rules"

    def __len__(self) -> int:
        return len(self._rules)

    def shutdown(self) -> None:
        """Shutdown the filter engine and release any resources (future extensibility)."""
        # Placeholder for future cleanup logic
        self.logger.info("Filter Engine shutdown.")
        pass