import 'package:flutter/material.dart';

class CreateAppletPage extends StatelessWidget {
  const CreateAppletPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Semantics(
      label: 'Create new applet page',
      child: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Semantics(
                header: true,
                child: const Text(
                  'Create a new AREA applet',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'An applet is an automation that connects services.',
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 20),
              Semantics(
                label: 'Applet name input field',
                hint: 'Enter a name for your new applet',
                child: TextField(
                  decoration: const InputDecoration(
                    labelText: 'Applet Name',
                    border: OutlineInputBorder(),
                    helperText: 'Choose a descriptive name for your applet',
                  ),
                ),
              ),
              const SizedBox(height: 10),
              Semantics(
                label: 'Trigger service selection',
                hint: 'Select which service will trigger the applet',
                child: DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Trigger Service',
                    border: OutlineInputBorder(),
                    helperText: 'Choose the service that will start the automation',
                  ),
                  items: ['Gmail', 'Discord', 'GitHub', 'Timer']
                      .map((service) => DropdownMenuItem(
                            value: service,
                            child: Text(service),
                          ))
                      .toList(),
                  onChanged: (value) {},
                ),
              ),
              const SizedBox(height: 10),
              Semantics(
                label: 'Action selection',
                hint: 'Select what action the applet should perform',
                child: DropdownButtonFormField<String>(
                  decoration: const InputDecoration(
                    labelText: 'Action',
                    border: OutlineInputBorder(),
                    helperText: 'Choose what the applet should do when triggered',
                  ),
                  items: ['Send message', 'Create task', 'Notify']
                      .map((action) => DropdownMenuItem(
                            value: action,
                            child: Text(action),
                          ))
                      .toList(),
                  onChanged: (value) {},
                ),
              ),
              const SizedBox(height: 20),
              Semantics(
                button: true,
                label: 'Create applet button',
                hint: 'Tap to create the new applet with selected settings',
                child: ElevatedButton(
                  onPressed: () {
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text('Applet created!'),
                        duration: Duration(seconds: 2),
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    minimumSize: const Size(double.infinity, 48),
                  ),
                  child: const Text(
                    'Create Applet',
                    style: TextStyle(fontSize: 16),
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