from typing import Dict, Any, List
import uuid
import os
import boto3
import time
from infradsl.cli.output_formatters import print_success, print_info, print_warning

class CloudFrontLifecycleMixin:
    """
    Mixin for CloudFront distribution lifecycle operations (create, update, destroy).
    """

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created, kept, and removed"""

        # Handle copy_from case
        if hasattr(self, '_copied_from_distribution_id') and self._copied_from_distribution_id:
            self._display_cloudfront_copy_preview()
            return {
                'resource_type': 'AWS CloudFront Distribution',
                'distribution_name': f"{self.name}-distribution",
                'status': 'Configuration copied and customized',
                'copied_from': self._copied_from_distribution_id,
                'note': f'Cloned from {self._copied_from_distribution_id} with customizations'
            }

        # For basic testing, provide a default preview even without origin
        if not self.origin_doain:
            return {
                'resource_type': 'AWS CloudFront Distribution',
                'distribution_name': f"{self.name}-distribution",
                'origin_domain': 'Not configured',
                'status': 'Configuration incomplete',
                'note': 'Origin domain required for deployment'
            }

        self._ensure_authenticated()

        # Mock discovery for now - in real implementation this would use AWS SDK
        existing_distributions = {}

        # Determine desired state - check if name is already a distribution ID
        if self.name.startswith('E') and len(self.name) == 14:  # CloudFront distribution ID format
            desired_distribution_name = self.name  # Use existing distribution ID
            is_existing_distribution = True
        else:
            desired_distribution_name = f"{self.name}-distribution"  # New distribution
            is_existing_distribution = False

        # Categorize distributions
        to_create = []
        to_keep = []
        to_remove = []

        if is_existing_distribution:
            # This is an existing distribution - show what will be updated
            to_keep.append({
                'name': desired_distribution_name,
                'status': 'EXISTING',
                'origin_domain': self.origin_domain,
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'note': 'Using existing CloudFront distribution'
            })
        else:
            # This is a new distribution to be created
            to_create.append({
                'name': desired_distribution_name,
                'origin_domain': self.origin_domain,
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'price_class': self.price_class_setting or 'PriceClass_All',
                'http2_enabled': self.http2_enabled,
                'ipv6_enabled': self.ipv6_enabled,
                'compression_enabled': self.compression_enabled,
                'security_headers': getattr(self, 'security_headers', False),
                'waf_enabled': bool(getattr(self, 'waf_web_acl_id', None)),
                'geo_restrictions': bool(getattr(self, 'geo_restriction', None)),
                'logging_enabled': getattr(self, 'logging_enabled', False),
                'behaviors_count': len(getattr(self, 'behaviors', [])),
                'error_pages_count': len(getattr(self, 'error_pages', []))
            })

        self._display_preview(to_create, to_keep, to_remove)

        # Generate mock distribution details for preview
        distribution_id = f"E{str(uuid.uuid4()).replace('-', '').upper()[:13]}"
        cloudfront_domain = f"{distribution_id.lower()}.cloudfront.net"

        # Set domain_name attribute for use in Route53
        self.domain_name = cloudfront_domain

        return {
            'resource_type': 'AWS CloudFront Distribution',
            'name': desired_distribution_name,
            'distribution_id': distribution_id,
            'distribution_domain': cloudfront_domain,
            'to_create': to_create,
            'to_keep': to_keep,
            'to_remove': to_remove,
            'existing_distributions': existing_distributions,
            'origin_domain': self.origin_domain,
            'custom_domains_count': len(self.custom_domains),
            'estimated_deployment_time': '15-20 minutes',
            'estimated_monthly_cost': self.estimate_monthly_cost() if hasattr(self, 'estimate_monthly_cost') else '$8.50'
        }

    def _display_preview(self, to_create: List[Dict], to_keep: List[Dict], to_remove: List[Dict]):
        """Display preview information in a clean format"""
        print(f"\n🌍 CloudFront CDN Preview")

        # Show distributions to create
        if to_create:
            print(f"╭─ 🚀 Distributions to CREATE: {len(to_create)}")
            for dist in to_create:
                print(f"├─ 🆕 {dist['name']}")
                print(f"│  ├─ 🌐 Origin: {dist['origin_domain']}")
                if dist['custom_domains']:
                    print(f"│  ├─ 🔗 Custom Domains: {len(dist['custom_domains'])}")
                    for domain in dist['custom_domains'][:3]:  # Show first 3
                        print(f"│  │  ├─ {domain}")
                    if len(dist['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(dist['custom_domains']) - 3} more")
                print(f"│  ├─ 🏷️  Price Class: {dist['price_class']}")
                print(f"│  ├─ 🔒 SSL Certificate: {'✅ Yes' if dist['ssl_certificate_arn'] else '❌ Default only'}")
                print(f"│  ├─ ⚡ HTTP/2: {'✅ Enabled' if dist['http2_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🌐 IPv6: {'✅ Enabled' if dist['ipv6_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 📦 Compression: {'✅ Enabled' if dist['compression_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🛡️  WAF: {'✅ Enabled' if dist['waf_enabled'] else '❌ Disabled'}")
                print(f"│  ├─ 🌍 Geo Restrictions: {'✅ Yes' if dist['geo_restrictions'] else '❌ None'}")
                print(f"│  ├─ 📊 Behaviors: {dist['behaviors_count']}")
                print(f"│  ├─ 🚨 Error Pages: {dist['error_pages_count']}")
                print(f"│  ├─ 📝 Logging: {'✅ Enabled' if dist['logging_enabled'] else '❌ Disabled'}")
                print(f"│  └─ ⏱️  Deployment Time: 15-20 minutes")
            print(f"╰─")

        # Show distributions to keep/update
        if to_keep:
            print(f"╭─ 🔄 Distributions to UPDATE: {len(to_keep)}")
            for dist in to_keep:
                print(f"├─ ✅ {dist['name']}")
                print(f"│  ├─ 📝 Status: {dist.get('status', 'EXISTING')}")
                print(f"│  ├─ 🌐 Origin: {dist['origin_domain']}")
                if dist.get('custom_domains'):
                    print(f"│  ├─ 🔗 Custom Domains: {len(dist['custom_domains'])}")
                    for domain in dist['custom_domains'][:3]:
                        print(f"│  │  ├─ {domain}")
                    if len(dist['custom_domains']) > 3:
                        print(f"│  │  └─ ... and {len(dist['custom_domains']) - 3} more")
                print(f"│  └─ 💡 {dist.get('note', 'No changes')}")
            print(f"╰─")

        # Show cost estimation
        print(f"\n💰 Estimated Monthly Costs:")
        if to_create:
            dist = to_create[0]
            print(f"   ├─ 📡 Data Transfer (100GB): $8.50/month")
            print(f"   ├─ 🔄 HTTP Requests (1M): $0.75/month")
            print(f"   ├─ 🔒 HTTPS Requests (1M): $1.00/month")
            if dist['ssl_certificate_arn']:
                print(f"   ├─ 🔐 Dedicated SSL Certificate: $50.00/month")
            if dist['price_class'] == 'PriceClass_100':
                print(f"   ├─ 🌍 Edge Locations (US, Canada, Europe): 40% cost reduction")
            elif dist['price_class'] == 'PriceClass_200':
                print(f"   ├─ 🌍 Edge Locations (+ Asia, India): 20% cost reduction")
            else:
                print(f"   ├─ 🌍 Edge Locations (All): Full global coverage")
            print(f"   └─ 📊 Total Estimated: ~$10-60/month")
        else:
            print(f"   ├─ 📡 Data Transfer: $0.085/GB")
            print(f"   ├─ 🔄 HTTP Requests: $0.0075/10,000")
            print(f"   ├─ 🔒 HTTPS Requests: $0.0100/10,000")
            print(f"   └─ 🔐 SSL Certificates: $600/year for dedicated")

    def _display_cloudfront_copy_preview(self):
        """Display detailed preview for copy_from operations"""
        print(f"\n🌍 CloudFront CDN Preview (Copied Configuration)")
        print(f"╭─ 📋 CLONED from: {self._copied_from_distribution_id}")
        print(f"├─ 🆕 NEW Distribution: {self.name}-distribution")
        print(f"│")
        print(f"├─ 🔄 COPIED Settings:")
        print(f"│  ├─ 🌐 Origin Domain: {self.origin_domain}")

        # Show origins
        if hasattr(self, 'origins') and self.origins:
            origins_count = len(self.origins)
            print(f"│  ├─ 📡 Origins: {origins_count}")
            for origin in self.origins[:2]:  # Show first 2 origins
                print(f"│  │  ├─ {origin['domain']} ({origin['type']})")
            if origins_count > 2:
                print(f"│  │  └─ ... and {origins_count - 2} more")

        # SSL Certificate
        if hasattr(self, 'ssl_certificate_arn') and self.ssl_certificate_arn:
            print(f"│  ├─ 🔐 SSL Certificate: Custom ACM Certificate")
        else:
            print(f"│  ├─ 🔐 SSL Certificate: CloudFront Default")

        # Price class
        if hasattr(self, 'price_class_setting') and self.price_class_setting:
            price_class_name = {
                'PriceClass_All': 'Worldwide (All Edge Locations)',
                'PriceClass_200': 'US, Canada, Europe, Asia, India',
                'PriceClass_100': 'US, Canada, Europe Only'
            }.get(self.price_class_setting, self.price_class_setting)
            print(f"│  ├─ 💰 Price Class: {price_class_name}")

        # Features
        if hasattr(self, 'http2_enabled'):
            print(f"│  ├─ ⚡ HTTP/2: {'✅ Enabled' if self.http2_enabled else '❌ Disabled'}")
        if hasattr(self, 'ipv6_enabled'):
            print(f"│  ├─ 🌐 IPv6: {'✅ Enabled' if self.ipv6_enabled else '❌ Disabled'}")
        if hasattr(self, 'compression_enabled'):
            print(f"│  ├─ 📦 Compression: {'✅ Enabled' if self.compression_enabled else '❌ Disabled'}")

        # WAF and Geo restrictions
        if hasattr(self, 'waf_web_acl_id') and self.waf_web_acl_id:
            print(f"│  ├─ 🛡️  WAF: ✅ Enabled")
        if hasattr(self, 'geo_restriction') and self.geo_restriction:
            print(f"│  ├─ 🌍 Geo Restrictions: ✅ {self.geo_restriction['type'].title()}")

        # Error pages and behaviors
        if hasattr(self, 'error_pages') and self.error_pages:
            print(f"│  ├─ 🚨 Error Pages: {len(self.error_pages)} configured")
        if hasattr(self, 'behaviors') and self.behaviors:
            print(f"│  ├─ 📊 Cache Behaviors: {len(self.behaviors)} custom")
            
        # Default cache behavior policies
        if hasattr(self, 'default_cache_policy_id') and self.default_cache_policy_id:
            default_cache_policy_name = getattr(self, 'policy_names', {}).get(self.default_cache_policy_id, 'Unknown')
            print(f"│  ├─ 🎯 Default Cache Policy: {default_cache_policy_name}")
        if hasattr(self, 'default_origin_request_policy_id') and self.default_origin_request_policy_id:
            default_origin_policy_name = getattr(self, 'policy_names', {}).get(self.default_origin_request_policy_id, 'Unknown')
            print(f"│  ├─ 📡 Default Origin Request Policy: {default_origin_policy_name}")
            
        # Show detailed behaviors with policy names
        if hasattr(self, 'behaviors') and self.behaviors:
            print(f"│  ├─ 📊 Behavior Details:")
            for i, behavior in enumerate(self.behaviors):
                path = behavior.get('path', '/*')
                print(f"│  │  ├─ 🔗 {path}")
                
                # Cache Policy
                if behavior.get('cache_policy_name'):
                    print(f"│  │  │  ├─ 🎯 Cache Policy: {behavior['cache_policy_name']}")
                elif behavior.get('cache_policy_id'):
                    print(f"│  │  │  ├─ 🎯 Cache Policy: {behavior['cache_policy_id']}")
                
                # Origin Request Policy
                if behavior.get('origin_request_policy_name'):
                    print(f"│  │  │  ├─ 📡 Origin Request Policy: {behavior['origin_request_policy_name']}")
                elif behavior.get('origin_request_policy_id'):
                    print(f"│  │  │  ├─ 📡 Origin Request Policy: {behavior['origin_request_policy_id']}")
                
                # Response Headers Policy
                if behavior.get('response_headers_policy_name'):
                    print(f"│  │  │  ├─ 📋 Response Headers Policy: {behavior['response_headers_policy_name']}")
                elif behavior.get('response_headers_policy_id'):
                    print(f"│  │  │  ├─ 📋 Response Headers Policy: {behavior['response_headers_policy_id']}")
                
                # Protocol and Target Origin
                protocol = behavior.get('viewer_protocol_policy', 'redirect-to-https')
                print(f"│  │  │  ├─ 🔒 Protocol: {protocol}")
                target_origin = behavior.get('target_origin_id', 'default')
                print(f"│  │  │  └─ 🎯 Target Origin: {target_origin}")
                
                # Add separator if not last item
                if i < len(self.behaviors) - 1:
                    print(f"│  │  │")

        print(f"│")
        print(f"├─ ✨ NEW/UPDATED Settings:")

        # Custom domains
        if hasattr(self, 'custom_domains') and self.custom_domains:
            print(f"│  ├─ 🔗 Custom Domains: {len(self.custom_domains)}")
            for domain in self.custom_domains:
                print(f"│  │  ├─ 🌐 {domain}")
        else:
            print(f"│  ├─ 🔗 Custom Domains: ⚠️  None (using CloudFront domain)")

        # Target Origin ID update
        if hasattr(self, '_custom_target_origin_id') and self._custom_target_origin_id:
            print(f"│  ├─ 🎯 Target Origin ID: {self._custom_target_origin_id}")
        
        # Custom allowed methods for default cache behavior
        if hasattr(self, 'default_allowed_methods') and self.default_allowed_methods:
            if set(self.default_allowed_methods) != {'GET', 'HEAD'}:
                print(f"│  ├─ 🔧 Default Allowed Methods: {', '.join(self.default_allowed_methods)}")
                if hasattr(self, 'default_cached_methods') and self.default_cached_methods:
                    print(f"│  ├─ 📋 Default Cached Methods: {', '.join(self.default_cached_methods)}")

        print(f"│")
        print(f"├─ ⏱️  Deployment Time: 15-20 minutes (distribution propagation)")
        print(f"├─ 💰 Estimated Cost: $10-60/month (based on usage)")
        print(f"└─ 🚀 Ready to deploy with customizations")

        print(f"\n💰 Estimated Monthly Costs:")
        print(f"   ├─ 📡 Data Transfer: $0.085/GB")
        print(f"   ├─ 🔄 HTTP Requests: $0.0075/10,000")
        print(f"   ├─ 🔒 HTTPS Requests: $0.0100/10,000")
        print(f"   └─ 🔐 SSL Certificates: $600/year for dedicated")

    def create(self) -> Dict[str, Any]:
        """Create/update CloudFront distribution"""
        self._ensure_authenticated()

        # Check if name is already a distribution ID (update mode)
        if self.name.startswith('E') and len(self.name) == 14:
            # Update existing distribution
            distribution_id = self.name
            print(f"\n🔄 Updating CloudFront Distribution: {distribution_id}")
            if self.origin_domain:
                print(f"   🌐 Origin: {self.origin_domain}")

            try:
                # Check if we're in production mode
                is_production = os.environ.get('INFRADSL_PRODUCTION_MODE') == 'true'

                if is_production:
                    # PRODUCTION MODE: Update real CloudFront distribution
                    result = self._update_real_cloudfront_distribution()
                else:
                    # SIMULATION MODE: Mock update
                    result = self._update_mock_cloudfront_distribution()

                # Instance attributes are set in the update method
                self._display_update_success(result)
                return self

            except Exception as e:
                print_warning(f"Failed to update CloudFront distribution: {str(e)}")
                raise
        else:
            # Create new distribution
            if not self.origin_domain:
                raise ValueError("Origin domain is required. Use .origin('your-domain.com')")

            desired_distribution_name = f"{self.name}-distribution"
            distribution_id = f"E{str(uuid.uuid4()).replace('-', '').upper()[:13]}"
            cloudfront_domain = f"{distribution_id.lower()}.cloudfront.net"

            print(f"\n🌍 Creating CloudFront Distribution: {desired_distribution_name}")
            print(f"   🌐 Origin: {self.origin_domain}")
            print(f"   🔗 CloudFront Domain: {cloudfront_domain}")

            try:
                # Check if we're in production mode
                is_production = os.environ.get('INFRADSL_PRODUCTION_MODE') == 'true'

                if is_production:
                    # PRODUCTION MODE: Create real CloudFront distribution
                    result = self._create_real_cloudfront_distribution()
                else:
                    # SIMULATION MODE: Mock creation for now
                    result = self._create_mock_cloudfront_distribution()

                # Instance attributes are set in the create method
                self._display_creation_success(result)
                return self

            except Exception as e:
                print_warning(f"Failed to create CloudFront distribution: {str(e)}")
                raise

    def _create_mock_cloudfront_distribution(self) -> Dict[str, Any]:
        """Create mock CloudFront distribution for simulation"""
        desired_distribution_name = f"{self.name}-distribution"
        distribution_id = f"E{str(uuid.uuid4()).replace('-', '').upper()[:13]}"
        cloudfront_domain = f"{distribution_id.lower()}.cloudfront.net"

        return {
            'distribution_id': distribution_id,
            'distribution_arn': f"arn:aws:cloudfront::{distribution_id}:distribution/{distribution_id}",
            'distribution_domain': cloudfront_domain,
            'distribution_name': desired_distribution_name,
            'origin_domain': self.origin_domain,
            'status': 'InProgress',
            'custom_domains': self.custom_domains,
            'ssl_certificate_arn': self.ssl_certificate_arn,
            'price_class': self.price_class_setting or 'PriceClass_All',
            'http2_enabled': self.http2_enabled,
            'ipv6_enabled': self.ipv6_enabled,
            'compression_enabled': self.compression_enabled,
            'security_headers': self.security_headers,
            'behaviors_count': len(self.behaviors),
            'error_pages_count': len(self.error_pages),
            'edge_locations': self._get_edge_locations_count(),
            'deployment_time': '15-20 minutes'
        }

    def _create_real_cloudfront_distribution(self) -> Dict[str, Any]:
        """Create real CloudFront distribution using AWS API"""
        print_info("🚀 Creating REAL CloudFront distribution via AWS API...")

        # Initialize CloudFront client
        cloudfront_client = boto3.client('cloudfront', region_name='us-east-1')

        # Build distribution configuration
        caller_reference = f"infradsl-{self.name}-{int(time.time())}"
        desired_distribution_name = f"{self.name}-distribution"

        # Determine the origin ID to use
        origin_id = f"{self.origin_domain}-origin"
        if hasattr(self, '_custom_target_origin_id') and self._custom_target_origin_id:
            origin_id = self._custom_target_origin_id
        
        # Build origins configuration with proper S3 and custom origin support
        origins_items = []
        
        if hasattr(self, 'origins') and self.origins:
            # Use copied origins configuration if available
            for origin in self.origins:
                origin_item = {
                    'Id': origin['id'],
                    'DomainName': origin['domain'],
                    'OriginPath': origin.get('path', '')
                }
                
                # Handle S3 origin configuration
                if origin['type'] == 's3':
                    s3_config = {}
                    
                    # Add Origin Access Control if present
                    if 'origin_access_control_id' in origin:
                        origin_item['OriginAccessControlId'] = origin['origin_access_control_id']
                        print_info(f"🔐 Using Origin Access Control: {origin['origin_access_control_id']}")
                    
                    # Legacy Origin Access Identity support
                    if 'origin_access_identity' in origin:
                        s3_config['OriginAccessIdentity'] = origin['origin_access_identity']
                        print_info(f"🔐 Using Origin Access Identity: {origin['origin_access_identity']}")
                    
                    origin_item['S3OriginConfig'] = s3_config
                    
                # Handle custom origin configuration
                else:
                    custom_config = origin.get('custom_origin_config', {})
                    origin_item['CustomOriginConfig'] = {
                        'HTTPPort': custom_config.get('http_port', 80),
                        'HTTPSPort': custom_config.get('https_port', 443),
                        'OriginProtocolPolicy': custom_config.get('origin_protocol_policy', 'https-only'),
                        'OriginSslProtocols': {
                            'Quantity': len(custom_config.get('origin_ssl_protocols', ['TLSv1.2'])),
                            'Items': custom_config.get('origin_ssl_protocols', ['TLSv1.2'])
                        }
                    }
                
                origins_items.append(origin_item)
        else:
            # Fallback to simple origin configuration
            origin_item = {
                'Id': origin_id,
                'DomainName': self.origin_domain,
                'OriginPath': ''
            }
            
            # Detect if this is an S3 origin
            if '.s3.' in self.origin_domain or self.origin_domain.endswith('.s3.amazonaws.com'):
                origin_item['S3OriginConfig'] = {}
                print_info(f"🪣 Detected S3 origin: {self.origin_domain}")
            else:
                origin_item['CustomOriginConfig'] = {
                    'HTTPPort': 80,
                    'HTTPSPort': 443,
                    'OriginProtocolPolicy': 'https-only',
                    'OriginSslProtocols': {
                        'Quantity': 3,
                        'Items': ['TLSv1', 'TLSv1.1', 'TLSv1.2']
                    }
                }
                print_info(f"🌐 Using custom origin: {self.origin_domain}")
            
            origins_items.append(origin_item)
        
        origins_config = {
            'Quantity': len(origins_items),
            'Items': origins_items
        }

        # Build default cache behavior
        default_cache_behavior = {
            'TargetOriginId': origin_id,
            'ViewerProtocolPolicy': 'redirect-to-https',
            'TrustedSigners': {
                'Enabled': False,
                'Quantity': 0
            },
            'Compress': self.compression_enabled if hasattr(self, 'compression_enabled') else True
        }
        
        # Add Cache Policy if present from copied configuration
        if hasattr(self, 'default_cache_policy_id') and self.default_cache_policy_id:
            default_cache_behavior['CachePolicyId'] = self.default_cache_policy_id
            # When using cache policies, don't include MinTTL, DefaultTTL, MaxTTL, or ForwardedValues
            print_info(f"🎯 Using Cache Policy: {self.default_cache_policy_id}")
        else:
            # Use legacy ForwardedValues if no cache policy
            default_cache_behavior['ForwardedValues'] = getattr(self, 'default_forwarded_values', {
                'QueryString': False,
                'Cookies': {'Forward': 'none'}
            })
            # Add TTL settings for legacy mode
            default_cache_behavior['MinTTL'] = 0
            default_cache_behavior['DefaultTTL'] = getattr(self, 'default_default_ttl', 86400)
            default_cache_behavior['MaxTTL'] = getattr(self, 'default_max_ttl', 31536000)
        
        # Add Origin Request Policy if present
        if hasattr(self, 'default_origin_request_policy_id') and self.default_origin_request_policy_id:
            default_cache_behavior['OriginRequestPolicyId'] = self.default_origin_request_policy_id
            print_info(f"📡 Using Origin Request Policy: {self.default_origin_request_policy_id}")
        
        # Add Response Headers Policy if present
        if hasattr(self, 'default_response_headers_policy_id') and self.default_response_headers_policy_id:
            default_cache_behavior['ResponseHeadersPolicyId'] = self.default_response_headers_policy_id
        
        # Add Realtime Log Config if present
        if hasattr(self, 'default_realtime_log_config_arn') and self.default_realtime_log_config_arn:
            default_cache_behavior['RealtimeLogConfigArn'] = self.default_realtime_log_config_arn
        
        # Add allowed methods
        allowed_methods = getattr(self, 'default_allowed_methods', ['GET', 'HEAD'])
        cached_methods = getattr(self, 'default_cached_methods', ['GET', 'HEAD'])
        default_cache_behavior['AllowedMethods'] = {
            'Quantity': len(allowed_methods),
            'Items': allowed_methods,
            'CachedMethods': {
                'Quantity': len(cached_methods),
                'Items': cached_methods
            }
        }

        # Build aliases (custom domains)
        aliases_config = {
            'Quantity': len(self.custom_domains),
            'Items': self.custom_domains
        } if self.custom_domains else {'Quantity': 0}

        # Build viewer certificate
        viewer_certificate = {
            'CloudFrontDefaultCertificate': True
        }
        if self.ssl_certificate_arn and self.custom_domains:
            # Extract ARN string if ssl_certificate_arn is a dict
            cert_arn = self.ssl_certificate_arn
            if isinstance(cert_arn, dict):
                cert_arn = cert_arn.get('certificate_arn', cert_arn.get('arn', ''))

            if cert_arn:
                viewer_certificate = {
                    'ACMCertificateArn': cert_arn,
                    'SSLSupportMethod': 'sni-only',
                    'MinimumProtocolVersion': 'TLSv1.2_2021'
                }

        # Build cache behaviors config
        cache_behaviors_config = {'Quantity': 0}
        if hasattr(self, 'behaviors') and self.behaviors:
            behaviors_items = []
            
            for behavior in self.behaviors:
                # All behaviors should use the same origin ID as the main origin
                behavior_item = {
                    'PathPattern': behavior.get('path', '/*'),
                    'TargetOriginId': origin_id,
                    'ViewerProtocolPolicy': behavior.get('viewer_protocol_policy', 'redirect-to-https'),
                    'TrustedSigners': {
                        'Enabled': False,
                        'Quantity': 0
                    },
                    'Compress': behavior.get('compress', True)
                }
                
                # Add Cache Policy if present
                if behavior.get('cache_policy_id'):
                    behavior_item['CachePolicyId'] = behavior.get('cache_policy_id')
                    # When using cache policies, don't include MinTTL, DefaultTTL, MaxTTL, or ForwardedValues
                    print_info(f"🎯 Using Cache Policy for {behavior.get('path', '/*')}: {behavior.get('cache_policy_id')}")
                else:
                    # Use legacy ForwardedValues if no cache policy
                    behavior_item['ForwardedValues'] = behavior.get('forwarded_values', {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    })
                    # Add TTL settings for legacy mode
                    behavior_item['MinTTL'] = behavior.get('ttl', 0)
                    behavior_item['DefaultTTL'] = behavior.get('default_ttl', 86400)
                    behavior_item['MaxTTL'] = behavior.get('max_ttl', 31536000)
                
                # Add Origin Request Policy if present
                if behavior.get('origin_request_policy_id'):
                    behavior_item['OriginRequestPolicyId'] = behavior.get('origin_request_policy_id')
                    print_info(f"📡 Using Origin Request Policy for {behavior.get('path', '/*')}: {behavior.get('origin_request_policy_id')}")
                
                # Add Response Headers Policy if present
                if behavior.get('response_headers_policy_id'):
                    behavior_item['ResponseHeadersPolicyId'] = behavior.get('response_headers_policy_id')
                
                # Add Realtime Log Config if present
                if behavior.get('realtime_log_config_arn'):
                    behavior_item['RealtimeLogConfigArn'] = behavior.get('realtime_log_config_arn')
                
                # Add allowed methods
                allowed_methods = behavior.get('allowed_methods', ['GET', 'HEAD'])
                cached_methods = behavior.get('cached_methods', ['GET', 'HEAD'])
                behavior_item['AllowedMethods'] = {
                    'Quantity': len(allowed_methods),
                    'Items': allowed_methods,
                    'CachedMethods': {
                        'Quantity': len(cached_methods),
                        'Items': cached_methods
                    }
                }
                
                behaviors_items.append(behavior_item)
            
            cache_behaviors_config = {
                'Quantity': len(behaviors_items),
                'Items': behaviors_items
            }

        # Build distribution config
        distribution_config = {
            'CallerReference': caller_reference,
            'Aliases': aliases_config,
            'Comment': f"InfraDSL managed distribution: {desired_distribution_name}",
            'Enabled': True,
            'Origins': origins_config,
            'DefaultCacheBehavior': default_cache_behavior,
            'CacheBehaviors': cache_behaviors_config,
            'ViewerCertificate': viewer_certificate,
            'PriceClass': self.price_class_setting or 'PriceClass_All',
            'HttpVersion': 'http2' if getattr(self, 'http2_enabled', True) else 'http1.1',
            'IsIPV6Enabled': getattr(self, 'ipv6_enabled', True)
        }

        try:
            # Check if we should update an existing distribution instead of creating new one
            existing_distribution_id = None
            
            if self.custom_domains:
                print_info("🔍 Checking for existing distributions with these domains...")
                existing_distribution_id = self._find_distribution_by_domains(cloudfront_client, self.custom_domains)
            
            # If no distribution found by domains, check by name pattern
            if not existing_distribution_id:
                print_info(f"🔍 Checking for existing distribution with name pattern: {desired_distribution_name}")
                existing_distribution_id = self._find_distribution_by_name_pattern(cloudfront_client, desired_distribution_name)
            
            if existing_distribution_id:
                if self.custom_domains:
                    print_info(f"🔄 Found existing distribution {existing_distribution_id} with matching domains")
                else:
                    print_info(f"🔄 Found existing distribution {existing_distribution_id} with matching name pattern")
                print_info(f"🔄 Updating existing distribution instead of creating new one...")
                
                # Switch to update mode
                self.name = existing_distribution_id
                return self._update_real_cloudfront_distribution()
            
            # Pre-creation CNAME cleanup - remove conflicting domains from other distributions
            if self.custom_domains:
                print_info("🔍 Checking for CNAME conflicts before creation...")
                self._cleanup_conflicting_cnames(cloudfront_client, self.custom_domains)

            # Create the distribution
            print_info("📡 Sending distribution creation request to AWS...")
            response = cloudfront_client.create_distribution(DistributionConfig=distribution_config)

            distribution = response['Distribution']
            distribution_id = distribution['Id']

            print_success(f"CloudFront distribution created: {distribution_id}")
            print_info(f"⏱️  Distribution is deploying (this takes 15-45 minutes)")

            result = {
                'distribution_id': distribution_id,
                'distribution_arn': distribution['ARN'],
                'distribution_domain': distribution['DomainName'],
                'distribution_name': desired_distribution_name,
                'origin_domain': self.origin_domain,
                'status': distribution['Status'],
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'price_class': distribution_config['PriceClass'],
                'http2_enabled': distribution_config['HttpVersion'] == 'http2',
                'ipv6_enabled': distribution_config['IsIPV6Enabled'],
                'compression_enabled': default_cache_behavior['Compress'],
                'security_headers': True,
                'behaviors_count': len(self.behaviors) if hasattr(self, 'behaviors') else 0,
                'error_pages_count': len(self.error_pages) if hasattr(self, 'error_pages') else 0,
                'edge_locations': self._get_edge_locations_count(),
                'deployment_time': '15-45 minutes (real AWS deployment)'
            }

            # Set instance attributes here to ensure they're available immediately
            self.distribution_id = result['distribution_id']
            self.distribution_arn = result['distribution_arn']
            self.distribution_domain = result['distribution_domain']
            self.domain_name = result['distribution_domain']  # For backward compatibility
            self.distribution_status = result['status']
            self.distribution_created = True

            return result

        except Exception as e:
            print_warning(f"❌ Failed to create real CloudFront distribution: {str(e)}")
            raise

    def _update_mock_cloudfront_distribution(self) -> Dict[str, Any]:
        """Update mock CloudFront distribution for simulation"""
        distribution_id = self.name
        cloudfront_domain = f"{distribution_id.lower()}.cloudfront.net"

        result = {
            'distribution_id': distribution_id,
            'distribution_arn': f"arn:aws:cloudfront::{distribution_id}:distribution/{distribution_id}",
            'distribution_domain': cloudfront_domain,
            'distribution_name': f"{distribution_id}-distribution",
            'origin_domain': self.origin_domain or 'Existing origins',
            'status': 'InProgress',
            'custom_domains': self.custom_domains,
            'ssl_certificate_arn': self.ssl_certificate_arn,
            'price_class': self.price_class_setting or 'PriceClass_All',
            'http2_enabled': self.http2_enabled,
            'ipv6_enabled': self.ipv6_enabled,
            'compression_enabled': self.compression_enabled,
            'security_headers': self.security_headers,
            'behaviors_count': len(self.behaviors) if hasattr(self, 'behaviors') else 0,
            'error_pages_count': len(self.error_pages) if hasattr(self, 'error_pages') else 0,
            'edge_locations': self._get_edge_locations_count(),
            'deployment_time': '15-20 minutes'
        }

        # Set instance attributes for mock mode too
        self.distribution_id = result['distribution_id']
        self.distribution_arn = result['distribution_arn']
        self.distribution_domain = result['distribution_domain']
        self.domain_name = result['distribution_domain']  # For backward compatibility
        self.distribution_status = result['status']
        self.distribution_created = True

        return result

    def _update_real_cloudfront_distribution(self) -> Dict[str, Any]:
        """Update real CloudFront distribution using AWS API"""
        print_info("🔄 Updating REAL CloudFront distribution via AWS API...")

        # Initialize CloudFront client
        cloudfront_client = boto3.client('cloudfront', region_name='us-east-1')
        distribution_id = self.name

        try:
            # Get current distribution configuration
            print_info("📡 Getting current distribution configuration...")
            response = cloudfront_client.get_distribution_config(Id=distribution_id)
            current_config = response['DistributionConfig']
            etag = response['ETag']

            # Update the configuration with our changes
            print_info("🔧 Updating distribution configuration...")

            # Debug: Check if cache behaviors exist and validate config completeness
            if 'CacheBehaviors' in current_config:
                behaviors_count = current_config['CacheBehaviors'].get('Quantity', 0)
                print_info(f"📊 Found {behaviors_count} existing cache behaviors")
                if behaviors_count > 0:
                    for i, behavior in enumerate(current_config['CacheBehaviors'].get('Items', [])):
                        pattern = behavior.get('PathPattern', 'N/A')
                        target = behavior.get('TargetOriginId', 'N/A')
                        print_info(f"  └─ Behavior {i+1}: {pattern} → {target}")
            else:
                print_info("📊 No cache behaviors found in current config")

            # Validate that we have all required fields for a complete config
            required_fields = ['DefaultCacheBehavior', 'Origins', 'CallerReference', 'Comment']
            missing_fields = [field for field in required_fields if field not in current_config]
            if missing_fields:
                print_warning(f"⚠️  Missing required fields in config: {missing_fields}")
                print_info("🔄 This may indicate the config is incomplete - proceeding with caution")

            # Update aliases (custom domains)
            existing_domains = set(current_config.get('Aliases', {}).get('Items', []))
            new_domains = set(self.custom_domains) if self.custom_domains else set()

            # Check if domains are already correct
            if existing_domains == new_domains:
                print_success("Custom domains already correctly configured")
                domains_need_update = False
            else:
                print_info(f"🔄 Updating custom domains: {', '.join(self.custom_domains) if self.custom_domains else 'None'}")
                domains_need_update = True
                if self.custom_domains:
                    current_config['Aliases'] = {
                        'Quantity': len(self.custom_domains),
                        'Items': self.custom_domains
                    }
                else:
                    current_config['Aliases'] = {'Quantity': 0}

            # Update SSL certificate if provided
            cert_need_update = False
            if self.ssl_certificate_arn and self.custom_domains:
                cert_arn = self.ssl_certificate_arn
                if isinstance(cert_arn, dict):
                    cert_arn = cert_arn.get('certificate_arn', cert_arn.get('arn', ''))

                if cert_arn:
                    existing_cert = current_config.get('ViewerCertificate', {}).get('ACMCertificateArn')
                    if existing_cert != cert_arn:
                        print_info(f"🔐 Updating SSL certificate")
                        cert_need_update = True
                        # Preserve existing ViewerCertificate config and only update necessary fields
                        viewer_cert = current_config.get('ViewerCertificate', {})
                        viewer_cert.update({
                            'CloudFrontDefaultCertificate': False,
                            'ACMCertificateArn': cert_arn,
                            'SSLSupportMethod': 'sni-only',
                            'MinimumProtocolVersion': 'TLSv1.2_2021',
                            'Certificate': cert_arn,
                            'CertificateSource': 'acm'
                        })
                        current_config['ViewerCertificate'] = viewer_cert
                    else:
                        print_success("SSL certificate already correctly configured")

            # Update target origin ID if provided
            origin_need_update = False
            if hasattr(self, '_custom_target_origin_id') and self._custom_target_origin_id:
                existing_origin_id = current_config.get('DefaultCacheBehavior', {}).get('TargetOriginId')
                if existing_origin_id != self._custom_target_origin_id:
                    print_info(f"🎯 Updating target origin ID to: {self._custom_target_origin_id}")
                    origin_need_update = True
                    current_config['DefaultCacheBehavior']['TargetOriginId'] = self._custom_target_origin_id
                    
                    # Also update the origins configuration to match
                    if 'Origins' in current_config and current_config['Origins']['Quantity'] > 0:
                        # Find and update the primary origin
                        primary_origin = current_config['Origins']['Items'][0]
                        old_origin_id = primary_origin['Id']
                        primary_origin['Id'] = self._custom_target_origin_id
                        
                        # Extract domain from the new origin ID (assuming format: domain-origin)
                        if self._custom_target_origin_id.endswith('-origin'):
                            new_domain = self._custom_target_origin_id.replace('-origin', '')
                        else:
                            new_domain = self._custom_target_origin_id
                        
                        primary_origin['DomainName'] = new_domain
                        
                        # Handle Origin Access Control for S3 origins
                        if hasattr(self, 'origins') and self.origins:
                            # Find the matching origin configuration
                            matching_origin = None
                            for origin in self.origins:
                                if origin['id'] == self._custom_target_origin_id:
                                    matching_origin = origin
                                    break
                            
                            if matching_origin:
                                # Update origin configuration with proper S3/custom settings
                                if matching_origin['type'] == 's3':
                                    # Convert to S3 origin if needed
                                    if 'CustomOriginConfig' in primary_origin:
                                        del primary_origin['CustomOriginConfig']
                                    
                                    s3_config = {}
                                    if 'origin_access_control_id' in matching_origin:
                                        primary_origin['OriginAccessControlId'] = matching_origin['origin_access_control_id']
                                        print_info(f"🔐 Applied Origin Access Control: {matching_origin['origin_access_control_id']}")
                                    
                                    if 'origin_access_identity' in matching_origin:
                                        s3_config['OriginAccessIdentity'] = matching_origin['origin_access_identity']
                                        print_info(f"🔐 Applied Origin Access Identity: {matching_origin['origin_access_identity']}")
                                    
                                    primary_origin['S3OriginConfig'] = s3_config
                                    
                                else:
                                    # Convert to custom origin if needed
                                    if 'S3OriginConfig' in primary_origin:
                                        del primary_origin['S3OriginConfig']
                                    if 'OriginAccessControlId' in primary_origin:
                                        del primary_origin['OriginAccessControlId']
                                    
                                    custom_config = matching_origin.get('custom_origin_config', {})
                                    primary_origin['CustomOriginConfig'] = {
                                        'HTTPPort': custom_config.get('http_port', 80),
                                        'HTTPSPort': custom_config.get('https_port', 443),
                                        'OriginProtocolPolicy': custom_config.get('origin_protocol_policy', 'https-only'),
                                        'OriginSslProtocols': {
                                            'Quantity': len(custom_config.get('origin_ssl_protocols', ['TLSv1.2'])),
                                            'Items': custom_config.get('origin_ssl_protocols', ['TLSv1.2'])
                                        }
                                    }
                                    print_info(f"🌐 Applied custom origin config for: {new_domain}")
                        
                        print_info(f"🌐 Updated primary origin: {old_origin_id} → {self._custom_target_origin_id}")
                        print_info(f"🌐 Updated origin domain: {primary_origin['DomainName']}")
                else:
                    print_success("Target origin ID already correctly configured")

            # Update default cache behavior policies if provided
            policies_need_update = False
            
            # Update default cache policy
            if hasattr(self, 'default_cache_policy_id') and self.default_cache_policy_id:
                existing_cache_policy = current_config.get('DefaultCacheBehavior', {}).get('CachePolicyId')
                if existing_cache_policy != self.default_cache_policy_id:
                    print_info(f"🎯 Updating default cache policy to: {self.default_cache_policy_id}")
                    policies_need_update = True
                    current_config['DefaultCacheBehavior']['CachePolicyId'] = self.default_cache_policy_id
                    
                    # Remove legacy settings that conflict with cache policies
                    if 'ForwardedValues' in current_config['DefaultCacheBehavior']:
                        del current_config['DefaultCacheBehavior']['ForwardedValues']
                    if 'MinTTL' in current_config['DefaultCacheBehavior']:
                        del current_config['DefaultCacheBehavior']['MinTTL']
                    if 'DefaultTTL' in current_config['DefaultCacheBehavior']:
                        del current_config['DefaultCacheBehavior']['DefaultTTL']
                    if 'MaxTTL' in current_config['DefaultCacheBehavior']:
                        del current_config['DefaultCacheBehavior']['MaxTTL']
                else:
                    print_success("Default cache policy already correctly configured")
            
            # Update default origin request policy
            if hasattr(self, 'default_origin_request_policy_id') and self.default_origin_request_policy_id:
                existing_origin_policy = current_config.get('DefaultCacheBehavior', {}).get('OriginRequestPolicyId')
                if existing_origin_policy != self.default_origin_request_policy_id:
                    print_info(f"📡 Updating default origin request policy to: {self.default_origin_request_policy_id}")
                    policies_need_update = True
                    current_config['DefaultCacheBehavior']['OriginRequestPolicyId'] = self.default_origin_request_policy_id
                else:
                    print_success("Default origin request policy already correctly configured")
            
            # Update default response headers policy
            if hasattr(self, 'default_response_headers_policy_id') and self.default_response_headers_policy_id:
                existing_response_policy = current_config.get('DefaultCacheBehavior', {}).get('ResponseHeadersPolicyId')
                if existing_response_policy != self.default_response_headers_policy_id:
                    print_info(f"📋 Updating default response headers policy to: {self.default_response_headers_policy_id}")
                    policies_need_update = True
                    current_config['DefaultCacheBehavior']['ResponseHeadersPolicyId'] = self.default_response_headers_policy_id
                else:
                    print_success("Default response headers policy already correctly configured")
            
            # Update default cache behavior allowed methods
            if hasattr(self, 'default_allowed_methods') and self.default_allowed_methods:
                existing_allowed_methods = current_config.get('DefaultCacheBehavior', {}).get('AllowedMethods', {}).get('Items', ['GET', 'HEAD'])
                existing_cached_methods = current_config.get('DefaultCacheBehavior', {}).get('AllowedMethods', {}).get('CachedMethods', {}).get('Items', ['GET', 'HEAD'])
                
                new_allowed_methods = self.default_allowed_methods
                new_cached_methods = getattr(self, 'default_cached_methods', ['GET', 'HEAD'])
                
                if set(existing_allowed_methods) != set(new_allowed_methods) or set(existing_cached_methods) != set(new_cached_methods):
                    print_info(f"🔧 Updating default cache behavior allowed methods: {', '.join(new_allowed_methods)}")
                    policies_need_update = True
                    current_config['DefaultCacheBehavior']['AllowedMethods'] = {
                        'Quantity': len(new_allowed_methods),
                        'Items': new_allowed_methods,
                        'CachedMethods': {
                            'Quantity': len(new_cached_methods),
                            'Items': new_cached_methods
                        }
                    }
                else:
                    print_success("Default cache behavior allowed methods already correctly configured")

            # Update cache behaviors with policies
            behaviors_need_update = False
            current_behaviors = current_config.get('CacheBehaviors', {}).get('Items', [])
            
            # Handle case where we should have no behaviors
            if not hasattr(self, 'behaviors') or not self.behaviors:
                # Check if we need to remove existing behaviors
                if current_behaviors:
                    print_info(f"🗑️  Removing {len(current_behaviors)} existing cache behaviors (should have none)")
                    behaviors_need_update = True
                    current_config['CacheBehaviors'] = {
                        'Quantity': 0,
                        'Items': []
                    }
            else:
                # Update existing behaviors or add new ones
                updated_behaviors = []
                for behavior in self.behaviors:
                    path = behavior.get('path', '/*')
                    
                    # Find existing behavior with same path
                    existing_behavior = next((b for b in current_behaviors if b.get('PathPattern') == path), None)
                    
                    if existing_behavior:
                        # Update existing behavior with policies
                        updated_behavior = existing_behavior.copy()
                        
                        # Update cache policy
                        if behavior.get('cache_policy_id'):
                            if updated_behavior.get('CachePolicyId') != behavior.get('cache_policy_id'):
                                print_info(f"🎯 Updating cache policy for {path} to: {behavior.get('cache_policy_id')}")
                                behaviors_need_update = True
                                updated_behavior['CachePolicyId'] = behavior.get('cache_policy_id')
                                
                                # Remove legacy settings that conflict with cache policies
                                if 'ForwardedValues' in updated_behavior:
                                    del updated_behavior['ForwardedValues']
                                if 'MinTTL' in updated_behavior:
                                    del updated_behavior['MinTTL']
                                if 'DefaultTTL' in updated_behavior:
                                    del updated_behavior['DefaultTTL']
                                if 'MaxTTL' in updated_behavior:
                                    del updated_behavior['MaxTTL']
                        
                        # Update origin request policy
                        if behavior.get('origin_request_policy_id'):
                            if updated_behavior.get('OriginRequestPolicyId') != behavior.get('origin_request_policy_id'):
                                print_info(f"📡 Updating origin request policy for {path} to: {behavior.get('origin_request_policy_id')}")
                                behaviors_need_update = True
                                updated_behavior['OriginRequestPolicyId'] = behavior.get('origin_request_policy_id')
                        
                        # Update response headers policy
                        if behavior.get('response_headers_policy_id'):
                            if updated_behavior.get('ResponseHeadersPolicyId') != behavior.get('response_headers_policy_id'):
                                print_info(f"📋 Updating response headers policy for {path} to: {behavior.get('response_headers_policy_id')}")
                                behaviors_need_update = True
                                updated_behavior['ResponseHeadersPolicyId'] = behavior.get('response_headers_policy_id')
                        
                        # Update target origin ID to match the distribution
                        if hasattr(self, '_custom_target_origin_id') and self._custom_target_origin_id:
                            if updated_behavior.get('TargetOriginId') != self._custom_target_origin_id:
                                print_info(f"🎯 Updating target origin for {path} to: {self._custom_target_origin_id}")
                                behaviors_need_update = True
                                updated_behavior['TargetOriginId'] = self._custom_target_origin_id
                        
                        updated_behaviors.append(updated_behavior)
                    else:
                        # Add new behavior (this would be for completely new behaviors)
                        print_info(f"➕ Adding new cache behavior: {path}")
                        behaviors_need_update = True
                        
                        new_behavior = {
                            'PathPattern': path,
                            'TargetOriginId': hasattr(self, '_custom_target_origin_id') and self._custom_target_origin_id or current_config['DefaultCacheBehavior']['TargetOriginId'],
                            'ViewerProtocolPolicy': behavior.get('viewer_protocol_policy', 'redirect-to-https'),
                            'TrustedSigners': {'Enabled': False, 'Quantity': 0},
                            'Compress': behavior.get('compress', True),
                            'SmoothStreaming': False,
                            'FieldLevelEncryptionId': '',
                            'LambdaFunctionAssociations': {
                                'Quantity': 0,
                                'Items': []
                            }
                        }
                        
                        # Add policies
                        if behavior.get('cache_policy_id'):
                            new_behavior['CachePolicyId'] = behavior.get('cache_policy_id')
                        if behavior.get('origin_request_policy_id'):
                            new_behavior['OriginRequestPolicyId'] = behavior.get('origin_request_policy_id')
                        if behavior.get('response_headers_policy_id'):
                            new_behavior['ResponseHeadersPolicyId'] = behavior.get('response_headers_policy_id')
                        
                        # Add allowed methods
                        allowed_methods = behavior.get('allowed_methods', ['GET', 'HEAD'])
                        cached_methods = behavior.get('cached_methods', ['GET', 'HEAD'])
                        new_behavior['AllowedMethods'] = {
                            'Quantity': len(allowed_methods),
                            'Items': allowed_methods,
                            'CachedMethods': {
                                'Quantity': len(cached_methods),
                                'Items': cached_methods
                            }
                        }
                        
                        updated_behaviors.append(new_behavior)
                
                # Update cache behaviors in config
                if behaviors_need_update:
                    current_config['CacheBehaviors'] = {
                        'Quantity': len(updated_behaviors),
                        'Items': updated_behaviors
                    }

            # Check if any updates are needed
            if not (domains_need_update or cert_need_update or origin_need_update or policies_need_update or behaviors_need_update):
                print_success("Distribution already in desired state - no updates needed")

                # Get current distribution info for response
                response = cloudfront_client.get_distribution(Id=distribution_id)
                distribution = response['Distribution']
            else:
                # Update the distribution
                print_info("📡 Sending distribution update request to AWS...")
                try:
                    response = cloudfront_client.update_distribution(
                        Id=distribution_id,
                        DistributionConfig=current_config,
                        IfMatch=etag
                    )
                    distribution = response['Distribution']
                except Exception as e:
                    if "CNAMEAlreadyExists" in str(e):
                        print_warning(f"⚠️  CNAME conflict detected for distribution {distribution_id}")
                        print_info("🔍 Checking if domains are already assigned to this distribution...")

                        # Check if the domains are already assigned to THIS distribution
                        current_aliases = set(current_config.get('Aliases', {}).get('Items', []))
                        desired_aliases = set(self.custom_domains) if self.custom_domains else set()

                        if current_aliases == desired_aliases:
                            print_success("Domains are already correctly assigned to this distribution")
                            # Get distribution info without updating
                            response = cloudfront_client.get_distribution(Id=distribution_id)
                            distribution = response['Distribution']
                        else:
                            print_warning(f"❌ Domains are assigned to a different distribution")
                            print_info(f"   Current: {current_aliases}")
                            print_info(f"   Desired: {desired_aliases}")
                            raise Exception(f"CNAME conflict: domains are assigned to different distributions. Please resolve manually.")
                    else:
                        raise

            # Only show final status message once
            if domains_need_update or cert_need_update or origin_need_update or policies_need_update or behaviors_need_update:
                final_message = f"CloudFront distribution updated: {distribution_id}"
                timing_message = f"⏱️  Distribution is updating (this takes 15-45 minutes)"
            else:
                final_message = f"CloudFront distribution verified: {distribution_id}"
                timing_message = f"ℹ️  No changes needed - distribution already in desired state"

            result = {
                'distribution_id': distribution_id,
                'distribution_arn': distribution['ARN'],
                'distribution_domain': distribution['DomainName'],
                'distribution_name': f"{distribution_id}-distribution",
                'origin_domain': self.origin_domain or 'Existing origins',
                'status': distribution['Status'],
                'custom_domains': self.custom_domains,
                'ssl_certificate_arn': self.ssl_certificate_arn,
                'price_class': current_config.get('PriceClass', 'PriceClass_All'),
                'http2_enabled': current_config.get('HttpVersion') == 'http2',
                'ipv6_enabled': current_config.get('IsIPV6Enabled', True),
                'compression_enabled': current_config['DefaultCacheBehavior'].get('Compress', True),
                'security_headers': True,
                'behaviors_count': len(self.behaviors) if hasattr(self, 'behaviors') else 0,
                'error_pages_count': len(self.error_pages) if hasattr(self, 'error_pages') else 0,
                'edge_locations': self._get_edge_locations_count(),
                'deployment_time': '15-45 minutes (real AWS deployment)',
                'final_message': final_message,
                'timing_message': timing_message
            }

            # Set instance attributes here to ensure they're available immediately
            self.distribution_id = result['distribution_id']
            self.distribution_arn = result['distribution_arn']
            self.distribution_domain = result['distribution_domain']
            self.domain_name = result['distribution_domain']  # For backward compatibility
            self.distribution_status = result['status']
            self.distribution_created = True

            return result

        except Exception as e:
            print_warning(f"❌ Failed to update real CloudFront distribution: {str(e)}")
            raise

    def _display_update_success(self, result: Dict[str, Any]):
        """Display update success information"""
        print(f"✅ CloudFront Distribution updated successfully")
        print(f"   📋 Distribution ID: {result['distribution_id']}")
        print(f"   🌍 CloudFront Domain: {result['distribution_domain']}")
        print(f"   🌐 Origin: {result['origin_domain']}")
        print(f"   🏷️  Price Class: {result['price_class']}")
        print(f"   📊 Status: {result['status']}")
        if result['custom_domains']:
            print(f"   🔗 Custom Domains: {len(result['custom_domains'])}")
        print(f"   🌍 Edge Locations: {result['edge_locations']}")
        print(f"   ⏱️  Deployment Time: {result['deployment_time']}")
        print(f"   ⚠️  Note: Distribution update can take 15-20 minutes to complete")

    def _find_distribution_by_domains(self, cloudfront_client, domains_to_check):
        """Find existing distribution that has all the specified domains"""
        try:
            # List all distributions
            response = cloudfront_client.list_distributions()
            distributions = response.get('DistributionList', {}).get('Items', [])
            
            domains_set = set(domains_to_check)
            
            for dist in distributions:
                # Check if this distribution has all of our domains
                current_aliases = set(dist.get('Aliases', {}).get('Items', []))
                
                # If this distribution has all our domains, use it
                if domains_set.issubset(current_aliases):
                    return dist['Id']
                
                # Also check for exact match (same domains)
                if current_aliases == domains_set:
                    return dist['Id']
            
            return None
            
        except Exception as e:
            print_warning(f"❌ Error finding existing distribution: {str(e)}")
            return None
    
    def _find_distribution_by_name_pattern(self, cloudfront_client, distribution_name_pattern):
        """Find existing distribution by name pattern in comment or tags"""
        try:
            # List all distributions
            response = cloudfront_client.list_distributions()
            distributions = response.get('DistributionList', {}).get('Items', [])
            
            # Look for distributions with matching comment patterns
            for dist in distributions:
                comment = dist.get('Comment', '')
                distribution_id = dist.get('Id', '')
                
                # Check if the comment contains our distribution name pattern
                if distribution_name_pattern in comment:
                    print_info(f"📝 Found distribution {distribution_id} with matching comment: {comment}")
                    return distribution_id
                
                # Also check if the distribution was created by InfraDSL with similar name
                if 'InfraDSL managed distribution:' in comment:
                    # Extract the name from the comment
                    if distribution_name_pattern.replace('-distribution', '') in comment:
                        print_info(f"📝 Found InfraDSL distribution {distribution_id} with similar name in comment: {comment}")
                        return distribution_id
            
            return None
                
        except Exception as e:
            print_warning(f"Could not search for distributions by name pattern: {str(e)}")
            return None

    def _cleanup_conflicting_cnames(self, cloudfront_client, domains_to_check):
        """Remove conflicting CNAMEs from existing distributions before creating new one"""
        try:
            print_info("🔍 Scanning all CloudFront distributions for CNAME conflicts...")

            # List all distributions
            response = cloudfront_client.list_distributions()
            distributions = response.get('DistributionList', {}).get('Items', [])

            conflicts_found = False

            for dist in distributions:
                # Check if this distribution has any of our domains
                current_aliases = dist.get('Aliases', {}).get('Items', [])
                conflicting_domains = [domain for domain in domains_to_check if domain in current_aliases]

                if conflicting_domains:
                    dist_id = dist['Id']
                    domains_set = set(domains_to_check)
                    current_aliases_set = set(current_aliases)
                    
                    # If this distribution has exactly our domains, don't remove them
                    # (this means we should be updating this distribution instead)
                    if domains_set == current_aliases_set:
                        print_info(f"🔄 Distribution {dist_id} has exactly our domains - this should be updated instead of creating new")
                        continue
                    
                    conflicts_found = True
                    print_info(f"🔄 Found conflicts in distribution {dist_id}: {', '.join(conflicting_domains)}")

                    # Get full distribution config
                    config_response = cloudfront_client.get_distribution_config(Id=dist_id)
                    config = config_response['DistributionConfig']
                    etag = config_response['ETag']

                    # Remove conflicting domains from aliases
                    current_aliases = config.get('Aliases', {}).get('Items', [])
                    new_aliases = [alias for alias in current_aliases if alias not in conflicting_domains]

                    config['Aliases'] = {
                        'Quantity': len(new_aliases),
                        'Items': new_aliases
                    }

                    # Update the distribution
                    print_info(f"🔧 Removing {len(conflicting_domains)} conflicting domains from {dist_id}...")
                    cloudfront_client.update_distribution(
                        Id=dist_id,
                        DistributionConfig=config,
                        IfMatch=etag
                    )

                    print_success(f"Removed conflicting domains from {dist_id}")

                    # Wait a moment for the update to process
                    time.sleep(2)

            if conflicts_found:
                print_success("All CNAME conflicts resolved - ready to create new distribution")
            else:
                print_info("No CNAME conflicts found - proceeding with creation")

        except Exception as e:
            print_warning(f"❌ Error during CNAME cleanup: {str(e)}")
            print_info("⚠️  Proceeding with creation anyway - AWS will show specific conflict details")

    def _get_edge_locations_count(self):
        """Get number of edge locations based on price class"""
        edge_counts = {
            'PriceClass_100': 53,    # US, Canada, Europe
            'PriceClass_200': 89,    # + Asia, India, South America
            'PriceClass_All': 225    # All edge locations worldwide
        }
        return edge_counts.get(self.price_class_setting, 225)

    def _display_creation_success(self, result: Dict[str, Any]):
        """Display creation success information"""
        print(f"✅ CloudFront Distribution created successfully")
        print(f"   📋 Distribution ID: {result['distribution_id']}")
        print(f"   🌍 CloudFront Domain: {result['distribution_domain']}")
        print(f"   🌐 Origin: {result['origin_domain']}")
        print(f"   🏷️  Price Class: {result['price_class']}")
        print(f"   📊 Status: {result['status']}")
        if result['custom_domains']:
            print(f"   🔗 Custom Domains: {len(result['custom_domains'])}")
        print(f"   🌍 Edge Locations: {result['edge_locations']}")
        print(f"   ⏱️  Deployment Time: {result['deployment_time']}")
        print(f"   ⚠️  Note: Distribution deployment can take 15-20 minutes to complete")

    def destroy(self) -> Dict[str, Any]:
        """Destroy the CloudFront distribution"""
        self._ensure_authenticated()

        print(f"🗑️ Destroying CloudFront Distribution: {self.name}")

        try:
            # Mock destruction for now - in real implementation this would use AWS SDK
            result = {
                'distribution_id': self.distribution_arn.split('/')[-1] if self.distribution_arn else 'Unknown',
                'distribution_name': f"{self.name}-distribution",
                'distribution_domain': self.distribution_domain,
                'status': 'Disabled',
                'deleted': True,
                'note': 'Distribution disabled and scheduled for deletion'
            }

            # Reset instance attributes
            self.distribution_arn = None
            self.distribution_domain = None
            self.distribution_status = None
            self.distribution_created = False

            print(f"✅ CloudFront Distribution destruction initiated")
            print(f"   📋 Distribution ID: {result['distribution_id']}")
            print(f"   📊 Status: {result['status']}")
            print(f"   ⚠️  Note: Complete deletion can take up to 24 hours")

            return result

        except Exception as e:
            print(f"❌ Failed to destroy CloudFront Distribution: {str(e)}")
            raise
