import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/create_applet/create_applet_widgets.dart';
import '../providers/service_catalog_provider.dart';
import '../providers/connected_services_provider.dart';
import '../providers/navigation_provider.dart';
import '../providers/automation_stats_provider.dart';
import '../services/applet_service.dart';
import '../utils/config_validator.dart';

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

  void _showErrorSnackBar(String message, {Duration duration = const Duration(seconds: 3)}) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(message),
          backgroundColor: Colors.red,
          duration: duration,
        ),
      );
    }
  }

  void _showSuccessSnackBar(String message) {
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            message,
            style: const TextStyle(color: Colors.white),
          ),
          backgroundColor: Colors.green,
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  bool _validateConfigSchema({
    required Map<String, dynamic>? schema,
    required Map<String, dynamic> config,
  }) {
    if (schema == null || schema.isEmpty) {
      return true;
    }

    final validationResult = ConfigValidator.validate(
      schema: schema,
      config: config,
      configName: '',
    );

    if (!validationResult.isValid) {
      String errorMessage = 'Please fill in the following required fields:\n';
      for (final error in validationResult.errors) {
        errorMessage += '• $error\n';
      }
      _showErrorSnackBar(errorMessage, duration: const Duration(seconds: 5));
      return false;
    }

    return true;
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
    final formValid = _formKey.currentState?.validate() ?? false;

    if (!formValid) {
      String errorMessage = 'Please fill in all required fields';
      if (_nameController.text.isEmpty) {
        errorMessage =
            'Please enter an automation name (at least 3 characters)';
      } else if (_nameController.text.length < 3) {
        errorMessage = 'Automation name must be at least 3 characters long';
      }
      _showErrorSnackBar(errorMessage);
      return;
    }

    // Validate trigger selection
    if (_selectedTriggerService == null || _selectedTriggerAction == null) {
      _showErrorSnackBar('Please select a trigger');
      return;
    }

    // Validate action selection
    if (_selectedActionService == null || _selectedActionReaction == null) {
      _showErrorSnackBar('Please select an action');
      return;
    }

    // Validate IDs are set
    if (_selectedActionId == null || _selectedReactionId == null) {
      _showErrorSnackBar('Invalid action or reaction selected');
      return;
    }

    // Validate configuration forms
    if (!(_validateConfigForm?.call() ?? true)) {
      _showErrorSnackBar('Please fill in all required configuration fields');
      return;
    }

    // Validate reaction configuration
    final reaction = context
        .read<ServiceCatalogProvider>()
        .getReaction(_selectedActionReaction!);

    if (!_validateConfigSchema(
      schema: reaction?.configSchema,
      config: _reactionConfig,
    )) {
      return;
    }

    // Validate action configuration
    final action = context
        .read<ServiceCatalogProvider>()
        .getAction(_selectedTriggerAction!);

    if (!_validateConfigSchema(
      schema: action?.configSchema,
      config: _actionConfig,
    )) {
      return;
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

      // Refresh statistics to reflect the new automation
      if (mounted) {
        WidgetsBinding.instance.addPostFrameCallback((_) async {
          final statsProvider = context.read<AutomationStatsProvider>();
          await statsProvider.loadAllStats(forceRefresh: true);
        });
      }

      if (mounted) {
        _showSuccessSnackBar(
          'Automation "${applet.name}" created successfully!',
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

        // Navigate to "My Automations" page
        context.read<NavigationProvider>().navigateToPage(2);
      }
    } catch (e) {
      _showErrorSnackBar(
        'Failed to create automation: ${e.toString()}',
        duration: const Duration(seconds: 5),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isCreating = false;
        });
      }
    }
  }
}
