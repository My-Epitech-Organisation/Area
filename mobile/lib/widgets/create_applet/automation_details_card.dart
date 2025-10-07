import 'package:flutter/material.dart';

/// Widget de carte pour la section de détails de l'automation
/// Contient le champ de saisie du nom de l'automation
class AutomationDetailsCard extends StatelessWidget {
  final TextEditingController nameController;

  const AutomationDetailsCard({
    super.key,
    required this.nameController,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.edit_note,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  'Automation Details',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Semantics(
              label: 'Automation name input field',
              hint: 'Enter a name for your new automation',
              child: TextFormField(
                controller: nameController,
                decoration: InputDecoration(
                  labelText: 'Automation Name',
                  hintText: 'e.g., Daily Report Generator',
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  prefixIcon: const Icon(Icons.title),
                  helperText: 'Choose a descriptive name for your automation',
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Please enter an automation name';
                  }
                  if (value.length < 3) {
                    return 'Name must be at least 3 characters long';
                  }
                  return null;
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
