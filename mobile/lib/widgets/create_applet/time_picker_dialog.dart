import 'package:flutter/material.dart';

/// Simple time picker dialog that returns TimeOfDay
///
/// Usage:
/// ```dart
/// final time = await showSimpleTimePicker(
///   context: context,
///   initialTime: TimeOfDay.now(),
/// );
/// if (time != null) {
///   print('Selected: ${time.hour}:${time.minute}');
/// }
/// ```
Future<TimeOfDay?> showSimpleTimePicker({
  required BuildContext context,
  TimeOfDay initialTime = const TimeOfDay(hour: 0, minute: 0),
}) {
  return showTimePicker(
    context: context,
    initialTime: initialTime,
    initialEntryMode: TimePickerEntryMode.input,
    helpText: 'Select time (HH:MM)',
    hourLabelText: 'Hour',
    minuteLabelText: 'Minute',
    confirmText: 'OK',
    cancelText: 'Cancel',
  );
}

/// Alternative: Custom time picker with numeric input only
class TimePickerInput extends StatefulWidget {
  final TimeOfDay initialTime;
  final Function(TimeOfDay) onTimeSelected;

  const TimePickerInput({
    super.key,
    required this.initialTime,
    required this.onTimeSelected,
  });

  @override
  State<TimePickerInput> createState() => _TimePickerInputState();
}

class _TimePickerInputState extends State<TimePickerInput> {
  late TextEditingController _hourController;
  late TextEditingController _minuteController;

  @override
  void initState() {
    super.initState();
    _hourController = TextEditingController(
      text: widget.initialTime.hour.toString().padLeft(2, '0'),
    );
    _minuteController = TextEditingController(
      text: widget.initialTime.minute.toString().padLeft(2, '0'),
    );
  }

  @override
  void dispose() {
    _hourController.dispose();
    _minuteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('Select Time', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Hour input
                SizedBox(
                  width: 80,
                  child: TextField(
                    controller: _hourController,
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    decoration: InputDecoration(
                      labelText: 'Hour',
                      border: const OutlineInputBorder(),
                      hintText: '00-23',
                    ),
                    onChanged: (value) {
                      final hour = int.tryParse(value) ?? 0;
                      if (hour > 23) {
                        _hourController.text = '23';
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Text(':', style: Theme.of(context).textTheme.headlineSmall),
                const SizedBox(width: 8),
                // Minute input
                SizedBox(
                  width: 80,
                  child: TextField(
                    controller: _minuteController,
                    keyboardType: TextInputType.number,
                    textAlign: TextAlign.center,
                    decoration: InputDecoration(
                      labelText: 'Minute',
                      border: const OutlineInputBorder(),
                      hintText: '00-59',
                    ),
                    onChanged: (value) {
                      final minute = int.tryParse(value) ?? 0;
                      if (minute > 59) {
                        _minuteController.text = '59';
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('Cancel'),
                ),
                const SizedBox(width: 8),
                ElevatedButton(
                  onPressed: () {
                    final hour = int.tryParse(_hourController.text) ?? 0;
                    final minute = int.tryParse(_minuteController.text) ?? 0;

                    if (hour < 0 || hour > 23) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Hour must be 0-23')),
                      );
                      return;
                    }

                    if (minute < 0 || minute > 59) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Minute must be 0-59')),
                      );
                      return;
                    }

                    widget.onTimeSelected(
                      TimeOfDay(hour: hour, minute: minute),
                    );
                    Navigator.pop(
                      context,
                      TimeOfDay(hour: hour, minute: minute),
                    );
                  },
                  child: const Text('OK'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

/// Show custom time picker dialog
Future<TimeOfDay?> showCustomTimePicker({
  required BuildContext context,
  TimeOfDay initialTime = const TimeOfDay(hour: 0, minute: 0),
}) {
  return showDialog<TimeOfDay>(
    context: context,
    builder: (context) =>
        TimePickerInput(initialTime: initialTime, onTimeSelected: (time) {}),
  );
}
