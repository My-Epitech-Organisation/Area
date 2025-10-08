import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/service_catalog_provider.dart';
import '../models/service.dart';
import '../widgets/list_widgets.dart';
import '../widgets/state_widgets.dart';

class ServicesPage extends StatefulWidget {
  const ServicesPage({super.key});

  @override
  State<ServicesPage> createState() => _ServicesPageState();
}

class _ServicesPageState extends State<ServicesPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadServices();
    });
  }

  Future<void> _loadServices() async {
    final provider = context.read<ServiceCatalogProvider>();
    await provider.loadServices(forceRefresh: true);
  }

  Future<void> _refreshServices() async {
    await _loadServices();
  }

  void _onServiceTap(Service service) {
    Navigator.pushNamed(
      context,
      '/service-details',
      arguments: service,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Services'),
        elevation: 0,
      ),
      body: Consumer<ServiceCatalogProvider>(
        builder: (context, provider, child) {
          if (provider.isLoadingServices && provider.services.isEmpty) {
            return const LoadingStateWidget();
          }

          if (provider.error != null && provider.services.isEmpty) {
            return ErrorStateWidget(
              title: 'Failed to load services',
              message: provider.error,
              onRetry: _loadServices,
            );
          }

          return RefreshableList(
            onRefresh: _refreshServices,
            child: SearchableServiceList(
              services: provider.services,
              onServiceTap: _onServiceTap,
            ),
          );
        },
      ),
    );
  }
}