import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/create_applet/create_applet_widgets.dart';
import '../providers/service_catalog_provider.dart';
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

  bool _isCreating = false;

  @override
  void initState() {
    super.initState();
    // Load services when page opens
    WidgetsBinding.instance.addPostFrameCallback((_) {
      context.read<ServiceCatalogProvider>().loadServices();
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

  void _createAutomation() async {
    if (_formKey.currentState?.validate() ?? false) {
      // Validate that all required fields are selected
      if (_selectedTriggerService == null || _selectedTriggerAction == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select a trigger'),
            backgroundColor: Colors.red,
          ),
        );
        return;
      }

      if (_selectedActionService == null || _selectedActionReaction == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Please select an action'),
            backgroundColor: Colors.red,
          ),
        );
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
          actionConfig: {}, // TODO: Add configuration step
          reactionConfig: {}, // TODO: Add configuration step
        );

        if (mounted) {
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

          // Navigate back to home or automations list
          Navigator.of(context).pop();
        }
      } catch (e) {
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
}
