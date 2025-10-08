import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/service_catalog_provider.dart';
import '../models/service.dart';
import '../widgets/service_card.dart';
import '../widgets/search_bar_widget.dart';

class ServicesPage extends StatefulWidget {
  const ServicesPage({super.key});

  @override
  State<ServicesPage> createState() => _ServicesPageState();
}

class _ServicesPageState extends State<ServicesPage> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadServices();
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadServices() async {
    final provider = context.read<ServiceCatalogProvider>();
    await provider.loadServices(forceRefresh: true);
  }

  Future<void> _refreshServices() async {
    await _loadServices();
  }

  void _onSearchChanged(String query) {
    setState(() {
      _searchQuery = query.toLowerCase();
    });
  }

  List<Service> _getFilteredServices(List<Service> services) {
    if (_searchQuery.isEmpty) {
      return services;
    }
    return services.where((service) {
      return service.displayName.toLowerCase().contains(_searchQuery) ||
             service.actions.any((action) =>
                 action.displayName.toLowerCase().contains(_searchQuery)) ||
             service.reactions.any((reaction) =>
                 reaction.displayName.toLowerCase().contains(_searchQuery));
    }).toList();
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
            return const Center(
              child: CircularProgressIndicator(),
            );
          }

          if (provider.error != null && provider.services.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.error_outline,
                    size: 64,
                    color: Colors.red,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Failed to load services',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    provider.error!,
                    style: Theme.of(context).textTheme.bodyMedium,
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _loadServices,
                    child: const Text('Retry'),
                  ),
                ],
              ),
            );
          }

          final filteredServices = _getFilteredServices(provider.services);

          return RefreshIndicator(
            onRefresh: _refreshServices,
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: SearchBarWidget(
                    controller: _searchController,
                    onChanged: _onSearchChanged,
                    hintText: 'Search services, actions, reactions...',
                  ),
                ),
                Expanded(
                  child: filteredServices.isEmpty
                      ? Center(
                          child: Text(
                            _searchQuery.isEmpty
                                ? 'No services available'
                                : 'No services match your search',
                            style: Theme.of(context).textTheme.bodyLarge,
                          ),
                        )
                      : ListView.builder(
                          padding: const EdgeInsets.symmetric(horizontal: 16.0),
                          itemCount: filteredServices.length,
                          itemBuilder: (context, index) {
                            final service = filteredServices[index];
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 12.0),
                              child: ServiceCard(
                                service: service,
                                onTap: () {
                                  Navigator.pushNamed(
                                    context,
                                    '/service-details',
                                    arguments: service,
                                  );
                                },
                              ),
                            );
                          },
                        ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}