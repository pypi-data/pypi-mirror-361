from typing import Dict, Any, List
import boto3
import logging
import os

class CloudFrontConfigurationMixin:
    """
    Mixin for CloudFront chainable configuration methods.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initialize configuration-specific attributes if not already set
        if not hasattr(self, 'origins'):
            self.origins = []
        if not hasattr(self, 'custom_domains'):
            self.custom_domains = []
        if not hasattr(self, 'behaviors'):
            self.behaviors = []
        if not hasattr(self, 'error_pages'):
            self.error_pages = []
        if not hasattr(self, 'cdn_tags'):
            self.cdn_tags = {}
    
    def copy_from(self, distribution_id: str):
        """
        Copy configuration from an existing CloudFront distribution.
        
        Args:
            distribution_id: The distribution ID to copy from (e.g., "E1L4Q3EMY24Z8R")
            
        This method fetches the configuration from the specified distribution and applies it
        to this instance. You can then override specific settings like custom domains,
        origin configurations, etc.
        
        Example:
            cdn = (AWS.CloudFront("my-new-distribution")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .custom_domain("new.example.com")
                   .create())
        """
        try:
            # Initialize CloudFront client - CloudFront is global but API is in us-east-1
            # Try to use the same AWS session/profile as the CLI
            session = boto3.Session()
            
            # If AWS_PROFILE is set, use it explicitly
            if 'AWS_PROFILE' in os.environ:
                session = boto3.Session(profile_name=os.environ['AWS_PROFILE'])
                logging.info(f"Using AWS profile: {os.environ['AWS_PROFILE']}")
            
            cloudfront_client = session.client('cloudfront', region_name='us-east-1')
            
            # Debug: Print current AWS identity to verify credentials
            try:
                sts_client = session.client('sts', region_name='us-east-1')
                identity = sts_client.get_caller_identity()
                logging.info(f"AWS Identity - Account: {identity.get('Account')}, User: {identity.get('Arn')}")
            except Exception as debug_error:
                logging.warning(f"Could not verify AWS identity: {debug_error}")
            
            # Get distribution configuration directly
            response = cloudfront_client.get_distribution_config(Id=distribution_id)
            config = response['DistributionConfig']
            
            logging.info(f"Successfully retrieved distribution config for {distribution_id}")
            logging.debug(f"Config keys: {list(config.keys())}")
            
            # Copy origin configuration
            if 'Origins' in config and 'Items' in config['Origins'] and config['Origins']['Items']:
                primary_origin = config['Origins']['Items'][0]
                self.origin_domain = primary_origin['DomainName']
                
                # Determine origin type
                if 'S3OriginConfig' in primary_origin:
                    self.origin_type = 's3'
                else:
                    self.origin_type = 'custom'
                
                # Store full origins configuration for advanced use
                self.origins = []
                for origin in config['Origins']['Items']:
                    origin_config = {
                        'domain': origin['DomainName'],
                        'type': 's3' if 'S3OriginConfig' in origin else 'custom',
                        'path': origin.get('OriginPath', '/'),
                        'id': origin['Id']
                    }
                    
                    # Copy Origin Access Control (OAC) configuration for S3 origins
                    if 'S3OriginConfig' in origin and 'OriginAccessIdentity' in origin['S3OriginConfig']:
                        origin_config['origin_access_identity'] = origin['S3OriginConfig']['OriginAccessIdentity']
                    
                    # Copy Origin Access Control ID for newer S3 origins
                    if 'OriginAccessControlId' in origin:
                        origin_config['origin_access_control_id'] = origin['OriginAccessControlId']
                    
                    # Copy custom origin protocol policy
                    if 'CustomOriginConfig' in origin:
                        custom_config = origin['CustomOriginConfig']
                        origin_config['custom_origin_config'] = {
                            'http_port': custom_config.get('HTTPPort', 80),
                            'https_port': custom_config.get('HTTPSPort', 443),
                            'origin_protocol_policy': custom_config.get('OriginProtocolPolicy', 'match-viewer'),
                            'origin_ssl_protocols': custom_config.get('OriginSslProtocols', {}).get('Items', ['TLSv1.2'])
                        }
                    
                    self.origins.append(origin_config)
            
            # Copy custom domains (aliases)
            if 'Aliases' in config and 'Items' in config['Aliases'] and config['Aliases']['Items']:
                self.custom_domains = config['Aliases']['Items'].copy()
            
            # Copy SSL certificate configuration
            if 'ViewerCertificate' in config:
                cert_config = config['ViewerCertificate']
                if 'ACMCertificateArn' in cert_config:
                    self.ssl_certificate_arn = cert_config['ACMCertificateArn']
                if 'MinimumProtocolVersion' in cert_config:
                    self.ssl_minimum_version = cert_config['MinimumProtocolVersion']
            
            # Copy price class
            if 'PriceClass' in config:
                self.price_class_setting = config['PriceClass']
            
            # Copy HTTP version settings
            if 'HttpVersion' in config:
                self.http2_enabled = config['HttpVersion'] == 'http2'
            
            # Copy IPv6 setting
            if 'IsIPV6Enabled' in config:
                self.ipv6_enabled = config['IsIPV6Enabled']
            
            # Copy default cache behavior settings
            if 'DefaultCacheBehavior' in config:
                default_behavior = config['DefaultCacheBehavior']
                
                # Store the target origin ID for replacement later
                self._source_target_origin_id = default_behavior.get('TargetOriginId')
                
                if 'Compress' in default_behavior:
                    self.compression_enabled = default_behavior['Compress']
                
                # Copy policies from default behavior
                self.default_cache_policy_id = default_behavior.get('CachePolicyId')
                self.default_origin_request_policy_id = default_behavior.get('OriginRequestPolicyId')
                self.default_response_headers_policy_id = default_behavior.get('ResponseHeadersPolicyId')
                self.default_realtime_log_config_arn = default_behavior.get('RealtimeLogConfigArn')
                
                # Copy legacy ForwardedValues if no cache policy is used
                if not self.default_cache_policy_id:
                    self.default_forwarded_values = default_behavior.get('ForwardedValues', {
                        'QueryString': False,
                        'Cookies': {'Forward': 'none'}
                    })
                    self.default_default_ttl = default_behavior.get('DefaultTTL', 86400)
                    self.default_max_ttl = default_behavior.get('MaxTTL', 31536000)
                
                # Copy allowed methods for default behavior
                if 'AllowedMethods' in default_behavior:
                    self.default_allowed_methods = default_behavior['AllowedMethods'].get('Items', ['GET', 'HEAD'])
                    self.default_cached_methods = default_behavior['AllowedMethods'].get('CachedMethods', {}).get('Items', ['GET', 'HEAD'])
                else:
                    self.default_allowed_methods = ['GET', 'HEAD']
                    self.default_cached_methods = ['GET', 'HEAD']
            
            # Copy additional cache behaviors
            if 'CacheBehaviors' in config and config['CacheBehaviors']['Quantity'] > 0:
                self.behaviors = []
                for behavior in config['CacheBehaviors']['Items']:
                    behavior_config = {
                        'path': behavior.get('PathPattern', ''),
                        'ttl': behavior.get('MinTTL', 0),
                        'compress': behavior.get('Compress', True),
                        'methods': ['GET', 'HEAD'],  # Simplified for now
                        'headers': [],
                        'target_origin_id': behavior.get('TargetOriginId', ''),
                        'viewer_protocol_policy': behavior.get('ViewerProtocolPolicy', 'redirect-to-https'),
                        # Copy Cache Policy and Origin Request Policy
                        'cache_policy_id': behavior.get('CachePolicyId'),
                        'origin_request_policy_id': behavior.get('OriginRequestPolicyId'),
                        'response_headers_policy_id': behavior.get('ResponseHeadersPolicyId'),
                        'realtime_log_config_arn': behavior.get('RealtimeLogConfigArn'),
                        # Copy legacy ForwardedValues if no cache policy is used
                        'forwarded_values': behavior.get('ForwardedValues') if not behavior.get('CachePolicyId') else None,
                        # Copy allowed methods
                        'allowed_methods': behavior.get('AllowedMethods', {}).get('Items', ['GET', 'HEAD']) if 'AllowedMethods' in behavior else ['GET', 'HEAD'],
                        'cached_methods': behavior.get('AllowedMethods', {}).get('CachedMethods', {}).get('Items', ['GET', 'HEAD']) if 'AllowedMethods' in behavior else ['GET', 'HEAD'],
                        # Copy TTL settings
                        'default_ttl': behavior.get('DefaultTTL', 86400),
                        'max_ttl': behavior.get('MaxTTL', 31536000)
                    }
                    self.behaviors.append(behavior_config)
                logging.info(f"Copied {len(self.behaviors)} cache behaviors with policies from source distribution")
                
                # Fetch and store policy names for display
                self._fetch_policy_names(cloudfront_client)
            
            # Copy WAF Web ACL
            if 'WebACLId' in config and config['WebACLId']:
                self.waf_web_acl_id = config['WebACLId']
            
            # Copy geo restrictions
            if 'Restrictions' in config and 'GeoRestriction' in config['Restrictions']:
                geo_config = config['Restrictions']['GeoRestriction']
                if geo_config['RestrictionType'] != 'none':
                    self.geo_restriction = {
                        'type': geo_config['RestrictionType'],
                        'locations': geo_config.get('Items', [])
                    }
            
            # Copy error pages
            if 'CustomErrorResponses' in config and 'Items' in config['CustomErrorResponses'] and config['CustomErrorResponses']['Items']:
                self.error_pages = []
                for error_config in config['CustomErrorResponses']['Items']:
                    self.error_pages.append({
                        'error_code': error_config['ErrorCode'],
                        'response_code': error_config.get('ResponseCode'),
                        'response_page': error_config.get('ResponsePagePath'),
                        'ttl': error_config.get('ErrorCachingMinTTL', 300)
                    })
            
            # Store the source distribution ID for reference
            self._copied_from_distribution_id = distribution_id
            
            # Always fetch policy names for display purposes
            self._fetch_policy_names(cloudfront_client)
            
            logging.info(f"Successfully copied configuration from distribution {distribution_id}")
            
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Failed to copy from distribution {distribution_id}: {error_msg}")
            
            # Provide helpful error messages
            if "NoSuchDistribution" in error_msg:
                help_msg = f"""
