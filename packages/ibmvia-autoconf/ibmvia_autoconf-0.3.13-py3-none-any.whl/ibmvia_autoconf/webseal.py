#!/bin/python3
"""
@copyright: IBM
"""

import logging
import json
import typing
import copy

from .util.configure_util import deploy_pending_changes, config_base_dir
from .util.data_util import prefix_keys, Map, FILE_LOADER, optional_list, filter_list, KUBE_CLIENT_SLEEP


_logger = logging.getLogger(__name__)


class WEB_Configurator(object):

    factory = None
    web = None
    config = Map()

    def __init__(self, config, factory):
        self.web = factory.get_web_settings()
        self.factory = factory
        self.config = config

    def __update_stanza(self, proxy_id, entry):
        rsp = self.web.reverse_proxy.update_configuration_stanza_entry(
                proxy_id, entry.stanza, entry.entry_id, entry.value)
        if rsp.success == True:
            _logger.info("Successfully updated stanza [{}] with [{}:{}]".format(
                    entry.stanza, entry.entry_id, entry.value))
        else:
            _logger.error("Failed to update stanza [{}] with [{}:{}]\n{}".format(
                    entry.stanza, entry.entry_id, entry.value, rsp.data))

    def __add_stanza(self, proxy_id, entry):
        rsp = None
        if entry.entry_id:
            rsp = self.web.reverse_proxy.add_configuration_stanza_entry(
                    proxy_id, entry.stanza, entry.entry_id, entry.value)
        elif entry.stanza:
            rsp = self.web.reverse_proxy.add_configuration_stanza(proxy_id, entry.stanza)
        else:
            _logger.error("Configuration invalid:\n{}".format(json.dumps(entry, indent=4)))
            return
        if rsp.success == True:
            _logger.info("Successfully created stanza entry")
        else:
            _logger.error("Failed to create stanza entry:\n{}\n{}".format(json.dumps(entry, indent=4), rsp.data))

    def __delete_stanza(self, proxy_id, entry):
        rsp = None
        if entry.entry_id:
            rsp = self.web.reverse_proxy.delete_configuration_stanza_entry(proxy_id, entry.stanza, entry.entry_id,
                    entry.value)
        elif entry.stanza:
            rsp = self.web.reverse_proxy.delete_configuration_stanza(proxy_id, entry.stana)
        else:
            _logger.error("Stanza configuration entry invalid:\n{}".format(json.dumps(entry, indent=4)))
            return
        if rsp.success == True:
            _logger.info("Successfully deleted stanza entry")
        else:
            _logger.error("Failed to delete stanza entry:\n{}\n{}".format(json.dumps(entry, indent=4), rsp.data))

    def _configure_stanza(self, proxy_id, config):
        for entry in config:
            if entry.operation == "delete":
                self.__delete_stanza(proxy_id, entry)
            elif entry.operation == "add":
                self.__add_stanza(proxy_id, entry)
            elif entry.operation == "update":
                self.__update_stanza(proxy_id, entry)
            else:
                _logger.error("Unknown operation {} in stanza entry: {}".format(
                    entry.operation, json.dumps(entry, indent=4)))

    def _configure_aac(self, proxy_id, aac_config):
        methodArgs = {
                "junction": aac_config.junction,
                "reuse_certs": aac_config.reuse_certs,
                "reuse_acls": aac_config.reuse_acls
            }
        if aac_config.runtime:
            methodArgs.update({
                                "runtime_hostname": aac_config.runtime.hostname,
                                "runtime_port": aac_config.runtime.port,
                                "runtime_username": aac_config.runtime.username,
                                "runtime_password": aac_config.runtime.password
                            })
        rsp = self.web.reverse_proxy.configure_aac(proxy_id, **methodArgs)
        if rsp.success == True:
            _logger.info("Successfully ran Advanced Access Control configuration wizard on {} proxy instance".format(proxy_id))
        else:
            _logger.error("Failed to run AAC configuration wizard on {} proxy instance with config:\n{}\n{}".format(
                proxy_id, json.dumps(aac_config, indent=4), rsp.data))


    def _configure_mmfa(self, proxy_id, mmfa_config):
        methodArgs = {
                "reuse_acls": mmfa_config.reuse_acls,
                "reuse_pops": mmfa_config.reuse_pops,
                "reuse_certs": mmfa_config.reuse_certs,
                "channel": mmfa_config.channel
            }
        if mmfa_config.lmi:
            lmi = mmfa_config.lmi
            methodArgs.update({
                    "lmi_hostname": lmi.hostname,
                    "lmi_port": lmi.port,
                    "lmi_username": lmi.username,
                    "lmi_password": lmi.password
                })
        if mmfa_config.runtime:
            runtime = mmfa_config.runtime
            methodArgs.update({
                    "runtime_hostname": runtime.hostname,
                    "runtime_port": runtime.port,
                    "runtime_username": runtime.username,
                    "runtime_password": runtime.password
                })
        rsp = self.web.reverse_proxy.configure_mmfa(proxy_id, **methodArgs)
        if rsp.success == True:
            _logger.info("Successfully ran MMFA configuration wizard on {} proxy instance".format(proxy_id))
        else:
            _logger.error("Failed to run MMFA configuration wizard on {} proxy instance with config:\n{}\n{}".format(
                proxy_id, json.dumps(mmfa_config, indent=4), rsp.data))


    def _configure_federations(self, proxy_id, fed_config):
        federations = optional_list(
                self.factory.get_federation().federations.list_federations().json)
        for fc in fed_config:
            #Convert federation name to uuid
            fed_cfg = copy.deepcopy(fc)
            fed_cfg['federation_id'] = optional_list(filter_list(
                        'name', fed_cfg.pop('name', "MISSING"), federations))[0].get("id", "-1")
            prefix_keys(fed_cfg, "runtime", "runtime_")
            #Run the wizard
            #_logger.debug("Federation wizard request {}".format(json.dumps(fed_cfg, indent=4)))
            rsp = self.web.reverse_proxy.configure_fed(proxy_id, **fed_cfg)
            if rsp.success == True:
                _logger.info("Successfully ran federation configuration utility for {} federation.".format(fc.name))
            else:
                _logger.error("Federation configuration wizard did not run successfully with config:\n{}\n{}".format(
                    json.dumps(fc, indent=4), rsp.data))


    def _configure_api_protection(self, proxy_id, api_config):
        methodArgs = {
                "junction": api_config.junction,
                "reuse_acls": api_config.reuse_acls,
                "reuse_certs": api_config.reuse_certs,
                "api": api_config.api,
                "browser": api_config.browser,
                "auth_register": api_config.auth_register,
                "fapi_compliant": api_config.fapi_compliant
        }
        if api_config.runtime:
            runtime = api_config.runtime
            methodArgs.update({
                    "hostname": runtime.hostname,
                    "port": runtime.port,
                    "username": runtime.username,
                    "password": runtime.password
            })
        rsp = self.web.reverse_proxy.configure_api_protection(proxy_id, **methodArgs)
        if rsp.success == True:
            _logger.info("Successfully created API protection junction {}".format(api_config.junction))
        else:
            _logger.error("Failed to create API protection junction:\n{}\n{}".format(
                    json.dumps(api_config, indent=4), rsp.data))


    def _add_junction(self, proxy_id, junction):
        forceJunction = "no"
        oldJunction = optional_list(filter_list("id", junction.junction_point, self.web.reverse_proxy.list_junctions(proxy_id).json))[0]
        if oldJunction:
            forceJunction = "yes"
        junction['force'] = forceJunction

        rsp = self.web.reverse_proxy.create_junction(proxy_id, **junction)

        if rsp.success == True:
            _logger.info("Successfully added junction to {} proxy".format(proxy_id))
        else:
            _logger.error("Failed to add junction to {} with config:\n{}\n{}".format(
                proxy_id, json.dumps(junction, indent=4), rsp.data))

    def _import_management_root(self, proxy_id, zip_file):
        path = optional_list(FILE_LOADER.read_file(zip_file))[0].get("path", "MISSING_PATH")
        rsp = self.web.reverse_proxy.import_management_root_files(proxy_id, path)
        if rsp.success == True:
            _logger.info("Successfully imported {} to {} proxy management root".format(
                zip_file, proxy_id))
        else:
            _logger.error("Failed to import {} to {} proxy:\n{}".format(
                                        path, proxy_id, rsp.data))

    class Reverse_Proxy(typing.TypedDict):
        '''
        .. note:: Configuration to connect to the user registry is read from the ``webseal.runtime`` entry.

        Example::

                  reverse_proxy:
                  - name: "default"
                    host: "ibmsec.verify.access"
                    listening_port: 7234
                    domain: "Default"
                    http:
                    - enabled: "no"
                    https:
                    - enabled: "yes"
                      port: 443
                    junctions:
                    - junction_point: "/app"
                      description: "Backend Application"
                      junction_type: "ssl"
                      transparent_path: true
                      server_hostname: "1.2.3.4"
                      server_port: 443
                      remote_http_header:
                      - "iv-user"
                      - "iv-groups"
                      - "iv-creds"
                    aac_configuration:
                      hostname: "localhost"
                      port: 443
                      runtime:
                        user: !secret default/isva-secrets:runtime_user
                        password: !secret default/isva-secrets:runtime_password
                      junction: "/mga"
                      reuse_acls: True
                      reuse_certs: True

        '''

        class AAC_Configuration(typing.TypedDict):
            class Liberty_Server(typing.TypedDict):
                hostname: str
                'Hostname or address of server.'
                port: int
                'Port server is listening on.'
                username: str
                'Username to use for basic authentication.'
                password: str
                'Password to use for basic authentication.'

            junction: str
            'Junction to create.'
            runtime: Liberty_Server
            'Liberty runtime server properties.'
            reuse_acls: bool
            'Re-use existing Policy Server ACL\'s'
            reuse_certs: bool
            'Re-use existing certificates in the SSL database.'

        class MMFA_Configuration(typing.TypedDict):
            class Liberty_Server(typing.TypedDict):
                hostname: str
                'Hostname or address of server.'
                port: int
                'Port server is listening on.'
                username: str
                'Username to use for basic authentication.'
                password: str
                'Password to use for basic authentication.'

            channel: str
            'MMFA channel to configure. ``mobile`` | ``browser`` | ``both``.'
            runtime: Liberty_Server
            'Liberty runtime server properties.'
            lmi: Liberty_Server
            'Liberty LMI server properties.'
            reuse_acls: bool
            'Re-use existing Policy Server ACL\'s'
            reuse_certs: bool
            'Re-use existing certificates in the SSL database.'
            reuse_pops: bool
            'Re-use existing Policy Server POP\'s'

        class Federation_Configuration(typing.TypedDict):
            class Liberty_Server(typing.TypedDict):
                hostname: str
                'Hostname or address of server.'
                port: int
                'Port server is listening on.'
                username: str
                'Username to use for basic authentication.'
                password: str
                'Password to use for basic authentication.'
                type: typing.Optional[str]
                'Type of runtime. Valid values are "local" for local runtimes (appliance) and "remote" for external runtime (container). Default is "local"'
                load_cert: typing.Optional[str]
                'Read the X.509 Certificate from the runtime server\'s https endpoint. Default is "on" (read the cert)'
                enable_mtls: typing.Optional[bool]
                'Boolean option indicates if mutual TLS (client certificate) authentication should be performed with the runtime server. Default is `false`.'

            name: str
            'Name of the Federation.'
            runtime: Liberty_Server
            'Liberty runtime server properties.'
            reuse_acls: bool
            'Re-use existing Policy Server ACL\'s'
            reuse_certs: bool
            'Re-use existing certificates in the SSL database.'

        class ApiProtectionConfiguration(typing.TypedDict):
            class Liberty_Server(typing.TypedDict):
                hostname: str
                'Hostname or address of server.'
                port: int
                'Port server is listening on.'
                username: str
                'Username to use for basic authentication.'
                password: str
                'Password to use for basic authentication.'

            junction: str
            'Name of the API Protection Junction.'
            runtime: Liberty_Server
            'Liberty runtime server properties.'
            reuse_acls: bool
            'Re-use existing Policy Server ACL\'s'
            reuse_certs: bool
            'Re-use existing certificates in the SSL database.'
            api: typing.Optional[bool]
            'Should this reverse proxy be configured for API protection. Default is ``false``.'
            browser: typing.Optional[bool]
            'Should this reverse proxy be configured for Browser interaction. Default is ``false``.'
            auth_register: typing.Optional[bool]
            'Will the client registration endpoint require authentication. Default is ``false``.'
            fapi_compliant: typing.Optional[bool]
            'Configures reverse proxy instance to be FAPI Compliant. Default is ``false``.'
            
        class Stanza_Configuration(typing.TypedDict):
            operation:str
            'Operation to perform on configuration file. Valid values include ``add``, ``delete`` and ``update``.'
            stanza: str
            'Name of stanza to modify.'
            entry_id: typing.Optional[str]
            'Optional entry name to modify.'
            value: typing.Optional[str]
            'Optional entry value to modify.'

        class Junction(typing.TypedDict):
            junction_type: str
            'Type of junction.'
            junction_point: str
            'Name of the location in the Reverse Proxy namespace where the root of the back-end application server namespace is mounted.'
            description: typing.Optional[str]
            'An optional description for this junction.'
            server_hostname: str
            'The DNS host name or IP address of the target back-end server.'
            server_port: str
            'TCP port of the back-end third-party server.'
            basic_auth_mode: str
            'Defines how the Reverse Proxy server passes client identity information in HTTP basic authentication (BA) headers to the back-end server.'
            tfim_sso: bool
            'Enables IBM Security Federated Identity Manager single sign-on (SSO) for the junction. ``yes`` | ``no``'
            stateful_junction: str
            'Specifies whether the junction supports stateful applications. ``yes`` | ``no``.'
            preserve_cookie: str
            'Specifies whether modifications of the names of non-domain cookies are to be made.'
            cookie_include_path: str
            'Specifies whether script generated server-relative URLs are included in cookies for junction identification.'
            transparent_path_junction: str
            'Specifies whether a transparent path junction is created. ``yes`` | ``no``.'
            mutual_auth: bool
            'Specifies whether to enforce mutual authentication between a front-end Reverse Proxy server and a back-end Reverse Proxy server over SSL. ``yes`` | ``no``.'
            insert_ltpa_cookie: bool
            ' Controls whether LTPA cookies are passed to the junctioned Web server. ``yes`` | ``no``'
            insert_session_cookie: bool
            'Controls whether to send the session cookie to the junctioned Web server.'
            request_encoding: str
            'Specifies the encoding to use when the system generates HTTP headers for junctions.'
            enable_basic_auth: str
            'Specifies whether to use BA header information to authenticate to back-end server. ``yes`` | ``no``.'
            key_label: str
            'The key label for the client-side certificate that is used when the system authenticates to the junctioned Web server.'
            gso_resource_group: str
            'The name of the GSO resource or resource group.'
            junction_cookie_javascript_block: str
            'Controls the junction cookie JavaScript block. ``trailer`` | ``inhead`` | ``onfocus`` | ``xhtml10`` | ``httpheader``.'
            client_ip_http: str
            'Specifies whether to insert the IP address of the incoming request into an HTTP header for transmission to the junctioned Web server.'
            version_two_cookies: str
            'Specifies whether LTPA version 2 cookies (LtpaToken2) are used.'
            ltpa_keyfile: str
            'Location of the key file that is used to encrypt the LTPA cookie data.'
            ltpa_keyfile_password: str
            'Password for the key file that is used to encrypt LTPA cookie data.'
            authz_rules: str
            'Specifies whether to allow denied requests and failure reason information from authorization rules to be sent in the Boolean Rule header (AM_AZN_FAILURE) across the junction.'
            fss_config_file: str
            'The name of the configuration file that is used for forms based single sign-on.'
            username: str
            'The Reverse Proxy user name to send BA header information to the back-end server.'
            password: str
            'The Reverse Proxy password to send BA header information to the back-end server.'
            server_uuid: str
            'Specifies the UUID that will be used to identify the junctioned Web server.'
            virtual_hostname: str
            'Virtual host name that is used for the junctioned Web server.'
            server_dn: str
            'Specifies the distinguished name of the junctioned Web server.'
            server_cn: str
            'Specifies the common name, or subject alternative name, of the junctioned Web server.'
            local_ip: str
            'Specifies the local IP address that the Reverse Proxy uses when the system communicates with the target back-end server.'
            query_contents: str
            'Provides the Reverse Proxy with the correct name of the query_contents program file and where to find the file.'
            case_sensitive_url: str
            'Specifies whether the Reverse Proxy server treats URLs as case sensitive.'
            windows_style_url: str
            'Specifies whether Windows style URLs are supported.'
            proxy_hostname: str
            'The TCP port of the proxy server.'
            sms_environment: str
            'Only applicable for virtual junctions. Specifies the replica set that sessions on the virtual junction are managed under.'
            vhost_label: str
            'Only applicable for virtual junctions. Causes a second virtual junction to share the protected object space with the initial virtual junction.'
            force: bool
            'Specifies whether to overwrite an existing junction of the same name.'
            delegation_support: str
            'This option is valid only with junctions that were created with the type of ``ssl`` or ``sslproxy``.'
            scripting_support: str
            'Supplies junction identification in a cookie to handle script-generated server-relative URLs.'
            junction_hard_limit: str
            'Defines the hard limit percentage for consumption of worker threads.'
            junction_soft_limit: str
            'Defines the soft limit percentage for consumption of worker threads.'
            https_port: str
            'HTTPS port of the back-end third-party server.'
            http_port: str
            'HTTP port of the back-end third-party server.'
            proxy_port: str
            'The TCP port of the proxy server.'
            remote_http_header: typing.List[str]
            'Controls the insertion of Security Verify Identity Access specific client identity information in HTTP headers across the junction.'


        class Endpoint(typing.TypedDict):
            enabled: bool
            'Enable traffic on this endpoint.'
            port: typing.Optional[int]
            'Network port that endpoint should listen on.'

        class LDAP(typing.TypedDict):
            ssl: str
            'Enable SSL Verification of connections. ``yes`` or ``no``'
            key_file: typing.Optional[str]
            'The SSL Database to use to verify connections. Only valid if ``ssl`` is ``yes``.'
            cert_file: typing.Optional[str]
            'The SSL Certificate to use to verify connections. Only valid of ``ssl`` is ``yes``.'
            port: int
            'The network port to communicate with the LDAP server.'

        name: str
        'Name of the reverse proxy instance.'
        host: str
        'The host name that is used by the Security Verify Identity Access policy server to contact the appliance.'
        nw_interface_yn: typing.Optional[str]
        'Specifies whether to use a logical network interface for the instance. Only valid for appliance deployments. ``yes`` | ``no``.'
        ip_address: typing.Optional[str]
        'The IP address for the logical interface. Only valid for appliance deployments where ``nw_interface_yn`` is ``yes``. ``yes`` | ``no``.'
        listening_port: int
        'This is the listening port through which the instance communicates with the Security Verify Identity Access policy server.'
        domain: str
        'The Security Verify Identity Access domain.'
        ldap: LDAP
        'LDAP policy server properties.'
        http: Endpoint
        'HTTP traffic endpoint properties.'
        https: Endpoint
        'HTTPS traffic endpoint properties.'
        junctions: typing.Optional[typing.List[Junction]]
        'Junctions to backend resource servers for this reverse proxy instance.'
        aac_configuration: typing.Optional[AAC_Configuration]
        'Properties for configuring this reverse proxy instance for use with advanced access control authentication and context based access service.'
        mmfa_configuration: typing.Optional[MMFA_Configuration]
        'Properties for configuring this reverse proxy instance to deliver MMFA capabilities.'
        federation_configuration: typing.Optional[typing.List[Federation_Configuration]]
        'Properties for integrating with a running Federation runtime.'
        api_protection_configuration: typing.Optional[ApiProtectionConfiguration]
        'Properties for integrating this reverse proxy with OIDC API Protection Clients.'
        stanza_configuration: typing.Optional[Stanza_Configuration]
        'List of modifications to perform on the ``webseald.conf`` configuration file for this reverse proxy instance.'
        management_root: typing.List[str]
        'List of files to import into WebSEAL hosted pages. Directory structure should be relative to the predefined top-level directories.'

    def wrp(self, runtime, proxy):
        wrp_instances = optional_list(self.web.reverse_proxy.list_instances().json)
        for instance in wrp_instances:
            if instance and instance['id'] == proxy.name:
                rsp = self.web.reverse_proxy.delete_instance(proxy.name,
                        runtime.admin_user if runtime.admin_user else "sec_master",
                        runtime.admin_password)
                if rsp.success != True:
                    _logger.error("WebSEAL Reverse proxy {} already exists with config: \n{}\nand cannot be removed".format(
                        proxy.name, proxy))
                    return
        methodArgs = {
                        "inst_name":proxy.name,
                        "host": proxy.host,
                        "admin_id": runtime.admin_user if runtime.admin_user else "sec_master",
                        "admin_pwd": runtime.admin_password,
                        "nw_interface_yn":  proxy.nw_interface_yn,
                        "ip_address": proxy.ip_address,
                        "listening_port": proxy.listening_port,
                        "domain": proxy.domain
                }
        if proxy.http != None:
            methodArgs.update({
                        "http_yn": proxy.http.enabled,
                        "http_port": proxy.http.port,
                        })
        if proxy.https != None:
            methodArgs.update({
                        "https_yn": proxy.https.enabled,
                        "https_port": proxy.https.port,
                        })
        if proxy.ldap != None:
            methodArgs.update({
                                "ssl_yn": proxy.ldap.ssl,
                                "key_file": proxy.ldap.key_file,
                                "cert_label": proxy.ldap.cert_file,
                                "ssl_port": proxy.ldap.port,
                        })
        _logger.debug("Configuring WRP with config {}".format(methodArgs))
        rsp = self.web.reverse_proxy.create_instance(**methodArgs)
        if rsp.success == True:
            _logger.info("Successfully configured proxy {}".format(proxy.name))
        else:
            _logger.error("Configuration of {} proxy failed with config:\n{}\n{}".format(
                proxy.name, json.dumps(proxy, indent=4), rsp.data))
        if proxy.management_root != None:
            for zipPages in proxy.management_root:
                self._import_management_root(proxy.name, zipPages)

        if proxy.junctions != None:
            for jct in proxy.junctions:
                self._add_junction(proxy.name, jct)

        if proxy.aac_configuration != None:
            self._configure_aac(proxy.name, proxy.aac_configuration)

        if proxy.mmfa_configuration != None:
            self._configure_mmfa(proxy.name, proxy.mmfa_configuration)

        if proxy.federation_configuration != None:
            self._configure_federations(proxy.name, proxy.federation_configuration)

        if proxy.api_protection_configuration != None:
            self._configure_api_protection(proxy.name, proxy.api_protection_configuration)

        if proxy.stanza_configuration != None:
            self._configure_stanza(proxy.name, proxy.stanza_configuration)

        deploy_pending_changes(self.factory, self.config)
        if self.factory.is_docker() == False:
            rsp = self.web.reverse_proxy.restart_instance(proxy.name)
            if rsp.success == True:
                _logger.info("Successfully restart {} proxy instance after applying configuration".format(proxy.name))
            else:
                _logger.error("Failed to restart {} proxy instance after applying configuration".format(proxy.name))


    def _runtime_stanza(self, stanza_config):
        for entry in stanza_config:
            rsp = None
            if entry.operation == "add":
                entries = [ [entry.entry, entry.value] ] if entry.entry else None
                rsp = self.web.runtime_component.create_configuration_file_entry(resource=entry.resource,
                                                                                 stanza=entry.stanza, entries=entries)

            elif entry.operation == "update":
                if entry.entry == None or entry.value == None:
                    _logger.error("Update operation for {} is missing entry or value property, skipping".format(entry))
                    continue
                entries = [ [entry.entry, entry.value] ]
                rsp = self.web.runtime_component.update_configuration_file_entry(resource=entry.resource,
                                                                                stanza=entry.stanza, entries=entries)

            elif entry.operation == "delete":
                rsp = self.web.runtime_component.delete_configuration_file_entry(resource=entry.resource,
                                                                                 stanza=entry.stanza, entry=entry.entry,
                                                                                 value=entry.value)
            else:
                _logger.error("Unable to determine operation for stanza file modification:" + 
                                "\n{}\n. . . skipping".format(entry))
                continue
            if rsp.success == True:
                _logger.info("Successfully modified the {} stanza file".format(entry.stanza))
            else:
                _logger.error("Failed to modify stanza properties file with config:\n{}\n{}".format(
                                                                                json.dumps(entry, indent=4), rsp.data))



    class Runtime(typing.TypedDict):
        '''
        Example::

                   runtime:
                     policy_server: "remote"
                     user_registry: "remote"
                     ldap:
                       host: "openldap"
                       port: 636
                       dn: "cn=root,secAuthority=Default"
                       dn_password: @secrets/isva-secrets:ldap-passwd
                       key_file: "lmi_trust_store"
                     clean_ldap: True
                     domain: "Default"
                     admin_password: @secrets/isva-secrets:secmaster-passwd
                     admin_cert_lifetime: 1460
                     ssl_compliance: "FIPS 140-2"
                     isam:
                       host: "isvaconfig"
                       port: 443
                     stanza_configuration:
                     - operation: "update"
                       resource: "ldap.conf"
                       stanza: "bind-credentials"
                       entry: "bind-dn"
                       value: "cn=root,secAuthority=Default"
                     - operation: "delete"
                       resource: "ldap.conf"
                       stanza: "server:MyFederatedDirectory"

        '''
        class LDAP(typing.TypedDict):
            host: str
            'Hostname or address for LDAP server.'
            port: int
            'Port LDAP server is listening on.'
            dn: str
            'Distinguished mane to bind to LDAP server for admin operations.'
            dn_password: str
            'Password to authenticate as ``dn``.'
            suffix: str
            'SecAuthority suffix.'
            key_file: str
            'SSL Database to use to verify connections to LDAP server.'
            cert_label: str
            'SSL Certificate label to verify connections to LDAP server.'

        class ISAM(typing.TypedDict):
            host: str
            'Hostname or address of Verify Identity Access policy server.'
            port: int
            'Port that Verify Identity Access policy server is listening on.'

        class Stanza_Configuration(typing.TypedDict):
            operation: str
            'Operation to perform on configuration file. ``add`` | ``delete`` | ``update``.'
            resource: str
            'Filename to be modified. ``ldap.conf`` | ``pd.conf`` | ``instance.conf``.'
            stanza: str
            'Name of stanza to modify.'
            entry: typing.Optional[str]
            'Optional entry_id to modify.'
            value: typing.Optional[str]
            'Optional value to modify.'

        policy_server: str
        'The mode for the policy server. ``local`` | ``remote``.'
        user_registry: str
        'Type of user registry to use. ``local`` | ``ldap``.'
        clean_ldap: bool
        'Remove any existing user data from registry. Only valid if ``user_registry`` is ``local``.'
        isam_domain: str
        'The Security Verify Identity Access domain name.'
        admin_password: str
        'The password for the ``sec_master`` user.'
        admin_cert_lifetime: int
        'The lifetime in days for the SSL server certificate.'
        ssl_compliance: str
        'Specifies whether SSL is compliant with any additional computer security standard. ``fips`` | ``sp800-131-transition`` | ``sp800-131-strict`` | ``suite-b-128`` | ``suite-b-192``.'
        ldap: LDAP
        'LDAP server properties.'
        isam: typing.Optional[ISAM]
        'Verify Identity Access policy server properties.'
        stanza_configuration: typing.Optional[typing.List[Stanza_Configuration]]
        'Optional list of modifications to configuration files.'
        override_config: typing.Optional[bool]
        'Optional property to attempt to force a reconfiguration of the runtime component if it is already configured. This is not possible if there are reverse proxy objects. Default is ``false``'

    def runtime(self, runtime):
        rte_status = self.web.runtime_component.get_status()
        _logger.debug("ENTRY Runtime status: {}".format(rte_status.json))
        if rte_status.json['status'] == "Available" and runtime.override_config == True:
            rsp = self.web.runtime_component.unconfigure(ldap_dn=runtime.ldap_dn, ldap_pwd=runtime.ldap_dn,
                    clean=runtime.clean_ldap, force=True)
            if rsp.success == True:
                _logger.info("Successfully unconfigured RTE")
            else:
                _logger.error("RTE cannot be unconfigured, will not override config")
                return
        if rte_status.json['status'] == "Available":
            _logger.info("RTE already configured, skipping.")
            return

        config = {"ps_mode": runtime.policy_server,
                  "user_registry": runtime.user_registry,
                  "ldap_suffix": runtime.suffix,
                  "clean_ldap": runtime.clean_ldap,
                  "isam_domain": runtime.domain,
                  "admin_password": runtime.admin_password,
                  "admin_cert_lifetime": runtime.admin_cert_lifetime,
                  "ssl_compliance": runtime.ssl_compliance
                }
        if runtime.ldap:
            config.update({
                        "ldap_host": runtime.ldap.host,
                        "ldap_port": runtime.ldap.port,
                        "ldap_dn": runtime.ldap.dn,
                        "ldap_password": runtime.ldap.dn_password,
                        "ldap_suffix": runtime.ldap.suffix,
                        "ldap_ssl_db": runtime.ldap.key_file,
                        "ldap_ssl_label": runtime.ldap.cert_label
                    })
        if runtime.isam:
            config.update({
                        "isam_host": runtime.isam.host,
                        "isam_port": runtime.isam.prt
                    })
        rsp = self.web.runtime_component.configure(**config)
        if rsp.success == True:
            _logger.info("Successfully configured Reverse Proxy Runtime Policy Server")
        else:
            _logger.error("Failed to configure Reverse Proxy Runtime Policy Server with config:\n{}\n{}".format(
                json.dumps(runtime, indent=4), rsp.data))

        if runtime.stanza_configuration != None:
            self._runtime_stanza(runtime.stanza_configuration)

        _logger.debug("EXIT Runtime status: {}".format(self.web.runtime_component.get_status().json))
        return


    def _pdadmin_object(self, runtime, obj):
        pdadminCommands = []
        pd_obj = "/WebSEAL/{}-{}{}".format(obj.hostname, obj.instance, obj.junction)
        if obj.attributes != None:
            for attr in obj.attributes:
                pdadminCommands += ["object modify {} set attribute {} {}".format(pd_obj, attr.key, attr.value)]
        if len(pdadminCommands) == 0:
            logger.error("did not find and attributes to attach to policy object {}".foramt(pd_obj))
            return

        rsp = self.web.policy_administration.execute(runtime.admin_user, runtime.admin_password, pdadminCommands)
        if rsp.success == True:
            _logger.info("Successfully attached attributes to policy directory objects {}".format(pd_obj))
        else:
            _logger.error("Failed to attach attributes to object {} with config:\n{}\n{}".format(
                    pd_obj, json.dumps(obj, indent=4), rsp.data))


    def _pdadmin_acl(self, runtime, acl):
        pdadminCommands = ["acl create {}".format(acl.name)]
        if acl.description:
            pdadminCommands += ["acl modify {} set description {}".format(acl.name, acl.description)]
        if acl.attributes:
            for attribute in acl.attributes:
                pdadminCommands += ["acl modify {} set attribute {} {}".format(acl.name, attribute.name,
                    attribute.value)]
        if acl.users:
            for user in acl.users:
                pdadminCommands += ["acl modify {} set user {} {}".format(acl.name, user.name, user.permissions)]

        if acl.groups:
            for group in acl.groups:
                pdadminCommands += ["acl modify {} set group {} {}".format(acl.name, group.name, group.permissions)]

        if acl.any_other:
            pdadminCommands += ["acl modify {} set any-other {}".format(acl.name, acl.any_other)]

        if acl.unauthenticated:
            pdadminCommands += ["acl modify {} set unauthenticated {}".format(acl.name, acl.unauthenticated)]

        rsp = self.web.policy_administration.execute(runtime.admin_user, runtime.admin_password, pdadminCommands)
        if rsp.success == True:
            _logger.info("Successfully created acl {}".format(acl.name))
        else:
            _logger.error("Failed to create acl {} with config:\n{}\n{}".format(
                    acl.name, json.dumps(acl, indent=4), rsp.data))

    def _pdadmin_pop(self, runtime, pop):
        pdadminCommands = ["pop create {}".format(pop.name)]
        if pop.description:
            pdadminCommands += ['pop modify {} set description "{}"'.format(pop.name, pop.description)]

        if pop.attributes:
            for attribute in pop.attributes:
                pdadminCommands += ["pop modify {} set attribute {} {}".format(
                                    pop.name, attribute.name, attribute.value)]

        if pop.tod_access:
            pdadminCommands += ["pop modify {} set tod-access {}".format(pop.name, pop.tod_access)]

        if pop.audit_level:
            pdadminCommands += ["pop modify {} set audit-level {}".format(pop.name, pop.audit_level)]

        if pop.ip_auth:
            if pop.ip_auth.any_other_network:
                pdadminCommands += ["pop modify {} set ipauth anyothernw {}".format(pop.name,
                    pop.ip_auth.any_other_network)]
            if pop.ip_auth.networks:
                for network in pop.ip_auth.networks:
                    pdadminCommands += ["pop modify {} set ipauth {} {}".format(pop.name, network.network,
                        network.netmask, network.auth_level)]

        rsp = self.web.policy_administration.execute(runtime.admin_user, runtime.admin_password, pdadminCommands)
        if rsp.success == True:
            _logger.info("Successfully created pop {}".format(pop.name))
        else:
            _logger.error("Failed to create pop {} with config:\n{}\n{}".format(
                        pop.name, json.dumps(pop, indent=4), rsp.data))

    def _pdadmin_proxy(self, runtime, proxy_config):
        pdadminCommands = []
        if proxy_config.acls:
            for acl in proxy_config.acls:
                for junction in acl.junctions:
                    pdadminCommands += ["acl attach /WebSEAL/{}-{}{} {}".format(proxy_config.host, proxy_config.instance, junction, acl.name)]

        if proxy_config.pops:
            for pop in proxy_config.pops:
                for junction in pop.junctions:
                    pdadminCommands += ["pop attach /WebSEAL/{}-{}{} {}".format(proxy_config.host, proxy_config.instance, junction, pop.name)]

        rsp = self.web.policy_administration.execute(runtime.admin_user, runtime.admin_password, pdadminCommands)
        if rsp.success == True:
            _logger.info("Successfully attached acls/pops to {}".format(proxy_config.host))
        else:
            _logger.error("Failed to attach acls/pops to {} with config:\n{}\n{}".format(
                    proxy_config.host, json.dumps(proxy_config, indent=4), rsp.data))

    def _pdadmin_user(self, runtime, user):
        firstName = user.first_name if user.first_name else user.username
        lastName = user.last_name if user.last_name else user.username
        pdadminCommands = [
                "user create {} {} {} {} {}".format(
                    user.username, user.dn, firstName, lastName, user.password),
                "user modify {} account-valid yes".format(user.username)
            ]
        rsp = self.web.policy_administration.execute(runtime.admin_user, runtime.admin_password, pdadminCommands)
        if rsp.success == True:
            _logger.info("Successfully created user {}".format(user.username))
        else:
            _logger.error("Failed to create user {} with config:\n{}\n{}".format(
                        user.username, json.dumps(user, indent=4), rsp.data))

    def _pdadmin_group(self, runtime, group):
        pdadminCommands = ["group create {} {} {}".format(group.name, group.dn, group.description)]
        if group.users:
            for user in group.users:
                pdadminCommands += ["group modify {} add {}".format(group.name, user)]
        rsp = self.web.policy_administration.execute(runtime.admin_user, runtime.admin_password, pdadminCommands)
        if rsp.success == True:
            _logger.info("Successfully created group {}".format(group.name))
        else:
            _logger.error("Failed to create group {} with config:\n{}\n{}".format(
                        group.name, json.dumps(group, indent=4), rsp.data))

    class PD_Admin(typing.TypedDict):
        '''
        .. note:: Configuration to connect to the user registry is read from the ``webseal.runtime`` entry.

        Example::

                pdadmin:
                  users:
                    - username: "testuser"
                      password: !secret default/isva-secrets:test_password
                      dn: "cn=testuser,dc=iswga"
                    - username: "aaascc"
                      password: !secret default/isva-secrets:aac_user_password
                      dn: "cn=aaascc,dc=iswga"
                    - username: "ob_client"
                      password: !secret default/isva-secrets:ob_client_password
                      dn: "cn=ob_client,dc=iswga"
                  reverse_proxies:
                    - host: "isva-wrp"
                      instance: "default-proxy"
                      acls:
                        - name: "isam_mobile_anyauth"
                          junctions:
                            - "/mga/sps/authsvc"
                            - "/mga/sps/apiauthsvc"
                            - "/intent/account-requests"
                        - name: "isam_mobile_rest_unauth"
                          junctions:
                            - "/mga/websock/mmfa-wss/"
                            - "/mga/sps/ac/info.js"
                            - "/mga/sps/ac/js/info.js"
                            - "/mga/sps/ac"
                            - "/.well-known"
                            - "/CertificateManagement/.well-known"
                            - "/mga/sps/mmfa/user/mgmt/qr_code"
                            - "/intent"
                        - name: "isam_mobile_unauth"
                          junctions:
                            - "/login"
                            - "/content"
                            - "/static"
                            - "/home"
                            - "/ob/sps/auth"
                        - name: "isam_mobile_rest"
                          junctions:
                            - "/scim"
                      pops:
                        - name: "oauth-pop"
                          junctions:
                            - "/scim"
                    - host: "default-proxy-mobile"
                      acls:
                        - name: "isam_rest_mobile"
                          junctions:
                            - "/scim"
                        - name: "isam_mobile_rest_unauth"
                          junctions:
                            - "/mga/sps/mmfa/user/mgmt/qr_code"
                      pops:
                        name: "oauth-pop"
                        junctions:
                          - "scim"

        '''

        class User(typing.TypedDict):
            username: str
            'The name the user will authenticate as. By default this is the UID LDAP attribute.'
            first_name: typing.Optional[str]
            'The CN LDAP attribute for this user. If not set then ``username`` will be used.'
            last_name: typing.Optional[str]
            'The SN LDAP attribute for this user. If not set then ``username`` will be used.'
            password: str
            'The secret to authenticate as ``username``.'
            dn: str
            'The DN LDAP attribute for this user.'

        class Group(typing.TypedDict):
            name: str
            'The CN LDAP attribute for this group.'
            dn: str
            'The DN LDAP attribute for this group.'
            description: typing.Optional[str]
            'Optional description of group.'
            users: typing.Optional[typing.List[str]]
            'Optional list of users to add to group. These users must already exist in the user registry.'

        class Access_Control_List(typing.TypedDict):

            class Attribute(typing.TypedDict):
                name: str
                'Name of the ACL attribute'
                value: str
                'Value of the ACL attribute.'

            class Entity(typing.TypedDict):
                name: str
                'User or Group entity to set permissions for.'
                permissions: str
                'Permission bit-string, eg. ``Tcmdbsvarxl``'

            name: str
            'Name of the ACL.'
            description: typing.Optional[str]
            'Optional description of the ACL'
            attributes: typing.Optional[typing.List[Attribute]]
            'List of extended attributes to add to ACL.'
            users: typing.Optional[typing.List[Entity]]
            'List of users and the permissions they are permitted to perform.'
            groups: typing.Optional[typing.List[Entity]]
            'List of groups and the permissions they are permitted to perform.'
            any_other: str
            'Permissions applied to users who do not match any of the defined user/group permissions.'
            unauthenticated: str
            'Permissions applied to unauthenticated users.'


        class Protected_Object_Policy(typing.TypedDict):

            class Attribute(typing.TypedDict):
                name: str
                'Name of the POP attribute.'
                value: str
                'value of the POP attribute.'

            class IP_Authorization(typing.TypedDict):
                class Network(typing.TypedDict):
                    network: str
                    'TCP/IP address to apply to this POP.'
                    netmask: str
                    'The corresponding netmask to apply to this POP.'
                    auth_level: str
                    'Required step-up authentication level.'

                any_other_network: str
                'Permissions for IP authentication not explicitly listed in the POP.'
                networks: typing.Optional[typing.List[Network]]
                'List of IP addresses to perform IP endpoint authentication.'

            name: str
            'Name of the POP.'
            description: typing.Optional[str]
            'Optional description of the POP.'
            attributes: typing.Optional[typing.List[Attribute]]
            'List of extended attribute to add to POP.'
            tod_access: str
            'Sets the time of day range for the specified protected object policy. '
            audit_level: str
            'Sets the audit level for the specified POP.'
            ip_auth: typing.Optional[typing.List[IP_Authorization]]
            'Sets the IP endpoint authentication settings in the specified POP.'

        class Reverse_Proxy(typing.TypedDict):
            class Reverse_Proxy_ACL(typing.TypedDict):
                name: str
                'Name of the ACL to attach to resources.'
                junctions: typing.List[str]
                'List of junction paths which use the specified ACL.'

            class Reverse_Proxy_POP(typing.TypedDict):
                name: str
                'Name of the POP to attach to resources.'
                junction: str
                'List of junction paths which use the specified POP.'

            host: str
            'Hostname use by the reverse proxy in the Policy Server\'s namespace.'
            instance: str
            'WebSEAL instance name if the Policy Server\'s namespace.'
            acls: typing.Optional[typing.List[Reverse_Proxy_ACL]]
            'List of ACL\'s to attach to reverse proxy instance.'
            pops: typing.Optional[typing.List[Reverse_Proxy_POP]]
            'List of POP\'s to attach to reverse proxy instance.'
        
        class WebSEALObject(typing.TypedDict):
            class Attribute(typing.TypedDict):
                key: str
                'Name of the attribute to attach to the junction object.'
                value: str
                'Value of the attribute to attach to the junction object.'

            hostname: str
            'Hostname use by the reverse proxy in the Policy Server\'s namespace.'
            instance: str
            'WebSEAL instance name if the Policy Server\'s namespace.'
            junction: str
            'WebSEAL junction to modify.'
            attributes: typing.List[Attribute]
            'List of attributes to add to junction object.'

        users: typing.Optional[typing.List[User]]
        'List of users to add to the User Registry. These will be created as "full" Verify Identity Access users.'
        groups: typing.Optional[typing.List[Group]]
        'List of groups to add to the User Registry. These will be created as "full" Verify Identity Access groups.'
        acls: typing.Optional[typing.List[Access_Control_List]]
        'List of ACL\'s to create in the Policy Server.'
        pops: typing.Optional[typing.List[Protected_Object_Policy]]
        'List of POP\'s to create in the Policy Server.'
        objects: typing.Optional[typing.List[WebSEALObject]]
        'List of objects to attach attributes to.'
        reverse_proxies: typing.Optional[typing.List[Reverse_Proxy]]
        'List of ACL\'s and POP\'s to attach to a WebSEAL reverse proxy instance.'


    def pdadmin(self, runtime, pdadmcfg):
        if pdadmcfg.objects != None:
            for obj in pdadmcfg.objects:
                self._pdadmin_object(runtime, obj)

        if pdadmcfg.acls != None:
            for acl in pdadmcfg.acls:
                self._pdadmin_acl(runtime, acl)

        if pdadmcfg.pops != None:
            for pop in pdadmcfg.pops:
                self._pdadmin_pop(runtime, pop)
        #Create users before groups, as groups can add users as members
        if pdadmcfg.users != None:
            for user in pdadmcfg.users:
                self._pdadmin_user(runtime, user)

        if pdadmcfg.groups != None:
            for group in pdadmcfg.groups:
                self._pdadmin_group(runtime, group)

        if pdadmcfg.reverse_proxies != None:
            for proxy in pdadmcfg.reverse_proxies:
                self._pdadmin_proxy(runtime, proxy)
        if self.factory.is_docker() == True:
            deploy_pending_changes(self.factory, self.config)


    class Client_Certificate_Mapping(typing.TypedDict):
        '''
        Example::

                   client_cert_mapping:
                   - demo.mapping.xslt
                   - cert_to_uid.xlst

        '''

        client_cert_mapping: typing.List[str]
        'List of XSLT files to for matching X509 certificates from an incoming connection to an entity in the User Registry.'

    def client_cert_mapping(self, config):
        for cert_mapping in config:
            cert_mapping_file = FILE_LOADER.read_file(cert_mapping)
            if len(cert_mapping_file) != 1:
                _logger.error("Can only specify one cert mapping file")
                return
            cert_mapping_file = cert_mapping_file[0]
            rsp = self.web.client_cert_mapping.create(name=cert_mapping_file['name'], content=cert_mapping_file['contents'])
            if rsp.success == True:
                _logger.info("Successfully configured certificate mapping")
            else:
                _logger.error("Failed to configure certificate mapping using {} config file:\n{}".format(
                            cert_mapping_file['name'], rsp.data))



    class Junction_Mapping(typing.TypedDict):
        '''
        Example::

                junction_mapping:
                - demo.jct.map
                - another.jct.map

        '''

        junction_mapping: typing.List[str]
        'List of properties file to map URI\'s to WebSEAL\'s object space.'


    def junction_mapping(self, config):
        for junction_mapping in config:
            jct_mapping_file = FILE_LOADER.read_file(junction_mapping)
            if len(jct_mapping_file) != 1:
                _logger.error("Can only specify one jct mapping file")
                return
            jct_mapping_file = jct_mapping_file[0]
            rsp = self.web.jct_mapping.create(name=jct_mapping_file['name'], jmt_config_data=jct_mapping_file['contents'])
            if rsp.success == True:
                _logger.info("Successfully configured junction mapping")
            else:
                _logger.error("Failed to configure junction mapping using {} config file:\n{}".format(
                                jct_mapping_file['name'], rsp.data))


    class Url_Mapping(typing.TypedDict):
        '''
        Examples::

                  url-mapping:
                  - dyn.url.conf
                  - url.map.conf
        '''

        url_mapping: typing.List[str]
        'List of configuration files to re-map URL\'s.'

    def url_mapping(self, config):
        for url_mapping in config:
            url_mapping_file = FILE_LOADER.read_file(url_mapping)
            if len(url_mapping_file) != 1:
                _logger.error("Can only specify one url mapping file")
                return
            url_mapping_file = url_mapping_file[0]
            rsp = self.web.url_mapping.create(name=url_mapping_file['name'], dynurl_config_data=url_mapping_file['contents'])
            if rsp.success == True:
                _logger.info("Successfully configured URL mapping")
            else:
                _logger.error("Failed to configure URL mapping using {} config file:\n{}".format(
                                url_mapping_file['name'], rsp.data))


    class User_Mapping(typing.TypedDict):
        '''
        Example::

                  user_mapping:
                  - add_email.xslt
                  - federated_identity_to_basic_user.xslt

        '''
        user_mapping: typing.List[str]
        'List of XSLT files to be uploaded as user mapping rules.'

    def user_mapping(self, config):
        for user_mapping in config:
            user_mapping_file = FILE_LOADER.read_file(user_mapping)
            if len(user_mapping_file) != 1:
                _logger.error("Can only specify one user mapping file")
                return
            rsp = self.web.user_mapping.create(name=user_mapping_file['name'], content=user_mapping_file['contents'])
            if rsp.success == True:
                _logger.info("Successfully configured user mapping")
            else:
                _logger.error("Failed to configure user mapping using {} config file:\n{}".format(
                                user_mapping_file['name'], rsp.data))


    class Form_Single_Sign_On(typing.TypedDict):
        '''
        Example::

                fsso:
                - liberty_jsp_fsso.conf
                - fsso.conf

        '''
        fsso: typing.List[str]
        'List of configuration files to be uploaded as Form Single Sign-On rules.'

    def form_single_sign_on(self, config):
        for fsso_config in config:
            fsso_config_file = FILE_LOADER.read_file(fsso_config)
            if len(fsso_config_file) != 1:
                _logger.error("Can only specify one FSSO configuration file")
                return
            rsp = self.web.fsso.create(name=fsso_config_file['name'], fsso_config_data=fsso_config_file['contents'])
            if rsp.success == True:
                _logger.info("Successfully configured Federated Singe Sign On configuration")
            else:
                _logger.error("Failed to configure FSSO using {} config file:\n{}".format(
                                fsso_config_file['name'], rsp.data))


    class Http_Transformations(typing.TypedDict):
        '''
        Example::

                 http_transforms:
                   requests:
                   - inject_header.xslt
                   lua:
                   - eai.lua

        '''
        requests: typing.List[str]
        'List of files to be uploaded as XSLT request HTTP Transformation Rules.'
        responses: typing.List[str]
        'List of files to be uploaded as XSLT response HTTP Transformation Rules.'
        lua: typing.List[str]
        'List of files to be uploaded as LUA HTTP Transformation Rules.'

    def http_transform(self, http_transform_rules):
        for key in ['requests', 'responses', 'lua']:
            rules = http_transform_rules.get(key, [])
            for http_transform_file_pointer in rules:
                http_transform_files = FILE_LOADER.read_files(http_transform_file_pointer)
                for http_transform_file in http_transform_files:
                    rsp = self.web.http_transform.create(name=http_transform_file['name'], template=key.rstrip('s'),
                            contents=http_transform_file['contents'])
                    if rsp.success == True:
                        _logger.info("Successfully created {} HTTP transform rule".format(http_transform_file['name']))
                    else:
                        _logger.error("Failed to create {} HTTP transform rule".format(http_transform_file['name']))


    def __create_kerberos_property(self, _id, subsection, name, value):
        rsp = self.web.kerberos.create(_id=_id, name=name, value=value)
        if rsp.success == True:
            _logger.info("Successfully configured Kerberos property")
        else:
            _logger.error("Failed to configure Kerberos property:\nsubsection: {} name: {} value:{}\n{}".format(
                            subsection, name, value, rsp.data))


    class Kerberos(typing.TypedDict):
        '''
        Example::

                   kerberos:
                     libdefault:
                       default_realm: "test.com"
                     realms:
                     - name: "test.com"
                       properties:
                       - kdc: "test.com"
                     domain_realms:
                     - name: "demo.com"
                       dns: "test.com"
                     keytabs:
                     - admin.keytab
                     - user.keytab

        '''
        class Realm(typing.TypedDict):
            name: str
            'Name of the Kerberos realm.'
            properties: typing.Optional[typing.List[typing.Dict]]
            'List of key / value properties to configure for realm.'

        class Domain_Realm(typing.TypedDict):
            name: str
            'Name of the Domain Realm.'
            dns: str
            'DNS server for the Domain Realm.'

        libdefaults: typing.Optional[typing.List[typing.Dict]]
        'List of key: value properties to configure as defaults.'
        realms: typing.Optional[typing.List[Realm]]
        'List of Kerberos Realm\'s to configure.'
        domain_realms: typing.Optional[typing.List[Domain_Realm]]
        'List of Kerberos DOmain Realm\'s to configure.'
        keytabs: typing.Optional[typing.List[str]]
        'List of files to import as Kerbros Keytab files.'
        capaths: typing.Dict
        'TODO.'

    def kerberos(self, config):
        if config.libdefault != None:
            for kerbdef, value in config.libdefault: self.__create_kerberos_property('libdefault', kerbdef, kerbdef, value)
        if config.realms != None:
            for realm in config.realms:
                self.__create_kerberos_property("realms", realm.name, None, None)
                if realm.properties != None:
                    for k, v in realm.properties: self.__create_property("realms/" + realm.name, None, k, v)
        if config.domain_realms != None:
            for domain_realm in config.domain_realms: self.__create_kerberos_property("domain_realm", None,
                    domain_realm.name, domain_realm.dns)
        if config.capaths != None:
            for capath in config.capaths:
                self.__create_kerberos_property("capaths", capath.name, None, None)
                if capath.properties != None:
                    for prop, value in capath.properties: self.__create_kerberos_property("capaths/" + capath.name,
                            None, prop, value)
        if config.keytabs != None:
            for kf in config.keytabs:
                if not kf.startswith('/'):
                    kf = config_base_dir() + kf
                rsp = self.web.kerberos.import_keytab(kf)
                if rsp.success == True:
                    _logger.info("Successfully imported Kerberos Keytab file")
                else:
                    _logger.error("Failed to import Kerberos Keytab file:\n{}\n{}".format(
                                json.dumps(prop, indent=4), rsp.data))


    class Password_Strength(typing.TypedDict):
        '''
        Example::

                   password_strength:
                   - demo_rule.xlst

        '''
        password_strength: typing.List[str]
        'List of XSLT file to be uploaded as password strength checks.'

    def password_strength(self, password_strength_rules):
        pwd_config_file = FILE_LOADER.read_file(password_strength_rules)
        if len(pwd_config_file) != 1:
            _logger.error("Can only specify one password strength rule file")
            return
        rsp = self.web.password_strength.create(name=pwd_config_file['name'], content=pwd_config_file['content'])
        if rsp.success == True:
            _logger.info("Successfully configured password strength rules")
        else:
            _logger.error("Failed to configure password strength rules using {}\n{}".format(
                            pwd_config_file['name'], rsp.data))


    class RSA(typing.TypedDict):
        '''
        Example::

                   rsa_config:
                     server_config: server.conf
                     optional_server_config: optional_server.conf

        '''
        server_config: str
        'The server configuration file to upload.'
        optional_server_config: str
        'The server configuration options file to upload.'

    def rsa(self, rsa_config):
        server_config = FILE_LOADER.read_file(rsa_config.server_config)
        methodArgs = { "server_config_file": server_config['path']}
        if rsa_config.optional_server_config:
            opts_config = FILE_LOADER.read_file(rsa_config.optional_server_config)
            methodArgs.update({"server_options_file": opts_config['path']})
        rsp = self.web.rsa.create(**methodArgs)
        if rsp.success == True:
            _logger.info("Successfully configured RSA")
        else:
            _logger.error("Failed to configure RSA using:\n{}\n{}".format(
                            json.dumps(rsa_config, indent=4), rsp.data))


    def __apiac_authz_server(self, runtime, authz_servers):
        for authz_server in authz_servers:
            methodArgs = {"hostname": authz_server.hostname,
                          "auth_port": authz_server.auth_port,
                          "admin_port": authz_server.admin_port,
                          "domain": authz_server.domain,
                          "admin_id": runtime.admin_id,
                          "admin_pwd": runtime.admin_password,
                          "addresses": authz_server.addresses,
                          "ssl": authz_server.ssl,
                          "ssl_port": authz_server.ssl_port,
                          "key_file": authz_server.key_file,
                          "key_label": authz_server.key_label
                }
            rsp = self.web.apiac.authz_server.create_server(authz_server.name, **methodArgs)
            if rsp.success == True:
                _logger.info("Successfully created {} API Access Control Authorization Server".format(authz_server.name))
            else:
                _logger.error("Failed to create API Authorization Server:\n{}\n{}".format(
                                                            json.dumps(authz_server, indent=4), rsp.data))

    def __apiac_resource_server(self, resource_servers):
        for resource_server in resource_servers:
            methodArgs = {
                    "server_hostname": resource_server.server_hostname,
                    "junction_point": resource_server.junction_point,
                    "junction_type": resource_server.junction_type,
                    "static_response_headers": resource_server.static_response_headers,
                    "description": resource_server.description,
                    "junction_hard_limit": resource_server.junction_hard_limit,
                    "junction_soft_limit": resource_server.junction_soft_limit,
                    "basic_auth_mode": resource_server.basic_auth_mode,
                    "tfim_sso": resource_server.tfim_sso,
                    "remote_http_header": resource_server.remote_http_header,
                    "stateful_junction": resource_server.stateful_junction,
                    "http2_junction": resource_server.http2_junction,
                    "sni_name": resource_server.sni_name,
                    "preserve_cookie": resource_server.preserve_cookie,
                    "cookie_include_path": resource_server.cookie_include_path,
                    "transparent_path_junction": resource_server.transparent_path_junction,
                    "mutual_auth": resource_server.mutual_auth,
                    "insert_ltpa_cookies": resource_server.insert_ltpa_cookies,
                    "insert_session_cookies": resource_server.insert_session_cookies,
                    "request_encoding": resource_server.request_encoding,
                    "enable_basic_auth": resource_server.enable_basic_auth,
                    "key_labelkey_label": resource_server.key_label,
                    "gso_resource_group": resource_server.gso_resource_group,
                    "junction_cookie_javascript_block": resource_server.junction_cookie_javascript_block,
                    "client_ip_http": resource_server.client_ip_http,
                    "version_two_cookies": resource_server.version_two_cookies,
                    "ltpa_keyfile": resource_server.ltpa_keyfile,
                    "authz_rules": resource_server.authz_rules,
                    "fsso_config_file": resource_server.fsso_config_file,
                    "username": resource_server.username,
                    "password": resource_server.password,
                    "server_port": resource_server.server_port,
                    "virtual_hostname" : resource_server.virtual_hostname,
                    "server_dn": resource_server.server_dn,
                    "local_ip": resource_server.local_ip,
                    "query_contents": resource_server.query_contents,
                    "case_sensitive_url": resource_server.case_sensitive_url,
                    "windows_style_url": resource_server.windows_style_url,
                    "ltpa_keyfile_password": resource_server.ltpa_keyfile_password,
                    "https_port": resource_server.https_port,
                    "http_port": resource_server.http_port,
                    "proxy_hostname": resource_server.proxy_hostname,
                    "proxy_port": resource_server.proxy_port,
                    "sms_environment": resource_server.sms_environment,
                    "vhost_label": resource_server.vhost_label,
                    "force": resource_server.force,
                    "delegation_support": resource_server.delegation_support,
                    "scripting_support": resource_server.scripting_support
                }
            if resource_server.policy:
                policy = resource_server.policy
                methodArgs.update({
                        "policy_name": policy.name,
                        "policy_type": policy.type
                    })
            if resource_server.authentication:
                methodArgs.update({"authentication_type": resource_server.authentication.type})
                if resource_server.authentication.oauth_introspection:
                    oauth_introspection = resource_server.authentication.oauth_introspection
                    methodArgs.update({
                            "oauth_introspection_transport": oauth_introspection.transport,
                            "oauth_introspection_endpoint": oauth_introspection.endpoint,
                            "oauth_introspection_proxy": oauth_introspection.proxy,
                            "oauth_introspection_auth_method": oauth_introspection.auth_method,
                            "oauth_introspection_client_id": oauth_introspection.client_id,
                            "oauth_introspection_client_secret": oauth_introspection.client_secret,
                            "oauth_introspection_client_id_hdr": oauth_introspection.client_id_hdr,
                            "oauth_introspection_token_type_hint": oauth_introspection.token_type_hint,
                            "oauth_introspection_mapped_id": oauth_introspection.mapped_id,
                            "oauth_introspection_external_user": oauth_introspection.external_user,
                            "oauth_introspection_response_attributes": oauth_introspection.response_attributes
                        })
                if resource_server.authentication.jwt:
                    jwt = resource_server.authentication.jwt
                    methodArgs.update({
                            "jwt_header_name": jwt.header_name,
                            "jwt_certificate": jwt.certificate,
                            "jwt_claims": jwt.claims
                        })
            rsp = self.web.api_access_control.resource_server.create_server(resource_server.reverse_proxy, **methodArgs)
            if rsp.success == True:
                _logger.info("Successfully created {} API AC Resource server".format(resource.server_hostname))
            else:
                _logger.error("Failed to create {} API AC Resource server with config:\n{}\n{}".format(
                    resource.server_hostname, json.dumps(resource, indent=4), rsp.data))
                continue
            if resource_server.resources:
                for resource in resource_server.resource:
                    methodArgs = {
                            "server_type": resource.server_type,
                            "method": resource.method,
                            "path": resource.path,
                            "name": resource.name,
                            "static_response_headers": resource.static_response_headers,
                            "rate_limiting_policy": resource.rate_limiting_policy,
                            "url_aliases": resource.url_aliases,
                            "policy_type": resource.policy_type,
                            "policy_name": resource.policy_name
                        }
                    if resource.documentation:
                        doc = resource.documentation
                        methodArgs.update({
                            "documentation_content_type": doc.content_type,
                            "documentation_file": doc.file
                        })
                    rsp = self.web.api_access_control.resource_server.create_resource(
                                resource_server.reverse_proxy, resource_server.junction_point, **methodArgs)
                    if rsp.success == True:
                        _logger.info("Successfully created {} junctioned resource".format(resource.name))
                    else:
                        _logger.error("Failed to create {} junctioned resource with config;\n{}\n{}".format(
                            resource.name, json.dumps(resource, indent=4), rsp.data))


    def __apiac_policies(self, policies):
        for policy in policies:
            rsp = self.web.api_access_control.policies.create(name=policy.name, groups=policy.groups, 
                                                              attributes=policy.attributes)
            if rsp.success == True:
                _logger.info("Successfully created {} policy".format(policy.name))
            else:
                _logger.error("Failed to create API Access Control policy {}:\n{}\n{}".format(
                                        policy.name, json.dumps(policy, indent=4), rsp.data))

    def __apiac_cors(self, cors_policies):
        for cors in cors_policies:
            rsp = self.web.api_access_control.cors.create(**cors)
            if rsp.success == True:
                _logger.info("Successfully created {} CORS policy".format(cors.name))
            else:
                _logger.error("Failed to create {} CORS policy using config:\n{}\n{}".format(cors.name,
                    json.dumps(cors, indent=4), rsp.data))

    def __apiac_document_root(self, proxy_id, doc_roots):
        for doc_root in doc_roots:
            files = FILE_LOADER.read_files(doc_root, include_directories=True)
            for _file in files:
                rsp = self.web.api_access_control.document_root.create(proxy_id, filename=_file['name'],
                        file_type=_file['type'], contents=_file.get('contents'))
                if rsp.success == True:
                    _logger.info("Successfully uploaded {} {}".format(_file['name'], _file['type']))
                else:
                    _logger.error("Failed to upload {} {}\n{}".format(_file["name"], _file["type"], rsp.data))


    class Api_Access_Control(typing.TypedDict):
        '''
        .. note:: Configuration to connect to the user registry is read from the ``webseal.runtime`` entry.

        Example::

                api_access_control:
                  authorization_servers:
                  - name: "api_server"
                    hostname: "localhost"
                    auth_port: 9443
                    admin_port: 7138
                    domain: "Deafult"
                    addresses:
                    - "192.168.42.102"
                    ssl: "yes"
                    ssl_port: 636
                    key_file: "pdsrv.kdb"
                    key_alias: "webseal-cert"
                  resource_servers:
                  - name: "authz_server"
                    hostname: "isvaruntime"
                    junction_point: "/scim"
                    junction_type:"SSL"
                    authentication:
                      type: "oauth"
                      oauth_introspection:
                        transport: "both"
                        auth_method: "client_secret_basic"
                        endpoint: "external.com/oauth"
                        client_id: !secret default/isva-secrets:apiac_authz_client_id
                        mapped_id: "{iss}/{sub}"
                        external_user: true
                        response_attributes:
                        - pos: 0
                          action: "put"
                          attribute: "test_attribute"
                      jwt:
                        header_name: "iv-jwt"
                        certiciate: "cert"
                        claims:
                        - type: "attr"
                          value: "AZN_CRED_PRINCIPAL_NAME"
                          claim_name: "sub"
                    document_root:
                    - webseal_root.zip
                    resources:
                    - name: "api_ac_instance"
                      hostname: "ibmsec.verify.access"
                  cors:
                  - name:
                    allowed_origins:
                    - "https://webseal.ibm.com"
                    - "https://webseal.ibm.com:9443"
                    - "http://static.webseal.ibm.com"
                    - "http://static.webseal.ibm.com:9080"
                    allowed_credentials: true
                    exposed_headers:
                    - "X-ISAM-VERSION"
                    - "X-ISAM-KEY"
                    handle_preflight: true
                    allowed_methods:
                    - "retry"
                    - "IBMPost"
                    - "Remove"
                    allowed_headers:
                    - "X-ISAM-MODE"
                    - "Content-type"
                    max_age: 86400

        '''
        class Resource_Server(typing.TypedDict):

            class Resource(typing.TypedDict):

                class Response_Header(typing.TypedDict):
                    name: str
                    'The name of the response header.'
                    value: str
                    'The value of the response header.'

                method: str
                'The HTTP action for this resource.'
                path: str
                'The URI path for this resource. This is a full server relative path including the junction point.'
                name: typing.Optional[str]
                'A description for this resource.'
                policy_name: str
                'The name of the custom policy if the type is custom.'
                policy_type: str
                'The type of Policy. The valid values are ``unauthenticated``, ``anyauthenticated``, ``none``, ``default`` or ``custom``.'
                static_response_headers: typing.Optional[typing.List[Response_Header]]
                'A list of header names and values that should be added to the HTTP response.'
                rate_limiting_policy: typing.Optional[str]
                'The name of the rate limiting policy that has been set for this resource.'
                url_aliases: typing.Optional[typing.List[str]]
                'A list of aliases that all map to the path of this resource.'
                doc_type: str
                'The value of the accept header that will trigger a documentation response.'
                doc_file: str
                'The name and path of the documentation file to respond with, relative to the junction root.'

            class Response_Header(typing.TypedDict):
                name: str
                'The name of the response header.'
                value: str
                'The value of the response header'

            class Attribute(typing.TypedDict):
                pos: str
                'The position of this attribute in the ordered list of all attributes.'
                action: str
                'The action to perform for this attribute. Valid values are ``put`` and ``remove``.'
                attribute: str
                'The name of the attribute.'

            class Policy(typing.TypedDict):
                type: str
                'The type of Policy. The valid values are ``unauthenticated``, ``anyauthenticated``, ``none``, ``default`` or ``custom``.'
                name: typing.Optional[str]
                'The name of the custom policy if the type is custom.'

            class Claim(typing.TypedDict):
                type: str
                'The type of claim to add to the JWT. Valid values are either ``text`` for a literal text claim or ``attr`` for a credential attribute claim.'
                value: str
                'The value for the claim. If the type is ``text`` this will be the literal text that is added to the JWT. If the type is ``attr`` this will be the name of the credential attribute to add to the JWT.'
                claim_name: str
                'The name of the claim that is added to the JWT. For attr type claims this is optional and if not specified the claim name will be set as the name of the credential attribute. If the type is attr and the value contains a wildcard this field is invalid and if specified will result in an error. '

            reverse_proxy: str
            'Name of the WebSEAL Reverse Proxy instance this resource server is attached to.'
            server_hostname: str
            'The DNS host name or IP address of the target back-end server.'
            server_port: int
            'TCP port of the back-end third-party server. Default is ``80`` for TCP junctions and ``443`` for SSL junctions.'
            virtual_hostname: typing.Optional[str]
            'Virtual host name that is used for the junctioned Web server.'
            server_dn: typing.Optional[str]
            'Specifies the distinguished name of the junctioned Web server.'
            sever_cn: typing.Optional[str]
            'Specifies the common name, or subject alternative name, of the junctioned Web server.'
            description: typing.Optional[str]
            'An optional description for this junction.'
            junction_point: str
            'Name of the location in the Reverse Proxy namespace where the root of the back-end application server namespace is mounted.'
            junction_type: str
            'Type of junction. Valid values include ``tcp``, ``ssl``, ``tcpproxy``, ``sslproxy`` and ``mutual``.'
            stateful_junction: typing.Optional[str]
            'Specifies whether the junction supports stateful applications. By default, junctions are not stateful. Valid value is ``yes`` or ``no``.'
            policy: Policy
            'The Policy that is associated with this Resource Server.'
            authentication_type: str
            'The type of Oauth authentication. The valid values are ``default`` or ``oauth``.'
            oauth_introspection_transport: typing.Optional[str]
            'The transport type. The valid values are ``none``, ``http``, ``https`` or ``both``.'
            oauth_introspection_proxy: typing.Optional[str]
            'The proxy, if any, used to reach the introspection endpoint.'
            oauth_introspection_auth_method: typing.Optional[str]
            'The method for passing the authentication data to the introspection endpoint. Valid values are ``client_secret_basic`` or ``client_secret_post``.'
            oauth_introspection_endpoint: typing.Optional[str]
            'This is the introspection endpoint which will be called to handle the token introspection.'
            oauth_introspection_client_id: typing.Optional[str]
            'The client identifier which is used for authentication with the external OAuth introspection endpoint.'
            oauth_introspection_client_secret: typing.Optional[str]
            'The client secret which is used for authentication with the external OAuth introspection endpoint.'
            oauth_introspection_client_id_hdr: typing.Optional[str]
            'The name of the HTTP header which contains the client identifier which is used to authenticate to the introspection endpoint. Only valid if client_id has not been set.'
            oauth_introspection_token_type_hint: typing.Optional[str]
            'A hint about the type of the token submitted for introspection.'
            oauth_introspection_mapped_id: typing.Optional[str]
            'A formatted string which is used to construct the Verify Identity Access principal name from elements of the introspection response. Claims can be added to the identity string, surrounded by ``{}``.'
            oauth_introspection_external_user: typing.Optional[str]
            'A boolean which is used to indicate whether the mapped identity should correspond to a known Verify Identity Access identity or not.'
            oauth_introspection_response_attributes: typing.List[Attribute]
            'A list of rules indicating which parts of the json response should be added to the credential.'
            static_response_headers: typing.List[Response_Header]
            'A list of header names and values that should be added to the HTTP response. List of key value pairs eg. ``{"name":"Access-Control-Max-Age", "value":"600"}``'
            jwt_header_name: typing.Optional[str]
            'The name of the HTTP header that will contain the JWT.'
            jwt_certificate: typing.Optional[str]
            'The label of the personal certificate that will sign the JWT.'
            jwt_claims: typing.Optional[Claim]
            'The list of claims to add to the JWT.'
            junction_hard_limit: str
            'Defines the hard limit percentage for consumption of worker threads. Valid value is an integer from ``0`` to ``100``.'
            junction_soft_limit: str
            'Defines the soft limit percentage for consumption of worker threads. Valid value is an integer from ``0`` to ``100``.'
            basic_auth_mode: typing.Optional[str]
            'Defines how the Reverse Proxy server passes client identity information in HTTP basic authentication (BA) headers to the back-end server. Valid value include ``filter`` (default), ``ignore``, ``supply`` and ``gso``.'
            tfim_sso: str
            'Enables IBM Security Federated Identity Manager single sign-on (SSO) for the junction. Valid value is ``yes`` or ``no``.'
            remote_http_header: typing.Optional[typing.List[str]]
            'Controls the insertion of Security Verify Identity Access specific client identity information in HTTP headers across the junction. The value is an array containing a combination of ``iv-user``, ``iv-user-l``, ``iv-groups``, ``iv-creds`` or ``all``.'
            http2_junction: typing.Optional[str]
            'Specifies whether the junction supports the HTTP/2 protocol. By default, junctions do not support the HTTP/2 protocol. A valid value is ``yes`` or ``no``.'
            http2_proxy: typing.Optional[str]
            'Specifies whether the junction proxy support the HTTP/2 protocol. By default, junction proxies do not support the HTTP/2 protocol. A valid values are ``yes`` or ``no``.'
            sni_name: typing.Optional[str]
            'The server name indicator (SNI) to send to TLS junction servers. By default, no SNI is sent.'
            preserve_cookie: typing.Optional[str]
            'Specifies whether modifications of the names of non-domain cookies are to be made. Valid value is ``yes`` or ``no``.'
            cookie_include_path: str
            'Specifies whether script generated server-relative URLs are included in cookies for junction identification. Valid value is ``yes`` or ``no``.'
            transparent_path_junction: str
            'Specifies whether a transparent path junction is created. Valid value is ``yes`` or ``no``.'
            mutual_auth: str
            'Specifies whether to enforce mutual authentication between a front-end Reverse Proxy server and a back-end Reverse Proxy server over SSL. Valid value is ``yes`` or ``no``.'
            insert_ltpa_cookies: str
            'Controls whether LTPA cookies are passed to the junctioned Web server. Valid value is ``yes`` or ``no``.'
            insert_session_cookies: str
            'Controls whether to send the session cookie to the junctioned Web server. Valid value is ``yes`` or ``no``.'
            request_encoding: str
            'Specifies the encoding to use when the system generates HTTP headers for junctions. Possible values for encoding include ``utf8_bin``, ``utf8_uri``, ``lcp_bin``, and ``lcp_uri``.'
            enable_basic_auth: str
            'Specifies whether to use BA header information to authenticate to back-end server. Valid value is ``yes`` or ``no``.'
            key_label: typing.Optional[str]
            'The key label for the client-side certificate that is used when the system authenticates to the junctioned Web server.'
            gso_respource_group: typing.Optional[str]
            'The name of the GSO resource or resource group.'
            junction_cookie_javascript_block: str
            'Controls the junction cookie JavaScript block. The value should be one of ``trailer``, ``inhead``, ``onfocus`` or ``xhtml10``.'
            client_ip_http: str
            'Specifies whether to insert the IP address of the incoming request into an HTTP header for transmission to the junctioned Web server. Valid value is ``yes`` or ``no``.'
            version_two_cookies: typing.Optional[str]
            'Specifies whether LTPA version 2 cookies (LtpaToken2) are used. Valid value is ``yes`` or ``no``.'
            ltpa_keyfile: typing.Optional[str]
            'Location of the key file that is used to encrypt the LTPA cookie data.'
            authz_rules: str
            'Specifies whether to allow denied requests and failure reason information from authorization rules to be sent in the Boolean Rule header (AM_AZN_FAILURE) across the junction. Valid value is ``yes`` or ``no``.'
            fsso_config_file: str
            'The name of the configuration file that is used for forms based single sign-on.'
            username: typing.Optional[str]
            'The Reverse Proxy user name. Used to send BA header information to the back-end server.'
            password: typing.Optional[str]
            'The Reverse Proxy password. Used to send BA header information to the back-end server.'
            local_ip: typing.Optional[str]
            'Specifies the local IP address that the Reverse Proxy uses when the system communicates with the target back-end server.'
            query_contents: str
            'Provides the Reverse Proxy with the correct name of the query_contents program file and where to find the file. By default, the Windows file is called ``query_contents.exe`` and the UNIX file is called ``query_contents.sh``.'
            case_sensitive_url: str
            'Specifies whether the Reverse Proxy server treats URLs as case sensitive. Valid value is ``yes`` or ``no``.'
            windows_style_url: str
            'Specifies whether Windows style URLs are supported. Valid value is ``yes`` or ``no``.'
            ltpa_keyfile_password: typing.Optional[str]
            'Password for the key file that is used to encrypt LTPA cookie data.'
            https_port: int
            'HTTPS port of the back-end third-party server. Applicable when the junction type is ``ssl``.'
            http_port: int
            'HTTP port of the back-end third-party server. Applicable when the junction type is ``tcp``.'
            proxy_hostname: typing.Optional[str]
            'The DNS host name or IP address of the proxy server. Applicable when the junction type is ``sslproxy``.'
            proxy_port: typing.Optional[int]
            'The TCP port of the proxy server. Applicable when the junction type is ``tcpproxy``.'
            sms_environment: typing.Optional[str]
            'Only applicable for virtual junctions. Specifies the replica set that sessions on the virtual junction are managed under.'
            vhost_label: typing.Optional[str]
            'Only applicable for virtual junctions. Causes a second virtual junction to share the protected object space with the initial virtual junction.'
            delegation_support: typing.Optional[str]
            'This option is valid only with junctions that were created with the type of ``ssl`` or ``sslproxy``. Indicates single sign-on from a front-end Reverse Proxy server to a back-end Reverse Proxy server.'
            scripting_support: typing.Optional[str]
            'Supplies junction identification in a cookie to handle script-generated server-relative URLs. '
            force: str
            'Specifies whether to overwrite an existing junction of the same name. Valid value is ``yes`` or ``no``.'
            resources: typing.Optional[typing.List[Resource]]
            'List of resources to add to resource server.'
            document_root: typing.Optional[typing.List[str]]
            'List of documents to upload to the document root.'

        class Authorization_Server(typing.TypedDict):

            name: str
            'This is the new instance name, which is a unique name that identifies the instance.'
            hostname: str
            'The host name of the local host. This name is used when constructing the authorization server name.'
            auth_port: int
            'The port on which authorization requests will be received.'
            admin_port: int
            'The port on which Security Verify Identity Access administration requests will be received.'
            domain: str
            'The Security Verify Identity Access domain.'
            addresses: typing.Optional[typing.List[str]]
            'A json array containing a list of local addresses on which the authorization server will listen for requests.'
            ssl: str
            'Whether or not to enable SSL between the Security Verify Identity Access authorization server and the LDAP server.'
            ssl_port: str
            'The SSL port on which the LDAP server will be contacted. Only valid if ``ssl`` set to ``yes``.'
            key_file: str
            'The name of the keyfile that will be used when communicating with the LDAP server over SSL.'
            key_label: str
            'The label of the certificate within the keyfile to use.'

        class Policy(typing.TypedDict):
            name: str
            'The name of the policy.'
            groups: typing.Optional[typing.List[str]]
            'The groups referenced by this policy. User must be a member of at least one group for this policy to be authorised. The default is no groups if not specified.'
            attributes: typing.Optional[typing.List[str]]
            'The attribute matches referenced by this policy. Each attribute must be matched for this policy to be authorised. The default is no attributes if not specified.'

        class Cross_Origin_Resource_Sharing(typing.TypedDict):
            name: str
            'The name of the CORS policy.'
            allowed_origin: typing.Optional[typing.List[str]]
            'An array of origins which are allowed to make cross origin requests to this resource. Each origin must contain the schema and any non-default port information. A value of ``*`` indicates that any origin will be allowed.'
            allow_credentials: typing.Optional[bool]
            'Controls whether or not the Access-Control-Allow-Credentials header will be set. If not present, this value will default to ``false``.'
            exposed_headers: typing.Optional[typing.List[str]]
            'Controls the values populated in the Access-Control-Expose-Headers header.'
            handle_preflight: typing.Optional[bool]
            'Controls whether or not the Reverse Proxy will handle pre-flight requests. If not present, this value will default to ``false``.'
            allowed_methods: typing.Optional[typing.List[str]]
            'Controls the methods permitted in pre-flight requests and the subsequent Access-Control-Allow-Methods header. This option only relates to pre-flight requests handled by the Reverse Proxy and will be ignored if handle_preflight is set to ``false``. Methods are case sensitive and simple methods (ie. GET, HEAD and POST) are always implicitly allowed.'
            allowed_headers: typing.Optional[typing.List[str]]
            'Controls the headers permitted in pre-flight requests and the subsequent Access-Control-Allow-Headers header. This option only relates to pre-flight requests handled by the Reverse Proxy and will be ignored if handle_preflight is set to ``false``.'
            max_age: typing.Optional[int]
            'Controls the Access-Control-Max-Age header added to pre-flight requests. If set to zero, the header will not be added to pre-flight responses. If set to ``-1``, clients will be told not to cache at all. If not present, this value will default to ``0``.'

        authorization_servers: typing.Optional[typing.List[Authorization_Server]]
        'List of API Authorization servers to create.'
        resource_servers: typing.Optional[typing.List[Resource_Server]]
        'List of API Resource servers to create.'
        policies: typing.Optional[typing.List[Policy]]
        'List of API access control policies to create.'
        cors: typing.Optional[typing.List[Cross_Origin_Resource_Sharing]]
        'List of Cross-Origin Resource Sharing policies to create.'


    def api_access_control(self, runtime, config):
        rsp = self.web.api_access.control.utilities.store_credential(admin_id=runtime.admin_user,
                admin_pwd=runtime.admin_password, admin_doman=runtime.domain)
        if rsp.success == True:
            _logger.info("API Access Control successfully stored admin credential")
        else:
            _logger.error("API Access Control was unable to store admin credential")
            return

        if config.policies != None:
            self.__apiac_policies(config.policies)

        if config.cors != None:
            self.__apiac_cors(config.cors)
            
        if config.authorization_servers != None:
            self.__apiac_authz_server(runtime, config.authorization_servers)

        if config.resource_servers != None:
            self.__apiac_resource_server(config.resource_servers)


    def configure(self):

        if self.config.webseal == None:
            _logger.info("No WebSEAL configuration detected, skipping")
            return
        websealConfig = self.config.webseal
        if websealConfig.client_cert_mapping != None:
            self.client_cert_mapping(websealConfig.client_cert_mapping)

        if websealConfig.junction_mapping != None:
            self.junction_mapping(websealConfig.junction_mapping)

        if websealConfig.url_mapping != None:
            self.url_mapping(websealConfig.url_mapping)

        if websealConfig.user_mapping != None:
            self.user_mapping(websealConfig.user_mapping)

        if websealConfig.fsso != None:
            self.form_single_sign_on(websealConfig.fsso)

        if websealConfig.http_transforms != None:
            self.http_transform(websealConfig.http_transforms)

        if websealConfig.kerberos != None:
            self.kerberos(websealConfig.kerberos)

        if websealConfig.password_strength != None:
            self.password_strength(websealConfig.password_strength)

        if websealConfig.rsa_config != None:
            self.rsa(websealConfig.rsa_config)

        #if websealConfig.runtime != None: done in configure.py global config
        #    self.runtime(websealConfig.runtime)
        if websealConfig.reverse_proxy != None:
            for proxy in websealConfig.reverse_proxy:
                self.wrp(websealConfig.runtime, proxy)

        if websealConfig.pdadmin != None:
            self.pdadmin(websealConfig.runtime, websealConfig.pdadmin)
        
        if websealConfig.api_access_control != None:
            self.api_access_control(websealConfig.runtime, websealConfig.api_access_control)

if __name__ == "__main__":
        w = WEB_Configurator()
        w.configure()
