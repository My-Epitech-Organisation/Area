import 'package:flutter/material.dart';
import '../widgets/create_applet/create_applet_widgets.dart';

class CreateAppletPage extends StatefulWidget {
  const CreateAppletPage({super.key});

  @override
  State<CreateAppletPage> createState() => _CreateAppletPageState();
}

class _CreateAppletPageState extends State<CreateAppletPage> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  String? _selectedTrigger;
  String? _selectedAction;

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Semantics(
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
                  AutomationDetailsCard(
                    nameController: _nameController,
                  ),

                  const SizedBox(height: 16),

                  // Trigger Configuration Card
                  TriggerConfigCard(
                    selectedTrigger: _selectedTrigger,
                    onChanged: (value) {
                      setState(() {
                        _selectedTrigger = value;
                      });
                    },
                  ),

                  const SizedBox(height: 16),

                  // Action Configuration Card
                  ActionConfigCard(
                    selectedAction: _selectedAction,
                    onChanged: (value) {
                      setState(() {
                        _selectedAction = value;
                      });
                    },
                  ),

                  const SizedBox(height: 32),

                  // Create Button
                  CreateAutomationButton(
                    onPressed: _createAutomation,
                  ),

                  const SizedBox(height: 20),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  void _createAutomation() {
    if (_formKey.currentState?.validate() ?? false) {
      // Here you would typically save the automation
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            'Automation "${_nameController.text}" created successfully!',
            style: const TextStyle(color: Colors.white),
          ),
          backgroundColor: Theme.of(context).colorScheme.primary,
          duration: const Duration(seconds: 3),
          behavior: SnackBarBehavior.floating,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      );

      // Reset form
      _nameController.clear();
      setState(() {
        _selectedTrigger = null;
        _selectedAction = null;
      });
      _formKey.currentState?.reset();
    }
  }
}
