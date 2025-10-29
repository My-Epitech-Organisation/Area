import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../models/service.dart';
import '../models/service_token.dart';
import '../providers/service_catalog_provider.dart';
import '../services/oauth_service.dart';
import '../config/service_provider_config.dart';
import '../utils/service_icons.dart';

/// Get color filter for logos based on connection status
ColorFilter? _getLogoColorFilter(bool requiresOAuth, bool isConnected) {
  if (!requiresOAuth) {
    return ColorFilter.mode(Colors.green, BlendMode.srcIn);
  }
  if (isConnected) {
    return ColorFilter.mode(Colors.green, BlendMode.srcIn);
  }
  return ColorFilter.mode(Colors.blue, BlendMode.srcIn);
}

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
    final oauthProvider = ServiceProviderConfig.mapServiceName(serviceName);
    return _connectedServices.any(
      (service) =>
          service.serviceName.toLowerCase() == oauthProvider.toLowerCase(),
    );
  }

  Future<void> _connectOAuthService(String serviceName) async {
    final oauthProvider = ServiceProviderConfig.mapServiceName(serviceName);

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

        _pollForOAuthCompletion(serviceName);
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

  Future<void> _pollForOAuthCompletion(String serviceName) async {
    const int maxAttempts = 30;
    const Duration initialDelay = Duration(milliseconds: 500);
    const double backoffMultiplier = 1.2;

    Duration currentDelay = initialDelay;
    int attempt = 0;

    while (attempt < maxAttempts && mounted) {
      attempt++;

      try {
        final services = await _oauthService.getConnectedServices();
        final isConnected = services.connectedServices.any(
          (token) =>
              token.serviceName.toLowerCase() == serviceName.toLowerCase(),
        );

        if (isConnected) {
          if (mounted) {
            _loadConnectedServices();
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text(
                  '${ServiceProviderConfig.getDisplayName(serviceName)} connected successfully!',
                ),
                backgroundColor: Colors.green,
                duration: const Duration(seconds: 3),
              ),
            );
          }
          return;
        }

        await Future.delayed(currentDelay);
        currentDelay = Duration(
          milliseconds: (currentDelay.inMilliseconds * backoffMultiplier)
              .round(),
        );
      } catch (e) {
        await Future.delayed(currentDelay);
        currentDelay = Duration(
          milliseconds: (currentDelay.inMilliseconds * backoffMultiplier)
              .round(),
        );
      }
    }

    // Timeout reached
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Connection timeout. Please check if you completed the authorization in your browser.',
          ),
          backgroundColor: Colors.orange,
          duration: const Duration(seconds: 5),
        ),
      );
      _loadConnectedServices();
    }
  }

  Future<void> _disconnectService(String serviceName) async {
    // Map service name for OAuth
    final oauthProvider = ServiceProviderConfig.mapServiceName(serviceName);

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
            if (a.requiresOAuth && !b.requiresOAuth) return -1;
            if (!a.requiresOAuth && b.requiresOAuth) return 1;
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
              const SizedBox(height: 12),
              ...sortedServices
                  .where((service) => service.requiresOAuth)
                  .map((service) => _buildServiceCard(service)),

              const SizedBox(height: 24),

              const Text(
                'Active Services',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
              ),
              const SizedBox(height: 12),
              ...sortedServices
                  .where((service) => !service.requiresOAuth)
                  .map((service) => _buildServiceCard(service)),
            ],
          ),
        );
      },
    );
  }

  Widget _buildServiceCard(Service service) {
    final requiresOAuth = service.requiresOAuth;
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
          child: service.logo != null
              ? SvgPicture.network(
                  service.logo!,
                  width: 24,
                  height: 24,
                  placeholderBuilder: (context) =>
                      const CircularProgressIndicator(strokeWidth: 1),
                  colorFilter: _getLogoColorFilter(requiresOAuth, isConnected),
                )
              : Icon(
                  ServiceIcons.getServiceIcon(service.name),
                  color: requiresOAuth
                      ? (isConnected ? Colors.green : Colors.blue)
                      : Colors.green,
                  size: 20,
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
