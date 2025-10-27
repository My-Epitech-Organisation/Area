import 'package:flutter/material.dart';

/// Time picker widget with manual input and time picker
///
/// Features:
/// - Manual text input (0-23 for hour, 0-59 for minute)
/// - Clock icon on the right that opens a time picker
/// - Real-time validation
/// - Color feedback (green for valid, red for invalid)
class TimePickerWidget extends StatefulWidget {
  final String label;
  final String? description;
  final int? initialValue;
  final bool required;
  final ValueChanged<int> onChanged;
  final int minValue;
  final int maxValue;
  final String unit; // 'hour' or 'minute'

  const TimePickerWidget({
    super.key,
    required this.label,
    this.description,
    this.initialValue,
    this.required = false,
    required this.onChanged,
    this.minValue = 0,
    this.maxValue = 23,
    this.unit = 'hour',
  });

  @override
  State<TimePickerWidget> createState() => _TimePickerWidgetState();
}

class _TimePickerWidgetState extends State<TimePickerWidget> {
  late TextEditingController _controller;
  late FocusNode _focusNode;
  int? _value;

  @override
  void initState() {
    super.initState();
    _focusNode = FocusNode();
    _value = widget.initialValue;
    _controller = TextEditingController(
      text: widget.initialValue != null
          ? widget.initialValue!.toString().padLeft(2, '0')
          : '',
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _focusNode.dispose();
    super.dispose();
  }

  bool _isValidValue(String input) {
    if (input.isEmpty) return false;
    final value = int.tryParse(input);
    if (value == null) return false;
    return value >= widget.minValue && value <= widget.maxValue;
  }

  void _handleTextChange(String value) {
    if (value.isEmpty) {
      setState(() => _value = null);
      return;
    }

    if (_isValidValue(value)) {
      final intValue = int.parse(value);
      setState(() => _value = intValue);
      // Format with leading zero
      _controller.text = intValue.toString().padLeft(2, '0');
      widget.onChanged(intValue);
    }
  }

  Future<void> _openTimePicker() async {
    final currentTime = TimeOfDay(
      hour: _value ?? 0,
      minute: widget.unit == 'minute' ? (_value ?? 0) : 0,
    );

    if (widget.unit == 'hour') {
      // Open hour picker (using a simple hour selection)
      final selectedHour = await _selectHour(currentTime.hour);
      if (selectedHour != null) {
        setState(() {
          _value = selectedHour;
          _controller.text = selectedHour.toString().padLeft(2, '0');
        });
        widget.onChanged(selectedHour);
      }
    } else {
      // Open minute picker (using a simple minute selection)
      final selectedMinute = await _selectMinute(currentTime.minute);
      if (selectedMinute != null) {
        setState(() {
          _value = selectedMinute;
          _controller.text = selectedMinute.toString().padLeft(2, '0');
        });
        widget.onChanged(selectedMinute);
      }
    }
  }

  Future<int?> _selectHour(int initialHour) async {
    return showDialog<int>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Select Hour'),
          content: SizedBox(
            width: double.maxFinite,
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 4,
                childAspectRatio: 1.5,
              ),
              itemCount: 24,
              itemBuilder: (context, index) {
                final isSelected = index == initialHour;
                return GestureDetector(
                  onTap: () => Navigator.pop(context, index),
                  child: Container(
                    margin: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? Colors.blue.shade600
                          : Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isSelected
                            ? Colors.blue.shade800
                            : Colors.grey.shade400,
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        index.toString().padLeft(2, '0'),
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w600,
                          color: isSelected
                              ? Colors.white
                              : Colors.grey.shade800,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
          ],
        );
      },
    );
  }

  Future<int?> _selectMinute(int initialMinute) async {
    return showDialog<int>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Select Minute'),
          content: SizedBox(
            width: double.maxFinite,
            child: GridView.builder(
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 5,
                childAspectRatio: 1.5,
              ),
              itemCount: 60,
              itemBuilder: (context, index) {
                final isSelected = index == initialMinute;
                return GestureDetector(
                  onTap: () => Navigator.pop(context, index),
                  child: Container(
                    margin: const EdgeInsets.all(4),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? Colors.blue.shade600
                          : Colors.grey.shade200,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isSelected
                            ? Colors.blue.shade800
                            : Colors.grey.shade400,
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        index.toString().padLeft(2, '0'),
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                          color: isSelected
                              ? Colors.white
                              : Colors.grey.shade800,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
          ],
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    final isValid = _value != null;
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

        // Input field with clock icon
        TextField(
          controller: _controller,
          focusNode: _focusNode,
          onChanged: _handleTextChange,
          keyboardType: TextInputType.number,
          textAlign: TextAlign.center,
          maxLength: 2,
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
            hintText: widget.minValue.toString().padLeft(2, '0'),
            hintStyle: TextStyle(color: Colors.grey.shade400),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 12,
              vertical: 12,
            ),
            suffixIcon: GestureDetector(
              onTap: _openTimePicker,
              child: Container(
                padding: const EdgeInsets.all(8),
                child: Icon(
                  widget.unit == 'hour' ? Icons.schedule : Icons.timer,
                  color: isValid
                      ? Colors.blue.shade600
                      : hasError
                      ? Colors.red.shade600
                      : Colors.grey.shade600,
                  size: 20,
                ),
              ),
            ),
            counterText: '', // Hide character counter
          ),
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),

        // Display validation feedback
        const SizedBox(height: 8),
        if (isValid)
          Text(
            widget.unit == 'hour'
                ? '$_value hour${_value == 1 ? '' : 's'}'
                : '$_value minute${_value == 1 ? '' : 's'}',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Colors.blue.shade600,
              fontWeight: FontWeight.w500,
              fontSize: 11,
            ),
          )
        else if (hasError)
          Text(
            'Enter a value between ${widget.minValue} and ${widget.maxValue}',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: Colors.red.shade600,
              fontSize: 11,
            ),
          ),
      ],
    );
  }
}

/// Shorthand for hour picker
class HourPickerWidget extends TimePickerWidget {
  const HourPickerWidget({
    super.key,
    required super.label,
    super.description,
    super.initialValue,
    super.required = false,
    required super.onChanged,
  }) : super(minValue: 0, maxValue: 23, unit: 'hour');
}

/// Shorthand for minute picker
class MinutePickerWidget extends TimePickerWidget {
  const MinutePickerWidget({
    super.key,
    required super.label,
    super.description,
    super.initialValue,
    super.required = false,
    required super.onChanged,
  }) : super(minValue: 0, maxValue: 59, unit: 'minute');
}
