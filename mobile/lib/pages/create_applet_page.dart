import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/create_applet/create_applet_widgets.dart';
import '../providers/service_catalog_provider.dart';
import '../providers/connected_services_provider.dart';
import '../providers/navigation_provider.dart';
import '../providers/automation_stats_provider.dart';
import '../services/applet_service.dart';

class CreateAppletPage extends StatefulWidget {
  const CreateAppletPage({super.key});

  @override
  State<CreateAppletPage> createState() => _CreateAppletPageState();
}

class _CreateAppletPageState extends State<CreateAppletPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  String? _selectedTriggerService;
  String? _selectedTriggerAction;
  String? _selectedActionService;
  String? _selectedActionReaction;

  int? _selectedActionId;
  int? _selectedReactionId;

  Map<String, dynamic> _actionConfig = {};
  Map<String, dynamic> _reactionConfig = {};

  bool Function()? _validateConfigForm;

  bool _isCreating = false;

  @override
  void initState() {
    super.initState();
    // Load services and connected services when page opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServiceCatalogProvider>().loadServices();
      context.read<ConnectedServicesProvider>().loadConnectedServices();
    });
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Create new automation page',
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Theme.of(context).colorScheme.surface,
              Theme.of(context).colorScheme.surface.withAlpha(204),
            ],
          ),
        ),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Form(
            key: _formKey,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 24),

                // Automation Details Card
                AutomationDetailsCard(nameController: _nameController),

                const SizedBox(height: 16),

                // Trigger Configuration Card
                TriggerConfigCard(
                  selectedService: _selectedTriggerService,
                  selectedAction: _selectedTriggerAction,
                  onServiceChanged: (value) {
                    setState(() {
                      _selectedTriggerService = value;
                      _selectedTriggerAction =
                          null; // Reset action when service changes
                      // Reset action selection when trigger changes
                      _selectedActionService = null;
                      _selectedActionReaction = null;
                      _selectedActionId = null;
                      _selectedReactionId = null;
                    });
                  },
                  onActionChanged: (value) {
                    setState(() {
                      _selectedTriggerAction = value;
                      _selectedActionId = context
                          .read<ServiceCatalogProvider>()
                          .getActionId(value!);
                    });
                  },
                ),

                const SizedBox(height: 16),

                // Action Configuration Card - Only show when trigger action is selected
                if (_selectedTriggerService != null &&
                    _selectedTriggerAction != null)
                  ActionConfigCard(
                    selectedService: _selectedActionService,
                    selectedReaction: _selectedActionReaction,
                    onServiceChanged: (value) {
                      setState(() {
                        _selectedActionService = value;
                        _selectedActionReaction =
                            null; // Reset reaction when service changes
                        _selectedReactionId = null;
                      });
                    },
                    onReactionChanged: (value) {
                      setState(() {
                        _selectedActionReaction = value;
                        _selectedReactionId = context
                            .read<ServiceCatalogProvider>()
                            .getReactionId(value!);
                      });
                    },
                  ),

                const SizedBox(height: 16),

                if (_selectedTriggerService != null &&
                    _selectedTriggerAction != null &&
                    _selectedActionService != null &&
                    _selectedActionReaction != null)
                  ConfigStepCard(
                    selectedActionName: _selectedTriggerAction!,
                    selectedReactionName: _selectedActionReaction!,
                    actionConfigSchema: context
                        .read<ServiceCatalogProvider>()
                        .getAction(_selectedTriggerAction!)
                        ?.configSchema,
                    reactionConfigSchema: context
                        .read<ServiceCatalogProvider>()
                        .getReaction(_selectedActionReaction!)
                        ?.configSchema,
                    actionConfig: _actionConfig,
                    reactionConfig: _reactionConfig,
                    onActionConfigChanged: (config) {
                      setState(() {
                        _actionConfig = config;
                      });
                    },
                    onReactionConfigChanged: (config) {
                      setState(() {
                        _reactionConfig = config;
                      });
                    },
                    onValidationChanged: (validateFunction) {
                      setState(() {
                        _validateConfigForm = validateFunction;
                      });
                    },
                  ),

                const SizedBox(height: 24),

                // Visual Preview - Show automation flow
                AutomationPreviewCard(
                  triggerServiceName: _selectedTriggerService,
                  triggerActionName: _selectedTriggerAction,
                  actionConfig: _actionConfig,
                  reactionServiceName: _selectedActionService,
                  reactionActionName: _selectedActionReaction,
                  reactionConfig: _reactionConfig,
                ),

                const SizedBox(height: 32),

                // Create Button
                CreateAutomationButton(
                  onPressed: _isCreating ? null : _createAutomation,
                  label: _isCreating ? 'Creating...' : 'Create Automation',
                ),

                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _createAutomation() async {
    debugPrint('🚀 Starting automation creation...');
    debugPrint('📊 Current state:');
    debugPrint('  - _selectedTriggerService: $_selectedTriggerService');
    debugPrint('  - _selectedTriggerAction: $_selectedTriggerAction');
    debugPrint('  - _selectedActionService: $_selectedActionService');
    debugPrint('  - _selectedActionReaction: $_selectedActionReaction');
    debugPrint('  - _selectedActionId: $_selectedActionId');
    debugPrint('  - _selectedReactionId: $_selectedReactionId');
    debugPrint('  - _nameController.text: "${_nameController.text}"');

    final formValid = _formKey.currentState?.validate() ?? false;
    debugPrint('📝 Form validation: $formValid');

    if (formValid) {
      debugPrint('✅ Form is valid, checking selections...');

      // Validate that all required fields are selected
      if (_selectedTriggerService == null || _selectedTriggerAction == null) {
        debugPrint('❌ Missing trigger selection');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select a trigger'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      debugPrint(
        '✅ Trigger selected: $_selectedTriggerService -> $_selectedTriggerAction',
      );

      if (_selectedActionService == null || _selectedActionReaction == null) {
        debugPrint('❌ Missing action selection');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select an action'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      debugPrint(
        '✅ Action selected: $_selectedActionService -> $_selectedActionReaction',
      );
    } else {
      debugPrint('❌ Form validation failed');
      // The form validation will show its own error messages
      return;
    }

    if (_selectedActionId == null || _selectedReactionId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Invalid action or reaction selected'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    // Validate configuration form if it exists
    if (_selectedTriggerService != null &&
        _selectedTriggerAction != null &&
        _selectedActionService != null &&
        _selectedActionReaction != null) {
      if (!(_validateConfigForm?.call() ?? true)) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please fill in all required configuration fields'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }
    }

    setState(() {
      _isCreating = true;
    });

    try {
      final appletService = AppletService();
      final applet = await appletService.createApplet(
        description: _nameController.text.isNotEmpty
            ? _nameController.text
            : 'Created from mobile app',
        actionId: _selectedActionId!,
        reactionId: _selectedReactionId!,
        actionConfig: _actionConfig.isNotEmpty ? _actionConfig : {},
        reactionConfig: _reactionConfig.isNotEmpty ? _reactionConfig : {},
      );

      debugPrint(
        '✅ Automation created successfully: ${applet.name} (ID: ${applet.id})',
      );

      // Refresh statistics to reflect the new automation
      if (mounted) {
        WidgetsBinding.instance.addPostFrameCallback((_) async {
          final statsProvider = context.read<AutomationStatsProvider>();
          await statsProvider.loadAllStats(forceRefresh: true);
        });
      }

      if (mounted) {
        debugPrint('📱 Showing success snackbar...');
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Automation "${applet.name}" created successfully!',
              style: const TextStyle(color: Colors.white),
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );

        // Reset form
        _nameController.clear();
        setState(() {
          _selectedTriggerService = null;
          _selectedTriggerAction = null;
          _selectedActionService = null;
          _selectedActionReaction = null;
          _selectedActionId = null;
          _selectedReactionId = null;
        });
        _formKey.currentState?.reset();

        // Navigate to "My Automations" page to show the newly created automation
        debugPrint('🔄 Navigating to My Automations page...');
        context.read<NavigationProvider>().navigateToPage(
          2,
        ); // Index 2 = My Automations
      }
    } catch (e, stackTrace) {
      debugPrint('❌ ERROR creating automation: $e');
      debugPrint('📚 Stack trace: $stackTrace');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Failed to create automation: ${e.toString()}',
              style: const TextStyle(color: Colors.white),
            ),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 5),
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isCreating = false;
        });
      }
    }
  }
}
