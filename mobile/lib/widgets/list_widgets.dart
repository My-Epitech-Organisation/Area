import 'package:flutter/material.dart';
import '../models/service.dart';
import 'service_card.dart';
import 'search_bar_widget.dart';
import 'state_widgets.dart';

class SearchableServiceList extends StatefulWidget {
  final List<Service> services;
  final Function(Service) onServiceTap;
  final String searchHint;

  const SearchableServiceList({
    super.key,
    required this.services,
    required this.onServiceTap,
    this.searchHint = 'Search services, actions, reactions...',
  });

  @override
  State<SearchableServiceList> createState() => _SearchableServiceListState();
}

class _SearchableServiceListState extends State<SearchableServiceList> {
  final TextEditingController _searchController = TextEditingController();
  String _searchQuery = '';

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    setState(() {
      _searchQuery = query.toLowerCase();
    });
  }

  List<Service> _getFilteredServices() {
    if (_searchQuery.isEmpty) {
      return widget.services;
    }
    return widget.services.where((service) {
      return service.displayName.toLowerCase().contains(_searchQuery) ||
             service.actions.any((action) =>
                 action.displayName.toLowerCase().contains(_searchQuery)) ||
             service.reactions.any((reaction) =>
                 reaction.displayName.toLowerCase().contains(_searchQuery));
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    final filteredServices = _getFilteredServices();

    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: SearchBarWidget(
            controller: _searchController,
            onChanged: _onSearchChanged,
            hintText: widget.searchHint,
          ),
        ),
        Expanded(
          child: filteredServices.isEmpty
              ? EmptyStateWidget(
                  message: _searchQuery.isEmpty
                      ? 'No services available'
                      : 'No services match your search',
                  icon: _searchQuery.isEmpty ? Icons.apps : Icons.search_off,
                )
              : ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  itemCount: filteredServices.length,
                  itemBuilder: (context, index) {
                    final service = filteredServices[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12.0),
                      child: ServiceCard(
                        key: ValueKey(service.name),
                        service: service,
                        onTap: () => widget.onServiceTap(service),
                      ),
                    );
                  },
                ),
        ),
      ],
    );
  }
}

/// Widget pour une liste avec pull-to-refresh
class RefreshableList extends StatelessWidget {
  final Future<void> Function() onRefresh;
  final Widget child;

  const RefreshableList({
    super.key,
    required this.onRefresh,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      child: child,
    );
  }
}
