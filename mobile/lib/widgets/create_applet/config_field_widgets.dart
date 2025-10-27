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
    'EST_US': '(UTC-5) New York',
    'CST_US': '(UTC-6) Chicago',
    'MST_US': '(UTC-7) Denver',
    'PST_US': '(UTC-8) Los Angeles',
    'KST': '(UTC+9) Seoul',
    'ACST': '(UTC+9:30) Adelaide',
    'AEDT': '(UTC+11) Australian Eastern Daylight',
    'NZST': '(UTC+12) Auckland',

    // Pacific
    'FJT': '(UTC+12) Fiji',
    'NZDT': '(UTC+13) New Zealand Daylight',
    'TOT': '(UTC+13) Tonga',
    'AEST': '(UTC+10) Sydney, Brisbane',
    'AWST': '(UTC+8) Perth',

    // Americas
    'BRST': '(UTC-2) Brasília Summer',
    'ART': '(UTC-3) Buenos Aires',
    'GFT': '(UTC-3) French Guiana',
    'PYST': '(UTC-3) Paraguay Summer',
    'CLST': '(UTC-3) Chile Summer',
    'VET': '(UTC-4:30) Venezuela',
    'BOT': '(UTC-4) Bolivia',
    'PYT': '(UTC-4) Paraguay',
    'CLT': '(UTC-4) Chile',
    'COT': '(UTC-5) Colombia',
    'PET': '(UTC-5) Peru',
    'ECT': '(UTC-5) Ecuador',
    'CST_MEXICO': '(UTC-6) Mexico',
    'PST': '(UTC-8) Los Angeles',
    'MST': '(UTC-7) Denver',
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
          isExpanded: true,
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

class TimePickerField extends StatefulWidget {
  final String label;
  final int initialHour;
  final int initialMinute;
  final bool required;
  final Function(int hour, int minute) onChanged;

  const TimePickerField({
    super.key,
    required this.label,
    this.initialHour = 0,
    this.initialMinute = 0,
    this.required = false,
    required this.onChanged,
  });

  @override
  State<TimePickerField> createState() => _TimePickerFieldState();
}

class _TimePickerFieldState extends State<TimePickerField> {
  late int selectedHour;
  late int selectedMinute;

  @override
  void initState() {
    super.initState();
    selectedHour = widget.initialHour;
    selectedMinute = widget.initialMinute;
  }

  void _openTimePicker() async {
    final ctx = context;
    final TimeOfDay? pickedTime = await showTimePicker(
      context: ctx,
      initialTime: TimeOfDay(
        hour: selectedHour.clamp(0, 23),
        minute: selectedMinute.clamp(0, 59),
      ),
    );

    if (pickedTime != null) {
      if (!mounted) return;
      setState(() {
        selectedHour = pickedTime.hour;
        selectedMinute = pickedTime.minute;
      });
      widget.onChanged(pickedTime.hour, pickedTime.minute);
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
          onTap: _openTimePicker,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 16),
            decoration: BoxDecoration(
              border: Border.all(color: Colors.grey.shade400),
              borderRadius: BorderRadius.circular(4),
              color: Colors.white,
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    '${selectedHour.toString().padLeft(2, '0')}:${selectedMinute.toString().padLeft(2, '0')}',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.black87,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Icon(Icons.access_time, color: Colors.blue.shade600),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
