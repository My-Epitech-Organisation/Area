import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// Widget for hour selection (0-23)
class HourField extends StatelessWidget {
  final String label;
  final int value;
  final bool required;
  final ValueChanged<int> onChanged;

  const HourField({
    super.key,
    required this.label,
    required this.value,
    this.required = false,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label${required ? ' *' : ''}',
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: value.toString().padLeft(2, '0'),
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            hintText: '00-23',
            suffixIcon: const Icon(Icons.access_time),
          ),
          onChanged: (val) {
            final hour = int.tryParse(val) ?? 0;
            if (hour >= 0 && hour <= 23) {
              onChanged(hour);
            }
          },
          validator: (val) {
            final hour = int.tryParse(val ?? '');
            if (hour == null || hour < 0 || hour > 23) {
              return 'Hour must be 0-23';
            }
            return null;
          },
        ),
      ],
    );
  }
}

/// Widget for minute selection (0-59)
class MinuteField extends StatelessWidget {
  final String label;
  final int value;
  final bool required;
  final ValueChanged<int> onChanged;

  const MinuteField({
    super.key,
    required this.label,
    required this.value,
    this.required = false,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label${required ? ' *' : ''}',
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: 8),
        TextFormField(
          initialValue: value.toString().padLeft(2, '0'),
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            hintText: '00-59',
            suffixIcon: const Icon(Icons.hourglass_bottom),
          ),
          onChanged: (val) {
            final minute = int.tryParse(val) ?? 0;
            if (minute >= 0 && minute <= 59) {
              onChanged(minute);
            }
          },
          validator: (val) {
            final minute = int.tryParse(val ?? '');
            if (minute == null || minute < 0 || minute > 59) {
              return 'Minute must be 0-59';
            }
            return null;
          },
        ),
      ],
    );
  }
}

/// Widget for timezone selection with cities
class TimezoneField extends StatelessWidget {
  static const Map<String, String> timezones = {
    'UTC': '(UTC+0) London',
    'CET': '(UTC+1) Paris',
    'EET': '(UTC+2) Cairo',
    'IST': '(UTC+5:30) India',
    'JST': '(UTC+9) Tokyo',
    'AEST': '(UTC+10) Sydney',
    'GMT-5': '(UTC-5) New York',
    'GMT-6': '(UTC-6) Chicago',
    'GMT-7': '(UTC-7) Denver',
    'GMT-8': '(UTC-8) Los Angeles',
  };

  final String label;
  final String value;
  final bool required;
  final ValueChanged<String> onChanged;

  const TimezoneField({
    super.key,
    required this.label,
    required this.value,
    this.required = false,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    final selectedTz = timezones.containsKey(value) ? value : 'UTC';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label${required ? ' *' : ''}',
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          initialValue: selectedTz,
          decoration: InputDecoration(
            border: const OutlineInputBorder(),
            suffixIcon: const Icon(Icons.public),
          ),
          items: timezones.entries.map((e) {
            return DropdownMenuItem(value: e.key, child: Text(e.value));
          }).toList(),
          onChanged: (val) {
            if (val != null) onChanged(val);
          },
        ),
        const SizedBox(height: 4),
        Text(
          'Selected: ${timezones[selectedTz]}',
          style: Theme.of(
            context,
          ).textTheme.bodySmall?.copyWith(color: Colors.grey),
        ),
      ],
    );
  }
}

/// Widget for date selection
class DateField extends StatefulWidget {
  final String label;
  final String value;
  final bool required;
  final ValueChanged<String> onChanged;

  const DateField({
    super.key,
    required this.label,
    required this.value,
    this.required = false,
    required this.onChanged,
  });

  @override
  State<DateField> createState() => _DateFieldState();
}

class _DateFieldState extends State<DateField> {
  late DateTime? selectedDate;

