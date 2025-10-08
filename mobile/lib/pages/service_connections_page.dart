import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/service.dart';
import '../providers/service_catalog_provider.dart';
import '../utils/service_icons.dart';

/// Page for managing service connections from about.json
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

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // All available services from about.json
            const Text(
              'Available Services',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...allServices.map(
              (service) => _buildServiceCard(service),
            ),

            // Info card
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
        trailing: ElevatedButton(
          onPressed: () {
            // TODO: Implement connection logic
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('${service.displayName} connection not implemented yet'),
                backgroundColor: Colors.orange,
              ),
            );
          },
          child: const Text('Connect'),
        ),
      ),
    );
  }
}
