#!/bin/python
"""
@copyright: IBM
"""
import logging
import json
import typing

from .util.constants import HEADERS
from .util.configure_util import config_yaml, deploy_pending_changes
from .util.data_util import Map, optional_list, filter_list, FILE_LOADER

_logger = logging.getLogger(__name__)

class Appliance_Configurator(object):

    config = Map()
    appliance = None

    def __init__(self, config, factory):
        self.config = config
        self.appliance = factory


    def _update_routes(self, route):
        system = self.appliance.get_system_settings()
        interfaces = system.interfaces.list_interfaces().json.get("interfaces", [])
        ifaceUuid = optional_list(filter_list('label', route.interface, interfaces))[0].get("uuid", None)
        if not ifaceUuid:
            _logger.error("Unable to find interface {} in : {}".format(
                route.interface, json.dumps(interfaces, indent=4)))
            return
        existingRoutes = system.static_routes.list_routes().json.get('staticRoutes', [])
        rsp = None; verb = "NONE"
        oldRoute = optional_list(filter_list('interfaceUUID', ifaceUuid, existingRoutes))[0]
        if oldRoute:
            rsp = system.static_routes.update_route(oldRoute['uuid'], enabled=route.enabled,
                    address=route.address, mask_or_prefix=route.mask_or_prefix, gateway=route.gateway,
                    interface_uuid=ifaceUuid, metric=route.metric, comment=route.comment,
                    table=route.table)
            verb = "updated" if rsp.success == True else "update"
        else:
            rsp = system.static_routes.create_route(enabled=route.enabled, address=route.address, mask_or_prefix=route.mask_or_prefix,
                    gateway=route.gateway, interface_uuid=ifaceUuid, metric=route.metric, comment=route.comment,
                    table=route.table)
            verb = "created" if rsp.success == True else "create"
        if rsp != None and rsp.success == True:
            _logger.info("Successfully {} route info for {} interface".format(
                                        verb, route.interface))
        else:
            _logger.error("Failed to {} route info for {} interface:\n{}\n{}".format(
                                verb, route.info, json.dumps(route, indent=4), rsp.data))

    def _update_interface(self, iface):
        system = self.appliance.get_system_settings()
        interfaces = system.interfaces.list_interfaces().json.get("interfaces", [])
        rsp = None
        if iface.ipv4 == None:
            _logger.error("Config tool only tested with IPv4 addresses, sorry")
            return
        oldIface = optional_list(filter_list('label', iface.label, interfaces))[0]
        if oldIface:
            methodArgs = {
                        "name": iface.name,
                        "comment": iface.comment,
                        "enabled": iface.enabled,
                        "vlan_id": iface.vlan_id,
                        "bonding_mode": iface.bonding_mode,
                        "bonded_to": iface.bonded_to,
                    }
            if iface.ipv4 != None:
                if iface.ipv4.dhcp != None:
                    methodArgs.update({
                            "ipv4_dhcp_enabled": iface.ipv4.dhcp.get("enabled", False),
                            "ipv4_dhcp_allow_management": iface.ipv4.dhcp.get("allow_management", False),
                            "ipv4_dhcp_default_route": iface.ipv4.dhcp.get("provides_default_route", False),
                            "ipv4_dhcp_route_metric": iface.ipv4.dhcp.route_metric
                        })
                if iface.ipv4.addresses != None and isinstance(iface.ipv4.addresses, list):
                    address = iface.ipv4.addresses[0]
                    methodArgs.update({
                            "ipv4_address": address.address,
                            "ipv4_mask_or_prefix": address.mask_or_prefix,
                            "ipv4_broadcast_address": address.broadcast_address,
                            "ipv4_allow_management": address.allow_mgmt,
                            "ipv4_enabled": address.enabled
                        })
            rsp = system.interfaces.update_interface(oldIface['uuid'], **methodArgs)
            if rsp.success == True and iface.ipv4.addresses != None: # Log error in outer if block
                for address in iface.ipv4.addresses[1:]:
                    methodArgs = {
                            "address": address.address,
                            "mask_or_prefix": address.mask_or_prefix,
                            "enabled": address.enabled,
                            "allow_management": address.allow_mgmt
                        }
                    rsp = system.interfaces.create_address(iface.label, **methodArgs)

            if rsp != None and rsp.success == True:
                _logger.info("Successfully set address for interface {}".format(iface.label))
            else:
                _logger.error("Failed to update address for interface {} with config:\n{}\n{}".format(
                    iface.label, json.dumps(iface, indent=4), rsp.data))


    def _update_dns(self, dns_config):
        rsp = self.appliance.get_system_settings().dns.update(**dns_config)
        if rsp.success == True:
            _logger.info("Successfully set the DNS properties")
        else:
            _logger.error("Failed to set the DNS properties:\n{}\n{}".format(
                                                json.dumps(dns_config, indent=4), rsp.data))


    def _update_hostname(self, hostname):
        rsp = self.appliance.get_system_settings().general.update_hostname(hostname)
        if rsp.success == True:
            _logger.info("Successfully updated the hostname of the Verify Identity Access appliance.")
        else:
            _logger.error("Failed to update the hostname of the Verify Identity Access appliance.")


    def _update_host_file(self, entries):
        for entry in entries:
            rsp = self.appliance.get_system_settings().hosts_file.get_record(entry.address)
            existing = optional_list(rsp.json)[0]
            verb = 'None'
            if existing:
                old_hosts = [h['name'] for h in existing]
                to_add = [h for h in entry.hosts if h not in old_hosts] # list of hosts not set for given address
                to_remove = [h for h in old_hosts if h not in entry.hosts] # list of hosts not in new config but currently set on appliance
                for new_host in to_add:
                    r = self.appliance.get_system_settings().hosts_file.update_record(entry.address, new_host)
                    if r.success != True:
                        rsp.success = False
                        rsp.data = r.data
                for old_host in to_remove:
                    r = self.appliance.get_system_settings().hosts_file.delete_host_name(entry.address, old_host)
                    if r.success != True:
                        rsp.success = False
                        rsp.data = r.data
                verb = "updated" if rsp.success == True else "update"
            else:
                rsp = self.appliance.get_system_settings().hosts_file.create_record(entry.address, entry.hosts)
                verb = "created" if rsp.success == True else "create"
            if rsp.success == True:
                _logger.info("Successfully {} {} host file entry".format(verb, entry.address))
            else:
                _logger.error("Failed to {} host file config with entry:\n{}\n{}".format(
                                        verb, json.dumps(entry, indent=4), rsp.data))


    class Networking(typing.TypedDict):
        '''
        Example::

                network:
                  hostname: "isam.myidp.ibm.com"
                  host_file:
                  - address: "192.168.42.102"
                    hosts:
                    - "www.myidp.ibm.com"
                  - address: "192.168.42.101"
                    hosts:
                    - "isam.myidp.ibm.com"
                  routes:
                  - enabled: true
                    address: "default"
                    gateway: "192.168.42.1"
                    interface: "1.1"
                    metric: 0
                    table: "main"
                    comment: "Example route"
                  interfaces:
                  - ipv4:
                      dhcp:
                        enabled: false
                    addresses:
                    - address": "192.168.42.101"
                      mask_or_prefix: "255.255.255.0"
                      broadcast_address: "192.168.42.10"
                      allow_mgmt: true
                      enabled: true
                    - address: "192.168.42.102"
                      mask_or_prefix: "/24"
                      broadcast_address: "192.168.42.10"
                      allow_mgmt: false
                      enabled: true

        '''
        class Route(typing.TypedDict):
            enabled: bool
            'Enable this route.'
            interface: str
            'Interface this route is attached to.'
            comment: typing.Optional[str]
            'Optional comment to add to route.'
            address: str
            'Network address to use for route.'
            gateway: str
            'Network gateway to use for route.'
            maks_or_prefix: str
            'Network bitmask or prefix to use for route.'
            metric: int
            'Route metric.'
            table: int
            'Route table.'

        class Interface(typing.TypedDict):
            class IPv4(typing.TypedDict):
                class IPv4Address(typing.TypedDict):
                    address: str
                    'IPv4 address to assign to interface.'
                    mask_or_prefix: str
                    'IPv4 netmask or prefix to assign to address.'
                    broadcast_address: str
                    'IPv4 address to use for broadcasting.'
                    allow_mgmt: bool
                    'Use this address for the Local Management Interface.'
                    enabled: bool
                    'Enable this address.'

                class IPv4DHCP(typing.TypedDict):
                    enabled: bool
                    'Enable DHCP on this interface.'
                    allow_mgmt: bool
                    'Use a DHCP address for the Local Management Interface.'
                    default_route: bool
                    'Use DHCP to determine the default network route.'
                    route_metric: int
                    'Route metric.'

                dhcp: typing.Optional[IPv4DHCP]
                'DHCP configuration for an interface.'
                addresses: typing.Optional[typing.List[IPv4Address]]
                'Static IPv4 addresses assigned to an interface.'

            label: str
            'System assigned label of interface.'
            comment: str
            'Comment to add to interface.'
            enabled: str
            'Enable this interface.'
            vlan_id: typing.Optional[str]
            'System assigned vlan ID.'
            ipv4: IPv4
            'IPv4 settings.'

        class DNS(typing.TypedDict):
            auto: bool
            'true if DNS should be auto configured via dhcp.'
            auto_from_interface: typing.Optional[str]
            'Name or ID of interface whose dhcp will defined the dns settings.'
            primary_server: typing.Optional[str]
            'Primary DNS Server address.'
            secondary_server: typing.Optional[str]
            'Secondary DNS Server address.'
            tertiary_server: typing.Optional[str]
            'Tertiary DNS Server address.'
            search_domains: typing.Optional[str]
            'Comma-separated list of DNS search domains.'

        class HostEntry(typing.TypedDict):
            hosts: typing.List[str]
            'List of host names or domain names to add.'
            address: str
            'IPv4 address to add for hosts.'

        routes: typing.Optional[typing.List[Route]]
        'Optional list of routes to add to an interface.'

        interfaces: typing.List[Interface]
        'List of properties for attached interfaces.'

        dns: typing.Optional[DNS]
        'Domain Name Server settings for appliance'

        hostname: typing.Optional[str]
        'Hostname to set for the Verify Identity Access appliance.'

        host_file: typing.Optional[typing.List[HostEntry]]
        'Entries to add to an appliance\'s hosts file.'

    def update_network(self, config):
        if config.network != None:
            if config.network.routes != None:
                for route in config.network.routes:
                    self._update_routes(route)
            if config.network.interfaces != None:
                for iface in config.network.interfaces:
                    self._update_interface(iface)
            if config.network.dns != None:
                self._update_dns(config.network.dns)
            if config.network.hostname != None:
                self._update_hostname(config.network.hostname)
            if config.network.host_file != None:
                self._update_host_file(config.network.host_file)
        deploy_pending_changes(self.appliance, self.config)


    class Date_Time(typing.TypedDict):
        '''
        Example::

                    date_time:
                      enable_ntp: true
                      ntp_servers:
                      - "time.ibm.com,192.168.0.1"
                      time_zone: "Australia/Brisbane"

        '''
        enable_ntp: bool
        'Enable Network Time Protocol synchronization.'
        ntp_servers: typing.Optional[typing.List[str]]
        'List of hostnames or addresses to use as NTP servers.'
        time_zone: str
        'The id of the timezone the appliance is operating in.'
        date_time: typing.Optional[str]
        'The current date and time, in the format ``YYYY-MM-DD HH:mm:ss``'

    def date_time(self, config):
        if config.date_time != None:
            rsp = self.appliance.get_system_settings().date_time.update(enable_ntp=config.date_time.enable_ntp,
                    ntp_servers=config.date_time.ntp_servers, time_zone=config.date_time.time_zone,
                    date_time=config.date_time.date_time)
            if rsp.success == True:
                _logger.info("Successfully updated Date/Time settings on appliance")
            else:
                _logger.error("Failed to update the Date/Time settings on the appliance with:\n{}\n{}".format(
                    json.dumps(config.date_time, indent=4), rsp.data))


    class Cluster_Configuration(typing.TypedDict):
        '''
        Example::

                 cluster:
                   config_db:
                     address: "127.0.10.1"
                     port: 1234
                     username: "database_user"
                     password: "database_password"
                     ssl: True
                     ssl_keystore: "lmi_trust_store.kdb"
                     db_name: "isva_config"
                   runtime_db:
                     address: "postgresql"
                     port: 5432
                     type: "Postgresql"
                     user: "postgres"
                     password: !secret verify-access/isva-secrets:postgres-passwd
                     ssl: False
                     db_name: "isva_hvdb"
                   cluster:
                     sig_file: "cluster/signature_file"
                     primary_master: "isva.primary.master"
                     secondary_master: "isva.secondary.master"
                     nodes:
                     - "isva.node"
                     restricted_nodes:
                     - "isva.restricted.node"

        '''
        class Database(typing.TypedDict):
            type: str
            'Database type. "postgresql" | "db2" | "oracle".'
            host: str
            'Hostname or address of database.'
            port: str
            'Port database is listening on.'
            ssl: bool
            'Enable SSL encryption of connections.'
            ssl_keystore: typing.Optional[str]
            'SSL database to use to verify connections. Only valid if ``ssl == true``.'
            user: str
            'Username to authenticate to database as.'
            password: str
            'Password to authenticate as ``username``.'
            db_name: str
            'Name of the database instance to use.'
            extra_config: typing.Optional[dict]
            'Database type specific configuration.'

        class Cluster(typing.TypedDict):
            sig_file: str
            'Signature file generated by the primary master; used to add nodes to the cluster.'
            primary_master: str
            'Verify Identity Access appliance designated as the primary master node.'
            secondary_master: typing.Optional[str]
            'Verify Identity Access appliance designated as the secondary master node.'
            nodes: typing.Optional[typing.List[str]]
            'Verify Identity Access appliance designated as nodes.'
            restricted_nodes: typing.Optional[typing.List[str]]
            'Verify Identity Access appliance designated as the restricted nodes.'

        config_database: typing.Optional[Database]
        'Configuration for the config database.'
        runtime_database: typing.Optional[Database]
        'Configuration for the runtime (HVDB) database.'
        cluster: typing.Optional[Cluster]
        'Configuration for Verify Identity Access High Availability cluster nodes.'

    def cluster(self, config):
        if config.config_database != None:
            confDbExtraConfig = config.config_database.copy()
            methodArgs = {"embedded": False, "db_type": confDbExtraConfig.pop('type'), 'host': confDbExtraConfig.pop('host'),
                          'port': confDbExtraConfig.pop('port'), 'secure': confDbExtraConfig.pop('ssl'), 
                          'db_keystore': confDbExtraConfig.pop('ssl_keystore'), 'user': confDbExtraConfig.pop('user'), 
                          'passwd': confDbExtraConfig.pop('password'), 'db_name': confDbExtraConfig.pop('db_name'), 
                          'extra_config': confDbExtraConfig
                }
            rsp = self.appliance.get_system_settings().cluster.set_config_db(**methodArgs)
            if rsp.success == True:
                _logger.info("Successfully set the configuration database")
            else:
                _logger.error("Failed to set the configuration database with:{}\n{}".format(
                    json.dumps(config.config_database, indent=4), rsp.data))
        if config.runtime_database != None:
            hvdbExtraConfig = config.runtime_database.copy()
            methodArgs = {'embedded': False, 'db_type': hvdbExtraConfig.pop('type'), 'host': hvdbExtraConfig.pop('host'),
                          'port': hvdbExtraConfig.po('port'), 'secure': hvdbExtraConfig.pop('ssl'),
                          'db_keystore': hvdbExtraConfig.pop('ssl_keystore'), 'user': hvdbExtraConfig.pop('user'),
                          'passwd': hvdbExtraConfig.pop('password'), 'db_name': hvdbExtraConfig.pop('db_name'),
                          'extra_config': hvdbExtraConfig
                }
            rsp = self.appliance.get_system_settings().cluster.set_runtime_db(**methodArgs)
            if rsp.success == True:
                _logger.info("Successfully set the runtime database")
            else:
                _logger.error("Failed to set the runtime database with: {}\n{}".format(json.dumps(
                    config.runtime_database, indent=4), rsp.data))
        if config.cluster != None:
            rsp = self.appliance.get_system_settings().cluster.update_cluster(**config.cluster)
            if rsp.success == True:
                _logger.info("Successfully set the cluster configuration")
            else:
                _logger.error("Failed to set the cluster configuration with:{}\n{}".format(
                    json.dumps(config.cluster, indent=4), rsp.data))


    def _container_volumes(self, containers):
        if containers.volumes != None:
            for volume in containers.volumes:
                existing = optional_list(filter_list('name', volume.name, 
                                                     self.appliance.get_system_settings().managed_containers.volumes.list()))[0]
                rsp = verb = None
                if existing:
                    rsp = self.appliance.get_system_settings().managed_containers.volumes.import_volume(
                        existing['id'], FILE_LOADER.read_file(volume.archive))
                    verb = "updated" if rsp.success == True else "update"
                else:
                    existing = self.appliance.get_system_settings().managed_containers.volumes.create(volume.name).id_from_location
                    rsp = self.appliance.get_system_settings().managed_containers.volumes.create(
                                                            existing, FILE_LOADER.read_file(volume.archive))
                    verb = "created" if rsp.success == True else "create"
                if rsp.success == True:
                    _logger.info("Successfully {} managed container volume {}".format(verb, volume.name))
                else:
                    _logger.error("Failed to {} managed container volume with:\n{}\n{}".format(
                                            verb, json.dumps(volume, indent=4), rsp.data))


    def _container_registries(self, containers):
        if containers.registries != None:
            for rgy in containers.registries:
                existing = optional_list(filter_list('host', rgy.host, 
                                                     self.appliance.get_system_settings().managed_containers.registries.list()))[0]
                rsp = verb = None
                if existing:
                    rsp = self.appliance.get_system_settings().managed_containers.registries.update(existing['id'], **rgy)
                    verb = "updated" if rsp.success == True else "update"
                else:
                    rsp = self.appliance.get_system_settings().managed_containers.registries.create(**rgy)
                    verb = "created" if rsp.success == True else "create"
                if rsp.success == True:
                    _logger.info("Successfully {} {} container registry properties".format(verb, rgy.host))
                else:
                    _logger.error("Failed to {} container registry properties:\n{}\n{}".format(
                                            verb, json.dumps(rgy, indent=4), rsp.data))


    def _container_images(self, containers):
        if containers.images != None:
            for image in containers.images:
                existing = optional_list(filter_list('image', image, 
                                                     self.appliance.get_system_settings().managed_containers.images.list()))[0]
                rsp = verb = None
                if existing:
                    rsp = self.appliance.get_system_settings().managed_containers.images.update(existing['id'])
                    verb = "updated" if rsp.success == True else "update"
                else:
                    rsp = self.appliance.get_system_settings().managed_containers.images.create(image)
                    verb = "created" if rsp.success == True else "create"
                if rsp.success == True:
                    _logger.info("Successfully {} {} cached container image".format(verb, image))
                else:
                    _logger.error("Failed to {} cached container image {}:\n{}".format(verb, image, rsp.data))


    def _container_deployments(self, containers):
        if containers.deployments != None:
            for deployment in containers.deployments:
                existing = optional_list(filter_list('name', deployment.name, 
                                                     self.appliance.get_system_settings().managed_containers.deployments.list()))[0]
                rsp = verb = None
                if existing:
                    rsp = self.appliance.get_system_settings().managed_containers.deployments.delete(existing['id'])
                    if rsp.success == True:
                        rsp = self.appliance.get_system_settings().managed_containers.deployments.create(**deployment)
                    verb = "redeploy"
                else:
                    rsp = self.appliance.get_system_settings().managed_containers.registries.create(**deployment)
                    verb = "created" if rsp.success == True else "create"
                if rsp.success == True:
                    _logger.info("Successfully {} {} managed container deployment".format(verb, deployment.name))
                else:
                    _logger.error("Failed to {} managed container deployment:\n{}\n{}".format(
                                            verb, json.dumps(deployment, indent=4), rsp.data))


    class Managed_Containers(typing.TypedDict):
        '''
        Example::

                managed_containers:
                  volumes:
                  - name: "iag-config"
                    archive: iag.zip
                  images:
                  - "icr.io/isva/verify-access-oidc-provider:23.03"
                  registries:
                  - host: "icr.io"
                    proxy:
                      host: "proxy.ibm.com"
                      port: 3128
                  deployments:
                  - name: "IAG Deployment"
                    image: "icr.io/isva/verify-access-oidc-provider:23.03"
                    type: "iag"
                    ports:
                    - name: "https"
                      value: "192.168.42.102:30443"
                    volumes:
                    - name: "config"
                      value: "iag-config"
                    env:
                    - name: "LOG_FORMAT"
                      value: "JSON"

        '''

        class Volume(typing.TypedDict):
            name: str
            'Name of volume to be created/updated.'
            archive: str
            'Zip archive of volume contents.'

        class Registry(typing.TypedDict):
            class Proxy:
                host: str
                'Host name or address of proxy'
                port: str
                'Port request should be proxied to'
                user: str
                'Username to (basic) authenticate to the proxy with'
                secret: str
                'Secret to (basic) authenticate to the proxy with'
                schema: str
                'TCP schema to communicate with proxy. Default is ``http://``'

            host: str
            'Domain or IP address of container registry.'
            user: str
            'User to authenticate to container registry as'
            secret: str
            'Secret to authenticate to the container registry as ``user``'
            proxy: typing.Optional[Proxy]
            'Proxy configuration for pulling images.'
            ca: str
            'Path to a X509 Certificate bundle to use as the Certificate Authority when pulling images from this registry.'
            

        class Deployment(typing.TypedDict):

            class PortProperties(typing.TypedDict):
                name: str
                'Name of the Metadata port mapping being forwarded to the host appliance.'
                value: str
                'Host port to map to. This can optionally include an interface address, eg. ``192.168.42.201:30443``'
            
            class VolumeProperties(typing.TypedDict):
                name: str
                'Name of Metadata volume mount point.'
                value: str
                'Name or ID of the volume being mounted.'
            
            class EnvProperties(typing.TypedDict):
                name: str
                'Name of environment variable to create.'
                value: str
                'Value of environment variable.'

            class LoggingProperties(typing.TypedDict): 
                max_files: typing.Optional[int]
                'The maximum number of roll-over log files to keep. If a value is not specified, the default of 10 (10 files) will be used.'
                max_size: typing.Optional[int]
                'The maximum size of a log file, in megabytes, before it will be rolled over. If a value is not specified, the default of 10 (10MB) will be used.'

            name: str
            'Name of the container deployment.'
            image: str
            'Container image to use.'
            type: str
            'Container deployment metadata type.'
            ports: typing.List[PortProperties]
            'Mapping between container ports and host ports.'
            volumes: typing.List[VolumeProperties]
            'Container volume mount properties.'
            env: typing.List[EnvProperties]
            'Container environment variable properties.'
            logging: typing.Optional[LoggingProperties]
            'Container logfile rollover properties.'
            command: typing.Optional[str]
            'An optional command from the metadata document to run instead of the container entrypoint.'
            args: typing.Optional[typing.List[str]]
            'An optional list of arguments to pass to the specified command.'


        volumes: typing.Optional[typing.List[Volume]]
        'List of volumes to be created or updated.'
        images: typing.Optional[typing.List[str]]
        'List of image to be pulled. This should include registry and tag information, eg. ``icr.io/isva/verify-access-oidc-provider:23.03``'
        registries: typing.Optional[typing.List[Registry]]
        'List of container registry authentication/proxy configuration to apply.'
        deployments: typing.Optional[typing.List[Deployment]]
        'List of managed container deployments to create.'

    def managed_containers(self, config):
        if config.managed_containers != None:
            self._container_volumes(config.managed_containers)
            self._container_registries(config.managed_containers)
            self._container_images(config.managed_containers)
            self._container_deployments(config.managed_containers)


    def configure(self):
        self.update_network(self.config.appliance)
        self.date_time(self.config.appliance)
        self.cluster(self.config.appliance)
        self.managed_containers(self.config.appliance)

if __name__ == "__main__":
    Appliance_Configurator(config_yaml(), None).configure()
