r'''
# Will be replacing this with project documentation
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

import aws_cdk as _aws_cdk_ceddda9d
import aws_cdk.aws_ec2 as _aws_cdk_aws_ec2_ceddda9d
import aws_cdk.aws_iam as _aws_cdk_aws_iam_ceddda9d
import aws_cdk.aws_opensearchservice as _aws_cdk_aws_opensearchservice_ceddda9d
import constructs as _constructs_77d1e7e8


@jsii.data_type(
    jsii_type="fnl-aws-cdk.CustomProps",
    jsii_struct_bases=[_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps],
    name_mapping={
        "version": "version",
        "access_policies": "accessPolicies",
        "advanced_options": "advancedOptions",
        "automated_snapshot_start_hour": "automatedSnapshotStartHour",
        "capacity": "capacity",
        "cognito_dashboards_auth": "cognitoDashboardsAuth",
        "cold_storage_enabled": "coldStorageEnabled",
        "custom_endpoint": "customEndpoint",
        "domain_name": "domainName",
        "ebs": "ebs",
        "enable_auto_software_update": "enableAutoSoftwareUpdate",
        "enable_version_upgrade": "enableVersionUpgrade",
        "encryption_at_rest": "encryptionAtRest",
        "enforce_https": "enforceHttps",
        "fine_grained_access_control": "fineGrainedAccessControl",
        "ip_address_type": "ipAddressType",
        "logging": "logging",
        "node_to_node_encryption": "nodeToNodeEncryption",
        "off_peak_window_enabled": "offPeakWindowEnabled",
        "off_peak_window_start": "offPeakWindowStart",
        "removal_policy": "removalPolicy",
        "security_groups": "securityGroups",
        "suppress_logs_resource_policy": "suppressLogsResourcePolicy",
        "tls_security_policy": "tlsSecurityPolicy",
        "use_unsigned_basic_auth": "useUnsignedBasicAuth",
        "vpc": "vpc",
        "vpc_subnets": "vpcSubnets",
        "zone_awareness": "zoneAwareness",
        "masteruser": "masteruser",
        "program": "program",
        "project": "project",
        "tier": "tier",
    },
)
class CustomProps(_aws_cdk_aws_opensearchservice_ceddda9d.DomainProps):
    def __init__(
        self,
        *,
        version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
        access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
        capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cold_storage_enabled: typing.Optional[builtins.bool] = None,
        custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_auto_software_update: typing.Optional[builtins.bool] = None,
        enable_version_upgrade: typing.Optional[builtins.bool] = None,
        encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enforce_https: typing.Optional[builtins.bool] = None,
        fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        node_to_node_encryption: typing.Optional[builtins.bool] = None,
        off_peak_window_enabled: typing.Optional[builtins.bool] = None,
        off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
        tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
        use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        masteruser: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
    ) -> None:
        '''
        :param version: The Elasticsearch/OpenSearch version that your domain will leverage.
        :param access_policies: Domain access policies. Default: - No access policies.
        :param advanced_options: Additional options to specify for the Amazon OpenSearch Service domain. Default: - no advanced options are specified
        :param automated_snapshot_start_hour: The hour in UTC during which the service takes an automated daily snapshot of the indices in the Amazon OpenSearch Service domain. Only applies for Elasticsearch versions below 5.3. Default: - Hourly automated snapshots not used
        :param capacity: The cluster capacity configuration for the Amazon OpenSearch Service domain. Default: - 1 r5.large.search data node; no dedicated master nodes.
        :param cognito_dashboards_auth: Configures Amazon OpenSearch Service to use Amazon Cognito authentication for OpenSearch Dashboards. Default: - Cognito not used for authentication to OpenSearch Dashboards.
        :param cold_storage_enabled: Whether to enable or disable cold storage on the domain. You must enable UltraWarm storage to enable cold storage. Default: - undefined
        :param custom_endpoint: To configure a custom domain configure these options. If you specify a Route53 hosted zone it will create a CNAME record and use DNS validation for the certificate Default: - no custom domain endpoint will be configured
        :param domain_name: Enforces a particular physical domain name. Default: - A name will be auto-generated.
        :param ebs: The configurations of Amazon Elastic Block Store (Amazon EBS) volumes that are attached to data nodes in the Amazon OpenSearch Service domain. Default: - 10 GiB General Purpose (SSD) volumes per node.
        :param enable_auto_software_update: Specifies whether automatic service software updates are enabled for the domain. Default: - false
        :param enable_version_upgrade: To upgrade an Amazon OpenSearch Service domain to a new version, rather than replacing the entire domain resource, use the EnableVersionUpgrade update policy. Default: - false
        :param encryption_at_rest: Encryption at rest options for the cluster. Default: - No encryption at rest
        :param enforce_https: True to require that all traffic to the domain arrive over HTTPS. Default: - false
        :param fine_grained_access_control: Specifies options for fine-grained access control. Requires Elasticsearch version 6.7 or later or OpenSearch version 1.0 or later. Enabling fine-grained access control also requires encryption of data at rest and node-to-node encryption, along with enforced HTTPS. Default: - fine-grained access control is disabled
        :param ip_address_type: Specify either dual stack or IPv4 as your IP address type. Dual stack allows you to share domain resources across IPv4 and IPv6 address types, and is the recommended option. If you set your IP address type to dual stack, you can't change your address type later. Default: - IpAddressType.IPV4
        :param logging: Configuration log publishing configuration options. Default: - No logs are published
        :param node_to_node_encryption: Specify true to enable node to node encryption. Requires Elasticsearch version 6.0 or later or OpenSearch version 1.0 or later. Default: - Node to node encryption is not enabled.
        :param off_peak_window_enabled: Options for enabling a domain's off-peak window, during which OpenSearch Service can perform mandatory configuration changes on the domain. Off-peak windows were introduced on February 16, 2023. All domains created before this date have the off-peak window disabled by default. You must manually enable and configure the off-peak window for these domains. All domains created after this date will have the off-peak window enabled by default. You can't disable the off-peak window for a domain after it's enabled. Default: - Disabled for domains created before February 16, 2023. Enabled for domains created after. Enabled if ``offPeakWindowStart`` is set.
        :param off_peak_window_start: Start time for the off-peak window, in Coordinated Universal Time (UTC). The window length will always be 10 hours, so you can't specify an end time. For example, if you specify 11:00 P.M. UTC as a start time, the end time will automatically be set to 9:00 A.M. Default: - 10:00 P.M. local time
        :param removal_policy: Policy to apply when the domain is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_groups: The list of security groups that are associated with the VPC endpoints for the domain. Only used if ``vpc`` is specified. Default: - One new security group is created.
        :param suppress_logs_resource_policy: Specify whether to create a CloudWatch Logs resource policy or not. When logging is enabled for the domain, a CloudWatch Logs resource policy is created by default. However, CloudWatch Logs supports only 10 resource policies per region. If you enable logging for several domains, it may hit the quota and cause an error. By setting this property to true, creating a resource policy is suppressed, allowing you to avoid this problem. If you set this option to true, you must create a resource policy before deployment. Default: - false
        :param tls_security_policy: The minimum TLS version required for traffic to the domain. Default: - TLSSecurityPolicy.TLS_1_2
        :param use_unsigned_basic_auth: Configures the domain so that unsigned basic auth is enabled. If no master user is provided a default master user with username ``admin`` and a dynamically generated password stored in KMS is created. The password can be retrieved by getting ``masterUserPassword`` from the domain instance. Setting this to true will also add an access policy that allows unsigned access, enable node to node encryption, encryption at rest. If conflicting settings are encountered (like disabling encryption at rest) enabling this setting will cause a failure. Default: - false
        :param vpc: Place the domain inside this VPC. Default: - Domain is not placed in a VPC.
        :param vpc_subnets: The specific vpc subnets the domain will be placed in. You must provide one subnet for each Availability Zone that your domain uses. For example, you must specify three subnet IDs for a three Availability Zone domain. Only used if ``vpc`` is specified. Default: - All private subnets.
        :param zone_awareness: The cluster zone awareness configuration for the Amazon OpenSearch Service domain. Default: - no zone awareness (1 AZ)
        :param masteruser: 
        :param program: 
        :param project: 
        :param tier: 
        '''
        if isinstance(capacity, dict):
            capacity = _aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig(**capacity)
        if isinstance(cognito_dashboards_auth, dict):
            cognito_dashboards_auth = _aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions(**cognito_dashboards_auth)
        if isinstance(custom_endpoint, dict):
            custom_endpoint = _aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions(**custom_endpoint)
        if isinstance(ebs, dict):
            ebs = _aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions(**ebs)
        if isinstance(encryption_at_rest, dict):
            encryption_at_rest = _aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions(**encryption_at_rest)
        if isinstance(fine_grained_access_control, dict):
            fine_grained_access_control = _aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions(**fine_grained_access_control)
        if isinstance(logging, dict):
            logging = _aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions(**logging)
        if isinstance(off_peak_window_start, dict):
            off_peak_window_start = _aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime(**off_peak_window_start)
        if isinstance(zone_awareness, dict):
            zone_awareness = _aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig(**zone_awareness)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a03703d95a993787b5270999ca3d7b38b3d63d6e700bf60381cbce055e48843c)
            check_type(argname="argument version", value=version, expected_type=type_hints["version"])
            check_type(argname="argument access_policies", value=access_policies, expected_type=type_hints["access_policies"])
            check_type(argname="argument advanced_options", value=advanced_options, expected_type=type_hints["advanced_options"])
            check_type(argname="argument automated_snapshot_start_hour", value=automated_snapshot_start_hour, expected_type=type_hints["automated_snapshot_start_hour"])
            check_type(argname="argument capacity", value=capacity, expected_type=type_hints["capacity"])
            check_type(argname="argument cognito_dashboards_auth", value=cognito_dashboards_auth, expected_type=type_hints["cognito_dashboards_auth"])
            check_type(argname="argument cold_storage_enabled", value=cold_storage_enabled, expected_type=type_hints["cold_storage_enabled"])
            check_type(argname="argument custom_endpoint", value=custom_endpoint, expected_type=type_hints["custom_endpoint"])
            check_type(argname="argument domain_name", value=domain_name, expected_type=type_hints["domain_name"])
            check_type(argname="argument ebs", value=ebs, expected_type=type_hints["ebs"])
            check_type(argname="argument enable_auto_software_update", value=enable_auto_software_update, expected_type=type_hints["enable_auto_software_update"])
            check_type(argname="argument enable_version_upgrade", value=enable_version_upgrade, expected_type=type_hints["enable_version_upgrade"])
            check_type(argname="argument encryption_at_rest", value=encryption_at_rest, expected_type=type_hints["encryption_at_rest"])
            check_type(argname="argument enforce_https", value=enforce_https, expected_type=type_hints["enforce_https"])
            check_type(argname="argument fine_grained_access_control", value=fine_grained_access_control, expected_type=type_hints["fine_grained_access_control"])
            check_type(argname="argument ip_address_type", value=ip_address_type, expected_type=type_hints["ip_address_type"])
            check_type(argname="argument logging", value=logging, expected_type=type_hints["logging"])
            check_type(argname="argument node_to_node_encryption", value=node_to_node_encryption, expected_type=type_hints["node_to_node_encryption"])
            check_type(argname="argument off_peak_window_enabled", value=off_peak_window_enabled, expected_type=type_hints["off_peak_window_enabled"])
            check_type(argname="argument off_peak_window_start", value=off_peak_window_start, expected_type=type_hints["off_peak_window_start"])
            check_type(argname="argument removal_policy", value=removal_policy, expected_type=type_hints["removal_policy"])
            check_type(argname="argument security_groups", value=security_groups, expected_type=type_hints["security_groups"])
            check_type(argname="argument suppress_logs_resource_policy", value=suppress_logs_resource_policy, expected_type=type_hints["suppress_logs_resource_policy"])
            check_type(argname="argument tls_security_policy", value=tls_security_policy, expected_type=type_hints["tls_security_policy"])
            check_type(argname="argument use_unsigned_basic_auth", value=use_unsigned_basic_auth, expected_type=type_hints["use_unsigned_basic_auth"])
            check_type(argname="argument vpc", value=vpc, expected_type=type_hints["vpc"])
            check_type(argname="argument vpc_subnets", value=vpc_subnets, expected_type=type_hints["vpc_subnets"])
            check_type(argname="argument zone_awareness", value=zone_awareness, expected_type=type_hints["zone_awareness"])
            check_type(argname="argument masteruser", value=masteruser, expected_type=type_hints["masteruser"])
            check_type(argname="argument program", value=program, expected_type=type_hints["program"])
            check_type(argname="argument project", value=project, expected_type=type_hints["project"])
            check_type(argname="argument tier", value=tier, expected_type=type_hints["tier"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "version": version,
            "masteruser": masteruser,
            "program": program,
            "project": project,
            "tier": tier,
        }
        if access_policies is not None:
            self._values["access_policies"] = access_policies
        if advanced_options is not None:
            self._values["advanced_options"] = advanced_options
        if automated_snapshot_start_hour is not None:
            self._values["automated_snapshot_start_hour"] = automated_snapshot_start_hour
        if capacity is not None:
            self._values["capacity"] = capacity
        if cognito_dashboards_auth is not None:
            self._values["cognito_dashboards_auth"] = cognito_dashboards_auth
        if cold_storage_enabled is not None:
            self._values["cold_storage_enabled"] = cold_storage_enabled
        if custom_endpoint is not None:
            self._values["custom_endpoint"] = custom_endpoint
        if domain_name is not None:
            self._values["domain_name"] = domain_name
        if ebs is not None:
            self._values["ebs"] = ebs
        if enable_auto_software_update is not None:
            self._values["enable_auto_software_update"] = enable_auto_software_update
        if enable_version_upgrade is not None:
            self._values["enable_version_upgrade"] = enable_version_upgrade
        if encryption_at_rest is not None:
            self._values["encryption_at_rest"] = encryption_at_rest
        if enforce_https is not None:
            self._values["enforce_https"] = enforce_https
        if fine_grained_access_control is not None:
            self._values["fine_grained_access_control"] = fine_grained_access_control
        if ip_address_type is not None:
            self._values["ip_address_type"] = ip_address_type
        if logging is not None:
            self._values["logging"] = logging
        if node_to_node_encryption is not None:
            self._values["node_to_node_encryption"] = node_to_node_encryption
        if off_peak_window_enabled is not None:
            self._values["off_peak_window_enabled"] = off_peak_window_enabled
        if off_peak_window_start is not None:
            self._values["off_peak_window_start"] = off_peak_window_start
        if removal_policy is not None:
            self._values["removal_policy"] = removal_policy
        if security_groups is not None:
            self._values["security_groups"] = security_groups
        if suppress_logs_resource_policy is not None:
            self._values["suppress_logs_resource_policy"] = suppress_logs_resource_policy
        if tls_security_policy is not None:
            self._values["tls_security_policy"] = tls_security_policy
        if use_unsigned_basic_auth is not None:
            self._values["use_unsigned_basic_auth"] = use_unsigned_basic_auth
        if vpc is not None:
            self._values["vpc"] = vpc
        if vpc_subnets is not None:
            self._values["vpc_subnets"] = vpc_subnets
        if zone_awareness is not None:
            self._values["zone_awareness"] = zone_awareness

    @builtins.property
    def version(self) -> _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion:
        '''The Elasticsearch/OpenSearch version that your domain will leverage.'''
        result = self._values.get("version")
        assert result is not None, "Required property 'version' is missing"
        return typing.cast(_aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion, result)

    @builtins.property
    def access_policies(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]]:
        '''Domain access policies.

        :default: - No access policies.
        '''
        result = self._values.get("access_policies")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]], result)

    @builtins.property
    def advanced_options(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Additional options to specify for the Amazon OpenSearch Service domain.

        :default: - no advanced options are specified

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createupdatedomains.html#createdomain-configure-advanced-options
        '''
        result = self._values.get("advanced_options")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    @builtins.property
    def automated_snapshot_start_hour(self) -> typing.Optional[jsii.Number]:
        '''The hour in UTC during which the service takes an automated daily snapshot of the indices in the Amazon OpenSearch Service domain.

        Only applies for Elasticsearch versions
        below 5.3.

        :default: - Hourly automated snapshots not used
        '''
        result = self._values.get("automated_snapshot_start_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def capacity(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig]:
        '''The cluster capacity configuration for the Amazon OpenSearch Service domain.

        :default: - 1 r5.large.search data node; no dedicated master nodes.
        '''
        result = self._values.get("capacity")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig], result)

    @builtins.property
    def cognito_dashboards_auth(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions]:
        '''Configures Amazon OpenSearch Service to use Amazon Cognito authentication for OpenSearch Dashboards.

        :default: - Cognito not used for authentication to OpenSearch Dashboards.
        '''
        result = self._values.get("cognito_dashboards_auth")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions], result)

    @builtins.property
    def cold_storage_enabled(self) -> typing.Optional[builtins.bool]:
        '''Whether to enable or disable cold storage on the domain.

        You must enable UltraWarm storage to enable cold storage.

        :default: - undefined

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/cold-storage.html
        '''
        result = self._values.get("cold_storage_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def custom_endpoint(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions]:
        '''To configure a custom domain configure these options.

        If you specify a Route53 hosted zone it will create a CNAME record and use DNS validation for the certificate

        :default: - no custom domain endpoint will be configured
        '''
        result = self._values.get("custom_endpoint")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions], result)

    @builtins.property
    def domain_name(self) -> typing.Optional[builtins.str]:
        '''Enforces a particular physical domain name.

        :default: - A name will be auto-generated.
        '''
        result = self._values.get("domain_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def ebs(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions]:
        '''The configurations of Amazon Elastic Block Store (Amazon EBS) volumes that are attached to data nodes in the Amazon OpenSearch Service domain.

        :default: - 10 GiB General Purpose (SSD) volumes per node.
        '''
        result = self._values.get("ebs")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions], result)

    @builtins.property
    def enable_auto_software_update(self) -> typing.Optional[builtins.bool]:
        '''Specifies whether automatic service software updates are enabled for the domain.

        :default: - false

        :see: https://docs.aws.amazon.com/it_it/AWSCloudFormation/latest/UserGuide/aws-properties-opensearchservice-domain-softwareupdateoptions.html
        '''
        result = self._values.get("enable_auto_software_update")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def enable_version_upgrade(self) -> typing.Optional[builtins.bool]:
        '''To upgrade an Amazon OpenSearch Service domain to a new version, rather than replacing the entire domain resource, use the EnableVersionUpgrade update policy.

        :default: - false

        :see: https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-attribute-updatepolicy.html#cfn-attributes-updatepolicy-upgradeopensearchdomain
        '''
        result = self._values.get("enable_version_upgrade")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def encryption_at_rest(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions]:
        '''Encryption at rest options for the cluster.

        :default: - No encryption at rest
        '''
        result = self._values.get("encryption_at_rest")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions], result)

    @builtins.property
    def enforce_https(self) -> typing.Optional[builtins.bool]:
        '''True to require that all traffic to the domain arrive over HTTPS.

        :default: - false
        '''
        result = self._values.get("enforce_https")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def fine_grained_access_control(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions]:
        '''Specifies options for fine-grained access control.

        Requires Elasticsearch version 6.7 or later or OpenSearch version 1.0 or later. Enabling fine-grained access control
        also requires encryption of data at rest and node-to-node encryption, along with
        enforced HTTPS.

        :default: - fine-grained access control is disabled
        '''
        result = self._values.get("fine_grained_access_control")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions], result)

    @builtins.property
    def ip_address_type(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType]:
        '''Specify either dual stack or IPv4 as your IP address type.

        Dual stack allows you to share domain resources across IPv4 and IPv6 address types, and is the recommended option.

        If you set your IP address type to dual stack, you can't change your address type later.

        :default: - IpAddressType.IPV4
        '''
        result = self._values.get("ip_address_type")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType], result)

    @builtins.property
    def logging(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions]:
        '''Configuration log publishing configuration options.

        :default: - No logs are published
        '''
        result = self._values.get("logging")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions], result)

    @builtins.property
    def node_to_node_encryption(self) -> typing.Optional[builtins.bool]:
        '''Specify true to enable node to node encryption.

        Requires Elasticsearch version 6.0 or later or OpenSearch version 1.0 or later.

        :default: - Node to node encryption is not enabled.
        '''
        result = self._values.get("node_to_node_encryption")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def off_peak_window_enabled(self) -> typing.Optional[builtins.bool]:
        '''Options for enabling a domain's off-peak window, during which OpenSearch Service can perform mandatory configuration changes on the domain.

        Off-peak windows were introduced on February 16, 2023.
        All domains created before this date have the off-peak window disabled by default.
        You must manually enable and configure the off-peak window for these domains.
        All domains created after this date will have the off-peak window enabled by default.
        You can't disable the off-peak window for a domain after it's enabled.

        :default: - Disabled for domains created before February 16, 2023. Enabled for domains created after. Enabled if ``offPeakWindowStart`` is set.

        :see: https://docs.aws.amazon.com/it_it/AWSCloudFormation/latest/UserGuide/aws-properties-opensearchservice-domain-offpeakwindow.html
        '''
        result = self._values.get("off_peak_window_enabled")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def off_peak_window_start(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime]:
        '''Start time for the off-peak window, in Coordinated Universal Time (UTC).

        The window length will always be 10 hours, so you can't specify an end time.
        For example, if you specify 11:00 P.M. UTC as a start time, the end time will automatically be set to 9:00 A.M.

        :default: - 10:00 P.M. local time
        '''
        result = self._values.get("off_peak_window_start")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime], result)

    @builtins.property
    def removal_policy(self) -> typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy]:
        '''Policy to apply when the domain is removed from the stack.

        :default: RemovalPolicy.RETAIN
        '''
        result = self._values.get("removal_policy")
        return typing.cast(typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy], result)

    @builtins.property
    def security_groups(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]]:
        '''The list of security groups that are associated with the VPC endpoints for the domain.

        Only used if ``vpc`` is specified.

        :default: - One new security group is created.

        :see: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html
        '''
        result = self._values.get("security_groups")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]], result)

    @builtins.property
    def suppress_logs_resource_policy(self) -> typing.Optional[builtins.bool]:
        '''Specify whether to create a CloudWatch Logs resource policy or not.

        When logging is enabled for the domain, a CloudWatch Logs resource policy is created by default.
        However, CloudWatch Logs supports only 10 resource policies per region.
        If you enable logging for several domains, it may hit the quota and cause an error.
        By setting this property to true, creating a resource policy is suppressed, allowing you to avoid this problem.

        If you set this option to true, you must create a resource policy before deployment.

        :default: - false

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/createdomain-configure-slow-logs.html
        '''
        result = self._values.get("suppress_logs_resource_policy")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def tls_security_policy(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy]:
        '''The minimum TLS version required for traffic to the domain.

        :default: - TLSSecurityPolicy.TLS_1_2
        '''
        result = self._values.get("tls_security_policy")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy], result)

    @builtins.property
    def use_unsigned_basic_auth(self) -> typing.Optional[builtins.bool]:
        '''Configures the domain so that unsigned basic auth is enabled.

        If no master user is provided a default master user
        with username ``admin`` and a dynamically generated password stored in KMS is created. The password can be retrieved
        by getting ``masterUserPassword`` from the domain instance.

        Setting this to true will also add an access policy that allows unsigned
        access, enable node to node encryption, encryption at rest. If conflicting
        settings are encountered (like disabling encryption at rest) enabling this
        setting will cause a failure.

        :default: - false
        '''
        result = self._values.get("use_unsigned_basic_auth")
        return typing.cast(typing.Optional[builtins.bool], result)

    @builtins.property
    def vpc(self) -> typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc]:
        '''Place the domain inside this VPC.

        :default: - Domain is not placed in a VPC.

        :see: https://docs.aws.amazon.com/opensearch-service/latest/developerguide/vpc.html
        '''
        result = self._values.get("vpc")
        return typing.cast(typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc], result)

    @builtins.property
    def vpc_subnets(
        self,
    ) -> typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]]:
        '''The specific vpc subnets the domain will be placed in.

        You must provide one subnet for each Availability Zone
        that your domain uses. For example, you must specify three subnet IDs for a three Availability Zone
        domain.

        Only used if ``vpc`` is specified.

        :default: - All private subnets.

        :see: https://docs.aws.amazon.com/vpc/latest/userguide/VPC_Subnets.html
        '''
        result = self._values.get("vpc_subnets")
        return typing.cast(typing.Optional[typing.List[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection]], result)

    @builtins.property
    def zone_awareness(
        self,
    ) -> typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig]:
        '''The cluster zone awareness configuration for the Amazon OpenSearch Service domain.

        :default: - no zone awareness (1 AZ)
        '''
        result = self._values.get("zone_awareness")
        return typing.cast(typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig], result)

    @builtins.property
    def masteruser(self) -> builtins.str:
        result = self._values.get("masteruser")
        assert result is not None, "Required property 'masteruser' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def program(self) -> builtins.str:
        result = self._values.get("program")
        assert result is not None, "Required property 'program' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project(self) -> builtins.str:
        result = self._values.get("project")
        assert result is not None, "Required property 'project' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def tier(self) -> builtins.str:
        result = self._values.get("tier")
        assert result is not None, "Required property 'tier' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Opensearch(
    _constructs_77d1e7e8.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="fnl-aws-cdk.Opensearch",
):
    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        masteruser: builtins.str,
        program: builtins.str,
        project: builtins.str,
        tier: builtins.str,
        version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
        access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
        advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
        capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
        cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        cold_storage_enabled: typing.Optional[builtins.bool] = None,
        custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        domain_name: typing.Optional[builtins.str] = None,
        ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enable_auto_software_update: typing.Optional[builtins.bool] = None,
        enable_version_upgrade: typing.Optional[builtins.bool] = None,
        encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        enforce_https: typing.Optional[builtins.bool] = None,
        fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
        logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
        node_to_node_encryption: typing.Optional[builtins.bool] = None,
        off_peak_window_enabled: typing.Optional[builtins.bool] = None,
        off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
        removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
        security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
        suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
        tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
        use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
        vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
        vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
        zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param scope: -
        :param id: -
        :param masteruser: 
        :param program: 
        :param project: 
        :param tier: 
        :param version: The Elasticsearch/OpenSearch version that your domain will leverage.
        :param access_policies: Domain access policies. Default: - No access policies.
        :param advanced_options: Additional options to specify for the Amazon OpenSearch Service domain. Default: - no advanced options are specified
        :param automated_snapshot_start_hour: The hour in UTC during which the service takes an automated daily snapshot of the indices in the Amazon OpenSearch Service domain. Only applies for Elasticsearch versions below 5.3. Default: - Hourly automated snapshots not used
        :param capacity: The cluster capacity configuration for the Amazon OpenSearch Service domain. Default: - 1 r5.large.search data node; no dedicated master nodes.
        :param cognito_dashboards_auth: Configures Amazon OpenSearch Service to use Amazon Cognito authentication for OpenSearch Dashboards. Default: - Cognito not used for authentication to OpenSearch Dashboards.
        :param cold_storage_enabled: Whether to enable or disable cold storage on the domain. You must enable UltraWarm storage to enable cold storage. Default: - undefined
        :param custom_endpoint: To configure a custom domain configure these options. If you specify a Route53 hosted zone it will create a CNAME record and use DNS validation for the certificate Default: - no custom domain endpoint will be configured
        :param domain_name: Enforces a particular physical domain name. Default: - A name will be auto-generated.
        :param ebs: The configurations of Amazon Elastic Block Store (Amazon EBS) volumes that are attached to data nodes in the Amazon OpenSearch Service domain. Default: - 10 GiB General Purpose (SSD) volumes per node.
        :param enable_auto_software_update: Specifies whether automatic service software updates are enabled for the domain. Default: - false
        :param enable_version_upgrade: To upgrade an Amazon OpenSearch Service domain to a new version, rather than replacing the entire domain resource, use the EnableVersionUpgrade update policy. Default: - false
        :param encryption_at_rest: Encryption at rest options for the cluster. Default: - No encryption at rest
        :param enforce_https: True to require that all traffic to the domain arrive over HTTPS. Default: - false
        :param fine_grained_access_control: Specifies options for fine-grained access control. Requires Elasticsearch version 6.7 or later or OpenSearch version 1.0 or later. Enabling fine-grained access control also requires encryption of data at rest and node-to-node encryption, along with enforced HTTPS. Default: - fine-grained access control is disabled
        :param ip_address_type: Specify either dual stack or IPv4 as your IP address type. Dual stack allows you to share domain resources across IPv4 and IPv6 address types, and is the recommended option. If you set your IP address type to dual stack, you can't change your address type later. Default: - IpAddressType.IPV4
        :param logging: Configuration log publishing configuration options. Default: - No logs are published
        :param node_to_node_encryption: Specify true to enable node to node encryption. Requires Elasticsearch version 6.0 or later or OpenSearch version 1.0 or later. Default: - Node to node encryption is not enabled.
        :param off_peak_window_enabled: Options for enabling a domain's off-peak window, during which OpenSearch Service can perform mandatory configuration changes on the domain. Off-peak windows were introduced on February 16, 2023. All domains created before this date have the off-peak window disabled by default. You must manually enable and configure the off-peak window for these domains. All domains created after this date will have the off-peak window enabled by default. You can't disable the off-peak window for a domain after it's enabled. Default: - Disabled for domains created before February 16, 2023. Enabled for domains created after. Enabled if ``offPeakWindowStart`` is set.
        :param off_peak_window_start: Start time for the off-peak window, in Coordinated Universal Time (UTC). The window length will always be 10 hours, so you can't specify an end time. For example, if you specify 11:00 P.M. UTC as a start time, the end time will automatically be set to 9:00 A.M. Default: - 10:00 P.M. local time
        :param removal_policy: Policy to apply when the domain is removed from the stack. Default: RemovalPolicy.RETAIN
        :param security_groups: The list of security groups that are associated with the VPC endpoints for the domain. Only used if ``vpc`` is specified. Default: - One new security group is created.
        :param suppress_logs_resource_policy: Specify whether to create a CloudWatch Logs resource policy or not. When logging is enabled for the domain, a CloudWatch Logs resource policy is created by default. However, CloudWatch Logs supports only 10 resource policies per region. If you enable logging for several domains, it may hit the quota and cause an error. By setting this property to true, creating a resource policy is suppressed, allowing you to avoid this problem. If you set this option to true, you must create a resource policy before deployment. Default: - false
        :param tls_security_policy: The minimum TLS version required for traffic to the domain. Default: - TLSSecurityPolicy.TLS_1_2
        :param use_unsigned_basic_auth: Configures the domain so that unsigned basic auth is enabled. If no master user is provided a default master user with username ``admin`` and a dynamically generated password stored in KMS is created. The password can be retrieved by getting ``masterUserPassword`` from the domain instance. Setting this to true will also add an access policy that allows unsigned access, enable node to node encryption, encryption at rest. If conflicting settings are encountered (like disabling encryption at rest) enabling this setting will cause a failure. Default: - false
        :param vpc: Place the domain inside this VPC. Default: - Domain is not placed in a VPC.
        :param vpc_subnets: The specific vpc subnets the domain will be placed in. You must provide one subnet for each Availability Zone that your domain uses. For example, you must specify three subnet IDs for a three Availability Zone domain. Only used if ``vpc`` is specified. Default: - All private subnets.
        :param zone_awareness: The cluster zone awareness configuration for the Amazon OpenSearch Service domain. Default: - no zone awareness (1 AZ)
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f289e3d47be66538820883b9d9b9bf3cfb3334b7a1c223666d909f6c00b61b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        props = CustomProps(
            masteruser=masteruser,
            program=program,
            project=project,
            tier=tier,
            version=version,
            access_policies=access_policies,
            advanced_options=advanced_options,
            automated_snapshot_start_hour=automated_snapshot_start_hour,
            capacity=capacity,
            cognito_dashboards_auth=cognito_dashboards_auth,
            cold_storage_enabled=cold_storage_enabled,
            custom_endpoint=custom_endpoint,
            domain_name=domain_name,
            ebs=ebs,
            enable_auto_software_update=enable_auto_software_update,
            enable_version_upgrade=enable_version_upgrade,
            encryption_at_rest=encryption_at_rest,
            enforce_https=enforce_https,
            fine_grained_access_control=fine_grained_access_control,
            ip_address_type=ip_address_type,
            logging=logging,
            node_to_node_encryption=node_to_node_encryption,
            off_peak_window_enabled=off_peak_window_enabled,
            off_peak_window_start=off_peak_window_start,
            removal_policy=removal_policy,
            security_groups=security_groups,
            suppress_logs_resource_policy=suppress_logs_resource_policy,
            tls_security_policy=tls_security_policy,
            use_unsigned_basic_auth=use_unsigned_basic_auth,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            zone_awareness=zone_awareness,
        )

        jsii.create(self.__class__, self, [scope, id, props])


