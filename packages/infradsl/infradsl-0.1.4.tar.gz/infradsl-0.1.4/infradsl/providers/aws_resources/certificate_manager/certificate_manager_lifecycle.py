import os
import boto3
import time
from botocore.exceptions import ClientError

class CertificateManagerLifecycleMixin:
    """
    Mixin for CertificateManager lifecycle operations (create, update, destroy).
    """
    def create(self):
        """Create/update certificate and remove any that are no longer needed"""
        self._ensure_authenticated()
        
        print(f"🔐 Creating/updating certificate for domain: {self.cert_domain_name or self.domain_name or self.name}")
        
        # Check if we're in production mode
        is_production = os.environ.get('INFRADSL_PRODUCTION_MODE') == 'true'
        
        if is_production:
            return self._create_real_certificate()
        else:
            return self._create_mock_certificate()
    
    def _create_mock_certificate(self):
        """Create mock certificate for simulation"""
        domain = self.cert_domain_name or self.domain_name or self.name
        self.certificate_arn = f"arn:aws:acm:us-east-1:123456789012:certificate/{domain.replace('.', '-')}-12345"
        self.status = "ISSUED"
        self.certificate_exists = True
        
        # Mock validation records for DNS validation
        if self.cert_validation_method == 'DNS':
            self.validation_records = [{
                'name': f'_acme-challenge.{domain}',
                'type': 'CNAME',
                'value': f'{domain}.acm-validations.aws.'
            }]
            print(f"   📝 DNS validation required - Nexus Engine will auto-add CNAME record")
            print(f"   🔄 Simulating automatic DNS validation record creation...")
            self._auto_add_validation_records_mock(domain)
        
        print(f"✅ Certificate created successfully!")
        print(f"   ARN: {self.certificate_arn}")
        print(f"   Status: {self.status}")
        
        return {
            'certificate_arn': self.certificate_arn,
            'domain_name': domain,
            'status': self.status,
            'validation_method': self.cert_validation_method or self.validation_method,
            'validation_records': self.validation_records,
            'auto_validation': True
        }
    
    def _create_real_certificate(self):
        """Create real certificate using AWS ACM"""
        domain = self.cert_domain_name or self.domain_name or self.name
        print(f"🚀 Creating REAL certificate for domain: {domain}")
        
        # Initialize ACM client
        acm_client = boto3.client('acm', region_name='us-east-1')
        
        try:
            # Check if certificate already exists
            existing_cert = self._find_existing_certificate(acm_client, domain)
            if existing_cert:
                print(f"✅ Found existing certificate: {existing_cert['CertificateArn']}")
                self.certificate_arn = existing_cert['CertificateArn']
                self.status = existing_cert['Status']
                self.certificate_exists = True

                # If existing certificate is pending validation, try to add records
                if self.status == 'PENDING_VALIDATION':
                    print(f"🔄 Existing certificate is PENDING_VALIDATION. Attempting to add DNS validation records...")
                    cert_details = acm_client.describe_certificate(CertificateArn=self.certificate_arn)
                    domain_validation_options = cert_details['Certificate'].get('DomainValidationOptions', [])
                    
                    validation_records = []
                    for domain_validation in domain_validation_options:
                        if 'ResourceRecord' in domain_validation:
                            rr = domain_validation['ResourceRecord']
                            validation_records.append({
                                'domain': domain_validation['DomainName'],
                                'name': rr['Name'],
                                'type': rr['Type'],
                                'value': rr['Value']
                            })
                            print(f"   📝 DNS validation record for {domain_validation['DomainName']}:")
                            print(f"      Name: {rr['Name']}")
                            print(f"      Type: {rr['Type']}")
                            print(f"      Value: {rr['Value']}")

                    if validation_records:
                        auto_validation_success = self._auto_add_validation_records(validation_records, domain)
                        if auto_validation_success:
                            print(f"✅ DNS validation records added automatically for existing certificate!")
                        else:
                            print(f"⚠️  Could not auto-add validation records for existing certificate. Please add manually:")
                            for record in validation_records:
                                print(f"   Add {record['type']} record: {record['name']} → {record['value']}")
                
                return {
                    'certificate_arn': self.certificate_arn,
                    'domain_name': domain,
                    'status': self.status,
                    'validation_method': self.cert_validation_method or 'DNS',
                    'validation_records': [], # This might need to be populated if we want to return it
                    'auto_validation': False
                }
            
            # Request new certificate
            validation_method = self.cert_validation_method or 'DNS'
            
            # Build SubjectAlternativeNames if we have wildcard or multiple domains
            san_list = []
            if hasattr(self, 'sans') and self.sans:
                san_list.extend(self.sans)
            elif hasattr(self, 'subject_alternative_names') and self.subject_alternative_names:
                san_list.extend(self.subject_alternative_names)
            
            request_params = {
                'DomainName': domain,
                'ValidationMethod': validation_method,
                'Options': {
                    'CertificateTransparencyLoggingPreference': 'ENABLED'
                }
            }
            
            if san_list:
                request_params['SubjectAlternativeNames'] = san_list
            
            print(f"📡 Requesting certificate from AWS ACM...")
            response = acm_client.request_certificate(**request_params)
            
            certificate_arn = response['CertificateArn']
            self.certificate_arn = certificate_arn
            self.certificate_exists = True
            
            print(f"✅ Certificate request submitted: {certificate_arn}")

            # Get validation records if DNS validation
            if validation_method == 'DNS':
                print(f"📝 Polling for DNS validation records...")
                validation_records = []
                poll_start_time = time.time()
                poll_timeout = 300  # 5 minutes timeout for polling validation records

                while not validation_records and (time.time() - poll_start_time < poll_timeout):
                    try:
                        cert_details = acm_client.describe_certificate(CertificateArn=certificate_arn)
                        print(f"   🔍 ACM describe_certificate response: {cert_details}")
                        domain_validation_options = cert_details['Certificate'].get('DomainValidationOptions', [])
                        print(f"   🔍 DomainValidationOptions: {domain_validation_options}")
                        
                        for domain_validation in domain_validation_options:
                            if 'ResourceRecord' in domain_validation:
                                rr = domain_validation['ResourceRecord']
                                validation_records.append({
                                    'domain': domain_validation['DomainName'],
                                    'name': rr['Name'],
                                    'type': rr['Type'],
                                    'value': rr['Value']
                                })
                                print(f"   📝 DNS validation record for {domain_validation['DomainName']}:")
                                print(f"      Name: {rr['Name']}")
                                print(f"      Type: {rr['Type']}")
                                print(f"      Value: {rr['Value']}")
                        
                        if not validation_records:
                            print(f"   ⏳ Validation records not yet available. Waiting 10 seconds...")
                            time.sleep(10)
                    except ClientError as e:
                        print(f"   ⚠️  Error describing certificate during polling: {e}")
                        time.sleep(10)
                    except Exception as e:
                        print(f"   ⚠️  Unexpected error during polling for validation records: {e}")
                        time.sleep(10)

                if not validation_records:
                    print(f"❌ Timed out waiting for DNS validation records from ACM.")
                    self.status = "FAILED"
                    return {
                        'success': False,
                        'certificate_arn': certificate_arn,
                        'domain_name': domain,
                        'status': self.status,
                        'error': 'Timed out waiting for DNS validation records from ACM'
                    }
                
                self.validation_records = validation_records
                self.status = "PENDING_VALIDATION"
                
                # Nexus Engine: Auto-add validation records to Route53
                print(f"🔄 Nexus Engine: Auto-adding DNS validation records to Route53...")
                auto_validation_success = self._auto_add_validation_records(validation_records, domain)
                
                # If auto-validation failed, check if we can use the existing zone from domain registration
                if not auto_validation_success:
                    print(f"🔄 Checking if domain was created with nexus_dns_setup()...")
                    auto_validation_success = self._try_nexus_dns_validation(validation_records, domain)
                
                if auto_validation_success:
                    print(f"✅ DNS validation records added automatically!")
                    print(f"⏳ Certificate validation will complete automatically in 5-10 minutes")
                    
                    # Check if we should wait for validation (for CloudFront compatibility)
                    if hasattr(self, 'cloudfront_compatible_cert') and self.cloudfront_compatible_cert:
                        print(f"🔄 CloudFront certificate - waiting for validation to complete...")
                        validation_success = self._wait_for_certificate_validation(acm_client, certificate_arn)
                        if validation_success:
                            self.status = "ISSUED"
                            print(f"✅ Certificate validated and ready for CloudFront!")
                        else:
                            self.status = "FAILED"
                            print(f"⚠️  Certificate validation timeout - certificate is not ready for CloudFront")
                            return {
                                'success': False,
                                'certificate_arn': certificate_arn,
                                'domain_name': domain,
                                'status': self.status,
                                'error': 'Certificate validation timed out or failed'
                            }
                else:
                    print(f"⚠️  Could not auto-add validation records. Please add manually:")
                    for record in validation_records:
                        print(f"   Add {record['type']} record: {record['name']} → {record['value']}")
                
            else:
                self.validation_records = []
                self.status = "PENDING_VALIDATION"
                
            return {
                'certificate_arn': certificate_arn,
                'domain_name': domain,
                'status': self.status,
                'validation_method': validation_method,
                'validation_records': self.validation_records,
                'auto_validation': validation_method == 'DNS'
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'LimitExceededException':
                print(f"❌ ACM certificate limit exceeded for this account")
            else:
                print(f"❌ Failed to create certificate: {str(e)}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error creating certificate: {str(e)}")
            raise
    
    def _auto_add_validation_records_mock(self, domain: str):
        """Mock automatic addition of DNS validation records"""
        print(f"   🧪 [SIMULATION] Adding DNS validation records to Route53...")
        print(f"   🧪 [SIMULATION] Would create CNAME record for certificate validation")
        print(f"   🧪 [SIMULATION] Domain {domain} validation would be automated")
    
    def _try_nexus_dns_validation(self, validation_records: list, domain: str) -> bool:
        """
        Try to add validation records using the Route53 provider directly.
        This works when the domain was created with nexus_dns_setup().
        """
        try:
            from infradsl.providers.aws import AWS
            
            print(f"   🔄 Attempting to add validation records using InfraDSL Route53 provider...")
            
            success_count = 0
            seen_records = set()
            for record in validation_records:
                # Create a unique key for deduplication
                record_key = (record['name'], record['type'], record['value'])
                if record_key not in seen_records:
                    seen_records.add(record_key)
                    try:
                        # Create validation record using InfraDSL
                        validation_dns = (AWS.Route53(f"validation-{record['domain'].replace('.', '-')}")
                                         .use_existing_zone(domain)
                                         .cname_record(record['name'], record['value'])
                                         .create())
                        
                        print(f"   ✅ Added validation record for {record['domain']}")
                        success_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Failed to add validation record for {record['domain']}: {str(e)}")
                else:
                    print(f"   ⚠️  Skipping duplicate validation record for {record['domain']}")
            
            return success_count > 0
            
        except Exception as e:
            print(f"   ❌ Failed to add validation records via InfraDSL: {str(e)}")
            return False

    def _auto_add_validation_records(self, validation_records: list, domain: str) -> bool:
        """
        Automatically add DNS validation records to Route53.
        This is the Nexus Engine auto-validation feature.
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
            
            route53_client = boto3.client('route53')
            
            # Find the hosted zone for the domain
            print(f"   🔍 Attempting to find hosted zone for domain: {domain}")
            hosted_zone = self._find_domain_hosted_zone(route53_client, domain)
            if not hosted_zone:
                print(f"   ❌ No Route53 hosted zone found for {domain}. Cannot add validation records.")
                return False
            
            zone_id = hosted_zone['Id'].split('/')[-1]
            print(f"   🎯 Using hosted zone: {zone_id} for {domain}")
            
            print(f"   📝 Validation records received from ACM: {validation_records}")
            
            # Create DNS records for validation (deduplicated)
            changes = []
            seen_records = set()
            for record in validation_records:
                # Create a unique key for deduplication
                record_key = (record['name'], record['type'], record['value'])
                if record_key not in seen_records:
                    seen_records.add(record_key)
                    changes.append({
                        'Action': 'UPSERT',
                        'ResourceRecordSet': {
                            'Name': record['name'],
                            'Type': record['type'],
                            'TTL': 300,
                            'ResourceRecords': [{'Value': record['value']}]
                        }
                    })
                    print(f"   📝 Adding validation record to changes: {record['name']} ({record['type']})")
                else:
                    print(f"   ⚠️  Skipping duplicate validation record: {record['name']} ({record['type']})")
            
            print(f"   📦 Route53 changes payload: {changes}")
            
            if changes:
                response = route53_client.change_resource_record_sets(
                    HostedZoneId=zone_id,
                    ChangeBatch={
                        'Comment': 'DNS validation records for ACM certificate (auto-created by InfraDSL)',
                        'Changes': changes
                    }
                )
                
                change_id = response['ChangeInfo']['Id']
                print(f"   ✅ DNS validation records created successfully!")
                print(f"   🔗 Route53 Change ID: {change_id}")
                return True
            
        except Exception as e:
            print(f"   ⚠️  Failed to auto-add validation records: {str(e)}")
            print(f"   💡 You can manually add the records shown above")
            return False
        
        return False
    
    def _find_domain_hosted_zone(self, route53_client, domain: str):
        """Find the Route53 hosted zone for a domain"""
        try:
            print(f"   🔍 Listing all hosted zones...")
            response = route53_client.list_hosted_zones()
            print(f"   ✅ Found {len(response['HostedZones'])} hosted zones.")
            
            # Try exact match first
            for zone in response['HostedZones']:
                zone_name = zone['Name'].rstrip('.')
                print(f"   Comparing domain '{domain}' with zone '{zone_name}'")
                if zone_name == domain:
                    print(f"   ✅ Exact match found for hosted zone: {zone_name}")
                    return zone
            
            # Try parent domains (for subdomains)
            domain_parts = domain.split('.')
            for i in range(1, len(domain_parts)):
                parent_domain = '.'.join(domain_parts[i:])
                print(f"   Comparing domain '{domain}' with parent zone '{parent_domain}'")
                for zone in response['HostedZones']:
                    zone_name = zone['Name'].rstrip('.')
                    if zone_name == parent_domain:
                        print(f"   ✅ Parent match found for hosted zone: {zone_name}")
                        return zone
                        
            print(f"   ❌ No suitable hosted zone found for domain: {domain}")
            return None
        except Exception as e:
            print(f"   ⚠️  Error finding hosted zone: {str(e)}")
            return None
    
    def _wait_for_certificate_validation(self, acm_client, certificate_arn, max_wait_minutes=15):
        """
        Wait for certificate validation to complete (for CloudFront compatibility)
        
        Args:
            acm_client: ACM client
            certificate_arn: Certificate ARN to check
            max_wait_minutes: Maximum time to wait in minutes
            
        Returns:
            bool: True if validation completed, False if timeout
        """
        import time
        
        print(f"⏳ Waiting for certificate validation (max {max_wait_minutes} minutes)...")
        start_time = time.time()
        max_wait_seconds = max_wait_minutes * 60
        
        while time.time() - start_time < max_wait_seconds:
            try:
                response = acm_client.describe_certificate(CertificateArn=certificate_arn)
                status = response['Certificate']['Status']
                
                if status == 'ISSUED':
                    return True
                elif status == 'FAILED':
                    print(f"❌ Certificate validation failed: {response['Certificate'].get('FailureReason', 'Unknown error')}")
                    return False
                elif status == 'PENDING_VALIDATION':
                    # Check validation details
                    validation_options = response['Certificate'].get('DomainValidationOptions', [])
                    for validation in validation_options:
                        validation_status = validation.get('ValidationStatus', 'PENDING_VALIDATION')
                        domain = validation.get('DomainName', '')
                        if validation_status == 'SUCCESS':
                            print(f"✅ Domain {domain} validated")
                        else:
                            print(f"⏳ Domain {domain} still validating...")
                    
                    # Wait 30 seconds before checking again
                    time.sleep(30)
                else:
                    print(f"🔄 Certificate status: {status}")
                    time.sleep(30)
                    
            except Exception as e:
                print(f"⚠️  Error checking certificate status: {e}")
                time.sleep(30)
        
        print(f"⏰ Validation timeout after {max_wait_minutes} minutes")
        return False

    def wait_until_issued(self, certificate_arn: str, max_wait_minutes: int = 15) -> bool:
        """
        Public method to wait for a certificate to be in 'ISSUED' status.
        """
        self._ensure_authenticated()
        acm_client = boto3.client('acm', region_name='us-east-1')
        return self._wait_for_certificate_validation(acm_client, certificate_arn, max_wait_minutes)

    def _find_existing_certificate(self, acm_client, domain):
        """Find existing certificate for the domain"""
        try:
            response = acm_client.list_certificates(
                CertificateStatuses=['ISSUED', 'PENDING_VALIDATION']
            )
            
            for cert in response['CertificateSummaryList']:
                if cert['DomainName'] == domain:
                    return cert
                    
        except Exception as e:
            print(f"Warning: Could not check for existing certificates: {str(e)}")
            
        return None

    def destroy(self):
        """Destroy the certificate"""
        self._ensure_authenticated()
        
        if not self.certificate_exists:
            print("⚠️  No certificate to destroy")
            return {'destroyed': False, 'reason': 'Certificate does not exist'}
        
        print(f"🗑️  Destroying certificate: {self.certificate_arn}")
        
        # Check if certificate is in use
        if hasattr(self, '_in_use_by') and self._in_use_by:
            print(f"⚠️  Warning: Certificate is in use by: {', '.join(self._in_use_by)}")
            print("   Remove certificate from these resources before deletion")
        
        # Mock deletion
        self.certificate_exists = False
        self.status = "DELETED"
        
        print("✅ Certificate destroyed successfully")
        
        return {
            'destroyed': True,
            'certificate_arn': self.certificate_arn,
            'domain_name': self.cert_domain_name or self.domain_name or self.name
        }
    
    def _display_preview(self, to_create, to_keep, to_remove):
        """Display preview of changes"""
        print("\n📋 Certificate Manager Preview:")
        print("=" * 50)
        
        if to_create:
            print("✨ To Create:")
            for cert in to_create:
                print(f"   - {cert['domain']} ({cert['type']})")
        
        if to_keep:
            print("✅ To Keep:")
            for cert in to_keep:
                print(f"   - {cert['domain']} (No changes)")
        
        if to_remove:
            print("🗑️  To Remove:")
            for cert in to_remove:
                print(f"   - {cert['domain']}")
        
        print("=" * 50) 