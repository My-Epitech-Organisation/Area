import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../config/service_provider_config.dart';
import '../models/service_token.dart';
import '../services/oauth_service.dart';

/// Page for managing OAuth2 service connections
class ServiceConnectionsPage extends StatefulWidget {
  const ServiceConnectionsPage({super.key});

  @override
  State<ServiceConnectionsPage> createState() => _ServiceConnectionsPageState();
}

class _ServiceConnectionsPageState extends State<ServiceConnectionsPage> {
  final OAuthService _oauthService = OAuthService();

  ServiceConnectionList? _serviceList;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadServices();
  }

  Future<void> _loadServices() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final services = await _oauthService.getConnectedServices();
      setState(() {
        _serviceList = services;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _connectService(String provider) async {
    try {
      // Show loading indicator
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (context) => const Center(child: CircularProgressIndicator()),
      );

      // Initiate OAuth flow
      final response = await _oauthService.initiateOAuth(provider);

      // Close loading dialog
      if (mounted) Navigator.pop(context);

      // Open browser with authorization URL
      final uri = Uri.parse(response.redirectUrl);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);

        // Show info dialog
        if (mounted) {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Autorisation en cours'),
              content: Text(
                'Autorisez l\'application dans votre navigateur.\n\n'
                'Une fois autorisé, vous serez redirigé vers l\'application.\n\n'
                'Provider: ${ServiceProviderConfig.getDisplayName(provider)}',
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                    _loadServices(); // Refresh services
                  },
                  child: const Text('Fermer'),
                ),
              ],
            ),
          );
        }
      } else {
        throw Exception('Impossible d\'ouvrir le navigateur');
      }
    } catch (e) {
      if (mounted) {
        // Close loading dialog if still open
        Navigator.of(context, rootNavigator: true).pop();

        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur de connexion: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _disconnectService(String provider) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Déconnecter le service'),
        content: Text(
          'Voulez-vous vraiment déconnecter ${ServiceProviderConfig.getDisplayName(provider)} ?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Annuler'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Déconnecter'),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    try {
      await _oauthService.disconnectService(provider);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              '${ServiceProviderConfig.getDisplayName(provider)} déconnecté',
            ),
            backgroundColor: Colors.green,
          ),
        );
      }

      _loadServices();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Erreur: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Services connectés'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _loadServices),
        ],
      ),
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text('Erreur: $_error'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadServices,
              child: const Text('Réessayer'),
            ),
          ],
        ),
      );
    }

    if (_serviceList == null) {
      return const Center(child: Text('Aucune donnée'));
    }

    return RefreshIndicator(
      onRefresh: _loadServices,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // Connected services section
          if (_serviceList!.connectedServices.isNotEmpty) ...[
            const Text(
              'Services connectés',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ..._serviceList!.connectedServices.map(
              (service) => _buildConnectedServiceCard(service),
            ),
            const SizedBox(height: 24),
          ],

          // Available services section
          if (_serviceList!.unconnectedProviders.isNotEmpty) ...[
            const Text(
              'Services disponibles',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ..._serviceList!.unconnectedProviders.map(
              (provider) => _buildAvailableServiceCard(provider),
            ),
          ],

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
                        'À propos des services OAuth',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Connectez vos services pour créer des automatisations '
                    'puissantes entre différentes plateformes.',
                    style: TextStyle(fontSize: 12),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Total connecté: ${_serviceList!.totalConnected}',
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
  }

  Widget _buildConnectedServiceCard(ServiceToken service) {
    Color statusColor;
    if (service.isExpired) {
      statusColor = Colors.red;
    } else if (service.expiresInMinutes != null &&
        service.expiresInMinutes! < 60) {
      statusColor = Colors.orange;
    } else {
      statusColor = Colors.green;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: statusColor.withValues(alpha: 0.2),
          child: Icon(
            _getProviderIcon(service.serviceName),
            color: statusColor,
          ),
        ),
        title: Text(service.displayName),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              service.statusText,
              style: TextStyle(color: statusColor, fontSize: 12),
            ),
            Text(
              'Connecté le ${_formatDate(service.createdAt)}',
              style: const TextStyle(fontSize: 10),
            ),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, color: Colors.red),
          onPressed: () => _disconnectService(service.serviceName),
        ),
      ),
    );
  }

  Widget _buildAvailableServiceCard(String provider) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.grey.withValues(alpha: 0.2),
          child: Icon(_getProviderIcon(provider), color: Colors.grey),
        ),
        title: Text(ServiceProviderConfig.getDisplayName(provider)),
        subtitle: Text(
          ServiceProviderConfig.getDescription(provider),
          style: const TextStyle(fontSize: 12),
        ),
        trailing: ElevatedButton(
          onPressed: () => _connectService(provider),
          child: const Text('Connecter'),
        ),
      ),
    );
  }

  IconData _getProviderIcon(String provider) {
    switch (provider.toLowerCase()) {
      case 'google':
        return Icons.g_mobiledata;
      case 'github':
        return Icons.code;
      default:
        return Icons.link;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
