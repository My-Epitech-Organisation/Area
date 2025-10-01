import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/applet.dart';
import '../providers/app_state.dart';
import 'edit_applet_page.dart';

class MyAppletsPage extends StatefulWidget {
  const MyAppletsPage({super.key});

  @override
  State<MyAppletsPage> createState() => _MyAppletsPageState();
}

class _MyAppletsPageState extends State<MyAppletsPage> {
  @override
  Widget build(BuildContext context) {
    return Consumer<AppState>(
      builder: (context, appState, child) {
        return Semantics(
          label: 'My applets page',
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // Header with refresh button
                Row(
                  children: [
                    Semantics(
                      header: true,
                      child: const Text(
                        'My Applets',
                        style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                      ),
                    ),
                    const Spacer(),
                    Semantics(
                      label: 'Refresh applets button',
                      hint: 'Tap to reload your applets from server',
                      button: true,
                      child: IconButton(
                        onPressed: appState.isLoadingApplets
                            ? null
                            : () => appState.loadApplets(forceRefresh: true),
                        icon: appState.isLoadingApplets
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Icon(Icons.refresh),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 16),

                // Stats cards
                Row(
                  children: [
                    Expanded(
                      child: Semantics(
                        label: 'Total applets count: ${appState.totalAppletsCount}',
                        child: _buildStatCard(
                          'Total',
                          appState.totalAppletsCount.toString(),
                          Icons.apps,
                          Colors.blue,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Semantics(
                        label: 'Active applets count: ${appState.activeAppletsCount}',
                        child: _buildStatCard(
                          'Active',
                          appState.activeAppletsCount.toString(),
                          Icons.play_circle,
                          Colors.green,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // Content area
                Expanded(
                  child: appState.isLoadingApplets
                      ? const Center(
                          child: CircularProgressIndicator(),
                        )
                      : appState.appletsError != null
                          ? _buildErrorView(appState)
                          : appState.applets.isEmpty
                              ? _buildEmptyView()
                              : _buildAppletsList(appState),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            Text(
              title,
              style: const TextStyle(color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView(AppState appState) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Semantics(
            label: 'Error loading applets',
            child: const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'Failed to load applets',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Text(
            appState.appletsError!,
            textAlign: TextAlign.center,
            style: const TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),
          Semantics(
            label: 'Retry loading applets button',
            hint: 'Tap to try loading applets again',
            button: true,
            child: ElevatedButton.icon(
              onPressed: () => appState.loadApplets(forceRefresh: true),
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Semantics(
            label: 'No applets found',
            child: const Icon(
              Icons.apps_outlined,
              size: 64,
              color: Colors.grey,
            ),
          ),
          const SizedBox(height: 16),
          const Text(
            'No applets yet',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          const Text(
            'Create your first applet to get started',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),
          Semantics(
            label: 'Create first applet button',
            hint: 'Tap to navigate to create applet page',
            button: true,
            child: ElevatedButton.icon(
              onPressed: () {
                // Navigate to create page (assuming it's index 1 in navigation)
                DefaultTabController.of(context)?.animateTo(1);
              },
              icon: const Icon(Icons.add),
              label: const Text('Create Applet'),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAppletsList(AppState appState) {
    return ListView.builder(
      itemCount: appState.applets.length,
      itemBuilder: (context, index) {
        final applet = appState.applets[index];
        return Semantics(
          label: 'Applet: ${applet.name}',
          hint: 'Tap to view details, double tap to edit',
          child: Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: Semantics(
                label: 'Applet status: ${applet.isActive ? 'active' : 'inactive'}',
                child: Icon(
                  applet.isActive ? Icons.play_circle : Icons.pause_circle,
                  color: applet.isActive ? Colors.green : Colors.orange,
                ),
              ),
              title: Text(
                applet.name,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(applet.description),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.flash_on, size: 16, color: Colors.orange),
                      const SizedBox(width: 4),
                      Text(
                        applet.triggerService,
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const SizedBox(width: 12),
                      Icon(Icons.arrow_forward, size: 16, color: Colors.grey),
                      const SizedBox(width: 4),
                      Icon(Icons.play_arrow, size: 16, color: Colors.blue),
                      const SizedBox(width: 4),
                      Text(
                        applet.actionService,
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ),
              trailing: PopupMenuButton<String>(
                onSelected: (value) async {
                  switch (value) {
                    case 'edit':
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => EditAppletPage(applet: applet),
                        ),
                      );
                      break;
                    case 'toggle':
                      await appState.toggleApplet(applet.id);
                      break;
                    case 'delete':
                      _showDeleteConfirmation(context, appState, applet);
                      break;
                  }
                },
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit',
                    child: ListTile(
                      leading: Icon(Icons.edit),
                      title: Text('Edit'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  PopupMenuItem(
                    value: 'toggle',
                    child: ListTile(
                      leading: Icon(
                        applet.isActive ? Icons.pause : Icons.play_arrow,
                      ),
                      title: Text(applet.isActive ? 'Deactivate' : 'Activate'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'delete',
                    child: ListTile(
                      leading: Icon(Icons.delete, color: Colors.red),
                      title: Text('Delete', style: TextStyle(color: Colors.red)),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ],
              ),
              onTap: () {
                // Quick view or edit
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => EditAppletPage(applet: applet),
                  ),
                );
              },
            ),
          ),
        );
      },
    );
  }

  void _showDeleteConfirmation(BuildContext context, AppState appState, Applet applet) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Applet'),
        content: Text('Are you sure you want to delete "${applet.name}"? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.of(context).pop();
              final success = await appState.deleteApplet(applet.id);
              if (success && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Applet deleted successfully')),
                );
              }
            },
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }
}
            Semantics(
              header: true,
              child: const Text(
                'My Applets:',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: _isLoading
                  ? Semantics(
                      label: 'Loading applets',
                      child: const Center(
                        child: CircularProgressIndicator(),
                      ),
                    )
                  : _errorMessage != null
                      ? Semantics(
                          label: 'Error loading applets',
                          child: Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text('Error: $_errorMessage'),
                                const SizedBox(height: 16),
                                Semantics(
                                  button: true,
                                  label: 'Retry loading applets',
                                  hint: 'Tap to try loading applets again',
                                  child: ElevatedButton(
                                    onPressed: _fetchApplets,
                                    style: ElevatedButton.styleFrom(
                                      minimumSize: const Size(120, 48),
                                    ),
                                    child: const Text('Retry'),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        )
                      : Semantics(
                          label: 'Applets list',
                          hint: '${_applets.length} applets available',
                          child: ListView.builder(
                            itemCount: _applets.length,
                            itemBuilder: (context, index) {
                              final applet = _applets[index];
                              return Semantics(
                                label: '${applet.name} applet',
                                hint: '${applet.isActive ? 'Active' : 'Inactive'} applet from ${applet.triggerService} to ${applet.actionService}. ${applet.description}',
                                button: true,
                                child: Card(
                                  child: ListTile(
                                    title: Text(applet.name),
                                    subtitle: Text('${applet.triggerService} → ${applet.actionService}\n${applet.description}'),
                                    trailing: Semantics(
                                      label: applet.isActive ? 'Applet is active' : 'Applet is inactive',
                                      child: Icon(
                                        applet.isActive ? Icons.check_circle : Icons.cancel,
                                        color: applet.isActive ? Colors.green : Colors.red,
                                      ),
                                    ),
                                    onTap: () {
                                      // Action to edit or view details
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        SnackBar(
                                          content: Text('Applet: ${applet.name}'),
                                          duration: const Duration(seconds: 2),
                                        ),
                                      );
                                    },
                                  ),
                                ),
                              );
                            },
                          ),
                        ),
            ),
          ],
        ),
      ),
    );
  }
}