import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional
from django.utils import timezone
from core.models import (ScannerIntegration, FieldMapping, SeverityMapping, AssetType, 
                        AssetCategory, AssetSubtype, Asset, Vulnerability, Finding)
from django.db import transaction
import json
import logging
from datetime import datetime
from decimal import Decimal

logger = logging.getLogger(__name__)

class ScannerImporter:
    """
    Importer for Nessus .nessus files using dynamic field and severity mappings from the database.
    Parses XML, extracts assets, vulnerabilities, and findings, and creates/updates records.
    """
    def __init__(self, integration_name: str = 'Nessus'):
        self.integration = ScannerIntegration.objects.get(name=integration_name, is_active=True)
        self.field_mappings = self._load_field_mappings()
        self.severity_mappings = self._load_severity_mappings()
        # Cache asset categories and subtypes for performance
        self._asset_categories = {cat.name: cat for cat in AssetCategory.objects.all()}
        self._asset_subtypes = {
            (sub.category.name, sub.name): sub 
            for sub in AssetSubtype.objects.select_related('category')
        }
        self.tree: Optional[ET.ElementTree] = None
        self.root: Optional[ET.Element] = None
        self.created_assets = 0
        self.created_vulnerabilities = 0
        self.created_findings = 0
        self.updated_findings = 0

    def _load_field_mappings(self) -> Dict[str, List[FieldMapping]]:
        """Load active field mappings from the database, grouped by target_model."""
        mappings = {}
        for mapping in self.integration.field_mappings.filter(is_active=True).order_by('sort_order'):
            mappings.setdefault(mapping.target_model, []).append(mapping)
        return mappings

    def _load_severity_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Load severity mappings from the database."""
        return {
            sm.external_severity: {
                'label': sm.internal_severity_label,
                'level': sm.internal_severity_level
            }
            for sm in self.integration.severity_mappings.filter(is_active=True)
        }

    def _apply_nessus_system_type_mapping(self, system_type_value):
        """Map Nessus system-type to AssetSubtype ID."""
        if not system_type_value:
            return None
            
        # Define mapping from Nessus system-type to our subtypes
        nessus_to_subtype_mapping = {
            'general-purpose': 'Server',
            'embedded': 'Appliance',
            'router': 'Router',
            'switch': 'Switch',
            'firewall': 'Firewall',
            'load-balancer': 'Load Balancer',
            'storage': 'Storage Device',
            'printer': 'Printer',
            'scanner': 'Scanner',
            'wireless-access-point': 'Network Device',
            'voip-adapter': 'Network Device',
            'voip-phone': 'Network Device',
            'webcam': 'IoT Device',
            'game-console': 'IoT Device',
            'media-device': 'IoT Device',
            'terminal-server': 'Server',
            'hypervisor': 'Virtual Machine',
            'virtualization': 'Virtual Machine',
            'scada': 'IoT Device',
            'broadband-router': 'Router',
            'PoS': 'Appliance',
            'VNC': 'Server',
            'X11': 'Workstation',
            'Windows': 'Workstation',
            'Linux': 'Server',
            'Unix': 'Server',
            'Mac': 'Workstation',
        }
        
        # Try exact match first
        subtype_name = nessus_to_subtype_mapping.get(system_type_value)
        if not subtype_name:
            # Try partial matches for common patterns
            lower_type = system_type_value.lower()
            if 'server' in lower_type or 'linux' in lower_type or 'unix' in lower_type:
                subtype_name = 'Server'
            elif 'router' in lower_type:
                subtype_name = 'Router'
            elif 'switch' in lower_type:
                subtype_name = 'Switch'
            elif 'firewall' in lower_type:
                subtype_name = 'Firewall'
            elif 'windows' in lower_type or 'workstation' in lower_type:
                subtype_name = 'Workstation'
            elif 'printer' in lower_type:
                subtype_name = 'Printer'
            elif 'storage' in lower_type or 'nas' in lower_type:
                subtype_name = 'Storage Device'
            else:
                # Default to Server for unknown types
                subtype_name = 'Server'
        
        # Look up the subtype ID
        subtype = self._asset_subtypes.get(('Host', subtype_name))
        return subtype.subtype_id if subtype else None

    def _get_default_scanner_category(self):
        """Get the default category ID for this scanner integration."""
        if self.integration.default_asset_category:
            return self.integration.default_asset_category.category_id
        # Fallback to Host category
        host_category = self._asset_categories.get('Host')
        return host_category.category_id if host_category else None

    def _apply_transformation(self, value, mapping):
        """Apply transformation rule if specified."""
        if not mapping.transformation_rule or not value:
            return value
            
        # Handle special transformation rules
        if mapping.transformation_rule == 'nessus_system_type_map':
            return self._apply_nessus_system_type_mapping(value)
        elif mapping.transformation_rule == 'default_scanner_category':
            return self._get_default_scanner_category()
        elif mapping.transformation_rule == 'severity_map':
            # Handle severity mapping
            severity_mapping = self.severity_mappings.get(str(value))
            return severity_mapping['level'] if severity_mapping else 5
        elif mapping.transformation_rule == 'first':
            # Take first item if value is a list or comma-separated
            if isinstance(value, list):
                return value[0] if value else ''
            elif isinstance(value, str) and ',' in value:
                return value.split(',')[0].strip()
            return value
            
        # Handle general transformations
        try:
            context = {
                'value': value,
                'str': str,
                'int': int,
                'float': float,
                'len': len,
                'strip': lambda x: x.strip() if hasattr(x, 'strip') else x,
                'lower': lambda x: x.lower() if hasattr(x, 'lower') else x,
                'upper': lambda x: x.upper() if hasattr(x, 'upper') else x,
                'split': lambda x, sep: x.split(sep) if hasattr(x, 'split') else [x],
                'first': lambda x: x[0] if x and len(x) > 0 else '',
            }
            return eval(mapping.transformation_rule, {"__builtins__": {}}, context)
        except Exception as e:
            logger.warning(f"Transformation error for {mapping.source_field}: {e}")
            return value

    def _convert_value(self, value, field_type):
        """Convert value to the appropriate Python type."""
        if not value and value != 0:
            return None
        try:
            if field_type == 'integer':
                return int(float(value)) if value else 0
            elif field_type == 'decimal':
                return float(value) if value else 0.0
            elif field_type == 'boolean':
                return str(value).lower() in ('true', '1', 'yes', 'on') if value else False
            elif field_type == 'json':
                return json.loads(value) if value else {}
            elif field_type == 'datetime':
                from django.utils.dateparse import parse_datetime
                return parse_datetime(value) if value else None
            else:  # string
                return str(value) if value else ''
        except (ValueError, TypeError, json.JSONDecodeError):
            return None

    def import_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse a Nessus .nessus file and ingest assets, vulnerabilities, and findings using dynamic mapping.
        Returns import statistics.
        """
        logger.info(f"Importing Nessus file: {file_path}")
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
        stats = {'assets': 0, 'vulnerabilities': 0, 'findings': 0, 'errors': []}
        for report_host in self.root.findall('.//ReportHost'):
            try:
                asset = self._process_host(report_host)
                stats['assets'] += 1
                for report_item in report_host.findall('ReportItem'):
                    vuln, finding = self._process_item(report_item, asset)
                    if vuln:
                        stats['vulnerabilities'] += 1
                    if finding:
                        stats['findings'] += 1
            except Exception as e:
                logger.error(f"Error processing host: {e}", exc_info=True)
                stats['errors'].append(f"Error processing host: {str(e)}")
        logger.info(f"Import stats: {stats}")
        return stats

    @transaction.atomic
    def _process_host(self, report_host: ET.Element):
        """
        Process a ReportHost element into an Asset using database field mappings
        with enhanced category/subtype support.
        """
        # Extract host properties
        host_props = {}
        for tag in report_host.findall('.//HostProperties/tag'):
            name = tag.get('name')
            value = tag.text
            if name and value:
                host_props[name] = value
        logger.debug(f"Host properties: {host_props}")
        
        asset_data = {'extra': {}}
        
        # Apply field mappings for assets
        if 'asset' in self.field_mappings:
            for mapping in self.field_mappings['asset']:
                source_value = None
                
                # Get value from host properties or XML attributes
                if mapping.source_field == '':
                    # Empty source field means use transformation only (e.g., default_scanner_category)
                    source_value = ''
                elif mapping.source_field in host_props:
                    source_value = host_props[mapping.source_field]
                elif mapping.source_field == 'HostName':
                    source_value = report_host.get('name')
                
                # Apply transformation if specified
                if source_value is not None or mapping.transformation_rule:
                    transformed_value = self._apply_transformation(source_value, mapping)
                    if transformed_value is not None:
                        source_value = transformed_value
                
                # Convert and assign value
                if source_value or mapping.default_value:
                    final_value = source_value or mapping.default_value
                    converted_value = self._convert_value(final_value, mapping.field_type)
                    
                    if '.' in mapping.target_field:
                        # Handle nested fields like 'extra.os'
                        parts = mapping.target_field.split('.')
                        if parts[0] == 'extra':
                            asset_data['extra'][parts[1]] = converted_value
                    else:
                        asset_data[mapping.target_field] = converted_value
        
        logger.debug(f"Asset data after field mappings: {asset_data}")
        
        # Ensure we have required fields
        if 'category_id' not in asset_data:
            # Fallback to default Host category
            host_category = self._asset_categories.get('Host')
            if host_category:
                asset_data['category_id'] = host_category.category_id
        
        # Get category and subtype objects
        category = None
        subtype = None
        
        if 'category_id' in asset_data:
            try:
                category = AssetCategory.objects.get(category_id=asset_data['category_id'])
            except AssetCategory.DoesNotExist:
                # Fallback to Host category
                category = self._asset_categories.get('Host')
        
        if 'subtype_id' in asset_data and asset_data['subtype_id']:
            try:
                subtype = AssetSubtype.objects.get(subtype_id=asset_data['subtype_id'])
            except AssetSubtype.DoesNotExist:
                subtype = None
        
        # Clean up the data for Asset creation
        asset_data['category'] = category
        asset_data['subtype'] = subtype
        
        # Remove the ID fields as we're using the objects
        asset_data.pop('category_id', None)
        asset_data.pop('subtype_id', None)
        
        # Keep legacy asset_type for backward compatibility during migration
        if not hasattr(asset_data, 'asset_type'):
            try:
                host_asset_type = AssetType.objects.get(name='Host')
                asset_data['asset_type'] = host_asset_type
            except AssetType.DoesNotExist:
                pass
        
        if 'name' not in asset_data:
            asset_data['name'] = asset_data.get('hostname') or asset_data.get('ip_address') or 'Unknown Host'
        
        asset_data['extra']['last_scan'] = timezone.now().isoformat()
        
        # Create or update asset
        defaults = asset_data.copy()
        lookup_fields = {}
        
        # Use hostname and IP for lookup if available
        if asset_data.get('hostname') and asset_data.get('ip_address'):
            lookup_fields['hostname'] = asset_data['hostname']
            lookup_fields['ip_address'] = asset_data['ip_address']
        else:
            # Fallback to name and category
            lookup_fields['name'] = asset_data['name']
            if category:
                lookup_fields['category'] = category
        
        asset, created = Asset.objects.update_or_create(
            **lookup_fields,
            defaults=defaults
        )
        
        logger.info(f"Asset {'created' if created else 'updated'}: {asset}")
        self.created_assets += 1 if created else 0
        return asset

    @transaction.atomic
    def _process_item(self, report_item: ET.Element, asset: Asset):
        """
        Process a ReportItem into Vulnerability and Finding using database field mappings.
        """
        vuln_data = {'extra': {}}
        finding_data = {'asset': asset, 'details': {}}
        # Get severity mapping
        severity_num = report_item.get('severity', '0')
        severity_mapping = self.severity_mappings.get(severity_num, {'label': 'Medium', 'level': 5})
        vuln_data['severity'] = severity_mapping['label']
        vuln_data['severity_label'] = severity_mapping['label']
        vuln_data['severity_level'] = severity_mapping['level']
        # Apply field mappings for vulnerabilities
        if 'vulnerability' in self.field_mappings:
            for mapping in self.field_mappings['vulnerability']:
                source_value = None
                # Handle ReportItem@attribute format
                if '@' in mapping.source_field:
                    # Split on @ to get attribute name
                    parts = mapping.source_field.split('@')
                    if len(parts) == 2 and parts[0] == 'ReportItem':
                        attr_name = parts[1]
                        source_value = report_item.get(attr_name)
                elif mapping.source_field.startswith('@'):
                    attr_name = mapping.source_field[1:]
                    source_value = report_item.get(attr_name)
                else:
                    source_value = self._get_text(report_item, mapping.source_field)
                if source_value:
                    source_value = self._apply_transformation(source_value, mapping)
                if source_value or mapping.default_value:
                    final_value = source_value or mapping.default_value
                    converted_value = self._convert_value(final_value, mapping.field_type)
                    if '.' in mapping.target_field:
                        parts = mapping.target_field.split('.')
                        if parts[0] == 'extra':
                            vuln_data['extra'][parts[1]] = converted_value
                    else:
                        vuln_data[mapping.target_field] = converted_value
        # Apply field mappings for findings
        if 'finding' in self.field_mappings:
            for mapping in self.field_mappings['finding']:
                source_value = None
                # Handle ReportItem@attribute format
                if '@' in mapping.source_field:
                    # Split on @ to get attribute name
                    parts = mapping.source_field.split('@')
                    if len(parts) == 2 and parts[0] == 'ReportItem':
                        attr_name = parts[1]
                        source_value = report_item.get(attr_name)
                elif mapping.source_field.startswith('@'):
                    attr_name = mapping.source_field[1:]
                    source_value = report_item.get(attr_name)
                else:
                    source_value = self._get_text(report_item, mapping.source_field)
                if source_value:
                    source_value = self._apply_transformation(source_value, mapping)
                if source_value or mapping.default_value:
                    final_value = source_value or mapping.default_value
                    converted_value = self._convert_value(final_value, mapping.field_type)
                    if '.' in mapping.target_field:
                        parts = mapping.target_field.split('.')
                        if parts[0] == 'details':
                            finding_data['details'][parts[1]] = converted_value
                    else:
                        finding_data[mapping.target_field] = converted_value
        # Ensure required vulnerability fields
        if 'external_id' not in vuln_data:
            vuln_data['external_id'] = report_item.get('pluginID')
        if 'title' not in vuln_data:
            vuln_data['title'] = report_item.get('pluginName', 'Unknown Vulnerability')
        # Add external source
        vuln_data['external_source'] = self.integration.name
        # Ensure references is always a list (never None)
        if 'references' not in vuln_data or vuln_data['references'] is None:
            vuln_data['references'] = []
        # Ensure cvss is always a dict (never None)
        if 'cvss' not in vuln_data or vuln_data['cvss'] is None:
            vuln_data['cvss'] = {}
        vuln, created = Vulnerability.objects.update_or_create(
            external_source=vuln_data['external_source'],
            external_id=vuln_data['external_id'],
            defaults=vuln_data
        )
        finding_data['vulnerability'] = vuln
        finding_data['integration'] = self.integration
        finding_data['severity_level'] = vuln_data.get('severity_level', 5)
        finding_data['last_seen'] = timezone.now()
        if 'port' in finding_data and finding_data['port']:
            try:
                finding_data['port'] = int(finding_data['port'])
            except (ValueError, TypeError):
                finding_data['port'] = 0
        else:
            finding_data['port'] = 0
        finding, created = Finding.objects.update_or_create(
            asset=asset,
            vulnerability=vuln,
            integration=self.integration,
            port=finding_data.get('port', 0),
            protocol=finding_data.get('protocol', ''),
            service=finding_data.get('service', ''),
            defaults=finding_data
        )
        if not created:
            finding.last_seen = timezone.now()
            finding.save()
        # NOTE: Removed _process_* methods as they modify vuln_data after creation
        # All field processing is handled by field mappings above
        self.created_vulnerabilities += 1 if created else 0
        return vuln, finding

    def _get_text(self, element: ET.Element, tag_name: str) -> str:
        tag = element.find(tag_name)
        return tag.text if tag is not None and tag.text else ''

    # --- Vulnerability references ---
    def _process_references(self, report_item: ET.Element, vuln_data: Dict[str, Any]):
        references = []
        for ref_tag in ['cve', 'bid', 'xref', 'see_also']:
            ref_values = []
            for ref in report_item.findall(ref_tag):
                if ref.text:
                    ref_values.append(ref.text)
            if ref_values:
                vuln_data['references'] = ref_values

    # --- Exploitability info ---
    def _process_exploit(self, report_item: ET.Element, vuln_data: Dict[str, Any]):
        exploit = {}
        for field in ['exploitability_ease', 'exploit_available', 'exploit_framework_canvas', 'exploit_framework_metasploit', 'exploit_framework_core', 'metasploit_name', 'canvas_package']:
            val = self._get_text(report_item, field)
            if val:
                exploit[field] = val
        if exploit:
            vuln_data['exploit'] = exploit

    # --- CVSS info ---
    def _process_cvss(self, report_item: ET.Element, vuln_data: Dict[str, Any]):
        cvss = {}
        for field in ['cvss_vector', 'cvss_temporal_score', 'cvss_temporal_vector']:
            val = self._get_text(report_item, field)
            if val:
                cvss[field] = val
        if cvss:
            vuln_data['cvss'] = cvss

    # --- Dates ---
    def _process_dates(self, report_item: ET.Element, vuln_data: Dict[str, Any]):
        for field, model_field in [
            ('vuln_publication_date', 'published_at'),
            ('plugin_modification_date', 'modified_at'),
            ('plugin_publication_date', 'plugin_publication_date'),
            ('patch_publication_date', 'patch_publication_date')
        ]:
            val = self._get_text(report_item, field)
            if val:
                vuln_data[model_field] = val

    # --- Risk factor ---
    def _process_risk_factor(self, report_item: ET.Element, vuln_data: Dict[str, Any]):
        risk_factor = self._get_text(report_item, 'risk_factor')
        if risk_factor:
            vuln_data['risk_factor'] = risk_factor

    # --- Fallback: store any unmapped fields in metadata ---
    def _process_metadata(self, report_item: ET.Element, vuln_data: Dict[str, Any]):
        for child in report_item:
            tag = child.tag
            if tag not in ['description', 'solution', 'synopsis', 'plugin_output', 'cvss_base_score', 'pluginFamily', 'pluginName', 'pluginID', 'port', 'protocol', 'svc_name', 'severity', 'cve', 'bid', 'xref', 'see_also', 'exploitability_ease', 'exploit_available', 'exploit_framework_canvas', 'exploit_framework_metasploit', 'exploit_framework_core', 'metasploit_name', 'canvas_package', 'cvss_vector', 'cvss_temporal_score', 'cvss_temporal_vector', 'vuln_publication_date', 'plugin_modification_date', 'plugin_publication_date', 'patch_publication_date', 'risk_factor']:
                if child.text:
                    vuln_data.setdefault('extra', {})[tag] = child.text

if __name__ == "__main__":
    # Example usage for local testing
    import sys
    if len(sys.argv) < 2:
        print("Usage: python nessus_scanreport_import.py <nessus_file>")
    else:
        importer = ScannerImporter()
        stats = importer.import_file(sys.argv[1])
        print(stats) 