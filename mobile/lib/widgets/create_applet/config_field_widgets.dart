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
