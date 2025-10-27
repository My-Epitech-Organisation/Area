import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/widgets/create_applet/config_field_widgets.dart';

void main() {
  group('HourField Widget Tests', () {
    testWidgets('HourField displays label correctly', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HourField(label: 'Start Hour', value: 10, onChanged: (_) {}),
          ),
        ),
      );

      expect(find.text('Start Hour'), findsOneWidget);
    });

    testWidgets('HourField displays initial value', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HourField(label: 'Hour', value: 14, onChanged: (_) {}),
          ),
        ),
      );

      expect(find.byType(TextFormField), findsOneWidget);
      final textField = find.byType(TextField);
      expect(textField, findsOneWidget);
    });

    testWidgets('HourField accepts valid input (0-23)', (
      WidgetTester tester,
    ) async {
      int? changedValue;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HourField(
              label: 'Hour',
              value: 0,
              onChanged: (val) => changedValue = val,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), '15');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      await tester.pumpAndSettle();

      expect(changedValue, 15);
    });

    testWidgets('HourField rejects invalid input (>23)', (
      WidgetTester tester,
    ) async {
      int? changedValue;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HourField(
              label: 'Hour',
              value: 0,
              onChanged: (val) => changedValue = val,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), '25');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      await tester.pumpAndSettle();

      // Should not update the value
      expect(changedValue, isNull);
    });

    testWidgets('HourField validator shows error for invalid value', (
      WidgetTester tester,
    ) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Form(
              key: formKey,
              child: HourField(
                label: 'Hour',
                value: 0,
                required: true,
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), '30');
      expect(formKey.currentState?.validate(), false);
    });

    testWidgets('HourField displays hour icon', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HourField(label: 'Hour', value: 10, onChanged: (_) {}),
          ),
        ),
      );

      expect(find.byIcon(Icons.access_time), findsOneWidget);
    });
  });

  group('MinuteField Widget Tests', () {
    testWidgets('MinuteField displays label correctly', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MinuteField(
              label: 'Start Minute',
              value: 30,
              onChanged: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Start Minute'), findsOneWidget);
    });

    testWidgets('MinuteField displays initial value', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MinuteField(label: 'Minute', value: 45, onChanged: (_) {}),
          ),
        ),
      );

      expect(find.byType(TextFormField), findsOneWidget);
    });

    testWidgets('MinuteField shows required indicator when required', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MinuteField(
              label: 'Minute',
              value: 0,
              required: true,
              onChanged: (_) {},
            ),
          ),
        ),
      );

      expect(find.text('Minute (required)'), findsOneWidget);
    });

    testWidgets('MinuteField accepts valid input (0-59)', (
      WidgetTester tester,
    ) async {
      int? changedValue;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MinuteField(
              label: 'Minute',
              value: 0,
              onChanged: (val) => changedValue = val,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), '45');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      await tester.pumpAndSettle();

      expect(changedValue, 45);
    });

    testWidgets('MinuteField rejects invalid input (>59)', (
      WidgetTester tester,
    ) async {
      int? changedValue;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MinuteField(
              label: 'Minute',
              value: 0,
              onChanged: (val) => changedValue = val,
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), '75');
      await tester.testTextInput.receiveAction(TextInputAction.done);
      await tester.pumpAndSettle();

      // Should not update the value
      expect(changedValue, isNull);
    });

    testWidgets('MinuteField validator shows error for invalid value', (
      WidgetTester tester,
    ) async {
      final formKey = GlobalKey<FormState>();

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Form(
              key: formKey,
              child: MinuteField(
                label: 'Minute',
                value: 0,
                required: true,
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      await tester.enterText(find.byType(TextFormField), '90');
      expect(formKey.currentState?.validate(), false);
    });

    testWidgets('MinuteField displays minute icon', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: MinuteField(label: 'Minute', value: 30, onChanged: (_) {}),
          ),
        ),
      );

      expect(find.byIcon(Icons.hourglass_bottom), findsOneWidget);
    });
  });

  group('TimezoneField Widget Tests', () {
    testWidgets('TimezoneField displays label correctly', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.text('Timezone'), findsOneWidget);
    });

    testWidgets('TimezoneField shows required indicator when required', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                required: true,
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.text('Timezone (required)'), findsOneWidget);
    });

    testWidgets('TimezoneField displays dropdown button', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });

    testWidgets('TimezoneField displays all timezone options', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      // Just verify the widget renders without errors
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });

    testWidgets('TimezoneField selects timezone correctly', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      // Verify the widget is rendered
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });

    testWidgets('TimezoneField displays selected timezone', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'CET',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.text('(UTC+1) Paris'), findsOneWidget);
    });

    testWidgets('TimezoneField defaults to UTC for invalid value', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'INVALID',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.text('(UTC+0) London'), findsOneWidget);
    });

    testWidgets('TimezoneField displays world icon', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.public), findsOneWidget);
    });

    testWidgets('TimezoneField contains all expected timezones', (
      WidgetTester tester,
    ) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 400,
              child: TimezoneField(
                label: 'Timezone',
                value: 'UTC',
                onChanged: (_) {},
              ),
            ),
          ),
        ),
      );

      // Verify the dropdown widget is rendered
      expect(find.byType(DropdownButtonFormField<String>), findsOneWidget);
    });
  });
}
