import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/applet.dart';
import '../providers/applet_provider.dart';

class EditAppletPage extends StatefulWidget {
  final Applet applet;

  const EditAppletPage({super.key, required this.applet});

  @override
  State<EditAppletPage> createState() => _EditAppletPageState();
}

class _EditAppletPageState extends State<EditAppletPage> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  late bool _isActive;

  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.applet.name);
    _descriptionController = TextEditingController(
      text: widget.applet.description,
    );
    _isActive = widget.applet.isActive;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  Future<void> _saveChanges() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final appletProvider = Provider.of<AppletProvider>(context, listen: false);
    final success = await appletProvider.updateApplet(
      widget.applet.id,
      name: _nameController.text.trim(),
      description: _descriptionController.text.trim(),
      status: _isActive ? 'active' : 'disabled',
    );

    setState(() {
      _isLoading = false;
    });

    if (success) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Applet updated successfully')),
        );
        Navigator.of(context).pop(true);
      }
    } else {
      setState(() {
        _errorMessage = 'Failed to update applet: ${appletProvider.error}';
      });
    }
  }

  Future<void> _toggleActive() async {
    final appletProvider = Provider.of<AppletProvider>(context, listen: false);
    final success = await appletProvider.toggleApplet(widget.applet.id);

    if (success) {
      setState(() {
        _isActive = !_isActive;
      });
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              _isActive ? 'Applet activated' : 'Applet deactivated',
            ),
          ),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Edit Applet'),
        actions: [
          Semantics(
            label: 'Save changes button',
            hint: 'Tap to save your modifications',
            button: true,
            child: IconButton(
              onPressed: _isLoading ? null : _saveChanges,
              icon: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Icon(Icons.save),
            ),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Applet status card
              Semantics(
                label: 'Applet status information',
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        Row(
                          children: [
                            Semantics(
                              label: 'Applet status indicator',
                              hint: _isActive
                                  ? 'Applet is currently active'
                                  : 'Applet is currently inactive',
                              child: Icon(
                                _isActive
                                    ? Icons.play_circle
                                    : Icons.pause_circle,
                                color: _isActive ? Colors.green : Colors.orange,
                                size: 24,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              _isActive ? 'Active' : 'Inactive',
                              style: TextStyle(
                                color: _isActive ? Colors.green : Colors.orange,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const Spacer(),
                            Semantics(
                              label: 'Toggle applet active status',
                              hint:
                                  'Tap to ${_isActive ? 'deactivate' : 'activate'} this applet',
                              button: true,
                              child: Switch(
                                value: _isActive,
                                onChanged: _isLoading
                                    ? null
                                    : (_) => _toggleActive(),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          'ID: ${widget.applet.id}',
                          style: const TextStyle(
                            color: Colors.grey,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Form fields
              Semantics(
                label: 'Applet name input field',
                hint: 'Enter a new name for your applet',
                child: TextFormField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Applet Name',
                    border: OutlineInputBorder(),
                    helperText: 'Choose a descriptive name for your applet',
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a name';
                    }
                    if (value.length < 3) {
                      return 'Name must be at least 3 characters';
                    }
                    return null;
                  },
                ),
              ),

              const SizedBox(height: 16),

              Semantics(
                label: 'Applet description input field',
                hint: 'Enter a new description for your applet',
                child: TextFormField(
                  controller: _descriptionController,
                  decoration: const InputDecoration(
                    labelText: 'Description',
                    border: OutlineInputBorder(),
                    helperText: 'Describe what this applet does',
                  ),
                  maxLines: 3,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Please enter a description';
                    }
                    return null;
                  },
                ),
              ),

              const SizedBox(height: 24),

              // Services info (read-only)
              Semantics(
                label: 'Applet services information',
                child: const Text(
                  'Services Configuration',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),

              const SizedBox(height: 16),

              Semantics(
                label: 'Trigger service information',
                child: Card(
                  child: ListTile(
                    leading: const Icon(Icons.flash_on, color: Colors.orange),
                    title: const Text('Trigger Service'),
                    subtitle: Text(widget.applet.triggerService),
                    trailing: const Icon(Icons.info_outline),
                  ),
                ),
              ),

              const SizedBox(height: 8),

              Semantics(
                label: 'Action service information',
                child: Card(
                  child: ListTile(
                    leading: const Icon(Icons.play_arrow, color: Colors.blue),
                    title: const Text('Action Service'),
                    subtitle: Text(widget.applet.actionService),
                    trailing: const Icon(Icons.info_outline),
                  ),
                ),
              ),

              const SizedBox(height: 24),

              // Error message
              if (_errorMessage != null)
                Semantics(
                  label: 'Error message',
                  child: Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: Colors.red.withValues(alpha: 0.3),
                      ),
                    ),
                    child: Text(
                      _errorMessage!,
                      style: const TextStyle(color: Colors.red),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),

              const SizedBox(height: 24),

              // Save button
              Semantics(
                label: 'Save changes button',
                hint: 'Tap to save your modifications',
                button: true,
                child: SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _saveChanges,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: _isLoading
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                Colors.white,
                              ),
                            ),
                          )
                        : const Text(
                            'Save Changes',
                            style: TextStyle(fontSize: 16),
                          ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Note about advanced editing
              Semantics(
                label: 'Advanced configuration note',
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: Colors.blue.withValues(alpha: 0.3),
                    ),
                  ),
                  child: const Row(
                    children: [
                      Icon(Icons.info, color: Colors.blue),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'For advanced configuration like trigger/action settings, please use the web interface.',
                          style: TextStyle(color: Colors.blue),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
