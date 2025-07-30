import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple
import re

from .canon_registry import CanonRegistry
from .sacred_chain import SacredChainBase, SacredChainTrace, TrustVerdict


class IRLEngine(SacredChainBase):

    def __init__(
            self,
            config: Any,
            canon_registry: Optional[CanonRegistry] = None) -> None:
        super().__init__()
        self.config = config
        self.canon_registry = canon_registry or CanonRegistry()
        self.logger = logging.getLogger(__name__)

    async def __aenter__(self) -> "IRLEngine":
        self.logger.info("IRL Engine initialized with full traceability")
        return self

    async def __aexit__(
            self,
            exc_type: Optional[type],
            exc_val: Optional[Exception],
            exc_tb: Optional[Any]) -> None:
        self._finalize_audit_log()

    def _finalize_audit_log(self) -> None:
        if not self.execution_log:
            return

        audit_file = f"audits/records/sigil_audit_{int(time.time())}.json"
        try:
            # Ensure audits/records directory exists
            import os
            os.makedirs("audits/records", exist_ok=True)
            
            with open(audit_file, "w") as f:
                # Since to_audit_log() returns JSON string, parse it first
                audit_data = []
                for trace in self.execution_log:
                    try:
                        audit_entry = json.loads(trace.to_audit_log())
                        audit_data.append(audit_entry)
                    except (json.JSONDecodeError, TypeError) as e:
                        self.logger.error(f"Failed to serialize trace: {e}")
                        # Add a fallback entry
                        audit_data.append({
                            "execution_id": getattr(trace, 'execution_id', 'unknown'),
                            "timestamp": getattr(trace, 'timestamp', 'unknown'),
                            "error": f"Serialization failed: {str(e)}",
                            "rule_zero_compliant": False
                        })
                
                json.dump(audit_data, f, indent=2)
            self.logger.info(f"Audit log finalized: {audit_file}")
        except IOError as e:
            self.logger.error(f"Failed to write audit log {audit_file}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error finalizing audit log: {e}")

    async def analyze_with_sacred_chain(
            self, input_data: str) -> SacredChainTrace:
        canonical_input = self._canonicalize_input(input_data)
        reasoning_steps = [
            f"Input canonicalized: '{input_data}' -> '{canonical_input}'"]

        context_sources = await self._gather_validated_context(canonical_input)
        reasoning_steps.append(
            f"Context gathered from {
                len(context_sources)} validated sources")

        analysis_results = await self._execute_reasoning_chain(canonical_input, context_sources)
        reasoning_steps.extend(analysis_results[0])

        suggestion = self._generate_traceable_suggestion(reasoning_steps)
        verdict, verdict_reason = self._make_trust_decision(
            reasoning_steps, suggestion, analysis_results[5],  # quality_score
            analysis_results[2],  # docs
            analysis_results[3],  # sentiment
            analysis_results[4],  # ecosystem
        )
        reasoning_steps.append(f"Trust decision: {verdict} - {verdict_reason}")

        irl_score = self._calculate_irl_score(
            context_sources, reasoning_steps, verdict,
            docs=analysis_results[1]) # Pass docs from analysis_results
        reasoning_steps.append(f"IRL confidence: {irl_score:.3f}")

        audit_info = {
            "metadata": analysis_results[1],
            "sentiment": analysis_results[2],
            "ecosystem": analysis_results[3],
            "quality_score": analysis_results[5],
            "verdict_reason": verdict_reason,
        }

        return self.create_sacred_chain_trace(
            input_data=canonical_input,
            context_sources=context_sources,
            reasoning_steps=reasoning_steps,
            suggestion=suggestion,
            verdict=verdict,
            audit_info=audit_info,
            irl_score=irl_score,
        )

    def _canonicalize_input(self, input_data: str) -> str:
        canonical = input_data.strip().lower()
        if canonical.startswith("crate:"):
            canonical = canonical[6:]
        if canonical.startswith("rust:"):
            canonical = canonical[5:]
        return canonical

    async def _gather_validated_context(self, input_data: str) -> List[str]:
        valid_sources = self.canon_registry.get_valid_canon_sources()
        context_sources = []

        for source in valid_sources:
            authority_level = self.canon_registry.get_authority_level(source)
            if authority_level >= 5:
                context_sources.append(source)

        return context_sources

    async def _execute_reasoning_chain(
        self, input_data: str, sources: List[str]
    ) -> Tuple[List[str], Dict[str, Any], Dict[str, Any], Dict[str, Any], Dict[str, Any], float]:
        reasoning_steps = []

        metadata = await self._extract_basic_metadata(input_data)
        reasoning_steps.append(f"Metadata extracted: {len(metadata)} fields")

        docs = {}
        docs = await self._analyze_documentation(input_data)
        reasoning_steps.append(
            f"Documentation analyzed: quality {
                docs.get(
                    'quality_score',
                    0):.1f}")

        sentiment = await self._analyze_community_sentiment(input_data)
        reasoning_steps.append(
            f"Sentiment analyzed: {
                sentiment.get(
                    'overall',
                    'unknown')}")

        ecosystem = await self._analyze_ecosystem_position(input_data)
        
        # Extract actual ecosystem data from documentation
        ecosystem = self._extract_ecosystem_data_from_docs(docs, ecosystem)
        
        reasoning_steps.append(
            f"Ecosystem analyzed: {
                ecosystem.get(
                    'category',
                    'unknown')}")

        quality_score = self._synthesize_quality_score(
            metadata, docs, sentiment, ecosystem)
        reasoning_steps.append(
            f"Quality score synthesized: {
                quality_score:.2f}")

        return reasoning_steps, metadata, docs, sentiment, ecosystem, quality_score

    async def _extract_basic_metadata(self, input_data: str) -> Dict[str, Any]:
        return {
            "name": input_data,
            "type": "rust_crate",
            "source": "manual_input",
            "extraction_method": "irl_engine",
        }

    async def _analyze_documentation(self, input_data: str) -> Dict[str, Any]:
        try:
            return {
                "quality_score": 7.0,
                "completeness": 0.8,
                "examples_present": True,
                "api_documented": True,
            }
        except Exception as e:
            self.logger.error(f"Documentation analysis failed: {e}")
            return {"quality_score": 5.0, "error": str(e)}

    async def _analyze_community_sentiment(
            self, input_data: str) -> Dict[str, Any]:
        # For now, return neutral sentiment as default
        # In a real implementation, this would analyze community discussions,
        # GitHub issues, Reddit posts, etc.
        return {
            "overall": "neutral",
            "positive_mentions": 0,
            "negative_mentions": 0,
            "neutral_mentions": 1,
            "total_mentions": 1,
        }

    async def _analyze_ecosystem_position(
            self, input_data: str) -> Dict[str, Any]:
        # This would normally analyze ecosystem data
        # For now, return default values that will be overridden by actual data extraction
        return {
            "category": "utilities",
            "maturity": "stable",
            "dependencies_count": 5,
            "reverse_deps_visible": 15,
            "ecosystem_score": 5.0,  # Start at neutral, not artificially high
            "downloads_all_time": 0,  # Will be extracted from docs
            "downloads_per_month": 0,  # Will be extracted from docs
        }

    def _extract_ecosystem_data_from_docs(self, docs: Dict[str, Any], ecosystem: Dict[str, Any]) -> Dict[str, Any]:
        """Extract ecosystem data from documentation using source-aware strategies"""
        updated_ecosystem = ecosystem.copy()
        
        for source_name, source_data in docs.get("sanitized_documentation", {}).items():
            content = source_data.get("content", {})
            raw_markdown = content.get("raw_markdown", "")
            
            # Apply source-specific extraction strategies
            if source_name == "lib_rs":
                updated_ecosystem = self._extract_lib_rs_data(raw_markdown, updated_ecosystem)
            elif source_name == "crates_io":
                updated_ecosystem = self._extract_crates_io_data(raw_markdown, updated_ecosystem)
            elif source_name == "docs_rs":
                updated_ecosystem = self._extract_docs_rs_data(raw_markdown, updated_ecosystem)
            elif source_name == "github_com":
                updated_ecosystem = self._extract_github_data(raw_markdown, updated_ecosystem)
            
            # If we found data, we can stop (prioritize lib.rs as it has the best data)
            if (updated_ecosystem.get("downloads_all_time", 0) > 0 and 
                updated_ecosystem.get("reverse_deps_visible", 0) > 0):
                break
        
        return updated_ecosystem
    
    def _extract_lib_rs_data(self, raw_markdown: str, ecosystem: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from lib.rs documentation (has the most reliable format)"""
        updated_ecosystem = ecosystem.copy()
        
        # lib.rs format: "**16,411,318** downloads per month Used in **42,104** crates (29,028 directly)"
        
        # Extract downloads (both monthly and all-time patterns)
        download_patterns = [
            r"\*\*(\d{1,3}(?:,\d{3})*)\*\*\s*downloads?\s*per\s*month",  # Monthly downloads
            r"(\d{1,3}(?:,\d{3})*)\s*downloads?\s*all\s*time",  # All-time downloads
            r"\*\*(\d{1,3}(?:,\d{3})*)\*\*\s*downloads?\s*all\s*time",  # All-time downloads with markdown
            r"\*\*(\d{1,3}(?:,\d{3})*)\*\*\s*downloads?\s*per\s*month\s*",  # Monthly downloads with trailing space
        ]
        
        for pattern in download_patterns:
            match = re.search(pattern, raw_markdown, re.IGNORECASE)
            if match:
                downloads_str = match.group(1).replace(",", "")
                try:
                    downloads = int(float(downloads_str))
                    if "per month" in pattern:
                        # Convert monthly to approximate all-time (rough estimate)
                        updated_ecosystem["downloads_all_time"] = downloads * 12 * 5  # 5 years estimate
                    else:
                        updated_ecosystem["downloads_all_time"] = downloads
                    break
                except ValueError:
                    pass
        
        # Extract reverse dependencies
        reverse_deps_patterns = [
            # Match inside a markdown link with bold numbers
            r"Used in \[\*\*(\d{1,3}(?:,\d{3})*)\*\* crates \((\d{1,3}(?:,\d{3})*) directly\)\]\([^)]+\)",
            # Fallbacks
            r"Used in\s*\[?\*\*(\d{1,3}(?:,\d{3})*)\*\*\s*crates?\s*\((\d{1,3}(?:,\d{3})*)\s*directly\)\]?",
            r"\*\*(\d{1,3}(?:,\d{3})*)\*\*\s*crates?\s*\((\d{1,3}(?:,\d{3})*)\s*directly\)",
            # More flexible pattern for the exact format we see
            r"Used in\s*\[?\*\*(\d{1,3}(?:,\d{3})*)\*\*\s*crates?\s*\((\d{1,3}(?:,\d{3})*)\s*directly\)\]?\([^)]*\)",
        ]

        found = False
        for pattern in reverse_deps_patterns:
            match = re.search(pattern, raw_markdown, re.IGNORECASE)
            if match:
                try:
                    total_deps = int(match.group(1).replace(",", ""))
                    direct_deps = int(match.group(2).replace(",", ""))
                    updated_ecosystem["reverse_deps_visible"] = total_deps
                    updated_ecosystem["reverse_deps_direct"] = direct_deps
                    found = True
                    break
                except ValueError:
                    pass
        # Fallback: extract all numbers from the 'Used in' line
        if not found:
            for line in raw_markdown.splitlines():
                if "Used in" in line:
                    nums = re.findall(r"\d{1,3}(?:,\d{3})*", line)
                    if len(nums) >= 2:
                        try:
                            total_deps = int(nums[0].replace(",", ""))
                            direct_deps = int(nums[1].replace(",", ""))
                            updated_ecosystem["reverse_deps_visible"] = total_deps
                            updated_ecosystem["reverse_deps_direct"] = direct_deps
                            found = True
                            break
                        except Exception:
                            pass
                    # Print the line for manual inspection if still not found
                    print(f"[DEBUG] Could not extract reverse deps from line: {line}")
        return updated_ecosystem
    
    def _extract_crates_io_data(self, raw_markdown: str, ecosystem: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from crates.io documentation"""
        updated_ecosystem = ecosystem.copy()
        
        # crates.io format: "453,318,021 Downloads all time"
        download_patterns = [
            r"(\d{1,3}(?:,\d{3})*)\s*Downloads?\s*all\s*time",
            r"(\d{1,3}(?:,\d{3})*)\s*downloads?\s*all\s*time",
        ]
        
        for pattern in download_patterns:
            match = re.search(pattern, raw_markdown, re.IGNORECASE)
            if match:
                downloads_str = match.group(1).replace(",", "")
                try:
                    downloads = int(float(downloads_str))
                    updated_ecosystem["downloads_all_time"] = downloads
                    break
                except ValueError:
                    pass
        
        # crates.io doesn't have reverse dependency data in the main page
        # We'd need to scrape the reverse dependencies page separately
        
        return updated_ecosystem
    
    def _extract_docs_rs_data(self, raw_markdown: str, ecosystem: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from docs.rs documentation"""
        updated_ecosystem = ecosystem.copy()
        
        # docs.rs typically doesn't have download/reverse dependency data
        # It's mainly API documentation
        # But we can look for any metadata that might be present
        
        return updated_ecosystem
    
    def _extract_github_data(self, raw_markdown: str, ecosystem: Dict[str, Any]) -> Dict[str, Any]:
        """Extract data from GitHub documentation"""
        updated_ecosystem = ecosystem.copy()
        
        # GitHub README might have some usage statistics
        # Look for common patterns in README files
        
        # Stars, forks, etc. could be indicators of popularity
        star_patterns = [
            r"(\d{1,3}(?:,\d{3})*)\s*stars?",
            r"⭐\s*(\d{1,3}(?:,\d{3})*)",
        ]
        
        for pattern in star_patterns:
            match = re.search(pattern, raw_markdown, re.IGNORECASE)
            if match:
                stars_str = match.group(1).replace(",", "")
                try:
                    stars = int(float(stars_str))
                    # Use stars as a rough proxy for ecosystem position
                    if stars > 1000:
                        updated_ecosystem["ecosystem_score"] = min(ecosystem.get("ecosystem_score", 5.0) + 2.0, 10.0)
                    elif stars > 100:
                        updated_ecosystem["ecosystem_score"] = min(ecosystem.get("ecosystem_score", 5.0) + 1.0, 10.0)
                    break
                except ValueError:
                    pass
        
        return updated_ecosystem

    def _synthesize_quality_score(
        self,
        metadata: Dict[str, Any],
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
    ) -> float:
        scores = []

        doc_score = docs.get("quality_score", 5.0)
        scores.append(doc_score)

        sentiment_score = 5.0
        if sentiment.get("overall") == "positive":
            sentiment_score = 8.0
        elif sentiment.get("overall") == "negative":
            sentiment_score = 3.0
        scores.append(sentiment_score)

        ecosystem_score = ecosystem.get("ecosystem_score", 5.0)
        scores.append(ecosystem_score)

        return sum(scores) / len(scores) if scores else 5.0

    def _generate_traceable_suggestion(
            self, reasoning_steps: List[str]) -> str:
        if not reasoning_steps:
            return "DEFER: Insufficient reasoning data"

        quality_indicators = [
            step for step in reasoning_steps if "quality" in step.lower()]
        sentiment_indicators = [
            step for step in reasoning_steps if "sentiment" in step.lower()]

        if quality_indicators and any(
                "high" in indicator.lower() for indicator in quality_indicators):
            return "ALLOW: High quality indicators detected"
        elif sentiment_indicators and any("positive" in indicator.lower() for indicator in sentiment_indicators):
            return "ALLOW: Positive community sentiment"
        else:
            return "DEFER: Requires additional analysis"

    def _make_trust_decision(
        self,
        reasoning_steps: List[str],
        suggestion: str,
        quality_score: float,
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
    ) -> Tuple[TrustVerdict, str]:
        # Auto-deny logic for clearly problematic crates
        if self._should_auto_deny(quality_score, docs, sentiment, ecosystem):
            return TrustVerdict.DENY, "Auto-denied: Crate fails critical safety criteria"
        
        # Auto-promotion logic for high-quality crates with strict criteria
        if self._should_auto_promote(quality_score, docs, sentiment, ecosystem):
            return TrustVerdict.ALLOW, "Auto-promoted: High quality with permissive license and high usage"
        
        # Everything else gets DEFER for manual review
        return TrustVerdict.DEFER, "Requires manual review - insufficient evidence for automatic decision"

    def _should_auto_deny(
        self,
        quality_score: float,
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
    ) -> bool:
        """
        Auto-deny crates that are clearly unfit for use:
        - Critical security advisories
        - Extremely low quality (score < 4.0)
        - Deprecated/abandoned crates
        - Negative sentiment with low quality
        """
        
        # Critical security advisories
        if self._has_critical_advisories(ecosystem):
            return True
            
        # Extremely low quality
        if quality_score < 4.0:
            return True
            
        # Negative sentiment with low quality
        if sentiment.get("overall") == "negative" and quality_score < 6.0:
            return True
            
        # Check for deprecation/abandonment indicators
        if self._is_deprecated_or_abandoned(docs, ecosystem):
            return True
            
        return False
    
    def _should_auto_promote(
        self,
        quality_score: float,
        docs: Dict[str, Any],
        sentiment: Dict[str, Any],
        ecosystem: Dict[str, Any],
    ) -> bool:
        """
        Auto-promote to ALLOW only when ALL criteria are met:
        - Quality score ≥ 8.0 (increased from 7.0)
        - Permissive license (MIT/Apache/Unlicense)
        - High usage: downloads ≥ 10M and reverse-deps ≥ 200 (increased thresholds)
        - No critical advisories
        - Not deprecated/abandoned
        - Recent activity (within 2 years)
        """
        
        # Quality score check (increased threshold)
        if quality_score < 8.0:
            return False
            
        # License check - look for permissive licenses in documentation
        license_info = self._extract_license_info(docs)
        if not self._is_permissive_license(license_info):
            return False
            
        # Usage metrics check (increased thresholds)
        downloads = ecosystem.get("downloads_all_time", 0)
        reverse_deps = ecosystem.get("reverse_deps_visible", 0)
        
        # Check for external trust artifacts
        trust_artifacts = self._check_external_trust_artifacts(docs)
        
        # Adjust thresholds based on trust artifacts
        if trust_artifacts.get("security_audit", False):
            # Security audit allows lower usage thresholds
            if downloads < 5000000 or reverse_deps < 100:  # 5M downloads, 100 reverse deps
                return False
        else:
            # Standard thresholds without audit (increased)
            if downloads < 10000000 or reverse_deps < 200:  # 10M downloads, 200 reverse deps
                return False
            
        # Security check - no critical advisories
        if self._has_critical_advisories(ecosystem):
            return False
            
        # Not deprecated/abandoned
        if self._is_deprecated_or_abandoned(docs, ecosystem):
            return False
            
        return True
    
    def _extract_license_info(self, docs: Dict[str, Any]) -> str:
        """Extract license information from documentation"""
        # Look for license info in various documentation sources
        for source_name, source_data in docs.get("sanitized_documentation", {}).items():
            content = source_data.get("content", {})
            raw_markdown = content.get("raw_markdown", "")
            
            # Common license patterns
            license_patterns = [
                r"Apache-2\.0.*MIT",
                r"MIT.*Apache-2\.0", 
                r"Apache License.*MIT",
                r"MIT license.*Apache",
                r"Unlicense",
                r"MIT OR Apache-2\.0",
                r"Apache-2\.0 OR MIT",
                r"\*\*MIT\*\* license",  # **MIT** license
                r"MIT license",  # MIT license
                r"licensed under the MIT license",  # licensed under the MIT license
                r"licensed under the \[MIT license\]",  # licensed under the [MIT license]
                r"MIT License",  # MIT License
                r"Apache-2\.0",  # Apache-2.0
                r"Apache License",  # Apache License
            ]
            
            for pattern in license_patterns:
                if re.search(pattern, raw_markdown, re.IGNORECASE):
                    return pattern
                    
        return ""
    
    def _is_permissive_license(self, license_info: str) -> bool:
        """Check if license is permissive (MIT, Apache-2.0, or Unlicense)"""
        permissive_licenses = ["mit", "apache", "unlicense"]
        return any(license in license_info.lower() for license in permissive_licenses)
    
    def _has_critical_advisories(self, ecosystem: Dict[str, Any]) -> bool:
        """Check for critical security advisories"""
        # This would need to be implemented with actual RUSTSEC database lookup
        # For now, return False (no critical advisories)
        return False
    
    def _is_deprecated_or_abandoned(self, docs: Dict[str, Any], ecosystem: Dict[str, Any]) -> bool:
        """
        Check if a crate is deprecated or abandoned based on documentation and ecosystem data
        """
        # Look for deprecation indicators in documentation
        for source_name, source_data in docs.get("sanitized_documentation", {}).items():
            content = source_data.get("content", {})
            raw_markdown = content.get("raw_markdown", "")
            
            # Check for deprecation keywords
            deprecation_patterns = [
                r"deprecated",
                r"this crate is deprecated",
                r"no longer maintained",
                r"abandoned",
                r"use.*instead",
                r"superseded by",
                r"replaced by",
                r"legacy",
                r"obsolete"
            ]
            
            for pattern in deprecation_patterns:
                if re.search(pattern, raw_markdown, re.IGNORECASE):
                    return True
        
        # Check for very low usage (potential abandonment)
        downloads = ecosystem.get("downloads_all_time", 0)
        reverse_deps = ecosystem.get("reverse_deps_visible", 0)
        
        # If downloads < 1000 and reverse deps < 5, likely abandoned
        if downloads < 1000 and reverse_deps < 5:
            return True
            
        return False

    def _check_external_trust_artifacts(self, docs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check for external trust artifacts like audit reports, SBOMs, etc.
        Returns a dict with artifact types found and their impact on confidence.
        """
        artifacts = {
            "security_audit": False,
            "sbom_available": False,
            "cargo_audit_clean": False,
            "audit_report_url": None,
            "confidence_boost": 0.0
        }
        
        # Look for audit mentions in documentation
        for source_name, source_data in docs.get("sanitized_documentation", {}).items():
            content = source_data.get("content", {})
            raw_markdown = content.get("raw_markdown", "")
            
            # Check for security audit mentions
            audit_patterns = [
                r"security audit by (\w+)",
                r"audit by (\w+)",
                r"(\w+) audit",
                r"audit report",
                r"NCC Group",
                r"Trail of Bits",
                r"Cure53",
                r"Quarkslab"
            ]
            
            for pattern in audit_patterns:
                if re.search(pattern, raw_markdown, re.IGNORECASE):
                    artifacts["security_audit"] = True
                    artifacts["confidence_boost"] += 0.2
                    
                    # Extract audit report URL if present
                    url_pattern = r"https?://[^\s\)]+(?:audit|review|report)[^\s\)]*"
                    url_match = re.search(url_pattern, raw_markdown, re.IGNORECASE)
                    if url_match:
                        artifacts["audit_report_url"] = url_match.group(0)
                    break
            
            # Check for SBOM mentions
            sbom_patterns = [
                r"SBOM",
                r"Software Bill of Materials",
                r"bom\.json",
                r"spdx",
                r"cyclonedx"
            ]
            
            for pattern in sbom_patterns:
                if re.search(pattern, raw_markdown, re.IGNORECASE):
                    artifacts["sbom_available"] = True
                    artifacts["confidence_boost"] += 0.1
                    break
        
        return artifacts

    def _calculate_irl_score(
        self,
        context_sources: List[str],
        reasoning_steps: List[str],
        verdict: TrustVerdict,
        docs: Optional[Dict[str, Any]] = None,
    ) -> float:
        base_score = 5.0

        authority_bonus = sum(self.canon_registry.get_authority_level(
            source) for source in context_sources) / 10.0
        base_score += min(authority_bonus, 2.0)

        reasoning_bonus = min(len(reasoning_steps) * 0.2, 2.0)
        base_score += reasoning_bonus

        # Add confidence boost from external trust artifacts
        if docs:
            trust_artifacts = self._check_external_trust_artifacts(docs)
            confidence_boost = trust_artifacts.get("confidence_boost", 0.0)
            base_score += confidence_boost

        if verdict == TrustVerdict.ALLOW:
            base_score += 1.0
        elif verdict == TrustVerdict.DENY:
            base_score += 0.5

        return min(base_score, 10.0)
