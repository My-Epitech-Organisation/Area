import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/service.dart';
import '../models/service_token.dart';
import '../providers/service_catalog_provider.dart';
import '../services/oauth_service.dart';
import '../utils/service_icons.dart';
import '../config/service_provider_config.dart';

class ServiceConnectionsPage extends StatefulWidget {
  const ServiceConnectionsPage({super.key});

  @override
  State<ServiceConnectionsPage> createState() => _ServiceConnectionsPageState();
}

class _ServiceConnectionsPageState extends State<ServiceConnectionsPage> {
  final OAuthService _oauthService = OAuthService();
  List<ServiceToken> _connectedServices = [];
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadConnectedServices();
  }

  Future<void> _loadConnectedServices() async {
    setState(() => _isLoading = true);
    try {
      final services = await _oauthService.getConnectedServices();
      setState(() => _connectedServices = services.connectedServices);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error loading services: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  bool _isServiceConnected(String serviceName) {
    final oauthProvider = _mapServiceNameForOAuth(serviceName);
    return _connectedServices.any(
      (service) =>
          service.serviceName.toLowerCase() == oauthProvider.toLowerCase(),
    );
  }

  String _mapServiceNameForOAuth(String serviceName) {
    switch (serviceName.toLowerCase()) {
      case 'gmail':
        return 'google';
      default:
        return serviceName;
    }
  }

  Future<void> _connectOAuthService(String serviceName) async {
    final oauthProvider = _mapServiceNameForOAuth(serviceName);

    setState(() => _isLoading = true);

    try {
      final oauthResponse = await _oauthService.initiateOAuth(oauthProvider);

      final url = Uri.parse(oauthResponse.redirectUrl);

      try {
        await launchUrl(url, mode: LaunchMode.externalApplication);

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(
                'Open your browser and authorize ${ServiceProviderConfig.getDisplayName(serviceName)}. '
                'Then return to the app to see the connection.',
              ),
              duration: const Duration(seconds: 5),
              backgroundColor: Colors.blue,
            ),
          );
        }

        Future.delayed(const Duration(seconds: 2), () {
          if (mounted) {
            _loadConnectedServices();
          }
        });
      } catch (e) {
        throw Exception('Could not launch authorization URL: ${e.toString()}');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('OAuth connection error: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _disconnectService(String serviceName) async {
    // Map service name for OAuth
    final oauthProvider = _mapServiceNameForOAuth(serviceName);

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Disconnect Service'),
        content: Text(
          'Are you sure you want to disconnect ${ServiceProviderConfig.getDisplayName(serviceName)}?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Disconnect'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    setState(() => _isLoading = true);

    try {
      await _oauthService.disconnectService(oauthProvider);
      await _loadConnectedServices();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '${ServiceProviderConfig.getDisplayName(serviceName)} disconnected',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error disconnecting service: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Connected Services'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _loadConnectedServices,
            tooltip: 'Refresh services',
          ),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading && _connectedServices.isEmpty) {
      return const Center(child: CircularProgressIndicator());
    }

    return Consumer<ServiceCatalogProvider>(
      builder: (context, serviceProvider, child) {
        final allServices = serviceProvider.services;

        final sortedServices = [...allServices]
          ..sort((a, b) {
            final aRequiresOAuth = ServiceProviderConfig.requiresOAuth(a.name);
            final bRequiresOAuth = ServiceProviderConfig.requiresOAuth(b.name);

            if (aRequiresOAuth && !bRequiresOAuth) return -1;
            if (!aRequiresOAuth && bRequiresOAuth) return 1;
            return a.displayName.compareTo(b.displayName);
          });

        return RefreshIndicator(
          onRefresh: _loadConnectedServices,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              const Text(
                'Services Requiring Connection',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.blue,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'These services need OAuth authentication to access your accounts',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 12),
              ...sortedServices
                  .where(
                    (service) =>
                        ServiceProviderConfig.requiresOAuth(service.name),
                  )
                  .map((service) => _buildServiceCard(service)),

              const SizedBox(height: 24),

              const Text(
                'Built-in Services',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              const SizedBox(height: 8),
              const Text(
                'These services are always available and don\'t require external connections',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 12),
              ...sortedServices
                  .where(
                    (service) =>
                        !ServiceProviderConfig.requiresOAuth(service.name),
                  )
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
                        'Total services: ${allServices.length}, Connected: ${_connectedServices.length}',
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
          ),
        );
      },
    );
  }

  Widget _buildServiceCard(Service service) {
    final requiresOAuth = ServiceProviderConfig.requiresOAuth(service.name);
    final isConnected = _isServiceConnected(service.name);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: requiresOAuth
              ? (isConnected
                    ? Colors.green.withValues(alpha: 0.2)
                    : Colors.blue.withValues(alpha: 0.2))
              : Colors.green.withValues(alpha: 0.2),
          child: Image.network(
            ServiceProviderConfig.getIconUrl(service.name),
            width: 24,
            height: 24,
            errorBuilder: (context, error, stackTrace) {
              return Icon(
                ServiceIcons.getServiceIcon(service.name),
                color: requiresOAuth
                    ? (isConnected ? Colors.green : Colors.blue)
                    : Colors.green,
                size: 20,
              );
            },
          ),
        ),
        title: Row(
          children: [
            Text(service.displayName),
            if (isConnected) ...[
              const SizedBox(width: 8),
              const Icon(Icons.check_circle, color: Colors.green, size: 16),
            ],
          ],
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Actions: ${service.actions.length}, Reactions: ${service.reactions.length}',
              style: const TextStyle(fontSize: 12),
            ),
            if (isConnected)
              const Text(
                'Connected',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.green,
                  fontWeight: FontWeight.bold,
                ),
              ),
          ],
        ),
        trailing: requiresOAuth
            ? isConnected
                  ? ElevatedButton(
                      onPressed: _isLoading
                          ? null
                          : () => _disconnectService(service.name),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                      child: const Text('Disconnect'),
                    )
                  : ElevatedButton(
                      onPressed: _isLoading
                          ? null
                          : () => _connectOAuthService(service.name),
                      child: const Text('Connect OAuth'),
                    )
            : ElevatedButton(
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(
                        '${service.displayName} is always available (no OAuth required)',
                      ),
                      backgroundColor: Colors.green,
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(backgroundColor: Colors.green),
                child: const Text('Available'),
              ),
      ),
    );
  }
}
