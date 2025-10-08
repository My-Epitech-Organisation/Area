import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/service.dart';
import '../providers/service_catalog_provider.dart';
import '../utils/service_icons.dart';
import '../config/service_provider_config.dart';

class ServiceConnectionsPage extends StatefulWidget {
  const ServiceConnectionsPage({super.key});

  @override
  State<ServiceConnectionsPage> createState() => _ServiceConnectionsPageState();
}

class _ServiceConnectionsPageState extends State<ServiceConnectionsPage> {

  @override
  void initState() {
    super.initState();
  }

    @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Connected Services'),
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    return Consumer<ServiceCatalogProvider>(
      builder: (context, serviceProvider, child) {
        final allServices = serviceProvider.services;

        final sortedServices = [...allServices]..sort((a, b) {
          final aRequiresOAuth = ServiceProviderConfig.requiresOAuth(a.name);
          final bRequiresOAuth = ServiceProviderConfig.requiresOAuth(b.name);

          if (aRequiresOAuth && !bRequiresOAuth) return -1;
          if (!aRequiresOAuth && bRequiresOAuth) return 1;
          return a.displayName.compareTo(b.displayName);
        });

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            const Text(
              'Services Requiring Connection',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blue),
            ),
            const SizedBox(height: 8),
            const Text(
              'These services need OAuth authentication to access your accounts',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            ...sortedServices
                .where((service) => ServiceProviderConfig.requiresOAuth(service.name))
                .map((service) => _buildServiceCard(service)),

            const SizedBox(height: 24),

            const Text(
              'Built-in Services',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green),
            ),
            const SizedBox(height: 8),
            const Text(
              'These services are always available and don\'t require external connections',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 12),
            ...sortedServices
                .where((service) => !ServiceProviderConfig.requiresOAuth(service.name))
                .map((service) => _buildServiceCard(service)),

            const SizedBox(height: 24),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.info_outline, color: Colors.blue),
                        SizedBox(width: 8),
                        Text(
                          'About Service Connections',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Connect your services to create powerful automations '
                      'between different platforms.',
                      style: TextStyle(fontSize: 12),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Total services: ${allServices.length}',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        );
      },
    );
  }

  Widget _buildServiceCard(Service service) {
    final requiresOAuth = ServiceProviderConfig.requiresOAuth(service.name);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey.withValues(alpha: 0.2),
          child: Icon(
            ServiceIcons.getServiceIcon(service.name),
            color: Colors.grey,
          ),
        ),
        title: Text(service.displayName),
        subtitle: Text(
          'Actions: ${service.actions.length}, Reactions: ${service.reactions.length}',
          style: const TextStyle(fontSize: 12),
        ),
        trailing: requiresOAuth
            ? ElevatedButton(
                onPressed: () {
                  // TODO: Implement OAuth connection logic
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('${service.displayName} OAuth connection not implemented yet'),
                      backgroundColor: Colors.orange,
                    ),
                  );
                },
                child: const Text('Connect OAuth'),
              )
            : ElevatedButton(
                onPressed: () {
                  // Services without OAuth are always "available"
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text('${service.displayName} is always available (no OAuth required)'),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                ),
                child: const Text('Available'),
              ),
      ),
    );
  }
}