  @override
  void initState() {
    super.initState();
    if (widget.value.isNotEmpty) {
      try {
        selectedDate = DateTime.parse(widget.value);
      } catch (_) {
        selectedDate = null;
      }
    } else {
      selectedDate = null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${widget.label}${widget.required ? ' *' : ''}',
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () async {
            final ctx = context;
            final picked = await showDatePicker(
              context: ctx,
              initialDate: selectedDate ?? DateTime.now(),
              firstDate: DateTime(2000),
              lastDate: DateTime(2100),
            );
            if (picked != null) {
              if (!mounted) return;
              setState(() => selectedDate = picked);
              widget.onChanged(picked.toIso8601String().split('T')[0]);
            }
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade400),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    selectedDate != null
                        ? DateFormat('yyyy-MM-dd').format(selectedDate!)
                        : 'Tap to select',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: selectedDate != null ? Colors.black : Colors.grey,
                    ),
                  ),
                ),
                const Icon(Icons.calendar_today, color: Colors.blue),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

/// Widget for date-time selection
/// DEPRECATED: Use DateTimePickerWidget instead for better UX
/// This widget is kept for backward compatibility but should not be used for new code
@Deprecated('Use DateTimePickerWidget instead')
class DateTimeField extends StatefulWidget {
  final String label;
  final String value;
  final bool required;
  final ValueChanged<String> onChanged;

  const DateTimeField({
    super.key,
    required this.label,
    required this.value,
    this.required = false,
    required this.onChanged,
  });

  @override
  State<DateTimeField> createState() => _DateTimeFieldState();
}

class _DateTimeFieldState extends State<DateTimeField> {
  late DateTime? selectedDateTime;

  @override
  void initState() {
    super.initState();
    if (widget.value.isNotEmpty) {
      try {
        selectedDateTime = DateTime.parse(widget.value);
      } catch (_) {
        selectedDateTime = null;
      }
    } else {
      selectedDateTime = null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '${widget.label}${widget.required ? ' *' : ''}',
          style: Theme.of(context).textTheme.labelSmall,
        ),
        const SizedBox(height: 8),
        InkWell(
          onTap: () async {
            // ignore: use_build_context_synchronously
            final DateTime? pickedDate = await showDatePicker(
              context: context,
              initialDate: selectedDateTime ?? DateTime.now(),
              firstDate: DateTime(2000),
              lastDate: DateTime(2100),
              helpText: 'Select a date',
            );

            if (pickedDate != null && mounted) {
              // ignore: use_build_context_synchronously
              final TimeOfDay? pickedTime = await showTimePicker(
                context: context,
                initialTime: TimeOfDay.fromDateTime(
                  selectedDateTime ?? DateTime.now(),
                ),
                helpText: 'Select a time',
              );

              if (pickedTime != null && mounted) {
                final DateTime dateTime = DateTime(
                  pickedDate.year,
                  pickedDate.month,
                  pickedDate.day,
                  pickedTime.hour,
                  pickedTime.minute,
                );
                setState(() => selectedDateTime = dateTime);
                widget.onChanged(dateTime.toIso8601String());
              }
            }
          },
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
            decoration: BoxDecoration(
              border: Border.all(
                color: selectedDateTime != null
                    ? Colors.blue.shade300
                    : Colors.grey.shade400,
                width: selectedDateTime != null ? 2 : 1,
              ),
              borderRadius: BorderRadius.circular(4),
              color: Colors.grey.shade50,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (selectedDateTime != null)
                        Text(
                          DateFormat('MMM d, yyyy').format(selectedDateTime!),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey.shade600,
                            fontSize: 12,
                          ),
                        ),
                      Text(
                        selectedDateTime != null
                            ? DateFormat('HH:mm').format(selectedDateTime!)
                            : 'Tap to select date & time',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: selectedDateTime != null
                              ? Colors.black87
                              : Colors.grey.shade500,
                          fontWeight: selectedDateTime != null
                              ? FontWeight.w500
                              : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.only(left: 8.0),
                  child: Icon(
                    Icons.calendar_today,
                    color: selectedDateTime != null
                        ? Colors.blue.shade600
                        : Colors.grey.shade400,
                    size: 24,
                  ),
                ),
              ],
            ),
          ),
        ),
        if (selectedDateTime != null)
          Padding(
            padding: const EdgeInsets.only(top: 8.0),
            child: Text(
              'ISO 8601: ${selectedDateTime!.toIso8601String()}',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.blue.shade600,
                fontSize: 10,
              ),
            ),
          ),
      ],
    );
  }
}