__all__ = [
    "CustomProps",
    "Opensearch",
]

publication.publish()

def _typecheckingstub__a03703d95a993787b5270999ca3d7b38b3d63d6e700bf60381cbce055e48843c(
    *,
    version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
    access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
    capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cold_storage_enabled: typing.Optional[builtins.bool] = None,
    custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    domain_name: typing.Optional[builtins.str] = None,
    ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_auto_software_update: typing.Optional[builtins.bool] = None,
    enable_version_upgrade: typing.Optional[builtins.bool] = None,
    encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enforce_https: typing.Optional[builtins.bool] = None,
    fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
    logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    node_to_node_encryption: typing.Optional[builtins.bool] = None,
    off_peak_window_enabled: typing.Optional[builtins.bool] = None,
    off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
    tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
    use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    masteruser: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f289e3d47be66538820883b9d9b9bf3cfb3334b7a1c223666d909f6c00b61b(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    masteruser: builtins.str,
    program: builtins.str,
    project: builtins.str,
    tier: builtins.str,
    version: _aws_cdk_aws_opensearchservice_ceddda9d.EngineVersion,
    access_policies: typing.Optional[typing.Sequence[_aws_cdk_aws_iam_ceddda9d.PolicyStatement]] = None,
    advanced_options: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    automated_snapshot_start_hour: typing.Optional[jsii.Number] = None,
    capacity: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CapacityConfig, typing.Dict[builtins.str, typing.Any]]] = None,
    cognito_dashboards_auth: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CognitoOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    cold_storage_enabled: typing.Optional[builtins.bool] = None,
    custom_endpoint: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.CustomEndpointOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    domain_name: typing.Optional[builtins.str] = None,
    ebs: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EbsOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enable_auto_software_update: typing.Optional[builtins.bool] = None,
    enable_version_upgrade: typing.Optional[builtins.bool] = None,
    encryption_at_rest: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.EncryptionAtRestOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    enforce_https: typing.Optional[builtins.bool] = None,
    fine_grained_access_control: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.AdvancedSecurityOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    ip_address_type: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.IpAddressType] = None,
    logging: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.LoggingOptions, typing.Dict[builtins.str, typing.Any]]] = None,
    node_to_node_encryption: typing.Optional[builtins.bool] = None,
    off_peak_window_enabled: typing.Optional[builtins.bool] = None,
    off_peak_window_start: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.WindowStartTime, typing.Dict[builtins.str, typing.Any]]] = None,
    removal_policy: typing.Optional[_aws_cdk_ceddda9d.RemovalPolicy] = None,
    security_groups: typing.Optional[typing.Sequence[_aws_cdk_aws_ec2_ceddda9d.ISecurityGroup]] = None,
    suppress_logs_resource_policy: typing.Optional[builtins.bool] = None,
    tls_security_policy: typing.Optional[_aws_cdk_aws_opensearchservice_ceddda9d.TLSSecurityPolicy] = None,
    use_unsigned_basic_auth: typing.Optional[builtins.bool] = None,
    vpc: typing.Optional[_aws_cdk_aws_ec2_ceddda9d.IVpc] = None,
    vpc_subnets: typing.Optional[typing.Sequence[typing.Union[_aws_cdk_aws_ec2_ceddda9d.SubnetSelection, typing.Dict[builtins.str, typing.Any]]]] = None,
    zone_awareness: typing.Optional[typing.Union[_aws_cdk_aws_opensearchservice_ceddda9d.ZoneAwarenessConfig, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass
