import boto3
from botocore.exceptions import ClientError
from typing import Dict, Any, Optional
import json
import os


class S3LifecycleMixin:
    """
    Mixin for S3 bucket lifecycle operations (create, update, destroy, uploads).
    """
    def create(self) -> Dict[str, Any]:
        """Create/update S3 bucket and remove any that are no longer needed"""
        self._ensure_authenticated()
        
        if not self.bucket_name:
            raise ValueError("Bucket name is required. Use .bucket_name('your-bucket-name')")
        
        try:
            # Initialize S3 client if not already done
            if not self.s3_client:
                self.s3_client = self.get_s3_client(self.region_name)
                self.s3_resource = self.get_s3_resource(self.region_name)
            
            # Check if bucket exists
            bucket_exists = self._bucket_exists()
            
            if not bucket_exists:
                # Create bucket
                self._create_bucket()
                print(f"✅ Created S3 bucket: {self.bucket_name}")
            else:
                print(f"📦 S3 bucket exists: {self.bucket_name}")
            
            # Configure bucket settings
            self._configure_bucket()
            
            # Update bucket policy if CloudFront access is configured
            if hasattr(self, '_cloudfront_access') and self._cloudfront_access:
                self._update_bucket_policy_for_cloudfront()
            
            # Process any file uploads
            if self._files_to_upload or self._directories_to_upload:
                self._process_file_uploads()
            
            # Get bucket info for return
            bucket_info = self._get_bucket_info()
            
            # Cache state for drift detection
            self._cache_resource_state(
                resource_config={
                    "bucket_name": self.bucket_name,
                    "region": self.region_name,
                    "storage_class": self.storage_class,
                    "public_access": self.public_access,
                    "versioning_enabled": self.versioning_enabled,
                    "encryption_enabled": self.encryption_enabled,
                    "website_enabled": self.website_enabled,
                    "cors_enabled": self.cors_enabled,
                    "lifecycle_rules": self.lifecycle_rules
                },
                current_state=bucket_info
            )
            
            return bucket_info
            
        except Exception as e:
            print(f"❌ Error creating S3 bucket: {str(e)}")
            raise

    def destroy(self) -> Dict[str, Any]:
        """Destroy the S3 bucket"""
        self._ensure_authenticated()
        
        if not self.bucket_name:
            raise ValueError("Bucket name is required to destroy bucket")
        
        try:
            if not self.s3_client:
                self.s3_client = self.get_s3_client(self.region_name)
                self.s3_resource = self.get_s3_resource(self.region_name)
            
            # Check if bucket exists
            if not self._bucket_exists():
                print(f"⚠️ Bucket {self.bucket_name} does not exist")
                return {"status": "not_found", "bucket_name": self.bucket_name}
            
            # Delete all objects in bucket first
            self._empty_bucket()
            
            # Delete the bucket
            self.s3_client.delete_bucket(Bucket=self.bucket_name)
            print(f"🗑️ Destroyed S3 bucket: {self.bucket_name}")
            
            return {
                "status": "destroyed",
                "bucket_name": self.bucket_name,
                "region": self.region_name
            }
            
        except Exception as e:
            print(f"❌ Error destroying S3 bucket: {str(e)}")
            raise

    def preview(self) -> Dict[str, Any]:
        """Preview what will be created"""
        return {
            "resource_type": "AWS S3 Bucket",
            "bucket_name": self.bucket_name,
            "region": self.region_name or "us-east-1",
            "storage_class": self.storage_class,
            "public_access": self.public_access,
            "versioning_enabled": self.versioning_enabled,
            "encryption_enabled": self.encryption_enabled,
            "website_enabled": self.website_enabled,
            "cors_enabled": self.cors_enabled,
            "lifecycle_rules_count": len(self.lifecycle_rules),
            "files_to_upload": len(self._files_to_upload),
            "directories_to_upload": len(self._directories_to_upload),
            "estimated_cost": self._estimate_storage_cost()
        }

    def _process_file_uploads(self):
        """Process queued file uploads"""
        if not self.s3_client:
            return
        
        # Upload individual files
        for file_info in self._files_to_upload:
            self._upload_file(
                file_info['local_path'],
                file_info.get('s3_key', os.path.basename(file_info['local_path'])),
                file_info.get('storage_class', self.storage_class)
            )
        
        # Upload directories
        for dir_info in self._directories_to_upload:
            self._upload_directory(
                dir_info['local_path'],
                dir_info.get('s3_prefix', ''),
                dir_info.get('storage_class', self.storage_class)
            )

    def _create_bucket(self):
        """Create the S3 bucket"""
        create_params = {'Bucket': self.bucket_name}
        
        # Add location constraint for regions other than us-east-1
        if self.region_name and self.region_name != 'us-east-1':
            create_params['CreateBucketConfiguration'] = {
                'LocationConstraint': self.region_name
            }
        
        self.s3_client.create_bucket(**create_params)

    def _configure_bucket(self):
        """Configure bucket settings"""
        # Configure versioning
        if self.versioning_enabled:
            self.s3_client.put_bucket_versioning(
                Bucket=self.bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
        
        # Configure encryption
        if self.encryption_enabled:
            self.s3_client.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [{
                        'ApplyServerSideEncryptionByDefault': {
                            'SSEAlgorithm': 'AES256'
                        }
                    }]
                }
            )
        
        # Configure public access block
        if not self.public_access:
            self.s3_client.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
        
        # Configure website hosting
        if self.website_enabled:
            self._configure_website()
        
        # Configure CORS
        if self.cors_enabled:
            self._configure_cors()
        
        # Configure lifecycle rules
        if self.lifecycle_rules:
            self._configure_lifecycle()

    def _bucket_exists(self) -> bool:
        """Check if bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except ClientError as e:
            error_code = int(e.response['Error']['Code'])
            if error_code == 404:
                return False
            raise

    def _empty_bucket(self):
        """Empty all objects from bucket before deletion"""
        bucket = self.s3_resource.Bucket(self.bucket_name)
        
        # Delete all object versions
        bucket.object_versions.delete()
        
        # Delete all objects
        bucket.objects.delete()

    def _get_bucket_info(self) -> Dict[str, Any]:
        """Get bucket information"""
        try:
            location = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            region = location.get('LocationConstraint') or 'us-east-1'
            
            # Get bucket URL
            bucket_url = f"https://{self.bucket_name}.s3.{region}.amazonaws.com"
            if region == 'us-east-1':
                bucket_url = f"https://{self.bucket_name}.s3.amazonaws.com"
            
            # Get website URL if website hosting is enabled
            website_url = None
            if self.website_enabled:
                website_url = f"http://{self.bucket_name}.s3-website-{region}.amazonaws.com"
                if region == 'us-east-1':
                    website_url = f"http://{self.bucket_name}.s3-website.amazonaws.com"
            
            return {
                "bucket_name": self.bucket_name,
                "region": region,
                "bucket_url": bucket_url,
                "website_url": website_url,
                "bucket_arn": f"arn:aws:s3:::{self.bucket_name}",
                "storage_class": self.storage_class,
                "public_access": self.public_access,
                "versioning_enabled": self.versioning_enabled,
                "encryption_enabled": self.encryption_enabled,
                "website_enabled": self.website_enabled,
                "cors_enabled": self.cors_enabled
            }
        except Exception as e:
            return {"error": str(e)}

    def _upload_file(self, local_path: str, s3_key: str, storage_class: str = None):
        """Upload a single file to S3"""
        try:
            extra_args = {}
            if storage_class:
                extra_args['StorageClass'] = storage_class
            
            self.s3_client.upload_file(local_path, self.bucket_name, s3_key, ExtraArgs=extra_args)
            print(f"📤 Uploaded {local_path} to s3://{self.bucket_name}/{s3_key}")
        except Exception as e:
            print(f"❌ Error uploading {local_path}: {str(e)}")

    def _upload_directory(self, local_path: str, s3_prefix: str = '', storage_class: str = None):
        """Upload a directory to S3"""
        for root, dirs, files in os.walk(local_path):
            for file in files:
                local_file = os.path.join(root, file)
                relative_path = os.path.relpath(local_file, local_path)
                s3_key = os.path.join(s3_prefix, relative_path).replace('\\', '/')
                self._upload_file(local_file, s3_key, storage_class)

    def _configure_website(self):
        """Configure static website hosting"""
        self.s3_client.put_bucket_website(
            Bucket=self.bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
                'ErrorDocument': {'Key': 'error.html'}
            }
        )

    def _configure_cors(self):
        """Configure CORS settings"""
        cors_configuration = {
            'CORSRules': [{
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'POST', 'PUT', 'DELETE'],
                'AllowedOrigins': ['*'],
                'MaxAgeSeconds': 3000
            }]
        }
        self.s3_client.put_bucket_cors(
            Bucket=self.bucket_name,
            CORSConfiguration=cors_configuration
        )

    def _configure_lifecycle(self):
        """Configure lifecycle rules"""
        if self.lifecycle_rules:
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.bucket_name,
                LifecycleConfiguration={'Rules': self.lifecycle_rules}
            )

    def _estimate_storage_cost(self) -> str:
        """Estimate monthly storage cost"""
        # Simple cost estimation - this could be enhanced
        base_cost = 0.023  # USD per GB per month for Standard storage
        estimated_gb = 1  # Default estimate
        
        if self.storage_class == 'STANDARD_IA':
            base_cost = 0.0125
        elif self.storage_class == 'GLACIER':
            base_cost = 0.004
        
        return f"${base_cost * estimated_gb:.2f}/month (estimated for {estimated_gb}GB)"
    
    def _update_bucket_policy_for_cloudfront(self):
        """Update bucket policy to allow CloudFront access"""
        print(f"🔒 Updating bucket policy for CloudFront access...")
        
        # Get current bucket policy
        try:
            policy_response = self.s3_client.get_bucket_policy(Bucket=self.bucket_name)
            policy = json.loads(policy_response['Policy'])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                # Create new policy if none exists
                policy = {
                    "Version": "2012-10-17",
                    "Statement": []
                }
            else:
                raise
        
        # Get AWS account ID for ARN construction
        try:
            sts_client = boto3.client('sts')
            account_id = sts_client.get_caller_identity()['Account']
        except Exception:
            account_id = None
        
        # Find existing CloudFront service principal statement
        cf_statement = None
        for statement in policy.get('Statement', []):
            if (statement.get('Sid') == 'AllowCloudFrontServicePrincipal' and
                statement.get('Principal', {}).get('Service') == 'cloudfront.amazonaws.com'):
                cf_statement = statement
                break
        
        # If no CloudFront statement exists, create one
        if not cf_statement:
            cf_statement = {
                "Sid": "AllowCloudFrontServicePrincipal",
                "Effect": "Allow",
                "Principal": {
                    "Service": "cloudfront.amazonaws.com"
                },
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{self.bucket_name}/*",
                "Condition": {
                    "StringEquals": {
                        "aws:SourceArn": []
                    }
                }
            }
            policy['Statement'].append(cf_statement)
        
        # Ensure the condition structure exists
        if 'Condition' not in cf_statement:
            cf_statement['Condition'] = {"StringEquals": {"aws:SourceArn": []}}
        if 'StringEquals' not in cf_statement['Condition']:
            cf_statement['Condition']['StringEquals'] = {"aws:SourceArn": []}
        if 'aws:SourceArn' not in cf_statement['Condition']['StringEquals']:
            cf_statement['Condition']['StringEquals']['aws:SourceArn'] = []
        
        # Get existing ARNs (handle both string and array)
        existing_arns = cf_statement['Condition']['StringEquals']['aws:SourceArn']
        if isinstance(existing_arns, str):
            existing_arns = [existing_arns]
        
        # Process each CloudFront distribution
        arns_added = []
        for dist in self._cloudfront_access:
            # Handle both distribution objects and IDs
            if hasattr(dist, 'distribution_id'):
                distribution_id = dist.distribution_id
            elif isinstance(dist, str) and dist.startswith('E'):
                distribution_id = dist
            else:
                print(f"⚠️  Skipping invalid distribution: {dist}")
                continue
            
            # Construct the ARN
            if account_id:
                dist_arn = f"arn:aws:cloudfront::{account_id}:distribution/{distribution_id}"
            else:
                # Fallback if we can't get account ID
                dist_arn = f"arn:aws:cloudfront::*:distribution/{distribution_id}"
            
            # Check if ARN already exists
            if dist_arn not in existing_arns:
                existing_arns.append(dist_arn)
                arns_added.append(distribution_id)
                print(f"  ✅ Added CloudFront distribution {distribution_id} to bucket policy")
            else:
                print(f"  ℹ️  CloudFront distribution {distribution_id} already has access")
        
        # Update the ARN list in the policy
        cf_statement['Condition']['StringEquals']['aws:SourceArn'] = existing_arns
        
        # Update the bucket policy if we're in production mode and made changes
        if os.environ.get('INFRADSL_PRODUCTION_MODE') == 'true':
            if arns_added:
                try:
                    self.s3_client.put_bucket_policy(
                        Bucket=self.bucket_name,
                        Policy=json.dumps(policy, indent=4)
                    )
                    print(f"✅ Updated bucket policy for {self.bucket_name}")
                    print(f"   Added distributions: {', '.join(arns_added)}")
                except Exception as e:
                    print(f"❌ Failed to update bucket policy: {str(e)}")
            else:
                print(f"ℹ️  No changes needed to bucket policy")
        else:
            # Preview mode
            if arns_added:
                print(f"📋 Preview: Would add distributions to bucket policy: {', '.join(arns_added)}")
            else:
                print(f"📋 Preview: No changes would be made to bucket policy") 