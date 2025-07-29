import os
from typing import Dict, Any, List, Optional

class Route53LifecycleMixin:
    """
    Mixin for Route53 hosted zone and record lifecycle operations (create, update, destroy).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""
        self._ensure_authenticated()
        
        # Mock discovery for now - in real implementation this would use the manager
        existing_zones = {}  # self.route53_manager.discover_existing_zones()
        
        # Determine desired state
        desired_zone_name = self.domain_name or self.name
        
        # Categorize zones
        to_create = []
        to_keep = []
        to_remove = []
        
        # Check if our desired zone exists or if we're using existing zone
        zone_exists = desired_zone_name in existing_zones or getattr(self, 'use_existing', False)
        
        if getattr(self, 'use_existing', False):
            # Using existing zone - show what will be updated
            to_keep.append({
                'name': desired_zone_name,
                'type': self.zone_type,
                'status': 'EXISTING (from domain registration)',
                'id': f"Z{desired_zone_name.replace('.', '').upper()}123456789",
                'records_to_add': len(self.records),
                'note': 'Using hosted zone created by domain registration'
            })
        elif not zone_exists:
            to_create.append({
                'name': desired_zone_name,
                'type': self.zone_type,
                'records_count': len(self.records)
            })
        else:
            to_keep.append(existing_zones[desired_zone_name])
        
        self._display_preview(to_create, to_keep, to_remove)
        
        return {
            'resource_type': 'aws_route53',
            'name': desired_zone_name,
            'zone_id': f"Z{self.name.upper()}123456789",  # Mock zone ID for preview
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_zones': existing_zones,
            'zone_type': self.zone_type,
            'records_count': len(self.records),
            'estimated_deployment_time': '1-2 minutes'
        }
    
    def _display_preview(self, to_create: List[Dict], to_keep: List[Dict], to_remove: List[Dict]):
        """Display preview information in a clean format"""
        print(f"\n🌐 Route53 DNS Preview")
        
        # Show zones to create
        if to_create:
            print(f"╭─ 📦 Zones to CREATE: {len(to_create)}")
            for zone in to_create:
                print(f"├─ 🆕 {zone['name']}")
                print(f"│  ├─ 🏷️  Type: {zone['type']}")
                print(f"│  ├─ 📝 Records: {zone['records_count']}")
                print(f"│  └─ ⏱️  Deployment Time: 1-2 minutes")
            print(f"╰─")
        
        # Show zones to keep/update
        if to_keep:
            print(f"╭─ 🔄 Zones to UPDATE: {len(to_keep)}")
            for zone in to_keep:
                print(f"├─ ✅ {zone.get('name', 'Unknown')}")
                print(f"│  ├─ 🆔 Zone ID: {zone.get('id', 'Unknown')}")
                print(f"│  ├─ 📊 Status: {zone.get('status', 'Active')}")
                if 'records_to_add' in zone:
                    print(f"│  ├─ 📝 Records to Add: {zone['records_to_add']}")
                    
                    # Show detailed DNS records
                    if hasattr(self, 'records') and self.records:
                        print(f"│  ├─ 🌐 DNS Records:")
                        for i, record in enumerate(self.records):
                            record_name = record.get('name', '@')
                            record_type = record.get('type', 'UNKNOWN')
                            record_value = record.get('value', record.get('alias_target', {}).get('DNSName', 'Unknown'))
                            
                            # Format the record display
                            if record_name == '@':
                                display_name = f"{self.domain_name} (root)"
                            elif '.' not in record_name:
                                display_name = f"{record_name}.{self.domain_name}"
                            else:
                                display_name = record_name
                            
                            # Show record with appropriate icon
                            if record_type == 'CNAME':
                                icon = "🔗"
                            elif record_type == 'A':
                                icon = "🏠" if record.get('is_alias') else "📍"
                            elif record_type == 'MX':
                                icon = "📧"
                            else:
                                icon = "📝"
                            
                            # Determine if this is the last record
                            is_last_record = i == len(self.records) - 1
                            connector = "└─" if is_last_record else "├─"
                            
                            print(f"│  │  {connector} {icon} {display_name} ({record_type}) → {record_value}")
                
                if 'note' in zone:
                    print(f"│  └─ 💡 {zone['note']}")
                else:
                    print(f"│  └─ 📊 Current Records: {zone.get('records_count', 0)}")
            print(f"╰─")
        
        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        print(f"   ├─ 🌐 Hosted Zone: $0.50 per month")
        print(f"   ├─ 📝 DNS Queries: $0.40 per million queries")
        print(f"   └─ 🔗 Health Checks: $0.50 per health check per month")
    
    def create(self) -> Dict[str, Any]:
        """Create/update Route53 hosted zone and records"""
        self._ensure_authenticated()
        
        desired_zone_name = self.domain_name or self.name
        
        # Check if we're in production mode
        is_production = os.environ.get('INFRADSL_PRODUCTION_MODE') == 'true'
        
        if is_production:
            return self._create_real_route53_zone(desired_zone_name)
        else:
            return self._create_mock_route53_zone(desired_zone_name)
    
    def _create_real_route53_zone(self, desired_zone_name: str) -> Dict[str, Any]:
        """Create/update Route53 hosted zone using real AWS API"""
        print(f"\n🚀 Processing Route53 Zone (PRODUCTION): {desired_zone_name}")
        
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            route53_client = boto3.client('route53')
            
            # Check if we should use existing zone
            if getattr(self, 'use_existing', False):
                print(f"🔍 Looking for existing hosted zone: {desired_zone_name}")
                
                # Find existing zone
                existing_zone = self._find_existing_zone(route53_client, desired_zone_name)
                if existing_zone:
                    print(f"✅ Found existing hosted zone: {existing_zone['Id']}")
                    self.hosted_zone_id = existing_zone['Id'].split('/')[-1]
                    self.zone_exists = True
                    
                    # Create records in existing zone
                    records_result = self._create_records_in_zone(route53_client, self.hosted_zone_id)
                    
                    return {
                        'zone_id': self.hosted_zone_id,
                        'zone_name': desired_zone_name,
                        'zone_type': self.zone_type,
                        'name_servers': existing_zone.get('NameServers', []),
                        'records_count': len(self.records),
                        'status': 'Updated',
                        'created': False,
                        'used_existing': True,
                        'records_created': records_result.get('records_created', 0)
                    }
                else:
                    print(f"⚠️  Existing zone not found for {desired_zone_name}")
                    print("   Creating new zone instead...")
            
            # Create new zone if not using existing or existing not found
            print(f"📦 Creating new hosted zone: {desired_zone_name}")
            
            caller_reference = f"infradsl-{desired_zone_name}-{int(__import__('time').time())}"
            
            response = route53_client.create_hosted_zone(
                Name=desired_zone_name,
                CallerReference=caller_reference,
                HostedZoneConfig={
                    'Comment': f'Created by InfraDSL for {desired_zone_name}',
                    'PrivateZone': self.zone_type == 'private'
                }
            )
            
            zone_id = response['HostedZone']['Id'].split('/')[-1]
            name_servers = response['DelegationSet']['NameServers']
            
            self.hosted_zone_id = zone_id
            self.zone_exists = True
            
            print(f"✅ Hosted zone created: {zone_id}")
            
            # Create records in the new zone
            records_result = self._create_records_in_zone(route53_client, zone_id)
            
            final_result = {
                'zone_id': zone_id,
                'zone_name': desired_zone_name,
                'zone_type': self.zone_type,
                'name_servers': name_servers,
                'records_count': len(self.records),
                'status': 'Active',
                'created': True,
                'used_existing': False,
                'records_created': records_result.get('records_created', 0)
            }
            
            self._display_creation_success(final_result)
            return final_result
            
        except Exception as e:
            print(f"❌ Failed to create Route53 Hosted Zone: {str(e)}")
            raise
    
    def _create_mock_route53_zone(self, desired_zone_name: str) -> Dict[str, Any]:
        """Create mock Route53 hosted zone for simulation"""
        print(f"\n🧪 Processing Route53 Zone (SIMULATION): {desired_zone_name}")
        
        # Check if we should use existing zone
        if getattr(self, 'use_existing', False):
            print(f"✅ Using existing hosted zone: {desired_zone_name}")
            print("   (In production, this would find the real zone)")
            
            zone_id = f"Z{desired_zone_name.replace('.', '').upper()}EXISTING"
            self.hosted_zone_id = zone_id
            self.zone_exists = True
            
            return {
                'zone_id': zone_id,
                'zone_name': desired_zone_name,
                'zone_type': self.zone_type,
                'name_servers': [
                    'ns-1234.awsdns-12.com',
                    'ns-567.awsdns-34.net',
                    'ns-890.awsdns-56.org',
                    'ns-123.awsdns-78.co.uk'
                ],
                'records_count': len(self.records),
                'status': 'Active (Existing)',
                'created': False,
                'used_existing': True,
                'records_created': len(self.records)
            }
        
        # Mock creation of new zone
        try:
            # Process records to handle both regular and ALIAS records
            processed_records = []
            for record in self.records:
                if record.get('is_alias'):
                    processed_records.append({
                        'name': record['name'],
                        'type': 'A (ALIAS)',
                        'target': record['alias_target']['DNSName']
                    })
                else:
                    processed_records.append({
                        'name': record['name'],
                        'type': record['type'],
                        'value': record['value']
                    })
            
            result = {
                'zone_id': f"Z{self.name.upper()}123456789",
                'zone_name': desired_zone_name,
                'zone_type': self.zone_type,
                'name_servers': [
                    'ns-1234.awsdns-12.com',
                    'ns-567.awsdns-34.net',
                    'ns-890.awsdns-56.org',
                    'ns-123.awsdns-78.co.uk'
                ],
                'records_created': len(self.records),
                'records': processed_records,
                'status': 'Active'
            }
            
            self.hosted_zone_id = result['zone_id']
            self.zone_exists = True
            
            final_result = {
                'zone_id': result['zone_id'],
                'zone_name': desired_zone_name,
                'zone_type': self.zone_type,
                'name_servers': result['name_servers'],
                'records_count': len(self.records),
                'status': result['status'],
                'created': True
            }
            
            self._display_creation_success(final_result)
            return final_result
            
        except Exception as e:
            print(f"❌ Failed to create Route53 Hosted Zone: {str(e)}")
            raise
    
    def _find_existing_zone(self, route53_client, domain_name: str):
        """Find existing hosted zone for the domain"""
        try:
            response = route53_client.list_hosted_zones()
            
            for zone in response['HostedZones']:
                zone_name = zone['Name'].rstrip('.')
                if zone_name == domain_name:
                    return zone
                    
        except Exception as e:
            print(f"Warning: Could not check for existing zones: {str(e)}")
            
        return None
    
    def _create_records_in_zone(self, route53_client, zone_id: str) -> Dict[str, Any]:
        """Create DNS records in the specified zone"""
        if not self.records:
            return {'records_created': 0}
        
        try:
            changes = []
            
            for record in self.records:
                # Format the record name properly
                record_name = record['name']
                zone = self.domain_name or self.name
                
                # Handle special cases
                if record_name == '@':
                    # @ means the apex/root domain
                    formatted_name = zone
                elif '.' not in record_name and not record_name.endswith('.'):
                    # It's a subdomain without the zone suffix
                    formatted_name = f"{record_name}.{zone}"
                else:
                    # Already has proper formatting or is a full domain
                    formatted_name = record_name
                
                # Ensure the name ends with a dot for Route53 API
                if not formatted_name.endswith('.'):
                    formatted_name += '.'
                
                if record.get('is_alias'):
                    # ALIAS record
                    changes.append({
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': formatted_name,
                            'Type': 'A',
                            'AliasTarget': record['alias_target']
                        }
                    })
                else:
                    # Regular record - handle both single value and multiple values
                    if 'values' in record:
                        # Multiple values (e.g., load balancer IPs)
                        resource_records = [{'Value': value} for value in record['values']]
                    else:
                        # Single value
                        resource_records = [{'Value': record['value']}]
                    
                    changes.append({
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': formatted_name,
                            'Type': record['type'],
                            'TTL': record.get('ttl', 300),
                            'ResourceRecords': resource_records
                        }
                    })
            
            if changes:
                response = route53_client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch={
                        'Comment': 'Created by InfraDSL',
                        'Changes': changes
                    }
                )
                
                print(f"✅ Created {len(changes)} DNS records")
                return {'records_created': len(changes), 'change_id': response['ChangeInfo']['Id']}
            
        except Exception as e:
            print(f"⚠️  Failed to create some DNS records: {str(e)}")
            return {'records_created': 0, 'error': str(e)}
        
        return {'records_created': 0}
    
    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ Route53 Hosted Zone created successfully")
        print(f"   📋 Zone ID: {result['zone_id']}")
        print(f"   🌐 Zone Name: {result['zone_name']}")
        print(f"   🏷️  Type: {result['zone_type']}")
        print(f"   📝 Records: {result['records_count']}")
        print(f"   📊 Status: {result['status']}")
        print(f"   🔗 Name Servers:")
        for ns in result['name_servers']:
            print(f"      - {ns}")
    
    def destroy(self) -> Dict[str, Any]:
        """Destroy the Route53 hosted zone and records"""
        self._ensure_authenticated()
        
        print(f"🗑️ Destroying Route53 Hosted Zone: {self.domain_name or self.name}")
        
        try:
            # Mock destruction for now - in real implementation this would use the manager
            result = {
                'zone_id': self.hosted_zone_id,
                'zone_name': self.domain_name or self.name,
                'status': 'Deleted',
                'deleted': True
            }
            
            self.hosted_zone_id = None
            self.zone_exists = False
            
            print(f"✅ Route53 Hosted Zone destruction completed")
            return result
            
        except Exception as e:
            print(f"❌ Failed to destroy Route53 Hosted Zone: {str(e)}")
            raise 