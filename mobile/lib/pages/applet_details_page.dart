import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/applet.dart';
import '../models/execution.dart';
import '../providers/applet_provider.dart';
import 'edit_applet_page.dart';

class AppletDetailsPage extends StatefulWidget {
  final Applet applet;

  const AppletDetailsPage({super.key, required this.applet});

  @override
  State<AppletDetailsPage> createState() => _AppletDetailsPageState();
}

class _AppletDetailsPageState extends State<AppletDetailsPage> {
  late Applet _applet;
  List<Execution> _executions = [];
  bool _isLoadingExecutions = false;

  @override
  void initState() {
    super.initState();
    _applet = widget.applet;
    _loadExecutions();
  }

  Future<void> _loadExecutions() async {
    setState(() => _isLoadingExecutions = true);
    try {
      final provider = context.read<AppletProvider>();
      final executions = await provider.getAppletExecutions(
        _applet.id,
        limit: 20,
      );
      if (mounted) {
        setState(() {
          _executions = executions;
          _isLoadingExecutions = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoadingExecutions = false);
        debugPrint('Error loading executions: $e');
      }
    }
  }

  void _editApplet() {
    Navigator.of(context)
        .push(
          MaterialPageRoute(
            builder: (context) => EditAppletPage(applet: _applet),
          ),
        )
        .then((updated) {
          if (updated == true) {
            _refreshAppletDetails();
          }
        });
  }

  Future<void> _refreshAppletDetails() async {
    final provider = context.read<AppletProvider>();
    final updatedApplet = provider.applets.firstWhere(
      (a) => a.id == _applet.id,
      orElse: () => _applet,
    );
    if (mounted) {
      setState(() => _applet = updatedApplet);
    }
  }

  Future<void> _deleteApplet() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Delete Automation'),
          content: Text(
            'Are you sure you want to delete "${_applet.name}"? This action cannot be undone.',
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(false),
              child: const Text('Cancel'),
            ),
            TextButton(
              onPressed: () => Navigator.of(context).pop(true),
              style: TextButton.styleFrom(foregroundColor: Colors.red),
              child: const Text('Delete'),
            ),
          ],
        );
      },
    );

    if (confirmed == true && mounted) {
      try {
        final provider = context.read<AppletProvider>();
        final success = await provider.deleteApplet(_applet.id);

        if (success && mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Automation deleted successfully'),
              backgroundColor: Colors.green,
            ),
          );
          // Pop back to the list
          Navigator.of(context).pop(true);
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
  }

  Future<void> _duplicateApplet() async {
    final TextEditingController nameController = TextEditingController(
      text: '${_applet.name} (Copy)',
    );

    if (mounted) {
      showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: const Text('Duplicate Automation'),
            content: TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: 'New automation name',
                hintText: 'Enter the name for the duplicated automation',
                border: OutlineInputBorder(),
              ),
              maxLines: 1,
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('Cancel'),
              ),
              TextButton(
                onPressed: () => _confirmDuplicate(nameController.text),
                style: TextButton.styleFrom(foregroundColor: Colors.blue),
                child: const Text('Duplicate'),
              ),
            ],
          );
        },
      );
    }
  }

  Future<void> _confirmDuplicate(String newName) async {
    Navigator.of(context).pop();

    if (newName.trim().isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please enter a name for the duplicated automation'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return;
    }

    try {
      final provider = context.read<AppletProvider>();
      final success = await provider.duplicateApplet(
        _applet.id,
        newName.trim(),
      );

      if (success && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Automation "${newName.trim()}" created successfully',
            ),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.of(context).pop(true);
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to duplicate automation: ${provider.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error duplicating automation: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _pauseApplet() async {
    try {
      final provider = context.read<AppletProvider>();
      final success = await provider.pauseApplet(_applet.id);

      if (success && mounted) {
        final updatedApplet = provider.applets.firstWhere(
          (a) => a.id == _applet.id,
          orElse: () => _applet,
        );
        setState(() => _applet = updatedApplet);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Automation paused'),
            backgroundColor: Colors.orange,
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to pause automation: ${provider.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error pausing automation: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  Future<void> _resumeApplet() async {
    try {
      final provider = context.read<AppletProvider>();
      final success = await provider.resumeApplet(_applet.id);

      if (success && mounted) {
        final updatedApplet = provider.applets.firstWhere(
          (a) => a.id == _applet.id,
          orElse: () => _applet,
        );
        setState(() => _applet = updatedApplet);

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Automation resumed'),
            backgroundColor: Colors.green,
          ),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Failed to resume automation: ${provider.error}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error resuming automation: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: true,
      child: Scaffold(
        appBar: AppBar(
          title: Text(_applet.name),
          elevation: 0,
          actions: [
            IconButton(
              icon: const Icon(Icons.edit),
              onPressed: _editApplet,
              tooltip: 'Edit',
            ),
            IconButton(
              icon: const Icon(Icons.content_copy),
              onPressed: _duplicateApplet,
              tooltip: 'Duplicate',
            ),
            if (_applet.status == 'paused')
              IconButton(
                icon: const Icon(Icons.play_arrow),
                onPressed: _resumeApplet,
                tooltip: 'Resume',
                color: Colors.green,
              )
            else if (_applet.status == 'active')
              IconButton(
                icon: const Icon(Icons.pause),
                onPressed: _pauseApplet,
                tooltip: 'Pause',
                color: Colors.orange,
              ),
            IconButton(
              icon: const Icon(Icons.delete),
              onPressed: _deleteApplet,
              tooltip: 'Delete',
              color: Colors.red,
            ),
          ],
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Status Card
              _buildStatusCard(context),
              const SizedBox(height: 24),

              // Trigger Configuration Card
              _buildTriggerCard(context),
              const SizedBox(height: 24),

              // Action Configuration Card
              _buildActionCard(context),
              const SizedBox(height: 24),

              // Metadata Card
              _buildMetadataCard(context),
              const SizedBox(height: 24),

              // Execution History Card
              _buildExecutionHistoryCard(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusCard(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _applet.status == 'active'
                    ? Colors.green.withAlpha(204)
                    : Colors.grey.withAlpha(204),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(
                _applet.status == 'active' ? Icons.check_circle : Icons.pause,
                color: _applet.status == 'active'
                    ? Colors.white
                    : Colors.white70,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Status', style: Theme.of(context).textTheme.labelSmall),
                  const SizedBox(height: 4),
                  Text(
                    _applet.status == 'active' ? 'Active' : 'Inactive',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: _applet.status == 'active'
                          ? Colors.green
                          : Colors.grey,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTriggerCard(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.play_arrow,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Trigger',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildConfigSection(
              context,
              'Service',
              _applet.action.service.name,
              _applet.action.service.description,
            ),
            const SizedBox(height: 12),
            _buildConfigSection(
              context,
              'Action',
              _applet.action.name,
              _applet.action.description,
            ),
            if (_applet.actionConfig.isNotEmpty) ...[
              const SizedBox(height: 12),
              _buildConfigSection(
                context,
                'Configuration',
                '',
                '',
                data: _applet.actionConfig,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.arrow_forward,
                  color: Theme.of(context).colorScheme.tertiary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Action',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildConfigSection(
              context,
              'Service',
              _applet.reaction.service.name,
              _applet.reaction.service.description,
            ),
            const SizedBox(height: 12),
            _buildConfigSection(
              context,
              'Reaction',
              _applet.reaction.name,
              _applet.reaction.description,
            ),
            if (_applet.reactionConfig.isNotEmpty) ...[
              const SizedBox(height: 12),
              _buildConfigSection(
                context,
                'Configuration',
                '',
                '',
                data: _applet.reactionConfig,
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildConfigSection(
    BuildContext context,
    String label,
    String value,
    String description, {
    Map<String, dynamic>? data,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
            color: Colors.grey,
            fontWeight: FontWeight.w500,
          ),
        ),
        const SizedBox(height: 4),
        if (data == null) ...[
          Text(
            value,
            style: Theme.of(
              context,
            ).textTheme.bodyMedium?.copyWith(fontWeight: FontWeight.w600),
          ),
          if (description.isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              description,
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: Colors.grey),
            ),
          ],
        ] else ...[
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey.shade100,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: data.entries
                  .map(
                    (entry) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(
                        children: [
                          Expanded(
                            flex: 1,
                            child: Text(
                              entry.key,
                              style: Theme.of(context).textTheme.bodySmall,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            flex: 2,
                            child: Text(
                              entry.value.toString(),
                              style: Theme.of(context).textTheme.bodySmall
                                  ?.copyWith(color: Colors.grey.shade700),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                  .toList(),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildMetadataCard(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Metadata',
              style: Theme.of(
                context,
              ).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildMetadataRow(context, 'ID', _applet.id.toString()),
            _buildMetadataRow(
              context,
              'Created',
              _formatDateTime(_applet.createdAt),
            ),
            _buildMetadataRow(context, 'Status', _applet.status),
          ],
        ),
      ),
    );
  }

  Widget _buildMetadataRow(BuildContext context, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              label,
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(color: Colors.grey),
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: Theme.of(
                context,
              ).textTheme.bodySmall?.copyWith(fontWeight: FontWeight.w600),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDateTime(DateTime dateTime) {
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour.toString().padLeft(2, '0')}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  Widget _buildExecutionHistoryCard(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Execution History',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (_isLoadingExecutions)
                  const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                else
                  IconButton(
                    icon: const Icon(Icons.refresh),
                    onPressed: _loadExecutions,
                    tooltip: 'Refresh',
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                  ),
              ],
            ),
            const SizedBox(height: 12),
            if (_executions.isEmpty)
              Center(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 24),
                  child: Text(
                    'No executions yet',
                    style: Theme.of(
                      context,
                    ).textTheme.bodyMedium?.copyWith(color: Colors.grey),
                  ),
                ),
              )
            else
              ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: _executions.length,
                separatorBuilder: (context, index) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final execution = _executions[index];
                  return _buildExecutionItem(context, execution);
                },
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildExecutionItem(BuildContext context, Execution execution) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          Icon(
            execution.getStatusIcon(),
            color: execution.getStatusColor(),
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  execution.status.toUpperCase(),
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    color: execution.getStatusColor(),
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatDateTime(execution.createdAt),
                  style: Theme.of(
                    context,
                  ).textTheme.bodySmall?.copyWith(color: Colors.grey),
                ),
                if (execution.durationSeconds case final duration?)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      'Duration: ${duration.toStringAsFixed(2)}s',
                      style: Theme.of(
                        context,
                      ).textTheme.bodySmall?.copyWith(color: Colors.grey),
                    ),
                  ),
                if (execution.errorMessage != null)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      'Error: ${execution.errorMessage}',
                      style: Theme.of(
                        context,
                      ).textTheme.bodySmall?.copyWith(color: Colors.red),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
