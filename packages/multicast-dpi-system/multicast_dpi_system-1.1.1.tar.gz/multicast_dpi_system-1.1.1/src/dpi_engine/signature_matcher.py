"""
Signature Matcher Module - Enhanced Version

This module provides signature matching for threat detection and packet prioritization.
Packet priority is determined by the highest severity signature match found.
"""
import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
from pathlib import Path
import logging

from src.core.packet_context import PacketContext
from src.utils.logging_utils import LoggingManager
from src.utils.config_handler import ConfigManager

@dataclass
class SignatureMatch:
    """Signature match result with threat level information"""
    signature_id: str
    signature_name: str
    category: str
    severity: int
    threat_level: int  # Threat level is derived from severity

@dataclass
class MatchResult:
    """Overall signature matching result"""
    matched: bool
    signature_name: str = ""
    threat_level: int = 0  # Renamed from priority to threat_level
    total_matches: int = 0
    highest_severity: int = 0

class SignatureMatcher:
    """
    Enhanced signature matcher for threat detection and security analysis.
    Threat level is determined by the highest severity signature match.
    This is separate from traffic classification priority.
    """
    
    def __init__(self, logging_manager: LoggingManager, config: Dict[str, Any], signatures_file: str):
        """Initialize signature matcher"""
        self.logger = logging_manager.get_logger(self.__class__.__name__)
        self.config = config or {}
        self.signatures_file = signatures_file
        self.signatures = []
        self._load_signatures(signatures_file)
    
    def _load_signatures(self, signature_file: str) -> None:
        """Load and compile signatures efficiently"""
        try:
            with open(signature_file, 'r') as f:
                data = json.load(f)
            
            for sig in data.get('signatures', []):
                try:
                    # Compile pattern once during initialization
                    pattern = re.compile(sig['pattern'].encode(), re.IGNORECASE)
                    self.signatures.append({
                        'id': sig['id'],
                        'name': sig['name'],
                        'category': sig['category'],
                        'severity': sig['severity'],
                        'protocol': sig.get('protocol', 'ANY'),  # Default to ANY protocol
                        'pattern': pattern,
                        'description': sig.get('description', '')
                    })
                except Exception as e:
                    self.logger.error(f"Failed to load signature {sig.get('id')}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to load signatures: {e}")
    
    def match_signatures(self, context: PacketContext) -> None:
        """
        Match signatures against packet payload and determine priority.
        Priority is based on the highest severity signature match.
        """
        try:
            # Get protocol information from previous DPI analysis
            dpi_metadata = context.dpi_metadata.get('protocol_identification', {})
            protocol = dpi_metadata.get('application_protocol', 'Unknown')
            codec = dpi_metadata.get('codec', 'Unknown')
            
            payload = context.packet.payload or b""
            if not payload:
                # No payload to analyze
                match_result = MatchResult(matched=False, threat_level=0)
                context.dpi_metadata['signature_matching'] = asdict(match_result)
                return
            
            # Find all matching signatures
            matches = []
            for sig in self.signatures:
                # Check if signature applies to this protocol or is protocol-agnostic
                if (sig['protocol'] == 'ANY' or 
                    sig['protocol'] == protocol or 
                    sig['protocol'] == 'Unknown' or
                    protocol == 'Unknown'):
                    
                    if sig['pattern'].search(payload):
                        # Create signature match with priority = severity
                        signature_match = SignatureMatch(
                            signature_id=sig['id'],
                            signature_name=sig['name'],
                            category=sig['category'],
                            severity=sig['severity'],
                            threat_level=sig['severity']  # Priority equals severity
                        )
                        matches.append(signature_match)
            
            # Determine overall match result and priority
            if matches:
                # Sort by severity (highest first)
                matches.sort(key=lambda x: x.severity, reverse=True)
                highest_severity = matches[0].severity
                
                # Overall priority is the highest severity match
                match_result = MatchResult(
                    matched=True,
                    signature_name=matches[0].signature_name,
                    threat_level=highest_severity,  # Priority = highest severity
                    total_matches=len(matches),
                    highest_severity=highest_severity
                )
                
                # Store all matches in metadata
                context.dpi_metadata['signature_matches'] = [
                    {
                        'id': m.signature_id,
                        'name': m.signature_name,
                        'category': m.category,
                        'severity': m.severity,
                        'threat_level': m.threat_level
                    }
                    for m in matches
                ]
            else:
                # No matches found
                match_result = MatchResult(
                    matched=False,
                    threat_level=0,
                    total_matches=0,
                    highest_severity=0
                )
            
            # Store the overall match result
            context.dpi_metadata['signature_matching'] = asdict(match_result)
            
        except Exception as e:
            self.logger.error(f"Signature matching error: {e}")
            # Set default result on error
            context.dpi_metadata['signature_matching'] = asdict(MatchResult(matched=False, threat_level=0))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get signature matcher statistics"""
        return {
            'total_signatures': len(self.signatures),
            'protocol_specific': len([s for s in self.signatures if s['protocol'] != 'ANY']),
            'protocol_agnostic': len([s for s in self.signatures if s['protocol'] == 'ANY'])
        }
    
    def shutdown(self):
        """Clean shutdown"""
        pass

    def reload_signatures(self, signatures_file: str) -> None:
        """Reloads signatures from the specified file."""
        self._load_signatures(signatures_file)
        print(f"✅ Signature Matcher: {len(self.signatures)} signatures loaded")

def create_signature_matcher(logging_manager: LoggingManager, config: Dict[str, Any], signatures_file: str) -> SignatureMatcher:
    """Create and return a signature matcher instance"""
    return SignatureMatcher(logging_manager, config, signatures_file)
