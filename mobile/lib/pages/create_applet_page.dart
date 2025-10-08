import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../widgets/create_applet/create_applet_widgets.dart';
import '../providers/service_catalog_provider.dart';

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
                    });
                  },
                  onActionChanged: (value) {
                    setState(() {
                      _selectedTriggerAction = value;
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
                      });
                    },
                    onReactionChanged: (value) {
                      setState(() {
                        _selectedActionReaction = value;
                      });
                    },
                  ),

                const SizedBox(height: 32),

                // Create Button
                CreateAutomationButton(onPressed: _createAutomation),

                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _createAutomation() {
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

      // Here you would typically save the automation with the selected services and actions
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Automation "${_nameController.text}" created successfully!\n'
            'Trigger: $_selectedTriggerService - $_selectedTriggerAction\n'
            'Action: $_selectedActionService - $_selectedActionReaction',
            style: const TextStyle(color: Colors.white),
          ),
          backgroundColor: Theme.of(context).colorScheme.primary,
          duration: const Duration(seconds: 5),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      );

      // Reset form
      _nameController.clear();
      setState(() {
        _selectedTriggerService = null;
        _selectedTriggerAction = null;
        _selectedActionService = null;
        _selectedActionReaction = null;
      });
      _formKey.currentState?.reset();
    }
  }
}