Distribution {distribution_id} not found. Common issues:
1. Check the distribution ID is correct
2. Ensure you have permissions to access CloudFront distributions
3. Verify your AWS credentials are set up correctly
4. The distribution might be in a different AWS account

Run 'aws cloudfront list-distributions' to see available distributions.
                """.strip()
                raise ValueError(help_msg)
            elif "AccessDenied" in error_msg:
                raise ValueError(f"Access denied to distribution {distribution_id}. Check your AWS IAM permissions for CloudFront.")
            else:
                raise ValueError(f"Could not copy from distribution {distribution_id}: {error_msg}")
        
        return self

    def _fetch_policy_names(self, cloudfront_client):
        """Fetch and store policy names for display purposes"""
        try:
            # Initialize policy name mappings
            self.policy_names = {}
            
            # Fetch policy names for default cache behavior
            if hasattr(self, 'default_cache_policy_id') and self.default_cache_policy_id:
                try:
                    response = cloudfront_client.get_cache_policy(Id=self.default_cache_policy_id)
                    self.policy_names[self.default_cache_policy_id] = response['CachePolicy']['CachePolicyConfig']['Name']
                except Exception:
                    self.policy_names[self.default_cache_policy_id] = 'Unknown Cache Policy'
            
            if hasattr(self, 'default_origin_request_policy_id') and self.default_origin_request_policy_id:
                try:
                    response = cloudfront_client.get_origin_request_policy(Id=self.default_origin_request_policy_id)
                    self.policy_names[self.default_origin_request_policy_id] = response['OriginRequestPolicy']['OriginRequestPolicyConfig']['Name']
                except Exception:
                    self.policy_names[self.default_origin_request_policy_id] = 'Unknown Origin Request Policy'
            
            if hasattr(self, 'default_response_headers_policy_id') and self.default_response_headers_policy_id:
                try:
                    response = cloudfront_client.get_response_headers_policy(Id=self.default_response_headers_policy_id)
                    self.policy_names[self.default_response_headers_policy_id] = response['ResponseHeadersPolicy']['ResponseHeadersPolicyConfig']['Name']
                except Exception:
                    self.policy_names[self.default_response_headers_policy_id] = 'Unknown Response Headers Policy'
            
            # Fetch policy names for behaviors
            if hasattr(self, 'behaviors') and self.behaviors:
                for behavior in self.behaviors:
                    if behavior.get('cache_policy_id'):
                        policy_id = behavior['cache_policy_id']
                        if policy_id not in self.policy_names:
                            try:
                                response = cloudfront_client.get_cache_policy(Id=policy_id)
                                self.policy_names[policy_id] = response['CachePolicy']['CachePolicyConfig']['Name']
                                behavior['cache_policy_name'] = self.policy_names[policy_id]
                            except Exception:
                                self.policy_names[policy_id] = 'Unknown Cache Policy'
                                behavior['cache_policy_name'] = 'Unknown Cache Policy'
                    
                    if behavior.get('origin_request_policy_id'):
                        policy_id = behavior['origin_request_policy_id']
                        if policy_id not in self.policy_names:
                            try:
                                response = cloudfront_client.get_origin_request_policy(Id=policy_id)
                                self.policy_names[policy_id] = response['OriginRequestPolicy']['OriginRequestPolicyConfig']['Name']
                                behavior['origin_request_policy_name'] = self.policy_names[policy_id]
                            except Exception:
                                self.policy_names[policy_id] = 'Unknown Origin Request Policy'
                                behavior['origin_request_policy_name'] = 'Unknown Origin Request Policy'
                    
                    if behavior.get('response_headers_policy_id'):
                        policy_id = behavior['response_headers_policy_id']
                        if policy_id not in self.policy_names:
                            try:
                                response = cloudfront_client.get_response_headers_policy(Id=policy_id)
                                self.policy_names[policy_id] = response['ResponseHeadersPolicy']['ResponseHeadersPolicyConfig']['Name']
                                behavior['response_headers_policy_name'] = self.policy_names[policy_id]
                            except Exception:
                                self.policy_names[policy_id] = 'Unknown Response Headers Policy'
                                behavior['response_headers_policy_name'] = 'Unknown Response Headers Policy'
                                
        except Exception as e:
            logging.warning(f"Could not fetch policy names: {e}")
            self.policy_names = {}

    def target_origin_id(self, new_origin_id: str):
        """
        Set a custom Target Origin ID for the default cache behavior.
        
        This is especially useful when copying from another distribution
        and you want to update the Target Origin ID to match your new domain.
        
        Args:
            new_origin_id: The new target origin ID (e.g., "production.example.com-{DOMAIN}")
            
        Example:
            cdn = (AWS.CloudFront("new-cdn")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .target_origin_id("production.newdomain.com-newdomain")
                   .create())
        """
        self._custom_target_origin_id = new_origin_id
        return self
    
    def default_allowed_methods(self, methods: List[str]):
        """
        Set allowed HTTP methods for the default cache behavior.
        
        Args:
            methods: List of HTTP methods to allow (e.g., ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'])
            
        Example:
            # For API/gaming endpoints that need all methods
            cdn = (AWS.CloudFront("game-cdn")
                   .copy_from("E2V4BM77LJFYB6")
                   .default_allowed_methods(['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'])
                   .create())
        """
        self.default_allowed_methods = methods
        # Also set cached methods to be a subset of allowed methods
        # For most cases, only GET and HEAD should be cached
        self.default_cached_methods = ['GET', 'HEAD']
        return self
    
    def enable_all_methods(self):
        """
        Convenience method to enable all HTTP methods for the default cache behavior.
        This is useful for gaming/API endpoints that need full HTTP method support.
        
        Example:
            game_cdn = (AWS.CloudFront("game-cdn")
                       .copy_from("E2V4BM77LJFYB6")
                       .enable_all_methods()
                       .create())
        """
        self.default_allowed_methods = ['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE']
        # Also set cached methods to be a subset of allowed methods
        # For most cases, only GET and HEAD should be cached
        self.default_cached_methods = ['GET', 'HEAD']
        return self

    def origin(self, domain: str, type_: str = 'custom', path: str = '/'):
        """Set the origin domain and type"""
        self.origin_domain = domain
        self.origin_type = type_
        
        # Add to origins list for advanced configurations
        origin_config = {
            'domain': domain,
            'type': type_,
            'path': path
        }
        
        # Check if origin already exists and update it
        existing_origin = next((o for o in self.origins if o['domain'] == domain), None)
        if existing_origin:
            existing_origin.update(origin_config)
        else:
            self.origins.append(origin_config)
        
        return self
    
    def s3_origin(self, bucket_name: str, path: str = '/'):
        """Convenience method for S3 origin"""
        s3_domain = f"{bucket_name}.s3.amazonaws.com"
        return self.origin(s3_domain, 's3', path)
    
    def load_balancer_origin(self, lb_domain: str, path: str = '/'):
        """Convenience method for Load Balancer origin"""
        return self.origin(lb_domain, 'load_balancer', path)
    
    def custom_domain(self, domain: str):
        """Add a custom domain to the distribution"""
        if domain not in self.custom_domains:
            self.custom_domains.append(domain)
        return self
    
    def domains(self, domains: List[str]):
        """Add multiple custom domains"""
        for domain in domains:
            self.custom_domain(domain)
        return self
    
    def clear_domains(self):
        """Clear all custom domains (useful when copying from another distribution)"""
        self.custom_domains = []
        return self
    
    def gaming_optimized(self):
        """Nexus Engine: Gaming-optimized CloudFront preset"""
        self.worldwide()  # All edge locations for global gaming
        self.http2(True)
        self.compression(True)
        self.real_time_logs(True)
        self.websocket_support(True)
        return self
    
    def production_optimized(self):
        """Nexus Engine: Production-optimized CloudFront preset"""
        self.worldwide()
        self.http2(True)
        self.compression(True)
        self.security_headers(True)
        self.ddos_protection(True)
        return self
    
    def ssl_certificate(self, certificate = None):
        """
        Set the SSL certificate for CloudFront distribution.
        
        Accepts multiple input types:
        - String ARN: Direct certificate ARN 
        - Certificate object: CertificateManager instance (extracts ARN)
        - Result dictionary: Result from certificate.create() (extracts ARN)
        - None: Use CloudFront default certificate
        
        Args:
            certificate: Certificate ARN string, CertificateManager object, 
                        result dict, or None for default
        """
        if certificate is None:
            self.viewer_certificate_cloudfront_default_certificate = True
            self.ssl_certificate_arn = None
        elif isinstance(certificate, str):
            # Direct ARN string
            self.ssl_certificate_arn = certificate
        elif isinstance(certificate, dict):
            # Result dictionary from certificate.create()
            arn = certificate.get('certificate_arn')
            if arn:
                self.ssl_certificate_arn = arn
                print(f"   🔗 Using certificate ARN: {arn}")
            else:
                print(f"   ⚠️  No certificate_arn found in result dictionary")
                self.viewer_certificate_cloudfront_default_certificate = True
        elif hasattr(certificate, 'certificate_arn'):
            # Certificate object with certificate_arn attribute
            if certificate.certificate_arn:
                self.ssl_certificate_arn = certificate.certificate_arn
                print(f"   🔗 Using certificate ARN: {certificate.certificate_arn}")
            else:
                print(f"   ⚠️  Certificate object has no ARN (may not be created yet)")
                # Try accessing domain_name for informative error
                domain = getattr(certificate, 'domain_name', getattr(certificate, 'cert_domain_name', 'unknown'))
                print(f"   💡 Tip: Create the certificate first, then pass the result or ARN to CloudFront")
                print(f"   📝 Certificate domain: {domain}")
                self.viewer_certificate_cloudfront_default_certificate = True
        else:
            # Unknown type - try to extract ARN or use default
            print(f"   ⚠️  Unknown certificate type: {type(certificate)}")
            print(f"   💡 Expected: ARN string, certificate object, or result dictionary")
            self.viewer_certificate_cloudfront_default_certificate = True
        
        return self
    
    def ssl_minimum_version(self, version: str):
        """Set minimum SSL version (TLSv1, TLSv1.1, TLSv1.2)"""
        self.ssl_minimum_version = version
        return self
    
    def price_class(self, price_class: str):
        """Set the price class (PriceClass_All, PriceClass_200, PriceClass_100)"""
        valid_classes = ['PriceClass_All', 'PriceClass_200', 'PriceClass_100']
        if price_class not in valid_classes:
            raise ValueError(f"Invalid price class. Must be one of: {valid_classes}")
        self.price_class_setting = price_class
        return self
    
    def worldwide(self):
        """Use all edge locations worldwide"""
        return self.price_class('PriceClass_All')
    
    def us_europe_asia(self):
        """Use edge locations in US, Canada, Europe, Asia, India"""
        return self.price_class('PriceClass_200')
    
    def us_europe_only(self):
        """Use edge locations in US, Canada, Europe only"""
        return self.price_class('PriceClass_100')
    
    def http2(self, enabled: bool = True):
        """Enable or disable HTTP/2"""
        self.http2_enabled = enabled
        return self
    
    def ipv6(self, enabled: bool = True):
        """Enable or disable IPv6"""
        self.ipv6_enabled = enabled
        return self
    
    def compress(self, enabled: bool = True):
        """Enable or disable compression"""
        self.compression_enabled = enabled
        return self
    
    def security_headers(self, enabled: bool = True):
        """Enable security headers"""
        self.security_headers = enabled
        return self
    
    def waf(self, web_acl_id: str):
        """Attach a WAF Web ACL"""
        self.waf_web_acl_id = web_acl_id
        return self
    
    def geo_restriction(self, restriction_type: str, locations: List[str] = None):
        """Set geo restriction configuration"""
        self.geo_restriction = {
            'type': restriction_type,  # 'blacklist', 'whitelist', 'none'
            'locations': locations or []
        }
        return self
    
    def block_countries(self, country_codes: List[str]):
        """Block specific countries"""
        return self.geo_restriction('blacklist', country_codes)
    
    def allow_countries(self, country_codes: List[str]):
        """Allow only specific countries"""
        return self.geo_restriction('whitelist', country_codes)
    
    def error_page(self, error_code: int, response_code: int = None, response_page: str = None, ttl: int = 300):
        """Add an error page configuration"""
        error_config = {
            'error_code': error_code,
            'response_code': response_code or error_code,
            'response_page': response_page,
            'ttl': ttl
        }
        self.error_pages.append(error_config)
        return self
    
    def error_404(self, response_page: str = '/404.html', ttl: int = 300):
        """Convenience method for 404 error page"""
        return self.error_page(404, 200, response_page, ttl)
    
    def error_403(self, response_page: str = '/403.html', ttl: int = 300):
        """Convenience method for 403 error page"""
        return self.error_page(403, 200, response_page, ttl)
    
    def behavior(self, path: str, ttl: int = 86400, compress: bool = True, 
                methods: List[str] = None, headers: List[str] = None):
        """Add a custom behavior for specific paths"""
        behavior_config = {
            'path': path,
            'ttl': ttl,
            'compress': compress,
            'methods': methods or ['GET', 'HEAD'],
            'headers': headers or []
        }
        self.behaviors.append(behavior_config)
        return self
    
    def api_behavior(self, path: str = '/api/*', ttl: int = 0):
        """Convenience method for API paths (no caching)"""
        return self.behavior(path, ttl, methods=['GET', 'HEAD', 'OPTIONS', 'PUT', 'POST', 'PATCH', 'DELETE'])
    
    def static_behavior(self, path: str = '/static/*', ttl: int = 31536000):  # 1 year
        """Convenience method for static assets (long caching)"""
        return self.behavior(path, ttl, compress=True)
    
    def logging(self, enabled: bool = True, bucket: str = None, prefix: str = None):
        """Enable or disable logging and set bucket/prefix"""
        self.logging_enabled = enabled
        if bucket:
            self.logging_bucket = bucket
        if prefix:
            self.logging_prefix = prefix
        return self
    
    def cloudwatch_metrics(self, enabled: bool = True):
        """Enable CloudWatch metrics"""
        # This would enable real-time metrics in a real implementation
        return self
    
    def tag(self, key: str, value: str):
        """Add a tag to the distribution"""
        self.cdn_tags[key] = value
        return self
    
    def tags(self, tags_dict: Dict[str, str]):
        """Add multiple tags to the distribution"""
        self.cdn_tags.update(tags_dict)
        return self
    
    @staticmethod
    def copy_from_examples():
        """
        Examples of using the copy_from functionality:
        
        Basic copy with new domains:
            cdn = (AWS.CloudFront("new-distribution")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .clear_domains()
                   .custom_domain("new.example.com")
                   .custom_domain("www.new.example.com")
                   .create())
        
        Copy with origin and target ID updates:
            from datetime import datetime
            
            DOMAIN_NAME = "newdomain.com"
            cdn = (AWS.CloudFront(f"{datetime.now().strftime('%Y%m%d')}")
                   .copy_from("E1L4Q3EMY24Z8R")
                   .clear_domains()
                   .custom_domain(f"ec.{DOMAIN_NAME}")
                   .custom_domain(f"nc.{DOMAIN_NAME}")
                   .target_origin_id(f"production.{DOMAIN_NAME}-{DOMAIN_NAME}")
                   .preview())
        
        Copy but keep origin domain:
            cdn = (AWS.CloudFront("cloned-distribution")
                   .copy_from("E1L4Q3EMY24Z8R")
                   # Origin domain is kept from source
                   .custom_domain("different.example.com")
                   .create())
                   
        What gets copied:
        - Origin configuration (domain, type, paths)
        - Custom domains/aliases
        - SSL certificate settings
        - Price class (edge location coverage)
        - HTTP/2 and IPv6 settings
        - Compression settings
        - WAF Web ACL
        - Geo restrictions
        - Custom error pages
        - Cache behaviors
        
        What you can override:
        - Custom domains (via .clear_domains() then .custom_domain())
        - Origin domain (via .origin())
        - Target Origin ID (via .target_origin_id())
        - SSL certificate (via .ssl_certificate())
        - Any other configuration method
        """
        pass 