import 'package:flutter/material.dart';
import '../models/service_token.dart';
import '../services/oauth_service.dart';

/// Widget to display a compact list of connected services
class ConnectedServicesWidget extends StatefulWidget {
  final VoidCallback? onServiceTap;

  const ConnectedServicesWidget({
    super.key,
    this.onServiceTap,
  });

  @override
  State<ConnectedServicesWidget> createState() =>
      _ConnectedServicesWidgetState();
}

class _ConnectedServicesWidgetState extends State<ConnectedServicesWidget> {
  final OAuthService _oauthService = OAuthService();
  List<ServiceToken>? _services;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadServices();
  }

  Future<void> _loadServices() async {
    setState(() => _isLoading = true);

    try {
      final serviceList = await _oauthService.getConnectedServices();
      if (mounted) {
        setState(() {
          _services = serviceList.connectedServices;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _services = [];
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: Center(
            child: CircularProgressIndicator(),
          ),
        ),
      );
    }

    if (_services == null || _services!.isEmpty) {
      return Card(
        child: InkWell(
          onTap: widget.onServiceTap,
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const Icon(Icons.link_off, size: 48, color: Colors.grey),
                const SizedBox(height: 8),
                const Text(
                  'Aucun service connecté',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Connectez des services pour créer des automatisations',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 12),
                ElevatedButton.icon(
                  onPressed: widget.onServiceTap,
                  icon: const Icon(Icons.add),
                  label: const Text('Connecter un service'),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Services connectés',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                TextButton(
                  onPressed: widget.onServiceTap,
                  child: const Text('Gérer'),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _services!.length,
            itemBuilder: (context, index) {
              final service = _services![index];
              return ListTile(
                dense: true,
                leading: Icon(
                  _getProviderIcon(service.serviceName),
                  color: service.isExpired ? Colors.red : Colors.green,
                ),
                title: Text(service.displayName),
                subtitle: Text(
                  service.statusText,
                  style: TextStyle(
                    fontSize: 11,
                    color: service.isExpired ? Colors.red : Colors.grey[600],
                  ),
                ),
                trailing: service.isExpired
                    ? const Icon(Icons.warning, color: Colors.red, size: 20)
                    : const Icon(Icons.check_circle, color: Colors.green, size: 20),
              );
            },
          ),
          if (widget.onServiceTap != null)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: TextButton.icon(
                onPressed: widget.onServiceTap,
                icon: const Icon(Icons.add),
                label: const Text('Ajouter un service'),
              ),
            ),
        ],
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
}
