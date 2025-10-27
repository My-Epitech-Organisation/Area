import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

/// A simple DateTime picker widget with manual input and calendar picker
///
/// Features:
/// - Manual text input field for ISO 8601 dates
/// - Calendar/Clock icon on the right that opens date/time pickers
/// - Shows parsed datetime when valid, error when invalid
/// - Supports both full ISO 8601 and user-friendly formats
class DateTimePickerWidget extends StatefulWidget {
  final String label;
  final String? description;
  final String? initialValue;
  final bool required;
  final ValueChanged<String> onChanged;
  final DateTime? firstDate;
  final DateTime? lastDate;

  const DateTimePickerWidget({
    super.key,
    required this.label,
    this.description,
    this.initialValue,
    this.required = false,
    required this.onChanged,
    this.firstDate,
    this.lastDate,
  });

  @override
  State<DateTimePickerWidget> createState() => _DateTimePickerWidgetState();
}

class _DateTimePickerWidgetState extends State<DateTimePickerWidget> {
  late TextEditingController _controller;
  late DateTime? selectedDateTime;
  late FocusNode _focusNode;

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode();
    _parseInitialValue();
    _controller = TextEditingController(
      text: selectedDateTime != null
          ? selectedDateTime!.toIso8601String()
          : widget.initialValue ?? '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  void _parseInitialValue() {
    if (widget.initialValue != null && widget.initialValue!.isNotEmpty) {
      try {
        selectedDateTime = DateTime.parse(widget.initialValue!);
      } catch (_) {
        selectedDateTime = null;
      }
    } else {
      selectedDateTime = null;
    }
  }

  /// Parse various datetime formats
  DateTime? _parseInput(String input) {
    if (input.isEmpty) return null;

    try {
      // Try ISO 8601 format first
      return DateTime.parse(input);
    } catch (_) {
      // Try common formats
      final formats = [
        'yyyy-MM-dd HH:mm',
        'yyyy-MM-dd HH:mm:ss',
        'dd/MM/yyyy HH:mm',
        'dd-MM-yyyy HH:mm',
        'yyyy-MM-dd',
        'dd/MM/yyyy',
      ];

      for (final format in formats) {
        try {
          return DateFormat(format).parse(input);
        } catch (_) {
          continue;
        }
      }
      return null;
    }
  }

  Future<void> _selectDateAndTime() async {
    final now = DateTime.now();
    final firstDate = widget.firstDate ?? DateTime(2000);
    final lastDate = widget.lastDate ?? DateTime(2100);

    // Parse current text if valid, otherwise use selectedDateTime or now
    DateTime initialDate = now;
    if (_controller.text.isNotEmpty) {
      final parsed = _parseInput(_controller.text);
      if (parsed != null) {
        initialDate = parsed;
      }
    } else if (selectedDateTime != null) {
      initialDate = selectedDateTime!;
    }

    final DateTime? pickedDate = await showDatePicker(
      context: context,
      initialDate: initialDate,
      firstDate: firstDate,
      lastDate: lastDate,
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: Colors.blue.shade600,
              onPrimary: Colors.white,
              surface: Colors.grey.shade50,
            ),
          ),
          child: child!,
        );
      },
    );

    if (pickedDate == null) return;

    if (!mounted) return;

    // ignore: use_build_context_synchronously
    final TimeOfDay? pickedTime = await showTimePicker(
      context: context,
      initialTime: initialDate.hour > 0 || initialDate.minute > 0
          ? TimeOfDay.fromDateTime(initialDate)
          : const TimeOfDay(hour: 9, minute: 0), // Default to 9:00 AM
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: ColorScheme.light(
              primary: Colors.blue.shade600,
              onPrimary: Colors.white,
            ),
          ),
          child: child!,
        );
      },
    );

    if (pickedTime == null) return;

    if (!mounted) return;

    final DateTime newDateTime = DateTime(
      pickedDate.year,
      pickedDate.month,
      pickedDate.day,
      pickedTime.hour,
      pickedTime.minute,
    );

    setState(() {
      selectedDateTime = newDateTime;
      _controller.text = newDateTime.toIso8601String();
    });
    widget.onChanged(newDateTime.toIso8601String());
  }

  void _handleTextChange(String value) {
    if (value.isEmpty) {
      setState(() => selectedDateTime = null);
      widget.onChanged('');
      return;
    }

    final parsed = _parseInput(value);
    if (parsed != null) {
      setState(() => selectedDateTime = parsed);
      // Convert to ISO 8601 for consistency
      final isoValue = parsed.toIso8601String();
      if (value != isoValue) {
        _controller.text = isoValue;
      }
      widget.onChanged(isoValue);
    }
  }

  @override
  Widget build(BuildContext context) {
    final isValid = selectedDateTime != null;
    final hasError = _controller.text.isNotEmpty && !isValid;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Label with required indicator
        RichText(
          text: TextSpan(
            children: [
              TextSpan(
                text: widget.label,
                style: Theme.of(
                  context,
                ).textTheme.labelSmall?.copyWith(fontWeight: FontWeight.w600),
              ),
              if (widget.required)
                const TextSpan(
                  text: ' *',
                  style: TextStyle(color: Colors.red),
                ),
            ],
          ),
        ),

        // Description if provided
        if (widget.description != null)
          Padding(
            padding: const EdgeInsets.only(top: 4.0),
            child: Text(
              widget.description!,
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: Colors.grey.shade600,
                fontSize: 11,
              ),
            ),
          ),

        const SizedBox(height: 12),

        // Input field with calendar icon
        TextField(
          controller: _controller,
          focusNode: _focusNode,
          onChanged: _handleTextChange,
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: hasError
                    ? Colors.red.shade400
                    : isValid
                    ? Colors.blue.shade300
                    : Colors.grey.shade300,
                width: hasError || isValid ? 2 : 1.5,
              ),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: hasError
                    ? Colors.red.shade400
                    : isValid
                    ? Colors.blue.shade300
                    : Colors.grey.shade300,
                width: hasError || isValid ? 2 : 1.5,
              ),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(
                color: hasError ? Colors.red.shade600 : Colors.blue.shade600,
                width: 2,
              ),
            ),
            filled: true,
            fillColor: hasError
                ? Colors.red.shade50
                : isValid
                ? Colors.blue.shade50
                : Colors.grey.shade50,
            hintText: 'YYYY-MM-DDTHH:MM:SS or tap calendar',
            hintStyle: TextStyle(color: Colors.grey.shade400),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 12,
            ),
            suffixIcon: GestureDetector(
              onTap: _selectDateAndTime,
              child: Container(
                padding: const EdgeInsets.all(8),
                child: Icon(
                  Icons.calendar_today,
                  color: isValid
                      ? Colors.blue.shade600
                      : hasError
                      ? Colors.red.shade600
                      : Colors.grey.shade600,
                  size: 20,
                ),
              ),
            ),
          ),
          style: Theme.of(context).textTheme.bodyMedium,
        ),

        // Display parsed datetime and error messages
        const SizedBox(height: 8),
        if (isValid)
          Text(
            DateFormat('EEEE, MMMM d, yyyy • HH:mm').format(selectedDateTime!),
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Colors.blue.shade600,
              fontWeight: FontWeight.w500,
              fontSize: 11,
            ),
          )
        else if (hasError)
          Text(
            'Invalid date/time format',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Colors.red.shade600,
              fontSize: 11,
            ),
          ),
      ],
    );
  }
}
