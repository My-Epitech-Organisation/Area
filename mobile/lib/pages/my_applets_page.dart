import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/applet_provider.dart';
import '../providers/navigation_provider.dart';
import '../models/applet.dart';
import '../widgets/state_widgets.dart';

class MyAppletsPage extends StatefulWidget {
  const MyAppletsPage({super.key});

  @override
  State<MyAppletsPage> createState() => _MyAppletsPageState();
}

class _MyAppletsPageState extends State<MyAppletsPage> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadApplets();
    });
  }

  Future<void> _loadApplets() async {
    final provider = context.read<AppletProvider>();
    await provider.loadApplets(forceRefresh: true);
  }

  Future<void> _refreshApplets() async {
    await _loadApplets();
  }

  void _onAppletTap(Applet applet) {
    // TODO: Navigate to applet details/edit page
    ScaffoldMessenger.of(
      context,
    ).showSnackBar(SnackBar(content: Text('Tapped on: ${applet.name}')));
  }

  void _onDeleteApplet(Applet applet) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Delete Automation'),
          content: Text(
            'Are you sure you want to delete "${applet.name}"? This action cannot be undone.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => _confirmDelete(applet),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _onToggleApplet(Applet applet) async {
    try {
      final provider = context.read<AppletProvider>();
      final success = await provider.toggleApplet(applet.id);

      if (success && mounted) {
        final newStatus = applet.status == 'active' ? 'disabled' : 'active';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Automation "${applet.name}" is now $newStatus'),
            backgroundColor: Colors.blue,
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to toggle automation: ${provider.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error toggling automation: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _confirmDelete(Applet applet) async {
    Navigator.of(context).pop(); // Close the dialog

    try {
      final provider = context.read<AppletProvider>();
      final success = await provider.deleteApplet(applet.id);

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Automation "${applet.name}" deleted successfully'),
            backgroundColor: Colors.green,
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to delete automation: ${provider.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error deleting automation: $e'),
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
        title: const Text('My Automations'),
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refreshApplets,
            tooltip: 'Refresh automations',
          ),
        ],
      ),
      body: Consumer<AppletProvider>(
        builder: (context, provider, child) {
          if (provider.isLoading && provider.applets.isEmpty) {
            return const LoadingStateWidget();
          }

          if (provider.error != null && provider.applets.isEmpty) {
            return ErrorStateWidget(
              title: 'Failed to load automations',
              message: provider.error,
              onRetry: _refreshApplets,
            );
          }

          if (provider.applets.isEmpty) {
            return _buildEmptyState();
          }

          return RefreshIndicator(
            onRefresh: _refreshApplets,
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: provider.applets.length,
              itemBuilder: (context, index) {
                final applet = provider.applets[index];
                return _buildAppletCard(applet);
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          final navigationProvider = Provider.of<NavigationProvider>(
            context,
            listen: false,
          );
          navigationProvider.navigateToPage(1); // Navigate to Create Automation tab
        },
        tooltip: 'Create new automation',
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildAppletCard(Applet applet) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      elevation: 2,
      child: InkWell(
        onTap: () => _onAppletTap(applet),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      applet.name,
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  _buildStatusChip(applet.status),
                  PopupMenuButton<String>(
                    onSelected: (value) {
                      switch (value) {
                        case 'toggle':
                          _onToggleApplet(applet);
                          break;
                        case 'delete':
                          _onDeleteApplet(applet);
                          break;
                      }
                    },
                    itemBuilder: (BuildContext context) => [
                      PopupMenuItem<String>(
                        value: 'toggle',
                        child: Row(
                          children: [
                            Icon(
                              applet.status == 'active'
                                  ? Icons.pause
                                  : Icons.play_arrow,
                              color: Colors.blue,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              applet.status == 'active' ? 'Disable' : 'Enable',
                              style: const TextStyle(color: Colors.blue),
                            ),
                          ],
                        ),
                      ),
                      const PopupMenuItem<String>(
                        value: 'delete',
                        child: Row(
                          children: [
                            Icon(Icons.delete, color: Colors.red),
                            SizedBox(width: 8),
                            Text('Delete', style: TextStyle(color: Colors.red)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                applet.description,
                style: TextStyle(color: Colors.grey[600], fontSize: 14),
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  Icon(Icons.play_arrow, size: 16, color: Colors.blue[600]),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      '${applet.action.service.name}: ${applet.action.name}',
                      style: const TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.arrow_forward, size: 16, color: Colors.green[600]),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Text(
                      '${applet.reaction.service.name}: ${applet.reaction.name}',
                      style: const TextStyle(fontSize: 14),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'Created: ${_formatDate(applet.createdAt)}',
                style: TextStyle(color: Colors.grey[500], fontSize: 12),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusChip(String status) {
    Color color;
    String label;

    switch (status.toLowerCase()) {
      case 'active':
        color = Colors.green;
        label = 'Active';
        break;
      case 'disabled':
        color = Colors.red;
        label = 'Disabled';
        break;
      case 'paused':
        color = Colors.orange;
        label = 'Paused';
        break;
      default:
        color = Colors.grey;
        label = status;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(
        label,
        style: TextStyle(
          color: color,
          fontSize: 12,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 48.0, horizontal: 24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.auto_fix_high, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'No automations yet',
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(color: Colors.grey[700]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              'Create your first automation to get started with automated workflows',
              style: Theme.of(
                context,
              ).textTheme.bodyMedium?.copyWith(color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                final navigationProvider = Provider.of<NavigationProvider>(
                  context,
                  listen: false,
                );
                navigationProvider.navigateToPage(1);
              },
              icon: const Icon(Icons.add),
              label: const Text('Create Automation'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 12,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final difference = now.difference(date);

    if (difference.inDays == 0) {
      return 'Today';
    } else if (difference.inDays == 1) {
      return 'Yesterday';
    } else if (difference.inDays < 7) {
      return '${difference.inDays} days ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}
